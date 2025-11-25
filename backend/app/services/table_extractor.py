"""
Table normalization and KPI extraction heuristics.

- normalize_table: convert raw table (list of rows) to cleaned string matrix
- detect_label_column: heuristics to decide if first column is labels (non-numeric)
- extract_kpi_rows: convert table rows into KPI dicts: {"label": ..., "values": {"col_1": val, ...}}
- _parse_numeric: try to parse ints/floats; return original string if not numeric
"""
from typing import List, Any, Tuple, Dict
import re
import logging

logger = logging.getLogger("app.services.table_extractor")

NUMERIC_RE = re.compile(r"^-?\d+([,.\u2009]\d+)*$")  # allow commas, dots, narrow spaces


def normalize_table(raw_table: List[List[Any]]) -> List[List[str]]:
    out: List[List[str]] = []
    for row in raw_table:
        # some pdfplumber tables contain lists where merged cells are None or ''
        cleaned = []
        for c in row:
            if c is None:
                cleaned.append("")
            else:
                # convert to str and strip whitespace, normalize unicode narrow spaces
                cleaned.append(str(c).strip().replace("\u2009", "").replace("\xa0", " "))
        out.append(cleaned)
    return out


def _parse_numeric(s: str):
    if s is None:
        return None
    st = str(s).strip()
    if st == "" or st.lower() in ("na", "n/a", "-"):
        return None
    # remove group separators like commas or narrow spaces
    clean = st.replace(",", "").replace("\u2009", "").replace(" ", "")
    # allow parentheses for negative numbers: (1,234) -> -1234
    if clean.startswith("(") and clean.endswith(")"):
        clean = "-" + clean[1:-1]
    # try parse int or float
    try:
        if "." in clean:
            return float(clean)
        # If it's digits only (possibly leading '-') parse int
        if re.fullmatch(r"-?\d+", clean):
            return int(clean)
        # maybe it's a float-like with thousands delimiters removed previously
        return float(clean)
    except Exception:
        # not strictly numeric, return original trimmed string
        return st


def detect_label_column(table: List[List[str]]) -> Tuple[bool, int]:
    """
    Heuristic:
    - If first column has low numeric fraction (<0.3) and other columns have higher numeric fraction (>0.5)
      then we assume the first column is label column.
    Returns (has_label_column, index_of_label_column)
    """
    if not table:
        return False, 0
    max_cols = max(len(r) for r in table)
    # gather columns
    cols: List[List[str]] = []
    for ci in range(max_cols):
        col = [r[ci] if len(r) > ci else "" for r in table]
        cols.append(col)

    def numeric_fraction(col: List[str]) -> float:
        cnt = 0
        tot = 0
        for v in col:
            vv = (v or "").strip()
            if vv == "":
                continue
            tot += 1
            # use NUMERIC_RE but after removing commas and spaces
            if NUMERIC_RE.match(vv.replace(",", "").replace(" ", "").replace("\u2009", "")):
                cnt += 1
        return (cnt / tot) if tot > 0 else 0.0

    first_frac = numeric_fraction(cols[0])
    others_fracs = [numeric_fraction(c) for c in cols[1:]] if len(cols) > 1 else []
    avg_others = (sum(others_fracs) / len(others_fracs)) if others_fracs else 0.0
    logger.debug(f"detect_label_column: first_frac={first_frac:.2f}, avg_others={avg_others:.2f}, others={others_fracs}")
    if first_frac < 0.3 and avg_others > 0.5:
        return True, 0
    return False, 0


def extract_kpi_rows(table: List[List[Any]], prefer_first_column_labels: bool = True, force_label_column: bool= False) -> List[Dict]:
    """
    Convert a table (raw list of rows) to KPI dicts.
    Each returned dict: {"label": str or None, "values": {"col_i": numeric_or_string, ...}}
    """
    norm = normalize_table(table)
    if force_label_column:
        result = []
        for row in norm:
            label = row[0] if len(row) > 0 else ""
            values = {
                f"col_{i}": _parse_numeric(cell)
                for i, cell in enumerate(row[1:], start=1)
            }
            result.append({"label": label, "values": values})
        return result
    has_label, label_idx = detect_label_column(norm)
    result: List[Dict] = []
    if has_label and prefer_first_column_labels:
        for row in norm:
            label = row[label_idx] if len(row) > label_idx else ""
            values = {}
            for i, cell in enumerate(row):
                if i == label_idx:
                    continue
                key = f"col_{i}"
                values[key] = _parse_numeric(cell)
            result.append({"label": label, "values": values})
    else:
        # fallback: return each row as unlabeled with columns
        for row in norm:
            values = {}
            for i, cell in enumerate(row):
                values[f"col_{i}"] = _parse_numeric(cell)
            result.append({"label": None, "values": values})
    return result