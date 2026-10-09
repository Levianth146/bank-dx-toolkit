"""Ma trận sẵn có dữ liệu + gợi ý điền dti_inputs + gói bàn giao dataset sạch.
  python 12_appendix.py                 # out/availability_matrix.csv  (NH x năm: tài liệu, trích text, số liệu DTI, chấm điểm, app)
  python 12_appendix.py --prefill       # out/dti_prefill.csv: số GỢI Ý từ financial_candidates.csv (CHƯA xác nhận, không ghi đè dti_inputs.csv)
  python 12_appendix.py --pages         # out/statement_pages.csv: trang CĐKT/KQKD/thuyết minh trong từng BCTC để mở PDF đọc tay
  python 12_appendix.py --bundle        # out/dataset_clean/: chỉ số liệu ĐÃ xác nhận + điểm chấm 'final' + app + ma trận + từ điển dữ liệu
Quy tắc: ô trống = không có dữ liệu (KHÔNG điền 0). data_conf = số chỉ số DTI TÍNH ĐƯỢC / 11."""
import csv, shutil, sys
import pandas as pd
from common import *

def rd(p):
    """Đọc CSV; nếu lệch số cột (append cũ) thử engine python / bỏ dòng lỗi."""
    if not p.exists():
        return pd.DataFrame()
    try:
        return pd.read_csv(p, encoding="utf-8-sig")
    except pd.errors.ParserError:
        return pd.read_csv(p, encoding="utf-8-sig", engine="python", on_bad_lines="warn")

def rd_extraction_report(p):
    """Chuẩn hóa extraction_report (header cũ 11 cột ↔ mới có bad_pages)."""
    if not p.exists():
        return pd.DataFrame()
    cols = ["file", "bank", "year", "doc_type", "pages", "pages_ocr", "avg_chars", "avg_junk",
            "engines_used", "flag", "lang", "bad_pages"]
    rows = []
    with open(p, newline="", encoding="utf-8-sig") as f:
        r = csv.reader(f)
        header = next(r, None) or []
        for row in r:
            d = dict(zip(header, row))
            if len(row) > len(header) and "bad_pages" not in header:
                d["lang"] = row[10] if len(row) > 10 else d.get("lang", "")
                d["bad_pages"] = row[11] if len(row) > 11 else ""
            rows.append({c: d.get(c, "") for c in cols})
    return pd.DataFrame(rows, columns=cols) if rows else pd.DataFrame(columns=cols)

banks = load_yaml("banks.yaml"); BK = list(banks["banks"]); YEARS = banks["years"]; CY = banks.get("coding_years", [])
src = rd(CONF / "sources.csv"); man = rd(DATA / "raw" / "manifest.csv")
rep = rd_extraction_report(OUT / "extraction_report.csv")
dti = rd(OUT / "dti_inputs.csv"); app = rd(OUT / "app_ratings.csv")
for df in (src, man, rep, dti):
    if len(df): df["year"] = df["year"].astype(int)
if len(rep): rep["doc_type"] = rep["doc_type"].astype(str)

def doc_state(b, y, t):
    s = src[(src.bank == b) & (src.year == y) & (src.doc_type == t)] if len(src) else []
    url = isinstance(s.iloc[0]["url"], str) and s.iloc[0]["url"].strip() if len(s) else ""
    note = s.iloc[0]["notes"] if len(s) and isinstance(s.iloc[0]["notes"], str) else ""
    if not url: return note or ("CHƯA ĐIỀN" if t != "bcptbv" else "chưa tìm thấy")
    r = rep[(rep.bank == b) & (rep.year == y) & (rep.doc_type == t)] if len(rep) else []
    if len(r): return "OK" if str(r.iloc[0]["flag"]).startswith("OK") else "CẦN KIỂM"
    m = man[(man.bank == b) & (man.year == y) & (man.doc_type == t)] if len(man) and "doc_type" in man else []
    return "đã tải, chưa trích" if len(m) else "có link, chưa tải"

LAG = 1   # Δ / CAGR tính so với năm liền trước — ĐỐI CHIẾU định nghĩa S-Q1, S-Q2, O-Q1, O-Q2 trong spec; đổi số này nếu cửa sổ khác
DEF = {}; DEFT = {}; HASDEF = False   # (bank, year) -> definition của digital_customers (nạp trong matrix())
AUX = {"digital_customer_share", "nci"}   # biến phụ, không tính vào inputs_coverage
IND = ["K-Q1", "K-Q2", "K-Q3", "S-Q1", "S-Q2", "T-Q1", "T-Q2", "O-Q1", "O-Q2", "C-Q1", "C-Q2"]

def computable(V, b, y, has_app):
    """Chỉ số DTI TÍNH ĐƯỢC từ dữ liệu hiện có (đủ biến đầu vào). T-Q2 (checklist 8 nền tảng) chưa có nguồn nên luôn 0.
    K-Q3 (app rating) chỉ là ảnh chụp 1 ngày -> chỉ tính cho năm cuối của kỳ phân tích."""
    g = lambda yy, n: V.get((b, yy, n))
    def cir(yy):
        o, p = g(yy, "opex"), g(yy, "op_profit_before_provision")
        return o / (o + p) if o and p and o + p > 0 else None
    def ipe(yy):
        o, p, h = g(yy, "opex"), g(yy, "op_profit_before_provision"), g(yy, "headcount")
        return (o + p) / h if o and p and h else None
    dc, tc, y0 = g(y, "digital_customers"), g(y, "total_customers"), y - LAG
    def sq2(yy):   # CAGR trên cửa sổ dài nhất: điểm sớm nhất cách >=2 năm, CÙNG definition (nếu có cột definition)
        if not g(yy, "digital_customers"): return False
        for y1 in range(min(YEARS), yy - 1):
            if g(y1, "digital_customers") and (not HASDEF or (DEF.get((b, yy)) and DEF.get((b, yy)) == DEF.get((b, y1)))): return True
        return False
    f = {"K-Q1": g(y, "digital_txn_share") is not None,
         "K-Q2": g(y, "digital_customer_share") is not None or bool(dc and tc and dc < tc),   # 2 cách: % công bố HOẶC KH số / tổng KH (dc == tc = cùng số chép hai lần -> không tính)
         "K-Q3": bool(has_app and y == max(YEARS)),
         "S-Q1": g(y, "digital_txn_share") is not None and g(y0, "digital_txn_share") is not None and (not HASDEF or (DEFT.get((b, y)) is not None and DEFT.get((b, y)) == DEFT.get((b, y0)))),   # cùng definition mới tính Δ
         "S-Q2": sq2(y),
         "T-Q1": bool(g(y, "software_gross_cost") and g(y, "total_assets")),
         "T-Q2": False,
         "O-Q1": cir(y) is not None and cir(y0) is not None,
         "O-Q2": ipe(y) is not None and ipe(y0) is not None,
         "C-Q1": bool(g(y, "tech_staff") and g(y, "headcount")),
         "C-Q2": g(y, "training_hours_per_head") is not None}
    return f

def matrix():
    rows = []
    V = {}
    global DEF, DEFT, HASDEF
    HASDEF = bool(len(dti)) and "definition" in dti.columns
    DEF = {(r["bank"], int(r["year"])): r["definition"] for _, r in dti[dti["variable"] == "digital_customers"].iterrows() if isinstance(r.get("definition"), str)} if HASDEF else {}
    DEFT = {(r["bank"], int(r["year"])): r["definition"] for _, r in dti[(dti["variable"] == "digital_txn_share") & dti["value"].notna()].iterrows() if isinstance(r.get("definition"), str)} if HASDEF else {}
    if len(dti):
        for _, r in dti[dti["value"].notna()].iterrows(): V[(r["bank"], int(r["year"]), r["variable"])] = float(r["value"])
    for b in BK:
        has_app = bool(len(app) and "bank" in app and (app.bank == b).any())
        for y in YEARS:
            d = dti[(dti.bank == b) & (dti.year == y) & ~dti.variable.isin(AUX)] if len(dti) else pd.DataFrame()
            nv = int(d["value"].notna().sum()) if len(d) else 0; nt = len(d)
            nc = int((d["value"].notna() & d["confirmed_by"].notna() & (d["confirmed_by"] != "auto-unverified")).sum()) if len(d) else 0
            npdf = int((d["value"].notna() & ~d["confirmed_by"].isin(["auto-unverified", "range-checked"]) & d["confirmed_by"].notna()).sum()) if len(d) else 0
            ar = int(((app.bank == b) & (app.get("year", y) == y)).sum()) if len(app) and "bank" in app else 0
            f = computable(V, b, y, has_app); n = sum(f.values())
            rows.append({"bank": b, "year": y, "bctn": doc_state(b, y, "bctn"), "bctc": doc_state(b, y, "bctc"), "bcptbv": doc_state(b, y, "bcptbv"),
                         "dti_vars_total": nt, "dti_vars_filled": nv, "dti_vars_confirmed": nc, "dti_vars_pdf_read": npdf,
                         "dti_vars_not_collected": int((d["value"].isna() & d["note"].fillna("").str.startswith("not_collected")).sum()) if len(d) else 0,
                         "inputs_coverage": round(nv / nt, 3) if nt else "",
                         "dti_ind_computable": n, "dti_ind_list": ";".join(k for k, v in f.items() if v),
                         "data_conf": round(n / len(IND), 3), "in_coding_years": y in CY, "app_rows": ar})
    m = pd.DataFrame(rows); m.to_csv(OUT / "availability_matrix.csv", index=False, encoding="utf-8-sig")
    print(m.drop(columns=["dti_ind_list"]).to_string(index=False)); print("->", OUT / "availability_matrix.csv")
    print(f"data_conf = chỉ số DTI tính được / {len(IND)} (T-Q2 chưa có nguồn = 0; K-Q3 chỉ năm {max(YEARS)}; LAG={LAG}). inputs_coverage = biến đầu vào đã điền / tổng biến.")

MAP = {"equity": "equity", "total_equity": "equity", "customer_deposits": "customer_deposits", "casa_deposits": "casa_deposits", "total_assets": "total_assets",
       "net_profit": "net_profit", "net_interest_income": "net_interest_income", "net_fee_income": "net_fee_income", "opex": "opex",
       "op_profit_before_provision": "op_profit_before_provision", "software_gross_cost": "software_gross_cost"}

def prefill():
    fc = rd(OUT / "financial_candidates.csv")
    if not len(fc): sys.exit("Chưa có out/financial_candidates.csv (chạy 04 --bctc trước).")
    out = []
    for (b, y, v), g in fc.groupby(["bank", "year", "variable"]):
        if v not in MAP: continue
        g = g.sort_values("page"); first = g.iloc[0]
        nums = str(first["parsed_numbers(first4)"]).split(" | ")
        out.append([b, y, MAP[v], nums[0].replace(",", ""), first.get("unit_hint", ""), "", first["page"], len(g), "GỢI Ý - phải đối chiếu PDF; dòng: " + str(first["raw_line (+dòng kế)"])[:90]])
    pd.DataFrame(out, columns=["bank", "year", "variable", "value_suggested", "unit", "source_file", "page", "n_candidates", "note"]).to_csv(OUT / "dti_prefill.csv", index=False, encoding="utf-8-sig")
    print(len(out), "gợi ý ->", OUT / "dti_prefill.csv", "(số liệu cột năm HIỆN TẠI = số đầu tiên; kiểm tay rồi chép sang dti_inputs.csv kèm confirmed_by)")

def bundle():
    d = OUT / "dataset_clean"; d.mkdir(exist_ok=True)
    matrix_df = rd(OUT / "availability_matrix.csv")
    if not len(matrix_df): matrix(); matrix_df = rd(OUT / "availability_matrix.csv")
    conf = dti[dti["confirmed_by"].notna() & dti["value"].notna() & (dti["confirmed_by"] != "auto-unverified")].copy() if len(dti) else dti
    if len(conf): conf["verification"] = conf["confirmed_by"].map(lambda c: "range-checked (chưa đối chiếu PDF)" if c == "range-checked" else "đã đối chiếu PDF")
    conf.to_csv(d / "dti_inputs_confirmed.csv", index=False, encoding="utf-8-sig")
    cs = OUT / "coding_sheet.xlsx"
    if cs.exists():
        c = pd.read_excel(cs); c = c[c["final"].notna() | (c.get("not_disclosed") == 1)] if "final" in c else c
        if len(c): c.to_csv(d / "coding_final.csv", index=False, encoding="utf-8-sig")
    if len(app): app.to_csv(d / "app_ratings.csv", index=False, encoding="utf-8-sig")
    matrix_df.to_csv(d / "availability_matrix.csv", index=False, encoding="utf-8-sig")
    (d / "DATA_DICTIONARY.md").write_text("""# Từ điển dữ liệu bàn giao — DTI inputs của 5 ngân hàng (Agribank, MB, TCB, BIDV, VCB), 2020–2025

Dữ liệu đầu vào cho 11 chỉ số DTI (hàng "Thu thập dữ liệu"). Ngày thu thập: 2026-10-08. Mọi con số lấy từ BCTC (hợp nhất), BCTN, BCPTBV công bố; link ở `sources.csv`. Không có số nào được ước lượng hoặc điền 0.

## 1. Các file
- `dti_inputs_confirmed.csv`: các ô CÓ SỐ đã qua xác nhận (loại `auto-unverified`). Một dòng = một ngân hàng × năm × biến.
- `dti_inputs_full.csv` (bản sao của `out/dti_inputs.csv`): đủ 540 dòng (5 NH × 6 năm × 18 biến), gồm cả ô trống kèm lý do ở cột `note`. Dùng file này để biết ô nào thiếu và vì sao.
- `availability_matrix.csv`: theo ngân hàng × năm: tình trạng tài liệu (bctn/bctc/bcptbv), số biến đã điền, `dti_ind_computable` (số chỉ số DTI tính được trên 11), `data_conf` = `dti_ind_computable` / 11, `inputs_coverage` = biến đầu vào đã điền / 16 (không tính 2 biến phụ `nci`, `digital_customer_share`).
- `app_ratings.csv`: điểm và số lượt đánh giá App Store và Google Play, chụp ngày 2026-10-08 (có cột ngày). Agribank dùng app "Agribank Retail eBanking", không phải Agribank Plus.
- `sources.csv`: URL báo cáo gốc theo ngân hàng × năm × loại (`bctn`, `bctc`, `bcptbv`); ô ghi "chưa tìm thấy" nghĩa là chưa có tài liệu.
- `dti_check.csv`: các cảnh báo kiểm tra tự động (21 cảnh báo). Đã rà tay: đều là tái trình bày báo cáo, lỗi OCR cột so sánh hoặc biến động thật, không phải lỗi nhập.
- Điểm rubric 0–4 (double coding) KHÔNG nằm trong gói này; thuộc phần làm sạch/chấm điểm của hàng sau.

## 2. Các cột của `dti_inputs_*`
`bank, year, variable, value, unit, source_file, page, confirmed_by, note, definition` (+ `verification` trong bản confirmed).
- `page`: trang trong PDF gốc (đếm từ 1). `source_file`: đường dẫn PDF trong `data/raw` (không đi kèm gói).
- `confirmed_by`: `nam` / `manual-*` = người đã mở báo cáo đối chiếu (lưu ý mục 5, các PDF scan đọc qua OCR); `range-checked` = chỉ qua kiểm tự động (ROA/ROE/CASA/xu hướng, đối chiếu cột năm trước), CHƯA mở PDF từng ô; `auto-unverified` = script tự điền, đã loại khỏi bản confirmed.
- `verification` (chỉ bản confirmed): "đã đối chiếu PDF" hoặc "range-checked (chưa đối chiếu PDF)".
- `definition`: nhãn định nghĩa của chỉ số KPI số (mục 4). Ô tài chính để trống, trừ `equity` (`parent`) và `nci`.
- Ô trống trong `dti_inputs_full.csv`: `not_disclosed: ...` = đã tìm trong báo cáo mà không có (ghi nơi đã tìm); `not_collected` = CHƯA tìm tay, KHÔNG có nghĩa là không công bố; `not_collected [TODO]` = việc chờ làm.

## 3. Biến (18) và chỉ số DTI dùng chúng
Đơn vị tiền: VND million (triệu đồng), số liệu hợp nhất cuối kỳ, trừ khi `note` nói khác. Phần trăm lưu dạng số (86 = 86%). Một số ô cũ ghi `percent`/`employees` thay vì `%`/`persons`, cùng nghĩa.

| Biến | Ý nghĩa | Số ô có số /30 | Dùng cho |
|---|---|---|---|
| `digital_txn_share` | % giao dịch khách hàng qua kênh số (định nghĩa khác nhau, mục 4) | 19 | K-Q1, S-Q1 |
| `digital_customer_share` | % khách hàng số / tổng khách hàng, do ngân hàng công bố. Biến phụ | 1 (MB 2023) | K-Q2 (cách 1) |
| `digital_customers` | số khách hàng số (người) | 8 | K-Q2 (cách 2), S-Q2 |
| `total_customers` | tổng khách hàng (người) | 19 | K-Q2 (cách 2) |
| `software_gross_cost` | nguyên giá "phần mềm máy tính" trong thuyết minh TSCĐ vô hình, cuối kỳ | 24 (VCB không có) | T-Q1 |
| `total_assets` | tổng tài sản | 30 | T-Q1 |
| `opex` | chi phí hoạt động (tổng, chưa trừ chi phí dự phòng rủi ro tín dụng); không phải chi phí hoạt động dịch vụ | 30 | O-Q1, O-Q2 |
| `op_profit_before_provision` | lợi nhuận thuần từ hoạt động kinh doanh trước chi phí dự phòng | 30 | O-Q1, O-Q2 |
| `headcount` | tổng số CBNV cuối năm (người) | 28 | O-Q2, C-Q1 |
| `tech_staff` | số nhân sự công nghệ (người) | 1 | C-Q1 |
| `training_hours_per_head` | số giờ đào tạo bình quân / CBNV / năm | 20 | C-Q2 |
| `net_interest_income` | thu nhập lãi thuần | 30 | tham khảo (DBI/ROA) |
| `net_fee_income` | lãi thuần từ hoạt động dịch vụ | 30 | tham khảo |
| `net_profit` | lợi nhuận sau thuế của cổ đông Ngân hàng mẹ (xem mục 5 về Agribank) | 29 | tham khảo (ROE) |
| `equity` | vốn chủ sở hữu của cổ đông Ngân hàng mẹ = tổng VCSH − `nci` | 30 | tham khảo (ROE) |
| `nci` | lợi ích cổ đông không kiểm soát (bảng cân đối kế toán hợp nhất). Biến phụ | 30 | tra ngược `equity` |
| `customer_deposits` | tiền gửi của khách hàng | 30 | tham khảo (CASA) |
| `casa_deposits` | tiền gửi không kỳ hạn | 25 | tham khảo (CASA) |
| (`app_rating`) | điểm đánh giá app gộp, từ `app_ratings.csv`, không nằm trong `dti_inputs` | 5 ngân hàng | K-Q3 |

## 4. Công thức 11 chỉ số và định nghĩa KPI
Chuẩn hóa: z = 100·min{1; max[0; (x−L)/(U−L)]}; L, U trong `config/dti_bounds.yaml` (đang là bản nháp, `locked=false`, 6 chỉ số chưa có nguồn). Δ và CAGR so với năm liền trước (LAG=1), trừ S-Q2.
- K-Q1 = `digital_txn_share`. K-Q2 = `digital_customer_share`, hoặc `digital_customers` / `total_customers`. K-Q3 = điểm app (ảnh chụp 1 ngày, chỉ tính cho năm cuối 2025).
- S-Q1 = `digital_txn_share`(năm y) − (năm y−1), CHỈ tính khi hai năm cùng `definition`. S-Q2 = CAGR `digital_customers` trên cửa sổ dài nhất (cách ≥ 2 năm) cùng `definition`.
- T-Q1 = `software_gross_cost` / `total_assets`. LƯU Ý: spec ghi "tổng tài sản BÌNH QUÂN" (cần tài sản năm trước, năm 2020 không có); `availability_matrix` đang đếm theo tài sản cuối kỳ cùng năm. T-Q2 (checklist 8 nền tảng) chưa có dữ liệu (`manual_audit.xlsx`), luôn tính là 0 trong `data_conf`.
- O-Q1 = ΔCIR, CIR = `opex` / (`opex` + `op_profit_before_provision`). O-Q2 = CAGR của (`opex` + `op_profit_before_provision`) / `headcount`.
- C-Q1 = `tech_staff` / `headcount` (gần như không có dữ liệu, chấp nhận `data_conf` thấp). C-Q2 = `training_hours_per_head`.

Nhãn `definition` (KHÔNG so sánh trực tiếp giữa các nhãn khác nhau):
- `digital_txn_share`: `all_txn` (mọi giao dịch: MB, Agribank 2025, VCB 2025, BIDV 2020–22); `full_line` (BIDV 2023); `retail` (TCB 2023–25); `remit_domestic` (TCB 2021–22, chỉ chuyển tiền trong nước); `product_digitized`.
- `digital_customers`: `registered`, `users`, `active`, `transacting`.
- `total_customers`: `total`; `cumulative` (MB 2020–22, 2025); `depositors`, `subset`, `lower_bound_or_accounts` (Agribank); `retail+corporate` (BIDV, là CẬN DƯỚI cộng "more than X" hai phân khúc).
- `training_hours_per_head`: `avg_hours`; `days_x6h` (BIDV 2021–23, quy đổi ngày × 6 giờ); `incl_new_hire` (MB 2023–24, tính cả lao động mới).
- `headcount`: `group`, `unspecified`, `group_approx` (Agribank 2020 = 40.000 là xấp xỉ "gần 4 vạn").
- `equity`: `parent` (tất cả 30 ô đã chuẩn hóa về cổ đông mẹ).

## 5. Quy tắc và lưu ý quan trọng
- Không bao giờ điền 0 cho dữ liệu không công bố; ô thiếu để trống.
- Mỗi số lấy từ báo cáo CỦA NĂM ĐÓ. Ngoại lệ (đều ghi trong `note`): Agribank `total_assets` 2021 (từ BCTC 2022: 1.694.320.049; BCTC 2021 ghi 1.694.231.522), `equity` Agribank 2022, 2024 và VCB 2022 (cột so sánh năm sau), `digital_txn_share` Agribank 2022 (BCTN 2024), `total_customers` MB 2020 (BCTN 2022). Chênh lệch nhỏ.
- Báo cáo năm sau có thể trình bày lại số năm trước (vd TCB chuyển 336.162 triệu 2020 và 374.889 triệu 2022 giữa phí dịch vụ và chi phí hoạt động; BIDV 2025 opex cột so sánh 27.979.504 so với 27.966.817 trong BCTC 2024). Với Δ/CAGR nên dùng cặp số cùng một báo cáo (cột năm nay và cột năm trước).
- `net_profit`: Agribank dùng LNST TỔNG vì báo cáo chỉ có một dòng lợi nhuận (không tách cổ đông mẹ/NCI); NCI nhỏ so với lợi nhuận. Các ngân hàng khác là lợi nhuận của cổ đông Ngân hàng mẹ.
- Phạm vi: mặc định là BCTC hợp nhất; một số ô Agribank lấy từ BCTC riêng (vd `customer_deposits` 2021, 2022, 2024; `software_gross_cost` 2024), ghi rõ ở `note`, nên tỷ số tiền gửi/tài sản của Agribank 2021 (91,2%) không đồng nhất phạm vi. `total_customers` Agribank trộn nhiều định nghĩa; `training_hours_per_head` VCB 2023 = 41 giờ (BCTN 2023), BCPTBV 2024 ghi 35 giờ theo phương pháp mới (giữ số của báo cáo năm đó); BIDV 2024 = 59 (biểu đồ cùng trang có 87); VCB 2020 `headcount` gồm VCBS+VCBL; VCB 2023 = 23.500 làm tròn.
- Độ tin cậy số liệu: các BCTC của Agribank, MB, BIDV, VCB là PDF scan đọc qua OCR (TCB là PDF có text). Đã từng gặp OCR đọc sai chữ số (vd Agribank total_assets 2021: 1.604 thay vì 1.694). Cột `verification` cho biết ô nào đã mở PDF, ô nào mới `range-checked`.
- Cờ `CẦN KIỂM` trong `availability_matrix` (cột bctn/bctc/bcptbv) là cờ chất lượng trích văn bản (OCR/ký tự lỗi); một số file đã xem tay và dùng được (TCB 2024 BCPTBV, BIDV 2025 BCTN/BCPTBV).
- `not_collected` không phải "không công bố": là việc chưa làm hoặc chưa tìm thấy bằng từ khóa. Còn nhiều ô loại này ở `digital_customer_share` (28), `digital_customers` (khoảng 22) và vài ô tài chính; xem `dti_inputs_full.csv`.

## 6. Khoảng trống đã biết
- VCB 2020–22: 0–2 chỉ số tính được (thiếu `digital_txn_share`, `total_customers`, cột phần mềm trong BCTC).
- T-Q2 chưa có nguồn. C-Q1 gần như không có dữ liệu. K-Q2 cách 1 chỉ có MB 2023 (86%), các ngân hàng khác phải dùng cách 2.
- `config/dti_bounds.yaml` chưa khóa, 6 chỉ số cần nguồn cho L và U (S-Q2, T-Q1, O-Q1, O-Q2, C-Q1, C-Q2).
- Chưa làm double coding và kappa.
""", encoding="utf-8")
    print("Đã tạo", d, [p.name for p in d.iterdir()])

def pages():
    """Tìm trang của từng báo cáo chính trong BCTC (đã OCR) để bạn mở PDF đọc tay số còn thiếu: out/statement_pages.csv."""
    import json, re, unicodedata
    def fold(s):
        s = unicodedata.normalize("NFD", s.replace("đ", "d").replace("Đ", "D")); return "".join(c for c in s if unicodedata.category(c) != "Mn").lower()
    KEYS = {"can_doi_ke_toan": r"bao cao tinh hinh tai chinh|balance sheet|statement of financial position|can doi ke toan",
            "ket_qua_kinh_doanh": r"bao cao ket qua hoat dong|income statement|statement of income|ket qua kinh doanh",
            "thuyet_minh_tien_gui_KH": r"tien gui cua khach hang|deposits from customers",
            "thuyet_minh_TSCD_vo_hinh": r"tai san co dinh vo hinh|intangible"}
    rows = []
    for jf in sorted((DATA / "text").glob("*_bctc.jsonl")):
        for line in open(jf, encoding="utf8"):
            d = json.loads(line); t = fold(d["text"])
            if len(re.findall(r"\d{1,3}[.,]\d{3}[.,]\d{3}", t)) < 4: continue          # trang có bảng số lớn mới tính
            for k, pat in KEYS.items():
                if re.search(pat, t[:600] if k in ("can_doi_ke_toan", "ket_qua_kinh_doanh") else t): rows.append([d["bank"], d["year"], k, d["page"]])
    df = pd.DataFrame(rows, columns=["bank", "year", "statement", "page"]).groupby(["bank", "year", "statement"]).page.apply(lambda s: ",".join(map(str, sorted(s)[:6]))).reset_index()
    df.to_csv(OUT / "statement_pages.csv", index=False, encoding="utf-8-sig"); print(df.to_string(index=False)); print("->", OUT / "statement_pages.csv")

if "--pages" in sys.argv: pages()
elif "--prefill" in sys.argv: prefill()
elif "--bundle" in sys.argv: bundle()
else: matrix()
