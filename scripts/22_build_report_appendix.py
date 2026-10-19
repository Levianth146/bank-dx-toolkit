"""Sinh các phụ lục của báo cáo từ cấu hình và kết quả hiện có, để phụ lục luôn khớp với dữ liệu.

Chạy từ thư mục scripts/:  python 22_build_report_appendix.py
Ghi vào report/phu_luc/:
  PL1_tieu_chi_cham_diem.md   24 tiêu chí DBI: rubric mức 0-4 và từ khóa định vị bằng chứng
  PL2_chi_so_DTI.md           11 chỉ số DTI: định nghĩa, chiều, cận L/U, nguồn, hạn chế
  PL3_nguon_du_lieu.md        Danh mục báo cáo công khai đã dùng (đường dẫn, ngày truy cập, mã băm)
  PL4_ket_qua_cham_diem.md    Điểm và mức từng ngân hàng, từng năm; điểm 6 trụ cột năm cuối
  PL5_do_phu_du_lieu.md       Độ phủ tài liệu và số liệu DTI theo ngân hàng-năm
Không sửa dữ liệu nguồn; chỉ đọc config/ và output_data/ rồi ghi Markdown."""
import csv
import pathlib
import sys

import yaml

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = pathlib.Path(__file__).resolve().parents[1]
CONF, OUT, DATA = ROOT / "config", ROOT / "output_data", ROOT / "data"
DEST = ROOT / "report" / "phu_luc"

PILLARS = {"K": "Khách hàng", "S": "Chiến lược", "T": "Công nghệ", "O": "Vận hành", "C": "Văn hóa", "D": "Dữ liệu"}
LEVEL0 = ("Không tìm thấy đề cập trong văn bản đã quét (`no_mention`). Đây là kết quả của phép tìm từ khóa, "
          "không chứng minh ngân hàng không thực hiện. Không có văn bản đọc được thì để trống (`no_document`).")
BANK_NAMES = {"agribank": "Agribank", "bidv": "BIDV", "vcb": "Vietcombank", "mb": "MB", "tcb": "Techcombank"}


def read_csv(path):
    with open(path, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def fnum(value, digits=1):
    try:
        return f"{float(value):.{digits}f}".replace(".", ",")
    except (TypeError, ValueError):
        return "—"


def cell(text):
    return str(text if text is not None else "").replace("|", "\\|").replace("\n", " ").strip()


def write(name, lines):
    DEST.mkdir(parents=True, exist_ok=True)
    (DEST / name).write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    print("ghi", (DEST / name).relative_to(ROOT))


def pl1():
    rubric = {}
    for r in read_csv(CONF / "rubric_anchors.csv"):
        rubric.setdefault(r["criterion"], {"name": r["name"], "levels": {}})["levels"][r["level"]] = r["text"]
    keywords = yaml.safe_load((CONF / "keywords.yaml").read_text(encoding="utf-8"))
    out = ["# Phụ lục 1. Tiêu chí chấm điểm DBI (24 tiêu chí)", "",
           "Mỗi tiêu chí chấm từ 0 đến 4. Bảng dưới đây là khung rubric (`config/rubric_anchors.csv`) và từ khóa "
           "dùng để định vị bằng chứng (`config/keywords.yaml`). Từ khóa song ngữ Việt - Anh. "
           "Cách thuật toán chuyển rubric thành điểm xem `specs/001-bank-dx-assessment/algorithm-scoring.md`.", "",
           "Điểm trụ cột `DBI_k` là trung bình 4 tiêu chí của trụ cột, đổi sang thang 0-100.", ""]
    for code, pname in PILLARS.items():
        out += [f"## Trụ cột {code} · {pname}", ""]
        for crit in sorted(c for c in rubric if c.startswith(code)):
            info = rubric[crit]
            out += [f"### {crit}. {info['name']}", "", "| Mức | Mô tả |", "|:-:|---|", f"| 0 | {cell(LEVEL0)} |"]
            for lv in ("1", "2", "3", "4"):
                out.append(f"| {lv} | {cell(info['levels'].get(lv, ''))} |")
            kws = (keywords.get(crit) or {}).get("keywords") or []
            out += ["", f"**Từ khóa định vị ({len(kws)}):** " + ", ".join(f"`{k}`" for k in kws), ""]
    write("PL1_tieu_chi_cham_diem.md", out)


STATUS_VI = {"sourced": "có nguồn trích dẫn", "derived": "suy ra từ dữ liệu có nguồn",
             "external_reference": "tham chiếu ngoài mẫu", "natural": "thang tự nhiên",
             "sample_percentile": "phân vị 10%/90% của mẫu gộp (thang tương đối)"}


def pl2():
    cfg = yaml.safe_load((CONF / "dti_bounds.yaml").read_text(encoding="utf-8"))
    out = ["# Phụ lục 2. Chỉ số DTI (11 chỉ số) và cận chuẩn hóa", "",
           f"Phiên bản cận: `{cfg.get('version')}` (khóa ngày {cfg.get('locked_on')}). "
           "Mỗi chỉ số được chuẩn hóa `z = 100 × clip((x − L) / (U − L), 0, 1)`; chỉ số `lower_better` đảo dấu.", "",
           "Phương pháp chọn cận và các hạn chế: `specs/001-bank-dx-assessment/dti-bounds-method.md`.", "",
           "| Mã | Chỉ số | Đơn vị | Chiều | L | U | Loại cận |", "|---|---|---|---|---:|---:|---|"]
    bounds = cfg.get("bounds", {})
    for code, b in bounds.items():
        out.append(f"| {code} | {cell(b.get('name'))} | {cell(b.get('unit'))} | {b.get('direction')} | "
                   f"{b.get('L')} | {b.get('U')} | {STATUS_VI.get(b.get('status'), b.get('status'))} |")
    out.append("")
    for code, b in bounds.items():
        out += [f"## {code}. {b.get('name')}", "", f"- **Biến nguồn:** `{b.get('variable')}`",
                f"- **Cận:** L = {b.get('L')}, U = {b.get('U')} ({STATUS_VI.get(b.get('status'), b.get('status'))})"]
        for c in b.get("source_citation") or []:
            out.append(f"- **Nguồn:** {c}")
        if b.get("rationale"):
            out.append(f"- **Lý do chọn cận:** {b['rationale']}")
        if b.get("caveat"):
            out.append(f"- **Hạn chế:** {b['caveat']}")
        out.append("")
    write("PL2_chi_so_DTI.md", out)


def pl3():
    manifest = read_csv(DATA / "raw" / "manifest.csv") if (DATA / "raw" / "manifest.csv").exists() else []
    sources = read_csv(CONF / "sources.csv")
    out = ["# Phụ lục 3. Nguồn dữ liệu", "",
           "Toàn bộ tài liệu là báo cáo công khai của ngân hàng. Danh mục nguồn nằm ở `config/sources.csv`; "
           "kết quả tải (ngày truy cập, mã băm sha256, kích thước) nằm ở `data/raw/manifest.csv`. "
           "File PDF gốc không đưa vào repository vì dung lượng lớn (khoảng 870 MB); chạy "
           "`python 01_download.py` để tải lại, hoặc đối chiếu bằng mã băm sha256 dưới đây.", "",
           "BCTN: báo cáo thường niên. BCTC: báo cáo tài chính hợp nhất đã kiểm toán. BCPTBV: báo cáo phát triển bền vững "
           "(tùy chọn; nhiều ngân hàng tích hợp trong BCTN).", ""]
    by = {(r["bank"], r["year"], r["doc_type"]): r for r in manifest}
    out += ["| Ngân hàng | Năm | Loại | Trạng thái | Ngày truy cập | sha256 (12 ký tự đầu) | Đường dẫn |", "|---|---|---|---|---|---|---|"]
    for s in sorted(sources, key=lambda r: (r["bank"], r["year"], r["doc_type"])):
        m = by.get((s["bank"], s["year"], s["doc_type"]))
        url = s.get("url", "").strip()
        if m:
            status, when, sha = m.get("status", ""), m.get("accessed_at", ""), (m.get("sha256") or "")[:12]
        else:
            status, when, sha = (s.get("notes") or "không có tệp").strip(), "", ""
        link = f"[liên kết]({url})" if url.startswith("http") else "—"
        out.append(f"| {BANK_NAMES.get(s['bank'], s['bank'])} | {s['year']} | {s['doc_type'].upper()} | "
                   f"{cell(status)} | {when} | {sha} | {link} |")
    out += ["", "Nguồn số liệu khác: điểm ứng dụng App Store và Google Play (`output_data/app_ratings.csv`, có ngày thu thập), "
            "kiểm kê 8 nền tảng số (`output_data/manual_audit.xlsx`), số liệu DTI đã đối chiếu PDF "
            "(`output_data/dti_inputs.csv`, kèm tệp, trang và định nghĩa)."]
    write("PL3_nguon_du_lieu.md", out)


def pl4():
    rows = read_csv(OUT / "score_summary.csv")
    pill = read_csv(OUT / "scores.csv")
    out = ["# Phụ lục 4. Kết quả chấm điểm", "",
           "Nguồn: `output_data/score_summary.csv` (điểm tổng và hạng), `output_data/scores.csv` (6 trụ cột). "
           "Điểm thang 0-100. Công thức: `P_k = 0,8·DBI_k + 0,2·DTI_k` (trụ cột không có DTI thì `P_k = DBI_k`); "
           "điểm ngân hàng là trung bình 6 trụ cột.", "",
           "**Lưu ý khi đọc:** số trụ cột nhận DTI khác nhau theo năm (0 trụ cột năm 2020-2021, ít trụ cột năm 2022-2024), "
           "nên điểm giữa các năm không hoàn toàn cùng cơ sở. Hạng sát nhau (dưới khoảng 3 điểm) chưa đủ cơ sở để phân biệt; "
           "xem phân tích độ vững ở `docs/sensitivity.md`.", ""]
    years = sorted({r["year"] for r in rows})
    for y in years:
        out += [f"## Năm {y}", "", "| Hạng | Ngân hàng | Điểm | Mức | Số chỉ số DTI có dữ liệu / dùng |", "|:-:|---|---:|---|:-:|"]
        for r in sorted((r for r in rows if r["year"] == y), key=lambda r: int(float(r["rank"] or 99))):
            out.append(f"| {r['rank']} | {BANK_NAMES.get(r['bank'], r['bank'])} | {fnum(r['score'], 2)} | "
                       f"{cell(r['maturity_level'])} | {r['n_dti_available']} / {r['n_dti_used']} |")
        out.append("")
    last = years[-1]
    out += [f"## Điểm 6 trụ cột năm {last}", "", "| Ngân hàng | " + " | ".join(PILLARS.values()) + " |",
            "|---|" + "---:|" * len(PILLARS)]
    for bank, name in BANK_NAMES.items():
        vals = {r["pillar"]: r["p"] for r in pill if r["bank"] == bank and r["year"] == last}
        out.append(f"| {name} | " + " | ".join(fnum(vals.get(p), 1) for p in PILLARS) + " |")
    out += ["", "Chi tiết DBI, DTI, số chỉ số DTI dùng từng trụ cột: `output_data/scores.csv`."]
    write("PL4_ket_qua_cham_diem.md", out)


def pl5():
    rows = read_csv(OUT / "availability_matrix.csv")
    out = ["# Phụ lục 5. Độ phủ dữ liệu", "",
           "Nguồn: `output_data/availability_matrix.csv`. `inputs_coverage` là tỷ lệ biến DTI thô đã có số liệu; "
           "`data_conf` là số chỉ số DTI tính được trước cổng bước 0 chia 11; `scoring_coverage` là số chỉ số thực sự dùng "
           "để tính điểm sau hai cổng bước 0 và 0b, chia 11. Ô thiếu luôn để trống, không điền 0.", "",
           "| Ngân hàng | Năm | BCTN | BCTC | BCPTBV | Biến DTI có số liệu | Chỉ số DTI tính được | Chỉ số DTI dùng chấm điểm |",
           "|---|---|---|---|---|:-:|:-:|:-:|"]
    for r in sorted(rows, key=lambda r: (r["bank"], r["year"])):
        out.append(f"| {BANK_NAMES.get(r['bank'], r['bank'])} | {r['year']} | {cell(r['bctn'])} | {cell(r['bctc'])} | "
                   f"{cell(r['bcptbv'])} | {r['dti_vars_filled']}/{r['dti_vars_total']} | {r['dti_ind_computable']} | {r['dti_ind_used']} |")
    out += ["", "Cổng bước 0 và 0b, cùng lý do loại từng ô: `output_data/step0_gate.csv` và cột `step0b_excluded` "
            "trong `output_data/dti_indicators.csv`."]
    write("PL5_do_phu_du_lieu.md", out)


if __name__ == "__main__":
    for fn in (pl1, pl2, pl3, pl4, pl5):
        fn()
