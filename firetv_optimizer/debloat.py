"""Package debloating and storage cleanup module."""

import json
import os
from typing import Dict, List, Tuple
from .adb_client import AdbClient

DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "bloat_packages.json")


class DebloatManager:
    def __init__(self, adb: AdbClient):
        self.adb = adb
        self.data = self._load_data()

    def _load_data(self) -> dict:
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            return json.load(f)

    def get_all_bloat_packages(self) -> List[str]:
        pkgs = []
        for cat in self.data["categories"].values():
            pkgs.extend(cat["packages"])
        return sorted(list(set(pkgs)))

    def inspect_packages(self) -> Dict[str, dict]:
        """Classify packages on device into user-updates (/data/app) vs system-stubs (/system)."""
        code, out = self.adb.shell("pm list packages -f")
        if code != 0:
            return {}

        results = {}
        for line in out.splitlines():
            line = line.strip()
            if line.startswith("package:"):
                raw = line.replace("package:", "")
                if "=" in raw:
                    path, pkg = raw.rsplit("=", 1)
                    is_update = path.startswith("/data/app/")
                    results[pkg] = {
                        "path": path,
                        "is_update": is_update,
                        "is_system": path.startswith("/system/")
                    }
        return results

    def strip_bloat_updates(self) -> List[Tuple[str, bool, str]]:
        """
        Uninstall accumulated updates for bloatware from /data/app.
        Reverts packages to clean factory stubs in /system/priv-app, freeing storage.
        """
        installed = self.inspect_packages()
        bloat_list = self.get_all_bloat_packages()
        results = []

        for pkg in bloat_list:
            if pkg in installed and installed[pkg]["is_update"]:
                code, out = self.adb.shell(f"pm uninstall -k --user 0 {pkg}")
                success = "success" in out.lower()
                results.append((pkg, success, out))

        return results

    def uninstall_package(self, pkg: str, force: bool = False) -> Tuple[bool, str]:
        """Safely uninstall a user package with protected whitelist check."""
        protected = self.data.get("protected_streaming_apps", [])
        if pkg in protected and not force:
            return False, f"Package {pkg} is protected (Core Streaming App). Use force=True to override."

        code, out = self.adb.run_cmd(["uninstall", pkg])
        success = "success" in out.lower()
        return success, out
