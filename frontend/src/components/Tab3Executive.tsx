import { useEffect, useMemo, useState } from 'react'
import {
  ArrowDownWideNarrow,
  ArrowUpWideNarrow,
  Check,
  ExternalLink,
  FileSearch,
  Info,
  SlidersHorizontal,
  X,
} from 'lucide-react'
import type { CSSProperties } from 'react'
import type {
  BankDetailResponse,
  DashboardMeta,
} from '../api/dashboard'

const BANK_ORDER = ['vcb', 'mb', 'tcb', 'bidv', 'agribank']

const BANK_COLORS: Record<string, string> = {
  vcb: '#007a4b',
  mb: '#0648a8',
  tcb: '#e7163d',
  bidv: '#008b8b',
  agribank: '#a31c28',
}

const PILLAR_COLORS: Record<string, string> = {
  K: '#7cb9e8',
  S: '#f4b183',
  T: '#8fd19e',
  O: '#c3a6f2',
  C: '#f7c8d0',
  D: '#a8dadc',
}

type CriterionRow = {
  code: string
  name: string
  pillar: string
  pillarName: string
  scores: Record<string, number | null>
}

type IndicatorRow = {
  code: string
  name: string
  unit: string
  direction: string
  lower: number | null
  upper: number | null
  values: Record<
    string,
    {
      x: number | null
      z: number | null
      hasData: boolean
      status: string
      note: string | null
    }
  >
}

const formatNumber = (value: number | null | undefined, digits = 1) =>
  value == null
    ? '—'
    : new Intl.NumberFormat('vi-VN', {
        maximumFractionDigits: digits,
      }).format(value)

function standardDeviation(values: number[]) {
  if (values.length < 2) return null
  const mean = values.reduce((sum, value) => sum + value, 0) / values.length
  const variance =
    values.reduce((sum, value) => sum + (value - mean) ** 2, 0) /
    (values.length - 1)
  return Math.sqrt(variance)
}

function getLevelClass(score: number | null | undefined) {
  return score == null ? 'is-missing' : `level-${Math.round(score)}`
}

function Tab3Executive({
  banks,
  pillars,
  details,
  year,
  loading,
  error,
}: {
  banks: DashboardMeta['banks']
  pillars: DashboardMeta['pillars']
  details: BankDetailResponse[]
  year: number
  loading: boolean
  error: string | null
}) {
  const [selectedPillar, setSelectedPillar] = useState('all')
  const [sortBySpread, setSortBySpread] = useState(false)
  const [dtiFilter, setDtiFilter] = useState<'all' | 'pass' | 'excluded'>('all')
  const [selectedCriterionCode, setSelectedCriterionCode] = useState<string | null>(
    null,
  )

  const orderedBanks = useMemo(
    () =>
      [...banks].sort((a, b) => {
        const aOrder = BANK_ORDER.indexOf(a.id)
        const bOrder = BANK_ORDER.indexOf(b.id)
        return (aOrder < 0 ? BANK_ORDER.length : aOrder) -
          (bOrder < 0 ? BANK_ORDER.length : bOrder)
      }),
    [banks],
  )
  const detailByBank = useMemo(
    () => new Map(details.map((detail) => [detail.summary.bank, detail])),
    [details],
  )

  const criterionRows = useMemo(() => {
    const byCode = new Map<string, CriterionRow>()
    for (const detail of details) {
      for (const criterion of detail.criteria) {
        const row = byCode.get(criterion.criterion) ?? {
          code: criterion.criterion,
          name: criterion.name,
          pillar: criterion.pillar,
          pillarName: criterion.pillar_name,
          scores: {},
        }
        row.scores[detail.summary.bank] = criterion.score
        byCode.set(criterion.criterion, row)
      }
    }
    return [...byCode.values()].sort((a, b) =>
      a.code.localeCompare(b.code, undefined, { numeric: true }),
    )
  }, [details])

  const indicatorRows = useMemo(() => {
    const byCode = new Map<string, IndicatorRow>()
    for (const detail of details) {
      for (const indicator of detail.dti_indicators) {
        const row = byCode.get(indicator.indicator) ?? {
          code: indicator.indicator,
          name: indicator.name,
          unit: indicator.unit,
          direction: indicator.direction,
          lower: indicator.L,
          upper: indicator.U,
          values: {},
        }
        row.values[detail.summary.bank] = {
          x: indicator.x,
          z: indicator.z,
          hasData: indicator.has_data,
          status: indicator.status,
          note: indicator.note ?? null,
        }
        byCode.set(indicator.indicator, row)
      }
    }
    return [...byCode.values()].sort((a, b) =>
      a.code.localeCompare(b.code, undefined, { numeric: true }),
    )
  }, [details])

  const visibleCriteria = useMemo(() => {
    const rows = criterionRows.filter(
      (row) => selectedPillar === 'all' || row.pillar === selectedPillar,
    )
    if (!sortBySpread) return rows
    return rows.sort((a, b) => {
      const valuesA = orderedBanks
        .map((bank) => a.scores[bank.id])
        .filter((value): value is number => value != null)
      const valuesB = orderedBanks
        .map((bank) => b.scores[bank.id])
        .filter((value): value is number => value != null)
      return (standardDeviation(valuesB) ?? -1) -
        (standardDeviation(valuesA) ?? -1)
    })
  }, [criterionRows, orderedBanks, selectedPillar, sortBySpread])

  const overallScores = useMemo(
    () =>
      orderedBanks.map((bank) => {
        const values = criterionRows
          .map((row) => row.scores[bank.id])
          .filter((value): value is number => value != null)
        const score =
          values.length > 0
            ? (values.reduce((sum, value) => sum + value, 0) / values.length) *
              25
            : null
        return { ...bank, score }
      }),
    [criterionRows, orderedBanks],
  )

  const mostDifferent = useMemo(
    () =>
      criterionRows
        .map((row) => {
          const values = orderedBanks
            .map((bank) => row.scores[bank.id])
            .filter((value): value is number => value != null)
          return { ...row, spread: standardDeviation(values) }
        })
        .filter(
          (row): row is CriterionRow & { spread: number } =>
            row.spread != null,
        )
        .sort((a, b) => b.spread - a.spread)
        .slice(0, 5),
    [criterionRows, orderedBanks],
  )

  const mostConsistent = useMemo(
    () =>
      criterionRows
        .map((row) => {
          const values = orderedBanks
            .map((bank) => row.scores[bank.id])
            .filter((value): value is number => value != null)
          return { ...row, spread: standardDeviation(values) }
        })
        .filter(
          (row): row is CriterionRow & { spread: number } =>
            row.spread != null,
        )
        .sort((a, b) => a.spread - b.spread)
        .slice(0, 5),
    [criterionRows, orderedBanks],
  )

  const dtiRowsWithCompleteness = useMemo(
    () =>
      indicatorRows.map((row) => {
        const available = orderedBanks.filter(
          (bank) => row.values[bank.id]?.hasData,
        ).length
        const missing = orderedBanks.length - available
        return { ...row, available, missing, excluded: missing >= 2 }
      }),
    [indicatorRows, orderedBanks],
  )

  const visibleIndicators = dtiRowsWithCompleteness.filter((row) => {
    if (dtiFilter === 'pass') return !row.excluded
    if (dtiFilter === 'excluded') return row.excluded
    return true
  })

  const selectedCriterion = selectedCriterionCode
    ? criterionRows.find((row) => row.code === selectedCriterionCode) ?? null
    : null

  useEffect(() => {
    if (!selectedCriterionCode) return
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') setSelectedCriterionCode(null)
    }
    window.addEventListener('keydown', onKeyDown)
    return () => window.removeEventListener('keydown', onKeyDown)
  }, [selectedCriterionCode])

  if (loading && details.length === 0) {
    return (
      <div className="loading-state">
        <SlidersHorizontal size={20} />
        <strong>Đang tải dữ liệu chỉ tiêu năm {year}</strong>
        <p>Danh sách DBI và DTI được lấy trực tiếp từ backend.</p>
      </div>
    )
  }

  if (error && details.length === 0) {
    return (
      <div className="error-state" role="alert">
        <strong>Không tải được dữ liệu chỉ tiêu</strong>
        <p>{error}</p>
      </div>
    )
  }

  if (details.length === 0) {
    return (
      <div className="empty-selection">
        <strong>Backend chưa trả dữ liệu chỉ tiêu cho năm {year}</strong>
        <p>Hãy thử chọn năm khác hoặc kiểm tra kết nối backend.</p>
      </div>
    )
  }

  return (
    <div className="indicator-page">
      {error && (
        <div className="warning-note" role="alert">
          <Info size={14} />
          <span>Không thể cập nhật một phần dữ liệu: {error}</span>
        </div>
      )}

      <section className="indicator-intro">
        <p>
          Ở từng tiêu chí, {orderedBanks.length} ngân hàng khác nhau ra sao? Khám
          phá {criterionRows.length} tiêu chí định tính DBI và{' '}
          {indicatorRows.length} chỉ số định lượng DTI trong năm {year}.
        </p>
        <div className="indicator-pillar-filters" aria-label="Lọc theo trụ cột">
          <button
            type="button"
            className={selectedPillar === 'all' ? 'is-active' : ''}
            aria-pressed={selectedPillar === 'all'}
            onClick={() => setSelectedPillar('all')}
          >
            Tất cả <span>{criterionRows.length}</span>
          </button>
          {pillars.map((pillar) => {
            const count = criterionRows.filter(
              (row) => row.pillar === pillar.code,
            ).length
            return (
              <button
                type="button"
                key={pillar.code}
                className={selectedPillar === pillar.code ? 'is-active' : ''}
                aria-pressed={selectedPillar === pillar.code}
                style={{ '--pillar-color': PILLAR_COLORS[pillar.code] ?? '#8293a8' } as CSSProperties}
                onClick={() => setSelectedPillar(pillar.code)}
              >
                <i aria-hidden="true" />
                {pillar.name} <span>{count}</span>
              </button>
            )
          })}
          <span className="indicator-pillar-hint">
            <FileSearch size={14} />
            Chọn một tiêu chí để xem bằng chứng
          </span>
        </div>
      </section>

      <div className="indicator-main-grid">
        <section className="indicator-panel indicator-criteria-panel">
          <div className="indicator-panel-heading">
            <div>
              <h2>① Mỗi tiêu chí đạt mức nào?</h2>
              <p>
                Điểm DBI theo thang 0–4; ô thiếu được giữ là thiếu, không quy đổi
                thành 0.
              </p>
            </div>
            <button
              type="button"
              className="indicator-sort-button"
              onClick={() => setSortBySpread((current) => !current)}
              aria-label={
                sortBySpread ? 'Sắp xếp theo mã tiêu chí' : 'Sắp xếp theo độ lệch'
              }
            >
              {sortBySpread ? (
                <ArrowUpWideNarrow size={15} />
              ) : (
                <ArrowDownWideNarrow size={15} />
              )}
              Sắp xếp: {sortBySpread ? 'Độ lệch' : 'Mã chuẩn'}
            </button>
          </div>

          <div className="indicator-table-scroll">
            <table className="indicator-table indicator-dbi-table">
              <thead>
                <tr>
                  <th>Mã &amp; tên tiêu chí</th>
                  {orderedBanks.map((bank) => (
                    <th key={bank.id} style={{ color: BANK_COLORS[bank.id] }}>
                      {bank.id === 'agribank' ? 'AGR' : bank.id.toUpperCase()}
                    </th>
                  ))}
                  <th>Trung bình</th>
                  <th>Độ lệch (SD)</th>
                </tr>
              </thead>
              <tbody>
                {pillars
                  .filter(
                    (pillar) =>
                      selectedPillar === 'all' || selectedPillar === pillar.code,
                  )
                  .map((pillar) => {
                    const rows = visibleCriteria.filter(
                      (row) => row.pillar === pillar.code,
                    )
                    if (rows.length === 0) return null
                    return (
                      <FragmentGroup
                        key={pillar.code}
                        pillar={pillar}
                        rows={rows}
                        banks={orderedBanks}
                        onSelect={setSelectedCriterionCode}
                      />
                    )
                  })}
              </tbody>
            </table>
          </div>
          <p className="indicator-table-note">
            Trung bình và độ lệch chuẩn chỉ tính trên điểm backend có cung cấp.
          </p>
        </section>

        <aside className="indicator-insights">
          <section className="indicator-panel">
            <div className="indicator-panel-heading">
              <div>
                <h2>② Điểm DBI chung</h2>
                <p>Điểm trung bình tiêu chí, chuẩn hóa trên thang 0–100</p>
              </div>
              <span className="indicator-panel-icon">▥</span>
            </div>
            <div className="indicator-bank-bars">
              {overallScores.map((bank) => (
                <div className="indicator-bank-bar" key={bank.id}>
                  <div>
                    <span>
                      <i style={{ backgroundColor: BANK_COLORS[bank.id] }} />
                      {bank.name} ({bank.id === 'agribank' ? 'AGR' : bank.id.toUpperCase()})
                    </span>
                    <strong style={{ color: BANK_COLORS[bank.id] }}>
                      {formatNumber(bank.score)}
                    </strong>
                  </div>
                  <span className="indicator-bank-bar__track">
                    <i
                      style={{
                        width: `${Math.max(0, Math.min(100, bank.score ?? 0))}%`,
                        backgroundColor: BANK_COLORS[bank.id],
                      }}
                    />
                  </span>
                </div>
              ))}
            </div>
            <p className="indicator-footnote">
              Điểm DBI = trung bình điểm tiêu chí × 25. Ô thiếu không được tính.
            </p>
          </section>

          <SpreadPanel
            title="③ Khác nhau nhiều nhất"
            subtitle="5 tiêu chí có độ lệch chuẩn lớn nhất"
            rows={mostDifferent}
            banks={orderedBanks}
          />

          <SpreadPanel
            title="④ Đồng đều nhất"
            subtitle="5 tiêu chí có độ lệch chuẩn nhỏ nhất"
            rows={mostConsistent}
            banks={orderedBanks}
          />
        </aside>
      </div>

      <section className="indicator-panel indicator-dti-panel">
        <div className="indicator-panel-heading indicator-dti-heading">
          <div>
            <h2>⑤ {indicatorRows.length} chỉ số định lượng (DTI)</h2>
            <p>
              Giá trị, ngưỡng và điểm chuẩn hóa z lấy từ backend; không tự điền
              dữ liệu còn thiếu.
            </p>
          </div>
          <div className="indicator-dti-filters" role="group" aria-label="Lọc trạng thái DTI">
            {([
              ['all', `Tất cả (${dtiRowsWithCompleteness.length})`],
              [
                'pass',
                `Đủ dữ liệu (${dtiRowsWithCompleteness.filter((row) => !row.excluded).length})`,
              ],
              [
                'excluded',
                `Thiếu nhiều (${dtiRowsWithCompleteness.filter((row) => row.excluded).length})`,
              ],
            ] as const).map(([filter, label]) => (
              <button
                type="button"
                key={filter}
                className={dtiFilter === filter ? 'is-active' : ''}
                aria-pressed={dtiFilter === filter}
                onClick={() => setDtiFilter(filter)}
              >
                {label}
              </button>
            ))}
          </div>
        </div>
        <div className="indicator-table-scroll">
          <table className="indicator-table indicator-dti-table">
            <thead>
              <tr>
                <th>Mã chỉ số &amp; tên</th>
                <th>Đơn vị</th>
                <th>Ngưỡng [L, U]</th>
                <th>Bước 0</th>
                {orderedBanks.map((bank) => (
                  <th key={bank.id} style={{ color: BANK_COLORS[bank.id] }}>
                    {bank.id === 'agribank' ? 'AGR' : bank.id.toUpperCase()}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {visibleIndicators.map((indicator) => (
                <tr key={indicator.code}>
                  <td>
                    <strong className="indicator-code">{indicator.code}</strong>
                    {indicator.name}
                  </td>
                  <td className="indicator-unit">{indicator.unit || '—'}</td>
                  <td className="indicator-range">
                    {indicator.lower == null || indicator.upper == null
                      ? '—'
                      : `[${formatNumber(indicator.lower, 2)}, ${formatNumber(indicator.upper, 2)}]`}
                  </td>
                  <td>
                    <span
                      className={`indicator-step-badge${indicator.excluded ? ' is-excluded' : ''}`}
                      title={`${indicator.available}/${orderedBanks.length} ngân hàng có dữ liệu`}
                    >
                      {indicator.excluded ? 'Thiếu ≥2 NH' : 'Đạt'}
                    </span>
                  </td>
                  {orderedBanks.map((bank) => {
                    const value = indicator.values[bank.id]
                    const hasValue = value?.hasData && value.x != null
                    return (
                      <td key={bank.id}>
                        {hasValue ? (
                          <div
                            className="indicator-dti-value"
                            style={{ '--bank-color': BANK_COLORS[bank.id] } as CSSProperties}
                            title={value.status || value.note || undefined}
                          >
                            <div>
                              <strong>
                                {formatNumber(value.x, 2)}
                                {indicator.unit ? ` ${indicator.unit}` : ''}
                              </strong>
                              <span>z={formatNumber(value.z, 1)}</span>
                            </div>
                            <span className="indicator-dti-value__track">
                              <i
                                style={{
                                  width: `${Math.max(0, Math.min(100, value.z ?? 0))}%`,
                                }}
                              />
                            </span>
                          </div>
                        ) : (
                          <span className="indicator-missing">Thiếu</span>
                        )}
                      </td>
                    )
                  })}
                </tr>
              ))}
              {visibleIndicators.length === 0 && (
                <tr>
                  <td colSpan={4 + orderedBanks.length} className="indicator-empty-row">
                    Không có chỉ số phù hợp với bộ lọc.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
        <p className="indicator-table-note">
          “Thiếu ≥2 NH” nghĩa là backend chưa có dữ liệu cho ít nhất 2 ngân
          hàng; trạng thái này chỉ phản ánh độ đầy đủ dữ liệu.
        </p>
      </section>

      {selectedCriterion && (
        <div
          className="indicator-modal-backdrop"
          role="presentation"
          onMouseDown={(event) => {
            if (event.target === event.currentTarget) setSelectedCriterionCode(null)
          }}
        >
          <section
            className="indicator-evidence-modal"
            role="dialog"
            aria-modal="true"
            aria-labelledby="indicator-evidence-title"
          >
            <div className="indicator-modal-heading">
              <div>
                <span>{selectedCriterion.pillarName}</span>
                <h2 id="indicator-evidence-title">
                  {selectedCriterion.code} · {selectedCriterion.name}
                </h2>
              </div>
              <button
                type="button"
                aria-label="Đóng chi tiết tiêu chí"
                onClick={() => setSelectedCriterionCode(null)}
              >
                <X size={18} />
              </button>
            </div>
            <div className="indicator-modal-banks">
              {orderedBanks.map((bank) => {
                const detail = detailByBank.get(bank.id)
                const criterion = detail?.criteria.find(
                  (item) => item.criterion === selectedCriterion.code,
                )
                return (
                  <article key={bank.id}>
                    <h3>
                      <i style={{ backgroundColor: BANK_COLORS[bank.id] }} />
                      {bank.name}
                      <strong style={{ color: BANK_COLORS[bank.id] }}>
                        {criterion?.score == null ? 'Chưa có điểm' : `${criterion.score}/4`}
                      </strong>
                    </h3>
                    <p className="indicator-modal-status">
                      {criterion?.status_label ?? 'Backend chưa trả trạng thái'}
                    </p>
                    {criterion?.evidence?.quote && (
                      <blockquote>{criterion.evidence.quote}</blockquote>
                    )}
                    {criterion?.note && (
                      <p className="indicator-modal-note">{criterion.note}</p>
                    )}
                    {criterion?.evidence?.url ? (
                      <a
                        href={criterion.evidence.url}
                        target="_blank"
                        rel="noreferrer"
                      >
                        <FileSearch size={14} />
                        {criterion.evidence.file ?? 'Mở nguồn'}
                        {criterion.evidence.page != null &&
                          ` · trang ${criterion.evidence.page}`}
                        <ExternalLink size={13} />
                      </a>
                    ) : (
                      <span className="indicator-modal-no-evidence">
                        Backend chưa cung cấp đường dẫn bằng chứng
                      </span>
                    )}
                  </article>
                )
              })}
            </div>
          </section>
        </div>
      )}
    </div>
  )
}

function FragmentGroup({
  pillar,
  rows,
  banks,
  onSelect,
}: {
  pillar: DashboardMeta['pillars'][number]
  rows: CriterionRow[]
  banks: DashboardMeta['banks']
  onSelect: (criterion: string) => void
}) {
  return (
    <>
      <tr
        className="indicator-pillar-row"
        style={{ '--pillar-color': PILLAR_COLORS[pillar.code] ?? '#8293a8' } as CSSProperties}
      >
        <td colSpan={banks.length + 3}>
          Trụ cột: {pillar.name} ({rows.length} tiêu chí)
        </td>
      </tr>
      {rows.map((row) => {
        const scores = banks
          .map((bank) => row.scores[bank.id])
          .filter((value): value is number => value != null)
        const average =
          scores.length > 0
            ? scores.reduce((sum, value) => sum + value, 0) / scores.length
            : null
        const spread = standardDeviation(scores)
        return (
          <tr
            className="indicator-criterion-row"
            key={row.code}
          >
            <td>
              <button
                type="button"
                className="indicator-criterion-trigger"
                onClick={() => onSelect(row.code)}
              >
                <strong className="indicator-code">{row.code}</strong>
                {row.name}
              </button>
            </td>
            {banks.map((bank) => {
              const score = row.scores[bank.id]
              return (
                <td key={bank.id}>
                  <span
                    className={`indicator-score-chip ${getLevelClass(score)}`}
                    aria-label={`${bank.name}: ${score == null ? 'Chưa có điểm' : `mức ${score}`}`}
                  >
                    {score ?? '—'}
                  </span>
                </td>
              )
            })}
            <td className="indicator-number">{formatNumber(average)}</td>
            <td className="indicator-number indicator-number--muted">
              {formatNumber(spread, 2)}
            </td>
          </tr>
        )
      })}
    </>
  )
}

function SpreadPanel({
  title,
  subtitle,
  rows,
  banks,
}: {
  title: string
  subtitle: string
  rows: Array<CriterionRow & { spread: number }>
  banks: DashboardMeta['banks']
}) {
  return (
    <section className="indicator-panel indicator-spread-panel">
      <div className="indicator-panel-heading">
        <div>
          <h2>{title}</h2>
          <p>{subtitle}</p>
        </div>
      </div>
      <div className="indicator-spread-list">
        {rows.map((row) => (
          <div key={row.code}>
            <div className="indicator-spread-label">
              <span>
                {row.code} · {row.name}
              </span>
              <strong>SD: {formatNumber(row.spread, 2)}</strong>
            </div>
            <div className="indicator-spread-track" aria-label={`Điểm ${row.code} từ 0 đến 4`}>
              <span className="indicator-spread-axis" aria-hidden="true">
                {[0, 1, 2, 3, 4].map((level) => (
                  <i key={level}>{level}</i>
                ))}
              </span>
              {banks.map((bank) => {
                const score = row.scores[bank.id]
                if (score == null) return null
                return (
                  <i
                    className="indicator-spread-dot"
                    key={bank.id}
                    style={{
                      '--bank-color': BANK_COLORS[bank.id],
                      left: `${Math.max(0, Math.min(100, (score / 4) * 100))}%`,
                    } as CSSProperties}
                    title={`${bank.name}: ${score}`}
                  />
                )
              })}
            </div>
          </div>
        ))}
        {rows.length === 0 && (
          <p className="indicator-empty-row">Chưa đủ dữ liệu để so sánh độ lệch.</p>
        )}
      </div>
      <p className="indicator-footnote">
        <Check size={13} /> Mỗi chấm là một ngân hàng · trục điểm từ 0 đến 4
      </p>
    </section>
  )
}

export default Tab3Executive
