"""FastAPI cho dashboard DBI–DTI.   Chạy từ thư mục gốc repo:

    pip install -r requirements-api.txt
    uvicorn api.main:app --reload --port 8000        # tài liệu tương tác: http://localhost:8000/docs

Biến môi trường:
    DX_CORS_ORIGINS   danh sách origin cho phép, cách nhau bằng dấu phẩy (mặc định '*': dữ liệu công khai, chỉ đọc)
    DX_ROOT           đường dẫn gốc repo nếu chạy ở nơi khác
"""
import datetime as dt
import os

from fastapi import APIRouter, FastAPI, Query, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse

from . import __version__, schemas as sch
from .config import API_PREFIX
from .errors import ApiError
from .services import DxService

service = DxService()

app = FastAPI(
    title="Bank DX Toolkit API",
    version=__version__,
    description=("API chỉ đọc cho dashboard mức độ trưởng thành chuyển đổi số của 5 ngân hàng "
                 "(Agribank, BIDV, Vietcombank, MB, Techcombank) theo mô hình DBI 80% + DTI 20%, giai đoạn 2020–2025. "
                 "Giá trị null = thiếu dữ liệu, không phải 0."),
)
_origins = [o.strip() for o in os.environ.get("DX_CORS_ORIGINS", "*").split(",") if o.strip()]
app.add_middleware(CORSMiddleware, allow_origins=_origins, allow_methods=["GET"], allow_headers=["*"],
                   allow_credentials=False)


@app.exception_handler(ApiError)
async def _api_error(_: Request, e: ApiError):
    return JSONResponse(status_code=e.status, content={"error": {"code": e.code, "message": e.message}})


@app.exception_handler(RequestValidationError)
async def _validation_error(_: Request, e: RequestValidationError):
    detail = "; ".join(f"{'.'.join(str(x) for x in err['loc'][1:])}: {err['msg']}" for err in e.errors())
    return JSONResponse(status_code=422, content={"error": {"code": "invalid_request", "message": detail}})


@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse("/docs")


r = APIRouter(prefix=API_PREFIX)
YEAR = Query(None, ge=2000, le=2100, description="Năm; bỏ trống = năm mới nhất có dữ liệu")


@r.get("/health", response_model=sch.Health, tags=["Hệ thống"])
def health():
    st = service.store
    files = {n: (dt.datetime.fromtimestamp(st.mtime(f"out/{n}"), dt.timezone.utc).isoformat()
                 if st.mtime(f"out/{n}") else None)
             for n in ("score_summary.csv", "scores.csv", "dti_indicators.csv", "coding_auto.xlsx")}
    return dict(status="ok", api_version=__version__, years=service.years(), banks=service.bank_ids(), files=files)


@r.get("/meta", tags=["Hệ thống"], summary="Danh mục ngân hàng, năm, trụ cột, 24 tiêu chí, 11 chỉ số DTI, 5 mức")
def meta():
    return service.meta()


@r.get("/snapshot", tags=["Hệ thống"], summary="Toàn bộ điểm 5 NH × 6 năm trong một lần gọi")
def snapshot():
    return service.snapshot()


@r.get("/ranking", response_model=sch.RankingResponse, tags=["Dashboard"], summary="Bảng xếp hạng một năm")
def ranking(year: int | None = YEAR,
            sort_by: str = Query("rank", description="rank | score | bank | K | S | T | O | C | D"),
            order: str | None = Query(None, description="asc | desc (mặc định theo sort_by)")):
    return service.ranking(year, sort_by, order)


@r.get("/trend", response_model=sch.TrendResponse, tags=["Dashboard"], summary="Xu hướng theo năm (biểu đồ đường)")
def trend(banks: str | None = Query(None, description="Ví dụ tcb,mb; bỏ trống = cả 5 ngân hàng"),
          metric: str = Query("score", description="score | data_confidence | K | S | T | O | C | D"),
          component: str = Query("p", description="p | dbi | dti (chỉ áp dụng khi metric là trụ cột)"),
          from_year: int | None = Query(None, ge=2000, le=2100), to_year: int | None = Query(None, ge=2000, le=2100)):
    return service.trend(banks, metric, component, from_year, to_year)


@r.get("/compare", response_model=sch.CompareResponse, tags=["Dashboard"], summary="So sánh ngân hàng (radar 6 trụ cột)")
def compare(year: int | None = YEAR, banks: str | None = Query(None, description="Ví dụ tcb,vcb,mb")):
    return service.compare(year, banks)


@r.get("/group-comparison", response_model=sch.GroupResponse, tags=["Dashboard"],
       summary="Trung bình nhóm NHTM Nhà nước và NHTM Cổ phần")
def group_comparison(year: int | None = Query(None, ge=2000, le=2100, description="Bỏ trống = mọi năm")):
    return service.group_comparison(year)


@r.get("/banks", tags=["Ngân hàng"], summary="Danh sách ngân hàng")
def banks():
    return service.meta()["banks"]


@r.get("/banks/{bank}", response_model=sch.BankProfile, tags=["Ngân hàng"], summary="Hồ sơ và lịch sử điểm một ngân hàng")
def bank_profile(bank: str):
    return service.bank_profile(bank)


@r.get("/banks/{bank}/{year}", response_model=sch.BankDetail, tags=["Ngân hàng"],
       summary="Chi tiết điểm thành phần: 6 trụ cột, 24 tiêu chí kèm bằng chứng, 11 chỉ số DTI")
def bank_detail(bank: str, year: int,
                include_quote: bool = Query(True, description="false để bỏ đoạn trích bằng chứng, nhẹ hơn")):
    return service.bank_detail(bank, year, include_quote)


@r.get("/banks/{bank}/{year}/criteria", response_model=sch.CriteriaResponse, tags=["Ngân hàng"],
       summary="24 tiêu chí DBI, lọc theo trụ cột")
def criteria(bank: str, year: int, pillar: str | None = Query(None, description="K|S|T|O|C|D"),
             include_quote: bool = True):
    return service.criteria(bank, year, pillar, include_quote)


@r.get("/dti-indicators", response_model=sch.DtiResponse, tags=["Chỉ số"], summary="11 chỉ số DTI (x, L, U, z)")
def dti_indicators(year: int | None = YEAR, bank: str | None = None, pillar: str | None = Query(None, description="K|S|T|O|C")):
    return service.dti_indicators(year, bank, pillar)


@r.get("/data-quality", response_model=sch.DataQualityResponse, tags=["Chỉ số"],
       summary="Độ phủ dữ liệu, rating app, cảnh báo kiểm tra DTI")
def data_quality(year: int | None = YEAR, bank: str | None = None):
    return service.data_quality(year, bank)


@r.get("/dti-inputs", response_model=sch.DtiInputsResponse, tags=["Chỉ số"],
       summary="Số liệu đầu vào DTI kèm tệp nguồn, trang PDF, định nghĩa (truy vết)")
def dti_inputs(bank: str | None = None, year: int | None = Query(None, ge=2000, le=2100),
               indicator: str | None = Query(None, description="Ví dụ T-Q1; trả biến cấu thành, tự lấy các năm công thức cần"),
               variable: str | None = Query(None, description="Ví dụ total_assets"),
               scope: str = Query("confirmed", description="confirmed | all (all thêm ô thiếu kèm lý do)")):
    return service.dti_inputs(bank, year, indicator, variable, scope)


@r.get("/dti-bounds", response_model=sch.BoundsResponse, tags=["Chỉ số"],
       summary="Cận L/U của 11 chỉ số: nguồn trích dẫn, lý do chọn, hạn chế, số liệu tham chiếu")
def dti_bounds():
    return service.dti_bounds()


@r.get("/dti-bounds/{indicator}", response_model=sch.BoundsResponse, tags=["Chỉ số"], summary="Cận L/U của một chỉ số")
def dti_bound(indicator: str):
    return service.dti_bounds(indicator)


@r.get("/financial-performance", response_model=sch.FinancialResponse, tags=["Lớp C"],
       summary="ROE, ROA, CIR, CASA, thu nhập ngoài lãi theo ngân hàng–năm, kèm điểm (cho biểu đồ phân tán)")
def financial_performance(year: int | None = Query(None, ge=2000, le=2100), bank: str | None = None,
                          score_var: str = Query("dbi", description="dbi | score")):
    return service.financial_performance(year, bank, score_var)


@r.get("/layer-c/correlation", response_model=sch.CorrelationResponse, tags=["Lớp C"],
       summary="Tương quan hạng (Spearman, Kendall) giữa điểm chuyển đổi số và ROE, ROA, CIR, CASA")
def layer_c_correlation(score_var: str = Query("dbi", description="dbi (mặc định, độc lập với BCTC) | score"),
                        lag: int = Query(0, description="0 = cùng năm; 1 = điểm năm t so với chỉ tiêu năm t+1")):
    return service.layer_c_correlation(score_var, lag)


@r.get("/sensitivity", response_model=sch.SensitivityResponse, tags=["Phân tích"],
       summary="Độ nhạy NHANH theo trọng số DBI/DTI (100/0, 80/20, 70/30, 60/40), mọi năm")
def sensitivity(year: int | None = YEAR):
    return service.sensitivity(year)


@r.get("/sensitivity/full", response_model=sch.SensFullResponse, tags=["Phân tích"],
       summary="Độ nhạy ĐẦY ĐỦ từ 11_sensitivity.py: Vững / Nhóm cùng mức, Monte Carlo, chuẩn hóa, cận L/U")
def sensitivity_full(year: int | None = Query(None, ge=2000, le=2100, description="Chỉ các năm đã chạy 11_sensitivity.py; bỏ trống = năm mới nhất")):
    return service.sensitivity_full(year)


@r.get("/sensitivity/scenarios", response_model=sch.ScenariosResponse, tags=["Phân tích"],
       summary="Bảng dài từng kịch bản × ngân hàng (điểm, hạng)")
def sensitivity_scenarios(year: int | None = Query(None, ge=2000, le=2100), family: str | None = Query(None, description="Tiền tố họ kịch bản, ví dụ A hoặc 'G.'"),
                          bank: str | None = None):
    return service.sensitivity_scenarios(year, family, bank)


app.include_router(r)
