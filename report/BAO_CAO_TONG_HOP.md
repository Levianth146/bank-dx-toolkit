# Báo cáo tổng hợp: xếp hạng chuyển đổi số 5 ngân hàng Việt Nam, 2020–2025

Ngân hàng: Agribank, MB, Techcombank (TCB), BIDV, Vietcombank (VCB). Mọi con số trong báo cáo lấy từ `output_data/` và có thể tái tạo bằng pipeline trong `scripts/`.

## 1. Mục tiêu và phạm vi

Đo mức độ chuyển đổi số của 5 ngân hàng theo từng năm 2020–2025 bằng một bộ tiêu chí công khai, kiểm chứng được, rồi xếp hạng và kiểm tra độ vững của kết quả. Chỉ dùng tài liệu công bố (báo cáo thường niên BCTN, báo cáo tài chính BCTC, báo cáo phát triển bền vững BCPTBV, xếp hạng app); không dùng dữ liệu nội bộ.

## 2. Mô hình

- **6 trụ cột**: Khách hàng (K), Chiến lược (S), Công nghệ (T), Vận hành (O), Văn hóa/Con người (C), Dữ liệu (D). Danh sách 24 tiêu chí và thang 0–4 ở [PL1](phu_luc/PL1_tieu_chi_cham_diem.md).
- **Lớp A, DBI** (Digital Business Index): chấm 24 tiêu chí theo rubric, mỗi tiêu chí 0–4, đưa về thang 0–100 theo trụ cột. Chấm bằng quy tắc (`rule-based-v1`, `scripts/09c_auto_score.py`) dựa trên từ khóa, mẫu số liệu và neo rubric trong `config/rubric_anchors.csv`; mỗi ô điểm có bằng chứng và trang nguồn.
- **Lớp B, DTI** (Digital Transformation Indicators): 11 chỉ số định lượng (ví dụ tỷ lệ giao dịch số, CASA, chi phí phần mềm) quy đổi `z = 100·clip((x−L)/(U−L), 0, 1)` với cận L/U cố định (`config/dti_bounds.yaml`, phiên bản `fixed-reference-v2-2026-10-17`). Mô tả ở [PL2](phu_luc/PL2_chi_so_DTI.md).
- **Điểm trụ cột**: `P_k = 0,8·DBI_k + 0,2·DTI_k`; trụ cột không có DTI thì `P_k = DBI_k`. **Điểm ngân hàng** = trung bình 6 trụ cột. Mức: <25 Khởi động, 25–50 Bắt đầu, 50–75 Hình thành, 75–100 Nâng cao, =100 Dẫn dắt.
- **Cổng chất lượng DTI**: bước 0 loại một chỉ số khỏi tất cả ngân hàng trong năm nếu thiếu ở từ 2 ngân hàng trở lên; bước 0b chỉ cho trụ cột nhận DTI khi cả 5 ngân hàng có ít nhất một chỉ số trong trụ cột đó (so sánh công bằng).
- **Lớp C, kiểm chứng ngoài**: tương quan Spearman giữa điểm và các tỷ số hiệu quả (CASA, tỷ trọng thu nhập ngoài lãi, ROE, ROA).
- **Lớp độ vững**: nhiều nhóm kịch bản (246 cặp kịch bản–năm; đổi trọng số DBI/DTI, trọng số trụ cột ±20%, Dirichlet, chuẩn hóa, nhiễu rubric) để xem hạng có đổi không.

## 3. Quy trình

`01 tải tài liệu → 02 PDF sang văn bản → 03 tìm bằng chứng → 04 trích số → 09c chấm DBI → 12 đóng gói dữ liệu sạch → 10 ghép điểm → 11 độ nhạy → 19 lớp C`. Lệnh, đầu vào, đầu ra từng bước: [docs/pipeline-guide.md](../docs/pipeline-guide.md). Nguồn tài liệu: [PL3](phu_luc/PL3_nguon_du_lieu.md) và `config/sources.csv`.

## 4. Kết quả

Điểm tổng (thang 0–100), nguồn `output_data/score_summary.csv`:

| Ngân hàng | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 |
|---|---:|---:|---:|---:|---:|---:|
| Techcombank | 47,92 | 51,04 | 67,08 | 58,38 | 61,65 | **77,49** |
| Vietcombank | 33,33 | 38,54 | 47,15 | 41,24 | 63,33 | **74,86** |
| MB | 43,75 | 45,83 | 53,40 | 48,04 | 61,94 | **73,35** |
| BIDV | 38,54 | 45,83 | 39,86 | 44,59 | 63,67 | **63,38** |
| Agribank | 22,92 | 22,92 | 21,25 | 42,12 | 48,09 | **54,92** |

Hạng 2025: TCB 1, VCB 2, MB 3, BIDV 4, Agribank 5. TCB và VCB ở mức "Nâng cao" thấp (gần ngưỡng 75), Agribank ở mức "Hình thành". Chi tiết từng trụ cột và từng năm: [PL4](phu_luc/PL4_ket_qua_cham_diem.md), `output_data/scores.csv`, `output_data/score_results.xlsx`.

Nhận xét chính:
- Mọi ngân hàng tăng điểm mạnh giai đoạn 2023–2025; Agribank và VCB tăng nhanh nhất so với mốc 2022.
- Khoảng cách đầu–cuối bảng thu hẹp từ ~25 điểm (2020) còn ~22 điểm (2025), nhưng thứ tự Agribank cuối bảng gần như không đổi.
- Hạng giữa bảng (MB, BIDV, VCB 2024) sát nhau, thường dưới 3 điểm.

## 5. Độ vững và kiểm chứng

- Phân tích độ nhạy (`output_data/sensitivity/`, [docs/sensitivity.md](../docs/sensitivity.md)): hạng đầu và cuối bảng ổn định ở hầu hết kịch bản; các hạng giữa bảng được gắn nhãn "nhóm cùng mức" khi tỷ lệ kịch bản giữ hạng thấp. Nên đọc hạng sát nhau theo nhóm, không theo thứ tự tuyệt đối.
- Lớp C (`output_data/layer_c_report.md`): với chỉ 5 ngân hàng, hệ số Spearman chỉ mang tính mô tả (nhãn `descriptive_only`), không kết luận nhân quả. Ví dụ năm 2022, CASA tương quan 0,90 với điểm, còn tỷ trọng thu nhập ngoài lãi gần như không tương quan (−0,10). ROE/ROA chưa tính được vì thiếu số dư đầu kỳ (xem mục 6).

## 6. Hạn chế đã biết

1. **Số trụ cột có DTI khác nhau theo năm** (0 trụ cột năm 2020–2021, 1 trụ cột 2022–2024, 3 trụ cột 2025) do cổng bước 0/0b; điểm giữa các năm không hoàn toàn cùng cơ sở. Phần lớn điểm đến từ DBI.
2. **DBI chấm bằng quy tắc, chưa có kiểm toán thủ công đầy đủ.** Kế hoạch: nhóm kiểm tra tay 40–60 ô điểm ngẫu nhiên có bằng chứng, báo tỷ lệ khớp.
3. **Một số chỉ số DTI yếu** (S-Q2, C-Q1, T-Q2) vì ngân hàng ít công bố; bị loại bởi bước 0.
4. **ROE/ROA lớp C chưa tính** do thiếu số liệu cuối 2019 và đầu kỳ các năm; CASA thiếu ở vài ngân hàng-năm.
5. **File PDF gốc (~870 MB) không nằm trong repo**; `data/raw/manifest.csv` lưu URL và SHA-256 để tải lại bằng `scripts/01_download.py`. Văn bản đã trích (`data/text/`, 21 MB) có trong repo để chạy lại chấm điểm.
6. Phần tiếng Anh của từ khóa chưa kiểm thử trên báo cáo thật.

## 7. Tái lập

Hướng dẫn cài đặt và chạy ở [README](../README.md). Kiểm thử: `pytest tests/test_api.py` và các script trong `tests/` (liệt kê ở README). Chuỗi hash quy tắc (`rules_hash`) trong `output_data/auto_scoring_manifest.json` bảo đảm điểm khớp với phiên bản code.
