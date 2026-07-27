#!/usr/bin/env python3
"""
MAHA SALES ENGINE V1 - Windows Service Wrapper
Install as Windows Service using: python installer/install_service.py install
"""

import win32serviceutil
import win32service
import win32event
import servicemanager
import socket
import sys
import os
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class MahaSalesEngineService(win32serviceutil.ServiceFramework):
    """Windows Service for MAHA Sales Engine"""
    
    _svc_name_ = "MahaSalesEngine"
    _svc_display_name_ = "MAHA Sales Engine V1"
    _svc_description_ = "Autonomous Digital Sales Engine for MAHA LAKSHMI HOLDINGS"
    
    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.stop_event = win32event.CreateEvent(None, 0, 0, None)
        self.engine = None
        socket.setdefaulttimeout(60)
    
    def SvcStop(self):
        """Stop the service"""
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.stop_event)
        
        if self.engine:
            self.engine.stop()
    
    def SvcDoRun(self):
        """Run the service"""
        servicemanager.LogMsg(
            servicemanager.EVENTLOG_INFORMATION_TYPE,
            servicemanager.PYS_SERVICE_STARTED,
            (self._svc_name_, '')
        )
        
        # Import and start engine
        try:
            from main import main
            main()
        except Exception as e:
            servicemanager.LogErrorMsg(f"Service error: {e}")


def main():
    """Service entry point"""
    if len(sys.argv) == 1:
        # Run as service
        win32serviceutil.HandleCommandLine(MahaSalesEngineService)
    else:
        # Run as console for debugging
        print("Running MAHA Sales Engine in console mode...")
        print("Press Ctrl+C to stop")
        try:
            from main import main as engine_main
            engine_main()
        except KeyboardInterrupt:
            print("\nShutting down...")


if __name__ == '__main__':
    main()
