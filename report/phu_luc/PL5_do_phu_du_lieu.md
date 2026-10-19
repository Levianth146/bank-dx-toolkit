# Phụ lục 5. Độ phủ dữ liệu

Nguồn: `output_data/availability_matrix.csv`. `inputs_coverage` là tỷ lệ biến DTI thô đã có số liệu; `data_conf` là số chỉ số DTI tính được trước cổng bước 0 chia 11; `scoring_coverage` là số chỉ số thực sự dùng để tính điểm sau hai cổng bước 0 và 0b, chia 11. Ô thiếu luôn để trống, không điền 0.

| Ngân hàng | Năm | BCTN | BCTC | BCPTBV | Biến DTI có số liệu | Chỉ số DTI tính được | Chỉ số DTI dùng chấm điểm |
|---|---|---|---|---|:-:|:-:|:-:|
| Agribank | 2020 | OK | OK | chưa tìm thấy | 12/16 | 1 | 0 |
| Agribank | 2021 | OK | CẦN KIỂM | chưa tìm thấy | 12/16 | 2 | 0 |
| Agribank | 2022 | OK | CẦN KIỂM | tích hợp trong BCTN | 14/16 | 4 | 1 |
| Agribank | 2023 | OK | CẦN KIỂM | tích hợp trong BCTN | 11/16 | 2 | 1 |
| Agribank | 2024 | OK | OK | tích hợp trong BCTN | 13/16 | 5 | 2 |
| Agribank | 2025 | OK | OK | tích hợp trong BCTN | 12/16 | 7 | 5 |
| BIDV | 2020 | OK | OK | chưa tìm thấy | 12/16 | 3 | 0 |
| BIDV | 2021 | OK | OK | chưa tìm thấy | 13/16 | 3 | 0 |
| BIDV | 2022 | OK | OK | chưa tìm thấy | 14/16 | 5 | 1 |
| BIDV | 2023 | OK | OK | OK | 15/16 | 6 | 2 |
| BIDV | 2024 | OK | OK | OK | 12/16 | 4 | 2 |
| BIDV | 2025 | CẦN KIỂM | OK | CẦN KIỂM | 11/16 | 6 | 5 |
| MB | 2020 | OK | CẦN KIỂM | tích hợp trong BCTN | 13/16 | 3 | 0 |
| MB | 2021 | OK | OK | tích hợp trong BCTN | 14/16 | 3 | 0 |
| MB | 2022 | OK | OK | tích hợp trong BCTN | 14/16 | 5 | 1 |
| MB | 2023 | OK | OK | tích hợp trong BCTN | 14/16 | 7 | 2 |
| MB | 2024 | OK | CẦN KIỂM | tích hợp trong BCTN | 14/16 | 6 | 2 |
| MB | 2025 | OK | OK | tích hợp trong BCTN | 14/16 | 9 | 6 |
| Techcombank | 2020 | OK | OK | tích hợp trong BCTN | 14/16 | 3 | 0 |
| Techcombank | 2021 | OK | OK | tích hợp trong BCTN | 13/16 | 2 | 0 |
| Techcombank | 2022 | OK | OK | tích hợp trong BCTN | 15/16 | 6 | 1 |
| Techcombank | 2023 | OK | OK | tích hợp trong BCTN | 14/16 | 5 | 2 |
| Techcombank | 2024 | OK | OK | CẦN KIỂM | 14/16 | 6 | 2 |
| Techcombank | 2025 | OK | OK | OK | 14/16 | 8 | 6 |
| Vietcombank | 2020 | OK | OK | tích hợp trong BCTN | 10/16 | 0 | 0 |
| Vietcombank | 2021 | OK | OK | tích hợp trong BCTN | 10/16 | 0 | 0 |
| Vietcombank | 2022 | OK | OK | tích hợp trong BCTN | 10/16 | 1 | 1 |
| Vietcombank | 2023 | OK | OK | tích hợp trong BCTN | 11/16 | 3 | 2 |
| Vietcombank | 2024 | OK | OK | OK | 11/16 | 3 | 2 |
| Vietcombank | 2025 | OK | OK | OK | 13/16 | 6 | 5 |

Cổng bước 0 và 0b, cùng lý do loại từng ô: `output_data/step0_gate.csv` và cột `step0b_excluded` trong `output_data/dti_indicators.csv`.
