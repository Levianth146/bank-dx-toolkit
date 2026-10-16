import { useEffect, useMemo, useState, type CSSProperties } from 'react'
import {
  AlertCircle,
  ArrowDownRight,
  ArrowUpRight,
  CheckCircle2,
  ExternalLink,
  FileSearch,
  Info,
  Landmark,
  ShieldCheck,
} from 'lucide-react'
import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  PolarAngleAxis,
  PolarGrid,
  Radar,
  RadarChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import vietcombankLogo from '../assets/vietcombank-mark.png'
import mbLogo from '../assets/mb-logo.png'
import techcombankLogo from '../assets/techcombank-mark.svg'
import bidvLogo from '../assets/bidv-mark.png'
import agribankLogo from '../assets/agribank-mark.png'
import { getBankDtiInputs, type DtiInput } from '../api/dashboard'
import type {
  BankDetailResponse,
  DashboardMeta,
  RankingItem,
  TrendResponse,
} from '../api/dashboard'

interface Tab2BankProfileProps {
  banks: DashboardMeta['banks']
  framework: DashboardMeta['framework']
  pillars: DashboardMeta['pillars']
  year: number
  ranking: RankingItem[]
  details: BankDetailResponse[]
  trend: TrendResponse | null
  loading: boolean
  error: string | null
}

const BANK_ORDER = ['vcb', 'mb', 'tcb', 'bidv', 'agribank']

const BANK_COLORS: Record<string, string> = {
  vcb: '#007a4b',
  mb: '#0648a8',
  tcb: '#e7163d',
  bidv: '#008b8b',
  agribank: '#a31c28',
}

const BANK_CODES: Record<string, string> = {
  vcb: 'VCB',
  mb: 'MB',
  tcb: 'TCB',
  bidv: 'BIDV',
  agribank: 'AGR',
}

const BANK_LEGAL_PROFILES: Record<
  string,
  {
    legalName: string
    listing: string
    founded: string
    headquarters: string
    website: string
    app: string
    source: string
  }
> = {
  vcb: {
    legalName: 'Ngân hàng TMCP Ngoại thương Việt Nam',
    listing: 'VCB · HOSE',
    founded: '1963',
    headquarters: '198 Trần Quang Khải, Hà Nội',
    website: 'https://www.vietcombank.com.vn/',
    app: 'VCB Digibank',
    source: 'https://www.vietcombank.com.vn/',
  },
  mb: {
    legalName: 'Ngân hàng TMCP Quân đội',
    listing: 'MBB · HOSE',
    founded: '1994',
    headquarters: '18 Lê Văn Lương, Hà Nội',
    website: 'https://www.mbbank.com.vn/',
    app: 'MBBank App',
    source: 'https://www.mbbank.com.vn/',
  },
  tcb: {
    legalName: 'Ngân hàng TMCP Kỹ thương Việt Nam',
    listing: 'TCB · HOSE',
    founded: '1993',
    headquarters: '6 Quang Trung, Hà Nội',
    website: 'https://techcombank.com/',
    app: 'Techcombank Mobile',
    source: 'https://techcombank.com/',
  },
  bidv: {
    legalName: 'Ngân hàng TMCP Đầu tư và Phát triển Việt Nam',
    listing: 'BID · HOSE',
    founded: '1957',
    headquarters: 'Tháp BIDV, 194 Trần Quang Khải, Hà Nội',
    website: 'https://bidv.com.vn/',
    app: 'BIDV SmartBanking',
    source: 'https://bidv.com.vn/',
  },
  agribank: {
    legalName: 'Ngân hàng Nông nghiệp và Phát triển Nông thôn Việt Nam',
    listing: 'Chưa niêm yết',
    founded: '1988',
    headquarters: '2 Láng Hạ, Hà Nội',
    website: 'https://www.agribank.com.vn/',
    app: 'Agribank Plus',
    source: 'https://www.agribank.com.vn/vn/ve-agribank/gioi-thieu-agribank',
  },
}

const formatNumber = (value: number | null | undefined, digits = 1) =>
  value == null
    ? 'Chưa có dữ liệu'
    : new Intl.NumberFormat('vi-VN', {
        maximumFractionDigits: digits,
      }).format(value)

const REPORT_FACTS = [
  { variable: 'total_assets', label: 'Tổng tài sản' },
  { variable: 'equity', label: 'Vốn chủ sở hữu' },
  { variable: 'customer_deposits', label: 'Tiền gửi khách hàng' },
  { variable: 'net_profit', label: 'LNST thuộc cổ đông ngân hàng mẹ' },
] as const

function formatReportValue(value: number | null, unit: string) {
  if (value == null) return 'Chưa có dữ liệu'
  if (unit === 'VND million') {
      return `${formatNumber(value / 1_000_000, 2)} nghìn tỷ đồng`
  }
  if (unit === 'VND') {
      return `${formatNumber(value / 1_000_000_000, 2)} tỷ đồng`
  }
  return `${formatNumber(value, 2)}${unit ? ` ${unit}` : ''}`
}

function shortFileName(file: string | null | undefined) {
  if (!file) return null
  return file.split(/[\\/]/).pop() ?? file
}

function PillarScoreCards({
  detail,
  ranking,
  pillars,
  framework,
}: {
  detail: BankDetailResponse
  ranking: RankingItem[]
  pillars: DashboardMeta['pillars']
  framework: DashboardMeta['framework']
}) {
  return (
    <section className="profile-panel profile-scoring">
      <div className="profile-section-heading">
        <div>
          <h2>Điểm được tính như thế nào?</h2>
          <p>
            Điểm của 6 trụ cột theo khung DBI–DTI; ô thiếu vẫn được giữ là thiếu.
          </p>
        </div>
        <span className="profile-formula">
          P = {Math.round(framework.dbi_weight * 100)}% DBI +{' '}
          {Math.round(framework.dti_weight * 100)}% DTI
        </span>
      </div>

      <div className="profile-pillar-grid">
        {pillars.map((pillar, index) => {
          const score = detail.summary.pillars[pillar.code]
          const peerScores = ranking
            .map((item) => item.pillars[pillar.code]?.p)
            .filter((value): value is number => value != null)
          const pillarRank =
            score?.p == null
              ? null
              : peerScores.filter((value) => value > score.p!).length + 1

          return (
            <article
              className={`profile-pillar-card${detail.highlights.strongest_pillar === pillar.code ? ' is-strongest' : ''}`}
              key={pillar.code}
            >
              <div className="profile-pillar-card__top">
                <h3>
                  {index + 1}. {pillar.name}
                </h3>
                <span>
                  {pillarRank == null
                    ? '—'
                    : `${pillarRank}/${ranking.length}`}
                </span>
              </div>
              <dl>
                <div>
                  <dt>DBI ({Math.round(framework.dbi_weight * 100)}%)</dt>
                  <dd>{formatNumber(score?.dbi)}</dd>
                </div>
                <div>
                  <dt>DTI ({Math.round(framework.dti_weight * 100)}%)</dt>
                  <dd>
                    {score?.dti_applied && score.dti != null
                      ? formatNumber(score.dti)
                      : 'Chưa có'}
                  </dd>
                </div>
              </dl>
              <div className="profile-pillar-card__score">
                <span>Điểm P</span>
                <strong>{formatNumber(score?.p)}</strong>
              </div>
              <div className="profile-pillar-coverage">
                DTI: {score?.n_dti ?? 0}/{score?.n_dti_total ?? 0} chỉ số
              </div>
            </article>
          )
        })}
      </div>

      <p className="profile-footnote">
        Khi trụ cột không có DTI áp dụng, điểm P được tính từ DBI theo quy tắc của
        backend; DTI không bị thay bằng 0.
      </p>
    </section>
  )
}

export default function Tab2BankProfile({
  banks,
  framework,
  pillars,
  year,
  ranking,
  details,
  trend,
  loading,
  error,
}: Tab2BankProfileProps) {
  const [selectedBank, setSelectedBank] = useState('vcb')
  const [comparisonMode, setComparisonMode] = useState(false)
  const [reportResponse, setReportResponse] = useState<{
    key: string
    items: DtiInput[]
    error: string | null
  }>({ key: '', items: [], error: null })

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

  const activeBank = orderedBanks.find((bank) => bank.id === selectedBank)
    ?? orderedBanks[0]
  const activeDetail = details.find(
    (item) => item.summary.bank === activeBank?.id,
  )
  const activeRanking = ranking.find(
    (item) => item.bank === activeBank?.id,
  )

  const activeBankId = activeBank?.id
  const reportQueryKey = activeBankId ? `${activeBankId}:${year}` : ''

  useEffect(() => {
    if (!activeBankId) return

    const requestKey = `${activeBankId}:${year}`
    const controller = new AbortController()

    getBankDtiInputs(activeBankId, year, controller.signal)
      .then((response) =>
        setReportResponse({
          key: requestKey,
          items: response.items,
          error: null,
        }),
      )
      .catch((loadError: unknown) => {
        if (!controller.signal.aborted) {
          setReportResponse({
            key: requestKey,
            items: [],
            error:
              loadError instanceof Error
                ? loadError.message
                : 'Không thể tải dữ liệu từ báo cáo tài chính.',
          })
        }
      })

    return () => controller.abort()
  }, [activeBankId, year])

  const hasReportResponse = reportResponse.key === reportQueryKey
  const reportInputs = hasReportResponse ? reportResponse.items : []
  const reportInputsError = hasReportResponse ? reportResponse.error : null
  const reportInputsLoading = Boolean(activeBankId && !hasReportResponse)

  const pillarScores = useMemo(
    () =>
      pillars.map((pillar) => {
        const peerScores = ranking
          .filter((item) => item.bank !== activeBank?.id)
          .map((item) => item.pillars[pillar.code]?.p)
          .filter((value): value is number => value != null)

        return {
          code: pillar.code,
          name: pillar.name,
          score: activeDetail?.summary.pillars[pillar.code]?.p ?? null,
          comparison: peerScores.length
            ? peerScores.reduce((sum, value) => sum + value, 0) /
              peerScores.length
            : null,
        }
      }),
    [activeBank?.id, activeDetail, pillars, ranking],
  )

  const trendData = useMemo(() => {
    if (!trend || !activeBank) return []
    const selectedSeries = trend.series.find(
      (series) => series.bank === activeBank.id,
    )

    return trend.years.map((trendYear) => {
      const bankValue =
        selectedSeries?.points.find((point) => point.year === trendYear)?.value ??
        null
      const peerValues = trend.series
        .filter((series) => series.bank !== activeBank.id)
        .map(
          (series) =>
            series.points.find((point) => point.year === trendYear)?.value,
        )
        .filter((value): value is number => value != null)

      return {
        year: trendYear,
        bank: bankValue,
        peers: peerValues.length
          ? peerValues.reduce((sum, value) => sum + value, 0) / peerValues.length
          : null,
      }
    })
  }, [activeBank, trend])

  const scoredCriteria = useMemo(
    () =>
      [...(activeDetail?.criteria ?? [])].filter(
        (criterion) => criterion.score != null,
      ),
    [activeDetail],
  )
  const strongestCriteria = useMemo(
    () =>
      [...scoredCriteria]
        .sort((a, b) => (b.score ?? -1) - (a.score ?? -1))
        .slice(0, 3),
    [scoredCriteria],
  )
  const improvementCriteria = useMemo(
    () =>
      [...scoredCriteria]
        .sort((a, b) => (a.score ?? 6) - (b.score ?? 6))
        .slice(0, 3),
    [scoredCriteria],
  )
  const criteriaByBank = useMemo(
    () =>
      new Map(
        details.map((detail) => [
          detail.summary.bank,
          new Map(detail.criteria.map((criterion) => [criterion.criterion, criterion])),
        ]),
      ),
    [details],
  )

  if (loading) {
    return (
      <div className="loading-state profile-state">
        <Landmark size={22} />
        <strong>Đang tải hồ sơ ngân hàng năm {year}</strong>
        <p>Dữ liệu điểm, tiêu chí và chỉ số được lấy trực tiếp từ backend.</p>
      </div>
    )
  }

  if (error) {
    return (
      <div className="error-state profile-state" role="alert">
        <AlertCircle size={22} />
        <strong>Không tải được dữ liệu hồ sơ</strong>
        <p>{error}</p>
      </div>
    )
  }

  if (!activeBank || !activeDetail || !activeRanking) {
    return (
      <div className="empty-selection profile-state">
        <strong>Chưa có hồ sơ cho năm {year}</strong>
        <p>Backend chưa trả về dữ liệu ngân hàng để hiển thị.</p>
      </div>
    )
  }

  const detail = activeDetail
  const summary = detail.summary
  const bankColor = BANK_COLORS[activeBank.id] ?? '#31516e'
  const bankCode = BANK_CODES[activeBank.id] ?? activeBank.id.toUpperCase()
  const legalProfile = BANK_LEGAL_PROFILES[activeBank.id]
  const coverage =
    summary.dti_indicators_total > 0
      ? (summary.dti_indicators_available / summary.dti_indicators_total) * 100
      : 0
  const confidence = summary.data_confidence * 100
  const scoreChange = activeRanking.score_change
  const site = activeBank.site
  const criteriaCount = detail.criteria.length
  const scoredCount = detail.criteria.filter(
    (criterion) => criterion.score != null,
  ).length
  const strongestPillarName =
    pillars.find((pillar) => pillar.code === detail.highlights.strongest_pillar)
      ?.name ?? 'Chưa có dữ liệu'
  const weakestPillarName =
    pillars.find((pillar) => pillar.code === detail.highlights.weakest_pillar)
      ?.name ?? 'Chưa có dữ liệu'

  return (
    <div
      className="bank-profile"
      style={{ '--bank-color': bankColor } as CSSProperties}
    >
      <div className="profile-bank-tabs" role="group" aria-label="Chọn ngân hàng">
        {orderedBanks.map((bank) => {
          const isSelected = bank.id === activeBank.id
          const color = BANK_COLORS[bank.id] ?? '#31516e'
          return (
            <button
              type="button"
              key={bank.id}
              className={`profile-bank-tab${isSelected ? ' is-selected' : ''}`}
              style={{ '--bank-color': color } as CSSProperties}
              aria-pressed={isSelected}
              onClick={() => setSelectedBank(bank.id)}
            >
              <span className="profile-bank-tab__dot" />
              <span>
                {bank.name} ({BANK_CODES[bank.id] ?? bank.id.toUpperCase()})
              </span>
              {isSelected && <CheckCircle2 size={14} aria-hidden="true" />}
            </button>
          )
        })}
      </div>

      <section
        className={`profile-hero${activeBank.id === 'vcb' ? ' profile-hero--vcb' : ''}${activeBank.id === 'mb' ? ' profile-hero--mb' : ''}${activeBank.id === 'tcb' ? ' profile-hero--tcb' : ''}${activeBank.id === 'bidv' ? ' profile-hero--bidv' : ''}${activeBank.id === 'agribank' ? ' profile-hero--agribank' : ''}`}
        style={{ '--bank-color': bankColor } as CSSProperties}
      >
        <div className="profile-hero__identity">
          {activeBank.id === 'vcb' ? (
            <span className="profile-vcb-logo">
              <img src={vietcombankLogo} alt="Logo Vietcombank" />
            </span>
          ) : activeBank.id === 'mb' ? (
            <span className="profile-mb-logo">
              <img src={mbLogo} alt="Logo MB Bank" />
            </span>
          ) : activeBank.id === 'tcb' ? (
            <span className="profile-tcb-logo">
              <img src={techcombankLogo} alt="Logo Techcombank" />
            </span>
          ) : activeBank.id === 'bidv' ? (
            <span className="profile-bidv-logo">
              <img src={bidvLogo} alt="Biểu tượng BIDV" />
            </span>
          ) : activeBank.id === 'agribank' ? (
            <span className="profile-agribank-logo">
              <img src={agribankLogo} alt="Biểu tượng Agribank" />
            </span>
          ) : (
            <span className="profile-bank-mark">{bankCode}</span>
          )}
          <div>
            <span className="profile-kicker">
              <span className="profile-kicker__dot" />
              {summary.group}
            </span>
            <h2>{summary.bank_name}</h2>
            <p>
              Mã ngân hàng: {bankCode} <span>·</span> Kỳ đo lường: {year}
            </p>
          </div>
        </div>

        <div className="profile-hero__metrics">
          <div className="profile-hero-score">
            <strong>{formatNumber(summary.score, 2)}</strong>
            <div>
              <span>Điểm tổng hợp</span>
              <div className="profile-hero-badges">
                <span>Hạng {summary.rank}/{ranking.length}</span>
                <span>{summary.maturity_level}</span>
              </div>
            </div>
          </div>

          <div className="profile-hero-coverage">
            <div className="profile-coverage-label">
              <span>Độ bao phủ DTI</span>
              <strong>
                {summary.dti_indicators_available}/
                {summary.dti_indicators_total} chỉ số
              </strong>
            </div>
            <div
              className="profile-coverage-track"
              role="progressbar"
              aria-label="Độ bao phủ DTI"
              aria-valuenow={coverage}
              aria-valuemin={0}
              aria-valuemax={100}
            >
              <span style={{ width: `${coverage}%` }} />
            </div>
            <div className="profile-coverage-footer">
              <span>Độ tin cậy dữ liệu: {formatNumber(confidence)}%</span>
              {scoreChange != null && (
                <span className={scoreChange >= 0 ? 'is-positive' : 'is-negative'}>
                  {scoreChange >= 0 ? <ArrowUpRight size={13} /> : <ArrowDownRight size={13} />}
                  {formatNumber(Math.abs(scoreChange), 2)} điểm so với kỳ trước
                </span>
              )}
            </div>
          </div>
        </div>
      </section>

      <section className="profile-panel profile-context">
        <div className="profile-section-heading profile-context__heading">
          <div className="profile-heading-title">
            <Landmark size={19} aria-hidden="true" />
            <div>
              <h2>Thông tin ngân hàng</h2>
              <p>
                Thông tin và chỉ số có trong API backend cho {summary.bank_name}.
              </p>
            </div>
          </div>
          <div className="profile-mode-switch" role="group" aria-label="Chế độ hồ sơ">
            <button
              type="button"
              className={!comparisonMode ? 'is-active' : ''}
              aria-pressed={!comparisonMode}
              onClick={() => setComparisonMode(false)}
            >
              Ngân hàng đang xem
            </button>
            <button
              type="button"
              className={comparisonMode ? 'is-active' : ''}
              aria-pressed={comparisonMode}
              onClick={() => setComparisonMode(true)}
            >
              So sánh 5 ngân hàng
            </button>
          </div>
        </div>

        {comparisonMode ? (
          <div className="profile-compare-grid">
            {orderedBanks.map((bank) => {
              const bankDetail = details.find(
                (item) => item.summary.bank === bank.id,
              )
              const color = BANK_COLORS[bank.id] ?? '#31516e'
              return (
                <button
                  type="button"
                  className={`profile-compare-card${bank.id === activeBank.id ? ' is-selected' : ''}`}
                  key={bank.id}
                  style={{ '--bank-color': color } as CSSProperties}
                  onClick={() => setSelectedBank(bank.id)}
                >
                  <span className="profile-compare-card__brand">
                    <span className="profile-bank-tab__dot" />
                    {bank.name}
                  </span>
                  <strong>{formatNumber(bankDetail?.summary.score, 2)}</strong>
                  <span>
                    {bankDetail
                      ? `Hạng ${bankDetail.summary.rank}/${ranking.length} · ${bankDetail.summary.maturity_level_name}`
                      : 'Chưa có dữ liệu'}
                  </span>
                  <span className="profile-compare-card__coverage">
                    DTI {bankDetail?.summary.dti_indicators_available ?? '—'}/
                    {bankDetail?.summary.dti_indicators_total ?? '—'}
                  </span>
                </button>
              )
            })}
          </div>
        ) : (
          <div className="profile-context-grid">
            <article className="profile-info-card profile-info-card--legal">
              <h3>Nhận diện pháp lý</h3>
              {legalProfile ? (
                <>
                  <dl className="profile-legal-facts">
                    <div className="profile-legal-facts__full">
                      <dt>Tên đầy đủ</dt>
                      <dd>{legalProfile.legalName}</dd>
                    </div>
                    <div>
                      <dt>Mã CK niêm yết</dt>
                      <dd>{legalProfile.listing}</dd>
                    </div>
                    <div>
                      <dt>Năm thành lập</dt>
                      <dd>{legalProfile.founded}</dd>
                    </div>
                    <div className="profile-legal-facts__full">
                      <dt>Trụ sở chính</dt>
                      <dd>{legalProfile.headquarters}</dd>
                    </div>
                    <div>
                      <dt>Website</dt>
                      <dd>
                        <a href={legalProfile.website} target="_blank" rel="noreferrer">
                          {legalProfile.website.replace(/^https?:\/\//, '').replace(/\/$/, '')}
                          <ExternalLink size={12} />
                        </a>
                      </dd>
                    </div>
                    <div>
                      <dt>Ứng dụng di động</dt>
                      <dd>{legalProfile.app}</dd>
                    </div>
                  </dl>
                  <a
                    className="profile-legal-source"
                    href={legalProfile.source}
                    target="_blank"
                    rel="noreferrer"
                  >
                    Nguồn: website chính thức <ExternalLink size={12} />
                  </a>
                </>
              ) : (
                <p className="profile-legal-unavailable">
                  Chưa có thông tin pháp lý cho ngân hàng này.
                  {site && (
                    <> Tra cứu tại <a href={site} target="_blank" rel="noreferrer">{site}</a>.</>
                  )}
                </p>
              )}
            </article>

            <article className="profile-info-card">
              <h3>Chỉ số từ backend</h3>
              <div className="profile-data-metrics">
                <div>
                  <span>Tiêu chí DBI có điểm</span>
                  <strong>
                    {scoredCount}/{criteriaCount}
                  </strong>
                </div>
                <div>
                  <span>Chỉ số DTI có dữ liệu</span>
                  <strong>
                    {summary.dti_indicators_available}/
                    {summary.dti_indicators_total}
                  </strong>
                </div>
                <div>
                  <span>Trụ cột mạnh nhất</span>
                  <strong>{strongestPillarName}</strong>
                </div>
                <div>
                  <span>Trụ cột cần chú ý</span>
                  <strong>{weakestPillarName}</strong>
                </div>
              </div>
              <p className="profile-data-note">
                <Info size={13} />
                Các thông tin tài chính từ báo cáo được dẫn nguồn ở thẻ kế bên.
              </p>
            </article>

            <article className="profile-info-card profile-info-card--report">
              <h3>Số liệu báo cáo · {year}</h3>
              {reportInputsLoading ? (
                <p className="profile-report-message">Đang tải số liệu và nguồn...</p>
              ) : reportInputsError ? (
                <p className="profile-report-message is-error" role="alert">
                  {reportInputsError}
                </p>
              ) : (
                <dl className="profile-report-facts">
                  {REPORT_FACTS.map(({ variable, label }) => {
                    const input = reportInputs.find(
                      (item) => item.variable === variable,
                    )
                    return (
                      <div key={variable}>
                        <dt>{label}</dt>
                        <dd>
                          <strong>
                            {input?.confirmed
                              ? formatReportValue(input.value, input.unit)
                              : 'Chưa có dữ liệu đã đối chiếu'}
                          </strong>
                          {input?.confirmed && input.source_url && (
                            <a
                              href={`${input.source_url}#page=${input.page ?? 1}`}
                              target="_blank"
                              rel="noreferrer"
                              title={`${input.source_file ?? 'Báo cáo tài chính'}${input.page != null ? ` · trang ${input.page}` : ''}`}
                            >
                              <FileSearch size={12} />
                              {input.page != null
                                ? `Nguồn · tr. ${input.page}`
                                : 'Nguồn báo cáo'}
                              <ExternalLink size={11} />
                            </a>
                          )}
                        </dd>
                      </div>
                    )
                  })}
                </dl>
              )}
              <p className="profile-report-note">
                Vốn chủ sở hữu không đồng nghĩa với vốn điều lệ. Trụ sở và cơ
                cấu cổ đông chưa có trong dữ liệu báo cáo backend.
              </p>
            </article>
          </div>
        )}
      </section>

      <PillarScoreCards
        detail={detail}
        ranking={ranking}
        pillars={pillars}
        framework={framework}
      />

      <section className="profile-analysis-grid">
        <article className="profile-panel">
          <div className="profile-section-heading">
            <div>
              <h2>Năng lực theo 6 trụ cột</h2>
              <p>
                {summary.bank_name} so với trung bình các ngân hàng còn lại.
              </p>
            </div>
          </div>
          <div className="profile-chart profile-radar-chart">
            <ResponsiveContainer width="100%" height="100%">
              <RadarChart data={pillarScores} outerRadius="72%">
                <PolarGrid stroke="#dbe4ee" />
                <PolarAngleAxis dataKey="name" tick={{ fontSize: 11 }} />
                <Tooltip formatter={(value) => formatNumber(Number(value))} />
                <Radar
                  name={summary.bank_name}
                  dataKey="score"
                  stroke={bankColor}
                  fill={bankColor}
                  fillOpacity={0.2}
                  strokeWidth={2}
                  connectNulls={false}
                />
                <Radar
                  name="Trung bình 4 ngân hàng"
                  dataKey="comparison"
                  stroke="#7b91aa"
                  fill="#9aabc0"
                  fillOpacity={0.08}
                  strokeDasharray="4 4"
                  connectNulls={false}
                />
                <Legend />
              </RadarChart>
            </ResponsiveContainer>
          </div>
        </article>

        <article className="profile-panel">
          <div className="profile-section-heading">
            <div>
              <h2>Điểm từng trụ cột gồm những gì?</h2>
              <p>Đóng góp DBI và DTI theo đúng trọng số trong API.</p>
            </div>
            <span className="profile-tag">DBI / DTI</span>
          </div>
          <div className="profile-contribution-list">
            {pillars.map((pillar, index) => {
              const score = detail.summary.pillars[pillar.code]
              if (score?.p == null) {
                return (
                  <div className="profile-contribution" key={pillar.code}>
                    <div className="profile-contribution__label">
                      <span>{index + 1}. {pillar.name}</span>
                      <strong>Chưa có dữ liệu</strong>
                    </div>
                    <div className="profile-contribution__track">
                      <span className="is-empty" />
                    </div>
                  </div>
                )
              }

              const dbiWeight = score.dti_applied
                ? framework.dbi_weight
                : 1
              const dbiContribution = (score.dbi ?? 0) * dbiWeight
              const dtiContribution =
                score.dti_applied && score.dti != null
                  ? score.dti * framework.dti_weight
                  : 0

              return (
                <div className="profile-contribution" key={pillar.code}>
                  <div className="profile-contribution__label">
                    <span>{index + 1}. {pillar.name}</span>
                    <strong>
                      {formatNumber(score.p)} đ
                      <small>
                        {score.dti_applied
                          ? ` (DBI ${formatNumber(dbiContribution)} + DTI ${formatNumber(dtiContribution)})`
                          : ` (100% DBI: ${formatNumber(score.dbi)})`}
                      </small>
                    </strong>
                  </div>
                  <div
                    className="profile-contribution__track"
                    aria-label={`Điểm ${pillar.name}: ${formatNumber(score.p)}`}
                  >
                    <span
                      className="profile-contribution__dbi"
                      style={{ width: `${Math.min(100, dbiContribution)}%` }}
                    />
                    {dtiContribution > 0 && (
                      <span
                        className="profile-contribution__dti"
                        style={{ width: `${Math.min(100, dtiContribution)}%` }}
                      />
                    )}
                  </div>
                </div>
              )
            })}
          </div>
          <div className="profile-legend">
            <span><i className="profile-legend__dbi" />DBI (80%)</span>
            <span><i className="profile-legend__dti" />DTI (20%)</span>
          </div>
        </article>
      </section>

      <section className="profile-insight-grid">
        <article className="profile-panel profile-insight-card is-positive">
          <h2><ArrowUpRight size={17} /> Điểm mạnh theo DBI</h2>
          {strongestCriteria.length ? (
            <ul>
              {strongestCriteria.map((criterion) => (
                <li key={criterion.criterion}>
                  <span>{criterion.criterion}</span>
                  <div>
                    <strong>{criterion.name}</strong>
                    <p>{criterion.status_label} · Mức {criterion.score}/4</p>
                  </div>
                </li>
              ))}
            </ul>
          ) : (
            <p>Backend chưa trả về tiêu chí DBI có điểm.</p>
          )}
        </article>

        <article className="profile-panel profile-insight-card is-attention">
          <h2><AlertCircle size={17} /> Các tiêu chí cần cải thiện</h2>
          {improvementCriteria.length ? (
            <ul>
              {improvementCriteria.map((criterion) => (
                <li key={criterion.criterion}>
                  <span>{criterion.criterion}</span>
                  <div>
                    <strong>{criterion.name}</strong>
                    <p>{criterion.status_label} · Mức {criterion.score}/4</p>
                  </div>
                </li>
              ))}
            </ul>
          ) : (
            <p>Chưa có đủ dữ liệu để xác định khoảng trống.</p>
          )}
        </article>

        <article className="profile-panel profile-insight-card is-quality">
          <h2><ShieldCheck size={17} /> Độ phủ &amp; kiểm định dữ liệu</h2>
          <dl>
            <div>
              <dt>Tiêu chí có điểm</dt>
              <dd>{scoredCount}/{criteriaCount}</dd>
            </div>
            <div>
              <dt>DTI có dữ liệu</dt>
              <dd>
                {summary.dti_indicators_available}/
                {summary.dti_indicators_total}
              </dd>
            </div>
            <div>
              <dt>Độ tin cậy</dt>
              <dd>{formatNumber(confidence)}%</dd>
            </div>
            <div>
              <dt>Mức tin cậy backend</dt>
              <dd>{summary.reliability}</dd>
            </div>
          </dl>
          {summary.warnings.length > 0 && (
            <p className="profile-warning">
              {summary.warnings.join(' ')}
            </p>
          )}
        </article>
      </section>

      <section className="profile-panel profile-history">
        <div className="profile-section-heading">
          <div>
            <h2>Tiến bộ so với các kỳ trước</h2>
            <p>
              Điểm tổng hợp của {summary.bank_name} và trung bình các ngân hàng
              khác theo dữ liệu xu hướng backend.
            </p>
          </div>
        </div>
        {trendData.length ? (
          <div className="profile-chart profile-trend-chart">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={trendData} margin={{ top: 12, right: 20, left: 8, bottom: 4 }}>
                <CartesianGrid strokeDasharray="3 4" vertical={false} />
                <XAxis dataKey="year" />
                <YAxis domain={[0, 100]} width={36} />
                <Tooltip formatter={(value) => formatNumber(Number(value), 2)} />
                <Legend />
                <Line
                  type="monotone"
                  dataKey="bank"
                  name={summary.bank_name}
                  stroke={bankColor}
                  strokeWidth={3}
                  dot={{ r: 4 }}
                  connectNulls={false}
                />
                <Line
                  type="monotone"
                  dataKey="peers"
                  name="Trung bình ngân hàng khác"
                  stroke="#8ca0b8"
                  strokeWidth={2}
                  strokeDasharray="5 4"
                  dot={{ r: 3 }}
                  connectNulls={false}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        ) : (
          <p className="profile-empty-chart">Backend chưa cung cấp dữ liệu xu hướng.</p>
        )}
      </section>

      <section className="profile-panel profile-evidence">
        <div className="profile-section-heading">
          <div>
            <h2>Bảng kiểm chứng định tính (DBI)</h2>
            <p>
              {detail.criteria.length} tiêu chí của {summary.bank_name}; điểm,
              trạng thái và dẫn chứng được đọc từ API.
            </p>
          </div>
          <span className="profile-tag">Trọng số DBI</span>
        </div>
        <div className="profile-table-scroll">
          <table className="profile-table profile-criteria-table">
            <thead>
              <tr>
                <th>Mã</th>
                <th>Trụ cột / tiêu chí</th>
                <th>Điểm</th>
                <th>So sánh 5 ngân hàng</th>
                <th>Trạng thái</th>
                <th>Nguồn</th>
              </tr>
            </thead>
            <tbody>
              {detail.criteria.map((criterion) => (
                <tr key={criterion.criterion}>
                  <td className="profile-code">{criterion.criterion}</td>
                  <td>
                    <strong>{criterion.name}</strong>
                    <small>{criterion.pillar_name}</small>
                  </td>
                  <td>
                    {criterion.score == null
                      ? 'Chưa có'
                      : `${criterion.score}/4`}
                  </td>
                  <td>
                    <div className="profile-criterion-peers">
                      {orderedBanks.map((bank) => {
                        const peerCriterion = criteriaByBank
                          .get(bank.id)
                          ?.get(criterion.criterion)
                        const value = peerCriterion?.score
                        return (
                          <span
                            className="profile-peer-score"
                            key={bank.id}
                            style={{ '--bank-color': BANK_COLORS[bank.id] ?? '#31516e' } as CSSProperties}
                            title={`${bank.name}: ${value == null ? 'Chưa có điểm' : `${value}/4`}`}
                          >
                            {value == null ? '—' : value}
                          </span>
                        )
                      })}
                    </div>
                  </td>
                  <td>
                    <span
                      className={`profile-status${criterion.score == null ? ' is-missing' : ''}`}
                      title={criterion.note ?? criterion.status}
                    >
                      {criterion.status_label}
                    </span>
                  </td>
                  <td>
                    {criterion.evidence?.url ? (
                      <a
                        className="profile-source-link"
                        href={criterion.evidence.url}
                        target="_blank"
                        rel="noreferrer"
                        title={criterion.evidence.quote ?? shortFileName(criterion.evidence.file) ?? 'Mở nguồn'}
                      >
                        <FileSearch size={13} />
                        {shortFileName(criterion.evidence.file) ?? 'Mở nguồn'}
                        {criterion.evidence.page != null &&
                          ` · tr. ${criterion.evidence.page}`}
                      </a>
                    ) : (
                      <span className="profile-no-source">Chưa có dẫn chứng</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <section className="profile-panel profile-dti">
        <div className="profile-section-heading">
          <div>
            <h2>Bảng chỉ số vận hành định lượng (DTI)</h2>
            <p>
              Các giá trị X và điểm chuẩn hóa được lấy từ dữ liệu backend; đơn vị
              được giữ nguyên theo từng chỉ số.
            </p>
          </div>
          <span className="profile-tag profile-tag--blue">Trọng số DTI</span>
        </div>
        <div className="profile-table-scroll">
          <table className="profile-table">
            <thead>
              <tr>
                <th>Mã chỉ số</th>
                <th>Chỉ số định lượng</th>
                <th>Giá trị</th>
                <th>Đơn vị</th>
                <th>Điểm chuẩn hóa</th>
                <th>Trạng thái backend</th>
              </tr>
            </thead>
            <tbody>
              {detail.dti_indicators.map((indicator) => (
                <tr key={indicator.indicator}>
                  <td className="profile-code">{indicator.indicator}</td>
                  <td>
                    <strong>{indicator.name}</strong>
                    <small>
                      {pillars.find((pillar) => pillar.code === indicator.pillar)?.name ??
                        indicator.pillar}
                    </small>
                  </td>
                  <td>
                    {indicator.has_data && indicator.x != null
                      ? formatNumber(indicator.x, 2)
                      : 'Chưa có dữ liệu'}
                  </td>
                  <td>{indicator.unit || '—'}</td>
                  <td>
                    {indicator.has_data && indicator.z != null
                      ? `${formatNumber(indicator.z, 1)}/100`
                      : '—'}
                  </td>
                  <td>
                    <span
                      className={`profile-status${indicator.has_data ? '' : ' is-missing'}`}
                      title={indicator.note ?? indicator.status}
                    >
                      {indicator.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  )
}
