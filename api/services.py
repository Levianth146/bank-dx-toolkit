"""Logic nghiệp vụ của API: biến các tệp trong out/ thành cấu trúc JSON cho dashboard.

Quy ước dữ liệu (theo AGENTS.md và specs/001-bank-dx-assessment):
  - Mọi điểm theo thang 0–100; data_confidence theo thang 0–1 (= số chỉ số DTI có dữ liệu / 11).
  - Ô thiếu = null. Không bao giờ đổi thiếu dữ liệu thành 0.
  - final = 0 với status `no_mention` nghĩa là thuật toán không tìm thấy đề cập trong tài liệu đã quét,
    KHÔNG có nghĩa ngân hàng không công bố (luật 3b) -> nhãn hiển thị được viết đúng như vậy.
  - Thiếu DTI của trụ cột thì P_k = DBI_k; trụ cột D không có DTI.
"""
import datetime as dt
import math
import re

import numpy as np
import pandas as pd

from . import __version__
from .config import (BANK_GROUPS, DTI_TOTAL, MATURITY_LEVELS, RELIABILITY_HIGH, RELIABILITY_MEDIUM,
                     W_DBI_BASE, WEIGHT_SCENARIOS, scoring)
from .errors import ApiError
from .repository import DataStore
from .serialize import integer, num, py, text
from .definitions import INDICATOR_FORMULAS, INDICATOR_INPUTS
from .services_inputs import InputsMixin
from .services_layerc import LayerCMixin
from .services_sens import SensitivityMixin

STATUS_LABELS = {
    "scored": "Đã chấm theo quy tắc thuật toán",
    "no_mention": "Thuật toán không tìm thấy đề cập trong tài liệu đã quét (không đồng nghĩa ngân hàng không công bố)",
    "no_document": "Thiếu văn bản đọc được; để trống",
}
_LEVEL_RE = re.compile(r"Mức\s*(\d+)\s*-\s*(.+)")
_DOC_RE = re.compile(r"(\d{4})_([a-z]+)\.pdf$", re.I)


def _kendall_tau(x, y):
    """Kendall tau-b cho hai dãy hạng (n nhỏ). None nếu một dãy hằng."""
    n, conc, disc, tx, ty = len(x), 0, 0, 0, 0
    for i in range(n):
        for j in range(i + 1, n):
            a, b = np.sign(x[i] - x[j]), np.sign(y[i] - y[j])
            if a == 0 and b == 0:
                continue
            if a == 0:
                tx += 1
            elif b == 0:
                ty += 1
            elif a == b:
                conc += 1
            else:
                disc += 1
    denom = math.sqrt((conc + disc + tx) * (conc + disc + ty))
    return None if denom == 0 else (conc - disc) / denom


class DxService(InputsMixin, LayerCMixin, SensitivityMixin):
    def __init__(self, store: DataStore | None = None):
        self.store = store or DataStore()
        self.S = scoring()                       # hằng số/hàm của 10_score.py
        self.PILLARS = self.S.PILLARS            # {"K": "Khách hàng", ...}
        self.DTI_BY_PILLAR = self.S.DTI_BY_PILLAR

    # ------------------------------------------------------------------ tiện ích
    def years(self) -> list[int]:
        return sorted(int(y) for y in self.store.summary()["year"].unique())

    def bank_ids(self) -> list[str]:
        return sorted(self.store.summary()["bank"].astype(str).str.lower().unique())

    def _year(self, year):
        ys = self.years()
        if year is None:
            return ys[-1]
        if year not in ys:
            raise ApiError(422, "invalid_year", f"Năm {year} không có trong dữ liệu; các năm hợp lệ: {ys}.")
        return int(year)

    def _bank(self, bank):
        b = str(bank).strip().lower()
        if b not in self.bank_ids():
            raise ApiError(404, "bank_not_found", f"Không có ngân hàng '{bank}'; hợp lệ: {self.bank_ids()}.")
        return b

    def _banks(self, banks):
        """banks: None | 'tcb,mb' | list -> danh sách id hợp lệ (giữ thứ tự, bỏ trùng)."""
        if banks is None or banks == "":
            return self.bank_ids()
        raw = banks.split(",") if isinstance(banks, str) else list(banks)
        out = []
        for b in raw:
            if str(b).strip():
                bid = self._bank(b)
                if bid not in out:
                    out.append(bid)
        return out

    def _pillar(self, code):
        c = str(code).strip().upper()
        if c not in self.PILLARS:
            raise ApiError(422, "invalid_pillar", f"Trụ cột '{code}' không hợp lệ; hợp lệ: {list(self.PILLARS)}.")
        return c

    def bank_name(self, bank):
        cfg = (self.store.banks_cfg().get("banks") or {}).get(bank) or {}
        return cfg.get("name") or bank.upper()

    @staticmethod
    def _level(label):
        m = _LEVEL_RE.match(label or "")
        return (int(m.group(1)), m.group(2).strip()) if m else (None, None)

    @staticmethod
    def reliability(conf):
        if conf is None:
            return None
        return "high" if conf >= RELIABILITY_HIGH else "medium" if conf >= RELIABILITY_MEDIUM else "low"

    # ------------------------------------------------------------------ bản ghi ngân hàng–năm
    def _records(self) -> dict:
        """{(bank, year): bản ghi đầy đủ} ghép từ score_summary.csv + scores.csv."""
        summ, sc = self.store.summary(), self.store.scores()
        pill: dict = {}
        for r in sc.itertuples(index=False):
            key = (str(r.bank).lower(), int(r.year))
            dbi, dti, p = num(r.dbi), num(r.dti), num(r.p)
            pill.setdefault(key, {})[r.pillar] = dict(
                code=r.pillar, name=self.PILLARS.get(r.pillar, r.pillar), dbi=dbi, dti=dti, p=p,
                n_dti=int(r.n_dti), n_dti_total=len(self.DTI_BY_PILLAR[r.pillar]), dti_applied=dti is not None)
        recs = {}
        for r in summ.itertuples(index=False):
            bank, year = str(r.bank).lower(), int(r.year)
            conf = num(r.data_confidence)
            n_avail = int(round(conf * DTI_TOTAL)) if conf is not None else None
            lvl_no, lvl_name = self._level(text(r.maturity_level))
            warns = []
            if conf is not None and conf < RELIABILITY_MEDIUM:
                warns.append(f"Chỉ {n_avail}/{DTI_TOTAL} chỉ số DTI có dữ liệu; điểm chủ yếu dựa trên DBI.")
            recs[(bank, year)] = dict(
                bank=bank, bank_name=self.bank_name(bank), group=BANK_GROUPS.get(bank), year=year,
                score=num(r.score), rank=integer(r.rank), maturity_level=text(r.maturity_level),
                maturity_level_number=lvl_no, maturity_level_name=lvl_name, data_confidence=conf,
                dti_indicators_available=n_avail, dti_indicators_total=DTI_TOTAL,
                reliability=self.reliability(conf), warnings=warns,
                pillars=pill.get((bank, year), {}))
        return recs

    # ------------------------------------------------------------------ meta
    def meta(self) -> dict:
        man, bnd = self.store.manifest(), self.store.bounds()
        coding = self.store.coding()
        crit_names = (coding[["criterion", "criterion_name"]].drop_duplicates("criterion")
                      .set_index("criterion")["criterion_name"].to_dict())
        banks_cfg = self.store.banks_cfg().get("banks") or {}
        pillars = []
        for p, name in self.PILLARS.items():
            pillars.append(dict(
                code=p, name=name,
                criteria=[dict(code=c, name=text(crit_names.get(c))) for c in self.S.CRITERIA if c[0] == p],
                dti_indicators=list(self.DTI_BY_PILLAR[p])))
        b_all = bnd.get("bounds") or {}
        dti = []
        for p, inds in self.DTI_BY_PILLAR.items():
            for i in inds:
                b = b_all.get(i) or {}
                dti.append(dict(code=i, pillar=p, name=text(b.get("name")), unit=text(b.get("unit")),
                                direction=b.get("direction", "higher_better"),
                                L=num(b.get("L")), U=num(b.get("U")), bounds_status=text(b.get("status")),
                                formula=INDICATOR_FORMULAS.get(i), input_variables=list(INDICATOR_INPUTS.get(i, []))))
        mt = [m for m in (self.store.mtime("out/score_summary.csv"), self.store.mtime("out/scores.csv")) if m]
        return dict(
            api_version=__version__,
            framework=dict(dbi_weight=W_DBI_BASE, dti_weight=round(1 - W_DBI_BASE, 2), pillars=len(self.PILLARS),
                           criteria=len(self.S.CRITERIA), dti_indicators=DTI_TOTAL, scale="0-100",
                           pillar_formula="P_k = 0,8*DBI_k + 0,2*DTI_k; thiếu DTI thì P_k = DBI_k",
                           score_formula="Score_Bank = (1/6) * sum(P_k)"),
            banks=[dict(id=b, name=self.bank_name(b), group=BANK_GROUPS.get(b),
                        site=text((banks_cfg.get(b) or {}).get("site"))) for b in self.bank_ids()],
            years=self.years(), latest_year=self.years()[-1], pillars=pillars, dti_indicators=dti,
            maturity_levels=[dict(m, label=f"Mức {m['number']} - {m['name']}") for m in MATURITY_LEVELS],
            scoring=dict(method=text(man.get("scoring_method")), rules_version=text(man.get("rules_version")),
                         rules_hash=text(man.get("rules_hash"))),
            dti_bounds=dict(version=text(bnd.get("version")), locked=bnd.get("locked"),
                            locked_on=text(bnd.get("locked_on"))),
            reliability_rule=dict(high=RELIABILITY_HIGH, medium=RELIABILITY_MEDIUM,
                                  note="Quy ước hiển thị theo data_confidence (= số chỉ số DTI có dữ liệu / 11); không ảnh hưởng điểm."),
            data_updated_at=dt.datetime.fromtimestamp(max(mt), dt.timezone.utc).isoformat() if mt else None)

    # ------------------------------------------------------------------ bảng xếp hạng
    def ranking(self, year=None, sort_by="rank", order=None) -> dict:
        year = self._year(year)
        recs = self._records()
        sort_by = str(sort_by)
        key = sort_by.upper() if len(sort_by) == 1 else sort_by.lower()
        if key not in {"rank", "score", "bank", *self.PILLARS}:
            raise ApiError(422, "invalid_sort", f"sort_by '{sort_by}' không hợp lệ (rank|score|bank|K|S|T|O|C|D).")
        order = order or ("asc" if key in ("rank", "bank") else "desc")
        if order not in ("asc", "desc"):
            raise ApiError(422, "invalid_order", "order phải là asc hoặc desc.")
        items = []
        for b in self.bank_ids():
            r = recs.get((b, year))
            if not r:
                continue
            r = dict(r)
            prev = recs.get((b, year - 1))
            r["score_change"] = num(r["score"] - prev["score"]) if prev and None not in (r["score"], prev["score"]) else None
            r["rank_change"] = (prev["rank"] - r["rank"]) if prev and None not in (r["rank"], prev["rank"]) else None
            items.append(r)

        def sk(r):
            v = {"rank": r["rank"], "score": r["score"], "bank": r["bank"]}.get(key)
            if key in self.PILLARS:
                v = r["pillars"].get(key, {}).get("p")
            return (v is None, v if v is not None else 0)
        items.sort(key=sk, reverse=(order == "desc"))
        if order == "desc":                      # None luôn xuống cuối dù đảo chiều
            items.sort(key=lambda r: sk(r)[0])
        return dict(year=year, count=len(items), sort_by=key, order=order,
                    scoring_method=text(self.store.manifest().get("scoring_method")),
                    rules_version=text(self.store.manifest().get("rules_version")), items=items)

    # ------------------------------------------------------------------ xu hướng
    def trend(self, banks=None, metric="score", component="p", from_year=None, to_year=None) -> dict:
        ids, recs, years = self._banks(banks), self._records(), self.years()
        m = str(metric)
        m = m.upper() if len(m) == 1 else m.lower()
        if m not in {"score", "data_confidence", *self.PILLARS}:
            raise ApiError(422, "invalid_metric", f"metric '{metric}' không hợp lệ (score|data_confidence|K|S|T|O|C|D).")
        component = str(component).lower()
        if component not in ("p", "dbi", "dti"):
            raise ApiError(422, "invalid_component", "component phải là p, dbi hoặc dti (chỉ áp dụng cho trụ cột).")
        lo, hi = from_year or years[0], to_year or years[-1]
        if lo > hi:
            raise ApiError(422, "invalid_range", "from_year phải nhỏ hơn hoặc bằng to_year.")
        sel = [y for y in years if lo <= y <= hi]
        series, any_change = [], False
        for b in ids:
            pts, cov = [], set()
            for y in sel:
                r = recs.get((b, y))
                if not r:
                    continue
                if m == "score":
                    v, n = r["score"], r["dti_indicators_available"]
                elif m == "data_confidence":
                    v, n = r["data_confidence"], r["dti_indicators_available"]
                else:
                    pil = r["pillars"].get(m, {})
                    v, n = pil.get(component), pil.get("n_dti")
                cov.add(n)
                pts.append(dict(year=y, value=v, rank=r["rank"], maturity_level_number=r["maturity_level_number"],
                                data_confidence=r["data_confidence"], n_dti=n))
            uses_dti = m == "score" or (m in self.PILLARS and component == "p")
            changes = uses_dti and len(cov) > 1
            any_change |= changes
            series.append(dict(bank=b, bank_name=self.bank_name(b), group=BANK_GROUPS.get(b),
                               points=pts, dti_coverage_changes=changes))
        unit = "độ tin cậy 0–1" if m == "data_confidence" else "điểm 0–100"
        warnings = []
        if any_change:
            warnings.append("Số chỉ số DTI có dữ liệu thay đổi giữa các năm (P_k = DBI_k khi thiếu DTI), "
                            "nên chênh lệch điểm giữa các năm có thể một phần do độ phủ dữ liệu; xem n_dti và data_confidence.")
        return dict(metric=m, component=component if m in self.PILLARS else None, unit=unit,
                    years=sel, series=series, warnings=warnings)

    # ------------------------------------------------------------------ so sánh
    def compare(self, year=None, banks=None) -> dict:
        year, ids, recs = self._year(year), None, self._records()
        ids = self._banks(banks)
        rows = [recs[(b, year)] for b in ids if (b, year) in recs]
        radar = []
        for p, name in self.PILLARS.items():
            radar.append(dict(code=p, name=name, values={r["bank"]: r["pillars"].get(p, {}).get("p") for r in rows},
                              dbi={r["bank"]: r["pillars"].get(p, {}).get("dbi") for r in rows},
                              dti={r["bank"]: r["pillars"].get(p, {}).get("dti") for r in rows}))
        leaders = {}
        for p in self.PILLARS:
            vals = [(r["pillars"].get(p, {}).get("p"), r["bank"]) for r in rows]
            vals = [v for v in vals if v[0] is not None]
            if vals:
                top = max(v[0] for v in vals)
                leaders[p] = sorted(b for v, b in vals if v == top)
        return dict(year=year, banks=rows, radar=radar, leaders=leaders)

    # ------------------------------------------------------------------ nhóm NHTM Nhà nước / Cổ phần
    def group_comparison(self, year=None) -> dict:
        recs = self._records()
        years = [self._year(year)] if year is not None else self.years()
        rows = []
        for y in years:
            for g in sorted({v for v in BANK_GROUPS.values()}):
                members = [recs[(b, y)] for b in self.bank_ids() if BANK_GROUPS.get(b) == g and (b, y) in recs]
                if not members:
                    continue

                def mean(vals):
                    vals = [v for v in vals if v is not None]
                    return num(sum(vals) / len(vals)) if vals else None
                rows.append(dict(
                    year=y, group=g, banks=[m["bank"] for m in members], n_banks=len(members),
                    score_mean=mean([m["score"] for m in members]),
                    data_confidence_mean=mean([m["data_confidence"] for m in members]),
                    pillar_p_mean={p: mean([m["pillars"].get(p, {}).get("p") for m in members]) for p in self.PILLARS}))
        return dict(items=rows, note="Trung bình giản đơn theo nhóm với số ngân hàng rất nhỏ (3 và 2): chỉ mang tính mô tả.")

    # ------------------------------------------------------------------ 24 tiêu chí DBI
    def _source_urls(self) -> dict:
        s = self.store.sources()
        if s.empty:
            return {}
        s = s.dropna(subset=["url"])
        return {(str(r.bank).lower(), int(r.year), str(r.doc_type).lower()): str(r.url) for r in s.itertuples(index=False)}

    def criteria(self, bank, year=None, pillar=None, include_quote=True) -> dict:
        bank, year = self._bank(bank), self._year(year)
        pil = self._pillar(pillar) if pillar else None
        c = self.store.coding()
        c = c[(c["bank"] == bank) & (c["year"].astype(int) == year)]
        urls, items = self._source_urls(), []
        order = {k: i for i, k in enumerate(self.S.CRITERIA)}
        for r in sorted(c.itertuples(index=False), key=lambda r: order.get(r.criterion, 99)):
            if pil and r.criterion[0] != pil:
                continue
            final = integer(r.final)
            status = text(r.status) or ("no_document" if final is None else "scored")
            if final is None:
                status = "no_document"
            ev_file, ev_page = text(r.evidence_file), integer(r.evidence_page)
            m = _DOC_RE.search(ev_file or "")
            ev_url = urls.get((bank, int(m.group(1)), m.group(2).lower())) if m else None
            feats = text(r.features)
            items.append(dict(
                criterion=r.criterion, pillar=r.criterion[0], pillar_name=self.PILLARS.get(r.criterion[0]),
                name=text(r.criterion_name), bank=bank, year=year, score=final,
                score_pct=None if final is None else final / 4 * 100, status=status,
                status_label=STATUS_LABELS.get(status, status), confidence=text(r.confidence),
                features=[f for f in (feats or "").split(",") if f],
                evidence=dict(file=ev_file, page=ev_page, url=ev_url,
                              quote=text(r.evidence_quote) if include_quote else None) if ev_file else None,
                note=text(r.note)))
        return dict(bank=bank, year=year, pillar=pil, count=len(items), items=items)

    # ------------------------------------------------------------------ 11 chỉ số DTI
    def dti_indicators(self, year=None, bank=None, pillar=None) -> dict:
        year = self._year(year)
        bank = self._bank(bank) if bank else None
        pil = self._pillar(pillar) if pillar else None
        ind = self.store.indicators()
        ind = ind[ind["year"].astype(int) == year]
        if bank:
            ind = ind[ind["bank"].astype(str).str.lower() == bank]
        meta = {d["code"]: d for d in self.meta()["dti_indicators"]}
        order = {k: i for i, k in enumerate(self.S.ALL_DTI)}
        items = []
        for r in sorted(ind.itertuples(index=False), key=lambda r: (str(r.bank), order.get(r.indicator, 99))):
            m = meta.get(r.indicator, {})
            if pil and m.get("pillar") != pil:
                continue
            items.append(dict(
                bank=str(r.bank).lower(), year=int(r.year), indicator=r.indicator, pillar=m.get("pillar"),
                name=m.get("name"), unit=m.get("unit"), direction=text(r.direction), x=num(r.x), L=num(r.L), U=num(r.U),
                z=num(r.z), status=text(r.status), has_data=py(r.z) is not None, note=text(r.note)))
        return dict(year=year, bank=bank, pillar=pil, count=len(items), items=items)

    # ------------------------------------------------------------------ chi tiết một ngân hàng–năm
    def bank_detail(self, bank, year=None, include_quote=True) -> dict:
        bank, year = self._bank(bank), self._year(year)
        recs = self._records()
        rec = recs.get((bank, year))
        if not rec:
            raise ApiError(404, "no_data", f"Không có dữ liệu {bank} năm {year}.")
        crit = self.criteria(bank, year, include_quote=include_quote)["items"]
        dist = {str(k): 0 for k in range(5)}
        for c in crit:
            if c["score"] is not None:
                dist[str(c["score"])] += 1
        with_p = {p: v["p"] for p, v in rec["pillars"].items() if v.get("p") is not None}
        hl = dict(strongest_pillar=max(with_p, key=with_p.get) if with_p else None,
                  weakest_pillar=min(with_p, key=with_p.get) if with_p else None,
                  criteria_score_distribution=dist)
        return dict(summary=rec, criteria=crit, dti_indicators=self.dti_indicators(year=year, bank=bank)["items"],
                    highlights=hl)

    def bank_profile(self, bank) -> dict:
        bank = self._bank(bank)
        recs = self._records()
        hist = [recs[(bank, y)] for y in self.years() if (bank, y) in recs]
        return dict(bank=bank, bank_name=self.bank_name(bank), group=BANK_GROUPS.get(bank),
                    latest=hist[-1] if hist else None, history=hist)

    # ------------------------------------------------------------------ chất lượng dữ liệu
    def data_quality(self, year=None, bank=None) -> dict:
        year = self._year(year) if year is not None else None
        bank = self._bank(bank) if bank else None
        av = self.store.availability()
        rows = []
        for r in av.itertuples(index=False):
            b, y = str(r.bank).lower(), int(r.year)
            if (bank and b != bank) or (year and y != year):
                continue
            lst = text(r.dti_ind_list)
            rows.append(dict(
                bank=b, year=y, bctn=text(r.bctn), bctc=text(r.bctc), bcptbv=text(r.bcptbv),
                dti_inputs_total=integer(r.dti_vars_total), dti_inputs_confirmed=integer(r.dti_vars_confirmed),
                dti_inputs_coverage=num(r.inputs_coverage), dti_indicators_computable=integer(r.dti_ind_computable),
                dti_indicators_list=[x for x in (lst or "").split(";") if x], data_confidence=num(r.data_conf)))
        app = self.store.app_ratings()
        apps = []
        if not app.empty:
            app = app.copy()
            app["date"] = pd.to_datetime(app["date"], errors="coerce")
            for b, g in app.dropna(subset=["date"]).groupby(app["bank"].astype(str).str.lower()):
                if bank and b != bank:
                    continue
                g = g[g["date"] == g["date"].max()].drop_duplicates("store", keep="last")   # như 10_score.py
                for r in g.itertuples(index=False):
                    apps.append(dict(bank=b, date=r.date.date().isoformat(), store=text(r.store), title=text(r.title),
                                     rating=num(r.rating), rating_count=integer(r.rating_count), version=text(r.version)))
        flags = []
        chk = self.store.dti_checks()
        for r in chk.itertuples(index=False):
            b, y = str(r.bank).lower(), int(r.year)
            if (bank and b != bank) or (year and y != year):
                continue
            flags.append(dict(bank=b, year=y, variable=text(r.variable), kind=text(r.kind), message=text(r.message)))
        return dict(year=year, bank=bank, availability=rows, app_ratings=apps, flags=flags,
                    note="K-Q3 (rating) và T-Q2 (8 nền tảng) chỉ áp dụng cho năm cuối của lần chạy; ô thiếu để trống, không điền 0.")

    # ------------------------------------------------------------------ độ nhạy trọng số DBI/DTI
    def sensitivity(self, year=None) -> dict:
        year = self._year(year)
        S = self.S
        sc = self.store.scores()
        sc = sc[sc["year"].astype(int) == year]
        base_label = f"{int(W_DBI_BASE * 100)}/{int(round((1 - W_DBI_BASE) * 100))}"
        labels = [f"{int(w * 100)}/{int(round((1 - w) * 100))}" for w in WEIGHT_SCENARIOS]
        per: dict = {}           # scenario -> bank -> (score, level)
        for w, lab in zip(WEIGHT_SCENARIOS, labels):
            for b, g in sc.groupby(sc["bank"].astype(str).str.lower()):
                pk = {}
                for r in g.itertuples(index=False):
                    dbi, dti = py(r.dbi), py(r.dti)
                    # Quy tắc P_k của 10_score.pillar_scores: thiếu DTI -> P_k = DBI_k
                    p = None if dbi is None else (dbi if dti is None else w * dbi + (1 - w) * dti)
                    pk[r.pillar] = (dbi, dti, p, 0)
                score = S.score_total(pk)
                per.setdefault(lab, {})[b] = (score, S.maturity(score) if score is not None else None)
        ranks: dict = {}
        for lab in labels:
            s = pd.Series({b: v[0] for b, v in per[lab].items()}, dtype="float64")
            ranks[lab] = S.rank_desc(s).to_dict()
        base_rank = ranks[base_label]
        alt = [l for l in labels if l != base_label]
        rows = []
        for b in sorted(per[base_label]):
            by = {lab: dict(score=num(per[lab][b][0]), rank=integer(ranks[lab].get(b)), level=per[lab][b][1])
                  for lab in labels}
            same = [by[l]["rank"] == by[base_label]["rank"] for l in alt]
            pct = sum(same) / len(same) if same else None
            rk = [by[l]["rank"] for l in labels if by[l]["rank"] is not None]
            rows.append(dict(bank=b, bank_name=self.bank_name(b), group=BANK_GROUPS.get(b), by_scenario=by,
                             rank_stable_pct=num(pct), rank_min=min(rk) if rk else None, rank_max=max(rk) if rk else None,
                             stable_under_weights=(pct is not None and pct >= 0.8)))
        banks = sorted(per[base_label])
        agree = []
        for lab in alt:
            x = [base_rank[b] for b in banks]
            y = [ranks[lab][b] for b in banks]
            sp = pd.Series(x, dtype=float).corr(pd.Series(y, dtype=float))
            agree.append(dict(scenario=lab, kendall_tau=num(_kendall_tau(x, y)), spearman=num(sp)))
        return dict(year=year, base_scenario=base_label, scenarios=labels, rows=rows, agreement_with_base=agree,
                    note=("Chỉ kịch bản trọng số DBI/DTI (mục V.2). rank_stable_pct = tỷ lệ kịch bản khác kịch bản cơ sở giữ nguyên hạng; "
                          "stable_under_weights khi >= 80%. CHỈ là kịch bản trọng số; kết luận Vững/Nhóm cùng mức đầy đủ nằm ở /sensitivity/full."))

    # ------------------------------------------------------------------ gói một lần cho frontend đơn giản
    def snapshot(self) -> dict:
        recs = self._records()
        rows = [recs[k] for k in sorted(recs, key=lambda k: (k[1], recs[k]["rank"] or 99, k[0]))]
        return dict(meta=self.meta(), records=rows)
