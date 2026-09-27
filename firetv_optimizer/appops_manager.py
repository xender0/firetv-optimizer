"""AppOps and background process restriction manager."""

from typing import List, Tuple
from .adb_client import AdbClient
from .debloat import DebloatManager


class AppOpsManager:
    def __init__(self, adb: AdbClient, debloat_manager: DebloatManager):
        self.adb = adb
        self.debloat = debloat_manager

    def restrict_package(self, pkg: str) -> None:
        """Apply dormancy policies on an individual package."""
        self.adb.shell(f"appops set {pkg} WAKE_LOCK ignore")
        self.adb.shell(f"appops set {pkg} POST_NOTIFICATION ignore")
        self.adb.shell(f"appops set {pkg} SYSTEM_ALERT_WINDOW deny")
        self.adb.shell(f"am force-stop {pkg}")

    def restrict_all_bloat(self, progress_callback=None) -> List[Tuple[str, bool]]:
        """Apply AppOps dormancy across all known Amazon telemetry and bloat services."""
        pkgs = self.debloat.get_all_bloat_packages()
        results = []

        total = len(pkgs)
        for idx, pkg in enumerate(pkgs):
            if progress_callback:
                progress_callback(pkg, idx + 1, total)

            self.restrict_package(pkg)
            results.append((pkg, True))

        return results
