#!/usr/bin/env python3
"""
MAHA SALES ENGINE V1 - Backup & Disaster Recovery
Automated backup procedures and disaster recovery scripts.
"""

import os
import sys
import json
import time
import shutil
import tarfile
import logging
import hashlib
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

logger = logging.getLogger("maha-sales-engine.backup")


class BackupStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class BackupMetadata:
    backup_id: str
    created_at: str
    status: str
    size_bytes: int
    checksum: str
    backup_type: str
    source_paths: List[str]
    destination_path: str
    retention_days: int
    error_message: Optional[str] = None


class BackupManager:
    """Manage database and file backups"""
    
    def __init__(self, backup_dir: str = "backups", retention_days: int = 30):
        self.backup_dir = Path(backup_dir)
        self.retention_days = retention_days
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self._backups: Dict[str, BackupMetadata] = {}
    
    def create_backup(
        self,
        backup_type: str,
        source_paths: List[str],
        destination_path: Optional[str] = None,
        compress: bool = True
    ) -> Optional[BackupMetadata]:
        """Create backup of files or database"""
        try:
            backup_id = f"backup-{int(time.time())}-{backup_type}"
            
            if not destination_path:
                timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
                extension = "tar.gz" if compress else "tar"
                destination_path = str(self.backup_dir / f"{backup_type}-{timestamp}.{extension}")
            
            logger.info(f"Starting backup: {backup_id}")
            
            # Create archive
            if compress:
                self._create_compressed_backup(source_paths, destination_path)
            else:
                self._create_uncompressed_backup(source_paths, destination_path)
            
            # Calculate checksum
            checksum = self._calculate_checksum(destination_path)
            size = Path(destination_path).stat().st_size
            
            metadata = BackupMetadata(
                backup_id=backup_id,
                created_at=datetime.now().isoformat(),
                status=BackupStatus.COMPLETED.value,
                size_bytes=size,
                checksum=checksum,
                backup_type=backup_type,
                source_paths=source_paths,
                destination_path=destination_path,
                retention_days=self.retention_days
            )
            
            self._backups[backup_id] = metadata
            self._save_metadata(metadata)
            
            logger.info(f"Backup completed: {backup_id} ({size} bytes)")
            return metadata
            
        except Exception as e:
            logger.error(f"Backup failed: {e}")
            return None
    
    def _create_compressed_backup(self, source_paths: List[str], destination: str):
        """Create compressed tar.gz backup"""
        with tarfile.open(destination, "w:gz") as tar:
            for path in source_paths:
                path_obj = Path(path)
                if path_obj.exists():
                    if path_obj.is_dir():
                        tar.add(path_obj, arcname=path_obj.name, recursive=True)
                    else:
                        tar.add(path_obj, arcname=path_obj.name)
    
    def _create_uncompressed_backup(self, source_paths: List[str], destination: str):
        """Create uncompressed tar backup"""
        with tarfile.open(destination, "w") as tar:
            for path in source_paths:
                path_obj = Path(path)
                if path_obj.exists():
                    tar.add(path_obj, arcname=path_obj.name)
    
    def _calculate_checksum(self, file_path: str) -> str:
        """Calculate SHA256 checksum"""
        sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256.update(chunk)
        return sha256.hexdigest()
    
    def _save_metadata(self, metadata: BackupMetadata):
        """Save backup metadata"""
        metadata_file = self.backup_dir / "backup-manifest.json"
        manifest = self._load_manifest()
        manifest[metadata.backup_id] = asdict(metadata)
        
        with open(metadata_file, "w") as f:
            json.dump(manifest, f, indent=2)
    
    def _load_manifest(self) -> Dict[str, Any]:
        """Load backup manifest"""
        metadata_file = self.backup_dir / "backup-manifest.json"
        if metadata_file.exists():
            with open(metadata_file) as f:
                return json.load(f)
        return {}
    
    def restore_backup(self, backup_id: str, destination: str) -> bool:
        """Restore from backup"""
        try:
            metadata = self._backups.get(backup_id)
            if not metadata:
                manifest = self._load_manifest()
                metadata_data = manifest.get(backup_id)
                if metadata_data:
                    metadata = BackupMetadata(**metadata_data)
            
            if not metadata:
                logger.error(f"Backup not found: {backup_id}")
                return False
            
            logger.info(f"Restoring backup: {backup_id}")
            
            # Verify checksum
            current_checksum = self._calculate_checksum(metadata.destination_path)
            if current_checksum != metadata.checksum:
                logger.error("Backup checksum mismatch")
                return False
            
            # Extract
            with tarfile.open(metadata.destination_path, "r:*") as tar:
                tar.extractall(destination)
            
            logger.info(f"Backup restored to: {destination}")
            return True
            
        except Exception as e:
            logger.error(f"Restore failed: {e}")
            return False
    
    def cleanup_old_backups(self) -> int:
        """Remove old backups beyond retention period"""
        cutoff = datetime.now() - timedelta(days=self.retention_days)
        removed = 0
        
        manifest = self._load_manifest()
        to_remove = []
        
        for backup_id, metadata in manifest.items():
            created_at = datetime.fromisoformat(metadata["created_at"])
            if created_at <= cutoff:
                to_remove.append(backup_id)
        
        for backup_id in to_remove:
            metadata = manifest[backup_id]
            backup_path = metadata["destination_path"]
            
            try:
                Path(backup_path).unlink(missing_ok=True)
                del manifest[backup_id]
                removed += 1
                logger.info(f"Removed old backup: {backup_id}")
            except Exception as e:
                logger.error(f"Failed to remove backup {backup_id}: {e}")
        
        # Update manifest
        if to_remove:
            metadata_file = self.backup_dir / "backup-manifest.json"
            with open(metadata_file, "w") as f:
                json.dump(manifest, f, indent=2)
        
        return removed
    
    def get_backup_status(self) -> Dict[str, Any]:
        """Get backup status"""
        manifest = self._load_manifest()
        backups = []
        
        for backup_id, metadata in manifest.items():
            path = Path(metadata["destination_path"])
            if path.exists():
                metadata["exists"] = True
                metadata["size_mb"] = round(path.stat().st_size / (1024*1024), 2)
            else:
                metadata["exists"] = False
            backups.append(metadata)
        
        return {
            "total_backups": len(backups),
            "backup_dir": str(self.backup_dir),
            "retention_days": self.retention_days,
            "backups": sorted(backups, key=lambda x: x["created_at"], reverse=True)
        }


class DisasterRecovery:
    """Disaster recovery procedures"""
    
    def __init__(self, backup_manager: BackupManager):
        self.backup_manager = backup_manager
    
    def create_recovery_plan(self) -> Dict[str, Any]:
        """Create disaster recovery plan"""
        return {
            "rpo": "1 hour",  # Recovery Point Objective
            "rto": "4 hours",  # Recovery Time Objective
            "backup_frequency": "daily",
            "retention_period": "30 days",
            "recovery_procedures": [
                "1. Stop all services",
                "2. Restore latest database backup",
                "3. Restore file backups",
                "4. Verify data integrity",
                "5. Restart services",
                "6. Run health checks",
                "7. Notify stakeholders"
            ],
            "contact_list": [
                "CEO: i Made Purna Ananda",
                "IT: [IT Contact]",
                "DBA: [Database Admin]"
            ]
        }
    
    def test_recovery(self, test_backup_id: str) -> Dict[str, Any]:
        """Test disaster recovery procedure"""
        try:
            test_dir = f"test-recovery-{int(time.time())}"
            Path(test_dir).mkdir(exist_ok=True)
            
            success = self.backup_manager.restore_backup(test_backup_id, test_dir)
            
            # Cleanup
            shutil.rmtree(test_dir)
            
            return {
                "test": "recovery",
                "backup_id": test_backup_id,
                "success": success,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Recovery test failed: {e}")
            return {
                "test": "recovery",
                "success": False,
                "error": str(e)
            }


def main():
    """Test backup system"""
    print("Backup & Disaster Recovery system loaded")
    
    backup_manager = BackupManager()
    dr = DisasterRecovery(backup_manager)
    
    plan = dr.create_recovery_plan()
    print(f"Recovery plan created: RPO={plan['rpo']}, RTO={plan['rto']}")


if __name__ == "__main__":
    main()
