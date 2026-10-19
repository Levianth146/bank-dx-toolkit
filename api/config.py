"""Cấu hình, hằng số và nạp mô-đun chấm điểm của pipeline (scripts/10_score.py).

API KHÔNG tự tính lại điểm chính thức: điểm, hạng, mức trưởng thành đọc từ output_data/*.csv do 10_score.py ghi.
Riêng phần độ nhạy trọng số (DBI/DTI) cần tính lại P_k nên dùng chung hàm/hằng số của 10_score.py
để công thức không bị lệch giữa pipeline và API.
"""
import importlib.util
import os
import pathlib
import sys
from functools import lru_cache

ROOT = pathlib.Path(os.environ.get("DX_ROOT") or pathlib.Path(__file__).resolve().parents[1]).resolve()
OUT = ROOT / "output_data"
CONF = ROOT / "config"
SCRIPTS = ROOT / "scripts"

API_PREFIX = "/api/v1"

# Nhóm ngân hàng (mục 3.2 của bài luận: so sánh NHTM Nhà nước và NHTM Cổ phần).
BANK_GROUPS = {
    "agribank": "NHTM Nhà nước",
    "bidv": "NHTM Nhà nước",
    "vcb": "NHTM Nhà nước",
    "mb": "NHTM Cổ phần",
    "tcb": "NHTM Cổ phần",
}

DTI_TOTAL = 11            # tổng số chỉ số DTI trong mô hình
W_DBI_BASE = 0.8          # trọng số cơ sở DBI (DTI = 1 - 0,8)
WEIGHT_SCENARIOS = (1.0, 0.8, 0.7, 0.6)   # giống 10_score.py --weight-scenarios

# Quy ước HIỂN THỊ độ tin cậy dữ liệu (chỉ để frontend tô màu/nhãn; KHÔNG ảnh hưởng điểm).
# data_confidence = số chỉ số DTI có dữ liệu / 11 (mục II docx).
RELIABILITY_HIGH = 0.7
RELIABILITY_MEDIUM = 0.4

MATURITY_LEVELS = [
    {"number": 1, "name": "Khởi động", "min": 0, "max": 25},
    {"number": 2, "name": "Bắt đầu", "min": 25, "max": 50},
    {"number": 3, "name": "Hình thành", "min": 50, "max": 75},
    {"number": 4, "name": "Nâng cao", "min": 75, "max": 100},
    {"number": 5, "name": "Dẫn dắt", "min": 100, "max": 100},
]


@lru_cache(maxsize=1)
def scoring():
    """Nạp scripts/10_score.py (tên file bắt đầu bằng số nên không import trực tiếp được)."""
    if str(SCRIPTS) not in sys.path:
        sys.path.insert(0, str(SCRIPTS))
    spec = importlib.util.spec_from_file_location("dx_score", SCRIPTS / "10_score.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod
