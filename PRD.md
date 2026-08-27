# Product Requirement Document (PRD)

**Project Name:** CryptoRecon (V4.0 Master Architecture)
**Tagline:** Multi-Chain Forensic Reconnaissance, VASP Attribution & Autonomous Asset Recovery Engine
**Target Event:** Smart India Hackathon 2026 (Problem Statement: SIH26183)
**Target Users:** Cyber Crime Cells (1930 / I4C / NCRP), State Police Units, FIU-IND, Judicial Investigators

---

## 1. Executive Summary & Problem Scope

CryptoRecon addresses the latency, dilution, cross-chain, and fiat-offramp tracking challenges in cryptocurrency financial fraud investigations. Traditional manual tracing approaches fail due to delayed exchange sweeping (up to 24-48 hours), smurfing across dozens of mule wallets, privacy mixing protocols, and the decoupling between blockchain ledgers and domestic fiat banking systems.

CryptoRecon establishes an automated multi-chain forensic pipeline:
* Ingests suspect wallets directly via NCRP/1930 schemas.
* Performs near-real-time multi-chain traversal across EVM, TRON, and Bitcoin networks.
* Employs Graph AI/ML (Node2Vec + LightGBM) for 0–100 risk scoring and fraud typology classification.
* Executes dedicated Dual-Stack VASP Attribution (Gas-Parent Ancestry for EVM/TRON and CIOH/HD-Derivation for Bitcoin).
* Prevents graph explosion through dynamic Cumulative Flow Ratio (CFR) pruning and Mule-Cluster aggregation.
* Closes the recovery loop by re-stitching P2P exchange cashout UIDs back to domestic Indian banking rails (1930 CFCFRMS portal) and auto-generating Section 94 BNSS Legal Notices and Section 65B BSA Evidence Certificates.

---

## 2. System Architecture & Component Design

```text
[1930 / NCRP / SAHYOG Gateway] 
           │ (REST Webhook: Suspect Address + Token + Incident Timestamp T_0)
           ▼
[FastAPI Ingestion & Validation Gateway]
           │
           ▼
[In-Memory Inverted Bloom Filter (100k+ Known VASP/Entity Tags)]
     ├── Match Found (<=1ms) ──► Direct Tag Attribution
     └── Unknown Entity ───────► Multi-Chain Micro-Batch RPC Engine
                                       │
           ┌───────────────────────────┴───────────────────────────┐
           ▼                                                       ▼
[EVM / TRON Execution Stack]                              [Bitcoin / UTXO Stack]
  - Multicall3 micro-batching (50 queries/call)             - Common-Input-Ownership Heuristic (CIOH)
  - ERC-20 / TRC-20 Event Log Decoders                      - Peel-Chain & Change-Address Heuristics
  - Native Gas Inflow Inspector                             - Blockstream / Native RPC Client
           │                                                       │
           └───────────────────────────┬───────────────────────────┘
                                       ▼
                 [Adaptive Flow Traversal & Clustering Engine]
                   - Cumulative Flow Ratio (CFR) Dynamic Pruning
                   - Mule-Cluster Compound Node Collapse (>=5 splits)
                                       │
     ┌─────────────────────────────────┼─────────────────────────────────┐
     ▼                                 ▼                                 ▼
[Dual-Stack VASP Attribution]    [Graph AI/ML Risk Engine]       [Mixer & Swapper Resolver]
 - EVM/TRON: Gas Ancestry ->      - Node2Vec Graph Embeddings     - EVM (Tornado, Railgun) &
   Bytecode -> Sweep Heuristic    - LightGBM Typology Classifier    BTC CoinJoin (Wasabi, Whirlpool)
 - BTC: CIOH Seed Clusters ->     - Features: Entropy, Velocity   - Status: CRYPTOGRAPHIC_BREAKPOINT
   HD-Derivation -> Subpoena      - Open Bootstrap Training Sets  - Relayer & Output Watchdogs
     │                                 │                                 │
     └─────────────────────────────────┼─────────────────────────────────┘
                                       ▼
                       [Neo4j Graph Database & Cache]
                                       │
     ┌─────────────────────────────────┼─────────────────────────────────┐
     ▼                                 ▼                                 ▼
[Active Mempool Watchdog]       [Dual-Track Legal Dispatch]     [P2P INR Re-Stitching Engine]
 - 30-Day Async WebSocket        - Track A: Sec 94 BNSS Notice   - Correlates VASP UID to P2P
   Listeners on Dormant Wallets  - Track B: Offshore MLAT Draft    Bank A/C, IFSC & UPI VPA
 - Push Webhook Notifications    - Sec 65B BSA Certificate       - Injects into 1930 CFCFRMS
                                       │
                                       ▼
                       [Cytoscape.js Frontend Visualizer]
```

---

## 3. Detailed Functional Modules & Technical Logic

### Module 1: Ingestion & Time-Lock Pre-Processor
* **Stack:** `FastAPI`, `Pydantic v2`, `Redis`
* **Endpoint:** `POST /api/v1/cases/ingest`
* **Input Schema:**
  ```json
  {
    "complaint_id": "NCRP-2026-98124",
    "suspect_address": "0x71C...8976",
    "blockchain": "ethereum", 
    "token_contract": "0xdAC17F958D2ee523a2206206994597C13D831ec7",
    "incident_timestamp_utc": "2026-08-27T10:00:00Z"
  }
  ```
* **Processing Rules:**
  1. Address format verification (`EIP-55` regex for EVM, `Base58Check` for TRON/BTC).
  2. Enforce Time-Lock: Traversal ignores any transaction where block_timestamp < T_incident.
  3. Query in-memory Inverted Bloom Filter for O(1) known entity tags (<= 1 ms).

### Module 2: Multi-Chain Traversal & Batch RPC Engine
* **Stack:** `Web3.py`, `TronPy`, `Multicall3`, `httpx`
* **EVM & TRON Processing:**
  * Uses `Multicall3` smart contract calls bundling up to 50 balance and event checks per single HTTP request to prevent public RPC rate-limiting.
  * Parses standard `Transfer(address from, address to, uint256 value)` events across ERC-20 / TRC-20 contracts.
* **Bitcoin (UTXO) Processing:**
  * Implements **Common-Input-Ownership Heuristic (CIOH)**: Groups multiple inputs in a single transaction under a single entity cluster.
  * Implements **Change-Address Detection**: Identifies peel-chain patterns by evaluating script types, round-number payment amounts, and non-reused return addresses.

### Module 3: Anti-Smurfing & Graph Optimization Engine
* **Stack:** `NetworkX`, `Neo4j Community Edition`
* **Dynamic CFR Pruning Formula:**
  $$\text{Traverse Branch If: } \text{Branch Flow} \ge \min\left(50\text{ USDT},\ \frac{\text{Total Stolen Amount}}{N_{\text{branches}} \times 1.5}\right)$$
  * Ensures fractional splits (2%–4%) are tracked while dropping sub-dust noise.
* **Mule-Cluster Aggregation:**
  * When a single wallet splits funds into >= 5 intermediate recipient addresses, the visualizer collapses them into a single composite `(:MuleCluster)` node.
  * Clicking the node expands an internal tabular breakdown containing wallet addresses, split amounts, and live on-chain balances.

### Module 4: Graph-AI/ML Risk & Typology Engine
* **Stack:** `node2vec`, `LightGBM`, `scikit-learn`
* **Training Data Provenance (Bootstrap Sources):**
  * Elliptic Dataset (200k+ labeled Bitcoin graph entities).
  * Ransomwhere Open Tracker (verified ransomware deposit clusters).
  * FIU-IND domestic watchlists and supplementary OFAC SDN address hashes.
* **Feature Engineering (14 Structural Dimensions):**
  * Fan-in / fan-out degree entropy, transaction burst velocity, median holding duration, native gas dispenser diversity, historical address reuse count.
* **Outputs:**
  * **Composite Risk Score (0–100)**.
  * **Typology Classification:** `Mule Ring`, `Ransomware`, `Darknet Market`, `Terror Financing`, or `Unflagged`.
  * **Human-in-the-Loop Feedback Loop:** System logs closed 1930 investigation outcomes to continuously retrain model weights.

### Module 5: Dedicated Dual-Stack VASP Attribution Engine
* **Account-Based Attribution (EVM & TRON):**
  1. *Tier 1 (Gas-Parent Ancestry - Primary):* Traces transaction index 0 of the destination address to locate the native gas dispenser (ETH/TRX) transfer from exchange hot wallets. Yields sub-3-second pre-sweep attribution.
  2. *Tier 2 (Contract Factory Bytecode - Fallback 1):* Matches forwarder contract bytecode against registered exchange proxy factories.
  3. *Tier 3 (Omnibus Sweep - Fallback 2):* Asynchronously monitors destination EOAs for balance sweeps into known exchange consolidation wallets.
* **UTXO-Based Attribution (Bitcoin):**
  1. *Tier 1 (CIOH & Labeled Cluster Match - Primary):* Matches transaction input clusters against labeled exchange hot-wallet seed databases.
  2. *Tier 2 (HD-Derivation Heuristic - Fallback 1):* Identifies predictable sequential batch-deposit signatures used by major VASPs.
  3. *Tier 3 (Subpoena Escalation - Fallback 2):* Flags unassigned UTXO candidate clusters for targeted legal KYC requests.

### Module 6: Mixer Breakpoint & Synthetic Linkage
* **Supported Protocols:** Tornado Cash, Railgun, Wasabi CoinJoin, Samourai Whirlpool, FixedFloat, ChangeNOW.
* **Handling Protocol:**
  * Assigns a `100% Risk Score: Cryptographic Obfuscation Detected`.
  * Marks the graph node with `[:CRYPTOGRAPHIC_BREAKPOINT]` to avoid false-positive forward links.
  * Spawns an asyncio WebSocket listener on known mixer relayers and withdrawal contracts to trigger alerts upon exit.

### Module 7: Closed-Loop Asset Recovery & Statutory Legal Dispatch
* **P2P Crypto-to-INR Re-Stitching:**
  * Extracts counterparty Bank Account Number, IFSC, UPI VPA, and KYC details linked to the VASP deposit UID.
  * Emits structured JSON payloads formatted for direct ingestion into the **1930 / I4C CFCFRMS Banking Freeze Portal**.
* **Dual-Track Notice Dispatch:**
  * **Track A (Onshore FIU-IND Registered VASPs):** Generates an automated **Section 94 BNSS Notice PDF** addressed to the registered Nodal Officer (CoinDCX, WazirX, ZebPay).
  * **Track B (Offshore Non-Compliant VASPs):** Compiles an **MLAT / Interpol Purple Notice Dossier Draft** and notifies the FIU-IND FINnet gateway.
* **Evidentiary Standard (Section 65B BSA):**
  * Auto-generates a court-admissible **Section 65B Bharatiya Sakshya Adhiniyam Certificate** containing SHA-256 RPC response digests, Merkle inclusion proofs, and UTC-stamped system logs.

---

## 4. Database & Storage Schemas

### Neo4j Graph Model
```cypher
// Node Labels
(:Wallet {address: String, chain: String, risk_score: Integer, typology: String, is_mule: Boolean})
(:VASP {name: String, entity_type: String, jurisdiction: String, compliance_email: String})
(:MuleCluster {cluster_id: String, total_wallets: Integer, total_volume: Float})
(:MixerPool {protocol: String, contract_address: String, breakpoint: Boolean})

// Relationship Types
(:Wallet)-[:TRANSFERRED {tx_hash: String, token: String, amount: Float, timestamp: Integer}]->(:Wallet)
(:Wallet)-[:DISPENSED_GAS_TO {tx_hash: String, native_amount: Float}]->(:Wallet)
(:Wallet)-[:DEPOSITED_TO {uid_tag: String, sweep_status: String}]->(:VASP)
(:Wallet)-[:ENTERED_OBFUSCATION {pool_type: String}]->(:MixerPool)
```

### PostgreSQL / Relational State Schema
```sql
CREATE TABLE complaints (
    complaint_id VARCHAR(64) PRIMARY KEY,
    suspect_address VARCHAR(128) NOT NULL,
    chain VARCHAR(32) NOT NULL,
    token_symbol VARCHAR(16) NOT NULL,
    incident_timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    current_status VARCHAR(32) DEFAULT 'PROCESSING',
    risk_score INT DEFAULT 0,
    attributed_vasp VARCHAR(64),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE p2p_recovery_links (
    id SERIAL PRIMARY KEY,
    complaint_id VARCHAR(64) REFERENCES complaints(complaint_id),
    vasp_name VARCHAR(64),
    exchange_uid VARCHAR(64),
    bank_account_number VARCHAR(64),
    bank_ifsc VARCHAR(32),
    upi_vpa VARCHAR(128),
    cfcfrms_freeze_status VARCHAR(32) DEFAULT 'PENDING'
);
```

---

## 5. UI/UX Interface Requirements

* **Framework:** `Next.js 14` (App Router), `Tailwind CSS`, `Cytoscape.js`, `Lucide React`
* **Core Views:**
  1. **Dashboard / Ingestion Bar:** Input field for Complaint ID, Suspect Address, Token, and Date/Time picker.
  2. **Interactive Forensic Canvas:**
     * Dark-themed visual canvas rendering nodes (Wallets, VASPs, Mule Clusters, Mixers).
     * Color Coding: Green (<= 30), Yellow (31–70), Red (>= 71), Purple (`CRYPTOGRAPHIC_BREAKPOINT`).
     * Click-to-expand drawer for Mule Clusters and VASP attribution evidence.
  3. **Intelligence & Action Panel:**
     * Displays LightGBM risk metrics and typology breakdown.
     * P2P Counterparty Details Card (Bank Account, UPI VPA).
     * Action Buttons: `Export Section 94 BNSS Notice (PDF)`, `Generate Section 65B BSA Certificate (PDF)`, `Trigger 1930 CFCFRMS Freeze`.

---

## 6. Target Engineering Benchmarks (Projected Single-Node Setup)

| Parameter | Target Architecture Design Estimate | Engineering Method |
| :--- | :--- | :--- |
| **Ingestion Throughput** | 120+ complaints / minute | Async FastAPI + Redis/Celery queue |
| **Tag Lookup Latency** | <= 1 ms latency (O(1)) | In-memory Inverted Bloom Filter (100k+ tags) |
| **Multi-Hop Traversal Speed** | 1.8 to 2.8 seconds (4–6 hops) | Multicall3 micro-batching + TronGrid REST pipelining |
| **AI/ML Inference Time** | <= 45 ms per sub-graph | Pre-computed embeddings + quantized LightGBM |
| **Mempool Watchdog Capacity** | Up to 5,000 concurrent addresses | Asyncio WebSocket block listeners |
| **Legal Notice PDF Render** | ~450 ms | Headless WeasyPrint template compilation |

---

## 7. Execution Phasing (Hackathon Sprint Plan)

* **Phase 1 (Backend Core & Ingestion):**
  * Setup FastAPI project structure, Pydantic schemas, and Redis connection.
  * Implement Multicall3 micro-batching and TronGrid parser.
* **Phase 2 (Tracing Algorithms & Attribution):**
  * Code CFR pruning formula and Mule-Cluster aggregation.
  * Implement Gas-Parent Ancestry (EVM/TRON) and CIOH Heuristics (Bitcoin).
* **Phase 3 (AI/ML & Obfuscation):**
  * Train baseline LightGBM model on Elliptic dataset features.
  * Add Mixer Breakpoint tagging and WebSocket mempool watchdog.
* **Phase 4 (Legal Dispatch & UI Integration):**
  * Configure Jinja2 templates and WeasyPrint for Section 94 BNSS / Section 65B BSA PDF generation.
  * Connect Next.js + Cytoscape.js frontend to FastAPI backend for real-time visualization.
