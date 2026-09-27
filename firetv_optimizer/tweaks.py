"""System tweaks, telemetry lockdown, and UI responsiveness."""

from typing import Dict
from .adb_client import AdbClient


class SystemTweaks:
    def __init__(self, adb: AdbClient):
        self.adb = adb

    def boost_animations(self) -> None:
        """Set UI animation scales to 0 in both global and system tables for instant responsiveness."""
        scales = ["window_animation_scale", "transition_animation_scale", "animator_duration_scale"]
        for s in scales:
            self.adb.shell(f"settings put global {s} 0")
            self.adb.shell(f"settings put system {s} 0")

    def lockdown_telemetry_and_ads(self) -> None:
        """Lock down ad-tracking, diagnostics upload, and Amazon telemetry."""
        secure_settings = {
            "limit_ad_tracking": "1",
            "amz_limit_ad_tracking": "1",
            "non_amz_limit_ad_tracking": "1",
            "advertisingIdApp:interestBasedAds:value": "0",
            "usage_metrics_marketing_enabled": "0",
            "USAGE_METRICS_UPLOAD_ENABLED": "0",
            "settingsApp:deviceUsageData:value": "0",
            "settingsApp:appUsageData:value": "0",
            "rdm_enabled": "0",
            "amz_appstore_auto_update": "0"
        }
        for key, val in secure_settings.items():
            self.adb.shell(f"settings put secure {key} {val}")

        # Block OTA auto-download
        self.adb.shell("settings put global ota_disable_automatic_update 1")

    def disable_home_video_previews(self) -> None:
        """Disable video previews and mute audio on the Amazon home banner."""
        self.adb.shell("settings put global com.amazon.tv.settings.featured_item_video_enabled 0")
        self.adb.shell("settings put global com.amazon.tv.settings.featured_item_video_volume 0.0")

    def set_background_process_limit(self, limit: int = 3) -> None:
        """Limit concurrent background processes to prevent out-of-memory crashes during streaming."""
        self.adb.shell(f"settings put global standard_process_limit {limit}")

    def set_sleep_timeout(self, timeout_minutes: int = 10) -> None:
        """Set device sleep and screen-off timeout (in minutes)."""
        ms = timeout_minutes * 60 * 1000
        self.adb.shell(f"settings put secure sleep_timeout {ms}")
        self.adb.shell(f"settings put system screen_off_timeout {ms}")

    def get_current_settings(self) -> Dict[str, str]:
        """Fetch current values for key settings."""
        keys = [
            ("global", "window_animation_scale"),
            ("global", "standard_process_limit"),
            ("global", "com.amazon.tv.settings.featured_item_video_enabled"),
            ("secure", "limit_ad_tracking"),
            ("secure", "sleep_timeout"),
            ("secure", "amz_appstore_auto_update")
        ]
        status = {}
        for ns, k in keys:
            code, val = self.adb.shell(f"settings get {ns} {k}")
            status[f"{ns}.{k}"] = val if code == 0 else "unknown"
        return status
