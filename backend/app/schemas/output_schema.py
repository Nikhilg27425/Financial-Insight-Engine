from pydantic import BaseModel
from typing import List, Dict, Any, Optional


class KPIEntry(BaseModel):
    label: Optional[str]
    values: Dict[str, Any]


class ExtractionOutput(BaseModel):
    balance_sheet: List[Dict[str, Any]] = []
    pnl: List[Dict[str, Any]] = []
    cash_flow: List[Dict[str, Any]] = []
    flags: List[Dict[str, Any]] = []
    important_kpis: Dict[str, Any] = {} 