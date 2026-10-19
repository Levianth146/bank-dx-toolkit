# Phụ lục 2. Chỉ số DTI (11 chỉ số) và cận chuẩn hóa

Phiên bản cận: `fixed-reference-v2-2026-10-17` (khóa ngày 2026-10-17). Mỗi chỉ số được chuẩn hóa `z = 100 × clip((x − L) / (U − L), 0, 1)`; chỉ số `lower_better` đảo dấu.

Phương pháp chọn cận và các hạn chế: `specs/001-bank-dx-assessment/dti-bounds-method.md`.

| Mã | Chỉ số | Đơn vị | Chiều | L | U | Loại cận |
|---|---|---|---|---:|---:|---|
| K-Q1 | Tỷ lệ giao dịch khách hàng qua kênh số | % | higher_better | 0 | 90 | có nguồn trích dẫn |
| K-Q2 | Tỷ lệ khách hàng số / tổng khách hàng | % | higher_better | 0 | 100 | thang tự nhiên |
| K-Q3 | Điểm đánh giá ứng dụng (gộp App Store + Google Play, trọng số theo lượt đánh giá) | sao (1-5) | higher_better | 1 | 5 | có nguồn trích dẫn |
| S-Q1 | Thay đổi tỷ lệ giao dịch số bình quân năm từ đầu kỳ có dữ liệu | điểm %/năm | higher_better | 0 | 18 | suy ra từ dữ liệu có nguồn |
| S-Q2 | Tăng trưởng kép số khách hàng số (CAGR) | %/năm | higher_better | 0 | 24.455463 | tham chiếu ngoài mẫu |
| T-Q1 | Nguyên giá phần mềm máy tính cuối kỳ / tổng tài sản bình quân | % | higher_better | 0.0799 | 0.5657 | phân vị 10%/90% của mẫu gộp (thang tương đối) |
| T-Q2 | Tỷ lệ phủ 8 nền tảng số (checklist manual_audit.xlsx) | % | higher_better | 0 | 100 | thang tự nhiên |
| O-Q1 | Thay đổi CIR bình quân năm từ đầu kỳ có dữ liệu | điểm %/năm | lower_better | -1.1226 | 1.4844 | phân vị 10%/90% của mẫu gộp (thang tương đối) |
| O-Q2 | Tăng trưởng kép thu nhập hoạt động trên CBNV bình quân (CAGR) | %/năm | higher_better | 3.0577 | 9.4781 | phân vị 10%/90% của mẫu gộp (thang tương đối) |
| C-Q1 | Tỷ lệ nhân sự công nghệ / tổng CBNV | % | higher_better | 0 | 100 | thang tự nhiên |
| C-Q2 | Số giờ đào tạo bình quân / CBNV | giờ/người/năm | higher_better | 34.5 | 83.331 | phân vị 10%/90% của mẫu gộp (thang tương đối) |

## K-Q1. Tỷ lệ giao dịch khách hàng qua kênh số

- **Biến nguồn:** `digital_txn_share`
- **Cận:** L = 0, U = 90 (có nguồn trích dẫn)
- **Nguồn:** NHNN, Quyết định 810/QĐ-NHNN (11/05/2021), Kế hoạch chuyển đổi số ngành Ngân hàng đến 2025, định hướng 2030: mục tiêu >= 70% giao dịch khách hàng qua kênh số năm 2025, 80% năm 2030 (theo Tin nhanh chứng khoán, https://www.tinnhanhchungkhoan.vn/ke-hoach-chuyen-doi-so-nganh-ngan-hang-la-hoan-toan-kha-thi-post270252.html).
- **Nguồn:** Đại diện Vụ Thanh toán NHNN (Lê Anh Dũng), 15/04/2025: nhiều tổ chức tín dụng có hơn 90% giao dịch tài chính qua kênh số (Tạp chí Thị trường Tài chính Tiền tệ, https://thitruongtaichinhtiente.vn/hon-90-giao-dich-tai-chinh-tai-to-chuc-tin-dung-duoc-thuc-hien-qua-cac-kenh-so-67010.html).
- **Lý do chọn cận:** U = 90% là mức NHNN nêu cho nhóm tổ chức tín dụng dẫn đầu; L = 0 (không có giao dịch số). Mục tiêu 70% của QĐ 810 là mốc trung gian, không dùng làm U vì nhiều NH đã vượt. Giữ cố định mọi năm để so sánh được theo thời gian.
- **Hạn chế:** Mỗi NH định nghĩa 'giao dịch số' khác nhau (số lượng vs giá trị, bán lẻ vs toàn hàng); ghi định nghĩa gốc vào dti_inputs.note.

## K-Q2. Tỷ lệ khách hàng số / tổng khách hàng

- **Biến nguồn:** `digital_customer_share`
- **Cận:** L = 0, U = 100 (thang tự nhiên)
- **Lý do chọn cận:** Thang tỷ lệ tự nhiên 0-100%. Chưa tìm được chuẩn ngành công bố cho 'khách hàng số / tổng khách hàng' (định nghĩa 'khách hàng số' khác nhau giữa các NH; tcb 2024 không công bố riêng).
- **Hạn chế:** U = 100 là biên tự nhiên; z bằng tỷ lệ phần trăm. Nếu NH không công bố -> để trống (không điền 0).

## K-Q3. Điểm đánh giá ứng dụng (gộp App Store + Google Play, trọng số theo lượt đánh giá)

- **Biến nguồn:** `app_rating`
- **Cận:** L = 1, U = 5 (có nguồn trích dẫn)
- **Nguồn:** Thang điểm 1-5 sao của Apple App Store và Google Play; công thức z = (r - 1)/4 * 100 theo data-model.md.
- **Lý do chọn cận:** Giới hạn là biên của thang đánh giá do cửa hàng ứng dụng quy định.
- **Hạn chế:** Điểm chỉ có tại ngày thu thập (05_app_ratings.py ghi ngày); không có lịch sử theo năm -> ghi rõ trong phương pháp.

## S-Q1. Thay đổi tỷ lệ giao dịch số bình quân năm từ đầu kỳ có dữ liệu

- **Biến nguồn:** `delta_digital_txn_share`
- **Cận:** L = 0, U = 18 (suy ra từ dữ liệu có nguồn)
- **Nguồn:** Suy ra từ K-Q1: (U_K-Q1 - L_K-Q1) / 5 năm = 90/5 = 18 điểm %/năm, 5 là số năm lịch thuộc kế hoạch 2021-2025, được nghiên cứu chọn làm thời hạn mục tiêu; không phải khoảng cách giữa hai mốc dữ liệu.
- **Lý do chọn cận:** Tốc độ cần có để đi từ 0 lên mức dẫn đầu 90% trong khung 5 năm của kế hoạch NHNN; L = 0 (không cải thiện). Giảm so với năm trước cho z = 0.
- **Hạn chế:** Cận do nghiên cứu suy ra, không phải chuẩn ngành công bố. Code đo tốc độ bình quân từ mốc đầu có dữ liệu, không nhất thiết chỉ so với năm trước. NH đã gần trần (>85%) khó có Δ lớn: cân nhắc ghi nhận hạn chế này.

## S-Q2. Tăng trưởng kép số khách hàng số (CAGR)

- **Biến nguồn:** `digital_customers_cagr`
- **Cận:** L = 0, U = 24.455463 (tham chiếu ngoài mẫu)
- **Nguồn:** Santander Annual Report 2018, trang in 6, bảng kế hoạch 2015-2018: https://www.santander.de/content/pdf/investor-relations/geschaeftsberichte/geschaeftsbericht-santander-2018-englisch.pdf
- **Nguồn:** Bản nộp SEC cùng báo cáo: https://www.sec.gov/Archives/edgar/data/891478/000155837019002417/san-20181231x20f.htm
- **Lý do chọn cận:** U = 100*((32.0/16.6)^(1/3)-1), CAGR khách hàng số của ngân hàng ngoài mẫu; L = 0, không tăng trưởng. Cận tham chiếu, không phải mức tối ưu ngành.
- **Hạn chế:** Hai mốc phải cùng định nghĩa khách hàng số; không thay bằng số giao dịch. Cần ít nhất 2 năm theo code. Vượt U được kẹp 100.

## T-Q1. Nguyên giá phần mềm máy tính cuối kỳ / tổng tài sản bình quân

- **Biến nguồn:** `software_cost_to_assets`
- **Cận:** L = 0.0799, U = 0.5657 (phân vị 10%/90% của mẫu gộp (thang tương đối))
- **Nguồn:** Phân vị 10% và 90% của 24 quan sát ngân hàng-năm có dữ liệu (5 ngân hàng, 2020-2025, gộp một lần, cố định từ phiên bản fixed-reference-v2-2026-10-17); tính từ output_data/dti_indicators.csv cột x.
- **Lý do chọn cận:** Cận tham chiếu DBS (U = 0,3038%) làm 10/24 quan sát chạm trần 100 nên không phân biệt được. Từ v2: L, U là phân vị 10% và 90% của mẫu gộp; thang chỉ có nghĩa tương đối trong 5 ngân hàng.
- **Hạn chế:** Cận phụ thuộc mẫu: đổi tập ngân hàng hoặc năm thì đổi cận. Bản v1 (DBS) được giữ làm kịch bản đối chứng. Nguyên giá phần mềm không đồng nhất giữa ngân hàng (vốn hóa và thuê dịch vụ).

## T-Q2. Tỷ lệ phủ 8 nền tảng số (checklist manual_audit.xlsx)

- **Biến nguồn:** `platform_coverage`
- **Cận:** L = 0, U = 100 (thang tự nhiên)
- **Nguồn:** Checklist 8 nền tảng do đề tài định nghĩa (scripts/00_make_templates.py, PLAT).
- **Lý do chọn cận:** Chỉ số tự định nghĩa: số nền tảng đạt / 8; biên tự nhiên 0-100%.
- **Hạn chế:** Chỉ có tại thời điểm kiểm kê (ngày ghi trong manual_audit.xlsx), không có lịch sử theo năm.

## O-Q1. Thay đổi CIR bình quân năm từ đầu kỳ có dữ liệu

- **Biến nguồn:** `delta_cir`
- **Cận:** L = -1.1226, U = 1.4844 (phân vị 10%/90% của mẫu gộp (thang tương đối))
- **Nguồn:** Phân vị 10% và 90% của 20 quan sát ngân hàng-năm có dữ liệu (5 ngân hàng, 2020-2025, gộp một lần, cố định từ phiên bản fixed-reference-v2-2026-10-17); tính từ output_data/dti_indicators.csv cột x.
- **Lý do chọn cận:** Cận v1 (L = -0,5845, U = 0) khiến 13/20 quan sát bằng 0 và 7/20 bằng 100 (phân hai cực). Từ v2: L, U là phân vị 10% và 90% của ΔCIR gộp; chiều lower_better nên ΔCIR thấp (CIR giảm) được điểm cao.
- **Hạn chế:** Cận phụ thuộc mẫu. ΔCIR chịu ảnh hưởng thu nhập, lãi suất và cơ cấu kinh doanh; không chứng minh tác động nhân quả của chuyển đổi số. Bản v1 được giữ làm kịch bản đối chứng.

## O-Q2. Tăng trưởng kép thu nhập hoạt động trên CBNV bình quân (CAGR)

- **Biến nguồn:** `income_per_employee_cagr`
- **Cận:** L = 3.0577, U = 9.4781 (phân vị 10%/90% của mẫu gộp (thang tương đối))
- **Nguồn:** Phân vị 10% và 90% của 13 quan sát ngân hàng-năm có dữ liệu (5 ngân hàng, 2020-2025, gộp một lần, cố định từ phiên bản fixed-reference-v2-2026-10-17); tính từ output_data/dti_indicators.csv cột x.
- **Lý do chọn cận:** Cận v1 (U = 1,18%/năm từ DBS) làm 13/13 quan sát bằng 100, tức không phân biệt. Từ v2: L, U là phân vị 10% và 90% của CAGR thu nhập/nhân sự gộp.
- **Hạn chế:** Cận phụ thuộc mẫu, chỉ 13 quan sát và phân vị 75% sát phân vị 90% nên vẫn có chụm ở đỉnh. Lạm phát, sáp nhập, thuê ngoài ảnh hưởng kết quả. Bản v1 được giữ làm kịch bản đối chứng.

## C-Q1. Tỷ lệ nhân sự công nghệ / tổng CBNV

- **Biến nguồn:** `tech_staff_share`
- **Cận:** L = 0, U = 100 (thang tự nhiên)
- **Nguồn:** Biên toán học của tỷ lệ tập con: 0 <= nhân sự công nghệ <= tổng nhân sự, cùng phạm vi và thời điểm.
- **Lý do chọn cận:** Chưa có nguồn đủ chắc để xác lập tỷ lệ nhân sự công nghệ tối ưu. Dùng biên tự nhiên: z bằng tỷ lệ phần trăm, không gán 20% hay 30% thành chuẩn ngành.
- **Hạn chế:** U = 100 là biên toán học, không phải mục tiêu tổ chức ngân hàng. Chỉ số có điểm thấp và đóng góp thực tế nhỏ; phải công bố hạn chế này. Loại nhà thầu khỏi tử số nếu mẫu số không gồm nhà thầu; thiếu dữ liệu để trống.

## C-Q2. Số giờ đào tạo bình quân / CBNV

- **Biến nguồn:** `training_hours_per_head`
- **Cận:** L = 34.5, U = 83.331 (phân vị 10%/90% của mẫu gộp (thang tương đối))
- **Nguồn:** Phân vị 10% và 90% của 20 quan sát ngân hàng-năm có dữ liệu (5 ngân hàng, 2020-2025, gộp một lần, cố định từ phiên bản fixed-reference-v2-2026-10-17); tính từ output_data/dti_indicators.csv cột x.
- **Lý do chọn cận:** Cận v1 (U = 38,7 giờ từ DBS) làm 16/20 quan sát bằng 100. Từ v2: L, U là phân vị 10% và 90% của mẫu gộp.
- **Hạn chế:** Cận phụ thuộc mẫu. Phạm vi nhân sự và hình thức đào tạo khác nhau giữa ngân hàng (BIDV theo ngày quy đổi, MB gồm nhân sự mới). Nhiều giờ chưa chứng minh chất lượng. Bản v1 được giữ làm kịch bản đối chứng.
