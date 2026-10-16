import { useEffect, useMemo, useState } from 'react'
import {
  AlertCircle,
  ArrowDownRight,
  ArrowUpRight,
  BookOpen,
  Building2,
  Check,
  ChevronRight,
  Database,
  Download,
  LayoutDashboard,
  Landmark,
  RefreshCw,
  ShieldCheck,
  SlidersHorizontal,
  Bell,
} from 'lucide-react'
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  ComposedChart,
  Line,
  LineChart,
  PolarAngleAxis,
  PolarGrid,
  PolarRadiusAxis,
  Radar,
  RadarChart,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import {
  getBankYearDetail,
  getDashboardMeta,
  getRanking,
  getScoreTrend,
  type BankDetailResponse,
  type DashboardMeta,
  type RankingItem,
  type TrendResponse,
} from '../api/dashboard'
import Tab2BankProfile from './Tab2BankProfile'
import Tab3Executive from './Tab3Executive.tsx'
import Tab4Diagnostic from './Tab4Diagnostic.tsx'
import Tab5Methodology from './Tab5Methodology.tsx'
import YearPicker from './YearPicker'

const BANK_COLORS: Record<string, string> = {
  vcb: '#007a4b',
  mb: '#0648a8',
  tcb: '#e7163d',
  bidv: '#008b8b',
  agribank: '#a31c28',
}

const PILLAR_NAMES: Record<string, string> = {
  K: 'Khách hàng',
  S: 'Chiến lược',
  T: 'Công nghệ',
  O: 'Vận hành',
  C: 'Văn hóa',
  D: 'Dữ liệu',
}

const DISTRIBUTION_COLORS: Record<string, string> = {
  '0': '#d9e1eb',
  '1': '#aec8e6',
  '2': '#70afe5',
  '3': '#3486e7',
  '4': '#0d2b49',
}

const formatScore = (value: number | null | undefined) =>
  value == null
    ? '—'
    : new Intl.NumberFormat('vi-VN', {
        maximumFractionDigits: 2,
      }).format(value)

function getErrorMessage(error: unknown) {
  return error instanceof Error ? error.message : 'Đã xảy ra lỗi không xác định.'
}

function BankScoreSparkline({
  bank,
  trend,
}: {
  bank: string
  trend: TrendResponse
}) {
  const series = trend.series.find((item) => item.bank === bank)
  const data = series?.points.filter((point) => point.value != null) ?? []

  if (data.length < 2) return <div className="score-mini-line" />

  return (
    <div className="score-mini-line" aria-label={`Xu hướng điểm ${series?.bank_name}`}>
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data} margin={{ top: 3, right: 5, bottom: 0, left: 5 }}>
          <Line
            type="monotone"
            dataKey="value"
            stroke={BANK_COLORS[bank]}
            strokeWidth={2}
            dot={false}
            isAnimationActive={false}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}

function PanelHeading({
  title,
  subtitle,
  tag,
}: {
  title: string
  subtitle: string
  tag?: string
}) {
  return (
    <div className="panel-heading">
      <div>
        <h2>{title}</h2>
        <p>{subtitle}</p>
      </div>
      {tag && <span className="panel-tag">{tag}</span>}
    </div>
  )
}

function getCriterionDistribution(
  details: BankDetailResponse[],
  visibleBanks: Set<string>,
) {
  const scores = ['0', '1', '2', '3', '4']
  return details
    .filter((detail) => visibleBanks.has(detail.summary.bank))
    .map((detail) => ({
      bank: detail.summary.bank,
      name:
        detail.summary.bank === 'vcb'
          ? 'VCB'
          : detail.summary.bank === 'mb'
            ? 'MB'
            : detail.summary.bank === 'tcb'
              ? 'TCB'
              : detail.summary.bank === 'bidv'
                ? 'BIDV'
                : 'AGR',
      ...Object.fromEntries(
        scores.map((score) => [
          score,
          detail.highlights.criteria_score_distribution[score] ?? 0,
        ]),
      ),
    }))
}

function downloadCsv(items: RankingItem[], year: number) {
  const headers = [
    'Năm',
    'Ngân hàng',
    'Xếp hạng',
    'Điểm tổng hợp',
    'Mức trưởng thành',
    'Độ tin cậy DTI',
    ...Object.values(PILLAR_NAMES),
  ]
  const rows = items.map((item) => [
    item.year,
    item.bank_name,
    item.rank,
    item.score,
    item.maturity_level_name,
    `${item.dti_indicators_available}/${item.dti_indicators_total}`,
    ...Object.keys(PILLAR_NAMES).map((code) => item.pillars[code]?.p ?? ''),
  ])
  const csv = [headers, ...rows]
    .map((row) =>
      row
        .map((value) => `"${String(value).replaceAll('"', '""')}"`)
        .join(','),
    )
    .join('\r\n')
  const blob = new Blob(['\ufeff', csv], {
    type: 'text/csv;charset=utf-8',
  })
  const url = URL.createObjectURL(blob)
  const anchor = document.createElement('a')
  anchor.href = url
  anchor.download = `bank-dx-overview-${year}.csv`
  anchor.click()
  URL.revokeObjectURL(url)
}

export default function Tab1Overview() {
  const [theme, setTheme] = useState<'light' | 'dark'>(() =>
    window.localStorage.getItem('dashboard-theme') === 'dark' ? 'dark' : 'light',
  )
  const [meta, setMeta] = useState<DashboardMeta | null>(null)
  const [trend, setTrend] = useState<TrendResponse | null>(null)
  const [ranking, setRanking] = useState<RankingItem[]>([])
  const [details, setDetails] = useState<BankDetailResponse[]>([])
  const [selectedYear, setSelectedYear] = useState(2025)
  const [visibleBanks, setVisibleBanks] = useState<Set<string>>(
    () => new Set(Object.keys(BANK_COLORS)),
  )
  const [loadingMeta, setLoadingMeta] = useState(true)
  const [loadingYear, setLoadingYear] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false)
  const [activeTab, setActiveTab] = useState<
    'overview' | 'profile' | 'indicators' | 'diagnostics' | 'methodology'
  >('overview')

  useEffect(() => {
    window.localStorage.setItem('dashboard-theme', theme)
  }, [theme])

  useEffect(() => {
    const controller = new AbortController()

    async function loadBaseData() {
      try {
        const [dashboardMeta, scoreTrend] = await Promise.all([
          getDashboardMeta(controller.signal),
          getScoreTrend(controller.signal),
        ])

        setMeta(dashboardMeta)
        setTrend(scoreTrend)
        setSelectedYear((year) =>
          dashboardMeta.years.includes(year)
            ? year
            : dashboardMeta.latest_year,
        )
        setError(null)
      } catch (loadError) {
        if (!controller.signal.aborted) {
          setError(getErrorMessage(loadError))
        }
      } finally {
        if (!controller.signal.aborted) setLoadingMeta(false)
      }
    }

    void loadBaseData()
    return () => controller.abort()
  }, [])

  useEffect(() => {
    if (!meta) return

    const controller = new AbortController()
    async function loadYearData() {
      setLoadingYear(true)
      setError(null)
      setRanking([])
      setDetails([])

      try {
        const { items } = await getRanking(selectedYear, controller.signal)
        const bankDetails = await Promise.all(
          items.map((item) =>
            getBankYearDetail(item.bank, selectedYear, controller.signal),
          ),
        )

        setRanking(items)
        setDetails(bankDetails)
      } catch (loadError) {
        if (!controller.signal.aborted) {
          setError(getErrorMessage(loadError))
        }
      } finally {
        if (!controller.signal.aborted) setLoadingYear(false)
      }
    }

    void loadYearData()
    return () => controller.abort()
  }, [meta, selectedYear])

  const visibleItems = useMemo(
    () => ranking.filter((item) => visibleBanks.has(item.bank)),
    [ranking, visibleBanks],
  )
  const visibleDetails = useMemo(
    () => details.filter((item) => visibleBanks.has(item.summary.bank)),
    [details, visibleBanks],
  )
  const leader = visibleItems[0]

  const trendData = useMemo(() => {
    if (!trend) return []
    return trend.years.map((year) => {
      const row: Record<string, number | string | null> = { year }
      for (const bank of trend.series) {
        const point = bank.points.find((entry) => entry.year === year)
        row[bank.bank] = point?.value ?? null
      }
      return row
    })
  }, [trend])

  const pillarData = useMemo(
    () =>
      Object.entries(PILLAR_NAMES).map(([code, name]) => {
        const row: Record<string, string | number | null> = {
          pillar: name,
          code,
        }
        for (const item of visibleItems) {
          row[item.bank] = item.pillars[code]?.p ?? null
        }
        return row
      }),
    [visibleItems],
  )

  const distributionData = useMemo(
    () => getCriterionDistribution(visibleDetails, visibleBanks),
    [visibleDetails, visibleBanks],
  )

  const leadersByPillar = useMemo(() => {
    const result: Record<string, number | null> = {}
    for (const code of Object.keys(PILLAR_NAMES)) {
      const values = visibleItems
        .map((item) => item.pillars[code]?.p)
        .filter((value): value is number => value != null)
        result[code] = values.length ? Math.max(...values) : null
      }
      return result
  }, [visibleItems])
  const leaderPillarCount = leader
      ? Object.keys(PILLAR_NAMES).filter(
          (code) =>
            leader.pillars[code]?.p != null &&
            leader.pillars[code]?.p === leadersByPillar[code],
        ).length
      : 0

  const scoreGap =
    visibleItems.length > 1
      ? visibleItems[0].score - visibleItems[1].score
      : null

  function toggleBank(bank: string) {
    setVisibleBanks((current) => {
      const next = new Set(current)
      if (next.has(bank)) next.delete(bank)
      else next.add(bank)
      return next
    })
  }

  if (loadingMeta) {
    return (
      <div className="dashboard-shell" data-theme={theme}>
        <div className="loading-state">
          <RefreshCw size={20} />
          <strong>Đang tải dữ liệu tổng quan</strong>
          <p>Đang kết nối tới API backend DBI–DTI.</p>
        </div>
      </div>
    )
  }

  if (error && !meta) {
    return (
      <div className="dashboard-shell" data-theme={theme}>
        <div className="error-state">
          <AlertCircle size={22} />
          <strong>Không tải được dữ liệu từ backend</strong>
          <p>{error}</p>
          <p>
            Kiểm tra API tại <code>http://localhost:8000/api/v1</code> và cấu
            hình CORS; có thể đổi địa chỉ bằng <code>VITE_API_BASE_URL</code>.
          </p>
          <button
            type="button"
            className="retry-button"
            onClick={() => window.location.reload()}
          >
            <RefreshCw size={13} />
            Thử lại
          </button>
        </div>
      </div>
    )
  }

  if (!meta || !trend) return null

  return (
    <div
      className={`dashboard-shell${sidebarCollapsed ? ' sidebar-collapsed' : ''}`}
      data-theme={theme}
    >
      <aside className="sidebar">
        <div className="brand">
          <span className="brand-mark">
            <Landmark size={19} />
          </span>
          <div className="brand-copy">
            <p className="brand-title">Đối sánh chuyển đổi số ngân hàng</p>
            <div className="brand-subtitle">
              5 ngân hàng · DBI 80% + DTI 20%
              <br />
              2020–{meta.latest_year}
            </div>
          </div>
        </div>
        <button
          type="button"
          className="sidebar-toggle"
          aria-expanded={!sidebarCollapsed}
          aria-label={sidebarCollapsed ? 'Mở rộng thanh điều hướng' : 'Thu gọn thanh điều hướng'}
          title={sidebarCollapsed ? 'Mở rộng thanh điều hướng' : 'Thu gọn thanh điều hướng'}
          onClick={() => setSidebarCollapsed((collapsed) => !collapsed)}
        >
          <ChevronRight size={15} />
        </button>

        <nav className="nav-list" aria-label="Điều hướng dashboard">
          <button
            type="button"
            className={`nav-item${activeTab === 'overview' ? ' active' : ''}`}
            aria-current={activeTab === 'overview' ? 'page' : undefined}
            title="Tổng quan"
            onClick={() => setActiveTab('overview')}
          >
            <LayoutDashboard size={14} />
            <span className="nav-item-label">TỔNG QUAN</span>
          </button>
          <button
            type="button"
            className={`nav-item${activeTab === 'profile' ? ' active' : ''}`}
            aria-current={activeTab === 'profile' ? 'page' : undefined}
            title="Hồ sơ ngân hàng"
            onClick={() => setActiveTab('profile')}
          >
            <Building2 size={14} />
            <span className="nav-item-label">HỒ SƠ NGÂN HÀNG</span>
          </button>
          <button
            type="button"
            className={`nav-item${activeTab === 'indicators' ? ' active' : ''}`}
            aria-current={activeTab === 'indicators' ? 'page' : undefined}
            title="Chỉ tiêu"
            onClick={() => setActiveTab('indicators')}
          >
            <SlidersHorizontal size={14} />
            <span className="nav-item-label">CHỈ TIÊU</span>
          </button>
          <button
            type="button"
            className={`nav-item${activeTab === 'diagnostics' ? ' active' : ''}`}
            aria-current={activeTab === 'diagnostics' ? 'page' : undefined}
            title="Độ vững & Kiểm định"
            onClick={() => setActiveTab('diagnostics')}
          >
            <ShieldCheck size={14} />
            <span className="nav-item-label">ĐỘ VỮNG &amp; KIỂM ĐỊNH</span>
          </button>
          <button
            type="button"
            className={`nav-item${activeTab === 'methodology' ? ' active' : ''}`}
            aria-current={activeTab === 'methodology' ? 'page' : undefined}
            title="Phương pháp & Hạn chế"
            onClick={() => setActiveTab('methodology')}
          >
            <BookOpen size={14} />
            <span className="nav-item-label">PHƯƠNG PHÁP &amp; HẠN CHẾ</span>
          </button>
        </nav>

        <div className="bank-filter-heading">
          <span>Ngân hàng hiển thị</span>
          <span className="bank-count">
            {visibleBanks.size}/{meta.banks.length} bật
          </span>
        </div>
        <div className="bank-filter-list">
          {meta.banks.map((bank) => (
            <label
              className="bank-filter"
              key={bank.id}
              title={bank.name}
              style={{ '--bank-color': BANK_COLORS[bank.id] } as React.CSSProperties}
            >
              <span className="bank-dot" />
              <span>{bank.name}</span>
              <input
                type="checkbox"
                checked={visibleBanks.has(bank.id)}
                onChange={() => toggleBank(bank.id)}
                aria-label={`Hiển thị ${bank.name}`}
              />
            </label>
          ))}
        </div>

        <div className="sidebar-spacer" />
        <div className="source-note">
          <strong>
            <Database size={12} />
            Dữ liệu từ backend
          </strong>
          Điểm lấy từ API dự án. Ô thiếu được giữ là thiếu, không quy đổi thành
          0.
        </div>
      </aside>

      <main className="main-area">
        <header className="topbar">
          <h1>
            {activeTab === 'overview'
              ? 'Tổng quan'
              : activeTab === 'profile'
                ? 'Hồ sơ ngân hàng'
                : activeTab === 'indicators'
                  ? 'Chỉ tiêu'
                  : activeTab === 'diagnostics'
                    ? 'Độ vững & Kiểm định'
                    : 'Phương pháp & Hạn chế'}
          </h1>
          <div className="topbar-actions">
            <YearPicker
              years={meta.years}
              selectedYear={selectedYear}
              onSelectYear={setSelectedYear}
            />
            <button
              type="button"
              className={`theme-switch ${theme}`}
              title={theme === 'light' ? 'Chuyển sang giao diện tối' : 'Chuyển sang giao diện sáng'}
              aria-label={theme === 'light' ? 'Chuyển sang giao diện tối' : 'Chuyển sang giao diện sáng'}
              aria-pressed={theme === 'dark'}
              onClick={() =>
                setTheme((current) => (current === 'light' ? 'dark' : 'light'))
              }
            >
              <span className="theme-switch__sky" aria-hidden="true">
                <span className="theme-switch__stars">
                  <i />
                  <i />
                  <i />
                  <i />
                </span>
                <span className="theme-switch__celestial">
                  <i />
                  <i />
                  <i />
                </span>
                <span className="theme-switch__cloud" />
              </span>
            </button>
            <button
              type="button"
              className="icon-button"
              title="Thông báo"
              aria-label="Thông báo"
            >
              <Bell size={16} />
            </button>
          </div>
        </header>

        <div className="dashboard-content">
          {activeTab === 'profile' ? (
            <Tab2BankProfile
              banks={meta.banks}
              framework={meta.framework}
              pillars={meta.pillars}
              year={selectedYear}
              ranking={ranking}
              details={details}
              trend={trend}
              loading={loadingYear}
              error={error}
            />
          ) : activeTab === 'indicators' ? (
            <Tab3Executive
              banks={meta.banks}
              pillars={meta.pillars}
              details={details}
              year={selectedYear}
              loading={loadingYear}
              error={error}
            />
          ) : activeTab === 'diagnostics' ? (
            <Tab4Diagnostic year={selectedYear} />
          ) : activeTab === 'methodology' ? (
            <Tab5Methodology
              meta={meta}
              details={details}
              ranking={ranking}
              year={selectedYear}
              loading={loadingYear}
              error={error}
              onNavigate={setActiveTab}
            />
          ) : (
            <>
          {error && (
            <div className="warning-note" role="alert">
              <AlertCircle size={14} />
              <span>
                Không thể cập nhật năm {selectedYear}: {error}
              </span>
            </div>
          )}

          {loadingYear && ranking.length === 0 ? (
            <div className="loading-state">
              <RefreshCw size={20} />
              <strong>Đang tải bảng xếp hạng {selectedYear}</strong>
              <p>Dữ liệu điểm và phân bố tiêu chí được lấy trực tiếp từ API.</p>
            </div>
          ) : error && ranking.length === 0 ? (
            <div className="error-state" role="alert">
              <AlertCircle size={22} />
              <strong>Không tải được dữ liệu năm {selectedYear}</strong>
              <p>{error}</p>
              <button
                type="button"
                className="retry-button"
                onClick={() => window.location.reload()}
              >
                <RefreshCw size={13} />
                Thử lại
              </button>
            </div>
          ) : visibleItems.length === 0 ? (
            <div className="empty-selection">
              <strong>Chưa chọn ngân hàng để hiển thị</strong>
              <p>Bật ít nhất một ngân hàng trong bộ lọc bên trái.</p>
            </div>
          ) : (
            <>
              <section className="hero-banner">
                <div className="hero-content">
                  <span className="hero-badge">
                    <span className="hero-badge-dot" />
                    BÁO CÁO ĐỐI SÁNH NĂNG LỰC SỐ {selectedYear}
                  </span>
                  <h2>
                    {leader?.bank_name} dẫn đầu bảng xếp hạng năm {selectedYear}
                  </h2>
                  <p>
                    Điểm tổng hợp DBI–DTI trên thang 0–100, đối chiếu 5 ngân
                    hàng theo dữ liệu backend.
                  </p>
                  <div className="hero-stats">
                    <div className="hero-stat">
                      <strong>{formatScore(leader?.score)}</strong>
                      <span>điểm tổng hợp của ngân hàng dẫn đầu</span>
                    </div>
                    <div className="hero-stat">
                      <strong className="green">
                        {scoreGap == null ? '—' : `+${formatScore(scoreGap)}`}
                      </strong>
                      <span>điểm cách biệt với vị trí kế tiếp</span>
                    </div>
                    <div className="hero-stat">
                      <strong>
                        {leaderPillarCount}/{Object.keys(PILLAR_NAMES).length}
                      </strong>
                      <span>trụ cột dẫn đầu hoặc đồng dẫn đầu</span>
                    </div>
                    <div className="hero-stat">
                      <strong>
                        {leader?.dti_indicators_available}/
                        {leader?.dti_indicators_total}
                      </strong>
                      <span>chỉ số DTI có dữ liệu · {leader?.bank_name}</span>
                    </div>
                  </div>
                </div>
              </section>

              <section className="score-cards" aria-label="Xếp hạng ngân hàng">
                {visibleItems.map((item) => (
                  <article
                    className="score-card"
                    key={item.bank}
                    style={
                      {
                        '--bank-color': BANK_COLORS[item.bank],
                        '--card-order': item.rank - 1,
                      } as React.CSSProperties
                    }
                  >
                    <div className="score-card-top">
                      <span className="rank-label">HẠNG {item.rank}</span>
                      <span className="maturity-pill">
                        Mức {item.maturity_level_number} · {item.maturity_level_name}
                      </span>
                    </div>
                    <h3>{item.bank_name}</h3>
                    <div className="score-card-score-row">
                      <strong className="score-card-score">
                        {formatScore(item.score)}
                      </strong>
                      {item.score_change != null && (
                        <span
                          className={`change-pill${item.score_change < 0 ? ' down' : ''}`}
                        >
                          {item.score_change < 0 ? (
                            <ArrowDownRight size={10} />
                          ) : (
                            <ArrowUpRight size={10} />
                          )}
                          {item.score_change > 0 ? '+' : ''}
                          {formatScore(item.score_change)} điểm
                        </span>
                      )}
                    </div>
                    <BankScoreSparkline bank={item.bank} trend={trend} />
                    <div className="score-card-confidence">
                      <span>Độ phủ DTI</span>
                      <span className="confidence-value">
                        {item.dti_indicators_available}/
                        {item.dti_indicators_total}
                      </span>
                    </div>
                  </article>
                ))}
              </section>

              <div className="dashboard-grid">
                <div className="dashboard-column">
                  <section className="panel">
                    <PanelHeading
                      title="Xếp hạng tổng điểm DBI–DTI"
                      subtitle={`Thứ hạng và điểm chính thức theo backend · ${selectedYear}`}
                      tag="Thang 0–100"
                    />
                    <div className="chart-wrap">
                      <ResponsiveContainer width="100%" height="100%">
                        <BarChart
                          data={visibleItems.map((item) => ({
                            name: item.bank_name,
                            score: item.score,
                            bank: item.bank,
                            rank: item.rank,
                          }))}
                          layout="vertical"
                          margin={{ top: 4, right: 32, bottom: 4, left: 4 }}
                        >
                          <CartesianGrid horizontal={false} />
                          <XAxis
                            type="number"
                            domain={[0, 100]}
                            tickLine={false}
                            axisLine={false}
                          />
                          <YAxis
                            type="category"
                            dataKey="name"
                            width={100}
                            tickLine={false}
                            axisLine={false}
                          />
                          <Tooltip
                            formatter={(value) => [`${formatScore(Number(value))}`, 'Điểm']}
                            labelFormatter={(label) => String(label)}
                          />
                          <Bar dataKey="score" radius={[0, 5, 5, 0]} barSize={24}>
                            {visibleItems.map((item) => (
                              <Cell key={item.bank} fill={BANK_COLORS[item.bank]} />
                            ))}
                          </Bar>
                        </BarChart>
                      </ResponsiveContainer>
                    </div>
                    <div className="panel-footer">
                      <span>
                        <strong>DBI {meta.framework.dbi_weight * 100}%</strong>
                        {' + '}
                        <strong>DTI {meta.framework.dti_weight * 100}%</strong>
                      </span>
                      <button
                        type="button"
                        className="retry-button"
                        onClick={() => downloadCsv(visibleItems, selectedYear)}
                      >
                        <Download size={12} />
                        Tải CSV
                      </button>
                    </div>
                  </section>

                  <section className="panel">
                    <PanelHeading
                      title="Từng trụ cột: ai hơn ai?"
                      subtitle={`Điểm P_k theo công thức DBI–DTI · ${selectedYear}`}
                      tag="6 trụ cột"
                    />
                    <div className="comparison-table-wrap">
                      <table className="comparison-table">
                        <thead>
                          <tr>
                            <th scope="col">TRỤ CỘT</th>
                            {visibleItems.map((item) => (
                              <th scope="col" key={item.bank}>
                                {item.bank.toUpperCase()}
                              </th>
                            ))}
                            <th scope="col">CHÊNH LỆCH</th>
                          </tr>
                        </thead>
                        <tbody>
                          {Object.entries(PILLAR_NAMES).map(([code, name]) => {
                            const values = visibleItems
                              .map((item) => item.pillars[code]?.p)
                              .filter((value): value is number => value != null)
                            const difference =
                              values.length > 1
                                ? Math.max(...values) - Math.min(...values)
                                : null

                            return (
                              <tr key={code}>
                                <td>{name}</td>
                                {visibleItems.map((item) => {
                                  const value = item.pillars[code]?.p
                                  return (
                                    <td key={item.bank}>
                                      {value == null ? (
                                        <span title="Chưa có dữ liệu">—</span>
                                      ) : (
                                        <>
                                          <span
                                            className={`pillar-value${
                                              value === Math.max(...values)
                                                ? ' leader'
                                                : ''
                                            }`}
                                            style={
                                              {
                                                '--bank-color':
                                                  BANK_COLORS[item.bank],
                                              } as React.CSSProperties
                                            }
                                          >
                                            {formatScore(value)}
                                          </span>
                                          <span className="pillar-track">
                                            <span
                                              className="pillar-fill"
                                              style={{
                                                width: `${value}%`,
                                                backgroundColor:
                                                  BANK_COLORS[item.bank],
                                              }}
                                            />
                                          </span>
                                        </>
                                      )}
                                    </td>
                                  )
                                })}
                                <td>{formatScore(difference)}</td>
                              </tr>
                            )
                          })}
                        </tbody>
                      </table>
                    </div>
                    <div className="quality-callout">
                      <strong>Lưu ý về độ phủ dữ liệu:</strong> điểm năm có thể
                      chịu ảnh hưởng bởi số chỉ số DTI được công bố; xem độ phủ
                      bên cạnh mỗi ngân hàng và không diễn giải chênh lệch điểm
                      như tiến bộ thuần túy.
                    </div>
                    <div className="panel-footer">
                      <span>★ Đánh dấu ngân hàng có điểm cao nhất mỗi trụ cột</span>
                      <span>Chênh lệch lớn nhất giữa các ngân hàng</span>
                    </div>
                  </section>

                  <section className="panel">
                    <PanelHeading
                      title="Tiến bộ qua các năm"
                      subtitle="Xu hướng điểm tổng hợp DBI–DTI, dữ liệu 2020–2025"
                      tag={`${trend.years[0]}–${trend.years.at(-1)}`}
                    />
                    <div className="chart-wrap trend-chart">
                      <ResponsiveContainer width="100%" height="100%">
                        <LineChart
                          data={trendData}
                          margin={{ top: 12, right: 20, bottom: 3, left: -15 }}
                        >
                          <CartesianGrid vertical={false} />
                          <XAxis
                            dataKey="year"
                            tickLine={false}
                            axisLine={false}
                            tickFormatter={(value) => String(value)}
                          />
                          <YAxis
                            domain={[0, 100]}
                            tickLine={false}
                            axisLine={false}
                          />
                          <ReferenceLine y={50} stroke="#c8d4e2" />
                          <Tooltip
                            formatter={(value, name) => [
                              value == null ? 'Chưa có dữ liệu' : formatScore(Number(value)),
                              String(name),
                            ]}
                            labelFormatter={(label) => `Năm ${label}`}
                          />
                          {visibleItems.map((item) => (
                            <Line
                              key={item.bank}
                              type="monotone"
                              dataKey={item.bank}
                              name={item.bank_name}
                              stroke={BANK_COLORS[item.bank]}
                              strokeWidth={item.bank === leader?.bank ? 2.8 : 2}
                              dot={{ r: 2.5, strokeWidth: 0 }}
                              activeDot={{ r: 4 }}
                              connectNulls={false}
                              isAnimationActive={false}
                            />
                          ))}
                        </LineChart>
                      </ResponsiveContainer>
                    </div>
                    <div className="panel-footer">
                      <span>Điểm chính thức của từng năm theo API backend</span>
                      <span>Đường bị ngắt nếu dữ liệu thiếu</span>
                    </div>
                    {trend.warnings.length > 0 && (
                      <div className="warning-note">
                        <AlertCircle size={13} />
                        <span>{trend.warnings[0]}</span>
                      </div>
                    )}
                  </section>
                </div>

                <div className="dashboard-column right-column">
                  <section className="panel">
                    <PanelHeading
                      title="Năng lực trên 6 trụ cột"
                      subtitle="So sánh điểm P_k từ dữ liệu backend"
                      tag="DBI–DTI"
                    />
                    <div className="chart-wrap radar-chart">
                      <ResponsiveContainer width="100%" height="100%">
                        <RadarChart
                          data={pillarData}
                          outerRadius="72%"
                          margin={{ top: 7, right: 18, bottom: 8, left: 18 }}
                        >
                          <PolarGrid />
                          <PolarAngleAxis dataKey="pillar" />
                          <PolarRadiusAxis
                            angle={30}
                            domain={[0, 100]}
                            tick={false}
                            axisLine={false}
                          />
                          <Tooltip
                            formatter={(value, name) => [
                              value == null ? 'Chưa có dữ liệu' : formatScore(Number(value)),
                              String(name),
                            ]}
                          />
                          {visibleItems.map((item) => (
                            <Radar
                              key={item.bank}
                              name={item.bank_name}
                              dataKey={item.bank}
                              stroke={BANK_COLORS[item.bank]}
                              fill={BANK_COLORS[item.bank]}
                              fillOpacity={item.bank === leader?.bank ? 0.12 : 0.04}
                              strokeWidth={item.bank === leader?.bank ? 2 : 1.4}
                              connectNulls={false}
                              isAnimationActive={false}
                            />
                          ))}
                        </RadarChart>
                      </ResponsiveContainer>
                    </div>
                    <div className="legend-list">
                      {visibleItems.map((item) => (
                        <span className="legend-item" key={item.bank}>
                          <span
                            className="legend-dot"
                            style={{ backgroundColor: BANK_COLORS[item.bank] }}
                          />
                          {item.bank.toUpperCase()}
                        </span>
                      ))}
                    </div>
                  </section>

                  <section className="panel">
                    <PanelHeading
                      title="24 tiêu chí đạt mức nào?"
                      subtitle="Phân bố điểm rubric 0–4 theo tiêu chí DBI"
                    />
                    <div className="chart-wrap">
                      <ResponsiveContainer width="100%" height="100%">
                        <BarChart
                          data={distributionData}
                          layout="vertical"
                          margin={{ top: 5, right: 8, bottom: 0, left: 0 }}
                        >
                          <CartesianGrid horizontal={false} />
                          <XAxis
                            type="number"
                            domain={[0, 24]}
                            ticks={[0, 6, 12, 18, 24]}
                            tickLine={false}
                            axisLine={false}
                          />
                          <YAxis
                            type="category"
                            dataKey="name"
                            width={38}
                            tickLine={false}
                            axisLine={false}
                          />
                          <Tooltip
                            formatter={(value, name) => [
                              `${value} tiêu chí`,
                              `Mức ${name}`,
                            ]}
                            labelFormatter={(label) => String(label)}
                          />
                          {[0, 1, 2, 3, 4].map((level) => (
                            <Bar
                              key={level}
                              dataKey={String(level)}
                              name={`Mức ${level}`}
                              stackId="criteria"
                              fill={DISTRIBUTION_COLORS[String(level)]}
                              isAnimationActive={false}
                            />
                          ))}
                        </BarChart>
                      </ResponsiveContainer>
                    </div>
                    <div className="legend-list">
                      {[0, 1, 2, 3, 4].map((level) => (
                        <span className="legend-item" key={level}>
                          <span
                            className="legend-dot"
                            style={{
                              borderRadius: 2,
                              backgroundColor:
                                DISTRIBUTION_COLORS[String(level)],
                            }}
                          />
                          Mức {level}
                        </span>
                      ))}
                    </div>
                    <div className="panel-footer">
                      <span>Phân bố từ trường `highlights` của API</span>
                      <span>
                        {meta.framework.criteria} tiêu chí / ngân hàng
                      </span>
                    </div>
                  </section>

                  <section className="panel">
                    <PanelHeading
                      title="Độ phủ dữ liệu DTI"
                      subtitle="Số chỉ số DTI có dữ liệu trên tổng 11 chỉ số"
                      tag="Chất lượng dữ liệu"
                    />
                    <div className="chart-wrap" style={{ height: 185 }}>
                      <ResponsiveContainer width="100%" height="100%">
                        <ComposedChart
                          data={visibleItems.map((item) => ({
                            name:
                              item.bank === 'agribank'
                                ? 'AGR'
                                : item.bank.toUpperCase(),
                            count: item.dti_indicators_available,
                            bank: item.bank,
                          }))}
                          margin={{ top: 12, right: 9, bottom: 0, left: -17 }}
                        >
                          <CartesianGrid vertical={false} />
                          <XAxis
                            dataKey="name"
                            tickLine={false}
                            axisLine={false}
                          />
                          <YAxis
                            domain={[0, meta.framework.dti_indicators]}
                            ticks={[0, 3, 6, 9, 11]}
                            tickLine={false}
                            axisLine={false}
                          />
                          <Tooltip
                            formatter={(value) => [
                              `${value}/${meta.framework.dti_indicators}`,
                              'Chỉ số có dữ liệu',
                            ]}
                          />
                          <Bar dataKey="count" radius={[4, 4, 0, 0]} barSize={28}>
                            {visibleItems.map((item) => (
                              <Cell key={item.bank} fill={BANK_COLORS[item.bank]} />
                            ))}
                          </Bar>
                        </ComposedChart>
                      </ResponsiveContainer>
                    </div>
                    <div className="panel-footer">
                      <span>
                        Độ tin cậy = số chỉ số có dữ liệu /{' '}
                        {meta.framework.dti_indicators}
                      </span>
                      <span>
                        {visibleItems.length > 0
                          ? `${visibleItems.filter((item) => item.reliability === 'high').length} ngân hàng có độ tin cậy cao`
                          : 'Chưa có ngân hàng'}
                      </span>
                    </div>
                  </section>
                </div>
              </div>

              <p className="content-footnote">
                <Check size={10} /> Điểm và phân bố lấy từ API read-only của
                bank-dx-toolkit. DBI = thuật toán quy tắc; thiếu DTI không được
                thay bằng 0. Xu hướng liên năm cần đọc cùng thay đổi độ phủ dữ
                liệu.
              </p>
            </>
          )}
            </>
          )}
        </div>
      </main>
    </div>
  )
}
