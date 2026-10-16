export interface DashboardMeta {
  latest_year: number
  years: number[]
  banks: Array<{
    id: string
    name: string
    group: string
    site?: string
  }>
  pillars: Array<{
    code: string
    name: string
    criteria?: Array<{
      code: string
      name: string
    }>
    dti_indicators?: string[]
  }>
  framework: {
    dbi_weight: number
    dti_weight: number
    pillars?: number
    criteria: number
    dti_indicators: number
    scale?: string
    pillar_formula?: string
    score_formula?: string
  }
}

export interface PillarScore {
  code: string
  name: string
  dbi: number | null
  dti: number | null
  p: number | null
  n_dti: number
  n_dti_total: number
  dti_applied: boolean
}

export interface RankingItem {
  bank: string
  bank_name: string
  group: string
  year: number
  score: number
  rank: number
  maturity_level: string
  maturity_level_number: number
  maturity_level_name: string
  data_confidence: number
  dti_indicators_available: number
  dti_indicators_total: number
  reliability: 'low' | 'medium' | 'high'
  warnings: string[]
  pillars: Record<string, PillarScore>
  score_change: number | null
  rank_change: number | null
}

export interface RankingResponse {
  year: number
  count: number
  items: RankingItem[]
}

export interface TrendPoint {
  year: number
  value: number | null
  rank: number | null
  data_confidence: number | null
  n_dti: number | null
}

export interface TrendResponse {
  metric: string
  years: number[]
  series: Array<{
    bank: string
    bank_name: string
    points: TrendPoint[]
  }>
  warnings: string[]
}

export interface BankDetailResponse {
  summary: {
    bank: string
    bank_name: string
    group: string
    year: number
    score: number
    rank: number
    maturity_level: string
    maturity_level_number: number
    maturity_level_name: string
    data_confidence: number
    dti_indicators_available: number
    dti_indicators_total: number
    reliability: 'low' | 'medium' | 'high'
    warnings: string[]
    pillars: Record<string, PillarScore>
  }
  criteria: Array<{
    criterion: string
    pillar: string
    pillar_name: string
    name: string
    bank: string
    year: number
    score: number | null
    score_pct: number | null
    status: string
    status_label: string
    confidence: string
    features: string[]
    evidence?: {
      file?: string | null
      page?: number | null
      url?: string | null
      quote?: string | null
    } | null
    note?: string | null
  }>
  dti_indicators: Array<{
    bank: string
    year: number
    indicator: string
    pillar: string
    name: string
    unit: string
    direction: string
    x: number | null
    L: number | null
    U: number | null
    z: number | null
    status: string
    has_data: boolean
    note?: string | null
  }>
  highlights: {
    strongest_pillar: string | null
    weakest_pillar: string | null
    criteria_score_distribution: Record<string, number>
  }
}

export interface DtiInput {
  bank: string
  year: number
  variable: string
  value: number | null
  unit: string
  source_file: string | null
  page: number | null
  source_url: string | null
  confirmed: boolean
  note: string | null
  missing_reason: string | null
}

export interface DtiInputsResponse {
  bank: string | null
  year: number | null
  count: number
  items: DtiInput[]
}

export interface SensitivityResponse {
  year: number
  base_scenario: string
  scenarios: string[]
  rows: Array<{
    bank: string
    bank_name: string
    by_scenario: Record<
      string,
      { score: number | null; rank: number | null; level: string | null }
    >
    rank_stable_pct: number | null
    rank_min: number | null
    rank_max: number | null
    stable_under_weights: boolean
  }>
  agreement_with_base: Array<{
    scenario: string
    kendall_tau: number | null
    spearman: number | null
  }>
  note: string
}

export interface SensitivityFullResponse {
  year: number
  available_years: number[]
  robust_threshold: number
  n_discrete_scenarios: number
  banks: Array<{
    bank: string
    bank_name: string
    base_score: number | null
    base_rank: number | null
    min_rank: number | null
    max_rank: number | null
    min_score: number | null
    max_score: number | null
    n_scenarios: number | null
    stable_share: number | null
    verdict: string | null
    is_robust: boolean
    borderline: boolean
    stable_by_family: Array<{
      family: string
      n_scenarios: number
      share: number | null
    }>
    monte_carlo: Array<{
      method: string
      p_base: number | null
      mean_rank: number | null
      rank_distribution: Array<{ rank: number; prob: number | null }>
    }>
  }>
  pairs: Array<{
    bank_a: string
    bank_b: string
    distinguishable: boolean
    borderline: boolean
    swapped_in_some_scenario: boolean
  }>
  rank_agreement: Array<{
    family: string
    scenario: string
    kendall_tau: number | null
    spearman_rho: number | null
    n_rank_changes: number | null
  }>
  note: string
}

export interface SensitivityScenariosResponse {
  year: number
  available_years: number[]
  count: number
  items: Array<{
    year: number
    family: string
    scenario: string
    bank: string
    score: number | null
    rank: number | null
    base_rank: number | null
    rank_change: number | null
  }>
}

export interface CorrelationResponse {
  score_var: string
  lag: number
  method: string
  metrics: Array<{
    metric: string
    name: string
    unit: string
    expected_sign: number | null
    by_year: Array<{
      year: number
      n: number
      spearman: number | null
      kendall: number | null
      p_kendall: number | null
      low_n: boolean | null
      consistent_with_expected: boolean | null
    }>
    pooled: {
      n: number
      spearman: number | null
      kendall: number | null
      p_kendall: number | null
      low_n: boolean | null
      consistent_with_expected: boolean | null
    }
    pooled_within_year: {
      n: number
      spearman: number | null
      consistent_with_expected: boolean | null
    }
  }>
  notes: string[]
}

export interface FinancialPerformanceResponse {
  year: number | null
  bank: string | null
  count: number
  metrics: Record<
    string,
    { name: string; unit: string; expected_sign: number | null }
  >
  items: Array<{
    bank: string
    bank_name: string
    year: number
    roe: number | null
    roa: number | null
    cir: number | null
    casa: number | null
    non_interest_share: number | null
    dbi_mean: number | null
    score: number | null
    data_confidence: number | null
    flags: string[]
  }>
  note: string
}

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000/api/v1'

async function getJson<T>(path: string, signal: AbortSignal): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, { signal })
  const responseText = await response.text()
  let payload: unknown

  try {
    payload = JSON.parse(responseText)
  } catch {
    throw new Error(
      `Backend trả về dữ liệu không phải JSON (HTTP ${response.status}) tại ${path}.`,
    )
  }

  if (!response.ok) {
    const apiError = payload as {
      error?: { message?: string }
    }
    throw new Error(
      apiError.error?.message ??
        `Yêu cầu backend thất bại (HTTP ${response.status}) tại ${path}.`,
    )
  }

  return payload as T
}

export function getDashboardMeta(signal: AbortSignal) {
  return getJson<DashboardMeta>('/meta', signal)
}

export function getRanking(year: number, signal: AbortSignal) {
  return getJson<RankingResponse>(
    `/ranking?year=${encodeURIComponent(year)}&sort_by=rank`,
    signal,
  )
}

export function getScoreTrend(signal: AbortSignal) {
  return getJson<TrendResponse>('/trend?metric=score', signal)
}

export function getBankYearDetail(
  bank: string,
  year: number,
  signal: AbortSignal,
) {
  return getJson<BankDetailResponse>(
    `/banks/${encodeURIComponent(bank)}/${encodeURIComponent(year)}`,
    signal,
  )
}

export function getBankDtiInputs(
  bank: string,
  year: number,
  signal: AbortSignal,
) {
  return getJson<DtiInputsResponse>(
    `/dti-inputs?bank=${encodeURIComponent(bank)}&year=${encodeURIComponent(year)}`,
    signal,
  )
}

export function getSensitivity(year: number, signal: AbortSignal) {
  return getJson<SensitivityResponse>(
    `/sensitivity?year=${encodeURIComponent(year)}`,
    signal,
  )
}

export function getSensitivityFull(signal: AbortSignal) {
  return getJson<SensitivityFullResponse>('/sensitivity/full', signal)
}

export function getSensitivityScenarios(year: number, signal: AbortSignal) {
  return getJson<SensitivityScenariosResponse>(
    `/sensitivity/scenarios?year=${encodeURIComponent(year)}`,
    signal,
  )
}

export function getLayerCCorrelation(signal: AbortSignal) {
  return getJson<CorrelationResponse>(
    '/layer-c/correlation?score_var=dbi&lag=0',
    signal,
  )
}

export function getFinancialPerformance(year: number, signal: AbortSignal) {
  return getJson<FinancialPerformanceResponse>(
    `/financial-performance?year=${encodeURIComponent(year)}&score_var=dbi`,
    signal,
  )
}
