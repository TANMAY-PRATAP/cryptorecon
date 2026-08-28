# 🛡️ CryptoRecon v4.0 Master — Operational Manual & Forensics Guide
**Autonomous Multi-Hop Blockchain Intelligence, Mule Ring Clustering & Statutory Evidence Engine**

---

## 📌 Executive Summary
**CryptoRecon** is an advanced on-chain cryptocurrency forensic investigation and fund recovery platform engineered for Law Enforcement Agencies (LEAs), the Indian Cyber Crime Coordination Centre (I4C/1930), Financial Intelligence Units (FIU-IND), and statutory compliance officers.

Modern cyber fraudsters exploit rapid smurfing, nested mule rings, and non-compliant offshore Virtual Asset Service Providers (VASPs) to siphon victim funds within minutes. CryptoRecon automates multi-hop tracing across heterogeneous blockchains, prunes transaction dust via dynamic continuous flow rate (CFR) mathematical models, detects and aggregates mule rings, resolves mixer breakpoints, and instantly generates court-admissible statutory notices under the **Bharatiya Nagarik Suraksha Sanhita (BNSS), 2023** and **Bharatiya Sakshya Adhiniyam (BSA), 2023**.

---

## 🌟 Core Architecture & Key Features

```
                               ┌──────────────────────────────────────────────┐
                               │       NCRP / 1930 Cyber Fraud Intake         │
                               └──────────────────────┬───────────────────────┘
                                                      │
                                                      ▼
                               ┌──────────────────────────────────────────────┐
                               │  Autonomous Multi-Chain Ingestion & Tracing  │
                               │   (Ethereum EVM, TRON TRC-20, Bitcoin UTXO)  │
                               └──────────────────────┬───────────────────────┘
                                                      │
                       ┌──────────────────────────────┴──────────────────────────────┐
                       ▼                                                             ▼
       ┌────────────────────────────────┐                            ┌────────────────────────────────┐
       │   Dynamic CFR Pruning Engine   │                            │   Dual-Stack VASP Attributor   │
       │ (Filters sub-floor dust noise) │                            │ (Tier 0-3 Sub-second Profiler) │
       └───────────────┬────────────────┘                            └───────────────┬────────────────┘
                       │                                                             │
                       └──────────────────────────────┬──────────────────────────────┘
                                                      │
                                                      ▼
                               ┌──────────────────────────────────────────────┐
                               │    Mule Ring Aggregator & Smurfing Engine    │
                               │  (Collapses high-fanout intermediary rings)  │
                               └──────────────────────┬───────────────────────┘
                                                      │
                                                      ▼
                               ┌──────────────────────────────────────────────┐
                               │    LightGBM Graph-AI Typology Classifier     │
                               │   (Mule Ring, Ransomware, Darknet Wash %)    │
                               └──────────────────────┬───────────────────────┘
                                                      │
                       ┌──────────────────────────────┴──────────────────────────────┐
                       ▼                                                             ▼
       ┌────────────────────────────────┐                            ┌────────────────────────────────┐
       │   P2P Banking Re-Stitching     │                            │ Statutory Legal Dispatch Suite │
       │  (Matches Indian Banks & UPI)  │                            │ (Section 94 BNSS / 65B BSA)    │
       └────────────────────────────────┘                            └────────────────────────────────┘
```

---

### 1. ⚡ Autonomous Multi-Chain Traversal
- **Ethereum & EVM**: Ingests both native ETH (`txlist`) and ERC-20 tokens (`tokentx` for USDT, USDC, DAI) simultaneously with zero data truncation.
- **TRON (TRC-20)**: Directly queries high-throughput TRC-20 USDT transfer contracts, decoding base58 addresses in real time.
- **Bitcoin (UTXO)**: Resolves Unspent Transaction Outputs using Common-Input Ownership Heuristics (CIOH) and multi-output transaction trees.
- **Auto-Detection**: Automatically detects blockchain network based on the input address format (e.g. `0x...` $\rightarrow$ EVM, `T...` $\rightarrow$ TRON, `bc1...` $\rightarrow$ Bitcoin).

### 2. 🧮 Dynamic Continuous Flow Rate (CFR) Pruning
To prevent graph explosion on high-activity target wallets, CryptoRecon utilizes dynamic continuous flow rate pruning:

$$\text{CFR Threshold} = \max\left(\text{Min Floor USDT},\; \frac{\text{Total Stolen Amount}}{\text{Dilution Factor} \times \text{FanOut}}\right)$$

- **Dust Elimination**: Prunes micro-transfers and dust spam while preserving the primary laundering trail.
- **Adaptive Dilution**: Dynamically adjusts traversal threshold as funds scatter deeper into multi-hop paths.

### 3. 🟠 Automated Mule Ring Smurfing Aggregation
- When an intermediary wallet splits funds across $5+$ downstream addresses (smurfing pattern), CryptoRecon compresses the chaotic web into a clean **Orange Rounded Mule Ring Node**.
- Displays the exact wallet count and total smurfed volume (e.g. `Mule Ring (15 wallets | 1,500 USDT)`).
- Clicking any Mule Ring opens the **Mule Drawer** with complete tabular breakdown: wallet addresses, split shares (%), parent ratios, and live balances.

### 4. 🏢 Dual-Stack VASP Attribution & Mixer Breakpoints
- **Tier-0 Direct Bloom Filter**: Instant sub-millisecond identification of verified Indian & global exchanges (CoinDCX, Binance, WazirX, OKX, Coinbase, Kraken).
- **Tier-1 Gas-Parent Ancestry**: Analyzes the funding origin of new smart contract wallets to attribute parent exchange hot vaults.
- **Mixer Breakpoints**: Flags cryptographic obfuscation protocols (Tornado Cash, Railgun) as **Purple Diamonds (100% Risk)**, identifying the cryptographic breakpoint where on-chain transparency ends.

### 5. 🤖 LightGBM Graph-AI Typology Engine
A machine-learning model trained on on-chain topology metrics (fan-out ratio, in-degree/out-degree entropy, velocity, holding time) that computes probabilistic risk classification:
- 🟠 **Mule Ring Smurfing** ($\%$)
- 🔵 **Ransomware Infiltration** ($\%$)
- 🟣 **Darknet Market Wash** ($\%$)

### 6. 🇮🇳 P2P Indian Banking Re-Stitching (1930 / I4C Simulation)
- Bridges on-chain cryptocurrency traces with Indian fiat off-ramps.
- Automatically calculates real-time **Seizure Value in Indian Rupees (INR)**:
  $$\text{Seizure Value (INR)} = \text{Total Suspicious USD Transferred} \times 90.25$$
- Displays Beneficiary Name, Bank Account Number, IFSC Code, Bank Branch, and UPI VPA Handle.

### 7. ⚖️ Statutory Legal Notice Suite
- **Section 94 BNSS Notice**: 24-hour statutory order demanding immediate VASP account freezing, transaction logs, KYC documents, and IP audit trails under Section 94 of the Bharatiya Nagarik Suraksha Sanhita, 2023.
- **Section 65B BSA Digital Evidence Certificate**: Cryptographically hashed (SHA-256) certificate verifying electronic blockchain evidence authenticity and RPC block Merkle root hash under Section 65B of the Bharatiya Sakshya Adhiniyam, 2023.
- **1930 CFCFRMS Freeze**: Dispatches automated emergency freeze triggers across Indian banking settlement gateways.

---

## 🎨 Visual Forensic Legend & Canvas Guide

| Node Type | Color Code | Shape | Description & Risk Tier |
| :--- | :--- | :--- | :--- |
| **Suspect Wallet / Exploiter** | 🔴 `#ef4444` (Crimson Red) | Circle | Primary target or high-fraud address ($\text{Risk} \ge 71$). |
| **Medium Risk Intermediary** | 🟡 `#f59e0b` (Amber Yellow) | Circle | Multi-hop transfer intermediary ($36 \le \text{Risk} \le 70$). |
| **Low Risk / Clean Peer** | 🟢 `#10b981` (Emerald Green) | Circle | Inactive or clean wallet with minimal risk ($\text{Risk} \le 35$). |
| **VASP Nodal Hub** | 🔵 `#3b82f6` (Cobalt Blue) | Circle | Verified exchange hot wallet, treasury, or fiat gateway. |
| **Mule Ring Cluster** | 🟠 `#f97316` (Deep Orange) | Round Box | Collapsed multi-wallet smurfing ring ($5+$ splits). |
| **Mixer Breakpoint** | 🟣 `#a855f7` (Neon Purple) | Diamond | Cryptographic mixer pool (Tornado Cash, Railgun). |

---

## 🚀 Step-by-Step Operator Guide

### Step 1: Open Application
Navigate to the live application URL:
👉 **[https://cryptorecon.vercel.app](https://cryptorecon.vercel.app)**

### Step 2: Enter Complaint & Target Address
1. Input the **NCRP Case ID** (e.g., `NCRP-2026-98124`).
2. Paste the suspect wallet address in the search bar.
3. Observe the live validation badge: **`42/42 ✓`** (EVM), **`34/34 ✓`** (TRON), or **`Valid ✓`** (BTC).
4. The system automatically switches to the matching blockchain network dropdown.

### Step 3: Run Forensics Traversal
1. Click **`Run Traversal`** (or press `Enter`).
2. The engine executes multi-hop breadth-first traversal, queries live on-chain RPC nodes, applies CFR dust filtering, and constructs the interactive Cytoscape forensic graph.

### Step 4: Canvas Layout & Navigation
- **`Fit`**: Auto-centers the complete graph in viewport.
- **`Force-Directed`**: Expands organic radial physics layout.
- **`Tree`**: Organizes fund flows into top-to-bottom hierarchical layers (Hop 0 $\rightarrow$ Hop 1 $\rightarrow$ Hop 2).
- **Interactive Drag & Zoom**: Freely pan, zoom, and inspect transfer labels.

### Step 5: Evidence Inspection & Legal Action
1. Click any node or edge on the canvas:
   - **`Node Inspector` Tab**: Displays entity tag, blockchain, calibrated risk score, and attribution tier.
   - **`Risk & P2P` Tab**: Displays AI typology breakdown and reconstructed Indian P2P banking details.
   - **`Mule Ring` Tab**: Displays member wallets, split shares, and balances if a Mule Ring is selected.
2. Click **`Generate Section 94 BNSS Notice`** to download a legal freeze notice for the designated VASP compliance officer.
3. Click **`Download Section 65B BSA Certificate`** to obtain the court-admissible cryptographic evidence certificate.

---

## 🧪 Benchmark Test Addresses & Expected Outcomes

| Scenario | Target Wallet Address | Network | Expected Graph & Attribution |
| :--- | :--- | :--- | :--- |
| **High-Profile Exploiter** | `0x098B716B8Aaf21512996dC57EB0615e2383E2f96` | Ethereum | 🔴 Red Suspect Node (`Ronin Exploiter`), Multi-hop smurfing tree, Orange Mule Rings, ₹3,800+ Cr Seizure. |
| **Verified Exchange VASP** | `0x28C6c06298d514Db089934071355E5743bf21d60` | Ethereum | 🔵 Blue VASP Node (`Binance Vault 14`), 14 child payouts, Nodal compliance email populated. |
| **Cryptographic Mixer** | `0x0769fd68dFb93167989C6f7254cd0D766Fb2841F` | Ethereum | 🟣 Purple Diamond Node (`Tornado.Cash`), 100 Risk Score, Critical Breakpoint banner. |
| **High Volume Whale** | `0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045` | Ethereum | 🔴 Multi-token edge labels ($9.4M USDT), ₹84+ Cr Seizure Value, Multi-hop flow. |
| **Standard NCRP Case** | `0x71C2e36675B8B1Fc2ffDa6112dE9C1C90D218976` | Ethereum | Full 3-hop benchmark tree, CoinDCX cashout link, Section 94 generation. |
| **Clean / Fresh Wallet** | Any new MetaMask/TrustWallet address | Ethereum | 🟢 Emerald Green Node (`Clean / Inactive`), Risk 15, Clean Peer 100%, Seizure ₹0. |

---

## 💻 Local Developer & Deployment Guide

### Prerequisites
- Python 3.10+
- Node.js 18+ & npm

### 1. Backend Server Setup
```bash
# Clone repository
git clone https://github.com/TANMAY-PRATAP/cryptorecon.git
cd cryptorecon

# Setup Python environment
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run Automated Test Suite (59/59 Tests)
pytest

# Start FastAPI Server (Port 8000)
uvicorn app.main:app --reload --port 8000
```

### 2. Frontend Dashboard Setup
```bash
cd frontend
npm install
npm run dev
```
Open **`http://localhost:3000`** in your browser.

---

## ⚖️ Statutory Legal & Compliance References

1. **Section 94, Bharatiya Nagarik Suraksha Sanhita (BNSS), 2023**: Replaces Section 91 of the erstwhile CrPC. Empowers investigating officers to summon any document or electronic asset required for investigation.
2. **Section 65B, Bharatiya Sakshya Adhiniyam (BSA), 2023**: Replaces Section 65B of the Indian Evidence Act, 1872. Mandates electronic digital certificate verifying system integrity and Merkle proofs.
3. **FIU-IND Anti-Money Laundering Regulations**: Virtual Digital Asset (VDA) service provider registration and suspicious transaction reporting (STR) alignment.
4. **CFCFRMS / Citizen Financial Cyber Fraud Reporting Management System (1930)**: Automated banking lien protocol for emergency debit freeze.

---

**© 2026 CryptoRecon Forensics Team. Built for Law Enforcement, I4C, and National Cybersecurity Resilience.**
