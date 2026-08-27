"""Async Mempool & Relayer Watchdog for Dormant Wallets and Mixer Exits."""

import asyncio
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional
from app.schemas.ml import (
    WatchdogSubscriptionRequest,
    WatchdogSubscriptionResponse,
    WatchdogAlert,
)


class MempoolMixerWatchdog:
    """Asyncio mempool and relayer watchdog for dormant wallets and mixer exits."""

    def __init__(self):
        self._subscriptions: Dict[str, Dict[str, Any]] = {}
        self._alerts: List[WatchdogAlert] = []
        self._lock = asyncio.Lock()

    async def subscribe(self, request: WatchdogSubscriptionRequest) -> WatchdogSubscriptionResponse:
        """Register a suspect wallet or mixer relayer for active mempool listening."""
        clean_addr = request.target_address.lower()
        sub_id = f"SUB_{request.blockchain.upper()}_{clean_addr[:8]}_{len(self._subscriptions) + 1}"
        expires_at = datetime.now(timezone.utc) + timedelta(days=request.monitoring_duration_days)

        sub_record = {
            "subscription_id": sub_id,
            "target_address": request.target_address,
            "blockchain": request.blockchain,
            "complaint_id": request.complaint_id,
            "webhook_url": request.webhook_url,
            "active": True,
            "created_at_utc": datetime.now(timezone.utc),
            "expires_at_utc": expires_at
        }

        async with self._lock:
            self._subscriptions[sub_id] = sub_record

        return WatchdogSubscriptionResponse(
            subscription_id=sub_id,
            target_address=request.target_address,
            blockchain=request.blockchain,
            active=True,
            expires_at_utc=expires_at,
            message=f"Wallet {request.target_address[:8]}... subscribed for 30-day active mempool & relayer watchdog."
        )

    async def emit_alert(
        self,
        subscription_id: str,
        event_type: str,
        detected_tx_hash: str,
        amount: float,
        token: str,
        counterparty: str
    ) -> WatchdogAlert:
        """Emit real-time alert for mempool movement or mixer exit."""
        sub = self._subscriptions.get(subscription_id, {})
        target = sub.get("target_address", "0xUnknown")
        chain = sub.get("blockchain", "ethereum")

        alert = WatchdogAlert(
            alert_id=f"ALERT_{len(self._alerts) + 1}",
            subscription_id=subscription_id,
            target_address=target,
            blockchain=chain,
            event_type=event_type,
            detected_tx_hash=detected_tx_hash,
            amount=amount,
            token=token,
            counterparty=counterparty,
            timestamp_utc=datetime.now(timezone.utc)
        )

        async with self._lock:
            self._alerts.append(alert)

        return alert

    async def list_alerts(self, limit: int = 50) -> List[WatchdogAlert]:
        """List recent watchdog alerts."""
        async with self._lock:
            return self._alerts[-limit:]

    @property
    def active_subscriptions_count(self) -> int:
        return len(self._subscriptions)


_watchdog_instance: Optional[MempoolMixerWatchdog] = None


def get_watchdog() -> MempoolMixerWatchdog:
    global _watchdog_instance
    if _watchdog_instance is None:
        _watchdog_instance = MempoolMixerWatchdog()
    return _watchdog_instance
