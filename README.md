# Fire TV Optimizer & Debloater 🚀

An all-in-one optimization, debloating, and telemetry lockdown toolkit designed to transform slow, ad-heavy Amazon Fire TV devices into lightning-fast, privacy-friendly streaming devices.

Specifically engineered with specialized handling for **Fire OS 5 (Fire TV Stick 2nd Gen / AFTT)** as well as compatible with **Fire OS 6, 7, and 8**.

---

## 💡 The Problem with Fire TV Sticks

Older Fire TV sticks (like the 2nd Gen Fire TV Stick) only have **1 GB of RAM** and limited storage. Over time:
1. **Bloated App Updates:** Amazon silently downloads hundreds of megabytes of updates to unused system apps (Shopping, Photos, Music, GameCircle) into `/data/app`.
2. **Reversion on Reboot:** On Fire OS 5, trying to delete root system apps results in `DELETE_FAILED_INTERNAL_ERROR`, and Fire OS automatically restores uninstalled system packages on every restart.
3. **Heavy Stock Launcher:** The Amazon home screen streams video previews, sponsored banners, and ad carousels that hoard memory and CPU.
4. **Continuous Telemetry:** Background analytics and logging daemons constantly wake the CPU, causing frame drops and audio stuttering in video apps.

---

## 🛠️ What This Toolkit Does

* ⚡ **Custom Launcher Interceptor:** Sets up **Launcher Manager (FOS5)** and **Leanback Launcher** (`LeanbackOnFire`) with required `READ_LOGS` permissions, so pressing **Home** opens a clean, ad-free Android TV interface.
* 🧹 **Update Stripper:** Strips bloated Amazon updates from `/data/app` back to read-only factory stubs, freeing **500 MB – 1 GB+** of user storage without triggering boot errors.
* 🛑 **AppOps Dormancy Engine:** Cuts off `WAKE_LOCK`, `POST_NOTIFICATION`, and `SYSTEM_ALERT_WINDOW` across **60+ Amazon bloat and telemetry services**, keeping them permanently dormant.
* 🏎️ **Instant 0.0s UI Animations:** Locks animation scales in both `global` and `system` tables to `0` for instantaneous menu and app switching.
* 🔒 **Telemetry & Ad Lockdown:** Disables ad-tracking IDs, marketing metrics, device usage monitoring, and home banner autoplay video/audio.
* 🧠 **RAM & Process Management:** Enforces a maximum background process limit (`standard_process_limit = 3`) to guarantee 100% of RAM and CPU goes to your active streaming app (Stremio, Netflix, SmartTube).
* 🛡️ **Appstore Auto-Update Freeze:** Prevents Amazon Appstore from silently re-downloading bloated app updates in the background.

---

## 📋 Prerequisites

1. **Fire TV Stick** connected to the same Wi-Fi network as your computer (or via USB).
2. **ADB Debugging Enabled:**
   * On your Fire TV: Go to **Settings** ➔ **My Fire TV** (or **Device**) ➔ **Developer Options**.
   * Turn **ADB Debugging** and **Apps from Unknown Sources** to **ON**.
   *(If Developer Options is hidden, go to About ➔ click on your Fire TV name 7 times).*
3. **ADB installed** on your computer (`sudo apt install adb` on Debian/Ubuntu, or platform-tools on macOS/Windows).

---

## 🚀 Quick Start

### Option A: Interactive Python CLI (Recommended)

No external pip dependencies required (runs on pure Python 3.8+):

```bash
git clone https://github.com/your-username/firetv-optimizer.git
cd firetv-optimizer

# Run interactive menu:
python3 run.py

# Or run with your Fire TV's IP address:
python3 run.py --host 192.168.1.150
```

### Option B: One-Command Quick Boost CLI

Run the full recommended optimization pipeline in one command:

```bash
python3 run.py --host 192.168.1.150 quick-boost
```

### Option C: Standalone Bash Script

If you just want a single bash script without Python:

```bash
chmod +x scripts/quick_optimize.sh
./scripts/quick_optimize.sh 192.168.1.150
```

---

## 🖥️ CLI Commands Overview

| Command | Description |
|---|---|
| `python3 run.py audit` | Full diagnostic report (Fire OS version, RAM, Storage, Launcher & Tweaks status) |
| `python3 run.py quick-boost` | Complete all-in-one optimization sequence |
| `python3 run.py strip-updates` | Revert bloated Amazon updates in `/data/app` to factory stubs to free disk space |
| `python3 run.py restrict-bloat` | Enforce AppOps dormancy policies across all 60+ Amazon telemetry packages |
| `python3 run.py tweaks` | Lock animation speeds to 0, kill ad-tracking, mute banner video, set 3-process limit |
| `python3 run.py uninstall-redundant` | Safely remove redundant apps (Official YouTube, DefSquid, ES File Explorer) |

---

## 📺 Recommended Streaming Configurations

For older hardware like the **Fire TV Stick 2nd Gen (MediaTek MT8127D)**:

### SmartTube
* Go to **SmartTube Settings ⚙️** ➔ **Video Player** ➔ **Video Formats**.
* Select **AVC / H.264** as preferred codec.
* Limit max resolution to **1080p (30fps)** or **720p (60fps)**.
* *Why:* The hardware decoder handles AVC 1080p30 flawlessly, while VP9 60fps causes frame drops and audio sync drift.

### Stremio
* Enable **Hardware-accelerated decoding** in settings.
* Select 1080p streams under 3–5 GB (avoid heavy 4K REMUX or 10-bit AV1 files).

---

## 🔒 Protected Core Apps

This toolkit includes built-in safeguards to ensure essential streaming apps are **never** accidentally uninstalled or corrupted:
* Netflix (`com.netflix.ninja`)
* Stremio (`com.stremio.one`)
* SmartTube (`org.smarttube.stable`)
* Leanback Launcher (`com.amazon.tv.leanbacklauncher`)
* Launcher Manager (`com.wolf.fos5.settings`)

---

## 📄 License

MIT License. See [LICENSE](LICENSE) for details.
