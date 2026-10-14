"""Lớp C (mục 3.3 của bài luận): hiệu quả tài chính và hoạt động (ROE, ROA, CIR, CASA) và tương quan với điểm chuyển đổi số.

CÔNG THỨC (chốt cho API; tính từ số liệu ĐÃ ĐỐI CHIẾU PDF trong dti_inputs_confirmed.csv, đơn vị triệu đồng):
  ROE  = LNST / bình quân(vốn CSH đầu kỳ, cuối kỳ) × 100
         Cả hai vế cùng là phần thuộc cổ đông ngân hàng mẹ: cột equity của cả 30 dòng được ghi definition = parent
         (tổng VCSH − lợi ích cổ đông không kiểm soát), và net_profit là lợi nhuận cổ đông mẹ ở hầu hết dòng.
  ROA  = LNST / bình quân(tổng tài sản) × 100         (LNST cổ đông mẹ; chênh lệch so với LNST tổng là nhỏ)
  CIR  = |chi phí hoạt động| / (|chi phí hoạt động| + LN thuần trước dự phòng) × 100     (như 10_score.py)
  CASA = tiền gửi không kỳ hạn / tiền gửi của khách hàng × 100                    (số cuối kỳ)
  Thu nhập ngoài lãi (phụ) = (TOI − thu nhập lãi thuần) / TOI × 100, TOI = |chi phí hoạt động| + LN thuần trước dự phòng
Thiếu năm trước thì dùng số cuối kỳ và ghi cờ (cùng quy tắc của 10_score.py). Thiếu dữ liệu -> null, không điền 0.

HƯỚNG PHÂN TÍCH TƯƠNG QUAN (chốt):
  - Biến điểm mặc định là DBI trung bình 6 trụ cột (chấm từ văn bản báo cáo), KHÔNG dùng Score_Bank: Score_Bank có 20% DTI,
    trong đó O-Q1 (từ CIR), O-Q2 (từ thu nhập hoạt động) và T-Q1 (từ tổng tài sản) lấy từ chính báo cáo tài chính,
    nên tương quan Score_Bank với CIR/ROA có phần cơ học. Vẫn cho chọn score_var=score để đối chiếu.
  - Hệ số: Spearman ρ và Kendall τ-b (n nhỏ, không giả định phân phối chuẩn).
  - Báo theo từng năm (n ≤ 5), gộp mọi năm, và gộp sau khi loại xu hướng chung theo năm (hạng phần trăm trong từng năm).
  - lag=1: điểm năm t so với chỉ tiêu năm t+1 (chuyển đổi số đi trước hiệu quả).
Với 5 ngân hàng mỗi năm, kết quả chỉ mang tính mô tả.
"""
import numpy as np
from scipy.stats import kendalltau, rankdata, spearmanr

from .definitions import LAYER_C_METRICS
from .errors import ApiError
from .serialize import num

MIN_N = 3          # số quan sát tối thiểu để tính hệ số
LOW_N = 8          # dưới ngưỡng này gắn cờ low_n


def _corr(x, y):
    """Spearman, Kendall τ-b và p-value của Kendall; trả None khi không tính được."""
    n = len(x)
    if n < MIN_N or np.ptp(x) == 0 or np.ptp(y) == 0:
        return dict(n=n, spearman=None, kendall=None, p_kendall=None, low_n=n < LOW_N)
    k = kendalltau(x, y)
    return dict(n=n, spearman=num(spearmanr(x, y).statistic), kendall=num(k.statistic), p_kendall=num(k.pvalue), low_n=n < LOW_N)


class LayerCMixin:
    # ------------------------------------------------------------------ tính chỉ tiêu
    def _financials(self) -> dict:
        """{(bank, year): {metric: giá trị|None, 'flags': [...]}} từ số liệu đã đối chiếu."""
        df = self.store.inputs_confirmed().copy()
        df["bank"] = df["bank"].astype(str).str.strip().str.lower()
        df = df[self.S.confirmed_mask(df)]
        V = {(r.bank, int(r.year), r.variable): float(r.value) for r in df.itertuples(index=False)}
        out = {}
        for b in self.bank_ids():
            for y in self.years():
                g = lambda v, yy=y: V.get((b, yy, v))
                flags = []

                def avg(v):
                    a, p = g(v), g(v, y - 1)
                    if a is None:
                        return None
                    if p is None:
                        flags.append(f"{v}: dùng số cuối kỳ do thiếu năm {y - 1}")
                        return a
                    return (a + p) / 2

                npf, eq, ta = g("net_profit"), avg("equity"), avg("total_assets")
                opex, opp = g("opex"), g("op_profit_before_provision")
                casa, dep, nii = g("casa_deposits"), g("customer_deposits"), g("net_interest_income")
                toi = None if opex is None or opp is None else abs(opex) + opp
                m = dict(
                    roe=None if npf is None or not eq or eq <= 0 else npf / eq * 100,
                    roa=None if npf is None or not ta or ta <= 0 else npf / ta * 100,
                    cir=None if toi is None or toi <= 0 else abs(opex) / toi * 100,
                    casa=None if casa is None or not dep or dep <= 0 else casa / dep * 100,
                    non_interest_share=None if toi is None or nii is None or toi <= 0 else (toi - nii) / toi * 100)
                for k, v in m.items():
                    if v is None:
                        flags.append(f"{k}: thiếu số liệu đầu vào đã đối chiếu")
                out[(b, y)] = dict(m, flags=sorted(set(flags)))
        return out

    def _score_value(self, rec, score_var):
        if score_var == "score":
            return rec["score"]
        vals = [p["dbi"] for p in rec["pillars"].values() if p.get("dbi") is not None]
        return sum(vals) / len(vals) if len(vals) == len(self.PILLARS) else None

    # ------------------------------------------------------------------ giá trị theo ngân hàng–năm (cho biểu đồ phân tán)
    def financial_performance(self, year=None, bank=None, score_var="dbi") -> dict:
        if score_var not in ("dbi", "score"):
            raise ApiError(422, "invalid_score_var", "score_var phải là dbi hoặc score.")
        year = self._year(year) if year is not None else None
        bank = self._bank(bank) if bank else None
        fin, recs, items = self._financials(), self._records(), []
        for (b, y), m in sorted(fin.items(), key=lambda kv: (kv[0][1], kv[0][0])):
            if (bank and b != bank) or (year and y != year):
                continue
            r = recs.get((b, y))
            items.append(dict(
                bank=b, bank_name=self.bank_name(b), group=r["group"] if r else None, year=y,
                roe=num(m["roe"]), roa=num(m["roa"]), cir=num(m["cir"]), casa=num(m["casa"]),
                non_interest_share=num(m["non_interest_share"]),
                dbi_mean=num(self._score_value(r, "dbi")) if r else None, score=r["score"] if r else None,
                data_confidence=r["data_confidence"] if r else None, flags=m["flags"]))
        return dict(year=year, bank=bank, count=len(items),
                    metrics={k: dict(v) for k, v in LAYER_C_METRICS.items()}, items=items,
                    note="Số liệu tài chính lấy từ dti_inputs_confirmed.csv (đã đối chiếu PDF); null là thiếu số liệu, không phải 0.")

    # ------------------------------------------------------------------ tương quan
    def layer_c_correlation(self, score_var="dbi", lag=0) -> dict:
        if score_var not in ("dbi", "score"):
            raise ApiError(422, "invalid_score_var", "score_var phải là dbi hoặc score.")
        if lag not in (0, 1):
            raise ApiError(422, "invalid_lag", "lag phải là 0 (cùng năm) hoặc 1 (điểm năm t so với chỉ tiêu năm t+1).")
        fin, recs, years = self._financials(), self._records(), self.years()
        metrics = []
        for key, meta in LAYER_C_METRICS.items():
            pairs = []          # (năm của điểm, x, y)
            for (b, y), r in recs.items():
                x = self._score_value(r, score_var)
                m = fin.get((b, y + lag))
                if x is None or m is None or m[key] is None:
                    continue
                pairs.append((y, x, m[key]))
            by_year = []
            for y in years:
                sel = [(x, v) for yy, x, v in pairs if yy == y]
                c = _corr([p[0] for p in sel], [p[1] for p in sel]) if sel else dict(n=0, spearman=None, kendall=None, p_kendall=None, low_n=True)
                sign = meta["expected_sign"]
                c["consistent_with_expected"] = (None if sign is None or c["spearman"] is None
                                                 else bool(np.sign(c["spearman"]) == sign))
                by_year.append(dict(year=y, **c))
            pooled = _corr(np.array([p[1] for p in pairs]), np.array([p[2] for p in pairs])) if pairs else dict(n=0)
            # loại xu hướng chung theo năm: hạng phần trăm trong từng năm rồi gộp
            xs, ys = [], []
            for y in years:
                sel = [(x, v) for yy, x, v in pairs if yy == y]
                if len(sel) >= 2:
                    n = len(sel)
                    xs += list((rankdata([s[0] for s in sel]) - (n + 1) / 2) / n)
                    ys += list((rankdata([s[1] for s in sel]) - (n + 1) / 2) / n)
            within = (dict(n=len(xs), spearman=num(np.corrcoef(xs, ys)[0, 1]) if len(xs) >= MIN_N and np.ptp(xs) and np.ptp(ys) else None)
                      if xs else dict(n=0, spearman=None))
            sign = meta["expected_sign"]
            for blk in (pooled, within):
                blk["consistent_with_expected"] = (None if sign is None or blk.get("spearman") is None
                                                   else bool(np.sign(blk["spearman"]) == sign))
            metrics.append(dict(metric=key, name=meta["name"], unit=meta["unit"], expected_sign=sign,
                                by_year=by_year, pooled=pooled, pooled_within_year=within))
        notes = [
            "Mỗi năm chỉ có tối đa 5 ngân hàng: hệ số theo năm chỉ mang tính mô tả, không dùng để kết luận quan hệ nhân quả; p_value gần như không có ý nghĩa thống kê ở n này.",
            "pooled gộp nhiều năm nên cùng một ngân hàng lặp lại, các quan sát không độc lập; pooled_within_year đã loại xu hướng chung theo năm bằng hạng phần trăm trong từng năm.",
            ("Biến điểm là DBI trung bình 6 trụ cột (chấm từ văn bản, độc lập với báo cáo tài chính)." if score_var == "dbi" else
             "Score_Bank gồm 20% DTI; O-Q1 (từ CIR), O-Q2 (từ thu nhập hoạt động) và T-Q1 (từ tổng tài sản) lấy từ cùng báo cáo tài chính nên tương quan với CIR và ROA có phần cơ học."),
            "expected_sign là dấu kỳ vọng nếu điểm cao đi cùng hiệu quả tốt hơn (CIR thấp hơn là tốt hơn); consistent_with_expected so dấu Spearman với kỳ vọng đó.",
        ]
        if lag:
            notes.append("lag=1: điểm năm t được ghép với chỉ tiêu năm t+1, nên năm cuối của điểm không có cặp.")
        return dict(score_var=score_var, lag=lag, method="Spearman ρ và Kendall τ-b",
                    metrics=metrics, notes=notes)
