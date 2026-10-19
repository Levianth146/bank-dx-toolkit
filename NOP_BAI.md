# Hồ sơ nộp bài: đối chiếu yêu cầu của giảng viên

| Yêu cầu | Nằm ở đâu trong repo |
|---|---|
| **Báo cáo**: nội dung, quy trình, phương pháp | [report/BAO_CAO_TONG_HOP.md](report/BAO_CAO_TONG_HOP.md); quy trình chi tiết [docs/pipeline-guide.md](docs/pipeline-guide.md); thuật toán [specs/001-bank-dx-assessment/algorithm-scoring.md](specs/001-bank-dx-assessment/algorithm-scoring.md); cận DTI [dti-bounds-method.md](specs/001-bank-dx-assessment/dti-bounds-method.md); độ nhạy [docs/sensitivity.md](docs/sensitivity.md) |
| **Phụ lục** | [report/phu_luc/](report/phu_luc/): PL1 tiêu chí chấm, PL2 chỉ số DTI, PL3 nguồn dữ liệu, PL4 kết quả, PL5 độ phủ dữ liệu (sinh bằng `scripts/22_build_report_appendix.py`) |
| **Tiêu chí chấm** | `config/rubric_anchors.csv` (neo rubric 24 tiêu chí), `config/keywords.yaml`, `config/dti_bounds.yaml`; bản đọc dễ: [PL1](report/phu_luc/PL1_tieu_chi_cham_diem.md) |
| **Data chấm điểm** | Đầu vào: `data/text/` (văn bản trích từ BCTN/BCTC), `output_data/dti_inputs.csv` (số liệu DTI kèm nguồn, trang), `output_data/app_ratings.csv`. Danh mục tài liệu gốc và SHA-256: `data/raw/manifest.csv`, `config/sources.csv` |
| **Kết quả chấm điểm (csv/excel)** | `output_data/score_summary.csv` (điểm tổng, hạng), `output_data/scores.csv` (6 trụ cột), `output_data/auto_scores.csv` và `output_data/coding_auto.xlsx` (24 tiêu chí kèm bằng chứng), `output_data/dti_indicators.csv`, `output_data/score_results.xlsx`; độ nhạy ở `output_data/sensitivity/`; kiểm chứng ở `output_data/layer_c_*` |
| **Code** | `scripts/` (pipeline), `api/` (FastAPI), `frontend/` (React), `tests/` |
| **Link sản phẩm** | Giao diện: https://frontend-ashy-kappa-57.vercel.app/ ; API: https://bank-dx-toolkit.onrender.com/api/v1 (docs tại `/docs`). Chạy local: xem [README](README.md) |

Tên thư mục kết quả là `output_data/` (trước đây `out/`).

## Còn thiếu, sẽ bổ sung tuần sau

- Kiểm tra tay 40–60 ô điểm DBI và báo tỷ lệ khớp với điểm quy tắc.
- Bản triển khai Render cần deploy lại để hiển thị số mới nhất (TCB 77,49; VCB 74,86; MB 73,35; BIDV 63,38; Agribank 54,92 năm 2025); bản build giao diện cũng cần build lại.
- PDF gốc (~870 MB) không đưa lên GitHub; tải lại bằng `python scripts/01_download.py` từ `config/sources.csv`.
- ROE/ROA lớp C chưa tính được do thiếu số liệu đầu kỳ.
- Một số chỉ số DTI yếu (S-Q2, C-Q1, T-Q2) do ngân hàng ít công bố.
- File codebook Word (`Mo_hinh_DBI_DTI_dieu_chinh_va_codebook.docx`) chưa nằm trong repo; nội dung tương ứng đã có ở PL1–PL2 và specs.
