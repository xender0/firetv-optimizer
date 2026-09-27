"""ADB Client wrapper for Fire TV communication."""

import subprocess
import time
from typing import List, Tuple, Optional


class AdbClient:
    def __init__(self, target_host: Optional[str] = None, port: int = 5555):
        self.target_host = target_host
        self.port = port
        self.device_serial = f"{target_host}:{port}" if target_host else None

    def connect(self) -> bool:
        """Connect to device over Wi-Fi if target_host is provided."""
        if not self.target_host:
            # Check if any device is connected
            devices = self.get_connected_devices()
            if devices:
                self.device_serial = devices[0]
                return True
            return False

        subprocess.run(["adb", "disconnect", self.device_serial], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(1)
        res = subprocess.run(["adb", "connect", self.device_serial], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if "connected to" in res.stdout.lower():
            time.sleep(1)
            return True
        return False

    def get_connected_devices(self) -> List[str]:
        """List currently connected active ADB devices."""
        res = subprocess.run(["adb", "devices"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        devices = []
        for line in res.stdout.splitlines()[1:]:
            parts = line.strip().split()
            if len(parts) >= 2 and parts[1] == "device":
                devices.append(parts[0])
        return devices

    def shell(self, cmd: str, timeout: int = 20) -> Tuple[int, str]:
        """Execute command in adb shell."""
        adb_cmd = ["adb"]
        if self.device_serial:
            adb_cmd.extend(["-s", self.device_serial])
        adb_cmd.extend(["shell", cmd])

        try:
            res = subprocess.run(adb_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=timeout)
            out = (res.stdout + res.stderr).strip()
            return res.returncode, out
        except subprocess.TimeoutExpired:
            return -1, "Command timed out"
        except Exception as e:
            return -1, str(e)

    def run_cmd(self, adb_subcommand: List[str], timeout: int = 60) -> Tuple[int, str]:
        """Execute raw adb subcommand (e.g. install, pull, push)."""
        cmd = ["adb"]
        if self.device_serial:
            cmd.extend(["-s", self.device_serial])
        cmd.extend(adb_subcommand)

        try:
            res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=timeout)
            out = (res.stdout + res.stderr).strip()
            return res.returncode, out
        except subprocess.TimeoutExpired:
            return -1, "Command timed out"
        except Exception as e:
            return -1, str(e)

    def get_prop(self, prop_name: str) -> str:
        """Get Android system property."""
        code, out = self.shell(f"getprop {prop_name}")
        return out if code == 0 else ""

    def get_device_info(self) -> dict:
        """Retrieve core device specs."""
        return {
            "model": self.get_prop("ro.product.model"),
            "fireos_version": self.get_prop("ro.build.version.fireos"),
            "android_version": self.get_prop("ro.build.version.release"),
            "build_id": self.get_prop("ro.build.display.id"),
            "device": self.device_serial or "default"
        }
