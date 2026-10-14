# API cho dashboard DBI–DTI

API **chỉ đọc**, lấy dữ liệu từ `out/` do pipeline sinh ra (`10_score.py`, `12_appendix.py`, `09c_auto_score.py`). API không ghi vào `out/` và không tự chấm lại điểm chính thức; riêng phần độ nhạy trọng số dùng lại hàm của `10_score.py` để công thức không lệch.

## Chạy

```bash
pip install -r requirements-api.txt
uvicorn api.main:app --reload --port 8000     # chạy từ thư mục gốc repo
```
- Tài liệu tương tác (Swagger): http://localhost:8000/docs  ·  Schema: http://localhost:8000/openapi.json
- Chạy lại `python 10_score.py ...` rồi **gọi API lại là có số mới**, không cần restart (API so sánh thời gian sửa tệp).
- CORS mặc định mở (`*`) vì dữ liệu công khai và chỉ có GET. Khi triển khai thật: `DX_CORS_ORIGINS=https://ten-mien-cua-nha.app`.
- Kiểm thử: `pytest tests/test_api.py -q`

## Không có server? Dùng JSON tĩnh

```bash
python -m api.export_static            # ghi api/static/v1/*.json (88 tệp, ~2,2 MB)
```
Cùng nội dung với endpoint, đặt trên GitHub Pages/Vercel/Netlify là frontend `fetch` được. Ánh xạ: `/api/v1/ranking?year=2025` → `ranking/2025.json`; `/trend?metric=K` → `trend/K.json`; `/banks/vcb/2025` → `banks/vcb/2025.json`. Phải chạy lại lệnh này sau mỗi lần pipeline cho kết quả mới.

## Endpoint (tiền tố `/api/v1`)

| Màn hình ở bảng phân công | Endpoint | Ghi chú |
|---|---|---|
| Khởi tạo, bộ lọc năm/trụ cột | `GET /meta` | Ngân hàng, năm, 6 trụ cột, 24 tiêu chí, 11 chỉ số DTI, 5 mức, phiên bản thuật toán |
| Bảng xếp hạng | `GET /ranking?year=2025&sort_by=rank` | `sort_by`: rank, score, bank, K, S, T, O, C, D; có `score_change`, `rank_change` so với năm trước |
| Biểu đồ xu hướng 2020–2025 | `GET /trend?metric=score&banks=tcb,vcb` | `metric`: score, data_confidence, K..D; `component`: p, dbi, dti (cho trụ cột); `from_year`, `to_year` |
| So sánh 5 ngân hàng | `GET /compare?year=2025&banks=tcb,vcb,mb` | `radar` 6 trụ cột, `leaders` dẫn đầu từng trụ cột |
| Nhà nước vs Cổ phần | `GET /group-comparison?year=2025` | Trung bình nhóm (3 và 2 ngân hàng, chỉ mô tả) |
| Chi tiết điểm thành phần | `GET /banks/{bank}/{year}` | 6 trụ cột + 24 tiêu chí kèm bằng chứng + 11 chỉ số DTI + `highlights` |
| (lọc từng phần) | `GET /banks/{bank}/{year}/criteria?pillar=T` · `GET /dti-indicators?year=&bank=&pillar=` | |
| Hồ sơ ngân hàng | `GET /banks/{bank}` | Điểm mới nhất + lịch sử 6 năm |
| Độ tin cậy dữ liệu | `GET /data-quality?year=2025&bank=vcb` | Độ phủ BCTN/BCTC/BCPTBV, rating app, cờ bất thường từ `dti_check.csv` |
| Độ nhạy nhanh | `GET /sensitivity?year=2025` | Chỉ kịch bản trọng số DBI/DTI (100/0, 80/20, 70/30, 60/40), mọi năm; cờ `stable_under_weights` **không phải** kết luận cuối |
| **Độ nhạy đầy đủ** | `GET /sensitivity/full?year=2025` | Từ `11_sensitivity.py`: Vững / Nhóm cùng mức, Monte Carlo, chuẩn hóa, cận L/U, cặp ngân hàng. Chỉ các năm đã chạy (2021, 2023, 2025) |
| Bảng kịch bản | `GET /sensitivity/scenarios?year=2025&family=G.&bank=tcb` | Điểm và hạng từng kịch bản × ngân hàng |
| Số liệu đầu vào + nguồn | `GET /dti-inputs?bank=tcb&year=2025&indicator=T-Q1` | Tệp nguồn, trang PDF, link, định nghĩa; `scope=all` thêm ô thiếu kèm lý do (`not_disclosed` / `not_collected`) |
| Cận L/U | `GET /dti-bounds` · `/dti-bounds/T-Q1` | Nguồn trích dẫn, lý do chọn, hạn chế, số liệu tham chiếu ngoài |
| Lớp C: chỉ tiêu | `GET /financial-performance?year=2025` | ROE, ROA, CIR, CASA, thu nhập ngoài lãi + điểm (cho biểu đồ phân tán) |
| Lớp C: tương quan | `GET /layer-c/correlation?score_var=dbi&lag=0` | Spearman, Kendall theo năm, gộp, gộp đã loại xu hướng năm |
| Một lần cho tất cả | `GET /snapshot` | `meta` + 30 bản ghi ngân hàng–năm |
| Kiểm tra sống | `GET /health` | Ngày sửa các tệp `out/` đang đọc |

Mã ngân hàng: `agribank`, `bidv`, `vcb`, `mb`, `tcb`. Mã trụ cột: `K S T O C D`.

## Quy ước dữ liệu frontend phải theo

1. **`null` = thiếu dữ liệu, không phải 0.** Ví dụ `dti: null` nghĩa là trụ cột đó không có chỉ số DTI nào, khi đó `p = dbi` (`dti_applied: false`). Biểu đồ nên ngắt đường hoặc ghi "chưa có", đừng vẽ về 0.
2. Điểm thang 0–100. `data_confidence` thang 0–1 (= số chỉ số DTI có dữ liệu / 11); `dti_indicators_available` cho sẵn dạng "7/11". `reliability` (`high ≥ 0,7`, `medium ≥ 0,4`, `low`) chỉ là quy ước hiển thị để tô màu huy hiệu.
3. **Xu hướng theo năm cần chú thích.** Khi số chỉ số DTI có dữ liệu đổi giữa các năm, chênh lệch điểm có thể một phần do độ phủ dữ liệu, không hoàn toàn do chuyển đổi số. API trả `dti_coverage_changes` và `warnings`; frontend nên hiện ra. Điểm DBI thuần (`component=dbi`) không bị ảnh hưởng.
4. **Tiêu chí `status = "no_mention"` (điểm 0)** nghĩa là thuật toán không tìm thấy đề cập trong tài liệu đã quét, **không** đồng nghĩa ngân hàng không công bố (luật 3b). Dùng `status_label` có sẵn để hiển thị, đừng tự viết "không công bố".
5. `evidence` của tiêu chí có `file`, `page`, `url` (từ `config/sources.csv`) và `quote` để truy vết nguồn (luật 4).
6. K-Q3 (rating app) và T-Q2 (8 nền tảng) chỉ áp dụng cho năm cuối của lần chạy, các năm trước luôn `null`.

## Lỗi

Mọi lỗi có dạng `{"error": {"code": "...", "message": "..."}}` với `bank_not_found` (404), `invalid_year` / `invalid_metric` / `invalid_sort` / `invalid_pillar` / `invalid_request` (422), `data_not_ready` (503, chưa có tệp trong `out/`).

## Ví dụ cho frontend

```js
const API = "http://localhost:8000/api/v1";
const get = async (p) => {
  const r = await fetch(API + p);
  if (!r.ok) throw new Error((await r.json()).error.message);
  return r.json();
};

const meta = await get("/meta");                                  // đổ bộ lọc năm/ngân hàng
const { items } = await get(`/ranking?year=${meta.latest_year}`); // bảng xếp hạng
const trend = await get("/trend?metric=score");                   // series[].points[{year, value}]
const detail = await get("/banks/vcb/2025");                      // trang chi tiết
// Vẽ điểm thiếu: giữ null để thư viện biểu đồ ngắt đường (Chart.js: spanGaps=false)
```

## Cấu trúc mã

```
api/main.py          route + CORS + định dạng lỗi
api/services*.py     logic: xếp hạng, xu hướng, so sánh, tiêu chí (services.py); số liệu đầu vào và cận L/U (_inputs); Lớp C (_layerc); độ nhạy đầy đủ (_sens)
api/definitions.py   chỉ số DTI dùng biến nào, công thức hiển thị, chỉ tiêu Lớp C
api/repository.py    đọc out/*.csv|xlsx, config/*.yaml, cache theo mtime
api/schemas.py       mô hình phản hồi (sinh OpenAPI)
api/export_static.py xuất JSON tĩnh
tests/test_api.py    24 test, đối chiếu API với kết quả của 10_score.py
```

## Lớp C: công thức và hướng phân tích đã chốt

Số liệu lấy từ `dti_inputs_confirmed.csv` (đã đối chiếu PDF), thiếu thì `null` và có cờ trong `flags`.

| Chỉ tiêu | Công thức |
|---|---|
| ROE | LNST / bình quân(vốn CSH đầu kỳ, cuối kỳ) × 100. Cả hai vế là phần thuộc cổ đông ngân hàng mẹ (cột `equity` của cả 30 dòng ghi `definition = parent`) |
| ROA | LNST / bình quân(tổng tài sản) × 100 |
| CIR | \|chi phí hoạt động\| / (\|chi phí hoạt động\| + LN thuần trước dự phòng) × 100, trùng `10_score.py` |
| CASA | tiền gửi không kỳ hạn / tiền gửi khách hàng × 100 (cuối kỳ) |
| Thu nhập ngoài lãi (phụ) | (TOI − thu nhập lãi thuần) / TOI × 100 |

Thiếu năm trước (2019) thì dùng số cuối kỳ và ghi cờ, cùng quy tắc của `10_score.py`.

Tương quan: biến điểm mặc định là **DBI trung bình 6 trụ cột**, không phải Score_Bank. Lý do: Score_Bank có 20% DTI mà O-Q1 (từ CIR), O-Q2 và T-Q1 (từ tổng tài sản) lấy từ chính báo cáo tài chính, nên tương quan với CIR và ROA có phần cơ học. Có thể đổi bằng `score_var=score`. Hệ số Spearman ρ và Kendall τ-b, báo theo từng năm (n ≤ 5, chỉ mô tả), gộp mọi năm, và gộp sau khi loại xu hướng chung theo năm. `lag=1` ghép điểm năm t với chỉ tiêu năm t+1.

## Chưa có trong API

- Điểm của `11_sensitivity.py` chỉ có cho các năm đã chạy; thêm năm bằng `python 11_sensitivity.py --years ...` rồi xuất lại JSON tĩnh.
- Biểu đồ PNG của `sens_plots.py` (heatmap, Monte Carlo) không phục vụ qua API; frontend nên tự vẽ từ `/sensitivity/full`.
