import { useMemo } from 'react'
import type { RankingItem } from '../../api/dashboard'
import { BANK_COLORS, BANK_SHORT, TIER_GAP, buildTiers, formatScore } from './shared'

interface Props {
  items: RankingItem[]
  year: number
}

export default function TierStrip({ items, year }: Props) {
  const tiers = useMemo(() => buildTiers(items), [items])

  const lo = Math.max(0, Math.floor((Math.min(...items.map((i) => i.score)) - 6) / 10) * 10)
  const hi = Math.min(100, Math.ceil((Math.max(...items.map((i) => i.score)) + 6) / 10) * 10)
  const pos = (score: number) => ((score - lo) / (hi - lo)) * 100

  const ticks: number[] = []
  for (let t = lo; t <= hi; t += 10) ticks.push(t)

  return (
    <div className="ov-tiers" key={year}>
      <div className="ov-tiers__axis">
        {ticks.map((t) => (
          <span key={t} style={{ left: `${pos(t)}%` }}>
            {t}
          </span>
        ))}

        {tiers.map((tier) => (
          <div
            key={tier.index}
            className="ov-tiers__group"
            style={{ left: `${pos(tier.min)}%`, width: `${Math.max(0.8, pos(tier.max) - pos(tier.min))}%` }}
          >
            <i />
            <b>
              Nhóm {tier.index}
            </b>
          </div>
        ))}

        {[...items].sort((a, b) => b.score - a.score).map((item, i) => (
          <div
            key={item.bank}
            className="ov-tiers__dot"
            style={
              {
                left: `${pos(item.score)}%`,
                '--bank-color': BANK_COLORS[item.bank],
                '--i': i,
                '--lift': `${(i % 3) * 26}px`,
              } as React.CSSProperties
            }
          >
            <span className="ov-tiers__tip">
              {BANK_SHORT[item.bank]} · {formatScore(item.score)}
            </span>
          </div>
        ))}
      </div>

      <ol className="ov-tiers__list">
        {tiers.map((tier) => (
          <li key={tier.index}>
            <strong>Nhóm {tier.index}</strong>
            <span>
              {tier.items.map((i) => BANK_SHORT[i.bank]).join(', ')}
              {tier.items.length > 1 && (
                <em>
                  {' '}
                  (chênh {formatScore(tier.max - tier.min)} điểm)
                </em>
              )}
            </span>
          </li>
        ))}
      </ol>

      <p className="ov-tiers__note">
        Ngân hàng cách nhau dưới {TIER_GAP} điểm được xếp cùng nhóm. Ngưỡng này là quy ước
        hiển thị: điểm DBI do luật tự động chấm và chưa được chuyên gia kiểm chứng, nên các
        vị trí sát nhau chưa đủ cơ sở để phân hạng.
      </p>
    </div>
  )
}
