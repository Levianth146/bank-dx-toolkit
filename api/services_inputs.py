"""Số liệu đầu vào DTI kèm nguồn (luật 4: mọi con số phải truy vết tới tệp, trang) và cơ sở của cận L/U."""
import re

import pandas as pd

from .definitions import (BOUNDS_STATUS_LABELS, INDICATOR_FORMULAS, INDICATOR_INPUTS, INDICATOR_LOOKBACK,
                          LAYER_C_INPUTS)
from .errors import ApiError
from .serialize import integer, num, py, text

_DOC_RE = re.compile(r"(\d{4})_([a-z]+)\.pdf$", re.I)


class InputsMixin:
    def _indicator(self, code):
        c = str(code).strip().upper()
        if c not in INDICATOR_INPUTS:
            raise ApiError(404, "indicator_not_found", f"Chỉ số '{code}' không tồn tại; hợp lệ: {list(INDICATOR_INPUTS)}.")
        return c

    def _used_by(self) -> dict:
        m: dict = {}
        for ind, vs in INDICATOR_INPUTS.items():
            for v in vs:
                m.setdefault(v, []).append(ind)
        for metric, vs in LAYER_C_INPUTS.items():
            for v in vs:
                m.setdefault(v, []).append(f"Lớp C: {metric}")
        return m

    def _doc_url(self, bank, source_file):
        m = _DOC_RE.search(source_file or "")
        return self._source_urls().get((bank, int(m.group(1)), m.group(2).lower())) if m else None

    # ------------------------------------------------------------------ số liệu đầu vào
    def dti_inputs(self, bank=None, year=None, indicator=None, variable=None, scope="confirmed") -> dict:
        """Dòng số liệu đầu vào kèm tệp nguồn, trang PDF, định nghĩa.

        - scope=confirmed: chỉ số đã đối chiếu PDF (đúng tập mà 10_score.py dùng). scope=all: thêm ô thiếu kèm lý do
          (not_disclosed = đã tìm và không có; not_collected = chưa thu thập).
        - Có `indicator`: trả đúng các biến cấu thành chỉ số đó; `year` là năm của chỉ số và API tự lấy thêm
          các năm trước mà công thức cần (bình quân, Δ, CAGR). Không có `indicator`: `year` lọc đúng năm đó.
        """
        if scope not in ("confirmed", "all"):
            raise ApiError(422, "invalid_scope", "scope phải là confirmed hoặc all.")
        bank = self._bank(bank) if bank else None
        year = self._year(year) if year is not None else None
        ind = self._indicator(indicator) if indicator else None
        df = (self.store.inputs_full() if scope == "all" else self.store.inputs_confirmed()).copy()
        df["bank"] = df["bank"].astype(str).str.strip().str.lower()
        df["year"] = df["year"].astype(int)
        df["is_confirmed"] = self.S.confirmed_mask(df)
        if scope == "confirmed":
            df = df[df["is_confirmed"]]
        if bank:
            df = df[df["bank"] == bank]
        if ind:
            df = df[df["variable"].isin(INDICATOR_INPUTS[ind])]
        if variable:
            df = df[df["variable"] == str(variable).strip()]
        if year is not None:
            back = INDICATOR_LOOKBACK.get(ind, 0) if ind else 0
            lo = df["year"].min() if back == "all" and len(df) else year - (back if isinstance(back, int) else 0)
            df = df[(df["year"] >= lo) & (df["year"] <= year)]
        used = self._used_by()
        items = []
        for r in df.sort_values(["bank", "variable", "year"]).itertuples(index=False):
            value, note = num(r.value, 6), text(r.note)
            reason = None
            if value is None and note:
                reason = "not_disclosed" if note.startswith("not_disclosed") else "not_collected" if note.startswith("not_collected") else None
            items.append(dict(
                bank=r.bank, year=int(r.year), variable=r.variable, value=value, unit=text(r.unit),
                source_file=text(r.source_file), page=integer(r.page), source_url=self._doc_url(r.bank, text(r.source_file)),
                confirmed=bool(r.is_confirmed), confirmed_by=text(r.confirmed_by), note=note,
                definition=text(r.definition), missing_reason=reason, used_by=used.get(r.variable, [])))
        other = {}
        if ind == "K-Q3":
            other["app_ratings"] = self.data_quality(bank=bank)["app_ratings"]
        if ind == "T-Q2":
            pa = self.store.platform_audit()
            rows = []
            for r in pa.to_dict("records"):
                if bank and str(r.get("bank")).lower() != bank:
                    continue
                rows.append(dict(bank=str(r.get("bank")).lower(), platform_no=integer(r.get("platform_no")),
                                 platform=text(r.get("platform")), achieved=integer(r.get("achieved(0/1)")),
                                 evidence=text(r.get("screenshot_or_url")), audit_date=text(r.get("audit_date")),
                                 tester=text(r.get("tester")), notes=text(r.get("notes"))))
            other["platform_checklist"] = rows
        return dict(bank=bank, year=year, indicator=ind, variable=variable, scope=scope,
                    formula=INDICATOR_FORMULAS.get(ind) if ind else None, count=len(items), items=items,
                    other_sources=other)

    # ------------------------------------------------------------------ cơ sở của cận L/U
    def dti_bounds(self, indicator=None) -> dict:
        cfg = self.store.bounds()
        if not cfg:
            raise ApiError(503, "data_not_ready", "Thiếu config/dti_bounds.yaml.")
        ref = self.store.bounds_reference()
        codes = [self._indicator(indicator)] if indicator else list(INDICATOR_INPUTS)
        pillar_of = {i: p for p, inds in self.DTI_BY_PILLAR.items() for i in inds}
        items = []
        for code in codes:
            b = (cfg.get("bounds") or {}).get(code) or {}
            refs = []
            if not ref.empty:
                for r in ref.itertuples(index=False):
                    if code in [x.strip() for x in str(r.indicator).split(";")]:
                        refs.append(dict(variable=text(r.variable), year=integer(r.year), value=num(r.value, 6), unit=text(r.unit),
                                         source_file=text(r.source_file), printed_page=text(r.printed_page),
                                         pdf_page=integer(r.pdf_page_1based), source_url=text(r.source_url), note=text(r.note)))
            st = text(b.get("status"))
            items.append(dict(
                code=code, pillar=pillar_of.get(code), variable=text(b.get("variable")), name=text(b.get("name")),
                unit=text(b.get("unit")), direction=text(b.get("direction")), L=num(b.get("L"), 6), U=num(b.get("U"), 6),
                status=st, status_label=BOUNDS_STATUS_LABELS.get(st, st), formula=INDICATOR_FORMULAS.get(code),
                source_citation=[str(c) for c in (b.get("source_citation") or [])], rationale=text(b.get("rationale")),
                caveat=text(b.get("caveat")), reference_inputs=refs))
        return dict(version=text(cfg.get("version")), locked=cfg.get("locked"), locked_on=text(cfg.get("locked_on")),
                    calibration_method=text(cfg.get("calibration_method")), method_document=text(cfg.get("method_document")),
                    normalization="z = 100·min{1; max[0; (x−L)/(U−L)]}; chỉ số nghịch: (U−x)/(U−L). L, U cố định trước khi chấm, không dùng MAX của 5 ngân hàng.",
                    count=len(items), items=items)
