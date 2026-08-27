"""Pre-seeded Entity Database for Inverted Bloom Filter & Direct Attribution.

Contains known VASP hot/cold wallets, FIU-IND registered entities (CoinDCX, WazirX, ZebPay),
privacy mixers (Tornado Cash, Railgun, Wasabi), and sanctioned/exploit addresses.
"""

from typing import List
from app.schemas.entity import EntityTag, EntityType

SEED_ENTITIES: List[EntityTag] = [
    # --- Indian FIU-IND Registered VASPs (Track A Nodal Officers) ---
    EntityTag(
        address="0x40ec5b33f54e0e8a33a975908c5ba1c14e5bbbdf",
        blockchain="ethereum",
        entity_name="CoinDCX Hot Wallet 1",
        entity_type=EntityType.VASP_HOT,
        jurisdiction="IN",
        compliance_email="nodal.officer@coindcx.com",
        fiu_registered=True,
        risk_rating=10,
        metadata={"fiu_registration_no": "FIU-IND-2023-CDX-001"}
    ),
    EntityTag(
        address="0x5a52e96bacdabb82fd05763e25335261b270efcb",
        blockchain="ethereum",
        entity_name="WazirX Sweep Vault",
        entity_type=EntityType.VASP_HOT,
        jurisdiction="IN",
        compliance_email="compliance@wazirx.com",
        fiu_registered=True,
        risk_rating=15,
        metadata={"fiu_registration_no": "FIU-IND-2023-WZX-002"}
    ),
    EntityTag(
        address="0x8b99f3660622e21f2910ecca7fbe51d654a1517d",
        blockchain="ethereum",
        entity_name="ZebPay Liquidity Pool",
        entity_type=EntityType.VASP_HOT,
        jurisdiction="IN",
        compliance_email="legal@zebpay.com",
        fiu_registered=True,
        risk_rating=10,
        metadata={"fiu_registration_no": "FIU-IND-2023-ZBP-003"}
    ),

    # --- Major Global Exchanges (EVM) ---
    EntityTag(
        address="0x28c6c06298d514db089934071355e5743bf21d60",
        blockchain="ethereum",
        entity_name="Binance 14",
        entity_type=EntityType.VASP_HOT,
        jurisdiction="OFFSHORE",
        compliance_email="case-inquiry@binance.com",
        fiu_registered=False,
        risk_rating=15,
        metadata={"exchange": "Binance", "cluster": "HotWallet14"}
    ),
    EntityTag(
        address="0x21a31ee1afc51d94c2efccaa2092ad1028285549",
        blockchain="ethereum",
        entity_name="Binance 15",
        entity_type=EntityType.VASP_HOT,
        jurisdiction="OFFSHORE",
        compliance_email="case-inquiry@binance.com",
        fiu_registered=False,
        risk_rating=15,
        metadata={"exchange": "Binance", "cluster": "HotWallet15"}
    ),
    EntityTag(
        address="0xdfd5293d8e347dfee59e53b243330057712a269e",
        blockchain="ethereum",
        entity_name="Binance 16",
        entity_type=EntityType.VASP_HOT,
        jurisdiction="OFFSHORE",
        compliance_email="case-inquiry@binance.com",
        fiu_registered=False,
        risk_rating=15,
        metadata={"exchange": "Binance", "cluster": "HotWallet16"}
    ),
    EntityTag(
        address="0x503828976d22510aad0201ac7ec88293211d23da",
        blockchain="ethereum",
        entity_name="Coinbase 1",
        entity_type=EntityType.VASP_HOT,
        jurisdiction="US",
        compliance_email="subpoena@coinbase.com",
        fiu_registered=False,
        risk_rating=10,
        metadata={"exchange": "Coinbase"}
    ),
    EntityTag(
        address="0x2faf487a4414fe77e2327f0bf4ae2a264a776ad2",
        blockchain="ethereum",
        entity_name="FTX / Alameda Liquidation",
        entity_type=EntityType.VASP_COLD,
        jurisdiction="US",
        compliance_email="claims@ftx.com",
        fiu_registered=False,
        risk_rating=40,
        metadata={"status": "Defunct"}
    ),
    EntityTag(
        address="0x6cc5f688a315f3dc28a7781717a9a798a59fda7b",
        blockchain="ethereum",
        entity_name="OKX Hot Wallet",
        entity_type=EntityType.VASP_HOT,
        jurisdiction="OFFSHORE",
        compliance_email="enforcement@okx.com",
        fiu_registered=False,
        risk_rating=20,
        metadata={"exchange": "OKX"}
    ),
    EntityTag(
        address="0x0d0707963952f2fba59dd06f2b425ace40b492fe",
        blockchain="ethereum",
        entity_name="Gate.io 1",
        entity_type=EntityType.VASP_HOT,
        jurisdiction="OFFSHORE",
        compliance_email="support@gate.io",
        fiu_registered=False,
        risk_rating=25,
        metadata={"exchange": "Gate.io"}
    ),

    # --- TRON VASPs & Bridges ---
    EntityTag(
        address="TYDzsYUE2UtZZ3z66o7kULg43H4tKq7rK6",
        blockchain="tron",
        entity_name="Binance TRON Hot Wallet",
        entity_type=EntityType.VASP_HOT,
        jurisdiction="OFFSHORE",
        compliance_email="case-inquiry@binance.com",
        fiu_registered=False,
        risk_rating=15,
        metadata={"exchange": "Binance", "network": "TRON"}
    ),
    EntityTag(
        address="TT2T17KZDxDuAPRGQRVH6MmXauP2UytEd8",
        blockchain="tron",
        entity_name="OKX TRON Deposit Sweeper",
        entity_type=EntityType.VASP_DEPOSIT,
        jurisdiction="OFFSHORE",
        compliance_email="enforcement@okx.com",
        fiu_registered=False,
        risk_rating=20,
        metadata={"exchange": "OKX", "network": "TRON"}
    ),
    EntityTag(
        address="TF17BgPaZYbz8oxbjhriP9zpG2qt3EcEhH",
        blockchain="tron",
        entity_name="Huobi / HTX TRON Treasury",
        entity_type=EntityType.VASP_HOT,
        jurisdiction="OFFSHORE",
        compliance_email="compliance@htx.com",
        fiu_registered=False,
        risk_rating=35,
        metadata={"exchange": "HTX", "network": "TRON"}
    ),

    # --- Bitcoin Entities & Labeled Clusters ---
    EntityTag(
        address="1NDyJtNTjmwk5xPNhjgAMu4HDHigtobu1s",
        blockchain="bitcoin",
        entity_name="Binance BTC Cold Storage 1",
        entity_type=EntityType.VASP_COLD,
        jurisdiction="OFFSHORE",
        compliance_email="case-inquiry@binance.com",
        fiu_registered=False,
        risk_rating=10,
        metadata={"cluster_size": 150000}
    ),
    EntityTag(
        address="34xp4vRoCGJym3xR7yCVPFHoCNxv4Twseo",
        blockchain="bitcoin",
        entity_name="Binance BTC Hot Wallet 1",
        entity_type=EntityType.VASP_HOT,
        jurisdiction="OFFSHORE",
        compliance_email="case-inquiry@binance.com",
        fiu_registered=False,
        risk_rating=15,
        metadata={"cluster_size": 248000}
    ),
    EntityTag(
        address="bc1qgdjqv0av3q56jvd82tkdjpy7gdp9ut8tlqmgrpmv24sq90ecnvqqjwvw97",
        blockchain="bitcoin",
        entity_name="Bitfinex BTC Vault",
        entity_type=EntityType.VASP_COLD,
        jurisdiction="OFFSHORE",
        compliance_email="legal@bitfinex.com",
        fiu_registered=False,
        risk_rating=15,
        metadata={"multisig": True}
    ),

    # --- Privacy Mixers & Obfuscation Breakpoints (100% Risk) ---
    EntityTag(
        address="0xd90e2f925da726b50c4ed8d0fb90ad053324f31b",
        blockchain="ethereum",
        entity_name="Tornado Cash Router",
        entity_type=EntityType.MIXER_POOL,
        jurisdiction="GLOBAL_P2P",
        compliance_email=None,
        fiu_registered=False,
        risk_rating=100,
        metadata={"status": "OFAC_SDN_SANCTIONED", "protocol": "TornadoCash"}
    ),
    EntityTag(
        address="0x12d66f87a04a9e220743712ce6d9bb1b5616b8fc",
        blockchain="ethereum",
        entity_name="Tornado Cash 0.1 ETH Pool",
        entity_type=EntityType.MIXER_POOL,
        jurisdiction="GLOBAL_P2P",
        compliance_email=None,
        fiu_registered=False,
        risk_rating=100,
        metadata={"pool_denom": "0.1 ETH", "protocol": "TornadoCash"}
    ),
    EntityTag(
        address="0x47ce0c6ed5b0ce3d3a51fdb1c52dc66a7c3c2936",
        blockchain="ethereum",
        entity_name="Tornado Cash 1 ETH Pool",
        entity_type=EntityType.MIXER_POOL,
        jurisdiction="GLOBAL_P2P",
        compliance_email=None,
        fiu_registered=False,
        risk_rating=100,
        metadata={"pool_denom": "1 ETH", "protocol": "TornadoCash"}
    ),
    EntityTag(
        address="0xfa8449189744799aed7cb7bb47470f4f107d706b",
        blockchain="ethereum",
        entity_name="Railgun Privacy Contract",
        entity_type=EntityType.MIXER_POOL,
        jurisdiction="GLOBAL_P2P",
        compliance_email=None,
        fiu_registered=False,
        risk_rating=95,
        metadata={"protocol": "Railgun zk-SNARKs"}
    ),

    # --- Exploiters, Sanctioned Entities & Ransomware (OFAC SDN) ---
    EntityTag(
        address="0x098b716b8aaf21512996dc57eb0615e2383e2f96",
        blockchain="ethereum",
        entity_name="Ronin Bridge Exploiter (Lazarus)",
        entity_type=EntityType.OFAC_SANCTIONED,
        jurisdiction="KP",
        compliance_email=None,
        fiu_registered=False,
        risk_rating=100,
        metadata={"threat_actor": "Lazarus Group", "ofac_id": "14114"}
    ),
    EntityTag(
        address="0x71C2e36675B8B1Fc2ffDa6112dE9C1C90D218976",
        blockchain="ethereum",
        entity_name="NCRP Test Suspect Mock Entity",
        entity_type=EntityType.MULE_WALLET,
        jurisdiction="IN",
        compliance_email=None,
        fiu_registered=False,
        risk_rating=75,
        metadata={"case_ref": "SIH26183-SEED-01"}
    )
]
