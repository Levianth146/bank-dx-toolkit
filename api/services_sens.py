"""Kết quả phân tích độ nhạy ĐẦY ĐỦ do scripts/11_sensitivity.py ghi ra out/sensitivity/ (nguồn có thẩm quyền).

Khác endpoint /sensitivity (nhanh, chỉ kịch bản trọng số DBI/DTI, mọi năm): ở đây gồm trọng số trụ cột ±20% và Dirichlet,
kỹ thuật chuẩn hóa, loại từng trụ, thiếu = 0, dịch cận L/U, nhiễu rubric; kết luận "Vững" / "Nhóm cùng mức" theo docx V.2
(giữ nguyên hạng trong >= 80% kịch bản rời rạc A–D, F, G). 11_sensitivity.py mặc định chỉ chạy một số năm (README: 2021, 2023, 2025).
"""
import pandas as pd

from .config import BANK_GROUPS
from .errors import ApiError
from .serialize import integer, num, text

STABLE_SHARE = 0.80


class SensitivityMixin:
    def sensitivity_years(self) -> list[int]:
        s = self.store.sens("summary")
        return sorted(int(y) for y in s["year"].unique()) if not s.empty else []

    def _sens_year(self, year):
        ys = self.sensitivity_years()
        if not ys:
            raise ApiError(404, "sensitivity_not_run",
                           "Chưa có out/sensitivity/. Chạy `python 11_sensitivity.py --years 2021,2023,2025` trong thư mục scripts/.")
        if year is None:
            return ys[-1]
        if year not in ys:
            raise ApiError(404, "sensitivity_year_not_run",
                           f"Chưa chạy 11_sensitivity.py cho năm {year}; đã có: {ys}. Thêm năm bằng --years.")
        return int(year)

    def sensitivity_full(self, year=None) -> dict:
        year = self._sens_year(year)
        summ = self.store.sens("summary")
        summ = summ[summ["year"].astype(int) == year]
        scen = self.store.sens("scenarios")
        scen = scen[(scen["year"].astype(int) == year) & (scen["family"] != "0. Cơ sở")]
        mc = self.store.sens("montecarlo_rank_dist")
        mc = mc[mc["year"].astype(int) == year] if not mc.empty else mc
        mc_methods = sorted({c[len("p_base_"):] for c in summ.columns if c.startswith("p_base_")})

        banks = []
        for r in summ.sort_values("base_rank").to_dict("records"):
            b = str(r["bank"]).lower()
            g = scen[scen["bank"] == b]
            fam = [dict(family=f, n_scenarios=int(len(t)), share=num((t["rank_change"] == 0).mean()))
                   for f, t in g.groupby("family")]
            mcs = []
            for m in mc_methods:
                dist = mc[(mc["bank"] == b) & (mc["method"] == m)].sort_values("rank") if not mc.empty else mc
                mcs.append(dict(method=m, p_base=num(r.get(f"p_base_{m}")), mean_rank=num(r.get(f"meanrank_{m}")),
                                rank_distribution=[dict(rank=int(x.rank), prob=num(x.prob)) for x in dist.itertuples(index=False)]))
            verdict = text(r["verdict"])
            banks.append(dict(
                bank=b, bank_name=self.bank_name(b), group=BANK_GROUPS.get(b), base_score=num(r["base_score"]),
                base_rank=integer(r["base_rank"]), min_rank=integer(r["min_rank"]), max_rank=integer(r["max_rank"]),
                min_score=num(r["min_score"]), max_score=num(r["max_score"]), n_scenarios=integer(r["n_scenarios"]),
                stable_share=num(r["stable_share"]), verdict=verdict, is_robust=bool(verdict and verdict.startswith("Vững")),
                borderline=bool(verdict and "sát ngưỡng" in verdict), tier=text(r["tier"]),
                stable_by_family=fam, monte_carlo=mcs))

        pairs = self.store.sens("pairs")
        pairs = pairs[pairs["year"].astype(int) == year]
        prow = []
        for r in pairs.to_dict("records"):
            prow.append(dict(
                bank_a=r["bank_a"], bank_b=r["bank_b"], share_a_above=num(r["share_a_above"]), share_b_above=num(r["share_b_above"]),
                share_tie=num(r["share_tie"]), distinguishable=bool(r["distinguishable"]), borderline=bool(r["borderline"]),
                swapped_in_some_scenario=bool(r["swapped_in_some_scenario"]),
                monte_carlo_a_above={m: num(r.get(f"mc_a_above [{m}]")) for m in mc_methods}))

        ks = self.store.sens("kendall_spearman")
        ks = ks[ks["year"].astype(int) == year]
        nt, nc = self.store.sens("norm_tau"), self.store.sens("norm_coverage")
        kw = self.store.sens("keyword_vs_rubric")
        return dict(
            year=year, available_years=self.sensitivity_years(), robust_threshold=STABLE_SHARE,
            n_discrete_scenarios=int(len(scen.groupby(["family", "scenario"]))), banks=banks, pairs=prow,
            rank_agreement=[dict(family=r["family"], scenario=r["scenario"], kendall_tau=num(r["kendall_tau"]),
                                 spearman_rho=num(r["spearman_rho"]), n_rank_changes=integer(r["n_rank_changes"]))
                            for r in ks.to_dict("records")],
            normalization=dict(
                kendall_tau=[dict(a=r["a"], b=r["b"], kendall_tau=num(r["kendall_tau"])) for r in nt[nt["year"].astype(int) == year].to_dict("records")],
                coverage=[dict(normalization=r["normalization"], n_indicator_with_z=integer(r["n_indicator_with_z"]), n_cells=integer(r["n_cells"]))
                          for r in nc[nc["year"].astype(int) == year].to_dict("records")]),
            keyword_vs_rubric=[{k: (None if pd.isna(v) else v) for k, v in r.items()} for r in kw.to_dict("records")],
            note=("Có thẩm quyền hơn /sensitivity (chỉ kịch bản trọng số). Hạng 'Vững' khi giữ nguyên trong >= 80% kịch bản rời rạc; "
                  "ngân hàng đổi hạng nhiều hơn được gộp 'Nhóm cùng mức'. Thành phần Monte Carlo chỉ mô tả xác suất."))

    def sensitivity_scenarios(self, year=None, family=None, bank=None) -> dict:
        year = self._sens_year(year)
        bank = self._bank(bank) if bank else None
        s = self.store.sens("scenarios")
        s = s[s["year"].astype(int) == year]
        if family:
            s = s[s["family"].astype(str).str.startswith(str(family).strip())]
        if bank:
            s = s[s["bank"].astype(str).str.lower() == bank]
        items = [dict(year=year, family=r["family"], scenario=r["scenario"], bank=str(r["bank"]).lower(), score=num(r["score"]),
                      rank=integer(r["rank"]), base_rank=integer(r["base_rank"]), rank_change=integer(r["rank_change"]))
                 for r in s.to_dict("records")]
        return dict(year=year, available_years=self.sensitivity_years(), count=len(items), items=items)
