"""Chuyển giá trị pandas/numpy sang kiểu JSON an toàn. Ô thiếu -> None (KHÔNG BAO GIỜ là 0, theo luật cứng số 2)."""
import numpy as np
import pandas as pd


def py(v):
    """NaN/NA/NaT -> None; numpy scalar -> kiểu Python."""
    try:
        if pd.isna(v):
            return None
    except (TypeError, ValueError):
        pass
    if isinstance(v, np.generic):
        v = v.item()
    return v


def num(v, nd=4):
    """Số thực làm tròn nd chữ số; thiếu hoặc không hữu hạn -> None."""
    v = py(v)
    if v is None:
        return None
    try:
        f = float(v)
    except (TypeError, ValueError):
        return None
    return round(f, nd) if np.isfinite(f) else None


def integer(v):
    v = py(v)
    return None if v is None else int(v)


def text(v):
    v = py(v)
    if v is None:
        return None
    s = str(v).strip()
    return s or None
