"""Xuất toàn bộ phản hồi API ra các tệp JSON tĩnh, để frontend triển khai không cần server Python
(GitHub Pages, Vercel, Netlify, hoặc mở trực tiếp trong Google AI Studio/Stitch).

    python -m api.export_static                     # ghi vào api/static/v1/
    python -m api.export_static --out docs/data     # đổi thư mục đích

Cấu trúc tệp (cùng nội dung với endpoint tương ứng):
    meta.json  snapshot.json  group-comparison.json  data-quality.json
    ranking/<năm>.json  compare/<năm>.json  sensitivity/<năm>.json  dti-indicators/<năm>.json
    trend/<metric>.json            metric: score, data_confidence, K, S, T, O, C, D (cả 5 ngân hàng)
    banks/<bank>.json              hồ sơ và lịch sử
    dti-bounds.json  financial-performance.json  layer-c/correlation-<dbi|score>-lag<0|1>.json
    sensitivity-full/<năm>.json  sensitivity-scenarios/<năm>.json   (chỉ các năm đã chạy 11_sensitivity.py)
    dti-inputs/<bank>.json         mọi số liệu đầu vào kèm nguồn (scope=all)
    banks/<bank>/<năm>.json        chi tiết 6 trụ cột, 24 tiêu chí kèm bằng chứng, 11 chỉ số DTI
JSON ghi bằng UTF-8 không BOM (BOM làm hỏng JSON.parse), khác với CSV của pipeline dùng utf-8-sig.
"""
import argparse
import json
import pathlib

from .config import ROOT
from .errors import ApiError
from .services import DxService


def _write(path: pathlib.Path, obj) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=1, allow_nan=False), encoding="utf-8")
    return 1


def export(out_dir: pathlib.Path, svc: DxService | None = None) -> int:
    svc = svc or DxService()
    n = 0
    n += _write(out_dir / "meta.json", svc.meta())
    n += _write(out_dir / "snapshot.json", svc.snapshot())
    n += _write(out_dir / "group-comparison.json", svc.group_comparison())
    n += _write(out_dir / "data-quality.json", svc.data_quality())
    for m in ("score", "data_confidence", *svc.PILLARS):
        n += _write(out_dir / "trend" / f"{m}.json", svc.trend(metric=m))
    for y in svc.years():
        n += _write(out_dir / "ranking" / f"{y}.json", svc.ranking(y))
        n += _write(out_dir / "compare" / f"{y}.json", svc.compare(y))
        n += _write(out_dir / "sensitivity" / f"{y}.json", svc.sensitivity(y))
        n += _write(out_dir / "dti-indicators" / f"{y}.json", svc.dti_indicators(y))
    n += _write(out_dir / "dti-bounds.json", svc.dti_bounds())
    n += _write(out_dir / "financial-performance.json", svc.financial_performance())
    for sv in ("dbi", "score"):
        for lag in (0, 1):
            n += _write(out_dir / "layer-c" / f"correlation-{sv}-lag{lag}.json", svc.layer_c_correlation(sv, lag))
    try:                                           # chỉ có khi đã chạy 11_sensitivity.py
        for y in svc.sensitivity_years():
            n += _write(out_dir / "sensitivity-full" / f"{y}.json", svc.sensitivity_full(y))
            n += _write(out_dir / "sensitivity-scenarios" / f"{y}.json", svc.sensitivity_scenarios(y))
    except ApiError:
        pass
    for b in svc.bank_ids():
        n += _write(out_dir / "dti-inputs" / f"{b}.json", svc.dti_inputs(bank=b, scope="all"))
        n += _write(out_dir / "banks" / f"{b}.json", svc.bank_profile(b))
        for y in svc.years():
            n += _write(out_dir / "banks" / b / f"{y}.json", svc.bank_detail(b, y))
    return n


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=str(ROOT / "api" / "static" / "v1"), help="thư mục đích")
    a = ap.parse_args()
    out = pathlib.Path(a.out)
    n = export(out)
    print(f"Đã ghi {n} tệp JSON vào {out}")


if __name__ == "__main__":
    main()
