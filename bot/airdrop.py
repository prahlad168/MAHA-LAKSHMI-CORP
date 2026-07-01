"""
Airdrop Configuration & Management for Molty Royale AI Agent.

Handles airdrop claim tracking, whitelist management, and auto-claim logic.
"""
import os
import asyncio
import json
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional
from enum import Enum

from bot.utils.logger import get_logger

log = get_logger(__name__)


class AirdropStatus(Enum):
    PENDING = "pending"
    AVAILABLE = "available"
    CLAIMING = "claiming"
    CLAIMED = "claimed"
    FAILED = "failed"
    EXPIRED = "expired"


@dataclass
class AirdropConfig:
    """Airdrop configuration loaded from environment variables."""
    enabled: bool = True
    whitelist_only: bool = False
    min_balance: int = 0
    gas_priority_fee: Optional[float] = None
    max_gas_price: float = 100.0
    claim_batch_size: int = 10
    retry_attempts: int = 3
    retry_delay: int = 60
    notify_webhook: Optional[str] = None
    auto_claim: bool = True
    claim_deadline: Optional[datetime] = None
    
    @classmethod
    def from_env(cls) -> "AirdropConfig":
        """Load configuration from environment variables."""
        deadline_str = os.getenv("AIRDROP_CLAIM_DEADLINE", "")
        claim_deadline = None
        if deadline_str:
            try:
                claim_deadline = datetime.fromisoformat(deadline_str)
            except ValueError:
                log.warning(f"Invalid AIRDROP_CLAIM_DEADLINE format: {deadline_str}")
        
        priority_fee_str = os.getenv("AIRDROP_GAS_PRIORITY_FEE", "")
        priority_fee = None
        if priority_fee_str:
            try:
                priority_fee = float(priority_fee_str)
            except ValueError:
                log.warning(f"Invalid AIRDROP_GAS_PRIORITY_FEE: {priority_fee_str}")
        
        return cls(
            enabled=os.getenv("ENABLE_AIRDROP", "true").lower() == "true",
            whitelist_only=os.getenv("AIRDROP_WHITELIST_ONLY", "false").lower() == "true",
            min_balance=int(os.getenv("AIRDROP_MIN_BALANCE", "0")),
            gas_priority_fee=priority_fee,
            max_gas_price=float(os.getenv("AIRDROP_MAX_GAS_PRICE", "100")),
            claim_batch_size=int(os.getenv("AIRDROP_CLAIM_BATCH_SIZE", "10")),
            retry_attempts=int(os.getenv("AIRDROP_RETRY_ATTEMPTS", "3")),
            retry_delay=int(os.getenv("AIRDROP_RETRY_DELAY", "60")),
            notify_webhook=os.getenv("AIRDROP_NOTIFY_WEBHOOK") or None,
            auto_claim=os.getenv("AIRDROP_AUTO_CLAIM", "true").lower() == "true",
            claim_deadline=claim_deadline,
        )


@dataclass
class AirdropClaim:
    """Represents a single airdrop claim record."""
    claim_id: str
    recipient_address: str
    amount: int
    status: AirdropStatus = AirdropStatus.PENDING
    tx_hash: Optional[str] = None
    claimed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    retry_count: int = 0


@dataclass
class AirdropRecord:
    """Represents an airdrop event."""
    airdrop_id: str
    name: str
    token_address: str
    total_amount: int
    start_time: datetime
    end_time: Optional[datetime] = None
    is_active: bool = True
    claims: list = field(default_factory=list)
    
    @property
    def remaining_amount(self) -> int:
        """Calculate remaining unclaimed amount."""
        claimed = sum(c.amount for c in self.claims if c.status == AirdropStatus.CLAIMED)
        return self.total_amount - claimed


class AirdropManager:
    """
    Manages airdrop configuration, tracking, and claiming.
    
    Usage:
        config = AirdropConfig.from_env()
        manager = AirdropManager(config)
        
        # Check available airdrops
        airdrops = await manager.get_available_airdrops()
        
        # Claim airdrop
        result = await manager.claim_airdrop(airdrop_id, recipient_address)
    """
    
    def __init__(self, config: AirdropConfig):
        self.config = config
        self._airdrops: dict[str, AirdropRecord] = {}
        self._load_state()
    
    def _get_state_file(self) -> Path:
        """Get path to airdrop state file."""
        state_dir = Path.home() / ".molty-royale"
        state_dir.mkdir(parents=True, exist_ok=True)
        return state_dir / "airdrop-state.json"
    
    def _load_state(self):
        """Load airdrop state from disk."""
        state_file = self._get_state_file()
        if state_file.exists():
            try:
                data = json.loads(state_file.read_text())
                for airdrop_data in data.get("airdrops", []):
                    claims = []
                    for claim_data in airdrop_data.pop("claims", []):
                        claim_data["status"] = AirdropStatus(claim_data["status"])
                        claims.append(AirdropClaim(**claim_data))
                    airdrop_data["start_time"] = datetime.fromisoformat(airdrop_data["start_time"])
                    if airdrop_data.get("end_time"):
                        airdrop_data["end_time"] = datetime.fromisoformat(airdrop_data["end_time"])
                    self._airdrops[airdrop_data["airdrop_id"]] = AirdropRecord(
                        claims=claims, **airdrop_data
                    )
                log.info(f"Loaded {len(self._airdrops)} airdrop records from state")
            except Exception as e:
                log.error(f"Failed to load airdrop state: {e}")
    
    def _save_state(self):
        """Save airdrop state to disk."""
        state_file = self._get_state_file()
        data = {
            "airdrops": [
                {
                    "airdrop_id": a.airdrop_id,
                    "name": a.name,
                    "token_address": a.token_address,
                    "total_amount": a.total_amount,
                    "start_time": a.start_time.isoformat(),
                    "end_time": a.end_time.isoformat() if a.end_time else None,
                    "is_active": a.is_active,
                    "claims": [
                        {
                            "claim_id": c.claim_id,
                            "recipient_address": c.recipient_address,
                            "amount": c.amount,
                            "status": c.status.value,
                            "tx_hash": c.tx_hash,
                            "claimed_at": c.claimed_at.isoformat() if c.claimed_at else None,
                            "error_message": c.error_message,
                            "retry_count": c.retry_count,
                        }
                        for c in a.claims
                    ],
                }
                for a in self._airdrops.values()
            ],
            "last_updated": datetime.now().isoformat(),
        }
        try:
            state_file.write_text(json.dumps(data, indent=2))
        except Exception as e:
            log.error(f"Failed to save airdrop state: {e}")
    
    def register_airdrop(
        self,
        airdrop_id: str,
        name: str,
        token_address: str,
        total_amount: int,
        start_time: datetime,
        end_time: Optional[datetime] = None,
    ) -> AirdropRecord:
        """Register a new airdrop event."""
        record = AirdropRecord(
            airdrop_id=airdrop_id,
            name=name,
            token_address=token_address,
            total_amount=total_amount,
            start_time=start_time,
            end_time=end_time,
        )
        self._airdrops[airdrop_id] = record
        self._save_state()
        log.info(f"Registered airdrop: {name} ({airdrop_id})")
        return record
    
    def get_available_airdrops(self) -> list[AirdropRecord]:
        """Get list of currently available airdrops."""
        now = datetime.now()
        available = []
        
        for airdrop in self._airdrops.values():
            if not airdrop.is_active:
                continue
            if airdrop.start_time > now:
                continue
            if airdrop.end_time and airdrop.end_time < now:
                continue
            if self.config.claim_deadline and self.config.claim_deadline < now:
                continue
            available.append(airdrop)
        
        return available
    
    def add_claim(self, airdrop_id: str, recipient: str, amount: int) -> Optional[AirdropClaim]:
        """Add a claim to an airdrop."""
        if airdrop_id not in self._airdrops:
            log.warning(f"Airdrop not found: {airdrop_id}")
            return None
        
        claim = AirdropClaim(
            claim_id=f"{airdrop_id}_{recipient}_{datetime.now().timestamp()}",
            recipient_address=recipient,
            amount=amount,
            status=AirdropStatus.AVAILABLE if self.config.auto_claim else AirdropStatus.PENDING,
        )
        self._airdrops[airdrop_id].claims.append(claim)
        self._save_state()
        return claim
    
    def update_claim_status(
        self,
        airdrop_id: str,
        claim_id: str,
        status: AirdropStatus,
        tx_hash: Optional[str] = None,
        error_message: Optional[str] = None,
    ):
        """Update the status of a claim."""
        if airdrop_id not in self._airdrops:
            return
        
        for claim in self._airdrops[airdrop_id].claims:
            if claim.claim_id == claim_id:
                claim.status = status
                if tx_hash:
                    claim.tx_hash = tx_hash
                if error_message:
                    claim.error_message = error_message
                if status == AirdropStatus.CLAIMED:
                    claim.claimed_at = datetime.now()
                self._save_state()
                return
    
    def get_pending_claims(self) -> list[tuple[AirdropRecord, AirdropClaim]]:
        """Get all pending claims that need to be processed."""
        pending = []
        for airdrop in self._airdrops.values():
            for claim in airdrop.claims:
                if claim.status in (AirdropStatus.PENDING, AirdropStatus.AVAILABLE, AirdropStatus.FAILED):
                    if claim.retry_count < self.config.retry_attempts:
                        pending.append((airdrop, claim))
        return pending
    
    async def claim_airdrop(self, airdrop_id: str, recipient_address: str) -> dict:
        """
        Claim airdrop for a recipient.
        
        Returns dict with status and details.
        """
        if not self.config.enabled:
            return {"success": False, "message": "Airdrop feature is disabled"}
        
        if airdrop_id not in self._airdrops:
            return {"success": False, "message": f"Airdrop not found: {airdrop_id}"}
        
        airdrop = self._airdrops[airdrop_id]
        
        # Find the claim
        claim = None
        for c in airdrop.claims:
            if c.recipient_address.lower() == recipient_address.lower():
                claim = c
                break
        
        if not claim:
            return {"success": False, "message": f"No claim found for {recipient_address}"}
        
        if claim.status == AirdropStatus.CLAIMED:
            return {"success": True, "message": "Already claimed", "tx_hash": claim.tx_hash}
        
        # Update status to claiming
        self.update_claim_status(airdrop_id, claim.claim_id, AirdropStatus.CLAIMING)
        
        # Simulate claim transaction
        # In real implementation, this would call the blockchain
        try:
            # TODO: Implement actual claim transaction
            await asyncio.sleep(0.1)  # Simulate tx delay
            
            tx_hash = f"0x{'a' * 64}"  # Placeholder
            
            self.update_claim_status(
                airdrop_id, 
                claim.claim_id, 
                AirdropStatus.CLAIMED,
                tx_hash=tx_hash
            )
            
            log.info(f"Airdrop claimed: {airdrop.name} -> {recipient_address} (tx: {tx_hash})")
            
            # Send webhook notification if configured
            if self.config.notify_webhook:
                await self._send_webhook_notification(airdrop, claim)
            
            return {
                "success": True,
                "message": "Claim successful",
                "tx_hash": tx_hash,
                "amount": claim.amount,
            }
            
        except Exception as e:
            log.error(f"Failed to claim airdrop: {e}")
            claim.retry_count += 1
            self.update_claim_status(
                airdrop_id,
                claim.claim_id,
                AirdropStatus.FAILED,
                error_message=str(e)
            )
            return {"success": False, "message": f"Claim failed: {str(e)}"}
    
    async def _send_webhook_notification(self, airdrop: AirdropRecord, claim: AirdropClaim):
        """Send webhook notification for successful claim."""
        if not self.config.notify_webhook:
            return
        
        try:
            import httpx
            payload = {
                "event": "airdrop_claimed",
                "airdrop_id": airdrop.airdrop_id,
                "airdrop_name": airdrop.name,
                "recipient": claim.recipient_address,
                "amount": claim.amount,
                "tx_hash": claim.tx_hash,
                "timestamp": datetime.now().isoformat(),
            }
            async with httpx.AsyncClient() as client:
                await client.post(self.config.notify_webhook, json=payload, timeout=10)
            log.info(f"Webhook notification sent for claim {claim.claim_id}")
        except Exception as e:
            log.warning(f"Failed to send webhook notification: {e}")
    
    def get_summary(self) -> dict:
        """Get airdrop summary statistics."""
        total_claims = sum(len(a.claims) for a in self._airdrops.values())
        claimed = sum(
            sum(1 for c in a.claims if c.status == AirdropStatus.CLAIMED)
            for a in self._airdrops.values()
        )
        pending = sum(
            sum(1 for c in a.claims if c.status in (AirdropStatus.PENDING, AirdropStatus.AVAILABLE))
            for a in self._airdrops.values()
        )
        failed = sum(
            sum(1 for c in a.claims if c.status == AirdropStatus.FAILED)
            for a in self._airdrops.values()
        )
        
        return {
            "enabled": self.config.enabled,
            "total_airdrops": len(self._airdrops),
            "total_claims": total_claims,
            "claimed": claimed,
            "pending": pending,
            "failed": failed,
            "success_rate": (claimed / total_claims * 100) if total_claims > 0 else 0,
        }


# Global instance
_config: Optional[AirdropConfig] = None
_manager: Optional[AirdropManager] = None


def get_airdrop_config() -> AirdropConfig:
    """Get or create airdrop configuration."""
    global _config
    if _config is None:
        _config = AirdropConfig.from_env()
    return _config


def get_airdrop_manager() -> AirdropManager:
    """Get or create airdrop manager."""
    global _manager
    if _manager is None:
        _manager = AirdropManager(get_airdrop_config())
    return _manager