# Độ nhạy của luật chấm DBI (rule-based-v1 so với bản siết)

Ngày 2026-10-17. Mục đích: cho thấy thứ hạng phụ thuộc vào cách viết luật văn bản của `09c_auto_score.py`.

## Bản siết (đối chứng, không dùng làm kết quả chính)

Thay đổi so với `rule-based-v1`:
- ACTION: bỏ động từ quá chung (xây dựng, áp dụng, hoàn thành, completed, established, introduced, signed); `chứng nhận` đổi thành `đạt/được chứng nhận`.
- NUM: số phải đi kèm đơn vị của đối tượng (%, khách hàng, giờ, người...); bỏ đơn vị tiền tệ (tỷ, VND, million, billion).
- MULTI_YEAR: cần dải năm, "từ 20xx đến 20xx" hoặc so sánh với năm khác; bỏ mẫu "hai năm bất kỳ trong 40 ký tự".
- INDEP: bỏ từ chung (giải thưởng, xếp hạng, chứng nhận), tên công ty kiểm toán (Deloitte, PwC, KPMG, Ernst) và Fitch/Moody; thêm "kiểm chứng độc lập".

Kết quả: 143/720 ô đổi điểm (138 giảm, 5 tăng); tỷ lệ ô điểm 4 năm 2025 giảm từ 44% xuống 32%.
Bảng: `output_data/sensitivity/dbi_rules_strict_score_summary.csv`, `output_data/sensitivity/dbi_rules_strict_auto_scores.csv`.

## Điểm tổng 2020–2025 (cận DTI v2, bước 0b)

| Ngân hàng | Chính 2024 | Siết 2024 | Chính 2025 | Siết 2025 |
|---|---:|---:|---:|---:|
| TCB | 61,7 | 42,5 | 77,5 | 66,5 |
| VCB | 63,3 | 58,1 | 74,9 | 71,1 |
| MB | 61,9 | 49,9 | 73,3 | 68,8 |
| BIDV | 63,7 | 58,5 | 63,4 | 63,4 |
| Agribank | 48,1 | 41,8 | 54,9 | 51,2 |

Hạng 1 năm 2025 là TCB theo luật chính nhưng VCB theo luật siết. Năm 2024, TCB đứng hạng 4 sát 3 ngân hàng còn lại theo luật chính (61,7 so với 63,7) và tụt xa hơn theo luật siết (42,5).

## Kết luận kiểm tra mẫu

Đọc tay (do AI đọc đoạn trích, chưa phải chuyên gia) 24 ô bị đổi điểm: luật siết đúng hơn ở khoảng 6 ô
(loại tiểu sử "completed a degree", lịch sử "Established under the name...", giải thưởng chung chung) nhưng sai hơn ở khoảng 9 ô
(mất bằng chứng thật như PCI DSS đạt chứng nhận, "completed 3 pillars of Basel 2", "migrated 90%", giải "Best Digital Transformation Bank"); 9 ô chưa rõ.
Cả hai bản đều có lỗi theo hai hướng khác nhau, nên chưa bản nào được coi là đã kiểm chứng. Thứ hạng ở 2024 (4 ngân hàng trong 2 điểm)
và vị trí 1–3 năm 2025 không nên báo cáo là thứ tự cứng.

## Việc cần làm để có độ chính xác thật

Người đọc báo cáo gốc chấm lại một mẫu phân tầng (ví dụ 40–60 ô, đủ mức 0–4 và đủ 5 ngân hàng), so với điểm thuật toán,
báo cáo tỷ lệ đồng ý và sai số theo từng mức. Chưa có số này thì không nêu độ chính xác của điểm DBI.
