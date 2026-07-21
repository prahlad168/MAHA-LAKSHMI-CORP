#!/usr/bin/env python3
"""
GAURANGA ROOT TOOLKIT - Simple Version
GAURANGA Penguasa Android - Versi Simpel
"""
import subprocess,os,sys

def check():
    print("\n=== GAURANGA ROOT CHECK ===")
    try:
        r=subprocess.run(['adb','version'],capture_output=True,text=True)
        if r.returncode==0: print("[OK] ADB Available")
        else: print("[FAIL] ADB Not Found")
    except: print("[FAIL] ADB Not Found")
    
    try:
        r=subprocess.run(['adb','devices'],capture_output=True,text=True)
        if 'device' in r.stdout and 'List' not in r.stdout: print("[OK] HP Connected!")
        else: print("[!] HP Not Detected - Enable USB Debugging!")
    except: print("[!] HP Not Connected")

def info():
    print("\n=== HP INFO ===")
    for prop in ['ro.product.model','ro.product.brand','ro.build.version.release']:
        r=subprocess.run(['adb','shell','getprop',prop],capture_output=True,text=True)
        if r.returncode==0: print(f"  {prop}: {r.stdout.strip()}")

def menu():
    print("""
╔══════════════════════════════════════════════╗
║   GAURANGA ROOT TOOLKIT                   ║
╠══════════════════════════════════════════════╣
║  1. Check ADB & Connection                ║
║  2. Show HP Info                         ║
║  3. Reboot Recovery                       ║
║  4. Reboot Fastboot                      ║
║  5. Reboot Normal                        ║
║  0. Exit                                 ║
╚══════════════════════════════════════════════╝
""")
    while True:
        c=input("Pilih: ").strip()
        if c=="1": check()
        elif c=="2": info()
        elif c=="3": 
            print("Rebooting to Recovery...")
            subprocess.run(['adb','reboot','recovery'])
        elif c=="4":
            print("Rebooting to Fastboot...")
            subprocess.run(['adb','reboot','bootloader'])
        elif c=="5":
            print("Rebooting...")
            subprocess.run(['adb','reboot'])
        elif c=="0": break
        else: print("Invalid!")

if __name__=="__main__":
    print("GAURANGA ROOT TOOLKIT v1.0")
    print("WARNING: Rooting risks are YOUR responsibility!\n")
    menu()
