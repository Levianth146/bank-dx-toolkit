"""Mô hình phản hồi (Pydantic) -> sinh tài liệu OpenAPI ở /docs và /openapi.json cho nhóm frontend.
Điểm theo thang 0–100; mọi trường Optional có thể là null nghĩa là THIẾU DỮ LIỆU (không phải 0)."""
from pydantic import BaseModel, Field


class PillarScore(BaseModel):
    code: str = Field(description="K, S, T, O, C hoặc D")
    name: str
    dbi: float | None = Field(None, description="DBI_k: trung bình 4 tiêu chí rubric quy về %")
    dti: float | None = Field(None, description="DTI_k: trung bình z của các chỉ số DTI có dữ liệu; null nếu không có")
    p: float | None = Field(None, description="P_k = 0,8·DBI_k + 0,2·DTI_k; thiếu DTI thì P_k = DBI_k")
    n_dti: int = Field(description="Số chỉ số DTI có dữ liệu của trụ cột")
    n_dti_total: int = Field(description="Tổng chỉ số DTI của trụ cột (trụ cột D = 0)")
    dti_applied: bool = Field(description="true nếu P_k có thành phần DTI 20%; false nếu P_k = DBI_k")


class BankYear(BaseModel):
    bank: str
    bank_name: str
    group: str | None
    year: int
    score: float | None = Field(description="Score_Bank = trung bình 6 trụ cột P_k")
    rank: int | None
    maturity_level: str | None = Field(description="Ví dụ 'Mức 3 - Hình thành'")
    maturity_level_number: int | None
    maturity_level_name: str | None
    data_confidence: float | None = Field(description="Độ tin cậy dữ liệu 0–1 = số chỉ số DTI có dữ liệu / 11")
    dti_indicators_available: int | None
    dti_indicators_total: int
    reliability: str | None = Field(description="high | medium | low (quy ước hiển thị theo data_confidence)")
    warnings: list[str]
    pillars: dict[str, PillarScore]


class RankingItem(BankYear):
    score_change: float | None = Field(None, description="Chênh lệch điểm so với năm trước (null ở năm đầu)")
    rank_change: int | None = Field(None, description="Hạng năm trước − hạng năm nay (dương = tăng hạng)")


class RankingResponse(BaseModel):
    year: int
    count: int
    sort_by: str
    order: str
    scoring_method: str | None
    rules_version: str | None
    items: list[RankingItem]


class TrendPoint(BaseModel):
    year: int
    value: float | None
    rank: int | None
    maturity_level_number: int | None
    data_confidence: float | None
    n_dti: int | None


class TrendSeries(BaseModel):
    bank: str
    bank_name: str
    group: str | None
    points: list[TrendPoint]
    dti_coverage_changes: bool = Field(description="true nếu số chỉ số DTI có dữ liệu đổi giữa các năm")


class TrendResponse(BaseModel):
    metric: str
    component: str | None
    unit: str
    years: list[int]
    series: list[TrendSeries]
    warnings: list[str]


class RadarRow(BaseModel):
    code: str
    name: str
    values: dict[str, float | None] = Field(description="P_k theo ngân hàng")
    dbi: dict[str, float | None]
    dti: dict[str, float | None]


class CompareResponse(BaseModel):
    year: int
    banks: list[BankYear]
    radar: list[RadarRow]
    leaders: dict[str, list[str]] = Field(description="Ngân hàng dẫn đầu từng trụ cột (có thể đồng hạng)")


class GroupRow(BaseModel):
    year: int
    group: str
    banks: list[str]
    n_banks: int
    score_mean: float | None
    data_confidence_mean: float | None
    pillar_p_mean: dict[str, float | None]


class GroupResponse(BaseModel):
    items: list[GroupRow]
    note: str


class Evidence(BaseModel):
    file: str | None
    page: int | None
    url: str | None = Field(None, description="URL tài liệu gốc trong config/sources.csv (nếu có)")
    quote: str | None


class CriterionScore(BaseModel):
    criterion: str
    pillar: str
    pillar_name: str | None
    name: str | None
    bank: str
    year: int
    score: int | None = Field(description="Rubric 0–4; null nếu thiếu văn bản")
    score_pct: float | None = Field(description="score × 25")
    status: str = Field(description="scored | no_mention | no_document")
    status_label: str
    confidence: str | None = Field(description="Độ chắc chắn của thuật toán: high | low")
    features: list[str]
    evidence: Evidence | None
    note: str | None


class CriteriaResponse(BaseModel):
    bank: str
    year: int
    pillar: str | None
    count: int
    items: list[CriterionScore]


class DtiIndicator(BaseModel):
    bank: str
    year: int
    indicator: str
    pillar: str | None
    name: str | None
    unit: str | None
    direction: str | None
    x: float | None = Field(description="Giá trị thô")
    L: float | None
    U: float | None
    z: float | None = Field(description="Điểm chuẩn hóa 0–100; null nếu thiếu dữ liệu")
    status: str | None
    has_data: bool
    note: str | None


class DtiResponse(BaseModel):
    year: int
    bank: str | None
    pillar: str | None
    count: int
    items: list[DtiIndicator]


class Highlights(BaseModel):
    strongest_pillar: str | None
    weakest_pillar: str | None
    criteria_score_distribution: dict[str, int] = Field(description="Số tiêu chí theo mức rubric 0..4")


class BankDetail(BaseModel):
    summary: BankYear
    criteria: list[CriterionScore]
    dti_indicators: list[DtiIndicator]
    highlights: Highlights


class BankProfile(BaseModel):
    bank: str
    bank_name: str
    group: str | None
    latest: BankYear | None
    history: list[BankYear]


class AvailabilityRow(BaseModel):
    bank: str
    year: int
    bctn: str | None
    bctc: str | None
    bcptbv: str | None
    dti_inputs_total: int | None
    dti_inputs_confirmed: int | None
    dti_inputs_coverage: float | None
    dti_indicators_computable: int | None
    dti_indicators_list: list[str]
    data_confidence: float | None


class AppRating(BaseModel):
    bank: str
    date: str
    store: str | None
    title: str | None
    rating: float | None
    rating_count: int | None
    version: str | None


class DataFlag(BaseModel):
    bank: str
    year: int
    variable: str | None
    kind: str | None
    message: str | None


class DataQualityResponse(BaseModel):
    year: int | None
    bank: str | None
    availability: list[AvailabilityRow]
    app_ratings: list[AppRating]
    flags: list[DataFlag]
    note: str


class ScenarioCell(BaseModel):
    score: float | None
    rank: int | None
    level: str | None


class SensitivityRow(BaseModel):
    bank: str
    bank_name: str
    group: str | None
    by_scenario: dict[str, ScenarioCell]
    rank_stable_pct: float | None
    rank_min: int | None
    rank_max: int | None
    stable_under_weights: bool = Field(description="Chỉ xét kịch bản trọng số DBI/DTI; kết luận đầy đủ ở /sensitivity/full")


class Agreement(BaseModel):
    scenario: str
    kendall_tau: float | None
    spearman: float | None


class SensitivityResponse(BaseModel):
    year: int
    base_scenario: str
    scenarios: list[str]
    rows: list[SensitivityRow]
    agreement_with_base: list[Agreement]
    note: str


class Health(BaseModel):
    status: str
    api_version: str
    years: list[int]
    banks: list[str]
    files: dict[str, str | None]


# ---------------------------------------------------------------- số liệu đầu vào DTI kèm nguồn
class DtiInputRow(BaseModel):
    bank: str
    year: int
    variable: str
    value: float | None = Field(description="null = thiếu; xem missing_reason")
    unit: str | None
    source_file: str | None
    page: int | None = Field(description="Trang PDF đã đối chiếu")
    source_url: str | None
    confirmed: bool
    confirmed_by: str | None
    note: str | None
    definition: str | None
    missing_reason: str | None = Field(description="not_disclosed (đã tìm, không có) | not_collected (chưa thu thập) | null")
    used_by: list[str] = Field(description="Chỉ số DTI hoặc chỉ tiêu Lớp C dùng biến này")


class DtiInputsResponse(BaseModel):
    bank: str | None
    year: int | None
    indicator: str | None
    variable: str | None
    scope: str
    formula: str | None
    count: int
    items: list[DtiInputRow]
    other_sources: dict = Field(description="K-Q3: app_ratings; T-Q2: platform_checklist (8 nền tảng)")


# ---------------------------------------------------------------- cơ sở cận L/U
class ReferenceInput(BaseModel):
    variable: str | None
    year: int | None
    value: float | None
    unit: str | None
    source_file: str | None
    printed_page: str | None
    pdf_page: int | None
    source_url: str | None
    note: str | None


class BoundsItem(BaseModel):
    code: str
    pillar: str | None
    variable: str | None
    name: str | None
    unit: str | None
    direction: str | None
    L: float | None
    U: float | None
    status: str | None
    status_label: str | None
    formula: str | None
    source_citation: list[str]
    rationale: str | None
    caveat: str | None
    reference_inputs: list[ReferenceInput]


class BoundsResponse(BaseModel):
    version: str | None
    locked: bool | None
    locked_on: str | None
    calibration_method: str | None
    method_document: str | None
    normalization: str
    count: int
    items: list[BoundsItem]


# ---------------------------------------------------------------- Lớp C
class FinancialRow(BaseModel):
    bank: str
    bank_name: str
    group: str | None
    year: int
    roe: float | None
    roa: float | None
    cir: float | None
    casa: float | None
    non_interest_share: float | None
    dbi_mean: float | None = Field(description="DBI trung bình 6 trụ cột (0–100)")
    score: float | None
    data_confidence: float | None
    flags: list[str] = Field(description="Ghi chú tính toán: dùng số cuối kỳ, thiếu số liệu đầu vào ...")


class FinancialResponse(BaseModel):
    year: int | None
    bank: str | None
    count: int
    metrics: dict
    items: list[FinancialRow]
    note: str


class CorrBlock(BaseModel):
    n: int
    spearman: float | None = None
    kendall: float | None = None
    p_kendall: float | None = None
    low_n: bool | None = None
    consistent_with_expected: bool | None = None


class CorrYear(CorrBlock):
    year: int


class CorrMetric(BaseModel):
    metric: str
    name: str
    unit: str
    expected_sign: int | None
    by_year: list[CorrYear]
    pooled: CorrBlock
    pooled_within_year: CorrBlock


class CorrelationResponse(BaseModel):
    score_var: str
    lag: int
    method: str
    metrics: list[CorrMetric]
    notes: list[str]


# ---------------------------------------------------------------- độ nhạy đầy đủ (11_sensitivity.py)
class FamilyShare(BaseModel):
    family: str
    n_scenarios: int
    share: float | None


class RankProb(BaseModel):
    rank: int
    prob: float | None


class MonteCarlo(BaseModel):
    method: str
    p_base: float | None
    mean_rank: float | None
    rank_distribution: list[RankProb]


class SensBank(BaseModel):
    bank: str
    bank_name: str
    group: str | None
    base_score: float | None
    base_rank: int | None
    min_rank: int | None
    max_rank: int | None
    min_score: float | None
    max_score: float | None
    n_scenarios: int | None
    stable_share: float | None
    verdict: str | None
    is_robust: bool
    borderline: bool
    tier: str | None
    stable_by_family: list[FamilyShare]
    monte_carlo: list[MonteCarlo]


class SensPair(BaseModel):
    bank_a: str
    bank_b: str
    share_a_above: float | None
    share_b_above: float | None
    share_tie: float | None
    distinguishable: bool
    borderline: bool
    swapped_in_some_scenario: bool
    monte_carlo_a_above: dict[str, float | None]


class RankAgreement(BaseModel):
    family: str
    scenario: str
    kendall_tau: float | None
    spearman_rho: float | None
    n_rank_changes: int | None


class SensFullResponse(BaseModel):
    year: int
    available_years: list[int]
    robust_threshold: float
    n_discrete_scenarios: int
    banks: list[SensBank]
    pairs: list[SensPair]
    rank_agreement: list[RankAgreement]
    normalization: dict
    keyword_vs_rubric: list[dict]
    note: str


class ScenarioRow(BaseModel):
    year: int
    family: str
    scenario: str
    bank: str
    score: float | None
    rank: int | None
    base_rank: int | None
    rank_change: int | None


class ScenariosResponse(BaseModel):
    year: int
    available_years: list[int]
    count: int
    items: list[ScenarioRow]
