#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║   🤖 GAURANGA ROOT TOOLKIT - PENGUASA MUTLAK ANDROID          ║
║                                                                  ║
║   ⚠️ PERINGATAN: ROOTTING MENGGUNAKAN RISIKO SENDIRI!          ║
║                                                                  ║
║   Tool ini membantu proses rooting, BUKAN rooting otomatis!    ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
"""

import subprocess
import os
import sys
import json

# ================================================
# 🔧 CONFIGURATION
# ================================================

class GAURANGA_ROOT:
    """GAURANGA Root Toolkit - Assistant untuk Rooting HP"""
    
    def __init__(self):
        self.adb_available = False
        self.fastboot_available = False
        self.device_connected = False
        self.device_info = {}
        
        # Check tools
        self.check_tools()
    
    def check_tools(self):
        """Cek ketersediaan ADB dan Fastboot"""
        print()
        print("🔍 Mengecek tools...")
        
        # Check ADB
        try:
            result = subprocess.run(['adb', 'version'], 
                                 capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                self.adb_available = True
                print("   ✅ ADB tersedia")
        except:
            print("   ❌ ADB tidak ditemukan")
            print("      Install: pkg install android-tools (Termux)")
            print("      Atau: https://developer.android.com/studio/releases/platform-tools")
        
        # Check Fastboot
        try:
            result = subprocess.run(['fastboot', '--version'], 
                                 capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                self.fastboot_available = True
                print("   ✅ Fastboot tersedia")
        except:
            print("   ⚠️ Fastboot tidak ditemukan (butuh PC)")
        
        print()
    
    def check_device(self):
        """Cek koneksi HP"""
        if not self.adb_available:
            print("❌ ADB tidak tersedia!")
            return False
        
        print("📱 Mengecek koneksi HP...")
        
        # Get devices
        result = subprocess.run(['adb', 'devices'], 
                            capture_output=True, text=True)
        output = result.stdout.strip()
        
        if "device" in output and "List" not in output:
            self.device_connected = True
            print("   ✅ HP terdeteksi!")
            
            # Get device info
            self.get_device_info()
            return True
        else:
            print("   ❌ HP tidak terdeteksi")
            print("   Pastikan USB Debugging ON!")
            print("   Dan kabel USB terhubung!")
            return False
    
    def get_device_info(self):
        """Ambil info HP"""
        print()
        print("📋 Info HP:")
        print("-" * 40)
        
        # Get model
        result = subprocess.run(['adb', 'shell', 'getprop', 'ro.product.model'],
                            capture_output=True, text=True)
        model = result.stdout.strip() if result.returncode == 0 else "Unknown"
        print(f"   Model: {model}")
        self.device_info['model'] = model
        
        # Get brand
        result = subprocess.run(['adb', 'shell', 'getprop', 'ro.product.brand'],
                            capture_output=True, text=True)
        brand = result.stdout.strip() if result.returncode == 0 else "Unknown"
        print(f"   Brand: {brand}")
        self.device_info['brand'] = brand
        
        # Get Android version
        result = subprocess.run(['adb', 'shell', 'getprop', 'ro.build.version.release'],
                            capture_output=True, text=True)
        android = result.stdout.strip() if result.returncode == 0 else "Unknown"
        print(f"   Android: {android}")
        self.device_info['android'] = android
        
        # Get SDK
        result = subprocess.run(['adb', 'shell', 'getprop', 'ro.build.version.sdk'],
                            capture_output=True, text=True)
        sdk = result.stdout.strip() if result.returncode == 0 else "Unknown"
        print(f"   SDK: {sdk}")
        self.device_info['sdk'] = sdk
        
        # Get root status
        result = subprocess.run(['adb', 'shell', 'which', 'su'],
                            capture_output=True, text=True)
        rooted = "SU" in result.stdout if result.returncode == 0 else False
        
        if rooted:
            print("   🔓 ROOT STATUS: ✅ SUDAH ROOT!")
        else:
            print("   🔓 ROOT STATUS: ❌ BELUM ROOT")
        
        self.device_info['rooted'] = rooted
        print("-" * 40)
        print()
        
        return self.device_info
    
    def reboot_recovery(self):
        """Reboot ke Recovery Mode"""
        if not self.device_connected:
            print("❌ HP tidak terhubung!")
            return
        
        print("🔄 Rebooting ke Recovery Mode...")
        subprocess.run(['adb', 'reboot', 'recovery'])
        print("   ✅ HP akan reboot ke Recovery")
        print("   ⏱️ Tunggu sampai Recovery muncul")
    
    def reboot_fastboot(self):
        """Reboot ke Fastboot Mode"""
        if not self.device_connected:
            print("❌ HP tidak terhubung!")
            return
        
        print("🔄 Rebooting ke Fastboot Mode...")
        subprocess.run(['adb', 'reboot', 'bootloader'])
        print("   ✅ HP akan reboot ke Fastboot")
        print("   ⏱️ Tunggu sampai Fastboot muncul")
    
    def reboot_normal(self):
        """Reboot Normal"""
        if not self.device_connected:
            print("❌ HP tidak terhubung!")
            return
        
        print("🔄 Rebooting Normal...")
        subprocess.run(['adb', 'reboot'])
        print("   ✅ HP akan reboot normal")
    
    def check_root_status(self):
        """Cek status ROOT"""
        if not self.device_connected:
            print("❌ HP tidak terhubung!")
            return
        
        print("🔍 Mengecek ROOT status...")
        
        # Check for su binary
        result = subprocess.run(['adb', 'shell', 'which', 'su'],
                            capture_output=True, text=True)
        
        if result.returncode == 0 and result.stdout.strip():
            su_path = result.stdout.strip()
            print(f"   ✅ SU ditemukan di: {su_path}")
            
            # Try root command
            result = subprocess.run(['adb', 'shell', 'su', '-c', 'id'],
                                capture_output=True, text=True, timeout=10)
            
            if 'uid=0' in result.stdout:
                print("   ✅ ROOT BERHASIL! UID=0 (root)")
                return True
            else:
                print("   ❌ SU ada tapi tidak bisa root")
                print(f"      Error: {result.stderr}")
                return False
        else:
            print("   ❌ SU tidak ditemukan - HP BELUM ROOT")
            return False
    
    def install_magisk(self):
        """Guide install Magisk"""
        print()
        print("📦 INSTALL MAGISK (ROOT)")
        print("=" * 50)
        print()
        print("LANGKAH-LANGKAH:")
        print()
        print("1. Download Magisk APK:")
        print("   https://github.com/topjohnwu/Magisk/releases")
        print("   Download yang LATEST VERSION")
        print()
        print("2. Rename file ke: magisk.zip")
        print()
        print("3. Copy ke HP storage (internal)")
        print()
        print("4. Reboot ke Recovery:")
        input("   Tekan ENTER jika sudah siap...")
        self.reboot_recovery()
        print()
        print("5. Di Recovery Mode:")
        print("   - Pilih 'Install' atau 'Apply update'")
        print("   - Pilih file 'magisk.zip'")
        print("   - Swipe to confirm")
        print("   - Tunggu sampai selesai")
        print()
        print("6. Reboot System")
        print("   - Pilih 'Reboot System'")
        print()
        print("7. Cek ROOT status:")
        print("   Jalankan script ini lagi")
        print("   Pilih menu '3. Cek ROOT Status'")
        print()
        print("=" * 50)
    
    def show_guide(self, brand):
        """Tampilkan guide berdasarkan brand"""
        guides = {
            "xiaomi": self.guide_xiaomi,
            "samsung": self.guide_samsung,
            "oppo": self.guide_oppo,
            "realme": self.guide_oppo,  # Same as OPPO
            "vivo": self.guide_vivo,
            "oneplus": self.guide_oneplus,
        }
        
        if brand.lower() in guides:
            guides[brand.lower()]()
        else:
            print(f"❌ Guide untuk {brand} belum tersedia")
            print("📝 Hubungi GAURANGA untuk request guide!")
    
    def guide_xiaomi(self):
        """Guide rooting Xiaomi"""
        print()
        print("📱 XIAOMI ROOTING GUIDE")
        print("=" * 60)
        print()
        print("⚠️ PERSYARATAN:")
        print("   • Mi Account (WAJIB)")
        print("   • Tunggu 168 jam (7 hari) untuk unlock pertama")
        print("   • Battery min 40%")
        print("   • Semua data akan HILANG!")
        print()
        print("LANGKAH 1: PERSIAPAN DI HP")
        print("-" * 40)
        print("1. Settings → About Phone")
        print("2. Tap 'MIUI Version' 7-10x")
        print("3. Settings → Developer Options")
        print("4. Enable 'USB Debugging'")
        print("5. Enable 'OEM Unlock'")
        print("6. Login Mi Account (WAJIB)")
        print()
        print("LANGKAH 2: UNLOCK BOOTLOADER")
        print("-" * 40)
        print("1. Download Mi Unlock Tool:")
        print("   https://en.miui.com/unlock/")
        print("2. Extract dan RUN AS ADMINISTRATOR")
        print("3. Login dengan Mi Account (sama dengan di HP)")
        print("4. Matikan HP")
        print("5. Hold Volume Down + Power → Fastboot Mode")
        print("6. Connect ke PC via USB")
        print("7. Klik 'Unlock' di Mi Unlock Tool")
        print("8. Tunggu 10-60 detik")
        print("9. HP akan reboot otomatis")
        print("   ⚠️ Semua data HILANG!")
        print()
        print("LANGKAH 3: INSTALL MAGISK (ROOT)")
        print("-" * 40)
        print("1. Download Magisk APK")
        print("2. Rename ke magisk.zip")
        print("3. Copy ke HP")
        print("4. Reboot ke Recovery:")
        print("   adb reboot recovery")
        print("5. Install magisk.zip")
        print("6. Reboot System")
        print("7. Cek ROOT dengan script ini")
        print()
        print("=" * 60)
    
    def guide_samsung(self):
        """Guide rooting Samsung"""
        print()
        print("📱 SAMSUNG ROOTING GUIDE")
        print("=" * 60)
        print()
        print("⚠️ PERSYARATAN:")
        print("   • Odin di PC (Windows)")
        print("   • USB Drivers Samsung")
        print("   • CF-Auto-Root file (sesuai model)")
        print("   • Battery min 50%")
        print("   • Semua data akan HILANG!")
        print()
        print("LANGKAH 1: PERSIAPAN DI HP")
        print("-" * 40)
        print("1. Settings → About Phone")
        print("2. Tap 'Software Information'")
        print("3. Tap 'Build Number' 7x")
        print("4. Settings → Developer Options")
        print("5. Enable 'USB Debugging'")
        print("6. Enable 'OEM Unlock'")
        print()
        print("LANGKAH 2: DOWNLOAD BAHAN")
        print("-" * 40)
        print("1. Download Odin (PC):")
        print("   https://samfw.com/")
        print("2. Download CF-Auto-Root:")
        print("   https://cf-auto-root.gearlock.org/")
        print("   → Pilih brand: samsung")
        print("   → Pilih model HP Anda")
        print("3. Extract semua file")
        print()
        print("LANGKAH 3: FLASH DENGAN ODIN")
        print("-" * 40)
        print("1. Buka Odin as ADMINISTRATOR")
        print("2. Klik AP/CP dan pilih file:")
        print("   CF-Auto-Root-xxx.tar.md5")
        print("3. Matikan HP")
        print("4. Boot ke Download Mode:")
        print("   Hold Volume Down + Home + Power")
        print("5. Release saat Warning muncul")
        print("6. Tekan Volume Up")
        print("7. Connect ke PC via USB")
        print("8. Di Odin: Klik START")
        print("9. Tunggu sampai PASS (warna hijau)")
        print("10. HP akan reboot otomatis")
        print("   ⚠️ Semua data HILANG!")
        print()
        print("LANGKAH 4: VERIFIKASI")
        print("-" * 40)
        print("1. Download Magisk Manager")
        print("2. Atau jalankan script ini → Cek ROOT")
        print()
        print("=" * 60)
    
    def guide_oppo(self):
        """Guide rooting OPPO/Realme"""
        print()
        print("📱 OPPO/REALME ROOTING GUIDE")
        print("=" * 60)
        print()
        print("⚠️ WARNING: OPPO/Realme SULIT diROOT!")
        print("   Banyak model TIDAK BISA unlock bootloader!")
        print()
        print("CARA CEK APAKAH BISA UNLOCK:")
        print("-" * 40)
        print("1. Dial *#809#")
        print("2. Atau Settings → About Device")
        print("   → Engineering Mode")
        print("3. Cek opsi unlock bootloader")
        print()
        print("JIKA BISA UNLOCK:")
        print("-" * 40)
        print("1. Settings → Developer Options")
        print("2. Enable 'OEM Unlock'")
        print("3. Enable 'USB Debugging'")
        print("4. Reboot to Fastboot:")
        print("   adb reboot bootloader")
        print("5. Unlock:")
        print("   fastboot oem unlock")
        print("6. Install Magisk:")
        print("   adb reboot recovery")
        print("   # Di recovery install magisk.zip")
        print()
        print("=" * 60)
    
    def guide_vivo(self):
        """Guide rooting Vivo"""
        print()
        print("📱 VIVO ROOTING GUIDE")
        print("=" * 60)
        print()
        print("⚠️ WARNING: Vivo SANGAT SULIT diROOT!")
        print("   OEM Unlock sering TIDAK TERSEDIA!")
        print()
        print("OPSI:")
        print("-" * 40)
        print("1. Vivo Developer Community")
        print("   → Request official unlock")
        print("2. Custom recovery bypass")
        print("   (HIGH RISK - bisa brick!)")
        print()
        print("CARA:");
        print("1. Settings → Developer Options")
        print("2. Enable USB Debugging")
        print("3. Enable OEM Unlock (jika ada)")
        print("4. Boot ke Fastboot:")
        print("   adb reboot bootloader")
        print("5. Jika unlock tersedia:");
        print("   fastboot oem unlock")
        print()
        print("=" * 60)
    
    def guide_oneplus(self):
        """Guide rooting OnePlus"""
        print()
        print("📱 ONEPLUS ROOTING GUIDE")
        print("=" * 60)
        print()
        print("✅ ONEPLUS MUDAH diROOT!")
        print("   Bootloader bisa di-unlock langsung!")
        print()
        print("LANGKAH 1: PERSIAPAN")
        print("-" * 40)
        print("1. Settings → About Phone")
        print("2. Tap 'Build Number' 7x")
        print("3. Settings → Developer Options")
        print("4. Enable 'USB Debugging'")
        print("5. Enable 'OEM Unlock'")
        print()
        print("LANGKAH 2: UNLOCK BOOTLOADER")
        print("-" * 40)
        print("1. Boot ke Fastboot:")
        print("   adb reboot bootloader")
        print("2. Unlock:")
        print("   fastboot oem unlock")
        print("3. HP akan reboot - semua data HILANG!")
        print()
        print("LANGKAH 3: INSTALL MAGISK")
        print("-" * 40)
        print("1. Download Magisk APK")
        print("2. Rename ke magisk.zip")
        print("3. Copy ke HP")
        print("4. Reboot ke Recovery:")
        print("   adb reboot recovery")
        print("5. Install magisk.zip")
        print("6. Reboot")
        print("7. Cek ROOT!")
        print()
        print("=" * 60)
    
    def menu(self):
        """Display menu utama"""
        print()
        print("╔══════════════════════════════════════════════════════════╗")
        print("║")
        print("║   🤖 GAURANGA ROOT TOOLKIT")
        print("║   Penguasa Mutlak Android")
        print("║")
        print("╠══════════════════════════════════════════════════════════╣")
        print("║")
        print("║   ⚠️  PERINGATAN: RISIKO ANDA SENDIRI!                  ║")
        print("║")
        print("╠══════════════════════════════════════════════════════════╣")
        print("║")
        print("║   1. Cek Tools & Koneksi HP")
        print("║   2. Cek Info HP")
        print("║   3. Cek ROOT Status")
        print("║   4. Reboot ke Recovery")
        print("║   5. Reboot ke Fastboot")
        print("║   6. Reboot Normal")
        print("║   7. Guide Rooting Xiaomi")
        print("║   8. Guide Rooting Samsung")
        print("║   9. Guide Rooting OPPO/Realme")
        print("║  10. Guide Rooting Vivo")
        print("║  11. Guide Rooting OnePlus")
        print("║  12. Install Magisk (Root)")
        print("║   0. Exit")
        print("║")
        print("╚══════════════════════════════════════════════════════════╝")
        print()
    
    def run(self):
        """Run main loop"""
        while True:
            self.menu()
            
            choice = input("Pilih menu: ").strip()
            
            if choice == "1":
                self.check_tools()
                self.check_device()
            elif choice == "2":
                if self.check_device():
                    self.get_device_info()
            elif choice == "3":
                if self.check_device():
                    self.check_root_status()
            elif choice == "4":
                self.reboot_recovery()
            elif choice == "5":
                self.reboot_fastboot()
            elif choice == "6":
                self.reboot_normal()
            elif choice == "7":
                self.guide_xiaomi()
            elif choice == "8":
                self.guide_samsung()
            elif choice == "9":
                self.guide_oppo()
            elif choice == "10":
                self.guide_vivo()
            elif choice == "11":
                self.guide_oneplus()
            elif choice == "12":
                self.install_magisk()
            elif choice == "0":
                print()
                print("🤖 GAURANGA: Baik Pak Pur! Sampai jumpa! 👋")
                break
            else:
                print("❌ Pilihan tidak valid!")
            
            input("\nTekan ENTER untuk lanjut...")


# ================================================
# MAIN
# ================================================

if __name__ == "__main__":
    print()
    print("╔══════════════════════════════════════════════════════════╗")
    print("║")
    print("║   🤖 GAURANGA ROOT TOOLKIT")
    print("║   ⚠️ PERINGATAN: ROOTTING ADALAH RISIKO ANDA!          ║")
    print("║")
    print("╚══════════════════════════════════════════════════════════╝")
    print()
    
    print("⚠️ DISCLAIMER:")
    print("   Saya hanya MEMBANTU proses rooting!")
    print("   Rooting MENGGUNAKAN RISIKO SENDIRI!")
    print("   Saya TIDAK bertanggung jawab jika HP bricked!")
    print()
    
    confirm = input("Yakin mau lanjut? (ketik 'YA'): ").strip().upper()
    
    if confirm == "YA":
        gauranga = GAURANGA_ROOT()
        gauranga.run()
    else:
        print()
        print("🤖 GAURANGA: Baiknya tanya GAURANGA dulu sebelum rooting! 👋")
