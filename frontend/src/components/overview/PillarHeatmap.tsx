import type { RankingItem } from '../../api/dashboard'
import { BANK_COLORS, BANK_SHORT, formatScore } from './shared'

const LEVELS = [
  { max: 25, name: 'Khởi động' },
  { max: 50, name: 'Bắt đầu' },
  { max: 75, name: 'Hình thành' },
  { max: 100.0001, name: 'Nâng cao' },
]

const levelOf = (v: number) => {
  const idx = LEVELS.findIndex((l) => v < l.max)
  return idx === -1 ? LEVELS.length - 1 : idx
}

interface Props {
  items: RankingItem[]
  year: number
}

export default function PillarHeatmap({ items, year }: Props) {
  const codes = Object.keys(items[0]?.pillars ?? {})
  const best: Record<string, number | null> = {}
  for (const c of codes) {
    const vals = items.map((i) => i.pillars[c]?.p).filter((v): v is number => v != null)
    best[c] = vals.length ? Math.max(...vals) : null
  }

  return (
    <div className="ov-heat" key={year}>
      <div className="ov-heat__scroll">
        <table className="ov-heat__table">
          <thead>
            <tr>
              <th scope="col">Ngân hàng</th>
              {codes.map((c) => (
                <th scope="col" key={c}>
                  {items[0].pillars[c].name}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {items.map((item, row) => (
              <tr key={item.bank}>
                <th scope="row">
                  <span
                    className="ov-heat__bank"
                    style={{ '--bank-color': BANK_COLORS[item.bank] } as React.CSSProperties}
                  >
                    <i />
                    {BANK_SHORT[item.bank]}
                  </span>
                </th>
                {codes.map((c, col) => {
                  const p = item.pillars[c]
                  const v = p?.p
                  const isBest = v != null && v === best[c]
                  return (
                    <td key={c}>
                      <span
                        className={`ov-heat__cell lv-${v == null ? 'na' : levelOf(v)}${isBest ? ' is-best' : ''}`}
                        style={{ '--i': row + col } as React.CSSProperties}
                        title={
                          v == null
                            ? 'Chưa có dữ liệu'
                            : `${LEVELS[levelOf(v)].name} · DBI ${formatScore(p.dbi)}${
                                p.dti_applied ? ` · DTI ${formatScore(p.dti)}` : ' · chưa có DTI'
                              }`
                        }
                      >
                        {formatScore(v == null ? null : Math.round(v * 10) / 10)}
                        {v != null && !p.dti_applied && <sup aria-label="chỉ có DBI">*</sup>}
                      </span>
                    </td>
                  )
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="ov-heat__legend">
        {LEVELS.map((l, i) => (
          <span key={l.name}>
            <i className={`lv-${i}`} />
            {l.name}
          </span>
        ))}
        <span>
          <i className="ov-heat__best" />
          Cao nhất trụ cột
        </span>
        <span>
          <sup>*</sup> Trụ cột chỉ có DBI, chưa có DTI
        </span>
      </div>
    </div>
  )
}
