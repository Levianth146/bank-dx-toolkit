"""Biểu đồ cho 11_sensitivity.py (matplotlib). Màu: mỗi ngân hàng một màu cố định (khe 1-5 của bảng màu phân loại đã kiểm
bằng validate_palette.js: PASS 4/4 kiểm tra, riêng độ tương phản < 3:1 ở 3 màu nên mọi điểm đều có nhãn trực tiếp);
thứ hạng dùng thang tuần tự một màu xanh, hạng 1 đậm nhất."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap

BANK_LABEL = {"tcb": "Techcombank", "vcb": "Vietcombank", "mb": "MB", "bidv": "BIDV", "agribank": "Agribank"}
BANK_COLOR = {"tcb": "#2a78d6", "vcb": "#eb6834", "mb": "#1baf7a", "bidv": "#eda100", "agribank": "#e87ba4"}
BANK_MARK = {"tcb": "o", "vcb": "s", "mb": "^", "bidv": "D", "agribank": "v"}
SURF, INK, INK2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e3e2de"
RAMP = LinearSegmentedColormap.from_list("rank", ["#1b4f9c", "#6ea2e3", "#cfe0f7"])    # hạng 1 -> 5 : đậm -> nhạt


def _style():
    plt.rcParams.update({"font.family": "DejaVu Sans", "figure.facecolor": SURF, "axes.facecolor": SURF,
                         "savefig.facecolor": SURF, "text.color": INK, "axes.labelcolor": INK2,
                         "xtick.color": INK2, "ytick.color": INK2, "axes.edgecolor": GRID, "font.size": 9})


def _rank_color(r, n):
    return RAMP((r - 1) / max(n - 1, 1))


def fig_heatmap(long, banks, order, outdir, year):
    d = long[long.family != "0. Cơ sở"]
    sc = d.drop_duplicates(["family", "scenario"])[["family", "scenario"]].reset_index(drop=True)
    sc = sc[~sc.family.str.contains("từng chỉ số")]                      # 14 kịch bản cận từng chỉ số: hạng không đổi, xem CSV
    piv = d.pivot_table(index=["family", "scenario"], columns="bank", values="rank", sort=False)[order]
    piv = piv.loc[list(zip(sc.family, sc.scenario))]
    fig, ax = plt.subplots(figsize=(6.4, 0.24 * len(piv) + 1.6))
    n = len(order)
    for i, (idx, row) in enumerate(piv.iterrows()):
        for j, b in enumerate(order):
            r = int(row[b])
            ax.add_patch(plt.Rectangle((j, i), 0.94, 0.9, color=_rank_color(r, n), lw=0))
            ax.text(j + 0.47, i + 0.45, str(r), ha="center", va="center", fontsize=8, fontweight="bold" if r <= 2 else "normal",
                    color="white" if r <= 2 else INK)
    ax.set_xlim(0, n); ax.set_ylim(len(piv), 0)
    ax.set_xticks([j + 0.47 for j in range(n)]); ax.set_xticklabels([BANK_LABEL[b] for b in order])
    ax.xaxis.tick_top()
    ax.set_yticks([i + 0.45 for i in range(len(piv))]); ax.set_yticklabels([f"{k[0][:1]}·{k[1]}" for k in piv.index], fontsize=7.5)
    for s in ax.spines.values(): s.set_visible(False)
    ax.tick_params(length=0)
    fig.suptitle(f"Thứ hạng theo từng kịch bản độ nhạy, {year}", x=0.02, ha="left", fontsize=11, fontweight="bold", y=0.995)
    fig.text(0.02, 0.005, "Chữ cái đầu = họ kịch bản (A trọng số DBI/DTI, B trọng số trụ cột, C chuẩn hóa, D loại trụ cột, F thiếu=0, G cận). "
             "Hạng 1 đậm nhất.", fontsize=6.8, color=INK2, ha="left")
    fig.tight_layout(rect=(0, 0.02, 1, 0.97))
    fig.savefig(outdir / f"fig1_rank_heatmap_{year}.png", dpi=200); plt.close(fig)


def fig_mc(mc, banks, order, outdir, year):
    methods = list(dict.fromkeys(mc["method"]))
    n = len(order)
    fig, axes = plt.subplots(len(methods), 1, figsize=(6.4, 1.55 * len(methods) + 0.9), sharex=True)
    axes = np.atleast_1d(axes)
    for ax, m in zip(axes, methods):
        t = mc[mc.method == m]
        for i, b in enumerate(order):
            left = 0.0
            for r in range(1, n + 1):
                p = float(t[(t.bank == b) & (t["rank"] == r)]["prob"].iloc[0])
                if p <= 0: continue
                ax.barh(i, p * 100 - 0.4, left=left, height=0.62, color=_rank_color(r, n), lw=0)
                if p >= 0.07:
                    ax.text(left + p * 50, i, f"{p*100:.0f}%", ha="center", va="center", fontsize=7.5,
                            color="white" if r <= 2 else INK)
                left += p * 100
        ax.set_yticks(range(n)); ax.set_yticklabels([BANK_LABEL[b] for b in order]); ax.invert_yaxis()
        ax.set_xlim(0, 100); ax.set_title(m, loc="left", fontsize=9, color=INK, fontweight="bold")
        ax.tick_params(length=0)
        for s in ax.spines.values(): s.set_visible(False)
    axes[-1].set_xlabel("Xác suất giữ từng thứ hạng (%)")
    handles = [plt.Rectangle((0, 0), 1, 1, color=_rank_color(r, n)) for r in range(1, n + 1)]
    fig.legend(handles, [f"Hạng {r}" for r in range(1, n + 1)], ncol=n, loc="lower center", frameon=False, fontsize=8)
    fig.suptitle(f"Phân bố thứ hạng trong mô phỏng Monte Carlo, {year}", x=0.02, ha="left", fontsize=11, fontweight="bold")
    fig.tight_layout(rect=(0, 0.05, 1, 0.96))
    fig.savefig(outdir / f"fig2_montecarlo_rank_{year}.png", dpi=200); plt.close(fig)


def fig_range(summ, order, outdir, year):
    fig, ax = plt.subplots(figsize=(6.4, 2.9))
    s = summ.set_index("bank")
    for i, b in enumerate(order):
        r = s.loc[b]
        ax.plot([r.min_score, r.max_score], [i, i], color=BANK_COLOR[b], lw=3, solid_capstyle="round", alpha=0.55, zorder=2)
        ax.scatter([r.base_score], [i], s=60, color=BANK_COLOR[b], marker=BANK_MARK[b], edgecolor=SURF, linewidth=1.5, zorder=3)
        ax.text(r.max_score + 0.5, i, f"{r.base_score:.1f}  (dải {r.min_score:.1f}–{r.max_score:.1f})", va="center", fontsize=8, color=INK)
    ax.set_yticks(range(len(order))); ax.set_yticklabels([BANK_LABEL[b] for b in order]); ax.invert_yaxis()
    ax.set_xlim(s.min_score.min() - 3, s.max_score.max() + 17)
    ax.set_xlabel("Score_Bank (%) — điểm cơ sở và dải min–max qua các kịch bản rời rạc")
    ax.grid(axis="x", color=GRID, lw=0.8); ax.set_axisbelow(True); ax.tick_params(length=0)
    for sp in ax.spines.values(): sp.set_visible(False)
    fig.suptitle(f"Dải điểm Score_Bank qua các kịch bản, {year}", x=0.02, ha="left", fontsize=11, fontweight="bold")
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    fig.savefig(outdir / f"fig3_score_range_{year}.png", dpi=200); plt.close(fig)


def make(r, banks, a, outdir, year):
    _style()
    summ = r["summ"].sort_values("base_rank")
    order = list(summ["bank"])
    fig_heatmap(r["long"], banks, order, outdir, year)
    fig_mc(r["mc"], banks, order, outdir, year)
    fig_range(summ, order, outdir, year)
