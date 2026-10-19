# Phụ lục 3. Nguồn dữ liệu

Toàn bộ tài liệu là báo cáo công khai của ngân hàng. Danh mục nguồn nằm ở `config/sources.csv`; kết quả tải (ngày truy cập, mã băm sha256, kích thước) nằm ở `data/raw/manifest.csv`. File PDF gốc không đưa vào repository vì dung lượng lớn (khoảng 870 MB); chạy `python 01_download.py` để tải lại, hoặc đối chiếu bằng mã băm sha256 dưới đây.

BCTN: báo cáo thường niên. BCTC: báo cáo tài chính hợp nhất đã kiểm toán. BCPTBV: báo cáo phát triển bền vững (tùy chọn; nhiều ngân hàng tích hợp trong BCTN).

| Ngân hàng | Năm | Loại | Trạng thái | Ngày truy cập | sha256 (12 ký tự đầu) | Đường dẫn |
|---|---|---|---|---|---|---|
| Agribank | 2020 | BCPTBV | chưa tìm thấy |  |  | — |
| Agribank | 2020 | BCTC | ok | 2026-10-08 | 05a1678c4683 | [liên kết](https://www.agribank.com.vn/wcm/connect/6bc5b15d-32ec-45f6-a8ab-293f7c4dc86c/BAO+CAO+TAI+CHINH+HOP+NHAT+SAU+KIEM+TOAN+2020.pdf?MOD=AJPERES&CONVERT_TO=url&CACHEID=ROOTWORKSPACE-6bc5b15d-32ec-45f6-a8ab-293f7c4dc86c-nCOcXW0) |
| Agribank | 2020 | BCTN | ok | 2026-10-08 | 582e2aae1aba | [liên kết](https://www.agribank.com.vn/wcm/connect/0e3855a5-dbd5-4558-9ac5-31d41474d978/FILE_20210715_140421_20_6+BCTN+2020_pdf+%28trang+%C4%91%C3%B4i%29.pdf?MOD=AJPERES&CONVERT_TO=url&CACHEID=ROOTWORKSPACE-0e3855a5-dbd5-4558-9ac5-31d41474d978-owJxqSW) |
| Agribank | 2021 | BCPTBV | chưa tìm thấy |  |  | — |
| Agribank | 2021 | BCTC | ok | 2026-10-08 | d3a5923ad74a | [liên kết](https://www.agribank.com.vn/wcm/connect/d793b9d3-1bfd-4133-8557-b8553fd25951/BCTC+2021-%C4%91%C3%A3+g%E1%BB%99p_compressed.pdf?MOD=AJPERES&CONVERT_TO=url&CACHEID=ROOTWORKSPACE-d793b9d3-1bfd-4133-8557-b8553fd25951-oud0eJT) |
| Agribank | 2021 | BCTN | ok | 2026-10-08 | 17bd9108d2a2 | [liên kết](https://www.agribank.com.vn/wcm/connect/67756266-cd5c-480d-a35b-0e372f0c10f0/BCN+2021.pdf?MOD=AJPERES&CONVERT_TO=url&CACHEID=ROOTWORKSPACE-67756266-cd5c-480d-a35b-0e372f0c10f0-owJxhEz) |
| Agribank | 2022 | BCPTBV | tích hợp trong BCTN |  |  | — |
| Agribank | 2022 | BCTC | ok | 2026-10-08 | ccad2f7efe7b | [liên kết](https://www.agribank.com.vn/wcm/connect/073c9539-7ad7-4e39-ab7a-db2a9251be53/B_C_T_C_FINAL.pdf?MOD=AJPERES&CONVERT_TO=url&CACHEID=ROOTWORKSPACE-073c9539-7ad7-4e39-ab7a-db2a9251be53-ouc-PdQ) |
| Agribank | 2022 | BCTN | ok | 2026-10-08 | 82783bef91b8 | [liên kết](https://www.agribank.com.vn/wcm/connect/25572f57-6366-4345-932f-a09736413356/BCTN+2022+18.5+zip.pdf?MOD=AJPERES&CONVERT_TO=url&CACHEID=ROOTWORKSPACE-25572f57-6366-4345-932f-a09736413356-oxBBFrN) |
| Agribank | 2023 | BCPTBV | tích hợp trong BCTN |  |  | — |
| Agribank | 2023 | BCTC | ok | 2026-10-08 | d9ea3f3cd5a6 | [liên kết](https://www.agribank.com.vn/wcm/connect/69b594c1-feaf-41dc-9659-7813edd3b2ac/B_C_T_C+2023-%C4%91%C3%A3+g%E1%BB%99p.pdf?MOD=AJPERES&CONVERT_TO=url&CACHEID=ROOTWORKSPACE-69b594c1-feaf-41dc-9659-7813edd3b2ac-pnC-dRL) |
| Agribank | 2023 | BCTN | ok | 2026-10-08 | f2b37651b4ac | [liên kết](https://www.agribank.com.vn/wcm/connect/1d6eb3e5-c3f8-43fa-8985-100f3bb6bc29/BCTN+2023+%28tieng+viet%29+-compressed_1.pdf?MOD=AJPERES&CONVERT_TO=url&CACHEID=ROOTWORKSPACE-1d6eb3e5-c3f8-43fa-8985-100f3bb6bc29-oZSzLYf) |
| Agribank | 2024 | BCPTBV | tích hợp trong BCTN |  |  | — |
| Agribank | 2024 | BCTC | ok | 2026-10-08 | 0d04d2bf9b56 | [liên kết](https://www.agribank.com.vn/wcm/connect/fc6371fa-7edd-476d-a0a2-bb38aa5d0c68/B%C3%81O+C%C3%81O+T%C3%80I+CH%C3%8DNH+2024.pdf?MOD=AJPERES&CONVERT_TO=url&CACHEID=ROOTWORKSPACE-fc6371fa-7edd-476d-a0a2-bb38aa5d0c68-pnC-1fb) |
| Agribank | 2024 | BCTN | ok | 2026-10-08 | b5267960da46 | [liên kết](https://www.agribank.com.vn/wcm/connect/1c602381-62d0-48a6-990a-ba14a078b603/BCTN2024+Agribank+V+version+S.pdf?MOD=AJPERES&CONVERT_TO=url&CACHEID=ROOTWORKSPACE-1c602381-62d0-48a6-990a-ba14a078b603-prorO97) |
| Agribank | 2025 | BCPTBV | tích hợp trong BCTN |  |  | — |
| Agribank | 2025 | BCTC | ok | 2026-10-08 | 473f82221cd9 | [liên kết](https://www.agribank.com.vn/wcm/connect/5737a4c4-63f4-40f4-931b-7e68ae154aa3/B_C_T_C_2025_gop.pdf?MOD=AJPERES&CONVERT_TO=url&CACHEID=ROOTWORKSPACE-5737a4c4-63f4-40f4-931b-7e68ae154aa3-pRjnrzL) |
| Agribank | 2025 | BCTN | ok | 2026-10-08 | 0e43d6943a1f | [liên kết](https://www.agribank.com.vn/wcm/connect/ef81c291-19b0-4cc0-8f30-ff348c7d5f91/25_04_2026_VIE.pdf?MOD=AJPERES&CONVERT_TO=url&CACHEID=ROOTWORKSPACE-ef81c291-19b0-4cc0-8f30-ff348c7d5f91-pThNs3K) |
| BIDV | 2020 | BCPTBV | chưa tìm thấy |  |  | — |
| BIDV | 2020 | BCTC | ok | 2026-10-08 | 87041b8271c1 | [liên kết](https://bidv.com.vn/wps/wcm/connect/945de012-3cab-465a-8731-8bbe49a697b5/VAS+2020+Consol.pdf?MOD=AJPERES&CACHEID=ROOTWORKSPACE-945de012-3cab-465a-8731-8bbe49a697b5-nzTsCjv) |
| BIDV | 2020 | BCTN | ok | 2026-10-08 | a55de3670f70 | [liên kết](https://bidv.com.vn/wps/wcm/connect/91a97d72-7053-4959-9684-2cd3285dec9f/BIDV+2020+Annual+Report.Final.pdf?MOD=AJPERES&CACHEID=ROOTWORKSPACE-91a97d72-7053-4959-9684-2cd3285dec9f-p5oXAty) |
| BIDV | 2021 | BCPTBV | chưa tìm thấy |  |  | — |
| BIDV | 2021 | BCTC | ok | 2026-10-08 | 27d54899f871 | [liên kết](https://bidv.com.vn/wps/wcm/connect/4027d283-aaaf-4b11-86e4-f24c0de2b90a/Scan+BCTC+HN+YE2021+%28E%29.pdf?MOD=AJPERES&CACHEID=ROOTWORKSPACE-4027d283-aaaf-4b11-86e4-f24c0de2b90a-ouYoKrf) |
| BIDV | 2021 | BCTN | ok | 2026-10-08 | e80f9d6a6798 | [liên kết](https://bidv.com.vn/wps/wcm/connect/6a0859d4-d932-442f-b8f4-a9ee5264b102/BCTN+BIDV+2021+FINAL+ENG.pdf?MOD=AJPERES&CACHEID=ROOTWORKSPACE-6a0859d4-d932-442f-b8f4-a9ee5264b102-p5oXpyz) |
| BIDV | 2022 | BCPTBV | chưa tìm thấy |  |  | — |
| BIDV | 2022 | BCTC | ok | 2026-10-08 | 150b76cd26be | [liên kết](https://bidv.com.vn/wps/wcm/connect/c0ffc47e-5a07-4292-a20c-d6b83506a4d8/SCAN+CONSO+YE2022_0001.pdf?MOD=AJPERES&CACHEID=ROOTWORKSPACE-c0ffc47e-5a07-4292-a20c-d6b83506a4d8-ouYoFqt) |
| BIDV | 2022 | BCTN | ok | 2026-10-08 | 1825384ef852 | [liên kết](https://bidv.com.vn/wps/wcm/connect/52ab7924-1010-42e8-8416-eddad6e6cbc8/BIDV+Annual+Report+2022.pdf?MOD=AJPERES&CACHEID=ROOTWORKSPACE-52ab7924-1010-42e8-8416-eddad6e6cbc8-p5oXgVY) |
| BIDV | 2023 | BCPTBV | ok | 2026-10-08 | 491dc67f27ee | [liên kết](https://bidv.com.vn/wps/wcm/connect/619c18db-9671-4765-b6a7-86cce73fc794/BIDV-Sustainability+report+2023.pdf?MOD=AJPERES&CACHEID=ROOTWORKSPACE-619c18db-9671-4765-b6a7-86cce73fc794-p5oX4li) |
| BIDV | 2023 | BCTC | ok | 2026-10-08 | 8474cfb80302 | [liên kết](https://bidv.com.vn/wps/wcm/connect/937a8aa4-b261-414c-88e7-6187baabedea/SCAN+BCTC+HN+2023+%28E%29.pdf?MOD=AJPERES&CACHEID=ROOTWORKSPACE-937a8aa4-b261-414c-88e7-6187baabedea-oYsXU85) |
| BIDV | 2023 | BCTN | ok | 2026-10-08 | c49e981b1327 | [liên kết](https://bidv.com.vn/wps/wcm/connect/acd4ead4-a670-4ec8-8507-fad89a3da862/BIDV+Annual+Report+2023+-+fn.pdf?MOD=AJPERES&CACHEID=ROOTWORKSPACE-acd4ead4-a670-4ec8-8507-fad89a3da862-p8fkcW7) |
| BIDV | 2024 | BCPTBV | ok | 2026-10-08 | 547371aef0aa | [liên kết](https://bidv.com.vn/wps/wcm/connect/4ee4ddfc-5d1d-40fd-9c33-6d58811505c6/BIDV_Sustainability+Report_2024.pdf?MOD=AJPERES&CACHEID=ROOTWORKSPACE-4ee4ddfc-5d1d-40fd-9c33-6d58811505c6-psM0r71) |
| BIDV | 2024 | BCTC | ok | 2026-10-08 | da573ba1d169 | [liên kết](https://bidv.com.vn/wps/wcm/connect/15007871-9c72-47c6-98b0-0cf96a54a0e3/20250328+-+BID+-+FS+Consol+2024.pdf?MOD=AJPERES&CACHEID=ROOTWORKSPACE-15007871-9c72-47c6-98b0-0cf96a54a0e3-pnwrC6K) |
| BIDV | 2024 | BCTN | ok | 2026-10-08 | e85b89628882 | [liên kết](https://bidv.com.vn/wps/wcm/connect/2961231d-3291-4326-89b6-7350d04c496c/BIDV+Annual+Report+2024.FNL.pdf?MOD=AJPERES&CACHEID=ROOTWORKSPACE-2961231d-3291-4326-89b6-7350d04c496c-pt4shHk) |
| BIDV | 2025 | BCPTBV | ok | 2026-10-08 | 4506261628ae | [liên kết](https://bidv.com.vn/wps/wcm/connect/ba12be38-ebb7-4976-aa9e-d20e9e1e7fbd/BIDV_Sustainability+Report_2025.pdf?MOD=AJPERES&CACHEID=ROOTWORKSPACE-ba12be38-ebb7-4976-aa9e-d20e9e1e7fbd-pWbpuLL) |
| BIDV | 2025 | BCTC | ok | 2026-10-08 | 3f9aa3c87046 | [liên kết](https://bidv.com.vn/wps/wcm/connect/468ec557-2377-42b4-99f3-27dfd08659e2/20260330+-+BID+-+FS+Consol+2025.pdf?MOD=AJPERES&CACHEID=ROOTWORKSPACE-468ec557-2377-42b4-99f3-27dfd08659e2-pQ-g0gw) |
| BIDV | 2025 | BCTN | ok | 2026-10-08 | 3eaee3700cc8 | [liên kết](https://bidv.com.vn/wps/wcm/connect/f6519b5f-3abf-4694-a32c-d3057f8d75bc/BIDV_BCTN_2025_EN_%28Interactive%29.pdf?MOD=AJPERES&CACHEID=ROOTWORKSPACE-f6519b5f-3abf-4694-a32c-d3057f8d75bc-pYsQuS-) |
| MB | 2020 | BCPTBV | tích hợp trong BCTN |  |  | — |
| MB | 2020 | BCTC | ok | 2026-10-08 | e5f30683615e | [liên kết](https://www.mbbank.com.vn/resources/files/NhaDauTu/Bao-cao-tai-chinh/2020/mbb.cbtt-bao-cao-tai-chinh-kiem-toan-hop-nhat-2020.pdf) |
| MB | 2020 | BCTN | ok | 2026-10-08 | 89b49d93852a | [liên kết](https://www.mbbank.com.vn/resources/files/NhaDauTu/bao-cao-thuong-nien/Tieng-Anh/mb-annualreport-en-210615.pdf) |
| MB | 2021 | BCPTBV | tích hợp trong BCTN |  |  | — |
| MB | 2021 | BCTC | ok | 2026-10-08 | a35d2c048b29 | [liên kết](https://www.mbbank.com.vn/resources/files/NhaDauTu/Bao-cao-tai-chinh/2021/mbb.cbtt-bao-cao-tai-chinh-hop-nhat-kiem-toan-nam-2021.pdf) |
| MB | 2021 | BCTN | ok | 2026-10-08 | a043fff19bdd | [liên kết](https://www.mbbank.com.vn/resources/files/NhaDauTu/bao-cao-thuong-nien/Tieng-Anh/en-mb-ar21-final.pdf) |
| MB | 2022 | BCPTBV | tích hợp trong BCTN |  |  | — |
| MB | 2022 | BCTC | ok | 2026-10-08 | de36f2f1d305 | [liên kết](https://www.mbbank.com.vn/resources/files/NhaDauTu/Bao-cao-tai-chinh/2022/mbb.cbtt---bctc-hop-nhat-kiem-toan-2022---signed.pdf) |
| MB | 2022 | BCTN | ok | 2026-10-08 | 0994ef2752b4 | [liên kết](https://www.mbbank.com.vn/resources/files/NhaDauTu/bao-cao-thuong-nien/2023/mb-annual-report-2022-english-230705-trang-doi.pdf) |
| MB | 2023 | BCPTBV | tích hợp trong BCTN |  |  | — |
| MB | 2023 | BCTC | ok | 2026-10-08 | 6370061e3b7f | [liên kết](https://www.mbbank.com.vn/resources/files/NhaDauTu/2024/thang-02/mbb.cbtt-bao-cao-hop-nhat-kiem-toan-2023.pdf) |
| MB | 2023 | BCTN | ok | 2026-10-08 | 15e35d45fa9a | [liên kết](https://www.mbbank.com.vn/resources/files/NhaDauTu/bao-cao-thuong-nien/2024/bctn-mb-2023--eng-resize.pdf) |
| MB | 2024 | BCPTBV | tích hợp trong BCTN |  |  | — |
| MB | 2024 | BCTC | ok | 2026-10-08 | 63f17f648f12 | [liên kết](https://www.mbbank.com.vn/resources/files/NhaDauTu/Bao-cao-tai-chinh/2024/20250330---mbb---cbtt-bao-cao-tai-chinh-hop-nhat-kiem-toan-nam-2024---vietnamese.pdf) |
| MB | 2024 | BCTN | ok | 2026-10-08 | 216e00d1d34a | [liên kết](https://www.mbbank.com.vn/resources/files/NhaDauTu/bao-cao-thuong-nien/2025/FINAL-24042025/en-mb-annual-report-2024.pdf) |
| MB | 2025 | BCPTBV | tích hợp trong BCTN |  |  | — |
| MB | 2025 | BCTC | ok | 2026-10-08 | 0c3c926caa84 | [liên kết](https://www.mbbank.com.vn/resources/files/NhaDauTu/2026/T03-2026/20260310---mbb---audited-consolidated-financial-statements-for-2025.pdf) |
| MB | 2025 | BCTN | ok | 2026-10-08 | f1e12d8947e9 | [liên kết](https://www.mbbank.com.vn/resources/files/NhaDauTu/bao-cao-thuong-nien/2025/mb-bctn2025-eng-30mb.pdf) |
| Techcombank | 2020 | BCPTBV | tích hợp trong BCTN |  |  | — |
| Techcombank | 2020 | BCTC | ok | 2026-10-08 | 8edc98377e22 | [liên kết](https://techcombank.com/content/dam/techcombank/public-site/imported-assets/Audited_Financial_Statements_for_year_ended_2020_Consolidated_Searchable_ad332022d5.pdf) |
| Techcombank | 2020 | BCTN | ok | 2026-10-08 | 7565b1661fb3 | [liên kết](https://techcombank.com/content/dam/techcombank/public-site/imported-assets/Annual_Report_2020_a99851d6c3.pdf) |
| Techcombank | 2021 | BCPTBV | tích hợp trong BCTN |  |  | — |
| Techcombank | 2021 | BCTC | ok | 2026-10-08 | 7084d5c7b1a4 | [liên kết](https://techcombank.com/content/dam/techcombank/public-site/imported-assets/TCB_31_12_2021_EFS_VAS_Conso_Searchable_xxzs2_pdf_dc401b8a02.pdf) |
| Techcombank | 2021 | BCTN | ok | 2026-10-08 | e5e89948eb4d | [liên kết](https://techcombank.com/content/dam/techcombank/public-site/imported-assets/20220628_Annual_Report_2021_double_page_6ce0c20104.pdf) |
| Techcombank | 2022 | BCPTBV | tích hợp trong BCTN |  |  | — |
| Techcombank | 2022 | BCTC | ok | 2026-10-08 | 157eaaf10977 | [liên kết](https://techcombank.com/content/dam/techcombank/public-site/imported-assets/Techcombank_VAS_consolidated_financial_statements_YE_22_2811bc0ce5.pdf) |
| Techcombank | 2022 | BCTN | ok | 2026-10-08 | 1b5e4fdbac13 | [liên kết](https://techcombank.com/content/dam/techcombank/public-site/imported-assets/ENG-Book-TCB-AR-22-Web-a51923978f.pdf) |
| Techcombank | 2023 | BCPTBV | tích hợp trong BCTN |  |  | — |
| Techcombank | 2023 | BCTC | ok | 2026-10-08 | 1216381cff20 | [liên kết](https://techcombank.com/content/dam/techcombank/public-site/vi/listviewdocument/Techcombank-VAS-consolidated-financial-statements-YE-23-searchable-04d9242943.pdf) |
| Techcombank | 2023 | BCTN | ok | 2026-10-08 | a55807f1faf9 | [liên kết](https://techcombank.com/content/dam/techcombank/public-site/promo_file/TCB-AR-EN-Interactive-21038b0025.pdf) |
| Techcombank | 2024 | BCPTBV | ok | 2026-10-07 | 8784d1525beb | [liên kết](https://techcombank.com/content/dam/techcombank/public-site/documents/techcombank-sustainability-report-2024.pdf) |
| Techcombank | 2024 | BCTC | ok | 2026-10-07 | 21a7c555cc99 | [liên kết](https://techcombank.com/content/dam/techcombank/public-site/documents/techcombank-vas-consolidated-financial-statements-ye24-searchable.pdf) |
| Techcombank | 2024 | BCTN | ok | 2026-10-07 | d579299d740a | [liên kết](https://techcombank.com/content/dam/techcombank/public-site/documents/bao-cao-thuong-nien-nam-2024-eng.pdf) |
| Techcombank | 2025 | BCPTBV | ok | 2026-10-08 | fc09699f4d50 | [liên kết](https://techcombank.com/content/dam/techcombank/public-site/documents/bao-cao-phat-trien-ben-vung-2026-eng-15052026.pdf) |
| Techcombank | 2025 | BCTC | ok | 2026-10-08 | d6a7ec29a81f | [liên kết](https://techcombank.com/content/dam/techcombank/public-site/documents/techcombank-vas-consolidated-financial-statements-ye25-searchable.pdf) |
| Techcombank | 2025 | BCTN | ok | 2026-10-08 | 1c04b314f7df | [liên kết](https://techcombank.com/content/dam/techcombank/public-site/documents/techcombank-2025-annual-report-eng-vf.pdf) |
| Vietcombank | 2020 | BCPTBV | tích hợp trong BCTN |  |  | — |
| Vietcombank | 2020 | BCTC | ok | 2026-10-08 | 79653fc212f0 | [liên kết](https://www.vietcombank.com.vn/-/media/Project/VCB-Sites/VCB/Nha-Dau-tu/Files-Migrate/3-Bao-cao-tai-chinh/2020/BC3A1o20cC3A1o20tC3A0i20chC3ADnh20hE1BBA3p20nhE1BAA5t20nC483m20202020C491C3A320kiE1BB83m20toC3A1n.pdf?ts=20230919132712) |
| Vietcombank | 2020 | BCTN | robots_blocked | 2026-10-08 |  | [liên kết](https://portal.vietcombank.com.vn/VCBDigital/2020/pdf/vi/Bao-cao-thuong-nien.pdf) |
| Vietcombank | 2021 | BCPTBV | tích hợp trong BCTN |  |  | — |
| Vietcombank | 2021 | BCTC | ok | 2026-10-08 | 971068460da9 | [liên kết](https://www.vietcombank.com.vn/-/media/Project/VCB-Sites/VCB/Nha-Dau-tu/Files-Migrate/3-Bao-cao-tai-chinh/2021/BC3A1o20cC3A1o20tC3A0i20chC3ADnh20HE1BBA3p20nhE1BAA5t20nC483m20202120C491C3A320kiE1BB83m20toC3A1n.pdf?ts=20230919132725) |
| Vietcombank | 2021 | BCTN | robots_blocked | 2026-10-08 |  | [liên kết](https://static2.vietstock.vn/vietstock/2022/4/18/20220418_20220418___vcb___bao_cao_thuong_nien_2021.pdf) |
| Vietcombank | 2022 | BCPTBV | tích hợp trong BCTN |  |  | — |
| Vietcombank | 2022 | BCTC | ok | 2026-10-08 | 0f6784fc4d19 | [liên kết](https://www.vietcombank.com.vn/-/media/Project/VCB-Sites/VCB/Nha-Dau-tu/Files-Migrate/3-Bao-cao-tai-chinh/2022/2022-CN-HN.pdf?ts=20230919132734) |
| Vietcombank | 2022 | BCTN | robots_blocked | 2026-10-08 |  | [liên kết](https://static2.vietstock.vn/vietstock/2023/4/20/20230420_20230420___vcb___bao_cao_thuong_nien_2022.pdf) |
| Vietcombank | 2023 | BCPTBV | tích hợp trong BCTN |  |  | — |
| Vietcombank | 2023 | BCTC | ok | 2026-10-08 | 09ed944b5db7 | [liên kết](https://www.vietcombank.com.vn/-/media/Project/VCB-Sites/VCB/Nha-Dau-tu/Files/BC-dinh-ky/BCTC/2023/20240329---VCB---BCTC-hop-nhat-kiem-toan-2023.pdf?ts=00010101000000) |
| Vietcombank | 2023 | BCTN | robots_blocked | 2026-10-08 |  | [liên kết](https://portal.vietcombank.com.vn/VCBDigital/2023/BCTN/pdf/vi/Bao-cao-thuong-nien.pdf) |
| Vietcombank | 2024 | BCPTBV | robots_blocked | 2026-10-08 |  | [liên kết](https://portal.vietcombank.com.vn/VCBDigital/2024/BCPTBV/pdf/vi/VN_VCB_ESG_2024_Full.pdf) |
| Vietcombank | 2024 | BCTC | ok | 2026-10-08 | 63498215e56d | [liên kết](https://www.vietcombank.com.vn/-/media/Project/VCB-Sites/VCB/Nha-Dau-tu/Files/BC-dinh-ky/BCTC/2024/VCB-31122024---FS-Conso---VIE.pdf?ts=00010101000000) |
| Vietcombank | 2024 | BCTN | ok | 2026-10-08 | 9deccc3518e2 | [liên kết](https://www.vietcombank.com.vn/-/media/Project/VCB-Sites/VCB/Nha-Dau-tu/Files/BC-dinh-ky/BC-thuong-nien/2024/VN_VCB-Annual-Report-2024_Full_250426_FN_compressed.pdf?ts=20250426091445) |
| Vietcombank | 2025 | BCPTBV | ok | 2026-10-08 | 042ace920b80 | [liên kết](https://www.vietcombank.com.vn/-/media/Project/VCB-Sites/VCB/Nha-Dau-tu/Bao-cao-PTBV/VN_VCB_ESG-Report-2025.pdf?ts=20260428074438) |
| Vietcombank | 2025 | BCTC | ok | 2026-10-08 | 295f397de287 | [liên kết](https://www.vietcombank.com.vn/-/media/Project/VCB-Sites/VCB/Nha-Dau-tu/Files/BC-dinh-ky/BCTC/2025/20260327---VCB---BCTC-hop-nhat-kiem-toan-nam-2025.pdf?ts=00010101000000) |
| Vietcombank | 2025 | BCTN | robots_blocked | 2026-10-08 |  | [liên kết](https://static2.vietstock.vn/vietstock/2026/4/17/20260416___vcb___bao_cao_thuong_nien_nam_2025.pdf) |

Nguồn số liệu khác: điểm ứng dụng App Store và Google Play (`output_data/app_ratings.csv`, có ngày thu thập), kiểm kê 8 nền tảng số (`output_data/manual_audit.xlsx`), số liệu DTI đã đối chiếu PDF (`output_data/dti_inputs.csv`, kèm tệp, trang và định nghĩa).
