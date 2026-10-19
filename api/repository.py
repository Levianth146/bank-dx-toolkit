"""Lớp đọc dữ liệu từ output_data/ và config/. Tự nạp lại khi tệp đổi (so sánh mtime) nên chạy lại 10_score.py
không cần khởi động lại server. Chỉ đọc, không bao giờ ghi vào output_data/."""
import json
import pathlib
import threading

import pandas as pd
import yaml

from .config import ROOT
from .errors import DataNotReady


class DataStore:
    def __init__(self, root: pathlib.Path | None = None):
        self.root = pathlib.Path(root) if root else ROOT
        self.out = self.root / "output_data"
        self.conf = self.root / "config"
        self._cache: dict[str, tuple[int, object]] = {}
        self._lock = threading.RLock()

    # ---- nền tảng ----
    def _load(self, path: pathlib.Path, reader, required=True, default=None):
        if not path.exists():
            if required:
                raise DataNotReady(str(path.relative_to(self.root)))
            return default
        key, mtime = str(path), path.stat().st_mtime_ns
        with self._lock:
            hit = self._cache.get(key)
            if hit and hit[0] == mtime:
                return hit[1]
            data = reader(path)
            self._cache[key] = (mtime, data)
            return data

    @staticmethod
    def _csv(path):
        return pd.read_csv(path, encoding="utf-8-sig")

    def mtime(self, rel: str):
        p = self.root / rel
        return p.stat().st_mtime if p.exists() else None

    # ---- kết quả chính thức của 10_score.py ----
    def summary(self) -> pd.DataFrame:
        return self._load(self.out / "score_summary.csv", self._csv)

    def scores(self) -> pd.DataFrame:
        return self._load(self.out / "scores.csv", self._csv)

    def indicators(self) -> pd.DataFrame:
        return self._load(self.out / "dti_indicators.csv", self._csv)

    def coding(self) -> pd.DataFrame:
        """Điểm DBI từng tiêu chí (coding_auto.xlsx, cột final = điểm chính thức, đúng như bước 10 đọc)."""
        def read(p):
            df = pd.read_excel(p)
            df["bank"] = df["bank"].astype(str).str.strip().str.lower()
            df["criterion"] = df["criterion"].astype(str).str.strip().str.upper()
            return df
        return self._load(self.out / "coding_auto.xlsx", read)

    # ---- dữ liệu phụ trợ (thiếu thì trả rỗng, không làm hỏng API) ----
    def availability(self) -> pd.DataFrame:
        return self._load(self.out / "availability_matrix.csv", self._csv, required=False, default=pd.DataFrame())

    def app_ratings(self) -> pd.DataFrame:
        return self._load(self.out / "app_ratings.csv", self._csv, required=False, default=pd.DataFrame())

    def dti_checks(self) -> pd.DataFrame:
        return self._load(self.out / "dti_check.csv", self._csv, required=False, default=pd.DataFrame())

    def sources(self) -> pd.DataFrame:
        return self._load(self.conf / "sources.csv", self._csv, required=False, default=pd.DataFrame())

    def manifest(self) -> dict:
        def read(p):
            with open(p, encoding="utf-8-sig") as f:
                return json.load(f)
        return self._load(self.out / "auto_scoring_manifest.json", read, required=False, default={})

    def bounds(self) -> dict:
        def read(p):
            with open(p, encoding="utf-8") as f:
                return yaml.safe_load(f)
        return self._load(self.conf / "dti_bounds.yaml", read, required=False, default={})

    def banks_cfg(self) -> dict:
        def read(p):
            with open(p, encoding="utf-8") as f:
                return yaml.safe_load(f)
        return self._load(self.conf / "banks.yaml", read, required=False, default={})

    # ---- số liệu đầu vào DTI/Lớp C (gói output_data/dataset_clean do 12_appendix.py --bundle tạo) ----
    def inputs_confirmed(self) -> pd.DataFrame:
        return self._load(self.out / "dataset_clean" / "dti_inputs_confirmed.csv", self._csv)

    def inputs_full(self) -> pd.DataFrame:
        return self._load(self.out / "dataset_clean" / "dti_inputs_full.csv", self._csv)

    def platform_audit(self) -> pd.DataFrame:
        return self._load(self.out / "manual_audit.xlsx", pd.read_excel, required=False, default=pd.DataFrame())

    def bounds_reference(self) -> pd.DataFrame:
        """Số liệu tham chiếu ngoài dùng suy ra cận L/U (output_data/dti_bounds_review_*/reference_inputs.csv)."""
        parts = [self._load(p, self._csv) for p in sorted(self.out.glob("dti_bounds_review_*/reference_inputs.csv"))]
        return pd.concat(parts, ignore_index=True) if parts else pd.DataFrame()

    # ---- kết quả 11_sensitivity.py (output_data/sensitivity/sens_<tên>.csv); thiếu thì trả rỗng ----
    def sens(self, name: str) -> pd.DataFrame:
        return self._load(self.out / "sensitivity" / f"sens_{name}.csv", self._csv, required=False, default=pd.DataFrame())
