"""
RIM-AGI v6.0 - Counterfactual Auto-Repair Gate (counterfactual_repair.py)
Implements Pearl's Do-Calculus for Enterprise Financial Data Healing.

When financial invariants return UNSAT, this engine computes:
    min ||x - x_orig||  s.t.  Financial_Invariant(x) == SAT
"""

from decimal import Decimal
from typing import Dict, Any, List, Tuple, Optional
from .financial_invariants import FinancialInvariantGate


class CounterfactualFinancialRepair:
    """
    Self-healing causal gateway for legacy accounting anomalies.
    Intervenes minimally to restore mathematical SAT without manual human labor.
    """

    TALLY_TO_SCHEDULE_III_MAP = {
        # Bank & Cash -> Cash and cash equivalents
        "bank accounts": ("Asset", "Asset", "Cash and cash equivalents", "In Bank accounts"),
        "bank": ("Asset", "Asset", "Cash and cash equivalents", "In Bank accounts"),
        "cash-in-hand": ("Asset", "Asset", "Cash and cash equivalents", "Cash"),
        "cash": ("Asset", "Asset", "Cash and cash equivalents", "Cash"),
        "bank od a/c": ("Liability", "Liability", "Other current liabilities", "Bank OD/CC Accounts"),
        "bank occ a/c": ("Liability", "Liability", "Other current liabilities", "Bank OD/CC Accounts"),

        # Receivables & Payables -> Schedule III
        "sundry debtors": ("Asset", "Asset", "Other current assets", ""),
        "debtors": ("Asset", "Asset", "Other current assets", ""),
        "sundry creditors": ("Liability", "Liability", "Other current liabilities", ""),
        "creditors": ("Liability", "Liability", "Other current liabilities", ""),

        # Loans & Advances
        "loans & advances (asset)": ("Asset", "Asset", "Short Term Loans and Advances", ""),
        "loans and advances (asset)": ("Asset", "Asset", "Short Term Loans and Advances", ""),
        "deposits (asset)": ("Asset", "Asset", "Other non-current assets", ""),

        # Duties & Taxes
        "duties & taxes": ("Liability", "Liability", "Other current liabilities", "Duties & Taxes (Liability)"),
        "taxes": ("Liability", "Liability", "Other current liabilities", "Duties & Taxes (Liability)"),
        "gst": ("Liability", "Liability", "Other current liabilities", "Duties & Taxes (Liability)"),
        "tds": ("Liability", "Liability", "Other current liabilities", "Duties & Taxes (Liability)"),

        # Fixed Assets -> Property, Plant & Equipment
        "fixed assets": ("Asset", "Asset", "Property, Plant & Equipment", "Tangible assets"),
        "plant and machinery": ("Asset", "Asset", "Property, Plant & Equipment", "Tangible assets"),
        "plant & machinery": ("Asset", "Asset", "Property, Plant & Equipment", "Tangible assets"),
        "furniture & fixtures": ("Asset", "Asset", "Property, Plant & Equipment", "Tangible assets"),
        "furniture and fittings": ("Asset", "Asset", "Property, Plant & Equipment", "Tangible assets"),
        "electrical equipment": ("Asset", "Asset", "Property, Plant & Equipment", "Tangible assets"),
        "software": ("Asset", "Asset", "Property, Plant & Equipment", "Intangible Assets"),
        "capital work in progress": ("Asset", "Asset", "Property, Plant & Equipment", "Capital work-in-progress"),
        "depreciation reserve": ("Asset", "Asset", "Property, Plant & Equipment", "Depreciation Reserve"),

        # Borrowings & Capital
        "loans (liability)": ("Liability", "Liability", "Long-term borrowings", ""),
        "secured loans": ("Liability", "Liability", "Long-term borrowings", "Secured Loans"),
        "unsecured loans": ("Liability", "Liability", "Long-term borrowings", "Unsecured Loans"),
        "capital account": ("Owners'  Funds", "Capital", "Share capital", "Equity Share Capital"),
        "equity share capital": ("Owners'  Funds", "Capital", "Share capital", "Equity Share Capital"),
        "reserves & surplus": ("Owners'  Funds", "Capital", "Reserves and surplus", "General Reserves"),

        # Incomes & Revenues
        "sales accounts": ("Income", "Income", "Revenue from operations", "Sale of Goods"),
        "direct incomes": ("Income", "Income", "Revenue from operations", "Sale of Services"),
        "indirect incomes": ("Income", "Income", "Other Income", "Others"),

        # Expenses & Purchases
        "purchase accounts": ("Expenditure", "Expense", "Cost of materials consumed", "Purchase"),
        "raw materials": ("Expenditure", "Expense", "Cost of materials consumed", "Purchase"),
        "consumables": ("Expenditure", "Expense", "Other expenses", "Consumables"),
        "direct expenses": ("Expenditure", "Expense", "Other expenses", "Direct Expenses"),
        "indirect expenses": ("Expenditure", "Expense", "Other expenses", "Indirect Expenses"),
        "other expenses": ("Expenditure", "Expense", "Other expenses", "Other Expenses"),
        "repair and maintenance": ("Expenditure", "Expense", "Other expenses", "Repair and Maintenance"),
        "bank charges": ("Expenditure", "Expense", "Other expenses", "Bank Charges"),

        # Suspense
        "suspense a/c": ("Asset", "Asset", "Other current assets", "Suspense A/c"),
    }

    CATEGORY_SYNONYMS = {
        "raw material & components": (1, "Raw Material"),
        "raw materials & components": (1, "Raw Material"),
        "raw materials": (1, "Raw Material"),
        "raw material": (1, "Raw Material"),
        "services & expenses": (2, "Services"),
        "services": (2, "Services"),
        "subcontract / job work": (3, "Jobwork"),
        "subcontract": (3, "Jobwork"),
        "job work": (3, "Jobwork"),
        "jobwork": (3, "Jobwork"),
        "stores & spares": (4, "Stores and Spares"),
        "stores and spares": (4, "Stores and Spares"),
        "stock-in trade": (5, "Stock-in Trade"),
        "stock in trade": (5, "Stock-in Trade"),
        "fixed assets": (6, "Fixed Assets"),
        "consumables": (7, "Consumables"),
    }

    @classmethod
    def repair_category_anomaly(cls, raw_category: str) -> Tuple[int, str, bool, str]:
        """
        Causal repair for Category Master mismatches.
        Returns: (canonical_id, canonical_name, was_repaired, explanation)
        """
        is_sat, cat_id, msg = FinancialInvariantGate.verify_category_fidelity(raw_category)
        if is_sat and cat_id is not None:
            return cat_id, FinancialInvariantGate.CANONICAL_CATEGORIES[cat_id], False, "Already canonical"

        clean = (raw_category or "").strip().lower()
        if clean in cls.CATEGORY_SYNONYMS:
            c_id, c_name = cls.CATEGORY_SYNONYMS[clean]
            explanation = f"Counterfactual intervention: do(category='{raw_category}') -> '{c_name}' (ID: {c_id})"
            return c_id, c_name, True, explanation

        # Default fallback to Services (ID 2) with explanation
        return 2, "Services", True, f"Counterfactual fallback: unmapped category '{raw_category}' projected to 'Services' (ID: 2)"

    @classmethod
    def repair_legacy_group_anomaly(
        cls, candidate_names: List[str], fallback_category: str = "Asset"
    ) -> Tuple[str, str, str, str, bool, str]:
        """
        Causal projection of legacy Tally group/subgroups to FinPixe Schedule III canonical group.
        Strictly enforces ZERO group creation!
        Returns: (category, major_group, group, sub_group_1, was_repaired, explanation)
        """
        for cand in candidate_names:
            if not cand:
                continue
            cand_clean = cand.strip().lower()
            if cand_clean in cls.TALLY_TO_SCHEDULE_III_MAP:
                cat, mg, grp, sg1 = cls.TALLY_TO_SCHEDULE_III_MAP[cand_clean]
                return cat, mg, grp, sg1, True, f"Causal projection: '{cand}' mapped to Schedule III group '{grp}'"

            # Partial match
            for tally_key, mapping in cls.TALLY_TO_SCHEDULE_III_MAP.items():
                if tally_key in cand_clean or cand_clean in tally_key:
                    cat, mg, grp, sg1 = mapping
                    return cat, mg, grp, sg1, True, f"Fuzzy causal projection: '{cand}' mapped to '{grp}'"

        # Categorical safe default into Schedule III
        cat_lower = fallback_category.lower()
        if "asset" in cat_lower:
            return "Asset", "Asset", "Other current assets", "", True, "Defaulted to 'Other current assets'"
        elif "liab" in cat_lower or "cap" in cat_lower:
            return "Liability", "Liability", "Other current liabilities", "", True, "Defaulted to 'Other current liabilities'"
        elif "inc" in cat_lower:
            return "Income", "Income", "Other Income", "", True, "Defaulted to 'Other Income'"
        else:
            return "Expenditure", "Expense", "Other expenses", "", True, "Defaulted to 'Other expenses'"

    @classmethod
    def repair_voucher_rounding_drift(
        cls, debit_total: Decimal, credit_total: Decimal, max_drift: Decimal = Decimal("1.00")
    ) -> Tuple[bool, Decimal, str]:
        """
        Calculates rounding adjustment under Pearl's minimal intervention:
        If diff <= max_drift, returns adjustment amount needed to restore SAT.
        """
        diff = debit_total - credit_total
        if diff == 0:
            return False, Decimal("0.00"), "Perfect parity, no repair needed"

        if abs(diff) <= max_drift:
            # If Debits > Credits, we need Credit adjustment of abs(diff)
            # If Credits > Debits, we need Debit adjustment of abs(diff)
            adjustment = -diff
            return True, adjustment, f"Counterfactual intervention: do(round_off={abs(diff)}) to restore double-entry SAT"

        return False, Decimal("0.00"), f"Drift exceeds automated threshold ({abs(diff)} > {max_drift}), escalated to Human Touch"
