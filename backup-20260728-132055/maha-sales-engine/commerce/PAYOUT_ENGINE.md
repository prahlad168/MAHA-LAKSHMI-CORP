# MAHA SALES ENGINE V1 - Payout Engine Documentation

## Overview

Payout processing and revenue distribution.

## Revenue Allocation

Configurable via YAML:
- CEO Wallet (80%)
- Company Wallet (25%)
- Operations Pool (15%)
- Reserve Pool (10%)
- Charity Pool (5%)
- Per-marketplace overrides
- Per-product overrides

## Usage

```python
from payouts.engine import PayoutEngine
from wallets.engine import WalletEngine

wallet_engine = WalletEngine(db_manager)
payout_engine = PayoutEngine(db_manager, wallet_engine)

# Process payout
payout_id = payout_engine.process_payout(
    recipient_id="wallet-123",
    amount=1000000,
    currency="IDR",
    payout_method="bank_transfer"
)
```

## Features

- Automatic distribution
- Minimum payout thresholds
- Scheduled payouts
- Multi-currency support
- Audit trail
- Notification