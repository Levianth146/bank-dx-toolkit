// Lucian UX/UI Prompt #208 · MIT License (c) 2026 Seokwoooo · https://lucianlabs.dev/uxui-prompt/#208
import { useEffect, useRef } from 'react'

type YearPickerProps = {
  years: number[]
  selectedYear: number
  onSelectYear: (year: number) => void
}

const BASE_SIZE = 39
const SPREAD = 58
const GAP = 3

export default function YearPicker({
  years,
  selectedYear,
  onSelectYear,
}: YearPickerProps) {
  const rootRef = useRef<HTMLDivElement>(null)
  const buttonsRef = useRef<Array<HTMLButtonElement | null>>([])
  const scheduleRef = useRef<() => void>(() => {})
  const focusedIndexRef = useRef(-1)

  useEffect(() => {
    const root = rootRef.current
    if (!root) return

    const dock = root.querySelector<HTMLElement>('.u208-dk')
    const tip = root.querySelector<HTMLElement>('.u208-tip')
    if (!dock || !tip) return

    let baseSize = window.matchMedia('(max-width: 480px)').matches ? 34 : BASE_SIZE
    let maxSize = baseSize + 14
    buttonsRef.current.slice(0, years.length).forEach((button) => {
      if (!button) return
      button.dataset.size = String(baseSize)
      button.style.setProperty('--s', `${baseSize}px`)
    })

    let pointerX: number | null = null
    let frameId = 0
    let reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches

    const frame = () => {
      frameId = 0
      if (!root.isConnected) return

      let busy = false
      let bestIndex = -1
      let bestSize = 0
      const focusedIndex = focusedIndexRef.current

      buttonsRef.current.slice(0, years.length).forEach((button, index) => {
        if (!button) return

        let targetSize = baseSize
        if (pointerX !== null) {
          const center = (index - (years.length - 1) / 2) * (baseSize + GAP)
          const distance = (pointerX - center) / SPREAD
          targetSize =
            baseSize + (maxSize - baseSize) * Math.exp(-distance * distance * 1.6)
        } else if (focusedIndex === index) {
          targetSize = baseSize + (maxSize - baseSize) * 0.8
        }

        const currentSize = Number(button.dataset.size ?? baseSize)
        const nextSize =
          currentSize + (targetSize - currentSize) * (reducedMotion ? 1 : 0.28)
        const settled = Math.abs(targetSize - nextSize) <= 0.1
        const size = settled ? targetSize : nextSize

        button.dataset.size = String(size)
        button.style.setProperty('--s', `${size.toFixed(2)}px`)
        button.style.setProperty(
          '--lift',
          `${((size - baseSize) * 0.25).toFixed(2)}px`,
        )
        button.style.setProperty(
          '--label-scale',
          '1',
        )

        if (!settled) busy = true
        if (size > bestSize) {
          bestSize = size
          bestIndex = index
        }
      })

      if ((pointerX !== null || focusedIndex >= 0) && bestSize > baseSize + 8) {
        const button = buttonsRef.current[bestIndex]
        if (button) {
          const buttonRect = button.getBoundingClientRect()
          const rootRect = root.getBoundingClientRect()
          tip.textContent = `Năm ${years[bestIndex]}`
          tip.style.left = `${buttonRect.left + buttonRect.width / 2 - rootRect.left}px`
          tip.classList.add('is-on')
        }
      } else {
        tip.classList.remove('is-on')
      }

      if (busy) frameId = window.requestAnimationFrame(frame)
    }

    const schedule = () => {
      if (!frameId) frameId = window.requestAnimationFrame(frame)
    }
    scheduleRef.current = schedule

    const handlePointerMove = (event: PointerEvent) => {
      const rootRect = root.getBoundingClientRect()
      const dockRect = dock.getBoundingClientRect()
      const scaledY = event.clientY - dockRect.bottom
      pointerX =
        scaledY > -130 && scaledY < 10
          ? event.clientX - rootRect.left - rootRect.width / 2
          : null
      schedule()
    }
    const handlePointerLeave = () => {
      pointerX = null
      schedule()
    }
    const motionPreference = window.matchMedia('(prefers-reduced-motion: reduce)')
    const mobileLayout = window.matchMedia('(max-width: 480px)')
    const handleMotionChange = (event: MediaQueryListEvent) => {
      reducedMotion = event.matches
      schedule()
    }
    const handleLayoutChange = (event: MediaQueryListEvent) => {
      baseSize = event.matches ? 34 : BASE_SIZE
      maxSize = baseSize + 14
      schedule()
    }

    root.addEventListener('pointermove', handlePointerMove)
    root.addEventListener('pointerleave', handlePointerLeave)
    motionPreference.addEventListener('change', handleMotionChange)
    mobileLayout.addEventListener('change', handleLayoutChange)
    schedule()

    return () => {
      root.removeEventListener('pointermove', handlePointerMove)
      root.removeEventListener('pointerleave', handlePointerLeave)
      motionPreference.removeEventListener('change', handleMotionChange)
      mobileLayout.removeEventListener('change', handleLayoutChange)
      if (frameId) window.cancelAnimationFrame(frameId)
      scheduleRef.current = () => {}
    }
  }, [years])

  return (
    <div className="u208 year-picker" role="group" aria-label="Chọn năm" ref={rootRef}>
      <div className="u208-dk">
        {years.map((year, index) => (
          <button
            type="button"
            key={year}
            ref={(button) => {
              buttonsRef.current[index] = button
              if (button && !button.dataset.size) {
                button.dataset.size = String(BASE_SIZE)
              }
            }}
            className={`u208-a year-button${year === selectedYear ? ' selected' : ''}`}
            aria-label={`Chọn năm ${year}`}
            aria-pressed={year === selectedYear}
            onClick={(event) => {
              const button = event.currentTarget
              button.classList.remove('is-hop')
              void button.offsetWidth
              button.classList.add('is-hop')
              onSelectYear(year)
            }}
            onFocus={() => {
              focusedIndexRef.current = index
              scheduleRef.current()
            }}
            onBlur={() => {
              focusedIndexRef.current = -1
              scheduleRef.current()
            }}
          >
            <span className="u208-label">{year}</span>
          </button>
        ))}
      </div>
      <span className="u208-tip" aria-hidden="true" />
    </div>
  )
}
