# FinPixe Migration Tool — Powered by RIM-BMT v3.0
### Enterprise Tally Prime → FinPixe Cloud ERP Migration Engine

[![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green?logo=fastapi)](https://fastapi.tiangolo.com)
[![MySQL](https://img.shields.io/badge/MySQL-8.0-orange?logo=mysql)](https://mysql.com)
[![License](https://img.shields.io/badge/License-Proprietary-red)](LICENSE)

**FinPixe Migration Tool** is a mission-critical, enterprise-grade data migration platform that transfers an entire company's financial history — ledgers, vouchers, inventory, customers, vendors, GST records, and opening balances — from **Tally Prime / Tally ERP 9** into the **FinPixe Cloud ERP** with 100% mathematical accuracy and cryptographic audit certification.

---

## 🔒 Architecture & IP Protection

This repository ships the **public-facing UI layer** and **pre-compiled RIM binary runtime**. The proprietary **RIM (Robust Invariant Migration) Engine** source code — which contains the 14-phase migration pipeline and the System 2 mathematical invariant engine — is protected under trade-secret law and is **not distributed** in this repository.

| Component | What's Included | Status |
|-----------|----------------|--------|
| `finfixe_migration_ui.py` | FastAPI UI + API Gateway (5-panel dashboard) | ✅ Full Source |
| `rim/engine.py` | RIM Engine interface module | ✅ Full Source |
| `rim/pyarmor_runtime_000000/` | Pre-compiled native binary runtime | ✅ Binary Only |
| `rim/management/commands/` | 14-Phase migration pipeline | 🔒 Proprietary (not distributed) |
| `requirements.txt` | All Python dependencies | ✅ Included |

---

## 🏛️ 3-System Cognitive Architecture

### System 1 — Cognitive Ingestion & Auto-Healing
- **Live Port 9000 Protocol**: Streams data directly from a running Tally instance via HTTP TDL requests — no manual export needed.
- **Byte-Level XML Sanitizer**: Detects and strips illegal control characters (`\x00–\x1F`), invalid XML entities (`&#4;`, `&#0;`), and UTF-16 BOM headers before the parser runs.
- **Accounting Axiom Classifier**: Automatically maps custom Tally ledger groups to FinPixe's `Asset / Liability / Equity / Income / Expense` taxonomy using semantic keyword rules.
- **Inventory Allocation Extractor**: Extracts and merges accounting allocation legs buried inside `<ALLINVENTORYENTRIES.LIST>` — the most common cause of broken double-entry in Tally migrations.

### System 2 — Deterministic Mathematical Invariant Audit
Four non-negotiable accounting laws are enforced as mathematical proofs before any record is written to the database:

| # | Invariant Law | Formula |
|---|--------------|---------|
| 1 | **Double-Entry Equilibrium** | `∑ Debit = ∑ Credit` for every voucher |
| 2 | **Fundamental Accounting Equation** | `Assets = Liabilities + Equity` |
| 3 | **AR Subledger Consensus** | `GL(Sundry Debtors) = ∑ Open Customer Invoices` |
| 4 | **AP Subledger Consensus** | `GL(Sundry Creditors) = ∑ Open Vendor Bills` |
| 5 | **Inventory Non-Negativity** | `∀ items: Qty ≥ 0 ∧ Value ≥ 0` |

### System 3 — Cryptographic State Proof & Governance
- **SHA-256 Merkle Seal**: Produces a tamper-evident cryptographic fingerprint of the final migrated state for SOX / SEBI / Big-4 audit compliance.
- **Quarantine Ledger**: Every anomaly is intercepted, classified, and displayed in the UI — no silent failures.
- **Human Touch Console**: CFO/Accountant review panel for records that require manual approval before final commit.

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10 or higher
- MySQL 8.0 or higher
- A running FinPixe Cloud ERP instance (target database)

### Installation

```bash
git clone https://github.com/budstechconsultancy-svg/finpixe_migration_tool.git
cd finpixe_migration_tool
pip install -r requirements.txt
```

### Environment Configuration

Configure the backend runner location if your Django backend is located in a custom path:

```bash
# Linux / EC2:
export FINPIXE_BACKEND_MANAGE_PY="/home/ubuntu/finpixe-deploy/backend/manage.py"

# Windows (PowerShell):
$env:FINPIXE_BACKEND_MANAGE_PY="C:\path\to\finpixe-backend\manage.py"
```

> **Note on Migration Pipeline Execution:**
> The Migration UI validates that `manage.py` exists and contains the licensed `run_full_migration` command before execution. If the proprietary command is not installed in the target backend, the UI will report the missing dependency. Contact `budstechconsultancy@gmail.com` for licensed pipeline modules.


### Launch the Web UI

**Option A — Batch file (Windows):**
```
Double-click  run_ui.bat
```

**Option B — Terminal:**
```bash
python -m uvicorn finfixe_migration_ui:app --host 0.0.0.0 --port 8888
```

Then open your browser at: **http://localhost:8888**

---

## 🖥️ Dashboard Panels

| Panel | Purpose |
|-------|---------|
| **Data Migration** | Configure DB credentials, select source (Live Port 9000 or XML upload), set Tenant UUID, run the pipeline |
| **Executive Dashboard** | Live KPIs — total entities migrated, Trial Balance, AR/AP outstandings, System 2 invariant matrix |
| **Error & Audit Logs** | Exception Quarantine Ledger with rich voucher cards, one-click RIM Auto-Fix, Excel export |
| **Human Touch Console** | Records flagged for CFO/Accountant review and approval |
| **SHA-256 Ledger** | Cryptographic migration certificate for statutory audit sign-off |

---

## 📦 The 14-Phase Migration Pipeline

| Phase | Domain |
|:-----:|--------|
| 1 | Accounting Masters & Chart of Accounts Hierarchy |
| 2 | Financial Vouchers & Double-Entry Journal Entries |
| 3 | Inventory Pipeline, Godowns & Stock Items |
| 4 | GST Reconciliation & Tax Masters |
| 5 | Bank Staging & BRS Allocations |
| 6 | Vendor & Customer AR/AP (Bill-by-Bill) |
| 7 | Payroll Engine & Employee Records |
| 8 | TDS / Direct Tax Framework |
| 9 | Manufacturing & Bill of Materials |
| 10 | Trade Finance (LCs / BGs) |
| 11 | E-Invoicing & IRN Pipeline |
| 12 | Cost Centres & Operational Allocations |
| 13 | Fixed Assets & Depreciation Register |
| 14 | Security & RBAC Roles |

---

## 📜 Statutory & Compliance

- ✅ **Indian GST** — CGST, SGST, IGST, Cess normalization
- ✅ **TDS** — Section 206AA, 194C, 194J
- ✅ **Ind AS Double-Entry** — mathematically certified via System 2
- ✅ **Non-Destructive Idempotency** — safe to re-run; never creates duplicate records
- ✅ **SHA-256 Audit Seal** — admissible for Big-4 and SEBI audits

---

## 📄 License

**Proprietary — All Rights Reserved © Budstech Consultancy**

The RIM Engine, migration pipeline logic, and invariant verification system are proprietary intellectual property. This software may not be copied, modified, or redistributed without a commercial license.

For licensing enquiries: **budstechconsultancy@gmail.com**
