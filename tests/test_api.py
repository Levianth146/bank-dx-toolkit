"""Kiểm thử lớp API. Chạy từ thư mục gốc repo:   pytest tests/test_api.py -q
Dùng dữ liệu thật trong out/ (score_summary.csv, scores.csv, ...), nên đây cũng là phép đối chiếu
API <-> pipeline: nếu 10_score.py đổi công thức mà API không theo, test sẽ vỡ."""
import json
import math
import pathlib
import sys

import pytest
from fastapi.testclient import TestClient

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import pandas as pd  # noqa: E402

from api.main import app  # noqa: E402
from api.export_static import export  # noqa: E402
from api.services import DxService, _kendall_tau  # noqa: E402

client = TestClient(app)
V1 = "/api/v1"


def get(path, status=200):
    r = client.get(V1 + path)
    assert r.status_code == status, r.text
    return r.json()


def test_health_and_meta():
    h = get("/health")
    assert h["status"] == "ok" and len(h["banks"]) == 5 and h["years"] == [2020, 2021, 2022, 2023, 2024, 2025]
    m = get("/meta")
    assert m["framework"]["criteria"] == 24 and m["framework"]["dti_indicators"] == 11
    assert [p["code"] for p in m["pillars"]] == list("KSTOCD")
    assert sum(len(p["criteria"]) for p in m["pillars"]) == 24
    assert len(m["dti_indicators"]) == 11 and len(m["maturity_levels"]) == 5


def test_ranking_matches_pipeline_output():
    summ = pd.read_csv(ROOT / "out" / "score_summary.csv", encoding="utf-8-sig")
    for y in range(2020, 2026):
        items = get(f"/ranking?year={y}")["items"]
        exp = summ[summ.year == y].sort_values("rank")
        assert [i["bank"] for i in items] == exp["bank"].tolist()
        assert [i["rank"] for i in items] == exp["rank"].tolist()
        for i, (_, e) in zip(items, exp.iterrows()):
            assert abs(i["score"] - e["score"]) < 1e-3
            assert i["maturity_level"] == e["maturity_level"]
            assert abs(i["data_confidence"] - e["data_confidence"]) < 1e-3


def test_recomputed_score_equals_pipeline():
    """Score = trung bình 6 trụ cột P_k; P_k = 0,8·DBI + 0,2·DTI (thiếu DTI -> DBI)."""
    for it in get("/ranking?year=2025")["items"] + get("/ranking?year=2021")["items"]:
        pk = []
        for p in it["pillars"].values():
            exp = p["dbi"] if p["dti"] is None else 0.8 * p["dbi"] + 0.2 * p["dti"]
            assert abs(exp - p["p"]) < 1e-3
            pk.append(p["p"])
        assert abs(sum(pk) / 6 - it["score"]) < 1e-3


def test_missing_is_null_never_zero_and_no_nan_in_json():
    r = client.get(V1 + "/snapshot")
    assert "NaN" not in r.text and "Infinity" not in r.text
    json.loads(r.text, parse_constant=lambda c: pytest.fail(f"hằng số không hợp lệ {c}"))
    ag = next(i for i in get("/ranking?year=2020")["items"] if i["bank"] == "agribank")
    assert ag["pillars"]["K"]["dti"] is None and ag["pillars"]["K"]["dti_applied"] is False   # thiếu DTI -> null, không phải 0
    assert ag["pillars"]["D"]["dti"] is None and ag["pillars"]["D"]["n_dti_total"] == 0        # trụ cột D không có DTI
    ind = get("/dti-indicators?year=2020&bank=agribank")["items"]
    miss = [i for i in ind if not i["has_data"]]
    assert miss and all(i["z"] is None for i in miss)


def test_rank_change_and_sorting():
    items = get("/ranking?year=2025&sort_by=score&order=desc")["items"]
    assert [i["score"] for i in items] == sorted((i["score"] for i in items), reverse=True)
    first = get("/ranking?year=2020")["items"][0]
    assert first["score_change"] is None and first["rank_change"] is None
    tcb24 = next(i for i in get("/ranking?year=2024")["items"] if i["bank"] == "tcb")
    tcb25 = next(i for i in get("/ranking?year=2025")["items"] if i["bank"] == "tcb")
    assert tcb25["rank_change"] == tcb24["rank"] - tcb25["rank"]
    byk = get("/ranking?year=2025&sort_by=K")["items"]
    ks = [i["pillars"]["K"]["p"] for i in byk]
    assert ks == sorted(ks, reverse=True)


def test_trend():
    t = get("/trend?metric=score")
    assert t["years"] == [2020, 2021, 2022, 2023, 2024, 2025] and len(t["series"]) == 5
    assert all(len(s["points"]) == 6 for s in t["series"])
    assert t["warnings"]                              # độ phủ DTI thay đổi theo năm
    assert not get("/trend?metric=K&component=dbi")["warnings"]    # DBI không phụ thuộc độ phủ DTI
    sub = get("/trend?metric=T&banks=tcb,vcb&from_year=2023&to_year=2025")
    assert [s["bank"] for s in sub["series"]] == ["tcb", "vcb"] and sub["years"] == [2023, 2024, 2025]


def test_compare_and_groups():
    c = get("/compare?year=2025&banks=tcb,vcb")
    assert [b["bank"] for b in c["banks"]] == ["tcb", "vcb"] and len(c["radar"]) == 6
    assert set(c["leaders"]) <= set("KSTOCD")
    g = get("/group-comparison?year=2025")["items"]
    assert {x["group"] for x in g} == {"NHTM Nhà nước", "NHTM Cổ phần"}
    assert {x["n_banks"] for x in g} == {3, 2}


def test_criteria_and_evidence_rules():
    d = get("/banks/vcb/2025")
    assert len(d["criteria"]) == 24 and len(d["dti_indicators"]) == 11
    assert sum(d["highlights"]["criteria_score_distribution"].values()) == 24
    nm = [c for y in (2020, 2021) for c in get(f"/banks/agribank/{y}/criteria")["items"] if c["status"] == "no_mention"]
    assert nm
    for c in nm:                                       # luật 3b: không được gọi là "không công bố"
        assert c["score"] == 0 and "không tìm thấy đề cập" in c["status_label"]
    scored = [c for c in d["criteria"] if c["status"] == "scored"]
    assert scored and all(c["evidence"] and c["evidence"]["page"] for c in scored)
    assert all(c["pillar"] == "T" for c in get("/banks/vcb/2025/criteria?pillar=t")["items"])


def test_sensitivity_base_equals_pipeline_and_robust_flag():
    for y in (2022, 2025):
        s = get(f"/sensitivity?year={y}")
        base = {r["bank"]: r["by_scenario"][s["base_scenario"]]["rank"] for r in s["rows"]}
        official = {i["bank"]: i["rank"] for i in get(f"/ranking?year={y}")["items"]}
        assert base == official
        s100 = {r["bank"]: r["by_scenario"]["100/0"]["score"] for r in s["rows"]}
        assert all(v is not None for v in s100.values())
        for r in s["rows"]:
            assert r["stable_under_weights"] == (r["rank_stable_pct"] is not None and r["rank_stable_pct"] >= 0.8)


def test_kendall_tau():
    assert _kendall_tau([1, 2, 3], [1, 2, 3]) == 1
    assert _kendall_tau([1, 2, 3], [3, 2, 1]) == -1
    assert _kendall_tau([1, 1, 1], [1, 2, 3]) is None


def test_data_quality():
    d = get("/data-quality?year=2025")
    assert len(d["availability"]) == 5 and d["app_ratings"]
    assert all(0 < a["rating"] <= 5 for a in d["app_ratings"])


def test_errors_use_one_format():
    for path, status, code in [("/banks/xxx/2025", 404, "bank_not_found"), ("/ranking?year=2018", 422, "invalid_year"),
                               ("/ranking?sort_by=zz", 422, "invalid_sort"), ("/trend?metric=foo", 422, "invalid_metric"),
                               ("/trend?component=zz", 422, "invalid_component"), ("/ranking?year=abc", 422, "invalid_request"),
                               ("/banks/vcb/2025/criteria?pillar=X", 422, "invalid_pillar")]:
        assert get(path, status)["error"]["code"] == code


def test_cors_and_openapi():
    r = client.get(V1 + "/meta", headers={"Origin": "http://localhost:5173"})
    assert r.headers.get("access-control-allow-origin") in ("*", "http://localhost:5173")
    assert client.get("/openapi.json").status_code == 200


def test_data_reload_on_file_change(tmp_path):
    """Chạy lại 10_score.py (đổi mtime) thì API đọc dữ liệu mới, không cần restart."""
    import shutil
    from api.repository import DataStore
    for d in ("out", "config", "scripts"):
        shutil.copytree(ROOT / d, tmp_path / d, ignore=shutil.ignore_patterns("*.pdf", "dataset_clean", "dti_bounds_review*"))
    svc = DxService(DataStore(tmp_path))
    assert svc.ranking(2025)["items"][0]["bank"] == "tcb"
    p = tmp_path / "out" / "score_summary.csv"
    df = pd.read_csv(p, encoding="utf-8-sig")
    df.loc[(df.bank == "mb") & (df.year == 2025), "score"] = 99.0
    df.to_csv(p, index=False, encoding="utf-8-sig")
    assert svc.ranking(2025, sort_by="score", order="desc")["items"][0]["bank"] == "mb"


def test_missing_output_gives_503(tmp_path):
    from api.repository import DataStore
    from api.errors import DataNotReady
    (tmp_path / "out").mkdir(); (tmp_path / "config").mkdir()
    with pytest.raises(DataNotReady):
        DxService(DataStore(tmp_path)).years()


def test_static_export(tmp_path):
    n = export(tmp_path)
    assert n == len(list(tmp_path.rglob("*.json")))
    for f in tmp_path.rglob("*.json"):
        raw = f.read_bytes()
        assert not raw.startswith(b"\xef\xbb\xbf")              # JSON không BOM
        json.loads(raw.decode("utf-8"))
    assert (tmp_path / "banks" / "vcb" / "2025.json").exists() and (tmp_path / "trend" / "score.json").exists()
    assert json.loads((tmp_path / "ranking" / "2025.json").read_text(encoding="utf-8"))["items"][0]["rank"] == 1


# ================================================================ số liệu đầu vào, cận L/U, Lớp C, độ nhạy đầy đủ
def test_dti_inputs_trace_and_lookback():
    d = get("/dti-inputs?bank=tcb&year=2025&indicator=T-Q1")
    assert {i["variable"] for i in d["items"]} == {"software_gross_cost", "total_assets"}
    assert {i["year"] for i in d["items"]} == {2024, 2025}                  # bình quân tổng tài sản cần năm trước
    assert all(i["source_file"] and i["page"] and i["confirmed"] for i in d["items"])
    assert d["formula"]
    vcb = get("/dti-inputs?bank=vcb&year=2025&indicator=T-Q1&scope=all")["items"]       # VCB không công bố nguyên giá phần mềm
    sw = next(i for i in vcb if i["variable"] == "software_gross_cost" and i["year"] == 2025)
    assert sw["value"] is None and sw["missing_reason"] == "not_disclosed"
    oq1 = get("/dti-inputs?bank=vcb&year=2025&indicator=O-Q1")["items"]
    assert min(i["year"] for i in oq1) == 2020 and max(i["year"] for i in oq1) == 2025   # Δ từ đầu kỳ
    exact = get("/dti-inputs?bank=vcb&year=2025&variable=total_assets")["items"]
    assert [i["year"] for i in exact] == [2025]
    assert "app_ratings" in get("/dti-inputs?bank=tcb&indicator=K-Q3")["other_sources"]
    assert len(get("/dti-inputs?bank=tcb&year=2025&indicator=T-Q2")["other_sources"]["platform_checklist"]) == 8


def test_dti_inputs_missing_reason_and_scope():
    allrows = get("/dti-inputs?bank=agribank&scope=all")["items"]
    miss = [i for i in allrows if i["value"] is None]
    assert miss and all(i["missing_reason"] in ("not_disclosed", "not_collected") for i in miss)
    conf = get("/dti-inputs?bank=agribank")["items"]
    assert all(i["value"] is not None and i["confirmed"] for i in conf)
    get("/dti-inputs?scope=zz", 422)
    assert get("/dti-inputs?indicator=zz", 404)["error"]["code"] == "indicator_not_found"


def test_dti_input_values_match_pipeline_indicator():
    """Số đầu vào API trả ra phải tái tạo đúng chỉ số trong dti_indicators.csv (C-Q1 = nhân sự công nghệ / CBNV)."""
    ind = {(i["bank"], i["year"]): i for i in get("/dti-indicators?year=2025&pillar=C")["items"] if i["indicator"] == "C-Q1"}
    for b in ("vcb", "tcb", "mb", "bidv", "agribank"):
        rows = {i["variable"]: i["value"] for i in get(f"/dti-inputs?bank={b}&year=2025&indicator=C-Q1")["items"]}
        x = ind[(b, 2025)]["x"]
        if x is None:
            assert not {"tech_staff", "headcount"} <= set(rows)
        else:
            assert abs(rows["tech_staff"] / rows["headcount"] * 100 - x) < 1e-3


def test_bounds_detail():
    b = get("/dti-bounds")
    assert b["count"] == 11 and b["locked"] is True and b["version"]
    for it in b["items"]:
        assert it["L"] is not None and it["U"] is not None and it["rationale"] and it["status_label"]
        assert it["source_citation"] or it["status"] == "natural"            # thang tự nhiên (K-Q2) không cần trích dẫn
    assert any(it["reference_inputs"] for it in b["items"])                # có số liệu tham chiếu ngoài (ví dụ T-Q1)
    one = get("/dti-bounds/t-q1")
    assert one["count"] == 1 and one["items"][0]["code"] == "T-Q1"
    meta = {d["code"]: d for d in get("/meta")["dti_indicators"]}
    assert meta["T-Q1"]["formula"] and meta["T-Q1"]["input_variables"] == ["software_gross_cost", "total_assets"]


def test_layer_c_formulas():
    fp = get("/financial-performance")
    assert fp["count"] == 30
    row = next(i for i in fp["items"] if i["bank"] == "vcb" and i["year"] == 2025)
    inp = {i["variable"]: i for i in get("/dti-inputs?bank=vcb&year=2025&scope=confirmed")["items"] if i["year"] in (2024, 2025)}
    v = {(i["variable"], i["year"]): i["value"] for i in get("/dti-inputs?bank=vcb&scope=confirmed")["items"]}
    roe = v[("net_profit", 2025)] / ((v[("equity", 2025)] + v[("equity", 2024)]) / 2) * 100
    cir = abs(v[("opex", 2025)]) / (abs(v[("opex", 2025)]) + v[("op_profit_before_provision", 2025)]) * 100
    casa = v[("casa_deposits", 2025)] / v[("customer_deposits", 2025)] * 100
    assert abs(row["roe"] - roe) < 1e-3 and abs(row["cir"] - cir) < 1e-3 and abs(row["casa"] - casa) < 1e-3
    # CIR khớp đúng cách tính của 10_score.py
    S = DxService().S
    V, D = S.load_inputs(str(ROOT / "out" / "dataset_clean" / "dti_inputs_confirmed.csv"), False)
    calc = S.Calc(V, D, S.load_app_rating(str(ROOT / "out" / "app_ratings.csv")), S.load_platform(str(ROOT / "out" / "manual_audit.xlsx")), 2021, 2025)
    for b in ("vcb", "tcb", "mb"):
        r = next(i for i in fp["items"] if i["bank"] == b and i["year"] == 2025)
        assert abs(r["cir"] - calc.cir(b, 2025)) < 1e-2
    # thiếu số liệu -> null + cờ, không phải 0
    bidv = next(i for i in fp["items"] if i["bank"] == "bidv" and i["year"] == 2025)
    assert bidv["casa"] is None and any("casa" in f for f in bidv["flags"])
    ag20 = next(i for i in fp["items"] if i["bank"] == "agribank" and i["year"] == 2020)
    assert any("cuối kỳ" in f for f in ag20["flags"])                       # thiếu năm 2019 -> dùng số cuối kỳ


def test_layer_c_correlation():
    c = get("/layer-c/correlation")
    assert c["score_var"] == "dbi" and [m["metric"] for m in c["metrics"]] == ["roe", "roa", "cir", "casa", "non_interest_share"]
    cir = next(m for m in c["metrics"] if m["metric"] == "cir")
    assert cir["expected_sign"] == -1 and len(cir["by_year"]) == 6
    assert all(y["n"] <= 5 and y["low_n"] for y in cir["by_year"])          # n nhỏ luôn gắn cờ
    assert all(-1 <= y["spearman"] <= 1 for y in cir["by_year"] if y["spearman"] is not None)
    assert cir["pooled"]["n"] == 30 and cir["pooled_within_year"]["n"] > 0
    lag1 = get("/layer-c/correlation?lag=1")
    assert next(m for m in lag1["metrics"] if m["metric"] == "cir")["by_year"][-1]["n"] == 0    # 2025 không có cặp t+1
    assert get("/layer-c/correlation?score_var=score")["score_var"] == "score"
    assert get("/layer-c/correlation?score_var=zz", 422)["error"]["code"] == "invalid_score_var"
    # kiểm tra tay một hệ số: Spearman cùng năm 2025 giữa DBI và CIR
    from scipy.stats import spearmanr
    items = [i for i in get("/financial-performance?year=2025")["items"]]
    expect = spearmanr([i["dbi_mean"] for i in items], [i["cir"] for i in items]).statistic
    got = next(y for y in cir["by_year"] if y["year"] == 2025)["spearman"]
    assert abs(got - expect) < 1e-3


def test_sensitivity_full_matches_script_output():
    sf = get("/sensitivity/full?year=2025")
    assert sf["available_years"] == sorted(set(pd.read_csv(ROOT / "out" / "sensitivity" / "sens_scenarios.csv", encoding="utf-8-sig").year)) and sf["robust_threshold"] == 0.8
    official = {i["bank"]: i["rank"] for i in get("/ranking?year=2025")["items"]}
    scen = pd.read_csv(ROOT / "out" / "sensitivity" / "sens_scenarios.csv", encoding="utf-8-sig")
    scen = scen[(scen.year == 2025) & (scen.family != "0. Cơ sở")]
    for b in sf["banks"]:
        assert b["base_rank"] == official[b["bank"]]                         # hạng cơ sở khớp điểm chính thức
        assert abs(b["stable_share"] - (scen[scen.bank == b["bank"]].rank_change == 0).mean()) < 1e-3
        assert b["is_robust"] == (b["stable_share"] >= 0.8)
        assert sum(f["n_scenarios"] for f in b["stable_by_family"]) == b["n_scenarios"] == 40
        for m in b["monte_carlo"]:
            assert abs(sum(r["prob"] for r in m["rank_distribution"]) - 1) < 1e-3
    assert len(sf["pairs"]) == 10
    assert 2024 in sf["available_years"]                                    # độ nhạy đã chạy đủ 6 năm
    rows = get("/sensitivity/scenarios?year=2025&family=G.&bank=tcb")
    assert rows["count"] == 16 and all(r["family"].startswith("G.") and r["bank"] == "tcb" for r in rows["items"])


def test_sensitivity_full_missing_outputs(tmp_path):
    import shutil
    from api.repository import DataStore
    from api.errors import ApiError
    for d in ("out", "config", "scripts"):
        shutil.copytree(ROOT / d, tmp_path / d, ignore=shutil.ignore_patterns("*.pdf", "sensitivity", "dataset_clean", "dti_bounds_review*"))
    with pytest.raises(ApiError) as e:
        DxService(DataStore(tmp_path)).sensitivity_full(2025)
    assert e.value.code == "sensitivity_not_run"
