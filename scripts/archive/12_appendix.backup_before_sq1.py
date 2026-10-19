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
DEF = {}; HASDEF = False   # (bank, year) -> definition của digital_customers (nạp trong matrix())
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
         "S-Q1": g(y, "digital_txn_share") is not None and g(y0, "digital_txn_share") is not None,
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
    global DEF, HASDEF
    HASDEF = bool(len(dti)) and "definition" in dti.columns
    DEF = {(r["bank"], int(r["year"])): r["definition"] for _, r in dti[dti["variable"] == "digital_customers"].iterrows() if isinstance(r.get("definition"), str)} if HASDEF else {}
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
        c.to_csv(d / "coding_final.csv", index=False, encoding="utf-8-sig")
    if len(app): app.to_csv(d / "app_ratings.csv", index=False, encoding="utf-8-sig")
    matrix_df.to_csv(d / "availability_matrix.csv", index=False, encoding="utf-8-sig")
    (d / "DATA_DICTIONARY.md").write_text("""# Từ điển dữ liệu bàn giao
- dti_inputs_confirmed.csv: chỉ dòng có value VÀ đã qua xác nhận (loại auto-unverified). Cột `verification`: 'đã đối chiếu PDF' hoặc 'range-checked' (chỉ qua kiểm ROA/ROE/CASA/xu hướng, kiểm tay mẫu). Đơn vị theo cột unit (BCTC thường 'VND million'). Ô thiếu = không công bố/không tìm thấy, KHÔNG phải 0.
- coding_final.csv: điểm rubric 0-4 cột `final` (sau hòa giải), `not_disclosed`=1 nghĩa là không có bằng chứng công bố; kèm evidence_file/page/quote.
- app_ratings.csv: điểm & số lượt đánh giá tại ngày thu thập (có cột ngày).
- availability_matrix.csv: tình trạng tài liệu và số chỉ số DTI có dữ liệu theo NH x năm; data_conf = số chỉ số DTI tính được / 11 (T-Q2 chưa có nguồn; K-Q3 chỉ năm cuối); inputs_coverage = biến đầu vào đã điền / tổng.
- Ô trống trong dti_inputs: `not_disclosed: ...` = đã tìm tay trong BCTN/BCTC mà không có (ghi lý do); `not_collected` = CHƯA tìm (không phải không công bố); `[TODO]` = việc đang chờ. Cột dti_vars_not_collected trong matrix đếm các ô này.
- confirmed_by: `nam`/`manual-*` = người đã mở PDF đối chiếu; `range-checked` = chỉ qua kiểm ROA/ROE/CASA/xu hướng và đối chiếu cột năm trước, chưa đọc PDF từng ô (đã kiểm tay mẫu). dti_vars_pdf_read = số ô đã đọc PDF.
- net_profit = lợi nhuận sau thuế của cổ đông Ngân hàng mẹ (không phải LNST tổng). Mỗi số lấy từ báo cáo CỦA NĂM ĐÓ; nếu báo cáo năm sau trình bày lại thì chênh nhỏ là bình thường (vd TCB chuyển 336.162 triệu 2020 và 374.889 triệu 2022 giữa phí dịch vụ và chi phí hoạt động). Với chỉ số Δ/CAGR (S-Q1, S-Q2, O-Q1, O-Q2) nên dùng cặp số cùng một báo cáo (cột năm này và cột năm trước) để cùng cơ sở.
- Phạm vi: một số ô lấy từ BCTC riêng chứ không phải hợp nhất (vd Agribank software 2024) — xem cột note. Định nghĩa KPI số (digital_txn_share, digital_customers, total_customers) khác nhau giữa các ngân hàng; cột note ghi định nghĩa gốc, không so sánh trực tiếp khi chưa chuẩn hóa.
- Cờ `CẦN KIỂM` trong matrix (cột bctn/bctc/bcptbv) là cờ chất lượng trích văn bản (OCR/ký tự lỗi); một số file đã được xem tay và dùng được (vd TCB 2024 BCPTBV, BIDV 2025 BCTN/BCPTBV).
- definition: nhãn định nghĩa của ô KPI (digital_customers: registered/users/active/transacting; total_customers: total/depositors/subset/lower_bound_or_accounts/cumulative/retail+corporate; digital_txn_share: all_txn/retail/full_line/product_digitized; training_hours_per_head: avg_hours/incl_new_hire/days_x6h; equity: parent/total). S-Q2 (CAGR cửa sổ dài nhất, cách >=2 năm) chỉ so các mốc CÙNG definition; K-Q2 tính theo digital_customer_share (tỷ lệ công bố, %) hoặc digital_customers/total_customers. equity chuẩn hóa về vốn cổ đông mẹ = equity(total) − nci.
- Quy tắc: không điền 0 cho dữ liệu không công bố; chuẩn hóa [L,U] làm ở bước tính điểm (config/dti_bounds.yaml).
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
