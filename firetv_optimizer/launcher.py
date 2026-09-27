"""Custom launcher setup and Launcher Manager configuration."""

import os
from typing import Tuple
from .adb_client import AdbClient

LM_PKG_FOS5 = "com.wolf.fos5.settings"
LEANBACK_PKG = "com.amazon.tv.leanbacklauncher"


class LauncherManagerHelper:
    def __init__(self, adb: AdbClient):
        self.adb = adb

    def is_leanback_installed(self) -> bool:
        code, out = self.adb.shell(f"pm list packages {LEANBACK_PKG}")
        return LEANBACK_PKG in out

    def is_lm_installed(self) -> bool:
        code, out = self.adb.shell(f"pm list packages {LM_PKG_FOS5}")
        return LM_PKG_FOS5 in out

    def install_lm_apk(self, apk_path: str) -> Tuple[bool, str]:
        """Install Launcher Manager APK from a given file path."""
        if not os.path.exists(apk_path):
            return False, f"APK file not found: {apk_path}"

        code, out = self.adb.run_cmd(["install", "-r", apk_path])
        success = "success" in out.lower()
        if success:
            self.grant_permissions()
        return success, out

    def grant_permissions(self) -> None:
        """Grant required permissions (READ_LOGS for Watchdog, etc.)."""
        self.adb.shell(f"pm grant {LM_PKG_FOS5} android.permission.READ_LOGS")

    def open_launcher_manager(self) -> Tuple[int, str]:
        """Launch the Launcher Manager configuration UI on the TV."""
        return self.adb.shell(f"am start -n {LM_PKG_FOS5}/.SettingsActivity")

    def press_home(self) -> None:
        """Simulate pressing the remote Home button."""
        self.adb.shell("input keyevent 3")
