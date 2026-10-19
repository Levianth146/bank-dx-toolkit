"""Kiểm thử 11_sensitivity.py. Chạy từ thư mục scripts/:  python ../tests/test_sensitivity.py"""
import argparse, importlib.util, pathlib, sys
import numpy as np, pandas as pd

SC = pathlib.Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SC))
def load(name, file):
    spec = importlib.util.spec_from_file_location(name, SC / file)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
S10, SE = load("score10t", "10_score.py"), load("sens11t", "11_sensitivity.py")

fails = []
def check(name, cond):
    print(("OK   " if cond else "FAIL ") + name)
    if not cond: fails.append(name)

# 1. Cơ sở khớp 10_score.py (điểm chính thức đã commit trong output_data/score_summary.csv)
OUT = SE.OUT
a = argparse.Namespace(coding=str(OUT / "coding_auto.xlsx"), inputs=str(OUT / "dataset_clean" / "dti_inputs_confirmed.csv"),
                       app=str(OUT / "app_ratings.csv"), audit=str(OUT / "manual_audit.xlsx"), start_year=2021,
                       w_dbi=0.8, nmin=3, alpha=[1.0], noise_q=0.25, n_mc=2000)
banks, bounds, meta, data = SE.prepare(a, [2025])
d = data[2025]
base, sc, pert, dti0 = SE.build_scenarios(d, bounds, meta, a)
off = pd.read_csv(OUT / "score_summary.csv", encoding="utf-8-sig"); off = off[off.year == 2025].set_index("bank")["score"]
check("điểm cơ sở khớp score_summary.csv (2025)", all(abs(base[i] - off[b]) < 1e-9 for i, b in enumerate(banks)))
ind = pd.read_csv(OUT / "dti_indicators.csv", encoding="utf-8-sig"); ind = ind[ind.year == 2025]
z = SE.z_matrix(d["x"], bounds)
ok = all((np.isnan(z[banks.index(r.bank), SE.IND.index(r.indicator)]) if pd.isna(r.z)
         else abs(z[banks.index(r.bank), SE.IND.index(r.indicator)] - r.z) < 1e-9) for r in ind.itertuples())
check("z chuẩn hóa cố định khớp dti_indicators.csv", ok)

# Bước 0 phải khớp điểm chính thức ở cả 6 năm, kể cả khi chạy riêng năm lịch sử.
years = list(range(2020, 2026))
all_banks, _, _, all_data = SE.prepare(a, years)
official = pd.read_csv(OUT / "score_summary.csv").set_index(["year", "bank"])
official_ind = pd.read_csv(OUT / "dti_indicators.csv")
for year in years:
    dy = all_data[year]
    by, _, _, _ = SE.build_scenarios(dy, bounds, meta, a)
    check(f"bước 0: điểm và hạng cơ sở khớp chính thức {year}",
          all(abs(by[i] - official.loc[(year, bank), "score"]) < 1e-9
              and SE.rank_of(by)[i] == official.loc[(year, bank), "rank"]
              for i, bank in enumerate(all_banks)))
    zy = SE.z_matrix(dy["x"], bounds)
    expected = official_ind[official_ind.year == year].pivot(index="bank", columns="indicator", values="z").loc[all_banks, SE.IND].to_numpy()
    check(f"bước 0: z khớp chính thức {year}", np.allclose(zy, expected, equal_nan=True))
    _, _, _, single = SE.prepare(a, [year])
    check(f"chạy riêng {year} không đổi dữ liệu DTI", np.allclose(single[year]["x"], dy["x"], equal_nan=True))

retained = np.ones(len(SE.IND), dtype=bool)
retained[:3] = False
zero_test = SE.dti_by_pillar(np.full((5, len(SE.IND)), np.nan), "zero", retained)
check("thiếu = 0 không phục hồi chỉ số đã loại ở bước 0", np.isnan(zero_test[:, 0]).all() and (zero_test[:, 1] == 0).all())

# 2. Kịch bản trọng số 70/30 khớp S.pillar_scores
b = banks[0]; i = 0
dbi_c = {c: d["levels"][i, k] / 4 * 100 for k, c in enumerate(S10.CRITERIA)}
z_i = {ind_: (None if np.isnan(z[i, j]) else z[i, j]) for j, ind_ in enumerate(SE.IND)}
ps = S10.pillar_scores(dbi_c, z_i, 0.7)
check("70/30 khớp pillar_scores của 10_score.py", abs(S10.score_total(ps) - SE.total(SE.pillar_p(d["dbi"], dti0, 0.7))[i]) < 1e-9)
fam = {f: n for f, n in ((f, sum(1 for g, *_ in sc if g == f)) for f in {g for g, *_ in sc})}
check("40 kịch bản rời rạc (3+12+2+6+1+2+14)", sum(fam.values()) == 40)

# 3. Loại trụ cột = trung bình đều 5 trụ còn lại
p = SE.pillar_p(d["dbi"], dti0, 0.8)
w = np.ones(6); w[0] = 0
check("loại 1 trụ = trung bình 5 trụ còn lại", np.allclose(SE.total(p, w), p[:, 1:].mean(axis=1)))

# 4. Thiếu = 0 chỉ có trong 11_sensitivity; quy trình chính thức vẫn cấm
try:
    S10.pillar_scores({c: 50.0 for c in S10.CRITERIA}, {i_: None for i_ in S10.ALL_DTI}, 0.8, missing="zero"); raised = False
except ValueError:
    raised = True
check("10_score.py vẫn cấm điền 0 cho DTI thiếu", raised)
zz = np.array([[np.nan, 50.0]]); dti = SE.dti_by_pillar(np.full((1, 11), np.nan), "zero")
check("thiếu = 0: trụ có chỉ số DTI -> DTI_k = 0; trụ D vẫn NaN", dti[0, 0] == 0 and np.isnan(dti[0, 5]))
check("thiếu = bỏ: không có dữ liệu -> NaN -> P_k = DBI_k",
      np.isnan(SE.dti_by_pillar(np.full((1, 11), np.nan))[0, 0]))

# 5. Chuẩn hóa min-max / xếp hạng trên dữ liệu giả
x = np.full((5, 11), np.nan); x[:, 0] = [10, 20, 30, 40, 50]; x[:2, 1] = [1, 2]
bd = {k: (0, 100, "higher_better") for k in SE.IND}; bd["K-Q2"] = (0, 100, "lower_better")
zm = SE.z_minmax(x, bd, 3); zr = SE.z_rankpct(x, bd, 3)
check("min-max: 10 -> 0, 50 -> 100", zm[0, 0] == 0 and zm[4, 0] == 100)
check("xếp hạng %: hạng thấp nhất 0, cao nhất 100", zr[0, 0] == 0 and zr[4, 0] == 100)
check("chỉ số < nmin ngân hàng -> thiếu", np.isnan(zm[:, 1]).all() and np.isnan(zr[:, 1]).all())
check("chỉ số nghịch đảo chiều", SE.z_minmax(np.where(np.arange(11) == 0, x[:, [0]], np.nan)[:, :11].copy(), {**bd, "K-Q1": (0, 100, "lower_better")}, 3)[0, 0] == 100)

# 6. Dịch cận giữ đầu 'kém nhất'
sb = SE.scale_bounds({"K-Q1": (0, 90, "higher_better"), "O-Q1": (-0.6, 0, "lower_better")}, {}, ["K-Q1", "O-Q1"], 1.2)
check("higher_better: giữ L, giãn U", sb["K-Q1"][0] == 0 and abs(sb["K-Q1"][1] - 108.0) < 1e-9)
check("lower_better: giữ U (đầu kém), giãn L", abs(sb["O-Q1"][0] + 0.72) < 1e-12 and sb["O-Q1"][1] == 0)

# 7. Hạng, nhóm cùng mức, Monte Carlo
check("hòa điểm -> cùng hạng (method=min)", list(SE.rank_of(np.array([3.0, 3.0, 1.0]))) == [1, 1, 3])
scen = [np.array([3.0, 2.9, 1.0]), np.array([2.9, 3.0, 1.0]), np.array([3.0, 2.9, 1.0])]
pairs, tier = SE.tier_groups(scen, np.array([3.0, 2.9, 1.0]), np.array([1, 2, 3]), ["a", "b", "c"], {"a", "b"})
check("a,b đảo chỗ và không vững -> cùng nhóm; c độc lập", tier["a"] == tier["b"] and tier["c"].startswith("Độc lập"))
rng = np.random.default_rng(1)
mc = SE.monte_carlo(d["dbi"], dti0, a, rng, d["levels"])
ok = all(np.all((R >= 1) & (R <= len(banks))) and R.shape == (len(banks), a.n_mc) for R in mc.values())
check("Monte Carlo: hạng thuộc 1..n, đúng kích thước", ok)
R = list(mc.values())[0]
check("mỗi lần mô phỏng có ít nhất một ngân hàng hạng 1", (R.min(axis=0) == 1).all())

print("\nTất cả đạt." if not fails else f"\n{len(fails)} lỗi: {fails}")
sys.exit(1 if fails else 0)
