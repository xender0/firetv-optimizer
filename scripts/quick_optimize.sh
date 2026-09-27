#!/usr/bin/env bash
# ==============================================================================
# Fire TV Quick Optimizer & Debloater
# Works over USB or Wi-Fi ADB without external dependencies.
# ==============================================================================

set -e

DEVICE_IP="${1:-}"

if [ -n "$DEVICE_IP" ]; then
    echo "Connecting to Fire TV at $DEVICE_IP..."
    adb disconnect "$DEVICE_IP:5555" 2>/dev/null || true
    adb connect "$DEVICE_IP:5555"
fi

echo "Checking connected ADB devices..."
adb devices

echo ""
echo "=========================================================="
echo " [1/5] Setting UI Animation Scales to 0.0 (Instant UI) "
echo "=========================================================="
adb shell settings put global window_animation_scale 0
adb shell settings put global transition_animation_scale 0
adb shell settings put global animator_duration_scale 0
adb shell settings put system window_animation_scale 0
adb shell settings put system transition_animation_scale 0
adb shell settings put system animator_duration_scale 0

echo ""
echo "=========================================================="
echo " [2/5] Locking Down Privacy, Telemetry & Auto-Updates "
echo "=========================================================="
adb shell settings put secure limit_ad_tracking 1
adb shell settings put secure amz_limit_ad_tracking 1
adb shell settings put secure non_amz_limit_ad_tracking 1
adb shell settings put secure advertisingIdApp:interestBasedAds:value 0
adb shell settings put secure usage_metrics_marketing_enabled 0
adb shell settings put secure USAGE_METRICS_UPLOAD_ENABLED 0
adb shell settings put secure settingsApp:deviceUsageData:value 0
adb shell settings put secure settingsApp:appUsageData:value 0
adb shell settings put secure rdm_enabled 0
adb shell settings put secure amz_appstore_auto_update 0
adb shell settings put global ota_disable_automatic_update 1
adb shell settings put global com.amazon.tv.settings.featured_item_video_enabled 0
adb shell settings put global com.amazon.tv.settings.featured_item_video_volume 0.0

echo ""
echo "=========================================================="
echo " [3/5] Setting RAM Management & Sleep Timeout "
echo "=========================================================="
adb shell settings put global standard_process_limit 3
adb shell settings put secure sleep_timeout 600000
adb shell settings put system screen_off_timeout 600000

echo ""
echo "=========================================================="
echo " [4/5] Restricting Background Bloat Services (AppOps) "
echo "=========================================================="
BLOAT_PACKAGES=(
    "com.amazon.device.crashmanager"
    "com.amazon.device.logmanager"
    "com.amazon.dp.logger"
    "com.amazon.client.metrics"
    "com.amazon.client.metrics.api"
    "com.amazon.perfcollection"
    "com.amazon.tv.fw.metrics"
    "com.amazon.metrics.api"
    "com.fireos.usagestats.proxy"
    "com.amazon.device.metrics"
    "com.amazon.device.software.ota"
    "com.amazon.device.software.ota.override"
    "com.amazon.tv.forcedotaupdater.v2"
    "com.amazon.alexashopping"
    "com.amazon.shoptv.client"
    "com.amazon.shoptv.firetv.client"
    "com.amazon.bueller.photos"
    "com.amazon.bueller.music"
    "com.amazon.gamehub"
    "com.amazon.minitv.android.app"
    "com.imdb.livingroom.firetv"
    "com.amazon.tv.livetv"
    "com.amazon.alexamediaplayer.runtime.ftv"
    "com.amazon.tmm.tutorial"
    "com.amazon.storm.lightning.tutorial"
    "com.amazon.kor.demo"
    "com.amazon.tv.support"
    "com.amazon.whisperjoin.wss.wifiprovisioner"
    "com.amazon.whisperjoin.middleware.np"
    "com.amazon.tahoe"
    "com.amazon.hedwig"
    "com.amazon.aria"
)

for pkg in "${BLOAT_PACKAGES[@]}"; do
    echo "Restricting: $pkg"
    adb shell appops set "$pkg" WAKE_LOCK ignore 2>/dev/null || true
    adb shell appops set "$pkg" POST_NOTIFICATION ignore 2>/dev/null || true
    adb shell appops set "$pkg" SYSTEM_ALERT_WINDOW deny 2>/dev/null || true
    adb shell am force-stop "$pkg" 2>/dev/null || true
done

echo ""
echo "=========================================================="
echo " [5/5] Granting Launcher Manager Watchdog Permissions "
echo "=========================================================="
if adb shell pm list packages | grep -q "com.wolf.fos5.settings"; then
    adb shell pm grant com.wolf.fos5.settings android.permission.READ_LOGS 2>/dev/null || true
    echo "✓ Launcher Manager (FOS5) READ_LOGS permission granted."
fi

echo ""
echo "=========================================================="
echo " Optimization Complete! Your Fire TV is fast & lightweight."
echo "=========================================================="
