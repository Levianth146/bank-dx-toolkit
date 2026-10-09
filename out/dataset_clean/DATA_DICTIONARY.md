# Từ điển dữ liệu bàn giao — DTI inputs của 5 ngân hàng (Agribank, MB, TCB, BIDV, VCB), 2020–2025

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
