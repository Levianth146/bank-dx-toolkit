import { useMemo, useState } from "react";
import type { TrendResponse } from "../../api/dashboard";
import { BANK_COLORS, BANK_SHORT, formatScore } from "./shared";

const W = 960;
const H = 330;
const M = { l: 44, r: 118, t: 18, b: 30 };

interface Props {
  trend: TrendResponse;
  selectedYear: number;
  visibleBanks: Set<string>;
  onSelectYear: (year: number) => void;
}

export default function JourneyChart({
  trend,
  selectedYear,
  visibleBanks,
  onSelectYear,
}: Props) {
  const [focused, setFocused] = useState<string | null>(null);

  const series = useMemo(
    () => trend.series.filter((s) => visibleBanks.has(s.bank)),
    [trend, visibleBanks],
  );

  const geometry = useMemo(() => {
    const years = trend.years;
    const values = series.flatMap((s) =>
      s.points.map((p) => p.value).filter((v): v is number => v != null),
    );
    const lo = values.length
      ? Math.max(0, Math.floor((Math.min(...values) - 4) / 10) * 10)
      : 0;
    const hi = values.length
      ? Math.min(100, Math.ceil((Math.max(...values) + 4) / 10) * 10)
      : 100;
    const x = (year: number) => {
      const i = years.indexOf(year);
      return M.l + (i * (W - M.l - M.r)) / Math.max(1, years.length - 1);
    };
    const y = (v: number) => M.t + ((hi - v) / (hi - lo)) * (H - M.t - M.b);
    const ticks: number[] = [];
    for (let t = lo; t <= hi; t += 10) ticks.push(t);
    return { years, lo, hi, x, y, ticks };
  }, [trend, series]);

  const { years, x, y, ticks } = geometry;

  // Nhãn cuối đường: đẩy ra để không chồng nhau.
  const endLabels = useMemo(() => {
    const rows = series
      .map((s) => {
        const last = [...s.points].reverse().find((p) => p.value != null);
        return last ? { bank: s.bank, y: y(last.value as number) } : null;
      })
      .filter((r): r is { bank: string; y: number } => r !== null)
      .sort((a, b) => a.y - b.y);
    const gap = 21;
    for (let i = 1; i < rows.length; i++) {
      if (rows[i].y - rows[i - 1].y < gap) rows[i].y = rows[i - 1].y + gap;
    }
    return rows;
  }, [series, y]);

  const readout = useMemo(
    () =>
      series
        .map((s) => ({
          bank: s.bank,
          value: s.points.find((p) => p.year === selectedYear)?.value ?? null,
        }))
        .filter((r) => r.value != null)
        .sort((a, b) => (b.value as number) - (a.value as number)),
    [series, selectedYear],
  );

  function pathFor(points: TrendResponse["series"][number]["points"]) {
    let d = "";
    let pen = false;
    for (const p of points) {
      if (p.value == null) {
        pen = false;
        continue;
      }
      d += `${pen ? "L" : "M"}${x(p.year).toFixed(1)} ${y(p.value).toFixed(1)} `;
      pen = true;
    }
    return d.trim();
  }

  return (
    <div className="ov-journey">
      <div className="ov-journey__scroll">
        <svg
          className="ov-journey__svg"
          viewBox={`0 0 ${W} ${H}`}
          role="img"
          aria-label={`Điểm tổng hợp của ${series.length} ngân hàng từ ${years[0]} đến ${years[years.length - 1]}`}
        >
          {ticks.map((t) => (
            <g key={t}>
              <line
                className="ov-journey__grid"
                x1={M.l}
                x2={W - M.r}
                y1={y(t)}
                y2={y(t)}
              />
              <text
                className="ov-journey__tick"
                x={M.l - 10}
                y={y(t) + 4}
                textAnchor="end"
              >
                {t}
              </text>
            </g>
          ))}

          <line
            className="ov-journey__marker"
            x1={x(selectedYear)}
            x2={x(selectedYear)}
            y1={M.t}
            y2={H - M.b}
          />

          {years.map((year) => (
            <rect
              key={year}
              className="ov-journey__hit"
              x={x(year) - (W - M.l - M.r) / (years.length - 1) / 2}
              y={M.t}
              width={(W - M.l - M.r) / (years.length - 1)}
              height={H - M.t - M.b}
              onClick={() => onSelectYear(year)}
            />
          ))}

          {series.map((s, index) => {
            const dim = focused != null && focused !== s.bank;
            return (
              <g
                key={s.bank}
                className={`ov-journey__bank${dim ? " is-dim" : ""}`}
                style={
                  { "--bank-color": BANK_COLORS[s.bank] } as React.CSSProperties
                }
              >
                <path
                  className="ov-journey__line"
                  d={pathFor(s.points)}
                  pathLength={1}
                  style={{ animationDelay: `${index * 130}ms` }}
                />
                {s.points.map((p) =>
                  p.value == null ? null : (
                    <circle
                      key={p.year}
                      className={`ov-journey__dot${p.year === selectedYear ? " is-selected" : ""}`}
                      cx={x(p.year)}
                      cy={y(p.value)}
                      r={p.year === selectedYear ? 6 : 3.5}
                    >
                      <title>{`${s.bank_name} ${p.year}: ${formatScore(p.value)}`}</title>
                    </circle>
                  ),
                )}
              </g>
            );
          })}

          {endLabels.map((label) => (
            <g
              key={label.bank}
              className="ov-journey__end"
              tabIndex={0}
              role="button"
              aria-label={`Làm nổi ${BANK_SHORT[label.bank]}`}
              onMouseEnter={() => setFocused(label.bank)}
              onMouseLeave={() => setFocused(null)}
              onFocus={() => setFocused(label.bank)}
              onBlur={() => setFocused(null)}
            >
              <rect
                x={W - M.r + 8}
                y={label.y - 9}
                width={M.r - 8}
                height={18}
                rx={9}
                fill={BANK_COLORS[label.bank]}
              />
              <text
                x={W - M.r + 17}
                y={label.y + 4}
                className="ov-journey__endtext"
              >
                {BANK_SHORT[label.bank]}
              </text>
            </g>
          ))}
        </svg>
      </div>

      <div className="ov-journey__years" role="group" aria-label="Chọn năm">
        {years.map((year) => (
          <button
            key={year}
            type="button"
            className={`ov-journey__year${year === selectedYear ? " is-active" : ""}`}
            aria-pressed={year === selectedYear}
            onClick={() => onSelectYear(year)}
          >
            {year}
          </button>
        ))}
      </div>

      <p className="ov-journey__readout" aria-live="polite">
        <strong>{selectedYear}</strong>
        {readout.map((r) => (
          <span
            key={r.bank}
            style={
              { "--bank-color": BANK_COLORS[r.bank] } as React.CSSProperties
            }
          >
            <i />
            {BANK_SHORT[r.bank]} {formatScore(r.value)}
          </span>
        ))}
      </p>
    </div>
  );
}
