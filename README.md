# CryptoRecon (V4.0 Master Architecture)

**Multi-Chain Forensic Reconnaissance, VASP Attribution & Autonomous Asset Recovery Engine**  
*Target Event:* Smart India Hackathon 2026 (Problem Statement: SIH26183)  
*Target Users:* Cyber Crime Cells (1930 / I4C / NCRP), State Police Units, FIU-IND, Judicial Investigators

---

## 1. Project Directory Structure

```text
c:\dataaaaa\project\
├── .env.example                         # Environment configuration template
├── README.md                            # Complete architecture & quick start guide
├── requirements.txt                     # Phase 1 & core forensic Python dependencies
├── PRD.md                               # Master Product Requirements Document
│
├── app/                                 # FastAPI Application Core
│   ├── __init__.py
│   ├── main.py                          # FastAPI Application entrypoint & lifespan
│   ├── config.py                        # Pydantic v2 settings & environment variables
│   │
│   ├── api/                             # API Routers & Endpoints
│   │   ├── __init__.py
│   │   ├── deps.py                      # FastAPI Dependency Injection (Redis, BloomFilter, Services)
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── api_router.py            # Aggregated v1 Router
│   │       └── endpoints/
│   │           ├── __init__.py
│   │           ├── cases.py             # POST /api/v1/cases/ingest, GET /api/v1/cases/{complaint_id}
│   │           ├── entities.py          # GET /api/v1/entities/lookup (Direct Tag Attribution)
│   │           └── health.py            # GET /health, GET /readiness
│   │
│   ├── core/                            # Core Ingestion, Filters & Validators
│   │   ├── __init__.py
│   │   ├── bloom_filter.py              # Inverted In-Memory Bloom Filter for 100k+ Entity Tags (<=1ms)
│   │   ├── validators.py                # EIP-55, Base58Check (TRON/BTC), Timelock rules
│   │   └── seed_entities.py             # Pre-seeded database of known VASPs, Mixers & Exploiters
│   │
│   ├── schemas/                         # Pydantic v2 Input/Output Models
│   │   ├── __init__.py
│   │   ├── case.py                      # CaseIngestRequest, CaseIngestResponse, CaseDetail
│   │   ├── chain.py                     # Blockchain, TokenContract, AddressValidationResult
│   │   └── entity.py                    # EntityTag, EntityType, TagLookupResponse
│   │
│   ├── engine/                          # Multi-Chain Traversal & Micro-Batching
│   │   ├── __init__.py
│   │   ├── evm/
│   │   │   ├── __init__.py
│   │   │   ├── multicall.py             # Multicall3 micro-batching (50 queries/batch)
│   │   │   └── client.py                # Web3 / httpx EVM client & ERC-20 event log decoders
│   │   ├── tron/
│   │   │   ├── __init__.py
│   │   │   └── client.py                # TronGrid / TRC-20 micro-batch client
│   │   └── bitcoin/
│   │       ├── __init__.py
│   │       └── client.py                # Bitcoin UTXO RPC / Blockstream client & CIOH
│   │
│   ├── storage/                         # Caching & State Management
│   │   ├── __init__.py
│   │   ├── redis_client.py              # Async Redis queue & cache with graceful fallback
│   │   └── memory_store.py              # Thread-safe in-memory case repository
│   │
│   ├── traversal/                       # Module 3: CFR Dynamic Pruning & Mule Aggregation
│   │   └── __init__.py
│   ├── attribution/                     # Module 5: Gas-Parent Ancestry & CIOH Heuristics
│   │   └── __init__.py
│   ├── ml/                              # Module 4: Node2Vec & LightGBM Typology Engine
│   │   └── __init__.py
│   └── legal/                           # Module 7: Section 94 BNSS & 65B BSA Dispatch
│       └── __init__.py
│
└── tests/                               # Comprehensive Automated Test Suite
    ├── __init__.py
    ├── conftest.py                      # Pytest fixtures & sample NCRP payloads
    ├── test_ingestion.py                # FastAPI Ingestion pipeline tests
    ├── test_bloom_filter.py             # Sub-millisecond lookup & latency benchmark tests
    ├── test_multicall.py                # Multicall3 batch chunking & ABI encoder tests
    └── test_validators.py               # EIP-55, Base58Check, Bech32 & Timelock tests
```

---

## 2. Ingestion Pipeline (Module 1)

### Input Payload Schema (`POST /api/v1/cases/ingest`)
```json
{
  "complaint_id": "NCRP-2026-98124",
  "suspect_address": "0x71C2e36675B8B1Fc2ffDa6112dE9C1C90D218976",
  "blockchain": "ethereum", 
  "token_contract": "0xdAC17F958D2ee523a2206206994597C13D831ec7",
  "incident_timestamp_utc": "2026-08-27T10:00:00Z",
  "stolen_amount": 5400.0,
  "victim_bank_ref": "AXIS/2026/UPI/88921"
}
```

### Ingestion Lifecycle:
1. **Address Format Verification**:
   - `EVM (Ethereum, Polygon, BSC, Arbitrum, Optimism)`: Validates format & calculates **EIP-55** checksum.
   - `TRON`: Decodes **Base58Check** ensuring `0x41` prefix and 4-byte checksum.
   - `Bitcoin`: Validates **Bech32 (bc1...)**, **P2PKH (1...)**, or **P2SH (3...)**.
2. **Time-Lock Pre-Processor Enforcement**:
   - Enforces $T \ge T_{\text{incident}}$. Any downstream block or transfer prior to the reported incident timestamp is omitted to prevent retroactive noise.
3. **Inverted In-Memory Bloom Filter Lookup**:
   - Executes $O(1)$ membership check in $\le 1$ ms against 100k+ known entity tags.
   - **Direct Tag Match**: Returns immediate VASP attribution (e.g., CoinDCX, Binance, WazirX) or Mixer classification (Tornado Cash, Railgun).
   - **Unknown Entity**: Automatically enqueues case payload to the asynchronous Multi-Chain Micro-Batch RPC engine.

---

## 3. Quick Start & Execution

### 1. Installation
```powershell
# Create virtual environment (Python 3.10+)
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install requirements
pip install -r requirements.txt
```

### 2. Environment Configuration
```powershell
cp .env.example .env
```

### 3. Launch Development Server
```powershell
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
Interactive Swagger API documentation is available at `http://localhost:8000/docs`.

### 4. Run Automated Test Suite
```powershell
pytest tests/ -v
```
