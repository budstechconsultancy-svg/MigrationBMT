"""
RIM-AGI v6.0 - Master Migration Engine (engine.py)
Unified Interface for Neuro-Symbolic Mathematical Verification & Auto-Repair.
"""

from decimal import Decimal
from typing import Dict, Any, List, Tuple, Optional
from .financial_invariants import FinancialInvariantGate
from .counterfactual_repair import CounterfactualFinancialRepair


class RIMAGIv6Engine:
    """
    RIM-AGI v6.0 Core Gateway for Financial Migration.
    Acts as the System 2 formal reasoning and error-repair gate for BMT v3.0.
    """

    VERSION = "6.0.0-PROD"

    def __init__(self):
        self.gate = FinancialInvariantGate
        self.repair = CounterfactualFinancialRepair

    def verify_double_entry(
        self, debit_total: Decimal, credit_total: Decimal
    ) -> Tuple[bool, Decimal, str]:
        """
        Verify double-entry parity.
        """
        return self.gate.verify_double_entry_parity(debit_total, credit_total)

    def repair_rounding_if_needed(
        self, debit_total: Decimal, credit_total: Decimal, max_drift: Decimal = Decimal("1.00")
    ) -> Tuple[bool, Decimal, str]:
        """
        Counterfactually repairs rounding drift if within permissible threshold.
        """
        return self.repair.repair_voucher_rounding_drift(debit_total, credit_total, max_drift)

    def project_group_to_schedule_iii(
        self, candidate_names: List[str], fallback_category: str = "Asset"
    ) -> Tuple[str, str, str, str, str]:
        """
        Projects any legacy Tally group/subgroup chain strictly onto FinPixe's 35 Schedule III groups.
        Guarantees ZERO new groups are created.
        Returns: (category, major_group, group, sub_group_1, diagnostic)
        """
        cat, mg, grp, sg1, was_repaired, diag = self.repair.repair_legacy_group_anomaly(
            candidate_names, fallback_category
        )
        return cat, mg, grp, sg1, diag

    def project_vendor_category(
        self, raw_category: str
    ) -> Tuple[int, str, bool, str]:
        """
        Validates or repairs vendor category strings into exact Category Master IDs and names.
        Returns: (category_id, category_name, was_repaired, explanation)
        """
        return self.repair.repair_category_anomaly(raw_category)

    def audit_reconciliation_invariants(
        self,
        total_open_dr: Decimal,
        total_open_cr: Decimal,
        voucher_dr: Decimal,
        voucher_cr: Decimal
    ) -> Dict[str, Any]:
        """
        Performs full end-to-end mathematical invariant audit across all phases.
        """
        open_is_sat, open_var, open_msg = self.gate.verify_double_entry_parity(total_open_dr, total_open_cr)
        vch_is_sat, vch_var, vch_msg = self.gate.verify_double_entry_parity(voucher_dr, voucher_cr)

        grand_dr = total_open_dr + voucher_dr
        grand_cr = total_open_cr + voucher_cr
        grand_is_sat, grand_var, grand_msg = self.gate.verify_double_entry_parity(grand_dr, grand_cr)

        return {
            "version": self.VERSION,
            "opening_balances": {
                "total_dr": float(total_open_dr),
                "total_cr": float(total_open_cr),
                "variance": float(open_var),
                "is_sat": open_is_sat,
                "diagnostic": open_msg
            },
            "voucher_transactions": {
                "total_dr": float(voucher_dr),
                "total_cr": float(voucher_cr),
                "variance": float(vch_var),
                "is_sat": vch_is_sat,
                "diagnostic": vch_msg
            },
            "grand_total": {
                "total_dr": float(grand_dr),
                "total_cr": float(grand_cr),
                "variance": float(grand_var),
                "is_sat": grand_is_sat,
                "diagnostic": grand_msg
            },
            "overall_status": "CONSERVED" if grand_is_sat else "DRIFT_DETECTED"
        }
