import {
  AlertTriangle,
  ArrowRight,
  BookOpen,
  Check,
  CircleHelp,
  Database,
  Layers3,
  Lightbulb,
  LockKeyhole,
  Workflow,
} from 'lucide-react'
import type {
  BankDetailResponse,
  DashboardMeta,
  RankingItem,
} from '../api/dashboard'

type Tab5MethodologyProps = {
  meta: DashboardMeta
  details: BankDetailResponse[]
  ranking: RankingItem[]
  year: number
  loading: boolean
  error: string | null
  onNavigate: (tab: 'indicators' | 'diagnostics') => void
}

const PILLAR_COLORS: Record<string, string> = {
  K: '#2878e6',
  S: '#e28b32',
  T: '#16a36a',
  O: '#8257c7',
  C: '#d75a70',
  D: '#098b91',
}

const MATURITY_LEVELS = [
  { level: 5, name: 'Dẫn đầu / Tiên phong', range: '4.21–5.00' },
  { level: 4, name: 'Nâng cao / Tích hợp', range: '3.41–4.20' },
  { level: 3, name: 'Định hình / Chuẩn hóa', range: '2.61–3.40' },
  { level: 2, name: 'Cơ bản / Phân tầng', range: '1.81–2.60' },
  { level: 1, name: 'Khởi động / Sơ khai', range: '1.00–1.80' },
]

function formatPercent(value: number | null) {
  return value == null
    ? '—'
    : `${new Intl.NumberFormat('vi-VN', { maximumFractionDigits: 1 }).format(value)}%`
}

export default function Tab5Methodology({
  meta,
  details,
  ranking,
  year,
  loading,
  error,
  onNavigate,
}: Tab5MethodologyProps) {
  const framework = meta.framework
  const pillarCount = framework.pillars ?? meta.pillars.length
  const pillarWeight = (framework.dbi_weight * 100).toLocaleString('vi-VN')
  const dtiWeight = (framework.dti_weight * 100).toLocaleString('vi-VN')
  const yearRange = meta.years.length
    ? `${Math.min(...meta.years)}–${Math.max(...meta.years)}`
    : '—'
  const evaluatedCriteria = details.reduce(
    (total, detail) =>
      total + detail.criteria.filter((criterion) => criterion.score != null).length,
    0,
  )
  const availableDti = ranking.reduce(
    (total, item) => total + item.dti_indicators_available,
    0,
  )
  const totalDti = ranking.reduce(
    (total, item) => total + item.dti_indicators_total,
    0,
  )
  const dataCoverage =
    totalDti > 0 ? formatPercent((availableDti / totalDti) * 100) : '—'
  const confidenceValues = ranking
    .map((item) => item.data_confidence)
    .filter(Number.isFinite)
  const averageConfidence = confidenceValues.length
    ? confidenceValues.reduce((sum, value) => sum + value, 0) /
      confidenceValues.length
    : null
  const confidencePercent =
    averageConfidence == null
      ? null
      : averageConfidence <= 1
        ? averageConfidence * 100
        : averageConfidence
  const criteriaByPillar = new Map<
    string,
    Array<{ code: string; name: string }>
  >()
  for (const detail of details) {
    for (const criterion of detail.criteria) {
      const existing = criteriaByPillar.get(criterion.pillar) ?? []
      if (!existing.some((item) => item.code === criterion.criterion)) {
        existing.push({ code: criterion.criterion, name: criterion.name })
      }
      criteriaByPillar.set(criterion.pillar, existing)
    }
  }
  const indicatorsByCode = new Map<
    string,
    { name: string; unit: string; direction: string }
  >()
  for (const detail of details) {
    for (const indicator of detail.dti_indicators) {
      if (!indicatorsByCode.has(indicator.indicator)) {
        indicatorsByCode.set(indicator.indicator, {
          name: indicator.name,
          unit: indicator.unit,
          direction: indicator.direction,
        })
      }
    }
  }
  const citationCount = details.reduce(
    (total, detail) =>
      total +
      detail.criteria.filter(
        (criterion) =>
          criterion.evidence?.file ||
          criterion.evidence?.url ||
          criterion.evidence?.quote,
      ).length,
    0,
  )

  return (
    <section className="methodology-page" aria-labelledby="methodology-title">
      <header className="methodology-hero">
        <div className="methodology-hero-copy">
          <div className="methodology-eyebrow">
            <span className="methodology-eyebrow-chip">
              <BookOpen size={13} />
              Phương pháp luận nghiên cứu
            </span>
            <span className="methodology-eyebrow-divider" aria-hidden="true">•</span>
            <span>Cận chuẩn hóa tham chiếu, đã khóa phiên bản</span>
          </div>
          <h2 id="methodology-title">
            Khung đánh giá đối sánh
            <span>chuyển đổi số ngân hàng Việt Nam</span>
          </h2>
          <p>
            Mô hình kết hợp năng lực số chiến lược (DBI) và mức độ chuyển đổi
            thực tế (DTI), dựa trên dữ liệu công khai do backend cung cấp cho
            năm {year}.
          </p>
          <svg
            className="methodology-hero-art"
            viewBox="0 0 280 210"
            fill="none"
            aria-hidden="true"
          >
            <defs>
              <linearGradient id="methodology-bars" x1="0" y1="0" x2="0" y2="1">
                <stop stopColor="#527cc8" stopOpacity=".72" />
                <stop offset="1" stopColor="#527cc8" stopOpacity=".08" />
              </linearGradient>
              <linearGradient id="methodology-curve" x1="28" y1="154" x2="260" y2="72">
                <stop stopColor="#d4e2ff" />
                <stop offset="1" stopColor="#7da4ef" />
              </linearGradient>
            </defs>
            <path d="M10 190C78 159 143 176 270 123" stroke="#dce8fb" strokeWidth="1.5" />
            <path d="M16 198C86 169 159 178 266 135" stroke="#e8effc" strokeWidth="1.5" />
            <path d="M35 156C82 147 114 132 151 115S214 89 250 45" stroke="url(#methodology-curve)" strokeWidth="2" />
            <path d="M35 156L82 145L117 131L151 115L190 99L221 79L250 45" stroke="#9eb9ee" strokeOpacity=".5" strokeDasharray="3 5" />
            <circle cx="82" cy="145" r="5" fill="#d6e2fa" />
            <circle cx="151" cy="115" r="5" fill="#c2d4f7" />
            <circle cx="221" cy="79" r="5" fill="#a9c1f0" />
            <path d="M67 184V161a5 5 0 0 1 5-5h13a5 5 0 0 1 5 5v23M112 184v-37a5 5 0 0 1 5-5h13a5 5 0 0 1 5 5v37M157 184v-54a5 5 0 0 1 5-5h13a5 5 0 0 1 5 5v54M202 184v-76a5 5 0 0 1 5-5h13a5 5 0 0 1 5 5v76" fill="url(#methodology-bars)" />
            <path d="M197 38l24-14 24 14h-48ZM203 42h36M207 45v18M216 45v18M226 45v18M235 45v18M202 66h40" stroke="#a9bee9" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
            <path d="M199 68h46" stroke="#c7d7f4" strokeWidth="4" strokeLinecap="round" />
            <circle cx="250" cy="45" r="5" fill="#9ab4e7" />
          </svg>
        </div>
        <div className="methodology-hero-metrics">
          <div className="methodology-hero-metric">
            <Database size={17} />
            <span>
              <small>Độ phủ dữ liệu DTI · {year}</small>
              <strong>{dataCoverage}</strong>
            </span>
          </div>
          <div className="methodology-hero-metric methodology-hero-metric--green">
            <Check size={17} />
            <span>
              <small>Tiêu chí có điểm · {year}</small>
              <strong>
                <span>{evaluatedCriteria.toLocaleString('vi-VN')}</span> lượt
              </strong>
            </span>
          </div>
        </div>
      </header>

      {error && (
        <div className="methodology-error" role="alert">
          <AlertTriangle size={15} />
          <span>
            Không thể cập nhật số liệu năm {year}: {error}. Trang vẫn hiển thị
            cấu trúc phương pháp và dữ liệu đã tải trước đó.
          </span>
        </div>
      )}

      <div className="methodology-overview-grid">
        <article className="methodology-card methodology-architecture">
          <div className="methodology-section-heading">
            <div className="methodology-heading-icon">
              <Layers3 size={17} />
            </div>
            <div>
              <h3>Sơ đồ kiến trúc 3 lớp</h3>
              <p>Phân rã từ đánh giá định tính đến kiểm định kết quả</p>
            </div>
            <span className="methodology-cycle">Dữ liệu {yearRange}</span>
          </div>

          <div className="methodology-layer-list">
            <section className="methodology-layer methodology-layer--dbi">
              <div className="methodology-layer-head">
                <span className="methodology-layer-tag">L1</span>
                <strong>
                  Lớp A · {framework.criteria} tiêu chí định tính DBI
                </strong>
                <span>Tỷ trọng {pillarWeight}%</span>
              </div>
              <p>
                Đánh giá năng lực chiến lược, quản trị và hạ tầng số theo rubric
                0–4; nhóm thành {pillarCount} trụ cột.
              </p>
              <div className="methodology-pillar-grid">
                {meta.pillars.map((pillar) => (
                  <div className="methodology-pillar" key={pillar.code}>
                    <i style={{ backgroundColor: PILLAR_COLORS[pillar.code] ?? '#2878e6' }} />
                    <strong>{pillar.name}</strong>
                    <small>
                      {pillar.criteria?.length ??
                        criteriaByPillar.get(pillar.code)?.length ??
                        0}{' '}
                      tiêu chí
                    </small>
                  </div>
                ))}
              </div>
            </section>

            <section className="methodology-layer methodology-layer--dti">
              <div className="methodology-layer-head">
                <span className="methodology-layer-tag">L2</span>
                <strong>
                  Lớp B · {framework.dti_indicators} chỉ số định lượng DTI
                </strong>
                <span>Tỷ trọng {dtiWeight}%</span>
              </div>
              <p>
                Đo lường kết quả vận hành qua dữ liệu công bố; chuẩn hóa từng
                chỉ số theo cận dưới, cận trên và chiều tác động.
              </p>
              <div className="methodology-chip-list">
                {[...indicatorsByCode.entries()].slice(0, 8).map(([code, item]) => (
                  <span key={code} title={`${item.name} · ${item.unit}`}>
                    {item.name}
                  </span>
                ))}
                {indicatorsByCode.size > 8 && (
                  <span>+{indicatorsByCode.size - 8} chỉ số khác</span>
                )}
                {!indicatorsByCode.size && (
                  <span>Danh mục chi tiết sẽ hiện khi backend trả về dữ liệu</span>
                )}
              </div>
            </section>

            <section className="methodology-layer methodology-layer--validation">
              <div className="methodology-layer-head">
                <span className="methodology-layer-tag">L3</span>
                <strong>Lớp C · Kiểm định độ vững &amp; kết quả</strong>
              </div>
              <p>
                Phân tích độ nhạy theo kịch bản trọng số và kiểm tra tương quan
                với chỉ số hiệu quả hoạt động; kết quả kiểm định nằm tại tab
                “Độ vững &amp; Kiểm định”.
              </p>
            </section>
          </div>
          <div className="methodology-footnote">
            <LockKeyhole size={12} />
            Số liệu hiển thị được đọc từ API; thông tin thiếu được giữ là thiếu,
            không tự quy đổi thành 0.
          </div>
        </article>

        <article className="methodology-card methodology-maturity">
          <div className="methodology-section-heading">
            <div className="methodology-heading-icon methodology-heading-icon--violet">
              <Layers3 size={17} />
            </div>
            <div>
              <h3>Thang đo mức độ trưởng thành</h3>
              <p>Thang chuẩn hóa 5 cấp độ</p>
            </div>
          </div>
          <div className="methodology-maturity-list">
            {MATURITY_LEVELS.map((item) => (
              <div
                className={`methodology-maturity-level methodology-maturity-level--${item.level}`}
                key={item.level}
              >
                <span className="methodology-maturity-number">{item.level}</span>
                <div>
                  <strong>Mức {item.level}: {item.name}</strong>
                  <small>{item.range}</small>
                </div>
              </div>
            ))}
          </div>
          <p className="methodology-maturity-note">
            Diễn giải và ngưỡng mức theo tài liệu phương pháp; hạng thực tế của
            từng ngân hàng lấy từ phản hồi backend.
          </p>
        </article>
      </div>

      <section className="methodology-formula-cards" aria-label="Công thức tính điểm">
        <article className="methodology-formula-card methodology-formula-card--dbi">
          <header className="methodology-formula-card-header">
            <span className="methodology-formula-badge">
              Công thức <CircleHelp size={12} />
            </span>
            <span>Trọng số {pillarCount} trụ cột</span>
          </header>
          <h3>Điểm Định tính DBI</h3>
          <p>
            Trung bình trọng số của {pillarCount} trụ cột chính sau khi lấy bình
            quân các tiêu chí thành phần:
          </p>
          <div className="methodology-equation">
            <strong>
              S<sub>DBI</sub> = ∑<sub>j=1/{pillarCount}</sub> (w<sub>j</sub> × P<sub>j</sub>)
            </strong>
            <small>
              Với ∑ w<sub>j</sub> = 1.0, w<sub>j</sub> = 1/{pillarCount} (trọng số bằng nhau)
            </small>
          </div>
          <div className="methodology-formula-note">
            <strong>P<sub>j</sub>:</strong> Điểm trung bình của các tiêu chí thuộc
            trụ cột j. Mỗi tiêu chí chấm số nguyên 0–4, quy về % (0/25/50/75/100).
          </div>
        </article>

        <article className="methodology-formula-card methodology-formula-card--dti">
          <header className="methodology-formula-card-header">
            <span className="methodology-formula-badge">
              Công thức <CircleHelp size={12} />
            </span>
            <span>Hàm chặn Min–Max</span>
          </header>
          <h3>Chuẩn hóa Định lượng DTI</h3>
          <p>
            Quy đổi các chỉ số đo lường thực tế về thang điểm tương thích [0, 100]:
          </p>
          <div className="methodology-equation methodology-equation--large">
            <strong>
              Z<sub>k</sub> ={' '}
              <span className="methodology-fraction">
                <span>X<sub>k</sub> − L<sub>k</sub></span>
                <span>U<sub>k</sub> − L<sub>k</sub></span>
              </span>{' '}
              × 100
            </strong>
            <small>
              Ràng buộc kỹ thuật: Z<sub>k</sub> ∈ [0, 100], cắt biên khi X<sub>k</sub> &gt; U<sub>k</sub>
            </small>
          </div>
          <div className="methodology-formula-note">
            <strong>L<sub>k</sub>, U<sub>k</sub>:</strong> Cận cố định, không hiệu chỉnh theo
            5 ngân hàng sau khi khóa. Lấy từ biên tự nhiên của thang đo, mốc tham chiếu ngoài mẫu
            (NHNN, Santander) hoặc phân vị 10%/90% của mẫu gộp (T-Q1, O-Q1, O-Q2, C-Q2; thang tương đối).
            Đây là cận tham chiếu của nghiên cứu, không phải chuẩn bắt buộc.
          </div>
        </article>

        <article className="methodology-formula-card methodology-formula-card--total">
          <header className="methodology-formula-card-header">
            <span className="methodology-formula-badge">
              Công thức <CircleHelp size={12} />
            </span>
            <span>Tổng hợp &amp; xử lý dữ liệu thiếu</span>
          </header>
          <h3>Điểm Tổng hợp &amp; dữ liệu thiếu</h3>
          <p>
            Tích hợp Lớp A và Lớp B. Chỉ số DTI thiếu dữ liệu bị bỏ qua,
            không bù khuyết và không điền 0:
          </p>
          <div className="methodology-equation">
            <strong>
              S<sub>Tổng</sub> = {framework.dbi_weight.toLocaleString('vi-VN')} · S<sub>DBI</sub> +{' '}
              {framework.dti_weight.toLocaleString('vi-VN')} · S<sub>DTI</sub>
            </strong>
            <small>
              Trụ cột không có chỉ số DTI nào: P<sub>k</sub> = DBI<sub>k</sub>; Điểm tổng = trung bình 6 trụ cột
            </small>
          </div>
          <div className="methodology-formula-note">
            <strong>S<sub>DTI</sub>:</strong> Trung bình z của các chỉ số DTI có dữ liệu trong trụ cột.
            Chỉ số thiếu ở từ 2 ngân hàng trở lên trong một năm bị loại cho cả 5 ngân hàng năm đó (bước 0).
          </div>
        </article>
      </section>

      <div className="methodology-overview-grid methodology-overview-grid--second">
        <article className="methodology-card methodology-rubric">
          <div className="methodology-section-heading">
            <div className="methodology-heading-icon methodology-heading-icon--navy">
              <BookOpen size={17} />
            </div>
            <div>
              <h3>Thang chấm tiêu chí DBI</h3>
              <p>Mỗi mức cao hơn yêu cầu bằng chứng mạnh hơn</p>
            </div>
          </div>
          <div className="methodology-rubric-table-wrap">
            <table className="methodology-rubric-table">
              <thead>
                <tr><th>Mức</th><th>Tỷ lệ</th><th>Đặc trưng &amp; điều kiện minh chứng</th></tr>
              </thead>
              <tbody>
                <tr><td>Mức 0</td><td>0%</td><td>Có văn bản đọc được nhưng thuật toán không tìm thấy từ khóa; không đồng nghĩa ngân hàng không công bố.</td></tr>
                <tr><td>Mức 1</td><td>25%</td><td>Chỉ nêu định hướng hoặc kế hoạch; chưa có bằng chứng triển khai cụ thể.</td></tr>
                <tr><td>Mức 2</td><td>50%</td><td>Có dự án, sản phẩm số hoặc chính sách cụ thể; kết quả chưa được công bố định lượng.</td></tr>
                <tr><td>Mức 3</td><td>75%</td><td>Triển khai diện rộng, có số liệu kết quả hoặc minh chứng rõ trong báo cáo.</td></tr>
                <tr><td>Mức 4</td><td>100%</td><td>Có kết quả định lượng qua nhiều kỳ và xác thực từ nguồn độc lập.</td></tr>
              </tbody>
            </table>
          </div>
          <div className="methodology-card-footer">
            <span>Điểm do thuật toán quy tắc (rule-based-v1) chấm từ văn bản báo cáo; chưa kiểm chứng độc lập với chuyên gia.</span>
            <button type="button" onClick={() => onNavigate('indicators')}>
              Xem điểm ở Chỉ tiêu <ArrowRight size={13} />
            </button>
          </div>
        </article>

        <article className="methodology-card methodology-process">
          <div className="methodology-section-heading">
            <div className="methodology-heading-icon methodology-heading-icon--blue">
              <Workflow size={17} />
            </div>
            <div>
              <h3>Quy trình thực hiện</h3>
              <p>Chu kỳ dữ liệu {yearRange}</p>
            </div>
          </div>
          <ol className="methodology-process-list">
            <li><strong>Kiểm tra dữ liệu cơ bản</strong><span>Đối chiếu tính đầy đủ của dữ liệu công khai; đánh dấu trường thiếu.</span></li>
            <li><strong>Thu thập tài liệu &amp; bằng chứng</strong><span>Tổng hợp báo cáo thường niên, báo cáo phát triển bền vững và nguồn chính thức.</span></li>
            <li><strong>Định vị bằng từ khóa</strong><span>Liên kết tài liệu và bằng chứng với từng tiêu chí trong codebook.</span></li>
            <li><strong>Chấm tự động &amp; chuẩn hóa</strong><span>Thuật toán quy tắc chấm mức DBI; chuẩn hóa DTI theo cận cố định và chiều tác động.</span></li>
            <li><strong>Tính điểm &amp; kiểm tra độ vững</strong><span>Tổng hợp theo trọng số, sau đó kiểm tra các kịch bản nhạy cảm.</span></li>
          </ol>
          <div className="methodology-process-stats">
            <span><strong>{details.length}/{meta.banks.length}</strong> ngân hàng tải được</span>
            <span><strong>{evaluatedCriteria.toLocaleString('vi-VN')}</strong> lượt có điểm</span>
            <span><strong>{formatPercent(confidencePercent)}</strong> độ tin cậy TB</span>
          </div>
          <div className="methodology-card-footer">
            <span>Chi tiết độ vững được tính trực tiếp từ backend.</span>
            <button type="button" onClick={() => onNavigate('diagnostics')}>
              Xem kiểm định <ArrowRight size={13} />
            </button>
          </div>
        </article>
      </div>

      <section className="methodology-card methodology-codebook">
        <div className="methodology-section-heading">
          <div className="methodology-heading-icon methodology-heading-icon--blue">
            <BookOpen size={17} />
          </div>
          <div>
            <h3>Tài liệu tham chiếu &amp; codebook</h3>
            <p>Danh mục tiêu chí, chỉ số và mức độ sẵn có từ backend</p>
          </div>
          <span className="methodology-version">Framework API · {year}</span>
        </div>
        <details className="methodology-accordion" open>
          <summary>
            <span>Codebook {framework.criteria} tiêu chí DBI</span>
            <span>{meta.pillars.length} trụ cột</span>
          </summary>
          <div className="methodology-codebook-content">
            {meta.pillars.map((pillar) => {
              const criterionList =
                pillar.criteria?.length
                  ? pillar.criteria
                  : criteriaByPillar.get(pillar.code) ?? []
              return (
                <section className="methodology-codebook-pillar" key={pillar.code}>
                  <h4>
                    <i style={{ backgroundColor: PILLAR_COLORS[pillar.code] ?? '#2878e6' }} />
                    {pillar.name}
                    <span>{criterionList.length} tiêu chí</span>
                  </h4>
                  {criterionList.length ? (
                    <ul>
                      {criterionList.map((criterion) => (
                        <li key={criterion.code}>
                          <code>{criterion.code}</code>
                          <span>{criterion.name}</span>
                        </li>
                      ))}
                    </ul>
                  ) : (
                    <p>Chưa có danh sách tiêu chí chi tiết trong phản hồi API.</p>
                  )}
                </section>
              )
            })}
          </div>
        </details>
        <details className="methodology-accordion">
          <summary>
            <span>Chỉ số định lượng DTI</span>
            <span>{indicatorsByCode.size || framework.dti_indicators} chỉ số</span>
          </summary>
          <div className="methodology-indicator-table-wrap">
            <table className="methodology-indicator-table">
              <thead><tr><th>Mã</th><th>Chỉ số</th><th>Đơn vị</th><th>Chiều tác động</th></tr></thead>
              <tbody>
                {[...indicatorsByCode.entries()].map(([code, indicator]) => (
                  <tr key={code}>
                    <td><code>{code}</code></td><td>{indicator.name}</td><td>{indicator.unit || '—'}</td><td>{indicator.direction || '—'}</td>
                  </tr>
                ))}
                {!indicatorsByCode.size && (
                  <tr><td colSpan={4}>Backend chưa trả về danh mục DTI chi tiết cho năm này.</td></tr>
                )}
              </tbody>
            </table>
          </div>
        </details>
        <details className="methodology-accordion">
          <summary>
            <span>Ma trận độ phủ và bằng chứng · năm {year}</span>
            <span>{citationCount.toLocaleString('vi-VN')} minh chứng được liên kết</span>
          </summary>
          <div className="methodology-indicator-table-wrap">
            <table className="methodology-indicator-table">
              <thead><tr><th>Ngân hàng</th><th>Tiêu chí có dữ liệu</th><th>DTI khả dụng</th><th>Độ tin cậy</th></tr></thead>
              <tbody>
                {details.map((detail) => (
                  <tr key={detail.summary.bank}>
                    <td>{detail.summary.bank_name}</td>
                    <td>{detail.criteria.filter((criterion) => criterion.score != null).length}/{framework.criteria}</td>
                    <td>{detail.summary.dti_indicators_available}/{detail.summary.dti_indicators_total}</td>
                    <td>{formatPercent(
                      detail.summary.data_confidence <= 1
                        ? detail.summary.data_confidence * 100
                        : detail.summary.data_confidence,
                    )}</td>
                  </tr>
                ))}
                {!details.length && (
                  <tr><td colSpan={4}>Chưa có dữ liệu chi tiết từ backend.</td></tr>
                )}
              </tbody>
            </table>
          </div>
        </details>
        <details className="methodology-accordion">
          <summary>
            <span>Nguồn dữ liệu &amp; giới hạn đo lường</span>
            <span>{loading ? 'Đang đồng bộ…' : 'Cập nhật theo năm đang chọn'}</span>
          </summary>
          <div className="methodology-source-grid">
            <p><strong>Nguồn:</strong> Báo cáo và thông tin công khai do hệ thống backend tập hợp; từng minh chứng có thể xem trong tab Chỉ tiêu khi API cung cấp.</p>
            <p><strong>Giới hạn:</strong> Không đồng nhất về mức độ công bố giữa các ngân hàng; độ phủ DTI khác nhau và có thể ảnh hưởng khả năng so sánh.</p>
            <p><strong>Diễn giải:</strong> Điểm là kết quả đối sánh theo bộ tiêu chí này, không phải xếp hạng chính thức hay kết luận giám sát của cơ quan quản lý.</p>
          </div>
        </details>
      </section>

      <div className="methodology-overview-grid methodology-overview-grid--closing">
        <article className="methodology-limitations">
          <div className="methodology-section-heading">
            <div className="methodology-heading-icon methodology-heading-icon--amber">
              <AlertTriangle size={17} />
            </div>
            <div>
              <h3>Hạn chế nghiên cứu &amp; ranh giới phương pháp</h3>
              <p>Minh bạch phạm vi và những điểm cần thận trọng</p>
            </div>
          </div>
          <ol>
            <li><strong>Phụ thuộc nguồn dữ liệu công khai</strong><span>Khác biệt về mức độ công bố có thể ảnh hưởng độ phủ và khả năng xác minh; điểm thấp hoặc thiếu dữ liệu không đồng nghĩa năng lực thực tế thấp.</span></li>
            <li><strong>Phạm vi mẫu có giới hạn</strong><span>Phân tích chỉ bao gồm {meta.banks.length} ngân hàng hiện được cấu hình trong backend ({yearRange}); không đại diện toàn bộ hệ thống ngân hàng.</span></li>
            <li><strong>Khung tiêu chí được rút gọn</strong><span>{framework.criteria} tiêu chí DBI và {framework.dti_indicators} chỉ số DTI hỗ trợ đối sánh nhất quán nhưng không bao quát mọi khía cạnh chuyển đổi số.</span></li>
            <li><strong>Dữ liệu giữa các ngân hàng chưa đồng đều</strong><span>Một số ngân hàng chưa công bố đủ dữ liệu cho cùng các chỉ tiêu, nên việc so sánh có thể chưa hoàn toàn ngang bằng. Dữ liệu thiếu không được xem là điểm 0; cần đọc kết quả cùng độ phủ dữ liệu.</span></li>
          </ol>
          <p className="methodology-recommendation">
            <Lightbulb size={15} />
            Sử dụng kết quả như chỉ dấu định hướng; nên đọc cùng nguồn gốc, độ phủ và bối cảnh từng ngân hàng.
          </p>
        </article>

        <article className="methodology-recommendations">
          <div className="methodology-section-heading">
            <div className="methodology-heading-icon methodology-heading-icon--cyan">
              <Lightbulb size={17} />
            </div>
            <div>
              <h3>Kết luận &amp; khuyến nghị ứng dụng</h3>
              <p>Giá trị thực tiễn cho các bên liên quan</p>
            </div>
          </div>
          <div className="methodology-audience">
            <strong>Cơ quan quản lý</strong>
            <span>Tham khảo cách chuẩn hóa chỉ tiêu và minh bạch dữ liệu; không thay thế hoạt động thanh tra, giám sát.</span>
          </div>
          <div className="methodology-audience">
            <strong>Ban điều hành ngân hàng</strong>
            <span>Dùng khoảng trống theo trụ cột để xác định ưu tiên cải thiện và theo dõi tiến độ.</span>
          </div>
          <div className="methodology-audience">
            <strong>Nhà đầu tư &amp; giới nghiên cứu</strong>
            <span>Kết hợp điểm số với độ phủ, nguồn bằng chứng và bối cảnh tài chính khi phân tích.</span>
          </div>
          <div className="methodology-confidence">
            <LockKeyhole size={13} />
            {loading
              ? 'Đang đồng bộ số liệu phương pháp với backend…'
              : `Đang dùng ${details.length} hồ sơ ngân hàng từ API · ${year}`}
          </div>
        </article>
      </div>
    </section>
  )
}
