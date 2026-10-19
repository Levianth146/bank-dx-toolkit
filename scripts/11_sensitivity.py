#!/usr/bin/env python3
"""11_sensitivity.py — Phân tích độ nhạy thứ hạng DBI–DTI (mục V.2 docx, đề cương mục 3.3).

Không đổi cách tính chính thức: dùng lại đúng hàm/hằng số của 10_score.py (Calc, normalize, load_*),
rồi tính lại Score_Bank dạng ma trận để chạy hàng nghìn kịch bản. Kịch bản cơ sở phải khớp 10_score.py.
Bước 0 dùng chung build_indicators của bước 10: tập chỉ số bị loại theo năm
được giữ nguyên trong mọi kịch bản và mô phỏng, kể cả thử thiếu = 0.

Kịch bản (bảng "Kịch bản độ nhạy" của docx):
  A. weights   Trọng số DBI/DTI: 100/0, 80/20 (cơ sở), 70/30, 60/40
  B. pillar_w  Trọng số trụ cột: đều 1/6 so với ±20% từng trụ (12 kịch bản) + Monte Carlo Dirichlet (10.000 lần)
  C. norm      Chuẩn hóa: cận cố định (cơ sở) so với min-max trong 5 ngân hàng so với xếp hạng phần trăm -> Kendall τ
  D. drop      Loại lần lượt từng trụ cột (6 kịch bản)
  E. keyword   Rubric so với mật độ đề cập từ khóa (Spearman ρ) — đọc output_data/tm_vs_dbi.csv do 07_text_mining.py --compare tạo
  F. missing   DTI thiếu = bỏ (cơ sở) so với thiếu = 0   [CHỈ để kiểm tra độ nhạy; điểm chính thức không bao giờ điền 0]
Bổ sung (ngoài bảng docx, vì L/U là cận tham chiếu và DBI do thuật toán quy tắc chấm, chưa kiểm chứng):
  G. bounds    Dịch khoảng [L,U] của các chỉ số có cận suy ra/tham chiếu ±20% (cùng lúc và từng chỉ số)
  H. Monte Carlo nhiễu điểm rubric: mỗi tiêu chí có xác suất q bị lệch ±1 mức

Tiêu chí kết luận (docx): thứ hạng "vững" nếu giữ nguyên trong >= 80% kịch bản rời rạc (A-D, F, G);
ngân hàng đổi hạng nhiều hơn thì báo cáo là "nhóm cùng mức" (cặp mà không bên nào hơn bên kia trong >= 80% kịch bản).

Chạy (trong thư mục scripts/):
  python 11_sensitivity.py                     # năm 2025
  python 11_sensitivity.py --years 2021,2023,2025 --n-mc 10000
Đầu ra: output_data/sensitivity/*.csv, sensitivity_results.xlsx, fig*.png (UTF-8-BOM cho CSV).
"""
import argparse
import importlib.util
import itertools
import pathlib
import sys
import warnings

import numpy as np
import pandas as pd
from scipy.stats import kendalltau, rankdata, spearmanr

SC = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(SC))
_spec = importlib.util.spec_from_file_location("score10", SC / "10_score.py")
S = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(S)
from common import OUT  # noqa: E402

PIL = list(S.PILLARS)                                    # K S T O C D
IND = list(S.ALL_DTI)                                    # 11 chỉ số
IND_BY_P = [[IND.index(i) for i in S.DTI_BY_PILLAR[p]] for p in PIL]
STABLE_SHARE = 0.80
BORDER = 0.05                                            # |tỷ lệ - 80%| < 5 điểm % thì gắn cờ "sát ngưỡng"
BANK_LABEL = {"tcb": "Techcombank", "vcb": "Vietcombank", "mb": "MB", "bidv": "BIDV", "agribank": "Agribank"}
# Chỉ số có cận do nghiên cứu suy ra/tham chiếu -> đáng đưa vào kiểm tra độ nhạy cận.
# (cận tự nhiên 0-100% và thang 1-5 sao không dịch chuyển được một cách có nghĩa)
PERTURB_STATUS = {"sourced", "derived", "external_reference", "sample_percentile"}


# ----------------------------------------------------------------------------------------------
# Lõi tính điểm dạng ma trận (khớp S.pillar_scores / S.score_total)
# ----------------------------------------------------------------------------------------------
def rank_of(score):
    return rankdata(-np.round(score, 9), method="min").astype(int)


def dti_by_pillar(z, missing="drop", retained=None):
    zz = np.where(np.isnan(z), 0.0, z) if missing == "zero" else z
    if retained is not None:
        # Chỉ số bị loại ở bước 0 không được đưa trở lại, kể cả kịch bản thiếu = 0.
        zz = np.where(np.asarray(retained)[None, :], zz, np.nan)
    out = np.full((z.shape[0], len(PIL)), np.nan)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        for k, idx in enumerate(IND_BY_P):
            if idx:
                out[:, k] = np.nanmean(zz[:, idx], axis=1)     # trụ cột không có chỉ số nào có dữ liệu -> NaN
    return out


def pillar_p(dbi, dti, w_dbi):
    return np.where(np.isnan(dti), dbi, w_dbi * dbi + (1 - w_dbi) * dti)    # thiếu DTI -> P_k = DBI_k


def total(p, w=None):
    w = np.full(len(PIL), 1 / len(PIL)) if w is None else np.asarray(w, float)
    return p @ (w / w.sum())


def z_matrix(x, bounds):
    z = np.full(x.shape, np.nan)
    for j, ind in enumerate(IND):
        L, U, d = bounds[ind]
        for i in range(x.shape[0]):
            v = S.normalize(x[i, j], L, U, d) if np.isfinite(x[i, j]) else None
            z[i, j] = np.nan if v is None else v
    return z


def z_minmax(x, bounds, nmin):
    z = np.full(x.shape, np.nan)
    for j, ind in enumerate(IND):
        ok = np.isfinite(x[:, j])
        if ok.sum() < nmin or np.ptp(x[ok, j]) == 0:
            continue
        lo, hi = x[ok, j].min(), x[ok, j].max()
        t = (x[ok, j] - lo) / (hi - lo)
        z[ok, j] = 100 * (1 - t if bounds[ind][2] == "lower_better" else t)
    return z


def z_rankpct(x, bounds, nmin):
    z = np.full(x.shape, np.nan)
    for j, ind in enumerate(IND):
        ok = np.isfinite(x[:, j])
        if ok.sum() < nmin:
            continue
        v = -x[ok, j] if bounds[ind][2] == "lower_better" else x[ok, j]
        z[ok, j] = 100 * (rankdata(v, method="average") - 1) / (ok.sum() - 1)     # kém nhất 0, tốt nhất 100
    return z


def scale_bounds(bounds, meta, inds, f):
    """Co/giãn độ rộng [L,U] theo hệ số f, giữ cố định đầu 'kém nhất' (z = 0)."""
    nb = dict(bounds)
    for ind in inds:
        L, U, d = bounds[ind]
        nb[ind] = (L, L + (U - L) * f, d) if d == "higher_better" else (U - (U - L) * f, U, d)
    return nb


# ----------------------------------------------------------------------------------------------
# Nạp dữ liệu (cùng cách 10_score.py)
# ----------------------------------------------------------------------------------------------
def prepare(a, years):
    bounds, _ = S.load_bounds(draft=False)
    meta = S.load_yaml("dti_bounds.yaml")["bounds"]
    coding = S.load_coding(a.coding, False)
    V, D = S.load_inputs(a.inputs, False)
    project = S.load_yaml("banks.yaml")
    calc = S.Calc(V, D, S.load_app_rating(a.app), S.load_platform(a.audit), a.start_year, max(project["coding_years"]))
    banks = sorted(coding["bank"].unique())
    if set(banks) != set(project["banks"]):
        sys.exit("DỪNG: bước 0 cần đủ tập ngân hàng trong config/banks.yaml.")
    _, gate = S.build_indicators(calc, banks, years, bounds)
    data = {}
    for y in years:
        c = coding[coding["year"] == y]
        lv = np.full((len(banks), len(S.CRITERIA)), np.nan)
        for r in c.itertuples():
            if r.bank in banks and r.criterion in S.CRITERIA:
                lv[banks.index(r.bank), S.CRITERIA.index(r.criterion)] = r.score
        if np.isnan(lv).any():
            sys.exit(f"DỪNG: năm {y} còn ô rubric chưa có điểm; chạy 09c_auto_score.py trước.")
        dbi = lv.reshape(len(banks), len(PIL), 4).mean(axis=2) / 4 * 100
        x = np.full((len(banks), len(IND)), np.nan)
        for i, b in enumerate(banks):
            for ind, (v, _) in calc.all(b, y).items():
                x[i, IND.index(ind)] = np.nan if v is None else v
        retained = gate[gate.year == y].set_index("indicator").loc[IND, "retained"].to_numpy(dtype=bool)
        # Giữ x gốc để truy vết; mọi kịch bản chỉ dùng tập chỉ số sau bước 0.
        xr = np.where(retained[None, :], x, np.nan)
        # Bước 0b (khớp 10_score.build_indicators): trụ cột chỉ nhận DTI khi mọi ngân hàng có ít nhất một chỉ số của trụ cột đó.
        for p_code, ids in S.DTI_BY_PILLAR.items():
            cols = [IND.index(i) for i in ids]
            if cols:
                has = ~np.isnan(xr[:, cols]).all(axis=1)
                if has.any() and not has.all():
                    xr[:, cols] = np.nan
        data[y] = dict(levels=lv, dbi=dbi, raw_x=x.copy(), x=xr,
                       retained=retained, gate=gate[gate.year == y].copy())
    return banks, bounds, meta, data


# ----------------------------------------------------------------------------------------------
# Dựng kịch bản rời rạc
# ----------------------------------------------------------------------------------------------
def build_scenarios(d, bounds, meta, a):
    dbi, x = d["dbi"], d["x"]
    z0 = z_matrix(x, bounds)
    dti0 = dti_by_pillar(z0)
    base = total(pillar_p(dbi, dti0, a.w_dbi))
    sc = []                                                  # (family, name, score)

    for w in (1.0, 0.7, 0.6):                                # A
        sc.append(("A. Trọng số DBI/DTI", f"{int(w*100)}/{int(round((1-w)*100))}", total(pillar_p(dbi, dti0, w))))
    for k, p in enumerate(PIL):                              # B
        for f, tag in ((1.2, "+20%"), (0.8, "-20%")):
            w = np.ones(len(PIL)); w[k] = f
            sc.append(("B. Trọng số trụ cột ±20%", f"{S.PILLARS[p]} {tag}", total(pillar_p(dbi, dti0, a.w_dbi), w)))
    for name, fn in (("Min-max trong 5 NH", z_minmax), ("Xếp hạng phần trăm", z_rankpct)):    # C
        z = fn(x, bounds, a.nmin)
        sc.append(("C. Kỹ thuật chuẩn hóa", name, total(pillar_p(dbi, dti_by_pillar(z), a.w_dbi))))
    for k, p in enumerate(PIL):                              # D
        w = np.ones(len(PIL)); w[k] = 0
        sc.append(("D. Loại một trụ cột", f"Bỏ {S.PILLARS[p]}", total(pillar_p(dbi, dti0, a.w_dbi), w)))
    sc.append(("F. Dữ liệu thiếu", "Thiếu = 0 (chỉ để thử độ nhạy)",
               total(pillar_p(dbi, dti_by_pillar(z0, "zero", d.get("retained")), a.w_dbi))))
    pert = [i for i in IND if meta.get(i, {}).get("status") in PERTURB_STATUS and i not in S.DOCX_FIXED]
    for f, tag in ((0.8, "-20%"), (1.2, "+20%")):            # G
        z = z_matrix(x, scale_bounds(bounds, meta, pert, f))
        sc.append(("G. Dịch cận [L,U] cùng lúc", f"Độ rộng cận {tag}", total(pillar_p(dbi, dti_by_pillar(z), a.w_dbi))))
    for i in pert:
        for f, tag in ((0.8, "-20%"), (1.2, "+20%")):
            z = z_matrix(x, scale_bounds(bounds, meta, [i], f))
            sc.append(("G. Dịch cận từng chỉ số", f"{i} {tag}", total(pillar_p(dbi, dti_by_pillar(z), a.w_dbi))))
    return base, sc, pert, dti0


def monte_carlo(dbi, dti0, a, rng, levels):
    """Trả dict {tên: ma trận hạng (n_bank, n_mc)}."""
    n = dbi.shape[0]
    p0 = pillar_p(dbi, dti0, a.w_dbi)
    res = {}
    for alpha in a.alpha:
        W = rng.dirichlet(np.full(len(PIL), alpha), size=a.n_mc)
        sc = p0 @ W.T
        res[f"Dirichlet α={alpha:g}"] = rankdata(-np.round(sc, 9), method="min", axis=0).astype(int)
    u = rng.random((a.n_mc, n, levels.shape[1]))
    shift = np.where(u < a.noise_q / 2, -1, np.where(u < a.noise_q, 1, 0))
    lv = np.clip(levels[None] + shift, 0, 4)
    dbi_n = lv.reshape(a.n_mc, n, len(PIL), 4).mean(axis=3) / 4 * 100
    p = np.where(np.isnan(dti0)[None], dbi_n, a.w_dbi * dbi_n + (1 - a.w_dbi) * dti0[None]).mean(axis=2)
    res[f"Nhiễu rubric q={a.noise_q:g}"] = rankdata(-np.round(p.T, 9), method="min", axis=0).astype(int)
    return res


def tier_groups(scores, base_score, base_rank, banks, unstable):
    """Nhóm cùng mức (docx V.2): ngân hàng có hạng không vững được gộp với các ngân hàng mà nó từng đổi chỗ
    (so với thứ tự cơ sở) trong ít nhất một kịch bản rời rạc. Bảng cặp ghi thêm tỷ lệ kịch bản mỗi bên xếp trên."""
    n = len(banks)
    sm = np.round(np.array(scores), 9)                       # (n_scen, n_bank)
    base_score = np.round(base_score, 9)
    parent = list(range(n))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]; i = parent[i]
        return i

    rows = []
    for i, j in itertools.combinations(range(n), 2):
        gi, gj = float((sm[:, i] > sm[:, j]).mean()), float((sm[:, j] > sm[:, i]).mean())
        sign0 = np.sign(base_score[i] - base_score[j])
        swapped = bool(((np.sign(sm[:, i] - sm[:, j]) * sign0) < 0).any())      # có kịch bản đảo thứ tự cơ sở
        rows.append(dict(bank_a=banks[i], bank_b=banks[j], share_a_above=gi, share_b_above=gj,
                         share_tie=max(0.0, round(1 - gi - gj, 9)), distinguishable=max(gi, gj) >= STABLE_SHARE,
                         borderline=abs(max(gi, gj) - STABLE_SHARE) < BORDER, swapped_in_some_scenario=swapped))
        if swapped and (banks[i] in unstable or banks[j] in unstable):
            parent[find(i)] = find(j)
    grp = {}
    for i in range(n):
        grp.setdefault(find(i), []).append(i)
    label = {}
    for g, (_, members) in enumerate(sorted(grp.items(), key=lambda kv: min(base_rank[m] for m in kv[1])), 1):
        for m in members:
            label[banks[m]] = (f"Nhóm cùng mức (hạng {min(base_rank[k] for k in members)}–{max(base_rank[k] for k in members)})"
                               if len(members) > 1 else f"Độc lập (hạng {base_rank[m]})")
    return pd.DataFrame(rows), label


# ----------------------------------------------------------------------------------------------
# Chạy một năm
# ----------------------------------------------------------------------------------------------
def run_year(y, banks, bounds, meta, d, a, rng):
    base, sc, pert, dti0 = build_scenarios(d, bounds, meta, a)
    base_rank = rank_of(base)
    n = len(banks)
    rows, krows = [], []
    for fam, name, s in [("0. Cơ sở", f"{int(a.w_dbi*100)}/{int(round((1-a.w_dbi)*100))}, cận cố định", base)] + sc:
        r = rank_of(s)
        tau = kendalltau(base_rank, r).statistic if n > 1 else np.nan
        rho = spearmanr(base_rank, r).statistic if n > 1 else np.nan
        krows.append(dict(year=y, family=fam, scenario=name, kendall_tau=tau, spearman_rho=rho,
                          n_rank_changes=int((r != base_rank).sum())))
        for i, b in enumerate(banks):
            rows.append(dict(year=y, family=fam, scenario=name, bank=b, score=s[i], rank=int(r[i]),
                             base_rank=int(base_rank[i]), rank_change=int(r[i] - base_rank[i])))
    long = pd.DataFrame(rows)
    kend = pd.DataFrame(krows)
    disc = long[long.family != "0. Cơ sở"]

    # độ vững: tỷ lệ kịch bản rời rạc giữ nguyên hạng cơ sở
    summ = []
    share_by_bank = {b: float((disc[disc.bank == b]["rank_change"] == 0).mean()) for b in banks}
    unstable = {b for b, v in share_by_bank.items() if v < STABLE_SHARE}
    pair_df, tier = tier_groups([s for _, _, s in sc], base, base_rank, banks, unstable)
    pair_df.insert(0, "year", y)
    for i, b in enumerate(banks):
        g = disc[disc.bank == b]
        fam_share = g.groupby("family").apply(lambda t: (t["rank_change"] == 0).mean(), include_groups=False)
        share = float((g["rank_change"] == 0).mean())
        near = abs(share - STABLE_SHARE) < BORDER
        summ.append(dict(year=y, bank=b, base_score=base[i], base_rank=int(base_rank[i]),
                         min_rank=int(g["rank"].min()), max_rank=int(g["rank"].max()),
                         min_score=float(g["score"].min()), max_score=float(g["score"].max()),
                         n_scenarios=len(g), stable_share=share, stable_share_famavg=float(fam_share.mean()),
                         **{f"stable_{f[0]}": float(v) for f, v in fam_share.items()},
                         verdict=("Vững" if share >= STABLE_SHARE else "Nhóm cùng mức") + (" (sát ngưỡng)" if near else ""),
                         tier=tier[b]))
    summ = pd.DataFrame(summ)

    # Monte Carlo
    mc = monte_carlo(d["dbi"], dti0, a, rng, d["levels"])
    mcrows = []
    for name, R in mc.items():
        for i, b in enumerate(banks):
            for r in range(1, n + 1):
                mcrows.append(dict(year=y, method=name, bank=b, rank=r, prob=float((R[i] == r).mean())))
            summ.loc[summ.bank == b, f"p_base_{name}"] = float((R[i] == base_rank[i]).mean())
            summ.loc[summ.bank == b, f"meanrank_{name}"] = float(R[i].mean())
    mcdf = pd.DataFrame(mcrows)
    for name, R in mc.items():                                # P(bank_a xếp trên bank_b) theo Monte Carlo
        pair_df[f"mc_a_above [{name}]"] = [float((R[banks.index(r.bank_a)] < R[banks.index(r.bank_b)]).mean())
                                           for r in pair_df.itertuples()]

    # Kendall τ giữa 3 kỹ thuật chuẩn hóa
    zs = {"Cận cố định": z_matrix(d["x"], bounds), "Min-max": z_minmax(d["x"], bounds, a.nmin),
          "Xếp hạng %": z_rankpct(d["x"], bounds, a.nmin)}
    rk = {k: rank_of(total(pillar_p(d["dbi"], dti_by_pillar(z), a.w_dbi))) for k, z in zs.items()}
    nrm = pd.DataFrame([dict(year=y, a=p, b=q, kendall_tau=kendalltau(rk[p], rk[q]).statistic)
                        for p, q in itertools.combinations(rk, 2)])
    coverage = pd.DataFrame([dict(year=y, normalization=k, n_indicator_with_z=int((~np.isnan(z).all(axis=0)).sum()),
                                  n_cells=int((~np.isnan(z)).sum())) for k, z in zs.items()])
    return dict(long=long, kend=kend, summ=summ, mc=mcdf, pairs=pair_df, norm_tau=nrm, coverage=coverage,
                pert=pert, base=base)


def keyword_check(years):
    p = OUT / "tm_vs_dbi.csv"
    if not p.exists():
        return pd.DataFrame([dict(status="CHƯA CHẠY", note="Thiếu output_data/tm_vs_dbi.csv: cần data/text (bước 1-2), rồi "
                                  "`python 07_text_mining.py --compare`; chạy lại 11_sensitivity.py.")])
    t = pd.read_csv(p, encoding="utf-8-sig")
    t = t[t["pillar"] == "TẤT CẢ TRỤ"].copy()
    t["status"] = "đã có"
    return t[t["year"].astype(int).isin(years)] if len(t) else pd.DataFrame([dict(status="TRỐNG")])


# ----------------------------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--years", default="2025")
    ap.add_argument("--start-year", type=int, default=2021)
    ap.add_argument("--w-dbi", type=float, default=0.8)
    ap.add_argument("--n-mc", type=int, default=10000)
    ap.add_argument("--alpha", default="1,10", help="tham số tập trung Dirichlet (1 = đều trên đơn hình; lớn = sát 1/6)")
    ap.add_argument("--noise-q", type=float, default=0.25, help="xác suất mỗi tiêu chí rubric bị lệch ±1 mức")
    ap.add_argument("--nmin", type=int, default=3, help="số NH tối thiểu có dữ liệu để chuẩn hóa min-max/xếp hạng")
    ap.add_argument("--seed", type=int, default=2026)
    ap.add_argument("--coding", default=str(OUT / "coding_auto.xlsx"))
    ap.add_argument("--inputs", default=str(OUT / "dataset_clean" / "dti_inputs_confirmed.csv"))
    ap.add_argument("--app", default=str(OUT / "app_ratings.csv"))
    ap.add_argument("--audit", default=str(OUT / "manual_audit.xlsx"))
    ap.add_argument("--outdir", default=str(OUT / "sensitivity"))
    ap.add_argument("--no-plots", action="store_true")
    a = ap.parse_args()
    a.alpha = [float(v) for v in a.alpha.split(",")]
    years = [int(v) for v in a.years.split(",")]
    outdir = pathlib.Path(a.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    banks, bounds, meta, data = prepare(a, years)
    # hạt giống riêng từng năm: kết quả một năm không phụ thuộc danh sách --years
    res = {y: run_year(y, banks, bounds, meta, data[y], a, np.random.default_rng([a.seed, y])) for y in years}
    cat = lambda k: pd.concat([res[y][k] for y in years], ignore_index=True)
    tables = {"scenarios": cat("long"), "kendall_spearman": cat("kend"), "summary": cat("summ"),
              "montecarlo_rank_dist": cat("mc"), "pairs": cat("pairs"), "norm_tau": cat("norm_tau"),
              "norm_coverage": cat("coverage"), "keyword_vs_rubric": keyword_check(years),
              "step0_gate": pd.concat([data[y]["gate"] for y in years], ignore_index=True)}
    for k, t in tables.items():
        t.to_csv(outdir / f"sens_{k}.csv", index=False, encoding="utf-8-sig")
    with pd.ExcelWriter(outdir / "sensitivity_results.xlsx", engine="openpyxl") as xw:
        for k, t in tables.items():
            t.to_excel(xw, sheet_name=k[:31], index=False)
            ws = xw.sheets[k[:31]]
            for col in ws.columns:
                ws.column_dimensions[col[0].column_letter].width = min(40, max(10, max(len(str(c.value or "")) for c in col[:50]) + 2))

    # --- in kết quả ---
    for y in years:
        s = res[y]["summ"].sort_values("base_rank")
        print(f"\n=== Năm {y}: {s['n_scenarios'].iloc[0]} kịch bản rời rạc + Monte Carlo {a.n_mc:,} lần ===")
        show = s[["base_rank", "bank", "base_score", "min_rank", "max_rank", "stable_share", "verdict", "tier"]].copy()
        show["bank"] = show["bank"].map(lambda b: BANK_LABEL.get(b, b))
        print(show.to_string(index=False, float_format=lambda v: f"{v:.2f}"))
        mcc = [c for c in s.columns if c.startswith("p_base_")]
        print("\nXác suất giữ đúng hạng cơ sở (Monte Carlo):")
        print(s[["bank"] + mcc].rename(columns=lambda c: c.replace("p_base_", "")).to_string(index=False, float_format=lambda v: f"{v:.3f}"))
        print("\nKendall τ giữa các kỹ thuật chuẩn hóa:\n", res[y]["norm_tau"].to_string(index=False, float_format=lambda v: f"{v:.2f}"))
        cv = res[y]["coverage"]
        print("Số chỉ số DTI còn dữ liệu sau chuẩn hóa:", dict(zip(cv.normalization, cv.n_indicator_with_z)),
              f"(min-max/xếp hạng cần >= {a.nmin} NH có dữ liệu)")
    print("\nĐối chiếu rubric vs từ khóa:", tables["keyword_vs_rubric"].iloc[0].get("note", "xem sens_keyword_vs_rubric.csv"))
    if not a.no_plots:
        try:
            import sens_plots
            sens_plots.make(res[max(years)], banks, a, outdir, max(years))
        except ImportError as e:                                      # matplotlib là tùy chọn
            print("Bỏ qua biểu đồ:", e)
    print("\nĐã ghi ->", outdir)


if __name__ == "__main__":
    main()
