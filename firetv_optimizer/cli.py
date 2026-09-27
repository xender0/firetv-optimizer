"""Command Line Interface for Fire TV Optimizer."""

import argparse
import sys
import time
from .adb_client import AdbClient
from .debloat import DebloatManager
from .appops_manager import AppOpsManager
from .tweaks import SystemTweaks
from .launcher import LauncherManagerHelper

# ANSI Color codes for clean output
GREEN = "\033[92m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
RED = "\033[91m"
BOLD = "\033[1m"
RESET = "\033[0m"


def print_banner():
    banner = f"""{CYAN}{BOLD}
╔═══════════════════════════════════════════════════════════════╗
║                  Fire TV Optimizer & Debloater                ║
║           Transform Fire TV into a Clean & Fast Stick         ║
╚═══════════════════════════════════════════════════════════════╝{RESET}"""
    print(banner)


def cmd_audit(adb: AdbClient, debloat: DebloatManager, tweaks: SystemTweaks, launcher: LauncherManagerHelper):
    print(f"\n{BOLD}=== DEVICE DIAGNOSTICS & AUDIT ==={RESET}")
    info = adb.get_device_info()
    print(f"Device Serial:   {CYAN}{info['device']}{RESET}")
    print(f"Model:           {info['model']}")
    print(f"Fire OS Version: {info['fireos_version']}")
    print(f"Android Base:    {info['android_version']}")

    # Memory
    _, mem = adb.shell("cat /proc/meminfo | grep -E 'MemTotal|MemAvailable'")
    print(f"\n{BOLD}Memory Info:{RESET}\n{mem}")

    # Storage
    _, df = adb.shell("df /data /cache")
    print(f"\n{BOLD}Storage Info:{RESET}\n{df}")

    # Launcher status
    leanback = launcher.is_leanback_installed()
    lm = launcher.is_lm_installed()
    print(f"\n{BOLD}Launcher Status:{RESET}")
    print(f"  Leanback Launcher Installed: {GREEN + 'Yes' if leanback else RED + 'No'}{RESET}")
    print(f"  Launcher Manager Installed:  {GREEN + 'Yes' if lm else RED + 'No'}{RESET}")

    # Settings status
    settings = tweaks.get_current_settings()
    print(f"\n{BOLD}Current Tweaks:{RESET}")
    for k, v in settings.items():
        print(f"  {k}: {CYAN}{v}{RESET}")


def cmd_quick_boost(adb: AdbClient, debloat: DebloatManager, appops: AppOpsManager, tweaks: SystemTweaks):
    print(f"\n{BOLD}{CYAN}=== RUNNING ALL-IN-ONE QUICK BOOST ==={RESET}")

    print(f"\n[1/4] {YELLOW}Applying instant UI animation scales (0.0)...{RESET}")
    tweaks.boost_animations()
    print(f"      {GREEN}✓ Animation scales set to 0 in global & system tables{RESET}")

    print(f"\n[2/4] {YELLOW}Enforcing Telemetry, Ad-Tracking & Auto-Update Lockdown...{RESET}")
    tweaks.lockdown_telemetry_and_ads()
    tweaks.disable_home_video_previews()
    tweaks.set_background_process_limit(3)
    tweaks.set_sleep_timeout(10)
    print(f"      {GREEN}✓ Privacy locked, autoplay banners disabled, RAM limit configured (3 processes){RESET}")

    print(f"\n[3/4] {YELLOW}Stripping bloated Amazon updates from /data/app...{RESET}")
    stripped = debloat.strip_bloat_updates()
    if stripped:
        for pkg, ok, _ in stripped:
            status = f"{GREEN}Cleaned{RESET}" if ok else f"{RED}Failed{RESET}"
            print(f"      - {pkg}: {status}")
    else:
        print(f"      {GREEN}✓ No bloated updates lingering in /data/app{RESET}")

    print(f"\n[4/4] {YELLOW}Enforcing AppOps background dormancy across all bloat services...{RESET}")
    def progress(pkg, current, total):
        sys.stdout.write(f"\r      Processing [{current}/{total}] {pkg}...")
        sys.stdout.flush()

    appops.restrict_all_bloat(progress_callback=progress)
    print(f"\n      {GREEN}✓ Dormancy and force-stops applied to all bloat services{RESET}")

    print(f"\n{BOLD}{GREEN}All-in-one optimization complete! Device is fast, light, and responsive.{RESET}\n")


def cmd_strip_updates(debloat: DebloatManager):
    print(f"\n{BOLD}{YELLOW}=== STRIPPING BLOATWARE UPDATES FROM /DATA/APP ==={RESET}")
    results = debloat.strip_bloat_updates()
    if not results:
        print(f"{GREEN}All bloatware packages are already at clean factory stubs.{RESET}")
        return

    for pkg, ok, out in results:
        if ok:
            print(f"{GREEN}✓ Reverted {pkg} to factory stub (freed user storage){RESET}")
        else:
            print(f"{RED}✗ Could not revert {pkg}: {out}{RESET}")


def cmd_appops_restrict(appops: AppOpsManager):
    print(f"\n{BOLD}{YELLOW}=== APPLYING APPOPS RESTRICTIONS ACROSS BLOAT SERVICES ==={RESET}")
    def progress(pkg, current, total):
        sys.stdout.write(f"\rRestricting [{current}/{total}]: {pkg}...")
        sys.stdout.flush()

    appops.restrict_all_bloat(progress_callback=progress)
    print(f"\n{GREEN}✓ All services restricted and terminated.{RESET}")


def cmd_uninstall_redundant(debloat: DebloatManager):
    print(f"\n{BOLD}{YELLOW}=== UNINSTALLING REDUNDANT APPS ==={RESET}")
    redundant = [
        ("com.amazon.firetv.youtube", "Official YouTube (SmartTube is preferred)"),
        ("com.cor.defsquid", "DefSquid (background scanner)"),
        ("com.estrongs.android.pop.pro", "ES File Explorer Pro")
    ]
    for pkg, name in redundant:
        print(f"Uninstalling {name} ({pkg})...")
        ok, out = debloat.uninstall_package(pkg)
        if ok:
            print(f"  {GREEN}✓ Uninstalled successfully{RESET}")
        else:
            print(f"  {YELLOW}Note: {out}{RESET}")


def interactive_menu(adb, debloat, appops, tweaks, launcher):
    while True:
        print_banner()
        print("Select an option:")
        print("  1. Device Audit & Diagnostic Status")
        print("  2. Full Quick Boost (Recommended All-in-One)")
        print("  3. Strip Bloat Updates (Free Internal Storage)")
        print("  4. Enforce AppOps Background Dormancy")
        print("  5. Apply UI Animations (0.0) & Telemetry Lockdown")
        print("  6. Launch / Configure Launcher Manager (FOS5)")
        print("  7. Uninstall Redundant Apps (YouTube, DefSquid, ES File Explorer)")
        print("  0. Exit")

        choice = input("\nEnter choice [0-7]: ").strip()
        if choice == "1":
            cmd_audit(adb, debloat, tweaks, launcher)
        elif choice == "2":
            cmd_quick_boost(adb, debloat, appops, tweaks)
        elif choice == "3":
            cmd_strip_updates(debloat)
        elif choice == "4":
            cmd_appops_restrict(appops)
        elif choice == "5":
            tweaks.boost_animations()
            tweaks.lockdown_telemetry_and_ads()
            tweaks.disable_home_video_previews()
            tweaks.set_background_process_limit(3)
            print(f"\n{GREEN}✓ Settings tweaks applied!{RESET}")
        elif choice == "6":
            launcher.grant_permissions()
            launcher.open_launcher_manager()
            print(f"\n{GREEN}✓ Launcher Manager launched on TV with granted permissions!{RESET}")
        elif choice == "7":
            cmd_uninstall_redundant(debloat)
        elif choice == "0":
            print("Exiting.")
            break
        else:
            print(f"{RED}Invalid option.{RESET}")

        input("\nPress Enter to continue...")


def main():
    parser = argparse.ArgumentParser(description="Fire TV Optimizer & Debloater Toolkit")
    parser.add_argument("--host", help="Fire TV IP address (optional if connected via USB/ADB)")
    parser.add_argument("--port", type=int, default=5555, help="ADB Port (default: 5555)")

    subparsers = parser.add_subparsers(dest="command")
    subparsers.add_parser("audit", help="Run full device diagnostics audit")
    subparsers.add_parser("quick-boost", help="Run all-in-one recommended optimization pipeline")
    subparsers.add_parser("strip-updates", help="Strip bloatware updates from /data/app")
    subparsers.add_parser("restrict-bloat", help="Apply AppOps dormancy across bloat services")
    subparsers.add_parser("tweaks", help="Apply animation, privacy, and process limit tweaks")
    subparsers.add_parser("uninstall-redundant", help="Uninstall redundant apps (YouTube, DefSquid, etc.)")

    args = parser.parse_args()

    adb = AdbClient(target_host=args.host, port=args.port)
    if not adb.connect():
        devices = adb.get_connected_devices()
        if not devices:
            print(f"{RED}Error: No ADB device found. Ensure ADB debugging is enabled and specify --host <IP>.{RESET}")
            sys.exit(1)

    debloat = DebloatManager(adb)
    appops = AppOpsManager(adb, debloat)
    tweaks = SystemTweaks(adb)
    launcher = LauncherManagerHelper(adb)

    if args.command == "audit":
        cmd_audit(adb, debloat, tweaks, launcher)
    elif args.command == "quick-boost":
        cmd_quick_boost(adb, debloat, appops, tweaks)
    elif args.command == "strip-updates":
        cmd_strip_updates(debloat)
    elif args.command == "restrict-bloat":
        cmd_appops_restrict(appops)
    elif args.command == "tweaks":
        tweaks.boost_animations()
        tweaks.lockdown_telemetry_and_ads()
        tweaks.disable_home_video_previews()
        tweaks.set_background_process_limit(3)
        print(f"{GREEN}✓ Tweaks applied successfully.{RESET}")
    elif args.command == "uninstall-redundant":
        cmd_uninstall_redundant(debloat)
    else:
        interactive_menu(adb, debloat, appops, tweaks, launcher)


if __name__ == "__main__":
    main()
