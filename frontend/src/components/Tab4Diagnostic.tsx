import { useEffect, useMemo, useState, type CSSProperties } from 'react'
import {
  AlertCircle,
  CheckCircle2,
  Info,
  ShieldCheck,
} from 'lucide-react'
import {
  CartesianGrid,
  LabelList,
  Legend,
  Line,
  LineChart,
  ReferenceLine,
  ResponsiveContainer,
  Scatter,
  ScatterChart,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import {
  getFinancialPerformance,
  getLayerCCorrelation,
  getSensitivity,
  getSensitivityFull,
  getSensitivityScenarios,
  type CorrelationResponse,
  type FinancialPerformanceResponse,
  type SensitivityFullResponse,
  type SensitivityResponse,
  type SensitivityScenariosResponse,
} from '../api/dashboard'

const BANK_ORDER = ['vcb', 'mb', 'tcb', 'bidv', 'agribank']
const BANK_COLORS: Record<string, string> = {
  vcb: '#007a4b',
  mb: '#0648a8',
  tcb: '#e7163d',
  bidv: '#008b8b',
  agribank: '#a31c28',
}

const FINANCIAL_METRICS = [
  { key: 'roe', title: 'Điểm DBI và ROE', label: 'ROE (%)', expected: 'positive' },
  { key: 'roa', title: 'Điểm DBI và ROA', label: 'ROA (%)', expected: 'positive' },
  { key: 'cir', title: 'Điểm DBI và CIR', label: 'CIR (%)', expected: 'negative' },
  { key: 'casa', title: 'Điểm DBI và CASA', label: 'CASA (%)', expected: 'positive' },
  {
    key: 'non_interest_share',
    title: 'Điểm DBI và thu nhập ngoài lãi',
    label: 'Thu nhập ngoài lãi (%)',
    expected: 'neutral',
  },
] as const

function formatNumber(value: number | null | undefined, digits = 2) {
  return value == null
    ? '—'
    : new Intl.NumberFormat('vi-VN', {
        maximumFractionDigits: digits,
      }).format(value)
}

function formatPercent(value: number | null | undefined, digits = 0) {
  return value == null ? '—' : `${formatNumber(value * 100, digits)}%`
}

function getBankOrder(bank: string) {
  const index = BANK_ORDER.indexOf(bank)
  return index < 0 ? BANK_ORDER.length : index
}

function getErrorMessage(error: unknown) {
  return error instanceof Error
    ? error.message
    : 'Không thể tải dữ liệu phân tích từ backend.'
}

function Tab4Diagnostic({ year }: { year: number }) {
  const [weightData, setWeightData] = useState<SensitivityResponse | null>(null)
  const [fullData, setFullData] = useState<SensitivityFullResponse | null>(null)
  const [scenarioData, setScenarioData] =
    useState<SensitivityScenariosResponse | null>(null)
  const [correlationData, setCorrelationData] =
    useState<CorrelationResponse | null>(null)
  const [financialData, setFinancialData] =
    useState<FinancialPerformanceResponse | null>(null)
  const [resourceErrors, setResourceErrors] = useState<Record<string, string>>({})
  const [loading, setLoading] = useState<Record<string, boolean>>({})
  const [monteCarloMethod, setMonteCarloMethod] = useState('')

  useEffect(() => {
    const controller = new AbortController()
    const { signal } = controller

    setLoading({
      weights: true,
      full: true,
      scenarios: true,
      correlation: true,
      financial: true,
    })
    setResourceErrors({})
    setWeightData(null)
    setFullData(null)
    setScenarioData(null)
    setCorrelationData(null)
    setFinancialData(null)

    const loadResource = async <T,>(
      key: string,
      request: Promise<T>,
      onSuccess: (value: T) => void,
    ) => {
      try {
        const value = await request
        if (!signal.aborted) onSuccess(value)
      } catch (requestError) {
        if (!signal.aborted) {
          setResourceErrors((current) => ({
            ...current,
            [key]: getErrorMessage(requestError),
          }))
        }
      } finally {
        if (!signal.aborted) {
          setLoading((current) => ({ ...current, [key]: false }))
        }
      }
    }

    void loadResource('weights', getSensitivity(year, signal), setWeightData)
    void loadResource(
      'correlation',
      getLayerCCorrelation(signal),
      setCorrelationData,
    )
    void loadResource(
      'financial',
      getFinancialPerformance(year, signal),
      setFinancialData,
    )

    void loadResource('full', getSensitivityFull(signal), (value) => {
      setFullData(value)
      void loadResource(
        'scenarios',
        getSensitivityScenarios(value.year, signal),
        setScenarioData,
      )
    })

    return () => controller.abort()
  }, [year])

  const orderedWeightRows = useMemo(
    () =>
      [...(weightData?.rows ?? [])].sort(
        (a, b) => getBankOrder(a.bank) - getBankOrder(b.bank),
      ),
    [weightData],
  )
  const orderedFullBanks = useMemo(
    () =>
      [...(fullData?.banks ?? [])].sort(
        (a, b) => getBankOrder(a.bank) - getBankOrder(b.bank),
      ),
    [fullData],
  )
  const rankedFullBanks = useMemo(
    () =>
      [...(fullData?.banks ?? [])].sort((a, b) => {
        if (a.base_rank == null) return b.base_rank == null ? 0 : 1
        if (b.base_rank == null) return -1
        return a.base_rank - b.base_rank
      }),
    [fullData],
  )
  const scenarioLineData = useMemo(
    () =>
      (weightData?.scenarios ?? []).map((scenario) => {
        const row: Record<string, number | string | null> = { scenario }
        for (const bank of orderedWeightRows) {
          row[bank.bank] = bank.by_scenario[scenario]?.rank ?? null
        }
        return row
      }),
    [orderedWeightRows, weightData],
  )
  const monteCarloMethods = useMemo(
    () => orderedFullBanks[0]?.monte_carlo.map((item) => item.method) ?? [],
    [orderedFullBanks],
  )
  const selectedMonteCarloMethod =
    monteCarloMethods.includes(monteCarloMethod)
      ? monteCarloMethod
      : monteCarloMethods[0] ?? ''
  const rankedScenarioRows = useMemo(() => {
    const groups = new Map<
      string,
      {
        family: string
        scenario: string
        ranks: Record<string, number | null>
        baseRanks: Record<string, number | null>
      }
    >()
    for (const item of scenarioData?.items ?? []) {
      const key = `${item.family}\u0000${item.scenario}`
      const row = groups.get(key) ?? {
        family: item.family,
        scenario: item.scenario,
        ranks: {},
        baseRanks: {},
      }
      row.ranks[item.bank] = item.rank
      row.baseRanks[item.bank] = item.base_rank
      groups.set(key, row)
    }
    return [...groups.values()].sort(
      (a, b) =>
        a.family.localeCompare(b.family, undefined, { numeric: true }) ||
        a.scenario.localeCompare(b.scenario, undefined, { numeric: true }),
    )
  }, [scenarioData])

  const agreementRange = useMemo(() => {
    const values = (fullData?.rank_agreement ?? [])
      .map((item) => item.kendall_tau)
      .filter((value): value is number => value != null)
    return values.length
      ? { min: Math.min(...values), max: Math.max(...values), count: values.length }
      : null
  }, [fullData])

  const orderedFinancialItems = useMemo(
    () =>
      [...(financialData?.items ?? [])].sort(
        (a, b) => getBankOrder(a.bank) - getBankOrder(b.bank),
      ),
    [financialData],
  )

  const hasNoData =
    !loading.weights &&
    !loading.full &&
    !loading.correlation &&
    !loading.financial &&
    !weightData &&
    !fullData &&
    !correlationData &&
    !financialData

  if (hasNoData) {
    return (
      <div className="error-state diagnostic-state" role="alert">
        <AlertCircle size={22} />
        <strong>Không tải được dữ liệu kiểm định</strong>
        <p>
          {Object.values(resourceErrors).join(' ')}
        </p>
      </div>
    )
  }

  return (
    <div className="diagnostic-page">
      {Object.entries(resourceErrors).map(([key, message]) => (
        <div className="warning-note" role="alert" key={key}>
          <AlertCircle size={14} />
          <span>
            {key === 'full' || key === 'scenarios'
              ? 'Độ nhạy đầy đủ'
              : key === 'weights'
                ? 'Kịch bản trọng số'
                : key === 'correlation'
                  ? 'Tương quan'
                  : 'Số liệu tài chính'}
            : {message}
          </span>
        </div>
      ))}

      <section className="diagnostic-intro">
        <h2>
          {fullData
            ? `Thứ hạng ổn định ra sao trong năm ${fullData.year}?`
            : `Kiểm tra độ vững và kiểm định năm ${year}`}
        </h2>
        <p>
          Đánh giá mức ổn định của thứ hạng qua các kịch bản trọng số, mô phỏng
          và đối chiếu tương quan với chỉ tiêu tài chính backend.
        </p>
      </section>

      <section className="diagnostic-section">
        <div className="diagnostic-section-heading">
          <div>
            <h2>Thứ hạng có ổn định không?</h2>
            <p>
              {fullData
                ? `Phân tích độ nhạy đầy đủ · ${fullData.year} · ${fullData.n_discrete_scenarios} kịch bản rời rạc`
                : 'Đang tải kết quả mô phỏng độ nhạy đầy đủ…'}
            </p>
          </div>
          {fullData && (
            <span className="diagnostic-tag">
              Ngưỡng vững {formatPercent(fullData.robust_threshold)}
            </span>
          )}
        </div>

        {fullData ? (
          <div className="diagnostic-rank-cards">
            {rankedFullBanks.map((bank) => (
              <article
                className="diagnostic-rank-card"
                key={bank.bank}
                style={{ '--bank-color': BANK_COLORS[bank.bank] ?? '#52637a' } as CSSProperties}
              >
                <div className="diagnostic-rank-card__bank">
                  <span>{bank.bank_name}</span>
                  <strong>{bank.bank === 'agribank' ? 'AGR' : bank.bank.toUpperCase()}</strong>
                </div>
                <b>Hạng {bank.base_rank ?? '—'}</b>
                <span className="diagnostic-card-detail">
                  {formatPercent(bank.stable_share)} kịch bản giữ hạng
                </span>
                <span
                  className={`diagnostic-verdict${bank.is_robust ? ' is-robust' : ' is-group'}`}
                >
                  {bank.is_robust ? <CheckCircle2 size={12} /> : <Info size={12} />}
                  {bank.verdict ?? 'Chưa có kết luận'}
                </span>
              </article>
            ))}
          </div>
        ) : (
          <ResourcePlaceholder
            loading={loading.full}
            message={resourceErrors.full}
            label="độ nhạy đầy đủ"
          />
        )}
      </section>

      <div className="diagnostic-two-column">
        <section className="diagnostic-panel">
          <div className="diagnostic-panel-heading">
            <div>
              <h3>Thứ hạng khi đổi trọng số DBI/DTI</h3>
              <p>
                {weightData
                  ? `So sánh các phương án trọng số trong năm ${weightData.year}.`
                  : `Đang tải kịch bản trọng số năm ${year}.`}
              </p>
            </div>
            <span className="diagnostic-tag">Kịch bản xác định</span>
          </div>
          {weightData ? (
            <>
              <div className="diagnostic-chart">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart
                    data={scenarioLineData}
                    margin={{ top: 12, right: 16, bottom: 2, left: 0 }}
                  >
                    <CartesianGrid strokeDasharray="3 4" vertical={false} />
                    <XAxis dataKey="scenario" tickLine={false} axisLine={false} />
                    <YAxis
                      type="number"
                      domain={[1, 5]}
                      reversed
                      ticks={[1, 2, 3, 4, 5]}
                      tickFormatter={(value) => `Hạng ${value}`}
                      tickLine={false}
                      axisLine={false}
                      width={64}
                    />
                    <Tooltip
                      formatter={(value, name) => [`Hạng ${value ?? '—'}`, String(name)]}
                    />
                    <Legend />
                    {orderedWeightRows.map((bank) => (
                      <Line
                        key={bank.bank}
                        type="linear"
                        dataKey={bank.bank}
                        name={bank.bank_name}
                        stroke={BANK_COLORS[bank.bank] ?? '#52637a'}
                        strokeWidth={2.5}
                        connectNulls={false}
                        isAnimationActive={false}
                      >
                        <LabelList
                          dataKey={bank.bank}
                          position="top"
                          formatter={(value) => value ?? ''}
                          style={{ fontSize: 9, fill: BANK_COLORS[bank.bank] }}
                        />
                      </Line>
                    ))}
                  </LineChart>
                </ResponsiveContainer>
              </div>
              <div className="diagnostic-weight-table-wrap">
                <table className="diagnostic-table diagnostic-weight-table">
                  <thead>
                    <tr>
                      <th>Trọng số DBI / DTI</th>
                      {orderedWeightRows.map((bank) => (
                        <th key={bank.bank} style={{ color: BANK_COLORS[bank.bank] }}>
                          {bank.bank === 'agribank' ? 'AGR' : bank.bank.toUpperCase()}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {(weightData.scenarios ?? []).map((scenario) => (
                      <tr key={scenario}>
                        <th>{scenario}</th>
                        {orderedWeightRows.map((bank) => {
                          const cell = bank.by_scenario[scenario]
                          const rankChanged =
                            cell?.rank != null &&
                            cell.rank !== bank.by_scenario[weightData.base_scenario]?.rank
                          return (
                            <td key={bank.bank}>
                              <span className={rankChanged ? 'is-changed' : ''}>
                                {cell?.rank ?? '—'}
                              </span>
                            </td>
                          )
                        })}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </>
          ) : (
            <ResourcePlaceholder
              loading={loading.weights}
              message={resourceErrors.weights}
              label="kịch bản trọng số"
            />
          )}
        </section>

        <section className="diagnostic-panel">
          <div className="diagnostic-panel-heading">
            <div>
              <h3>Xác suất mỗi thứ hạng</h3>
              <p>
                Phân bố thứ hạng Monte Carlo, lấy trực tiếp từ backend
                {fullData ? ` · ${fullData.year}` : ''}.
              </p>
            </div>
            {monteCarloMethods.length > 0 && (
              <select
                className="diagnostic-method-select"
                aria-label="Chọn phương pháp mô phỏng"
                value={selectedMonteCarloMethod}
                onChange={(event) => setMonteCarloMethod(event.target.value)}
              >
                {monteCarloMethods.map((method) => (
                  <option key={method} value={method}>
                    {method}
                  </option>
                ))}
              </select>
            )}
          </div>
          {fullData ? (
            <>
              <div className="diagnostic-probability-table-wrap">
                <table className="diagnostic-table diagnostic-probability-table">
                  <thead>
                    <tr>
                      <th>Ngân hàng</th>
                      {orderedFullBanks.map((_, index) => (
                        <th key={index}>Hạng {index + 1}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {orderedFullBanks.map((bank) => {
                      const simulation = bank.monte_carlo.find(
                        (item) => item.method === selectedMonteCarloMethod,
                      )
                      return (
                        <tr key={bank.bank}>
                          <th>
                            <i style={{ backgroundColor: BANK_COLORS[bank.bank] }} />
                            {bank.bank_name}
                          </th>
                          {orderedFullBanks.map((_, index) => {
                            const rank = index + 1
                            const probability =
                              simulation?.rank_distribution.find(
                                (item) => item.rank === rank,
                              )?.prob ?? null
                            return (
                              <td key={rank}>
                                <span
                                  style={{
                                    '--probability': `${Math.max(0, Math.min(100, (probability ?? 0) * 100))}%`,
                                    '--bank-color': BANK_COLORS[bank.bank] ?? '#52637a',
                                  } as CSSProperties}
                                  title={`${bank.bank_name}, hạng ${rank}: ${formatPercent(probability)}`}
                                >
                                  {formatPercent(probability)}
                                </span>
                              </td>
                            )
                          })}
                        </tr>
                      )
                    })}
                  </tbody>
                </table>
              </div>
              <p className="diagnostic-footnote">
                Mô phỏng Monte Carlo phản ánh xác suất trong mô hình, không phải xác suất dự báo thực tế.
              </p>
            </>
          ) : (
            <ResourcePlaceholder
              loading={loading.full}
              message={resourceErrors.full}
              label="phân bố Monte Carlo"
            />
          )}
        </section>

        <section className="diagnostic-panel">
          <div className="diagnostic-panel-heading">
            <div>
              <h3>Điểm dao động bao nhiêu?</h3>
              <p>Khoảng điểm thấp nhất–cao nhất qua mô phỏng đầy đủ</p>
            </div>
            <span className="diagnostic-tag">Min – Max</span>
          </div>
          {fullData ? (
            <div className="diagnostic-score-ranges">
              {orderedFullBanks.map((bank) => {
                const range =
                  bank.min_score == null || bank.max_score == null
                    ? 0
                    : Math.max(0, bank.max_score - bank.min_score)
                const marker =
                  range > 0 && bank.base_score != null && bank.min_score != null
                    ? ((bank.base_score - bank.min_score) / range) * 100
                    : 50
                return (
                  <div
                    className="diagnostic-score-range"
                    key={bank.bank}
                    style={{ '--bank-color': BANK_COLORS[bank.bank] ?? '#52637a' } as CSSProperties}
                  >
                    <div className="diagnostic-range-label">
                      <span>
                        <i />
                        {bank.bank_name}
                      </span>
                      <strong>
                        {formatNumber(bank.min_score, 1)}–{formatNumber(bank.max_score, 1)}
                        {bank.base_score != null && ` · Cơ sở ${formatNumber(bank.base_score, 1)}`}
                      </strong>
                    </div>
                    <div className="diagnostic-range-track">
                      <i
                        style={{
                          left: `${Math.max(2, Math.min(98, marker))}%`,
                        }}
                        title={`Điểm cơ sở ${formatNumber(bank.base_score, 2)}`}
                      />
                    </div>
                  </div>
                )
              })}
            </div>
          ) : (
            <ResourcePlaceholder
              loading={loading.full}
              message={resourceErrors.full}
              label="khoảng dao động điểm"
            />
          )}
        </section>

        <section className="diagnostic-panel diagnostic-agreement-panel">
          <div className="diagnostic-panel-heading">
            <div>
              <h3>Hệ số nhất quán Kendall τ</h3>
              <p>Độ tương đồng thứ hạng giữa các kịch bản độ nhạy</p>
            </div>
            <span className="diagnostic-tag">Thứ hạng</span>
          </div>
          {agreementRange ? (
            <div className="diagnostic-agreement-value">
              <strong>
                {formatNumber(agreementRange.min, 2)}–{formatNumber(agreementRange.max, 2)}
              </strong>
              <span>{agreementRange.count} đối chiếu kịch bản có dữ liệu</span>
            </div>
          ) : (
            <ResourcePlaceholder
              loading={loading.full}
              message={resourceErrors.full}
              label="độ nhất quán"
            />
          )}
          {fullData && fullData.pairs.some((pair) => pair.borderline) && (
            <p className="diagnostic-footnote">
              Một số cặp ngân hàng sát ngưỡng phân biệt trong ít nhất một kịch bản.
            </p>
          )}
        </section>
      </div>

      <section className="diagnostic-panel diagnostic-scenarios-panel">
        <div className="diagnostic-panel-heading">
          <div>
            <h3>Các kịch bản kiểm định</h3>
            <p>
              Thứ hạng theo từng kịch bản đầy đủ; ô được tô màu khi thay đổi so với hạng cơ sở.
            </p>
          </div>
          {scenarioData && (
            <span className="diagnostic-tag">
              {scenarioData.count} kết quả ngân hàng–kịch bản
            </span>
          )}
        </div>
        {scenarioData ? (
          <div className="diagnostic-scenario-table-wrap">
            <table className="diagnostic-table diagnostic-scenario-table">
              <thead>
                <tr>
                  <th>Nhóm kịch bản</th>
                  <th>Kịch bản</th>
                  {orderedFullBanks.map((bank) => (
                    <th key={bank.bank} style={{ color: BANK_COLORS[bank.bank] }}>
                      {bank.bank === 'agribank' ? 'AGR' : bank.bank.toUpperCase()}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {rankedScenarioRows.map((row) => (
                  <tr key={`${row.family}-${row.scenario}`}>
                    <td>{row.family}</td>
                    <td>{row.scenario}</td>
                    {orderedFullBanks.map((bank) => {
                      const rank = row.ranks[bank.bank]
                      const changed =
                        rank != null &&
                        row.baseRanks[bank.bank] != null &&
                        rank !== row.baseRanks[bank.bank]
                      return (
                        <td key={bank.bank}>
                          <span className={changed ? 'is-changed' : ''}>
                            {rank == null ? '—' : `Hạng ${rank}`}
                          </span>
                        </td>
                      )
                    })}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <ResourcePlaceholder
            loading={loading.scenarios}
            message={resourceErrors.scenarios}
            label="bảng kịch bản"
          />
        )}
      </section>

      <section className="diagnostic-correlation-section">
        <div className="diagnostic-correlation-heading">
          <div className="diagnostic-correlation-icon">
            <ShieldCheck size={19} />
          </div>
          <div>
            <h2>Phân tích tương quan chỉ số thực chứng</h2>
            <p>
              Đối chiếu điểm DBI với chỉ tiêu tài chính backend trong năm {year}; mỗi điểm là một ngân hàng.
            </p>
          </div>
          <span className="diagnostic-tag">Spearman ρ · n nhỏ</span>
        </div>

        {correlationData && financialData ? (
          <div className="diagnostic-correlation-grid">
            {FINANCIAL_METRICS.map((metric) => {
              const corr = correlationData.metrics.find(
                (item) => item.metric === metric.key,
              )
              const yearCorrelation = corr?.by_year.find(
                (item) => item.year === year,
              )
              const points = orderedFinancialItems
                .map((item) => {
                  const yValue = item[metric.key]
                  if (item.dbi_mean == null || yValue == null) return null
                  return {
                    x: item.dbi_mean,
                    y: yValue,
                    bank: item.bank,
                    bankName: item.bank_name,
                  }
                })
                .filter((point): point is NonNullable<typeof point> => point != null)

              return (
                <article className="diagnostic-correlation-card" key={metric.key}>
                  <div className="diagnostic-correlation-card-heading">
                    <h3>{metric.title}</h3>
                    <span>Backend</span>
                  </div>
                  <div className="diagnostic-scatter-chart">
                    {points.length ? (
                      <ResponsiveContainer width="100%" height="100%">
                        <ScatterChart margin={{ top: 12, right: 13, bottom: 2, left: 0 }}>
                          <CartesianGrid strokeDasharray="3 4" />
                          <XAxis
                            type="number"
                            dataKey="x"
                            name="Điểm DBI"
                            domain={['dataMin - 5', 'dataMax + 5']}
                            tickLine={false}
                            axisLine={false}
                            tick={{ fontSize: 9 }}
                          />
                          <YAxis
                            type="number"
                            dataKey="y"
                            name={metric.label}
                            domain={['auto', 'auto']}
                            tickLine={false}
                            axisLine={false}
                            width={35}
                            tick={{ fontSize: 9 }}
                          />
                          <Tooltip
                            cursor={{ strokeDasharray: '3 3' }}
                            formatter={(value, name) => [
                              `${formatNumber(Number(value), 2)}${name === 'Điểm DBI' ? '' : '%'}`,
                              String(name),
                            ]}
                            labelFormatter={(_, payload) =>
                              payload?.[0]?.payload?.bankName ?? ''
                            }
                          />
                          <ReferenceLine
                            x={50}
                            stroke="var(--border)"
                            strokeDasharray="3 3"
                          />
                          {orderedFinancialItems.map((bank) => {
                            const data = points.filter((point) => point.bank === bank.bank)
                            if (!data.length) return null
                            return (
                              <Scatter
                                key={bank.bank}
                                name={bank.bank_name}
                                data={data}
                                fill={BANK_COLORS[bank.bank] ?? '#52637a'}
                              />
                            )
                          })}
                        </ScatterChart>
                      </ResponsiveContainer>
                    ) : (
                      <p className="diagnostic-no-points">
                        Backend chưa có đủ dữ liệu cho chỉ tiêu này trong năm {year}.
                      </p>
                    )}
                  </div>
                  <div className="diagnostic-correlation-footer">
                    <span>
                      {metric.expected === 'negative'
                        ? 'Kỳ vọng tương quan nghịch'
                        : metric.expected === 'positive'
                          ? 'Kỳ vọng tương quan thuận'
                          : 'Chưa quy định dấu kỳ vọng'}
                    </span>
                    <strong>
                      ρ = {formatNumber(yearCorrelation?.spearman, 2)}
                      {yearCorrelation?.n != null && ` · n=${yearCorrelation.n}`}
                    </strong>
                  </div>
                  <div className="diagnostic-bank-legend">
                    {orderedFinancialItems.map((bank) => (
                      <span key={bank.bank}>
                        <i style={{ backgroundColor: BANK_COLORS[bank.bank] }} />
                        {bank.bank === 'agribank' ? 'AGR' : bank.bank.toUpperCase()}
                      </span>
                    ))}
                  </div>
                </article>
              )
            })}
            <div className="diagnostic-caveat">
              <Info size={15} />
              <p>
                {correlationData.notes.join(' ')}
              </p>
            </div>
          </div>
        ) : (
          <ResourcePlaceholder
            loading={loading.correlation || loading.financial}
            message={resourceErrors.correlation ?? resourceErrors.financial}
            label="tương quan tài chính"
          />
        )}
      </section>

      {fullData?.note && (
        <p className="diagnostic-data-note">
          <Info size={14} />
          {fullData.note}
        </p>
      )}
    </div>
  )
}

function ResourcePlaceholder({
  loading,
  message,
  label,
}: {
  loading: boolean
  message?: string
  label: string
}) {
  return (
    <div className="diagnostic-resource-placeholder">
      {loading ? (
        <span>Đang tải {label} từ backend…</span>
      ) : (
        <span>{message ?? `Backend chưa cung cấp ${label}.`}</span>
      )}
    </div>
  )
}

export default Tab4Diagnostic
