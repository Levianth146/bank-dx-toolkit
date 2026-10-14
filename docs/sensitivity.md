# Bộ công cụ thu thập dữ liệu cho mô hình DBI–DTI (5 ngân hàng)

Đi kèm file `Mo_hinh_DBI_DTI_dieu_chinh_va_codebook.docx`. Bộ script tải tài liệu, đọc PDF, tìm bằng chứng và lấy chỉ số định lượng. Theo quyết định của nhóm ngày **2026-10-12**, điểm DBI được chấm bằng thuật toán quy tắc `09c_auto_score.py`, thay quy trình người chấm + kappa. Số liệu DTI vẫn cần xác nhận nguồn.

Quy trình chính: **01–04 → 09c → 12 --bundle → 10**. Điểm, bằng chứng và phiên bản nằm trong `out/coding_auto.xlsx`; xem [phương pháp thuật toán](specs/001-bank-dx-assessment/algorithm-scoring.md).

Bộ cận DTI đã khóa ở phiên bản `fixed-reference-v1-2026-10-12`; nguồn, phép tính và hạn chế được mô tả trong [phương pháp chọn L/U](specs/001-bank-dx-assessment/dti-bounds-method.md). Đây là cận tham chiếu của nghiên cứu, không phải chuẩn ngành bắt buộc. Kết quả hiện có cho 5 ngân hàng trong giai đoạn 2020–2025 nằm ở `out/score_summary.csv`; chi tiết trụ cột ở `out/scores.csv` và chỉ số DTI ở `out/dti_indicators.csv`. File có hậu tố `_draft` là kết quả thử trước đó.

Sau khi đối chiếu và cập nhật dữ liệu DTI, chạy từ thư mục `scripts/`:

```bash
python 12_appendix.py --bundle
python 10_score.py --years 2020,2021,2022,2023,2024,2025
```

Kiểm tra trước khi bàn giao: `python ../tests/smoke_test.py`, `python ../tests/test_auto_score.py`, `python ../tests/test_regressions.py`, `python ../tests/test_download_sources.py`, `python ../tests/test_score.py`. Kiểm thử xác nhận hành vi code; việc chạy đạt không thay thế đối chiếu dữ liệu hoặc kiểm chứng chất lượng chấm điểm trên báo cáo thật.

## 1. Cài đặt
```
pip install -r requirements.txt
```
Tùy chọn (khuyến nghị):
- `pdftotext` (gói Poppler) — engine đọc PDF tốt cho tiếng Việt. Windows: tải Poppler, thêm vào PATH.
- Tesseract OCR + gói ngôn ngữ `vie` + `pip install pytesseract` — cho PDF dạng ảnh hoặc lỗi font.
- `pip install playwright` rồi `playwright install chromium` — cho trang web tải bằng JavaScript và chụp ảnh bằng chứng.

## 2. Quy trình chạy (làm trong thư mục `scripts/`)
| Bước | Lệnh | Việc | Đầu ra |
|---|---|---|---|
| 0 | `python 00_make_templates.py` | Tạo file mẫu | `config/sources.csv`, `out/coding_sheet.xlsx`, `out/manual_audit.xlsx`, `out/dti_inputs.csv` |
| 1 | điền `config/sources.csv` bằng tay, rồi `python 01_download.py` | Tải BCTN/BCTC/BCPTBV (BCPTBV tùy chọn; nếu nằm trong BCTN thì để trống `url` và ghi `tích hợp trong BCTN` vào `notes`) | `data/raw/<bank>/<năm>_<loại>.pdf`, `data/raw/manifest.csv` (sha256, ngày truy cập) |
| 2 | `python 02_extract_text.py [--ocr]` | PDF → text từng trang, tự chọn engine ít lỗi nhất | `data/text/*.jsonl`, `out/extraction_report.csv` (cờ nghi lỗi font) |
| 3 | `python 03_locate_evidence.py` | Tìm đoạn chứa từ khóa của 24 tiêu chí | `out/evidence_candidates.csv`, `out/keyword_density.csv` |
| 4a | `python 04_extract_numbers.py --bctc` | Ứng viên số liệu BCTC | `out/financial_candidates.csv` |
| 4b | `python 04_extract_numbers.py --kpi` | Ứng viên KPI trong BCTN/BCPTBV | `out/kpi_candidates.csv` |
| 5 | `python 05_app_ratings.py --discover`, điền id vào `config/banks.yaml`, rồi `--collect` | Rating app | `out/app_ratings.csv` |
| 6 | điền mục `probe` trong `config/banks.yaml`, rồi `python 06_probe_web.py [--screenshot]` | Snapshot trang developer, chính sách bảo mật | `out/web_probe.csv`, `data/web/...` |
| 7 | `python 07_text_mining.py [--expand] [--compare]` (chạy sau bước 2) | Text mining: BM25, độ phủ, tỷ lệ câu có số liệu, TF-IDF, mở rộng từ điển, đối chiếu điểm thuật toán | `out/tm_criterion.csv`, `tm_pillar.csv`, `tm_tfidf_terms.csv`, `tm_dictionary_expansion.csv`, `tm_vs_dbi.csv` |
| 8 | `python 08_lda_topics.py [--k 12] [--segment]` | LDA: khám phá chủ đề, tỷ trọng nội dung theo trụ cột | `out/lda_topics.csv`, `lda_bank_topic_share.csv`, `lda_bank_pillar_share.csv`, `lda_k_scan.csv` |
| 9 | `python 09_phobert.py --build-train / --finetune / --predict` (hoặc `--anchors`) | PhoBERT: lọc câu bằng chứng sai, gợi ý mức rubric | `out/phobert_predictions.csv`, `phobert_evidence_counts.csv`, `phobert_anchor_suggestions.csv` |
| 09c | `python 09c_auto_score.py` | Chấm DBI theo quy tắc, không yêu cầu bảng chấm tay | `out/auto_scores.csv`, `out/coding_auto.xlsx`, `out/auto_scoring_manifest.json` |
| 12 | `python 12_appendix.py --bundle` | Đóng gói DTI đã xác nhận + điểm thuật toán | `out/dataset_clean/` |
| 10 | `python 10_score.py` (hoặc `--draft` khi L/U chưa khóa) | Ghép DBI 80% + DTI 20% | `out/score_summary.csv` (bản nháp có hậu tố `_draft`) |
| 11 | `python 11_sensitivity.py [--years 2021,2023,2025] [--n-mc 10000]` | Độ nhạy thứ hạng (mục V.2 docx): trọng số DBI/DTI, trọng số trụ cột ±20% và Dirichlet, chuẩn hóa (Kendall τ), loại từng trụ, thiếu=0, dịch cận L/U, nhiễu rubric | `out/sensitivity/` (CSV, `sensitivity_results.xlsx`, `fig1-3_*.png`) |

## 2a. Lọc và ngôn ngữ
- 01–04 và 07–09 nhận `--bank tcb,mb`, `--year 2024,2025`, `--type bctn,bctc`, `--only-lang vi|en` (ví dụ chạy thử một ô: `python 01_download.py --bank tcb --year 2024`).
- Bước 02 gắn `lang` (vi/en/unknown) cho từng văn bản và ghi vào `extraction_report.csv`. File `data/text/*.jsonl` tạo trước khi có cột này coi như tiếng Việt; chạy lại 02 với `--force` để gắn nhãn.
- Từ khóa, nhãn BCTC và mẫu KPI hỗ trợ cả tiếng Việt và tiếng Anh. Phần tiếng Anh chưa kiểm thử trên báo cáo thật; mỗi ngân hàng dịch nhãn BCTC hơi khác, nên bổ sung vào `BCTC_LABELS` khi gặp.
- 07 tách văn bản, IDF, chuẩn hóa và tương quan riêng từng ngôn ngữ; 08 và 09 chỉ nhận tiếng Việt, kể cả khi truyền `--only-lang en`.
- Bước 00 giữ nguyên bảng kiểm kê đã có. Bước 12 `--bundle` chỉ xuất số đã đối chiếu PDF và có nguồn/trang; `range-checked` chưa được dùng để tính điểm chính thức.
- Bước 10 lấy rating từ ngày thu thập mới nhất của từng ngân hàng, không gộp nhiều ngày. Dữ liệu DTI thiếu luôn để trống, kể cả khi chạy kịch bản trọng số.

## 2b. Text mining (script 07)
- **BM25** (k1=1,2; b=0,75; IDF = ln(1+(N−df+0,5)/(df+0,5))) cho từng tiêu chí × ngân hàng × năm: mức độ "nói về" tiêu chí so với các báo cáo khác trong cùng tập.
- **Độ phủ**: số từ khóa khác nhau xuất hiện / tổng từ khóa của tiêu chí.
- **Tỷ lệ câu định lượng**: trong các câu chứa từ khóa, tỷ lệ câu có kèm số + đơn vị (phân biệt "nêu chung chung" với "có số liệu").
- **TF-IDF unigram/bigram**: thuật ngữ đặc trưng của từng báo cáo.
- `--expand`: gợi ý từ khóa mới bằng log-odds của các từ nằm trong cửa sổ ±120 ký tự quanh từ khóa (đã gộp cửa sổ chồng nhau). Chỉ là ứng viên, phải duyệt tay rồi mới thêm vào `config/keywords.yaml`.
- `--compare`: Spearman giữa điểm thuật toán (`coding_auto.xlsx`) và BM25/độ phủ.
- **Giới hạn**: chỉ chạy thử trên dữ liệu giả lập, chưa thử trên báo cáo thật. Với n = 5 ngân hàng chỉ mang tính mô tả. Các chỉ số này là phụ trợ, điểm chính là rubric vận hành hóa bằng quy tắc 09c. Có thể mở rộng thêm PhoBERT/LDA nhưng bộ công cụ chưa kiểm thử.

## 2c. LDA và PhoBERT (script 08, 09)
**08 LDA** (scikit-learn). Cắt báo cáo thành đoạn ~120 từ, huấn luyện LDA trên toàn bộ đoạn của cả 5 ngân hàng. Kết quả: mỗi ngân hàng-năm dành bao nhiêu % nội dung cho từng chủ đề, và chủ đề nào thuộc trụ cột nào (gán theo độ trùng với `keywords.yaml`, cần ≥ 2 từ khóa khác nhau, nếu không xếp "khác").
- Quét K bằng UMass coherence (`lda_k_scan.csv`). UMass thường ưu tiên K nhỏ, nên đọc top từ rồi chọn K bằng `--k`.
- Chạy nhiều seed, cột `stability` = Jaccard top-15 từ giữa các seed. Chủ đề dưới 0,4 là không ổn định, đừng diễn giải.
- Nên dùng `--segment` (pyvi) để tách từ ghép tiếng Việt.
- Phải đọc lại mapping chủ đề→trụ cột bằng mắt. Tỷ trọng chủ đề chỉ nói báo cáo viết nhiều về gì, không nói mức triển khai.

**09 PhoBERT**. Hai cách dùng:
1. *Lọc câu bằng chứng sai (khuyến nghị)*. Chạy 03 để có `evidence_candidates.csv`, thêm cột `valid` (1/0) cho các câu bạn đã đọc, rồi `--build-train` → `--finetune --cv 5` (in macro-F1 theo fold) → `--predict`. Mô hình học phân biệt câu "đúng là bằng chứng của tiêu chí" với câu "trúng từ khóa nhưng sai nghĩa". Cần khoảng 30 câu mỗi tiêu chí trở lên. Nếu CV macro-F1 dưới ~0,6 thì đừng dùng để lọc.
2. *Gợi ý mức rubric không cần dữ liệu huấn luyện (`--anchors`)*. So embedding câu với 96 mô tả mức trong `config/rubric_anchors.csv`. Embedding PhoBERT thô không được huấn luyện cho độ tương đồng câu nên chất lượng thấp, chỉ dùng để người chấm xem trước.
- PhoBERT được huấn luyện trên văn bản đã tách từ. Mặc định tách bằng pyvi (thay VnCoreNLP). Tinh chỉnh nhanh hơn nhiều khi có GPU.
- Lần đầu cần mạng để tải `vinai/phobert-base-v2` từ HuggingFace.

**Mức kiểm thử**: chỉ trên dữ liệu giả lập. Với 09, luồng code đã chạy hết (build-train, finetune có CV, predict, anchors) nhưng bằng model BERT nhỏ khởi tạo ngẫu nhiên, vì sandbox không tải được trọng số PhoBERT. Chất lượng phân loại thật của PhoBERT trên báo cáo ngân hàng chưa được đo.

## 3. Từng tiêu chí / biến lấy bằng cách nào
| Nhóm | Tiêu chí / biến | Cách lấy | Công cụ |
|---|---|---|---|
| A. Văn bản báo cáo | S1–S4, K4, T1, T4, O1–O4, C1–C4, D1–D3 (và phần văn bản của K1–K3, T2, T3, D4) | Tải BCTN + BCPTBV → đọc text → script liệt kê đoạn chứa từ khóa, xếp theo gợi ý ưu tiên đọc → 09c tính điểm 0–4 và lưu bằng chứng/phiên bản | 01, 02, 03 |
| B. Kiểm kê trực tiếp | K1, K2, K3, T3, T4 (chatbot), T2 (Smart OTP/sinh trắc), D4 (trang chính sách), **T-Q2 (8 nền tảng)** | Người chấm thao tác trên app/website, chụp màn hình, ghi vào `manual_audit.xlsx`. Với trang web công khai: script 06 lưu snapshot HTML/ảnh và kiểm tra từ khóa kỳ vọng. Không tự động hóa thao tác bên trong app | 06 + thủ công |
| C. API cửa hàng ứng dụng | **K-Q3** | iTunes Search/Lookup API (App Store) + `google-play-scraper` (Google Play); gộp có trọng số theo số lượt đánh giá | 05 |
| D. Báo cáo tài chính | **T-Q1** (phần mềm máy tính, tổng tài sản), **O-Q1** (chi phí hoạt động, LN thuần trước dự phòng → CIR), **O-Q2** (tổng thu nhập HĐ, CBNV), Lớp C: ROE, ROA, CASA, thu nhập ngoài lãi | BCTC kiểm toán → script tìm dòng theo nhãn (bỏ qua khoảng trắng thừa, nhãn ngắt dòng) → người dùng đối chiếu trang → ghi vào `dti_inputs.csv` | 04 `--bctc` |
| E. KPI trong BCTN/BCPTBV | **K-Q1, K-Q2, S-Q1, S-Q2, C-Q1, C-Q2** và CBNV | Script tìm câu có cụm từ khóa + con số; người dùng chọn đúng con số, ghi định nghĩa của từng ngân hàng | 04 `--kpi` |
| F. Tra cứu bên thứ ba (thủ công) | Chứng nhận ISO 27001/PCI DSS (T2 mức 3–4), giải thưởng/xếp hạng (mức 4 nhiều tiêu chí, Lớp C) | Tra trên website ngân hàng, trang tổ chức chứng nhận, trang ban tổ chức giải thưởng; lưu link + ngày | thủ công |

Công thức tính từ số đã xác nhận (BCTC ngân hàng thường tính bằng triệu đồng):
- Tổng thu nhập hoạt động (TOI) = (mục IX) + (mục VIII, lấy giá trị dương); CIR = chi phí hoạt động / TOI.
- ROE = LNST / bình quân vốn CSH (đầu kỳ, cuối kỳ); ROA = LNST / bình quân tổng tài sản. BCTC có cả cột năm trước nên tính được bình quân.
- CASA = tiền gửi không kỳ hạn / tiền gửi của khách hàng; thu nhập ngoài lãi = (TOI − thu nhập lãi thuần) / TOI.
- T-Q1 = nguyên giá phần mềm máy tính cuối kỳ / tổng tài sản bình quân.

## 4. Những chỗ dễ sai
- **Lỗi font/dấu tiếng Việt khi đọc PDF.** Script chọn engine ít lỗi nhất cho từng trang và cho cờ cảnh báo trong `extraction_report.csv`; từ khóa dùng chế độ chịu lỗi khoảng trắng thừa (`--exact` để tắt). Với file bị cờ: chạy `--ocr` và kiểm tra tay vài trang.
- **Nhãn BCTC khác nhau giữa ngân hàng** (số mục, cách ngắt dòng, thuyết minh). Script chỉ đưa ứng viên kèm trang và dòng kế tiếp. Luôn mở PDF đối chiếu trước khi ghi vào `dti_inputs.csv`. Với "phần mềm máy tính": lấy nguyên giá cuối kỳ, không lấy hao mòn lũy kế.
- **Số liệu KPI trong BCTN** do script chỉ lọc câu có số; nhiều con số không phải chỉ số cần tìm. Ghi lại câu gốc và trang vào `dti_inputs.csv`.
- **Điểm app chỉ có tại thời điểm chạy**: ghi ngày thu thập trong đề tài. Chọn đúng app chính chủ (xem tên nhà phát hành) trước khi `--collect`.
- **Trang web nhiều nội dung JavaScript hoặc chặn bot**: dùng `--js`; nếu vẫn bị chặn thì mở tay và lưu ảnh chụp. Không cố vượt rào chặn.
- Thiếu văn bản đọc được: 09c ghi `no_document`, điểm DBI để trống. Không tự điền 0 cho DTI; `no_mention=0` chỉ là kết quả tìm từ khóa trong văn bản đã quét.

## 5. Đạo đức và pháp lý khi thu thập
- Chỉ lấy tài liệu công khai (báo cáo, trang web không cần đăng nhập). Không đăng nhập, không scrape bên trong app, không vượt giới hạn truy cập.
- Script 01 và 06 kiểm tra `robots.txt` (không có tùy chọn bỏ kiểm tra), nghỉ ít nhất 3 giây giữa các yêu cầu, đặt biến `CONTACT` (email) để ghi vào User-Agent.
- Lưu `manifest.csv` (URL, ngày, sha256) làm bằng chứng nguồn cho phần phương pháp của đề tài.
- Dùng cho mục đích học thuật; trích dẫn nguồn đầy đủ.

## 6. Kiểm soát chất lượng
- Kiểm tay ít nhất 10% số liệu định lượng đã trích (đối chiếu PDF gốc).
- Kiểm tra ca kiểm thử thuật toán, mẫu bằng chứng, độ phủ tài liệu và độ nhạy với từ khóa/cửa sổ; không yêu cầu kappa.
- `coding_sheet.xlsx` cũ được giữ để lưu trữ; điểm chính thức nằm trong `coding_auto.xlsx`. Thiếu văn bản để trống; `no_mention=0` chỉ mô tả kết quả phát hiện của thuật toán.
- Thư mục `examples/` có PDF mẫu giả lập và đầu ra của từng script để bạn thấy định dạng kết quả.
