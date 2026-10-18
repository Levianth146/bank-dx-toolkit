import type { RankingItem } from '../../api/dashboard'

interface Props {
  items: RankingItem[]
  year: number
}

export default function DataNotice({ items, year }: Props) {
  const first = items[0]
  const codes = Object.keys(first?.pillars ?? {})
  const withDti = codes.filter((c) => items.every((i) => i.pillars[c]?.dti_applied)).length
  const total = codes.length

  return (
    <aside className="ov-notice" aria-label="Lưu ý về dữ liệu">
      <h3>Đọc số năm {year} thế nào cho đúng</h3>
      <ul>
        <li>
          {withDti === 0 ? (
            <>
              Năm {year} chưa có chỉ số DTI nào đủ điều kiện, nên điểm chỉ phản ánh DBI
              (chấm từ văn bản công bố).
            </>
          ) : (
            <>
              DTI chỉ tác động tới <strong>{withDti}/{total} trụ cột</strong> năm {year}; các
              trụ cột còn lại chỉ có DBI. Chỉ số DTI chỉ được dùng khi cả 5 ngân hàng đều có
              dữ liệu.
            </>
          )}
        </li>
        <li>
          DBI do luật tự động chấm (rule-based-v1) và chưa được chuyên gia kiểm chứng. Mức 0
          nghĩa là không tìm thấy từ khóa, chưa chắc ngân hàng không làm.
        </li>
        <li>
          So sánh giữa các năm cần thận trọng: số trụ cột có DTI thay đổi theo năm.
        </li>
      </ul>
    </aside>
  )
}
