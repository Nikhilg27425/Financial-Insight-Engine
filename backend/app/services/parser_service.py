# import re
# from typing import List, Dict, Any, Optional
# from app.services.preprocessing_service import parse_number_string_to_crore, scale_crore_to_rupees
# from app.services.preprocessing_service import find_first_number_in_line

# def parse_financial_document(cleaned_text: str, tables: List[List[List[str]]], scale: float) -> Dict[str, Any]:
#     """
#     Parse cleaned text and extracted tables to extract financial sections.
#     """
#     balance_sheet: List[Dict[str, Any]] = []
#     pnl: Dict[str, Dict[str, Any]] = {}
#     cash_flow: Dict[str, Dict[str, Any]] = {}

#     # Helper functions
#     def add_bs_item(name: str, current: Optional[int], previous: Optional[int] = None):
#         item = {"item": name}
#         if current is not None:
#             item["current_period"] = current
#         if previous is not None:
#             item["previous_period"] = previous
#         balance_sheet.append(item)

#     def set_section_value(section: Dict[str, Any], key: str, val_crore: Optional[float], prev_crore: Optional[float] = None):
#         rupees = scale_crore_to_rupees(val_crore, scale) if val_crore is not None else None
#         prev_rupees = scale_crore_to_rupees(prev_crore, scale) if prev_crore is not None else None
#         section[key] = {"value_crore": val_crore, "value_rupees": rupees}
#         if prev_rupees is not None:
#             section[key]["previous_value_rupees"] = prev_rupees

#     # Parse lines from text
#     lines = [ln for ln in cleaned_text.splitlines() if ln.strip()]
#     for line in lines:
#         low = line.lower()
#         # Balance Sheet lines
#         if "total assets" in low and "current assets" not in low:
#             val = find_first_number_in_line(line)
#             if val is not None:
#                 rupees = scale_crore_to_rupees(val, scale)
#                 balance_sheet.append({"item": "Total Assets", "current_period": rupees})
#         if "total equity" in low:
#             val = find_first_number_in_line(line)
#             if val is not None:
#                 rupees = scale_crore_to_rupees(val, scale)
#                 balance_sheet.append({"item": "Total Equity", "current_period": rupees})
#         if "total liabilities" in low:
#             val = find_first_number_in_line(line)
#             if val is not None:
#                 rupees = scale_crore_to_rupees(val, scale)
#                 balance_sheet.append({"item": "Total Liabilities", "current_period": rupees})
#         if "current assets" in low:
#             val = find_first_number_in_line(line)
#             if val is not None:
#                 rupees = scale_crore_to_rupees(val, scale)
#                 balance_sheet.append({"item": "Current Assets", "current_period": rupees})
#         if "current liabilities" in low:
#             val = find_first_number_in_line(line)
#             if val is not None:
#                 rupees = scale_crore_to_rupees(val, scale)
#                 balance_sheet.append({"item": "Current Liabilities", "current_period": rupees})
#         # P&L lines
#         if ("total income" in low or "total revenue" in low or "revenue from operations" in low) and "profit" not in low:
#             val = find_first_number_in_line(line)
#             if val is not None:
#                 rupees = scale_crore_to_rupees(val, scale)
#                 pnl["revenue"] = {"value_crore": val, "value_rupees": rupees}
#         if ("net profit" in low or "profit after tax" in low or "profit for the year" in low or "profit for the period" in low):
#             val = find_first_number_in_line(line)
#             if val is not None:
#                 rupees = scale_crore_to_rupees(val, scale)
#                 pnl["net_profit"] = {"value_crore": val, "value_rupees": rupees}
#         # Cash Flow lines
#         if "net cash from operating" in low or "net cash generated from operating" in low or "cash generated from operations" in low:
#             val = find_first_number_in_line(line)
#             if val is not None:
#                 rupees = scale_crore_to_rupees(val, scale)
#                 cash_flow["operating_cf"] = {"value_crore": val, "value_rupees": rupees}
#         if ("purchase of fixed" in low or "payment for property" in low or "capital expenditure" in low or "capex" in low):
#             val = find_first_number_in_line(line)
#             if val is not None:
#                 rupees = scale_crore_to_rupees(val, scale)
#                 cash_flow["capex"] = {"value_crore": val, "value_rupees": rupees}

#     # Parse tables for multi-period data (if any)
#     for table in tables:
#         if len(table) < 2:
#             continue
#         header = table[0]
#         # Identify numeric columns by year in header
#         numeric_cols = [i for i, cell in enumerate(header) if isinstance(cell, str) and re.search(r"\d{4}", cell)]
#         if len(numeric_cols) >= 2:
#             cur_idx, prev_idx = numeric_cols[0], numeric_cols[1]
#         else:
#             # fallback: assume first column is labels, next two are numbers
#             if len(header) >= 3 and header[1] and header[2] and all(re.match(r"^[\d,\.\-]+$", str(x).replace(',', '')) for x in header[1:3]):
#                 cur_idx, prev_idx = 1, 2
#             else:
#                 continue
#         for row in table[1:]:
#             if not row or len(row) <= max(cur_idx, prev_idx):
#                 continue
#             label = str(row[0]).strip()
#             label_norm = label.lower()
#             cur_val = parse_number_string_to_crore(str(row[cur_idx])) if row[cur_idx] not in (None, "") else None
#             prev_val = parse_number_string_to_crore(str(row[prev_idx])) if row[prev_idx] not in (None, "") else None
#             cur_rupees = scale_crore_to_rupees(cur_val, scale) if cur_val is not None else None
#             prev_rupees = scale_crore_to_rupees(prev_val, scale) if prev_val is not None else None
#             # Balance Sheet items
#             if "total assets" in label_norm:
#                 balance_sheet = [item for item in balance_sheet if item.get("item") != "Total Assets"]
#                 add_bs_item("Total Assets", cur_rupees, prev_rupees)
#             elif "total equity" in label_norm or "shareholders funds" in label_norm or "equity and liabilities" in label_norm:
#                 balance_sheet = [item for item in balance_sheet if item.get("item") != "Total Equity"]
#                 add_bs_item("Total Equity", cur_rupees, prev_rupees)
#             elif "total liabilities" in label_norm:
#                 balance_sheet = [item for item in balance_sheet if item.get("item") != "Total Liabilities"]
#                 add_bs_item("Total Liabilities", cur_rupees, prev_rupees)
#             elif "current assets" in label_norm:
#                 balance_sheet = [item for item in balance_sheet if item.get("item") != "Current Assets"]
#                 add_bs_item("Current Assets", cur_rupees, prev_rupees)
#             elif "current liabilities" in label_norm:
#                 balance_sheet = [item for item in balance_sheet if item.get("item") != "Current Liabilities"]
#                 add_bs_item("Current Liabilities", cur_rupees, prev_rupees)
#             # P&L items
#             elif "total income" in label_norm or "total revenue" in label_norm or "revenue from operations" in label_norm or "sales" in label_norm:
#                 set_section_value(pnl, "revenue", cur_val, prev_val)
#             elif ("net profit" in label_norm or "profit after tax" in label_norm or "profit for the year" in label_norm) and "gross profit" not in label_norm:
#                 set_section_value(pnl, "net_profit", cur_val, prev_val)
#             # Cash Flow items
#             elif "net cash from operating" in label_norm or "net cash generated from operating" in label_norm:
#                 set_section_value(cash_flow, "operating_cf", cur_val, prev_val)
#             elif "capital expenditure" in label_norm or "purchase of fixed assets" in label_norm or "capex" in label_norm:
#                 set_section_value(cash_flow, "capex", cur_val, prev_val)

#     # Remove duplicate balance sheet items, keeping last entries
#     unique = {}
#     for item in balance_sheet:
#         unique[item["item"]] = item
#     balance_sheet = list(unique.values())

#     return {"sections": {"balance_sheet": balance_sheet, "pnl": pnl, "cash_flow": cash_flow}, "scale": scale, "raw_text": cleaned_text}









# """
# Parser orchestration: converts OCR outputs (pages_text + tables) into final JSON.

# Strategy summary:
# - For each table, attempt KPI extraction using table_extractor.extract_kpi_rows(...)
# - Classify the table into balance_sheet / pnl / cash_flow using page text heuristics (keywords)
# - Append extracted KPI rows to the matching section
# - Provide flags for unclassified or suspicious tables

# Usage:
#     parser = ParserService(prefer_first_column_labels=True)
#     result_dict = parser.parse(tables, pages_text)
# """
# import logging
# from typing import List, Dict, Any
# from app.services.table_extractor import extract_kpi_rows
# from app.schemas.output_schema import ExtractionOutput

# logger = logging.getLogger("app.services.parser_service")


# class ParserServiceError(Exception):
#     pass


# class ParserService:
#     def __init__(self, prefer_first_column_labels: bool = True):
#         self.prefer_first_column = bool(prefer_first_column_labels)
    
#     def _compute_important_kpis(self, parsed):
#         bs = parsed.get("balance_sheet", []) or []
#         pnl = parsed.get("pnl", []) or []
#         cf = parsed.get("cash_flow", []) or []

#         def normalize(s):
#             if not s: return ""
#             return (
#                 s.lower()
#                 .replace(" ", "")
#                 .replace("\u00a0", "")
#                 .replace("\u2009", "")
#                 .replace(".", "")
#                 .replace(":", "")
#             )

#         def get_val(row):
#             for v in row.get("values", {}).values():
#                 if isinstance(v, (int, float)):
#                     return v
#             return None


#         def match_exact_label(rows, keywords):
#             """Only match clean labels, and avoid matching 'total liabilities and equity'."""
#             for row in rows:
#                 lbl = normalize(row.get("label"))
#                 if any(k == lbl for k in keywords):
#                     return get_val(row)
#             return None

#         def match_contains(rows, keywords, exclude=None):
#             """General contains search."""
#             for row in reversed(rows):
#                 lbl = normalize(row.get("label"))
#                 if exclude:
#                     if any(e in lbl for e in exclude):
#                         continue
#                 if any(k in lbl for k in keywords):
#                     v = get_val(row)
#                     if v is not None:
#                         return v
#             return None

#         # ---------------------------------------
#         # 1️⃣ TOTAL ASSETS (always direct)
#         # ---------------------------------------
#         total_assets = match_contains(
#             bs,
#             ["totalassets"],
#             exclude=["liabilitiesandequity", "assetsliabilities"]
#         )

#         # ---------------------------------------
#         # 2️⃣ TOTAL EQUITY
#         # ---------------------------------------
#         total_equity = match_exact_label(bs, ["totalequity"])

#         if not total_equity:
#             # Equity attributable to owners + NCI
#             eq_attr = match_contains(bs, ["equityattributable"])
#             nci = match_contains(bs, ["noncontrollinginterest", "n on-controllinginterest"])
#             if eq_attr is not None:
#                 total_equity = eq_attr + (nci or 0)

#         # ---------------------------------------
#         # 3️⃣ TOTAL LIABILITIES
#         # ---------------------------------------
#         total_liabilities = match_exact_label(bs, ["totalliabilities", "total liabilities"])

#         if not total_liabilities:
#             total_liabilities = match_contains(
#                 bs,
#                 ["totalliabilities", "totalliability", "totalliabilitie"],
#                 exclude=["equity", "assets"]  # prevent picking "total equity and liabilities"
#             )

#         if not total_liabilities:
#             # Find "Total current liabilities"
#             tcl = match_contains(
#                 bs,
#                 ["totalcurrentliabilities", "total current liabilities"]
#             )

#             # Find "Total non-current liabilities"
#             tncl = match_contains(
#                 bs,
#                 ["totalnoncurrentliabilities", "total non-current liabilities"]
#             )

#             if isinstance(tcl, (int, float)) and isinstance(tncl, (int, float)):
#                 total_liabilities = tcl + tncl
#             else:
#                 total_liabilities = None   # Avoid wrong numbers

#         # ---------------------------------------
#         # 4️⃣ PNL KPIs
#         # ---------------------------------------
#         revenue = match_contains(pnl, ["totalincome", "totalrevenue", "revenue"])
#         net_profit = match_contains(pnl, ["profitfortheperiod", "profit"])

#         # ---------------------------------------
#         # 5️⃣ CASH FLOW KPIs
#         # ---------------------------------------
#         operating_cash_flow = match_contains(cf, ["operatingactivities", "netcashfromoperating"])
#         net_cash_flow = match_contains(cf, ["net(decrease)/increaseincash", "netcash"])

#         # ---------------------------------------
#         # 6️⃣ RATIO CALCULATION
#         # ---------------------------------------
#         ratios = {}

#         if total_equity and total_liabilities:
#             ratios["debt_equity_ratio"] = total_liabilities / total_equity

#         if total_assets and total_equity:
#             ratios["equity_ratio"] = total_equity / total_assets

#         if revenue and net_profit:
#             ratios["net_profit_margin"] = net_profit / revenue

#         if net_profit and total_equity:
#             ratios["roe"] = net_profit / total_equity

#         if net_profit and total_assets:
#             ratios["roa"] = net_profit / total_assets

#         if net_profit and operating_cash_flow:
#             ratios["cashflow_to_netincome"] = operating_cash_flow / net_profit

#         # remove None
#         clean = {
#             k: v for k, v in {
#                 "total_assets": total_assets,
#                 "total_equity": total_equity,
#                 "total_liabilities": total_liabilities,
#                 "revenue": revenue,
#                 "net_profit": net_profit,
#                 "operating_cash_flow": operating_cash_flow,
#                 "net_cash_flow": net_cash_flow,
#                 "ratios": ratios
#             }.items() if v is not None
#         }

#         return clean


#     def parse(self, tables: List[Dict[str, Any]], pages_text: Dict[int, str]) -> Dict[str, Any]:
#         """
#         tables: List of { "page": int, "table": List[List] }
#         pages_text: Dict[page_number -> text]
#         returns: dict conforming to ExtractionOutput
#         """
#         out = {
#             "balance_sheet": [],
#             "pnl": [],
#             "cash_flow": [],
#             "flags": [],
#         }

#         if not tables:
#             logger.warning("No tables provided to parser_service.parse")
#         else:
#             logger.info(
#                 f"Parsing tables in range: pages {tables[0].get('page')} - {tables[-1].get('page')} , total tables: {len(tables)}"
#             )

#         for t in tables:
#             page = t.get("page")
#             raw = t.get("table", [])
#             # try:
#             #     kpis = extract_kpi_rows(raw, prefer_first_column_labels=self.prefer_first_column)
#             # except Exception:
#             #     logger.exception(f"Failed to extract KPI rows from table on page {page}")
#             #     out["flags"].append({"page": page, "note": "kpi_extraction_failed"})
#             #     continue
#             page_text = pages_text.get(page, "") or ""
#             section = self._guess_section(page_text)
#             try:

#                 # Force the first column to be label for cash flow tables
#                 if section == "cash_flow":
#                     kpis = extract_kpi_rows(
#                         raw,
#                         prefer_first_column_labels=True,
#                         force_label_column=True   # NEW FLAG
#                     )
#                 else:
#                     kpis = extract_kpi_rows(
#                         raw,
#                         prefer_first_column_labels=self.prefer_first_column
#                     )

#             except Exception:
#                 logger.exception(f"Failed to extract KPI rows from table on page {page}")
#                 out["flags"].append({"page": page, "note": "kpi_extraction_failed"})
#                 continue
#             #till here

#             logger.debug(f"Table on page {page} guessed as section {section}; extracted {len(kpis)} rows")


#             if section == "balance_sheet":
#                 out["balance_sheet"].extend(kpis)
#             elif section == "pnl":
#                 out["pnl"].extend(kpis)
#             elif section == "cash_flow":
#                 out["cash_flow"].extend(kpis)
#             else:
#                 # attempt simple fallback: recognize words inside table labels
#                 labelled = any((row.get("label") for row in kpis))
#                 if labelled:
#                     # try to detect using label keywords inside labels
#                     placed = False
#                     for row in kpis:
#                         lbl = (row.get("label") or "").lower()
#                         if any(x in lbl for x in ["assets", "liabilities", "equity", "shareholders"]):
#                             out["balance_sheet"].append(row)
#                             placed = True
#                         elif any(x in lbl for x in ["revenue", "profit", "loss", "income", "turnover"]):
#                             out["pnl"].append(row)
#                             placed = True
#                         elif any(x in lbl for x in ["cash", "operating activities", "investing activities", "financing activities"]):
#                             out["cash_flow"].append(row)
#                             placed = True
#                         else:
#                             continue
#                     if not placed:
#                         out["flags"].append({"page": page, "note": "unclassified_but_has_labels"})
#                 else:
#                     out["flags"].append({"page": page, "note": "unclassified_table_no_labels"})
        
#         important_kpis = self._compute_important_kpis(out)

#         # convert to pydantic model for validation and normalization
#         try:    
#             final = ExtractionOutput(
#                 balance_sheet=out["balance_sheet"],
#                 pnl=out["pnl"],
#                 cash_flow=out["cash_flow"],
#                 flags=out["flags"],
#                 important_kpis=important_kpis,
#             )
#             return final.dict()
#         except Exception:
#             logger.exception("Failed to validate final output against schema")
#             # return raw out as fallback
#             return out

#     @staticmethod
#     def _guess_section(page_text: str) -> str:
#         """
#         Detect section type using ALL common variants seen in DRHP/RHP/AR.
#         """
#         if not page_text:
#             return "unknown"

#         t = page_text.lower()

#         # BALANCE SHEET keywords
#         bs_keywords = [
#             "balance sheet",
#             "statement of financial position",
#             "statement of assets and liabilities",
#             "assets and liabilities",
#             "summary of assets and liabilities",
#             "restated consolidated balance sheet",
#             "restated statement of assets",
#             "summary restated balance sheet",
#             "summary restated statement of assets",
#             "summary of restated balance sheet",
#             "summary of restated consolidated assets",
#             "summary of restated consolidated balance sheet",
#             "summary of balance sheet",
#             "summary balance sheet",
#             "assets & liabilities",
#             "assets and liability",
#             "restated financial position",
#             "restated consolidated statement of assets and liabilities"
#         ]

#         # PROFIT & LOSS keywords
#         pnl_keywords = [
#             "profit and loss",
#             "profit & loss",
#             "p&l",
#             "statement of profit",
#             "statement of profit and loss",
#             "consolidated p&l",
#             "summary restated profit",
#             "summary of profit and loss",
#             "summary profit and loss",
#             "restated consolidated profit",
#             "income statement",
#             "statement of income",
#             "total income",
#             "other comprehensive income",
#             "oci",
#             "restated consolidated statement of profit and loss"
#         ]

#         # CASH FLOW keywords
#         cf_keywords = [
#             "cash flow",
#             "cashflow",
#             "cash flows",
#             "statement of cash flows",
#             "summary cash flow",
#             "summary of cash flows",
#             "restated cash flows",
#             "restated consolidated cash flow",
#             "summary restated cash flows",
#             "summary restated consolidated cash flows",
#             "cash flow statement",
#             "cash flows statement",
#             "restated consolidated statement of cash flows",
#             "restated consolidated statement of cashflows"
#         ]

#         if any(k in t for k in bs_keywords):
#             return "balance_sheet"

#         if any(k in t for k in pnl_keywords):
#             return "pnl"

#         if any(k in t for k in cf_keywords):
#             return "cash_flow"

#         return "unknown"





# #correct
# """
# Parser orchestration: converts OCR outputs (pages_text + tables) into final JSON.

# Strategy summary:
# - For each table, attempt KPI extraction using table_extractor.extract_kpi_rows(...)
# - Classify the table into balance_sheet / pnl / cash_flow using page text heuristics (keywords)
# - Append extracted KPI rows to the matching section
# - Provide flags for unclassified or suspicious tables

# Usage:
#     parser = ParserService(prefer_first_column_labels=True)
#     result_dict = parser.parse(tables, pages_text)
# """
# import logging
# from typing import List, Dict, Any
# from app.services.table_extractor import extract_kpi_rows
# from app.schemas.output_schema import ExtractionOutput

# logger = logging.getLogger("app.services.parser_service")


# class ParserServiceError(Exception):
#     pass


# class ParserService:
#     def __init__(self, prefer_first_column_labels: bool = True):
#         self.prefer_first_column = bool(prefer_first_column_labels)
    
#     def _compute_important_kpis(self, parsed):
#         bs = parsed.get("balance_sheet", []) or []
#         pnl = parsed.get("pnl", []) or []
#         cf = parsed.get("cash_flow", []) or []

#         def norm(s):
#             if not s:
#                 return ""
#             return (
#                 s.lower()
#                 .replace(" ", "")
#                 .replace("\u00a0", "")
#                 .replace("\u2009", "")
#                 .replace(".", "")
#                 .replace(":", "")
#             )

#         def is_number(x):
#             return isinstance(x, (int, float))


#         def extract_latest_single_value(row):
#             """Return value from FIRST numeric column (latest: June 30, 2025)."""
#             vals = row.get("values", {}) or {}
#             for k in sorted(vals.keys()):
#                 try:
#                     num = float(str(vals[k]).replace(",", ""))
#                     return num
#                 except:
#                     continue
#             return None

#         # -------------------------
#         # Extract last-3-values (handles 4-col, 5-col and fallbacks)
#         # -------------------------
#         def extract_period_values(row):
#             vals = row.get("values", {}) or {}

#             # normalize numeric strings -> float
#             clean_vals = {}
#             for k,v in vals.items():
#                 try:
#                     clean_vals[k] = float(str(v).replace(",", ""))
#                 except:
#                     clean_vals[k] = None

#             keys = sorted(clean_vals.keys())

#             # 5 column pattern
#             if "col_5" in clean_vals:
#                 mapping = {
#                     "2025": clean_vals.get("col_3"),
#                     "2024": clean_vals.get("col_4"),
#                     "2023": clean_vals.get("col_5"),
#                 }
#             # 4 column pattern
#             elif "col_4" in clean_vals:
#                 mapping = {
#                     "2025": clean_vals.get("col_2"),
#                     "2024": clean_vals.get("col_3"),
#                     "2023": clean_vals.get("col_4"),
#                 }
#             else:
#                 # fallback: last 3 numeric columns
#                 numeric = [k for k in keys if clean_vals.get(k) is not None]
#                 if len(numeric) >= 3:
#                     last3 = numeric[-3:]
#                     mapping = {
#                         "2025": clean_vals[last3[-1]],
#                         "2024": clean_vals[last3[-2]],
#                         "2023": clean_vals[last3[-3]],
#                     }
#                 else:
#                     mapping = {}

#             latest = mapping.get("2025")

#             return latest, {
#                 "latest": mapping.get("2025"),
#                 "prev1": mapping.get("2024"),
#                 "prev2": mapping.get("2023"),
#             }


#         # -------------------------
#         # Row match helpers
#         # -------------------------
#         def match_row(rows, keywords, exclude=None, must_exact=False):
#             # prefer exact equality for exact keywords, else contains
#             for row in rows:
#                 lbl = norm(row.get("label") or "")
#                 if exclude and any(e in lbl for e in exclude):
#                     continue
#                 if must_exact:
#                     if any(k == lbl for k in keywords):
#                         return row
#                 else:
#                     if any(k in lbl for k in keywords):
#                         return row
#             return None

#         # -------------------------
#         # Collect KPIs (latest + periods)
#         # -------------------------
#         kpi = {}

#         def assign_kpi(name, row):
#             if not row:
#                 return
#             single_latest = extract_latest_single_value(row)   # <— correct latest value

#             _, periods = extract_period_values(row)            # <— for charts (unchanged)

#             if is_number(single_latest):
#                 kpi[name] = single_latest                      # <— FIRST COLUMN!
#                 kpi[f"{name}_periods"] = periods

#         # TOTAL ASSETS - avoid picking "total liabilities and equity" etc.
#         assign_kpi(
#             "total_assets",
#             match_row(bs, ["totalassets", "totalassetsandliabilities", "totalasset"], exclude=["liabilitiesandequity", "assetsliabilities"])
#         )

#         # TOTAL EQUITY - try exact first, else equity attributable + NCI fallback later
#         equity_row = match_row(bs, ["totalequity", "shareholdersfunds"], must_exact=False)
#         assign_kpi("total_equity", equity_row)

#         # TOTAL LIABILITIES - try exact; if missing, try total current + total non-current
#         liabilities_row = match_row(bs, ["totalliabilities", "totalliabilities", "totalliability", "totalliabilitie"], must_exact=False)
#         if liabilities_row:
#             assign_kpi("total_liabilities", liabilities_row)
#         else:
#             # try total current + total non-current
#             tcl_row = match_row(bs, ["totalcurrentliabilities", "total current liabilities", "currentliabilities"])
#             tncl_row = match_row(bs, ["totalnoncurrentliabilities", "total non-current liabilities", "noncurrentliabilities"])
#             # extract numeric latests
#             _, tcl_periods = extract_period_values(tcl_row) if tcl_row else (None, {})
#             _, tncl_periods = extract_period_values(tncl_row) if tncl_row else (None, {})
#             tcl_latest = tcl_periods.get("latest") if tcl_periods else None
#             tncl_latest = tncl_periods.get("latest") if tncl_periods else None

#             if is_number(tcl_latest) and is_number(tncl_latest):
#                 total_liab_latest = tcl_latest + tncl_latest
#                 kpi["total_liabilities"] = total_liab_latest
#                 # for periods combine when both exist
#                 kpi["total_liabilities_periods"] = {
#                     "latest": total_liab_latest,
#                     "prev1": (tcl_periods.get("prev1") or 0) + (tncl_periods.get("prev1") or 0) if (tcl_periods or tncl_periods) else None,
#                     "prev2": (tcl_periods.get("prev2") or 0) + (tncl_periods.get("prev2") or 0) if (tcl_periods or tncl_periods) else None,
#                 }

#         # REVENUE (P&L)
#         assign_kpi("revenue", match_row(pnl, ["totalincome", "totalrevenue", "revenue", "sales"]))

#         # NET PROFIT (P&L)
#         assign_kpi("net_profit", match_row(pnl, ["profitfortheperiod", "profitaftertax", "profit", "netprofit", "profitfortheyear"]))

#         # NET CASH FLOW (cash flow)
#         assign_kpi("net_cash_flow", match_row(cf, ["netcash", "net(decrease)/increaseincash", "netcashfromoperating", "netcashflow"]))

#         # If total_equity not found directly, try equity attributable + non-controlling interest
#         if "total_equity" not in kpi:
#             eq_attr_row = match_row(bs, ["equityattributable", "equityattributabletoowners", "equityattributabletoownersofparent"])
#             nci_row = match_row(bs, ["noncontrollinginterest", "non-controllinginterest", "n on-controllinginterest"])
#             eq_attr_latest = None
#             nci_latest = None
#             eq_attr_periods = {}
#             nci_periods = {}
#             if eq_attr_row:
#                 _, eq_attr_periods = extract_period_values(eq_attr_row)
#                 eq_attr_latest = eq_attr_periods.get("latest")
#             if nci_row:
#                 _, nci_periods = extract_period_values(nci_row)
#                 nci_latest = nci_periods.get("latest")
#             if is_number(eq_attr_latest):
#                 total_equity_val = eq_attr_latest + (nci_latest or 0)
#                 kpi["total_equity"] = total_equity_val
#                 kpi["total_equity_periods"] = {
#                     "latest": total_equity_val,
#                     "prev1": (eq_attr_periods.get("prev1") or 0) + (nci_periods.get("prev1") or 0),
#                     "prev2": (eq_attr_periods.get("prev2") or 0) + (nci_periods.get("prev2") or 0),
#                 }

#         # ---------------------------------------
#         # RATIOS (use latest values only - safe checks)
#         # ---------------------------------------
#         ratios = {}
#         ta = kpi.get("total_assets")
#         te = kpi.get("total_equity")
#         tl = kpi.get("total_liabilities")
#         rev = kpi.get("revenue")
#         npv = kpi.get("net_profit")
#         cf_latest = kpi.get("net_cash_flow")

#         # make sure denominators are valid (non-zero)
#         if is_number(te) and is_number(tl) and te != 0:
#             ratios["debt_equity_ratio"] = tl / te

#         if is_number(ta) and is_number(te) and ta != 0:
#             ratios["equity_ratio"] = te / ta

#         if is_number(rev) and is_number(npv) and rev != 0:
#             ratios["net_profit_margin"] = npv / rev

#         if is_number(npv) and is_number(te) and te != 0:
#             ratios["roe"] = npv / te

#         if is_number(npv) and is_number(ta) and ta != 0:
#             ratios["roa"] = npv / ta

#         if is_number(npv) and is_number(cf_latest) and npv != 0:
#             ratios["cashflow_to_netincome"] = cf_latest / npv

#         # attach ratios
#         if ratios:
#             kpi["ratios"] = ratios

#         return kpi




#     def parse(self, tables: List[Dict[str, Any]], pages_text: Dict[int, str]) -> Dict[str, Any]:
#         """
#         tables: List of { "page": int, "table": List[List] }
#         pages_text: Dict[page_number -> text]
#         returns: dict conforming to ExtractionOutput
#         """
#         out = {
#             "balance_sheet": [],
#             "pnl": [],
#             "cash_flow": [],
#             "flags": [],
#         }

#         if not tables:
#             logger.warning("No tables provided to parser_service.parse")
#         else:
#             logger.info(
#                 f"Parsing tables in range: pages {tables[0].get('page')} - {tables[-1].get('page')} , total tables: {len(tables)}"
#             )

#         for t in tables:
#             page = t.get("page")
#             raw = t.get("table", [])
#             # try:
#             #     kpis = extract_kpi_rows(raw, prefer_first_column_labels=self.prefer_first_column)
#             # except Exception:
#             #     logger.exception(f"Failed to extract KPI rows from table on page {page}")
#             #     out["flags"].append({"page": page, "note": "kpi_extraction_failed"})
#             #     continue
#             page_text = pages_text.get(page, "") or ""
#             section = self._guess_section(page_text)
#             try:

#                 # Force the first column to be label for cash flow tables
#                 if section == "cash_flow":
#                     kpis = extract_kpi_rows(
#                         raw,
#                         prefer_first_column_labels=True,
#                         force_label_column=True   # NEW FLAG
#                     )
#                 else:
#                     kpis = extract_kpi_rows(
#                         raw,
#                         prefer_first_column_labels=self.prefer_first_column
#                     )

#             except Exception:
#                 logger.exception(f"Failed to extract KPI rows from table on page {page}")
#                 out["flags"].append({"page": page, "note": "kpi_extraction_failed"})
#                 continue
#             #till here

#             logger.debug(f"Table on page {page} guessed as section {section}; extracted {len(kpis)} rows")


#             if section == "balance_sheet":
#                 out["balance_sheet"].extend(kpis)
#             elif section == "pnl":
#                 out["pnl"].extend(kpis)
#             elif section == "cash_flow":
#                 out["cash_flow"].extend(kpis)
#             else:
#                 # attempt simple fallback: recognize words inside table labels
#                 labelled = any((row.get("label") for row in kpis))
#                 if labelled:
#                     # try to detect using label keywords inside labels
#                     placed = False
#                     for row in kpis:
#                         lbl = (row.get("label") or "").lower()
#                         if any(x in lbl for x in ["assets", "liabilities", "equity", "shareholders"]):
#                             out["balance_sheet"].append(row)
#                             placed = True
#                         elif any(x in lbl for x in ["revenue", "profit", "loss", "income", "turnover"]):
#                             out["pnl"].append(row)
#                             placed = True
#                         elif any(x in lbl for x in ["cash", "operating activities", "investing activities", "financing activities"]):
#                             out["cash_flow"].append(row)
#                             placed = True
#                         else:
#                             continue
#                     if not placed:
#                         out["flags"].append({"page": page, "note": "unclassified_but_has_labels"})
#                 else:
#                     out["flags"].append({"page": page, "note": "unclassified_table_no_labels"})
        
#         important_kpis = self._compute_important_kpis(out)

#         # convert to pydantic model for validation and normalization
#         try:    
#             final = ExtractionOutput(
#                 balance_sheet=out["balance_sheet"],
#                 pnl=out["pnl"],
#                 cash_flow=out["cash_flow"],
#                 flags=out["flags"],
#                 important_kpis=important_kpis,
#             )
#             return final.dict()
#         except Exception:
#             logger.exception("Failed to validate final output against schema")
#             # return raw out as fallback
#             return out

#     @staticmethod
#     def _guess_section(page_text: str) -> str:
#         """
#         Detect section type using ALL common variants seen in DRHP/RHP/AR.
#         """
#         if not page_text:
#             return "unknown"

#         t = page_text.lower()

#         # BALANCE SHEET keywords
#         bs_keywords = [
#             "balance sheet",
#             "statement of financial position",
#             "statement of assets and liabilities",
#             "assets and liabilities",
#             "summary of assets and liabilities",
#             "restated consolidated balance sheet",
#             "restated statement of assets",
#             "summary restated balance sheet",
#             "summary restated statement of assets",
#             "summary of restated balance sheet",
#             "summary of restated consolidated assets",
#             "summary of restated consolidated balance sheet",
#             "summary of balance sheet",
#             "summary balance sheet",
#             "assets & liabilities",
#             "assets and liability",
#             "restated financial position",
#             "restated consolidated statement of assets and liabilities"
#         ]

#         # PROFIT & LOSS keywords
#         pnl_keywords = [
#             "profit and loss",
#             "profit & loss",
#             "p&l",
#             "statement of profit",
#             "statement of profit and loss",
#             "consolidated p&l",
#             "summary restated profit",
#             "summary of profit and loss",
#             "summary profit and loss",
#             "restated consolidated profit",
#             "income statement",
#             "statement of income",
#             "total income",
#             "other comprehensive income",
#             "oci",
#             "restated consolidated statement of profit and loss"
#         ]

#         # CASH FLOW keywords
#         cf_keywords = [
#             "cash flow",
#             "cashflow",
#             "cash flows",
#             "statement of cash flows",
#             "summary cash flow",
#             "summary of cash flows",
#             "restated cash flows",
#             "restated consolidated cash flow",
#             "summary restated cash flows",
#             "summary restated consolidated cash flows",
#             "cash flow statement",
#             "cash flows statement",
#             "restated consolidated statement of cash flows",
#             "restated consolidated statement of cashflows"
#         ]

#         if any(k in t for k in bs_keywords):
#             return "balance_sheet"

#         if any(k in t for k in pnl_keywords):
#             return "pnl"

#         if any(k in t for k in cf_keywords):
#             return "cash_flow"

#         return "unknown"





"""
Parser orchestration: converts OCR outputs (pages_text + tables) into final JSON.

Strategy summary:
- For each table, attempt KPI extraction using table_extractor.extract_kpi_rows(...)
- Classify the table into balance_sheet / pnl / cash_flow using page text heuristics (keywords)
- Append extracted KPI rows to the matching section
- Provide flags for unclassified or suspicious tables

Usage:
    parser = ParserService(prefer_first_column_labels=True)
    result_dict = parser.parse(tables, pages_text)
"""
import logging
from typing import List, Dict, Any
from app.services.table_extractor import extract_kpi_rows
from app.schemas.output_schema import ExtractionOutput

logger = logging.getLogger("app.services.parser_service")


class ParserServiceError(Exception):
    pass


class ParserService:
    def __init__(self, prefer_first_column_labels: bool = True):
        self.prefer_first_column = bool(prefer_first_column_labels)
    
    def _compute_important_kpis(self, parsed):
        bs = parsed.get("balance_sheet", []) or []
        pnl = parsed.get("pnl", []) or []
        cf = parsed.get("cash_flow", []) or []

        def norm(s):
            if not s:
                return ""
            return (
                s.lower()
                .replace(" ", "")
                .replace("\u00a0", "")
                .replace("\u2009", "")
                .replace(".", "")
                .replace(":", "")
            )

        def is_number(x):
            return isinstance(x, (int, float))


        def extract_latest_single_value(row):
            """Return value from FIRST numeric column (latest: June 30, 2025)."""
            vals = row.get("values", {}) or {}
            for k in sorted(vals.keys()):
                try:
                    num = float(str(vals[k]).replace(",", ""))
                    return num
                except:
                    continue
            return None

        # -------------------------
        # Extract last-3-values (handles 4-col, 5-col and fallbacks)
        # -------------------------
        def extract_period_values(row):
            vals = row.get("values", {}) or {}

            # normalize numeric strings -> float
            clean_vals = {}
            for k,v in vals.items():
                try:
                    clean_vals[k] = float(str(v).replace(",", ""))
                except:
                    clean_vals[k] = None

            keys = sorted(clean_vals.keys())

            # 5 column pattern
            if "col_5" in clean_vals:
                mapping = {
                    "2025": clean_vals.get("col_3"),
                    "2024": clean_vals.get("col_4"),
                    "2023": clean_vals.get("col_5"),
                }
            # 4 column pattern
            elif "col_4" in clean_vals:
                mapping = {
                    "2025": clean_vals.get("col_2"),
                    "2024": clean_vals.get("col_3"),
                    "2023": clean_vals.get("col_4"),
                }
            else:
                # fallback: last 3 numeric columns
                numeric = [k for k in keys if clean_vals.get(k) is not None]
                if len(numeric) >= 3:
                    last3 = numeric[-3:]
                    mapping = {
                        "2025": clean_vals[last3[-1]],
                        "2024": clean_vals[last3[-2]],
                        "2023": clean_vals[last3[-3]],
                    }
                else:
                    mapping = {}

            latest = mapping.get("2025")

            return latest, {
                "latest": mapping.get("2025"),
                "prev1": mapping.get("2024"),
                "prev2": mapping.get("2023"),
            }


        # -------------------------
        # Row match helpers
        # -------------------------
        # ---------------------------------------
        # MATCH HELPERS (old logic behavior)
        # ---------------------------------------
        def match_exact_label(rows, keywords):
            for row in rows:
                lbl = norm(row.get("label"))
                if any(k == lbl for k in keywords):
                    return row
            return None

        def match_contains(rows, keywords, exclude=None):
            for row in rows:
                lbl = norm(row.get("label"))
                if exclude and any(e in lbl for e in exclude):
                    continue
                if any(k in lbl for k in keywords):
                    return row
            return None
        # -------------------------
        # Collect KPIs (latest + periods)
        # -------------------------
        kpi = {}

        def assign_kpi(name, row):
            if not row:
                return
            single_latest = extract_latest_single_value(row)   # <— correct latest value

            _, periods = extract_period_values(row)            # <— for charts (unchanged)

            if is_number(single_latest):
                kpi[name] = single_latest                      # <— FIRST COLUMN!
                kpi[f"{name}_periods"] = periods

        # ---------------------------------------
        # 1️⃣ TOTAL ASSETS
        # ---------------------------------------
        assets_row = match_contains(
            bs,
            ["totalassets"],
            exclude=["liabilitiesandequity", "assetsliabilities"]
        )
        assign_kpi("total_assets", assets_row)

        # ---------------------------------------
        # 2️⃣ TOTAL EQUITY
        # ---------------------------------------
        equity_row = match_exact_label(bs, ["totalequity"])
        assign_kpi("total_equity", equity_row)

        # fallback: equity attributable + NCI
        if "total_equity" not in kpi:
            eq_attr = match_contains(bs, ["equityattributable"])
            nci = match_contains(bs, ["noncontrollinginterest", "n on-controllinginterest"])

            if eq_attr:
                eq_latest = extract_latest_single_value(eq_attr)
                _, p1 = extract_period_values(eq_attr)

                if nci:
                    _, p2 = extract_period_values(nci)
                    nci_latest = p2.get("latest")
                else:
                    nci_latest = 0
                    p2 = {"prev1": 0, "prev2": 0}

                total_equity_val = (eq_latest or 0) + (nci_latest or 0)
                kpi["total_equity"] = total_equity_val
                kpi["total_equity_periods"] = {
                    "latest": total_equity_val,
                    "prev1": (p1.get("prev1") or 0) + (p2.get("prev1") or 0),
                    "prev2": (p1.get("prev2") or 0) + (p2.get("prev2") or 0),
                }

        # ---------------------------------------
        # 3️⃣ TOTAL LIABILITIES
        # ---------------------------------------
        liab_row = match_exact_label(bs, ["totalliabilities", "total liabilities"])
        if not liab_row:
            liab_row = match_contains(
                bs,
                ["totalliabilities", "totalliability", "totalliabilitie"],
                exclude=["equity", "assets"]
            )

        if liab_row:
            assign_kpi("total_liabilities", liab_row)

        else:
            # fallback to current + non-current
            tcl = match_contains(bs, ["totalcurrentliabilities", "total current liabilities"])
            tncl = match_contains(bs, ["totalnoncurrentliabilities", "total non-current liabilities"])

            tcl_latest, tcl_periods = extract_period_values(tcl) if tcl else (None, {})
            tncl_latest, tncl_periods = extract_period_values(tncl) if tncl else (None, {})

            if tcl_latest is not None and tncl_latest is not None:
                total_latest = tcl_latest + tncl_latest
                kpi["total_liabilities"] = total_latest
                kpi["total_liabilities_periods"] = {
                    "latest": total_latest,
                    "prev1": (tcl_periods.get("prev1") or 0) + (tncl_periods.get("prev1") or 0),
                    "prev2": (tcl_periods.get("prev2") or 0) + (tncl_periods.get("prev2") or 0),
                }

        # ---------------------------------------
        # 4️⃣ PNL KPIs
        # ---------------------------------------
        rev_row = match_contains(pnl, ["totalincome", "totalrevenue", "revenue"])
        assign_kpi("revenue", rev_row)

        profit_row = match_contains(pnl, ["profitfortheperiod", "profit"])
        assign_kpi("net_profit", profit_row)

        # ---------------------------------------
        # 5️⃣ CASH FLOW KPIs
        # ---------------------------------------
        ocf_row = match_contains(cf, ["operatingactivities", "netcashfromoperating"])
        assign_kpi("operating_cash_flow", ocf_row)

        ncf_row = match_contains(cf, [
            "net(decrease)/increaseincash",
            "netcash",
            "netcashflow",
            "netincreaseincash",
            "netdecreaseincash",
            "netcashfromoperating",
        ])
        assign_kpi("net_cash_flow", ncf_row)

        # ---------------------------------------
        # RATIOS (use latest values only - safe checks)
        # ---------------------------------------
        ratios = {}
        ta = kpi.get("total_assets")
        te = kpi.get("total_equity")
        tl = kpi.get("total_liabilities")
        rev = kpi.get("revenue")
        npv = kpi.get("net_profit")
        cf_latest = kpi.get("net_cash_flow")

        # make sure denominators are valid (non-zero)
        if is_number(te) and is_number(tl) and te != 0:
            ratios["debt_equity_ratio"] = tl / te

        if is_number(ta) and is_number(te) and ta != 0:
            ratios["equity_ratio"] = te / ta

        if is_number(rev) and is_number(npv) and rev != 0:
            ratios["net_profit_margin"] = npv / rev

        if is_number(npv) and is_number(te) and te != 0:
            ratios["roe"] = npv / te

        if is_number(npv) and is_number(ta) and ta != 0:
            ratios["roa"] = npv / ta

        if is_number(npv) and is_number(cf_latest) and npv != 0:
            ratios["cashflow_to_netincome"] = cf_latest / npv

        # attach ratios
        if ratios:
            kpi["ratios"] = ratios

        return kpi




    def parse(self, tables: List[Dict[str, Any]], pages_text: Dict[int, str]) -> Dict[str, Any]:
        """
        tables: List of { "page": int, "table": List[List] }
        pages_text: Dict[page_number -> text]
        returns: dict conforming to ExtractionOutput
        """
        out = {
            "balance_sheet": [],
            "pnl": [],
            "cash_flow": [],
            "flags": [],
        }

        if not tables:
            logger.warning("No tables provided to parser_service.parse")
        else:
            logger.info(
                f"Parsing tables in range: pages {tables[0].get('page')} - {tables[-1].get('page')} , total tables: {len(tables)}"
            )

        for t in tables:
            page = t.get("page")
            raw = t.get("table", [])
            # try:
            #     kpis = extract_kpi_rows(raw, prefer_first_column_labels=self.prefer_first_column)
            # except Exception:
            #     logger.exception(f"Failed to extract KPI rows from table on page {page}")
            #     out["flags"].append({"page": page, "note": "kpi_extraction_failed"})
            #     continue
            page_text = pages_text.get(page, "") or ""
            section = self._guess_section(page_text)
            try:

                # Force the first column to be label for cash flow tables
                if section == "cash_flow":
                    kpis = extract_kpi_rows(
                        raw,
                        prefer_first_column_labels=True,
                        force_label_column=True   # NEW FLAG
                    )
                else:
                    kpis = extract_kpi_rows(
                        raw,
                        prefer_first_column_labels=self.prefer_first_column
                    )

            except Exception:
                logger.exception(f"Failed to extract KPI rows from table on page {page}")
                out["flags"].append({"page": page, "note": "kpi_extraction_failed"})
                continue
            #till here

            logger.debug(f"Table on page {page} guessed as section {section}; extracted {len(kpis)} rows")


            if section == "balance_sheet":
                out["balance_sheet"].extend(kpis)
            elif section == "pnl":
                out["pnl"].extend(kpis)
            elif section == "cash_flow":
                out["cash_flow"].extend(kpis)
            else:
                # attempt simple fallback: recognize words inside table labels
                labelled = any((row.get("label") for row in kpis))
                if labelled:
                    # try to detect using label keywords inside labels
                    placed = False
                    for row in kpis:
                        lbl = (row.get("label") or "").lower()
                        if any(x in lbl for x in ["assets", "liabilities", "equity", "shareholders"]):
                            out["balance_sheet"].append(row)
                            placed = True
                        elif any(x in lbl for x in ["revenue", "profit", "loss", "income", "turnover"]):
                            out["pnl"].append(row)
                            placed = True
                        elif any(x in lbl for x in ["cash", "operating activities", "investing activities", "financing activities"]):
                            out["cash_flow"].append(row)
                            placed = True
                        else:
                            continue
                    if not placed:
                        out["flags"].append({"page": page, "note": "unclassified_but_has_labels"})
                else:
                    out["flags"].append({"page": page, "note": "unclassified_table_no_labels"})
        
        important_kpis = self._compute_important_kpis(out)

        # convert to pydantic model for validation and normalization
        try:    
            final = ExtractionOutput(
                balance_sheet=out["balance_sheet"],
                pnl=out["pnl"],
                cash_flow=out["cash_flow"],
                flags=out["flags"],
                important_kpis=important_kpis,
            )
            return final.dict()
        except Exception:
            logger.exception("Failed to validate final output against schema")
            # return raw out as fallback
            return out

    @staticmethod
    def _guess_section(page_text: str) -> str:
        """
        Detect section type using ALL common variants seen in DRHP/RHP/AR.
        """
        if not page_text:
            return "unknown"

        t = page_text.lower()

        # BALANCE SHEET keywords
        bs_keywords = [
            "balance sheet",
            "statement of financial position",
            "statement of assets and liabilities",
            "assets and liabilities",
            "summary of assets and liabilities",
            "restated consolidated balance sheet",
            "restated statement of assets",
            "restated statement of assets and liabilities",
            "restated consolidated statement of assets and liabilities",
            "restated consolidated statement of assets & liabilities",
            "summary restated balance sheet",
            "summary restated statement of assets",
            "summary of restated balance sheet",
            "summary of restated consolidated assets",
            "summary of restated consolidated balance sheet",
            "summary of balance sheet",
            "summary balance sheet",
            "summary restated consolidated balance sheet",
            "assets & liabilities",
            "assets and liability",
            "restated financial position",
            "restated consolidated statement of assets and liabilities",
            "summary of restated assets and liabilities",
            "summary restated assets and liabilities",
        ]

        # PROFIT & LOSS keywords
        pnl_keywords = [
            "profit and loss",
            "profit & loss",
            "p&l",
            "statement of profit",
            "statement of profit and loss",
            "consolidated p&l",
            "summary restated profit",
            "summary of profit and loss",
            "summary profit and loss",
            "restated consolidated profit",
            "income statement",
            "statement of income",
            "total income",
            "other comprehensive income",
            "oci",
            "restated consolidated statement of profit and loss",
            "summary restated profit and loss",
            "summary of restated profit and loss",
            "restated consolidated profit and loss",
            "statement of profit & loss",
            "restated statement of profit and loss",
            "restated consolidated statement of profit and loss",
            "restated consolidated statement of profit & loss",
            "summary consolidated profit and loss",
            "profit for the year",
            "profit for the period",
            "income statement",
        ]

        # CASH FLOW keywords
        cf_keywords = [
            "cash flow",
            "cashflow",
            "cash flows",
            "cashflows",
            "statement of cash flows",
            "summary cash flow",
            "summary of cash flows",
            "restated cash flows",
            "summary cash flows",
            "restated consolidated cash flow",
            "summary restated cash flows",
            "summary restated consolidated cash flows",
            "cash flow statement",
            "cash flows statement",
            "restated consolidated statement of cash flows",
            "restated consolidated statement of cashflows",
            "summary restated cash flows",
            "summary of restated cash flows",
            "restated consolidated cash flows",
            "summary consolidated cash flows",
            "net cash",
        ]

        if any(k in t for k in bs_keywords):
            return "balance_sheet"

        if any(k in t for k in pnl_keywords):
            return "pnl"

        if any(k in t for k in cf_keywords):
            return "cash_flow"

        return "unknown"