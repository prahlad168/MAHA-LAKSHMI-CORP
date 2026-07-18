#!/usr/bin/env python3
"""
CEO Profit Transfer Updater
Update status transfer setelah Pak Pur transfer ke BCA

Usage:
    python3 update-transfer-status.py --id PENDING-001 --ref BCA123456789 --amount 800000
"""

import json
import sys
import os
from datetime import datetime

TRACKER_FILE = "/workspace/project/MAHA-LAKSHMI-CORP/ceo-revenue-share/VALID-TRANSFER-TRACKER.json"

def load_tracker():
    """Load transfer tracker"""
    with open(TRACKER_FILE, 'r') as f:
        return json.load(f)

def save_tracker(data):
    """Save transfer tracker"""
    with open(TRACKER_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def update_transfer(transfer_id, reference_number, amount, screenshot_path=None):
    """Update transfer status to COMPLETED"""
    data = load_tracker()
    
    # Find pending transfer
    found = False
    for pending in data['pending_transfers']:
        if pending['transfer_id'] == transfer_id:
            found = True
            pending['status'] = 'COMPLETED'
            pending['bank_transfer']['reference_number'] = reference_number
            pending['bank_transfer']['transfer_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            if screenshot_path:
                pending['bank_transfer']['screenshot'] = screenshot_path
            
            # Move to completed
            completed = pending.copy()
            completed['completed_at'] = datetime.now().isoformat()
            data['completed_transfers'].append(completed)
            
            # Remove from pending
            data['pending_transfers'].remove(pending)
            
            # Update totals
            data['total_revenue']['distributed'] += completed['ceo_share']
            data['total_revenue']['pending_distribution'] -= completed['ceo_share']
            
            break
    
    if not found:
        print(f"❌ Transfer ID {transfer_id} tidak ditemukan!")
        return False
    
    # Add audit log
    data['audit_log'].append({
        "timestamp": datetime.now().isoformat(),
        "action": "TRANSFER_COMPLETED",
        "transfer_id": transfer_id,
        "reference_number": reference_number,
        "amount": amount,
        "status": "COMPLETED"
    })
    
    save_tracker(data)
    print(f"✅ Transfer {transfer_id} di-update ke COMPLETED!")
    print(f"   Reference: {reference_number}")
    print(f"   Amount: Rp {amount:,}")
    return True

def show_pending():
    """Show all pending transfers"""
    data = load_tracker()
    
    print("\n📋 PENDING TRANSFERS")
    print("=" * 60)
    print(f"Total Pending: Rp {data['total_revenue']['pending_distribution']:,}")
    print()
    
    for pending in data['pending_transfers']:
        print(f"ID: {pending['transfer_id']}")
        print(f"Source: {pending['source']}")
        print(f"Amount: Rp {pending['ceo_share']:,}")
        print(f"Status: {pending['status']}")
        print("-" * 40)
    
    print()
    print("📋 COMPLETED TRANSFERS")
    print("=" * 60)
    if not data['completed_transfers']:
        print("Belum ada transfer yang completed.")
    else:
        for completed in data['completed_transfers']:
            print(f"ID: {completed['transfer_id']}")
            print(f"Amount: Rp {completed['ceo_share']:,}")
            print(f"Reference: {completed['bank_transfer']['reference_number']}")
            print(f"Date: {completed['bank_transfer']['transfer_date']}")
            print("-" * 40)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='CEO Profit Transfer Updater')
    parser.add_argument('--id', required=True, help='Transfer ID')
    parser.add_argument('--ref', required=True, help='BCA Reference Number')
    parser.add_argument('--amount', type=float, required=True, help='Amount transferred')
    parser.add_argument('--screenshot', help='Screenshot file path')
    parser.add_argument('--show', action='store_true', help='Show pending transfers')
    
    args = parser.parse_args()
    
    if args.show:
        show_pending()
    else:
        update_transfer(args.id, args.ref, args.amount, args.screenshot)
