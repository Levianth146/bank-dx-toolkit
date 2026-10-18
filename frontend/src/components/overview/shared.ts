import { useEffect, useRef, useState } from 'react'
import type { RankingItem } from '../../api/dashboard'

export const BANK_COLORS: Record<string, string> = {
  vcb: '#007a4b',
  mb: '#0648a8',
  tcb: '#e7163d',
  bidv: '#008b8b',
  agribank: '#a31c28',
}

export const BANK_SHORT: Record<string, string> = {
  vcb: 'Vietcombank',
  mb: 'MB',
  tcb: 'Techcombank',
  bidv: 'BIDV',
  agribank: 'Agribank',
}

/** Các ngân hàng cách nhau dưới ngưỡng này (điểm) được xếp cùng nhóm.
 *  Đây là quy ước hiển thị, không phải kiểm định thống kê. */
export const TIER_GAP = 3

export const formatScore = (value: number | null | undefined) =>
  value == null
    ? '—'
    : new Intl.NumberFormat('vi-VN', { maximumFractionDigits: 2 }).format(value)

export interface Tier {
  index: number
  items: RankingItem[]
  min: number
  max: number
}

/** Gom các ngân hàng (đã sắp theo điểm giảm dần) thành nhóm theo khoảng cách liền kề. */
export function buildTiers(items: RankingItem[]): Tier[] {
  const sorted = [...items].sort((a, b) => b.score - a.score)
  const tiers: Tier[] = []
  for (const item of sorted) {
    const last = tiers[tiers.length - 1]
    const prev = last?.items[last.items.length - 1]
    if (last && prev && prev.score - item.score < TIER_GAP) {
      last.items.push(item)
      last.min = item.score
    } else {
      tiers.push({
        index: tiers.length + 1,
        items: [item],
        min: item.score,
        max: item.score,
      })
    }
  }
  return tiers
}

export function joinNames(names: string[]) {
  if (names.length <= 1) return names.join('')
  return `${names.slice(0, -1).join(', ')} và ${names[names.length - 1]}`
}

export function usePrefersReducedMotion() {
  const [reduced, setReduced] = useState(
    () =>
      typeof window !== 'undefined' &&
      window.matchMedia?.('(prefers-reduced-motion: reduce)').matches,
  )
  useEffect(() => {
    const query = window.matchMedia?.('(prefers-reduced-motion: reduce)')
    if (!query) return
    const onChange = () => setReduced(query.matches)
    query.addEventListener('change', onChange)
    return () => query.removeEventListener('change', onChange)
  }, [])
  return reduced
}

/** Đếm số từ giá trị trước tới giá trị mới, một lần mỗi khi giá trị đổi. */
export function useCountUp(target: number | null | undefined, duration = 900) {
  const reduced = usePrefersReducedMotion()
  const [animated, setAnimated] = useState<number>(target ?? 0)
  const from = useRef<number>(target ?? 0)

  useEffect(() => {
    if (target == null || reduced) return
    const start = performance.now()
    const origin = from.current
    let frame = 0
    const tick = (now: number) => {
      const t = Math.min(1, (now - start) / duration)
      const next = origin + (target - origin) * (1 - Math.pow(1 - t, 3))
      from.current = next
      setAnimated(next)
      if (t < 1) frame = requestAnimationFrame(tick)
    }
    frame = requestAnimationFrame(tick)
    return () => cancelAnimationFrame(frame)
  }, [target, duration, reduced])

  return target == null || reduced ? (target ?? null) : animated
}
