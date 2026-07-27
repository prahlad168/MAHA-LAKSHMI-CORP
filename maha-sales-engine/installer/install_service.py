#!/usr/bin/env python3
"""
MAHA SALES ENGINE V1 - Windows Service Installer
Usage:
    python installer/install_service.py install   # Install service
    python installer/install_service.py start     # Start service
    python installer/install_service.py stop      # Stop service
    python installer/install_service.py remove    # Remove service
"""

import win32serviceutil
import win32service
import win32event
import os
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def install_service():
    """Install the Windows service"""
    print("Installing MAHA Sales Engine Service...")
    
    service_name = "MahaSalesEngine"
    display_name = "MAHA Sales Engine V1"
    description = "Autonomous Digital Sales Engine for MAHA LAKSHMI HOLDINGS"
    
    # Create service
    win32serviceutil.InstallService(
        pythonClassString="maha_sales_engine.installer.windows_service.MahaSalesEngineService",
        serviceName=service_name,
        displayName=display_name,
        description=description
    )
    
    print(f"✅ Service installed: {service_name}")
    print(f"   Display Name: {display_name}")
    print(f"   Description: {description}")
    print(f"\nTo start the service:")
    print(f"   python installer/install_service.py start")
    print(f"\nOr use Windows Services Manager:")
    print(f"   services.msc")


def remove_service():
    """Remove the Windows service"""
    print("Removing MAHA Sales Engine Service...")
    win32serviceutil.RemoveService("MahaSalesEngine")
    print("✅ Service removed")


def main():
    """Main installer entry point"""
    if len(sys.argv) == 1:
        print("Usage:")
        print("  python installer/install_service.py install   # Install service")
        print("  python installer/install_service.py start     # Start service")
        print("  python installer/install_service.py stop      # Stop service")
        print("  python installer/install_service.py remove    # Remove service")
        return
    
    command = sys.argv[1].lower()
    
    if command == "install":
        install_service()
    elif command == "remove":
        remove_service()
    else:
        # Pass other commands to win32serviceutil
        win32serviceutil.HandleCommandLine(
            win32serviceutil.GetServiceClassString("maha_sales_engine.installer.windows_service.MahaSalesEngineService"),
            command
        )


if __name__ == '__main__':
    main()
