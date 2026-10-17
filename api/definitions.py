"""Định nghĩa chỉ số dùng chung: chỉ số DTI nào dùng biến đầu vào nào, công thức hiển thị, và các chỉ tiêu Lớp C.

Bảng INDICATOR_INPUTS phải khớp scripts/10_score.py (lớp Calc); nếu 10_score.py đổi cách tính một chỉ số
thì cập nhật ở đây (test_api.py có phép đối chiếu K-Q1, C-Q2, T-Q1 để bắt lệch).
"""

# Biến đầu vào (cột `variable` của dti_inputs) của từng chỉ số DTI.
INDICATOR_INPUTS = {
    "K-Q1": ["digital_txn_share"],
    "K-Q2": ["digital_customer_share", "digital_customers", "total_customers"],
    "K-Q3": [],                                   # lấy từ app_ratings.csv
    "S-Q1": ["digital_txn_share"],
    "S-Q2": ["digital_customers"],
    "T-Q1": ["software_gross_cost", "total_assets"],
    "T-Q2": [],                                   # lấy từ manual_audit.xlsx (8 nền tảng)
    "O-Q1": ["opex", "op_profit_before_provision"],
    "O-Q2": ["opex", "op_profit_before_provision", "headcount"],
    "C-Q1": ["tech_staff", "headcount"],
    "C-Q2": ["training_hours_per_head"],
}
# Số năm đầu vào cần lấy ngược từ năm chỉ số: 0 = chỉ năm đó; 1 = thêm năm trước (bình quân);
# "all" = mọi năm từ đầu dữ liệu đến năm đó (Δ, CAGR từ năm đầu kỳ).
INDICATOR_LOOKBACK = {"K-Q1": 0, "K-Q2": 0, "C-Q1": 0, "C-Q2": 0, "T-Q1": 1,
                      "S-Q1": "all", "S-Q2": "all", "O-Q1": "all", "O-Q2": "all"}

INDICATOR_FORMULAS = {
    "K-Q1": "Tỷ lệ giao dịch khách hàng qua kênh số (%), số do ngân hàng công bố",
    "K-Q2": "Khách hàng số / tổng khách hàng (%)",
    "K-Q3": "Điểm đánh giá app gộp App Store và Google Play, trọng số theo lượt đánh giá (sao 1–5)",
    "S-Q1": "(Tỷ lệ giao dịch số năm cuối − năm đầu kỳ) / số năm, đơn vị điểm %/năm",
    "S-Q2": "Tăng trưởng kép (CAGR) số khách hàng số từ năm đầu kỳ",
    "T-Q1": "Nguyên giá phần mềm máy tính cuối kỳ / tổng tài sản bình quân (%)",
    "T-Q2": "Số nền tảng số đạt (trên 8) × 100",
    "O-Q1": "Thay đổi CIR bình quân năm từ đầu kỳ (điểm %/năm; âm là cải thiện)",
    "O-Q2": "CAGR của thu nhập hoạt động trên số cán bộ nhân viên bình quân",
    "C-Q1": "Nhân sự công nghệ / tổng cán bộ nhân viên (%)",
    "C-Q2": "Số giờ đào tạo bình quân trên một cán bộ nhân viên",
}

BOUNDS_STATUS_LABELS = {
    "sourced": "Có nguồn trích dẫn",
    "derived": "Suy ra theo phương pháp trong dti-bounds-method.md",
    "external_reference": "Cận tham chiếu của nghiên cứu (không phải chuẩn ngành bắt buộc)",
    "natural": "Thang tự nhiên của chỉ số",
    "sample_percentile": "Phân vị 10%/90% của mẫu gộp 5 ngân hàng (thang tương đối, phụ thuộc mẫu)",
}

# Biến đầu vào của các chỉ tiêu Lớp C (ROE, ROA, CIR, CASA, thu nhập ngoài lãi) -> dùng để gắn nhãn `used_by`.
LAYER_C_INPUTS = {
    "ROE": ["net_profit", "equity"],
    "ROA": ["net_profit", "total_assets"],
    "CIR": ["opex", "op_profit_before_provision"],
    "CASA": ["casa_deposits", "customer_deposits"],
    "NON_INTEREST_SHARE": ["opex", "op_profit_before_provision", "net_interest_income"],
}

# expected_sign: dấu tương quan KỲ VỌNG nếu chuyển đổi số đi cùng hiệu quả tốt hơn (CIR càng thấp càng tốt).
# Tỷ trọng thu nhập ngoài lãi không có kỳ vọng một chiều rõ ràng nên để None.
LAYER_C_METRICS = {
    "roe": dict(name="ROE (LNST cổ đông mẹ / vốn CSH thuộc cổ đông mẹ bình quân)", unit="%", expected_sign=1),
    "roa": dict(name="ROA (LNST cổ đông mẹ / tổng tài sản bình quân)", unit="%", expected_sign=1),
    "cir": dict(name="CIR (chi phí hoạt động / tổng thu nhập hoạt động)", unit="%", expected_sign=-1),
    "casa": dict(name="CASA (tiền gửi không kỳ hạn / tiền gửi khách hàng)", unit="%", expected_sign=1),
    "non_interest_share": dict(name="Tỷ trọng thu nhập ngoài lãi (TOI − thu nhập lãi thuần) / TOI", unit="%", expected_sign=None),
}
