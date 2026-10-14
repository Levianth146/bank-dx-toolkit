"""Lỗi nghiệp vụ của API, trả về cùng một định dạng: {"error": {"code", "message"}}."""


class ApiError(Exception):
    def __init__(self, status: int, code: str, message: str):
        super().__init__(message)
        self.status, self.code, self.message = status, code, message


class DataNotReady(ApiError):
    def __init__(self, missing: str):
        super().__init__(
            503, "data_not_ready",
            f"Chưa có dữ liệu đầu ra: {missing}. Chạy `python 12_appendix.py --bundle` rồi "
            f"`python 10_score.py --years 2020,2021,2022,2023,2024,2025` trong thư mục scripts/.")
