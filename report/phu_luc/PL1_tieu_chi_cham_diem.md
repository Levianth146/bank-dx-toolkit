# Phụ lục 1. Tiêu chí chấm điểm DBI (24 tiêu chí)

Mỗi tiêu chí chấm từ 0 đến 4. Bảng dưới đây là khung rubric (`config/rubric_anchors.csv`) và từ khóa dùng để định vị bằng chứng (`config/keywords.yaml`). Từ khóa song ngữ Việt - Anh. Cách thuật toán chuyển rubric thành điểm xem `specs/001-bank-dx-assessment/algorithm-scoring.md`.

Điểm trụ cột `DBI_k` là trung bình 4 tiêu chí của trụ cột, đổi sang thang 0-100.

## Trụ cột K · Khách hàng

### K1. Phủ sóng kênh số và liên thông đa kênh

| Mức | Mô tả |
|:-:|---|
| 0 | Không tìm thấy đề cập trong văn bản đã quét (`no_mention`). Đây là kết quả của phép tìm từ khóa, không chứng minh ngân hàng không thực hiện. Không có văn bản đọc được thì để trống (`no_document`). |
| 1 | Chỉ nêu chủ trương phát triển kênh số/đa kênh; không nêu tên kênh hay tính năng. |
| 2 | Có app/web cho khách hàng cá nhân, liệt kê một số tính năng chính; chưa có kênh riêng cho doanh nghiệp hoặc chưa nói đến liên thông. |
| 3 | Có kênh số cho cả cá nhân và doanh nghiệp; đa số dịch vụ cốt lõi (chuyển tiền, tiết kiệm, vay, thanh toán) thực hiện được đầu cuối trên số (kiểm kê xác nhận); có ít nhất một số liệu quy mô. |
| 4 | Như mức 3, và có minh chứng liên thông trải nghiệm (một định danh/tài khoản xuyên kênh, tiếp tục giao dịch giữa các kênh), số liệu quy mô đa kỳ tăng, và kiểm chứng độc lập (giải thưởng, xếp hạng bên thứ ba). |

**Từ khóa định vị (16):** `omnichannel`, `đa kênh`, `ngân hàng số`, `digital banking`, `mobile banking`, `internet banking`, `kênh số`, `ứng dụng ngân hàng`, `omni-channel`, `multi-channel`, `digital channels`, `digital bank`, `mobile app`, `mobile application`, `online banking`, `digital banking platform`

### K2. Định danh và xác thực điện tử (eKYC, sinh trắc học)

| Mức | Mô tả |
|:-:|---|
| 0 | Không tìm thấy đề cập trong văn bản đã quét (`no_mention`). Đây là kết quả của phép tìm từ khóa, không chứng minh ngân hàng không thực hiện. Không có văn bản đọc được thì để trống (`no_document`). |
| 1 | Chỉ nêu định hướng triển khai eKYC/sinh trắc học. |
| 2 | Có mở tài khoản trực tuyến bằng eKYC (ảnh giấy tờ và khuôn mặt) cho khách hàng cá nhân; chưa có số liệu. |
| 3 | eKYC kết hợp đọc chip NFC/đối chiếu dữ liệu dân cư (hoặc VNeID) và xác thực sinh trắc học cho giao dịch theo quy định; có số liệu (số tài khoản mở trực tuyến hoặc tỷ lệ). |
| 4 | Như mức 3, và số liệu đa kỳ (tỷ lệ tài khoản mở mới qua kênh trực tuyến tăng qua các năm), có phủ khách hàng doanh nghiệp hoặc ủy quyền, và kiểm chứng độc lập (chứng nhận kỹ thuật, giải thưởng). |

**Từ khóa định vị (20):** `eKYC`, `định danh điện tử`, `xác thực sinh trắc học`, `nhận diện khuôn mặt`, `vân tay`, `NFC`, `CCCD gắn chip`, `VNeID`, `mở tài khoản trực tuyến`, `e-KYC`, `electronic identification`, `biometric authentication`, `biometrics`, `facial recognition`, `face recognition`, `fingerprint`, `chip-based ID`, `online account opening`, `remote account opening`, `digital onboarding`

### K3. Cá nhân hóa

| Mức | Mô tả |
|:-:|---|
| 0 | Không tìm thấy đề cập trong văn bản đã quét (`no_mention`). Đây là kết quả của phép tìm từ khóa, không chứng minh ngân hàng không thực hiện. Không có văn bản đọc được thì để trống (`no_document`). |
| 1 | Chỉ nêu mục tiêu cá nhân hóa trải nghiệm. |
| 2 | Có tính năng cá nhân hóa cụ thể (gợi ý, ưu đãi theo nhóm khách hàng, giao diện tùy biến); chưa có số liệu hiệu quả. |
| 3 | Cá nhân hóa dựa trên mô hình dữ liệu hành vi, chạy trên app/kênh chính; có số liệu hiệu quả (tỷ lệ chuyển đổi, doanh số, mức tăng tương tác). |
| 4 | Như mức 3, và vận hành theo thời gian thực/đa kênh, số liệu hiệu quả đa kỳ, có đánh giá độc lập. |

**Từ khóa định vị (18):** `cá nhân hóa`, `personalization`, `gợi ý sản phẩm`, `next best action`, `phân khúc khách hàng`, `hành vi khách hàng`, `đề xuất thông minh`, `ưu đãi riêng`, `personalisation`, `personalized`, `personalised`, `product recommendation`, `recommendation engine`, `customer segmentation`, `behavioural`, `behavioral`, `tailored offers`, `next best offer`

### K4. Đo lường trải nghiệm khách hàng

| Mức | Mô tả |
|:-:|---|
| 0 | Không tìm thấy đề cập trong văn bản đã quét (`no_mention`). Đây là kết quả của phép tìm từ khóa, không chứng minh ngân hàng không thực hiện. Không có văn bản đọc được thì để trống (`no_document`). |
| 1 | Nêu cam kết nâng cao trải nghiệm khách hàng nhưng không có công cụ đo. |
| 2 | Có khảo sát, kênh phản hồi hoặc tiếp nhận khiếu nại trực tuyến; chưa công bố chỉ số. |
| 3 | Công bố ít nhất một chỉ số (NPS, CSAT…) với giá trị cụ thể của ít nhất một kỳ, kèm mô tả quy trình xử lý phản hồi. |
| 4 | Như mức 3, và chỉ số đa kỳ cải thiện, có nêu phương pháp đo, có đơn vị khảo sát bên thứ ba. |

**Từ khóa định vị (19):** `NPS`, `CSAT`, `CES`, `hài lòng khách hàng`, `trải nghiệm khách hàng`, `voice of customer`, `khiếu nại`, `phản hồi`, `tổng đài`, `Net Promoter Score`, `customer satisfaction`, `customer experience`, `customer feedback`, `customer complaints`, `contact centre`, `contact center`, `call center`, `customer journey`, `CX`

## Trụ cột S · Chiến lược

### S1. Chiến lược chuyển đổi số chính thức

| Mức | Mô tả |
|:-:|---|
| 0 | Không tìm thấy đề cập trong văn bản đã quét (`no_mention`). Đây là kết quả của phép tìm từ khóa, không chứng minh ngân hàng không thực hiện. Không có văn bản đọc được thì để trống (`no_document`). |
| 1 | Nhắc chuyển đổi số là định hướng chung; không có văn bản hay lộ trình. |
| 2 | Có chiến lược/kế hoạch CĐS được nêu tên (theo giai đoạn) và các hướng ưu tiên; chưa có mục tiêu định lượng. |
| 3 | Chiến lược có mục tiêu định lượng và mốc thời gian (ví dụ tỷ lệ khách hàng số, doanh thu số) và báo cáo tiến độ so với kế hoạch. |
| 4 | Như mức 3, và mục tiêu được HĐQT/ĐHĐCĐ phê duyệt, cập nhật theo kỳ, kết quả đa kỳ được đối chiếu với mục tiêu. |

**Từ khóa định vị (14):** `chiến lược chuyển đổi số`, `tầm nhìn số`, `lộ trình chuyển đổi số`, `ngân hàng số`, `digital strategy`, `mục tiêu chuyển đổi số`, `đến năm 2030`, `digital transformation strategy`, `digital transformation roadmap`, `digital transformation`, `digital vision`, `digital roadmap`, `digital-first`, `by 2030`

### S2. Quản trị chuyển đổi số

| Mức | Mô tả |
|:-:|---|
| 0 | Không tìm thấy đề cập trong văn bản đã quét (`no_mention`). Đây là kết quả của phép tìm từ khóa, không chứng minh ngân hàng không thực hiện. Không có văn bản đọc được thì để trống (`no_document`). |
| 1 | Nêu lãnh đạo "chỉ đạo" CĐS nhưng không rõ đầu mối. |
| 2 | Có đơn vị, ban hoặc người phụ trách CĐS được nêu tên. |
| 3 | Có ủy ban/ban chỉ đạo cấp HĐQT hoặc Ban điều hành, có cơ chế họp/báo cáo, và người phụ trách cấp điều hành. |
| 4 | Như mức 3, và KPI CĐS gắn với đánh giá lãnh đạo/thưởng, hoặc báo cáo CĐS định kỳ trước HĐQT/ĐHĐCĐ có nội dung công bố. |

**Từ khóa định vị (18):** `ban chỉ đạo chuyển đổi số`, `ủy ban công nghệ`, `Chief Digital Officer`, `CDO`, `CIO`, `CTO`, `khối chuyển đổi số`, `giám đốc khối công nghệ`, `KPI chuyển đổi số`, `steering committee`, `technology committee`, `Chief Information Officer`, `Chief Technology Officer`, `digital transformation division`, `digital transformation committee`, `head of digital`, `digital governance`, `digital KPI`

### S3. Cam kết nguồn lực cho chuyển đổi số

| Mức | Mô tả |
|:-:|---|
| 0 | Không tìm thấy đề cập trong văn bản đã quét (`no_mention`). Đây là kết quả của phép tìm từ khóa, không chứng minh ngân hàng không thực hiện. Không có văn bản đọc được thì để trống (`no_document`). |
| 1 | Nêu "tăng cường đầu tư công nghệ", không có con số. |
| 2 | Nêu hạng mục/dự án đầu tư công nghệ cụ thể nhưng không có giá trị. |
| 3 | Công bố giá trị hoặc tỷ trọng đầu tư/ngân sách công nghệ-CĐS của ít nhất một kỳ. |
| 4 | Công bố đa kỳ, có kế hoạch theo giai đoạn và đối chiếu thực hiện với kế hoạch. |

**Từ khóa định vị (14):** `ngân sách chuyển đổi số`, `đầu tư công nghệ`, `đầu tư CNTT`, `chi đầu tư`, `kế hoạch đầu tư công nghệ`, `digital transformation budget`, `technology investment`, `IT investment`, `investment in technology`, `investment in digital`, `technology spending`, `technology capex`, `IT budget`, `digital investment`

### S4. Hợp tác hệ sinh thái và fintech

| Mức | Mô tả |
|:-:|---|
| 0 | Không tìm thấy đề cập trong văn bản đã quét (`no_mention`). Đây là kết quả của phép tìm từ khóa, không chứng minh ngân hàng không thực hiện. Không có văn bản đọc được thì để trống (`no_document`). |
| 1 | Nêu định hướng hợp tác hệ sinh thái. |
| 2 | Có ký kết hợp tác với ít nhất một đối tác công nghệ/fintech được nêu tên. |
| 3 | Hợp tác tạo ra sản phẩm/dịch vụ chung đã vận hành (thanh toán, cho vay số…) và có số liệu kết quả. |
| 4 | Hệ sinh thái nhiều đối tác với tích hợp mở (API/nền tảng), số liệu đa kỳ, hoặc ngân hàng cùng sáng lập nền tảng chung. |

**Từ khóa định vị (18):** `fintech`, `hệ sinh thái`, `ecosystem`, `đối tác chiến lược`, `liên minh`, `API đối tác`, `ví điện tử`, `siêu ứng dụng`, `fintechs`, `partner ecosystem`, `open ecosystem`, `strategic partner`, `strategic partners`, `strategic partnership`, `alliance`, `e-wallet`, `super app`, `partnership`

## Trụ cột T · Công nghệ

### T1. Hạ tầng và kiến trúc công nghệ

| Mức | Mô tả |
|:-:|---|
| 0 | Không tìm thấy đề cập trong văn bản đã quét (`no_mention`). Đây là kết quả của phép tìm từ khóa, không chứng minh ngân hàng không thực hiện. Không có văn bản đọc được thì để trống (`no_document`). |
| 1 | Chỉ nêu định hướng hiện đại hóa hạ tầng. |
| 2 | Nêu dự án hiện đại hóa core/cloud/trung tâm dữ liệu cụ thể đang triển khai. |
| 3 | Hoàn thành và vận hành hệ thống mới (core mới, cloud, DR có tên và phạm vi), có mô tả kết quả. |
| 4 | Như mức 3, và có chứng nhận hạ tầng độc lập (ví dụ chứng nhận trung tâm dữ liệu) hoặc số liệu độ sẵn sàng/khả năng chịu tải đa kỳ. |

**Từ khóa định vị (22):** `core banking`, `hệ thống lõi`, `điện toán đám mây`, `cloud`, `hybrid cloud`, `trung tâm dữ liệu`, `data center`, `dự phòng thảm họa`, `DR`, `microservices`, `Tier III`, `core system`, `private cloud`, `public cloud`, `cloud-native`, `data centre`, `disaster recovery`, `technology infrastructure`, `technology architecture`, `IT infrastructure`, `Kubernetes`, `containerization`

### T2. An toàn thông tin

| Mức | Mô tả |
|:-:|---|
| 0 | Không tìm thấy đề cập trong văn bản đã quét (`no_mention`). Đây là kết quả của phép tìm từ khóa, không chứng minh ngân hàng không thực hiện. Không có văn bản đọc được thì để trống (`no_document`). |
| 1 | Chỉ nêu cam kết bảo đảm an toàn thông tin chung. |
| 2 | Nêu biện pháp cụ thể (OTP/Smart OTP, giám sát, chính sách ATTT) nhưng chưa có chứng nhận. |
| 3 | Có ít nhất một chứng nhận quốc tế còn hiệu lực (ISO 27001 hoặc PCI DSS), hoặc có SOC vận hành; nêu phạm vi áp dụng. |
| 4 | Có từ hai chứng nhận trở lên cho các phạm vi chính, và công bố kết quả đánh giá/kiểm tra độc lập (kiểm thử xâm nhập, kiểm toán) đa kỳ. |

**Từ khóa định vị (19):** `ISO 27001`, `PCI DSS`, `an toàn thông tin`, `an ninh mạng`, `SOC`, `Security Operations Center`, `Smart OTP`, `xác thực đa yếu tố`, `MFA`, `sinh trắc học`, `information security`, `cybersecurity`, `cyber security`, `security operations centre`, `multi-factor authentication`, `two-factor authentication`, `penetration testing`, `cyber resilience`, `ISO/IEC 27001`

### T3. Open API và tích hợp đối tác

| Mức | Mô tả |
|:-:|---|
| 0 | Không tìm thấy đề cập trong văn bản đã quét (`no_mention`). Đây là kết quả của phép tìm từ khóa, không chứng minh ngân hàng không thực hiện. Không có văn bản đọc được thì để trống (`no_document`). |
| 1 | Chỉ nêu định hướng ngân hàng mở/Open API. |
| 2 | Có API dùng cho đối tác chọn lọc (thanh toán, tra cứu) nhưng không công khai tài liệu. |
| 3 | Có cổng developer hoặc tài liệu API công khai; nêu số API hoặc số đối tác tích hợp. |
| 4 | Cổng developer đầy đủ (sandbox, đăng ký tự phục vụ), nhiều nhóm API, có số liệu đối tác/lượng gọi đa kỳ. |

**Từ khóa định vị (14):** `open API`, `API mở`, `cổng developer`, `developer portal`, `open banking`, `API banking`, `tích hợp đối tác`, `SDK`, `APIs`, `API platform`, `API gateway`, `partner integration`, `third-party integration`, `sandbox`

### T4. Công nghệ mới ở mức use-case

| Mức | Mô tả |
|:-:|---|
| 0 | Không tìm thấy đề cập trong văn bản đã quét (`no_mention`). Đây là kết quả của phép tìm từ khóa, không chứng minh ngân hàng không thực hiện. Không có văn bản đọc được thì để trống (`no_document`). |
| 1 | Chỉ nhắc tên công nghệ mới ở mức định hướng. |
| 2 | Có thử nghiệm (pilot/POC) cụ thể, có tên và phạm vi. |
| 3 | Có ứng dụng vận hành chính thức cho khách hàng/nhân viên (chatbot, OCR, trợ lý GenAI) và số liệu quy mô sử dụng. |
| 4 | Như mức 3, và hiệu quả đo được đa kỳ (thời gian xử lý, tỷ lệ tự phục vụ) hoặc có kiểm chứng độc lập. |

**Từ khóa định vị (18):** `trí tuệ nhân tạo`, `AI tạo sinh`, `GenAI`, `chatbot`, `trợ lý ảo`, `OCR`, `blockchain`, `IoT`, `artificial intelligence`, `generative AI`, `AI`, `chatbots`, `virtual assistant`, `robo-advisor`, `large language model`, `LLM`, `AI-powered`, `machine vision`

## Trụ cột O · Vận hành

### O1. Tự động hóa quy trình

| Mức | Mô tả |
|:-:|---|
| 0 | Không tìm thấy đề cập trong văn bản đã quét (`no_mention`). Đây là kết quả của phép tìm từ khóa, không chứng minh ngân hàng không thực hiện. Không có văn bản đọc được thì để trống (`no_document`). |
| 1 | Chỉ nêu mục tiêu tự động hóa. |
| 2 | Có dự án/quy trình tự động hóa cụ thể được nêu. |
| 3 | Tự động hóa triển khai diện rộng, có số liệu (số quy trình/robot, giờ công tiết kiệm). |
| 4 | Như mức 3, và hiệu quả đo được đa kỳ (chi phí, thời gian, lỗi giảm) hoặc kiểm chứng độc lập. |

**Từ khóa định vị (17):** `RPA`, `tự động hóa`, `automation`, `robot`, `quy trình tự động`, `workflow`, `giờ công tiết kiệm`, `robotic process automation`, `process automation`, `intelligent automation`, `straight-through processing`, `STP`, `bots`, `workflow automation`, `hours saved`, `man-hours saved`, `FTE`

### O2. Số hóa quy trình tín dụng và hậu trường

| Mức | Mô tả |
|:-:|---|
| 0 | Không tìm thấy đề cập trong văn bản đã quét (`no_mention`). Đây là kết quả của phép tìm từ khóa, không chứng minh ngân hàng không thực hiện. Không có văn bản đọc được thì để trống (`no_document`). |
| 1 | Chỉ nêu mục tiêu số hóa quy trình. |
| 2 | Có quy trình số hóa cụ thể (hợp đồng điện tử, chữ ký số…) ở ít nhất một nghiệp vụ. |
| 3 | Quy trình tín dụng hoặc nghiệp vụ chính chạy đầu cuối trên hệ thống số, có số liệu (thời gian xử lý, tỷ lệ hồ sơ điện tử). |
| 4 | Như mức 3, và cải thiện đa kỳ (thời gian giảm), phủ nhiều nghiệp vụ, có kiểm chứng độc lập. |

**Từ khóa định vị (24):** `phê duyệt tín dụng tự động`, `hợp đồng điện tử`, `chữ ký số`, `paperless`, `không giấy tờ`, `hồ sơ điện tử`, `quy trình số`, `thời gian xử lý`, `thời gian giải ngân`, `e-contract`, `electronic contract`, `digital signature`, `e-signature`, `digitised`, `digitized`, `digitalised`, `digitalized`, `end-to-end digital`, `automated credit approval`, `loan origination`, `turnaround time`, `time to disbursement`, `digital lending`, `electronic documents`

### O3. Quản trị rủi ro và tuân thủ số

| Mức | Mô tả |
|:-:|---|
| 0 | Không tìm thấy đề cập trong văn bản đã quét (`no_mention`). Đây là kết quả của phép tìm từ khóa, không chứng minh ngân hàng không thực hiện. Không có văn bản đọc được thì để trống (`no_document`). |
| 1 | Chỉ nêu định hướng tự động hóa quản trị rủi ro. |
| 2 | Có hệ thống giám sát/cảnh báo gian lận hoặc AML cụ thể được nêu. |
| 3 | Giám sát tự động theo thời gian thực trên kênh số/đa số giao dịch, có số liệu (số giao dịch chặn, tổn thất giảm). |
| 4 | Như mức 3, và dùng mô hình học máy, kết quả đa kỳ, có kiểm toán/kiểm chứng độc lập. |

**Từ khóa định vị (19):** `giám sát giao dịch`, `phát hiện gian lận`, `fraud`, `AML`, `chống rửa tiền`, `thời gian thực`, `real-time`, `cảnh báo`, `rủi ro vận hành`, `KRI`, `fraud detection`, `fraud prevention`, `transaction monitoring`, `anti-money laundering`, `real-time monitoring`, `early warning`, `key risk indicators`, `operational risk`, `KYC`

### O4. Vận hành linh hoạt

| Mức | Mô tả |
|:-:|---|
| 0 | Không tìm thấy đề cập trong văn bản đã quét (`no_mention`). Đây là kết quả của phép tìm từ khóa, không chứng minh ngân hàng không thực hiện. Không có văn bản đọc được thì để trống (`no_document`). |
| 1 | Nhắc "linh hoạt/Agile" như khẩu hiệu. |
| 2 | Áp dụng Agile ở một số dự án/đơn vị cụ thể. |
| 3 | Mô hình Agile/squad ở quy mô khối hoặc nhiều khối, có số đội/nhân sự áp dụng. |
| 4 | Như mức 3, và kết quả đo được đa kỳ (thời gian ra sản phẩm giảm, tần suất phát hành tăng). |

**Từ khóa định vị (13):** `Agile`, `squad`, `tribe`, `DevOps`, `Scrum`, `vận hành linh hoạt`, `sprint`, `squads`, `tribes`, `sprints`, `agile transformation`, `agile way of working`, `CI/CD`

## Trụ cột C · Văn hóa

### C1. Lãnh đạo và thông điệp văn hóa số

| Mức | Mô tả |
|:-:|---|
| 0 | Không tìm thấy đề cập trong văn bản đã quét (`no_mention`). Đây là kết quả của phép tìm từ khóa, không chứng minh ngân hàng không thực hiện. Không có văn bản đọc được thì để trống (`no_document`). |
| 1 | Có thông điệp chung của lãnh đạo về văn hóa số. |
| 2 | Có chương trình/chiến dịch chuyển đổi văn hóa có tên. |
| 3 | Chương trình có mục tiêu, phạm vi toàn hệ thống và số liệu (số người tham gia, kết quả khảo sát). |
| 4 | Như mức 3, và kết quả khảo sát đa kỳ cải thiện hoặc kiểm chứng độc lập (xếp hạng nơi làm việc). |

**Từ khóa định vị (14):** `chuyển đổi văn hóa`, `văn hóa số`, `tư duy số`, `lãnh đạo số`, `văn hóa đổi mới`, `digital mindset`, `digital culture`, `cultural transformation`, `culture transformation`, `digital leadership`, `innovation culture`, `culture of innovation`, `change management`, `digital-first mindset`

### C2. Đào tạo và nâng cao kỹ năng số

| Mức | Mô tả |
|:-:|---|
| 0 | Không tìm thấy đề cập trong văn bản đã quét (`no_mention`). Đây là kết quả của phép tìm từ khóa, không chứng minh ngân hàng không thực hiện. Không có văn bản đọc được thì để trống (`no_document`). |
| 1 | Nêu chủ trương đào tạo kỹ năng số. |
| 2 | Có chương trình/nền tảng đào tạo số cụ thể. |
| 3 | Công bố số liệu tham gia (số lượt, số giờ, tỷ lệ CBNV). |
| 4 | Số liệu đa kỳ tăng, có lộ trình năng lực/chứng chỉ và kết quả (tỷ lệ đạt, số chứng chỉ). |

**Từ khóa định vị (17):** `đào tạo số`, `upskilling`, `reskilling`, `học viện`, `academy`, `e-learning`, `kỹ năng số`, `chứng chỉ công nghệ`, `giờ đào tạo`, `digital skills`, `digital training`, `training hours`, `hours of training`, `technology certification`, `learning platform`, `digital capability`, `talent development`

### C3. Văn hóa đổi mới sáng tạo

| Mức | Mô tả |
|:-:|---|
| 0 | Không tìm thấy đề cập trong văn bản đã quét (`no_mention`). Đây là kết quả của phép tìm từ khóa, không chứng minh ngân hàng không thực hiện. Không có văn bản đọc được thì để trống (`no_document`). |
| 1 | Chỉ nhắc khuyến khích đổi mới sáng tạo. |
| 2 | Có sự kiện/chương trình cụ thể (hackathon, cuộc thi sáng kiến). |
| 3 | Có cơ chế thường xuyên (lab, quỹ, quy trình đưa ý tưởng vào sản phẩm) và số liệu (số ý tưởng, số sáng kiến áp dụng). |
| 4 | Như mức 3, và sáng kiến thành sản phẩm hoặc giá trị đo được, đa kỳ. |

**Từ khóa định vị (16):** `hackathon`, `innovation lab`, `trung tâm đổi mới sáng tạo`, `sáng kiến`, `ươm tạo`, `cuộc thi sáng tạo`, `intrapreneurship`, `hackathons`, `innovation labs`, `innovation centre`, `innovation center`, `incubator`, `incubation`, `innovation contest`, `innovation challenge`, `innovation initiatives`

### C4. Môi trường làm việc số

| Mức | Mô tả |
|:-:|---|
| 0 | Không tìm thấy đề cập trong văn bản đã quét (`no_mention`). Đây là kết quả của phép tìm từ khóa, không chứng minh ngân hàng không thực hiện. Không có văn bản đọc được thì để trống (`no_document`). |
| 1 | Chỉ nhắc xây dựng môi trường làm việc hiện đại. |
| 2 | Có công cụ/nền tảng làm việc số cụ thể (cổng nhân viên, công cụ cộng tác). |
| 3 | Công cụ triển khai toàn hệ thống, kèm quy trình nhân sự số (tuyển dụng, đánh giá, đào tạo trực tuyến) có số liệu sử dụng. |
| 4 | Như mức 3, và khảo sát mức hài lòng của nhân viên với công cụ/môi trường cải thiện đa kỳ. |

**Từ khóa định vị (19):** `môi trường làm việc số`, `làm việc linh hoạt`, `làm việc từ xa`, `công cụ cộng tác`, `văn phòng số`, `HR tech`, `nhân sự số`, `cổng nhân viên`, `digital workplace`, `flexible working`, `remote working`, `remote work`, `hybrid working`, `collaboration tools`, `Microsoft 365`, `digital HR`, `HRIS`, `employee portal`, `employee app`

## Trụ cột D · Dữ liệu

### D1. Quản trị dữ liệu

| Mức | Mô tả |
|:-:|---|
| 0 | Không tìm thấy đề cập trong văn bản đã quét (`no_mention`). Đây là kết quả của phép tìm từ khóa, không chứng minh ngân hàng không thực hiện. Không có văn bản đọc được thì để trống (`no_document`). |
| 1 | Chỉ nêu dữ liệu là tài sản/định hướng quản trị dữ liệu. |
| 2 | Có đơn vị, vai trò hoặc chính sách dữ liệu được nêu. |
| 3 | Có khung quản trị (chính sách, vai trò, chuẩn chất lượng, danh mục dữ liệu) đang vận hành, nêu phạm vi. |
| 4 | Như mức 3, và có chỉ số chất lượng dữ liệu hoặc đánh giá/kiểm toán độc lập. |

**Từ khóa định vị (15):** `data governance`, `quản trị dữ liệu`, `chất lượng dữ liệu`, `data quality`, `Chief Data Officer`, `danh mục dữ liệu`, `data catalog`, `master data`, `data management`, `data stewardship`, `data strategy`, `data ownership`, `data lineage`, `data catalogue`, `metadata`

### D2. Hạ tầng dữ liệu

| Mức | Mô tả |
|:-:|---|
| 0 | Không tìm thấy đề cập trong văn bản đã quét (`no_mention`). Đây là kết quả của phép tìm từ khóa, không chứng minh ngân hàng không thực hiện. Không có văn bản đọc được thì để trống (`no_document`). |
| 1 | Chỉ nêu định hướng xây dựng nền tảng dữ liệu. |
| 2 | Có dự án data lake/warehouse được nêu tên, đang xây dựng. |
| 3 | Nền tảng dữ liệu tập trung đang vận hành, phục vụ báo cáo/phân tích, nêu phạm vi nguồn dữ liệu. |
| 4 | Như mức 3, và xử lý thời gian thực/phục vụ nhiều đơn vị, có số liệu quy mô đa kỳ hoặc đánh giá độc lập. |

**Từ khóa định vị (17):** `data lake`, `data warehouse`, `kho dữ liệu`, `hồ dữ liệu`, `big data`, `dữ liệu lớn`, `nền tảng dữ liệu`, `streaming`, `real-time`, `data lakehouse`, `data platform`, `real-time data`, `data mart`, `data hub`, `data pipeline`, `ETL`, `data infrastructure`

### D3. Phân tích nâng cao và AI/ML ra quyết định

| Mức | Mô tả |
|:-:|---|
| 0 | Không tìm thấy đề cập trong văn bản đã quét (`no_mention`). Đây là kết quả của phép tìm từ khóa, không chứng minh ngân hàng không thực hiện. Không có văn bản đọc được thì để trống (`no_document`). |
| 1 | Chỉ nêu định hướng dùng dữ liệu/AI. |
| 2 | Có mô hình/pilot cụ thể (chấm điểm tín dụng, dự báo). |
| 3 | Mô hình đã vận hành cho quyết định kinh doanh/rủi ro và có số liệu hiệu quả. |
| 4 | Như mức 3, và hiệu quả đo đa kỳ (tăng duyệt, giảm nợ xấu, giảm gian lận) cùng quản trị/kiểm định mô hình, hoặc có kiểm chứng độc lập. |

**Từ khóa định vị (20):** `machine learning`, `AI/ML`, `chấm điểm tín dụng`, `credit scoring`, `phân tích dữ liệu`, `dự báo`, `mô hình rời bỏ`, `churn`, `phân tích nâng cao`, `data analytics`, `advanced analytics`, `predictive analytics`, `predictive model`, `credit scorecard`, `churn prediction`, `forecasting`, `data-driven`, `decision engine`, `behavioural scoring`, `behavioral scoring`

### D4. Bảo vệ dữ liệu cá nhân

| Mức | Mô tả |
|:-:|---|
| 0 | Không tìm thấy đề cập trong văn bản đã quét (`no_mention`). Đây là kết quả của phép tìm từ khóa, không chứng minh ngân hàng không thực hiện. Không có văn bản đọc được thì để trống (`no_document`). |
| 1 | Chỉ có tuyên bố chung về bảo mật thông tin khách hàng. |
| 2 | Có chính sách bảo mật/điều khoản xử lý dữ liệu cá nhân công khai trên website/app. |
| 3 | Chính sách nêu căn cứ pháp lý hiện hành, quyền của chủ thể dữ liệu, cơ chế đồng ý/rút đồng ý, đầu mối bảo vệ dữ liệu. |
| 4 | Như mức 3, và có đánh giá tác động/chứng nhận (ví dụ ISO 27701) hoặc báo cáo độc lập, công bố kết quả tuân thủ. |

**Từ khóa định vị (21):** `bảo vệ dữ liệu cá nhân`, `Nghị định 13`, `quyền riêng tư`, `chính sách bảo mật`, `đồng ý của chủ thể dữ liệu`, `DPO`, `đánh giá tác động xử lý dữ liệu`, `ISO 27701`, `personal data protection`, `data privacy`, `privacy policy`, `Decree 13`, `Decree No. 13`, `PDPD`, `data protection officer`, `consent`, `data subject`, `privacy impact assessment`, `data protection impact assessment`, `GDPR`, `privacy`
