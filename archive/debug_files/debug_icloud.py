"""Command-line utility for checking iCloud photo access.

This script allows manual login to iCloud using PyiCloudService, including the
optional two-factor authentication step. It lists photos taken on the same day
for a number of previous years and can optionally download them.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timedelta
from getpass import getpass
from pathlib import Path
import os
from typing import Optional

try:
    from pyicloud import PyiCloudService  # type: ignore
except ImportError:  # pragma: no cover - pyicloud may not be installed
    PyiCloudService = None

try:
    from PIL import Image  # type: ignore
except ImportError:  # pragma: no cover
    Image = None

try:
    import cv2  # type: ignore
    import numpy as np  # type: ignore
    _FACE_CASCADE = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )
except Exception:  # pragma: no cover - optional dependency
    cv2 = None
    np = None
    _FACE_CASCADE = None


def _entropy(img: "Image.Image") -> float:
    hist = img.histogram()
    pixels = sum(hist)
    if pixels == 0:
        return 0.0
    from math import log2

    return -sum((h / pixels) * log2(h / pixels) for h in hist if h)


def _is_interesting(path: Path) -> bool:
    """Heuristic filter to skip non-photo images."""
    if Image is None:
        return True

    try:
        with Image.open(path) as img:
            w, h = img.size
            if w < 800 or h < 600:
                return False

            if cv2 is not None and np is not None and _FACE_CASCADE is not None:
                arr = cv2.cvtColor(np.array(img.convert("RGB")), cv2.COLOR_RGB2BGR)
                gray = cv2.cvtColor(arr, cv2.COLOR_BGR2GRAY)
                faces = _FACE_CASCADE.detectMultiScale(gray, 1.1, 5)
                if len(faces) > 0:
                    return True

            entropy = _entropy(img.convert("L"))
            return entropy >= 5.0
    except Exception:
        return False


def _login(username: str, password: str) -> "PyiCloudService":
    if PyiCloudService is None:
        raise RuntimeError("pyicloud-ipd is not installed")

    api = PyiCloudService(username, password)
    if api.requires_2sa:
        devices = api.trusted_devices
        if not devices:
            # Some accounts do not return devices. Allow a manually generated
            # verification code instead of failing immediately.
            code = os.environ.get("ICLOUD_2FA_CODE") or input("Enter 2FA code: ")
            if not code:
                raise RuntimeError(
                    "Two-factor code required but no trusted devices found. "
                    "Generate a code on a trusted device and set ICLOUD_2FA_CODE."
                )
            if not api.validate_verification_code(None, code):
                raise RuntimeError("Failed to verify 2FA code")
            try:
                api.trust_session()
            except Exception:
                pass
            return api

        index_env = os.environ.get("ICLOUD_2FA_DEVICE")
        if index_env is None and len(devices) > 1:
            print("Trusted devices:")
            for i, d in enumerate(devices):
                name = d.get("deviceName") or d.get("name") or str(d)
                print(f"  [{i}] {name}")
            index_env = input("Select device index: ") or "0"

        index = int(index_env or 0)
        if index < 0 or index >= len(devices):
            raise RuntimeError("Invalid 2FA device index")

        device = devices[index]
        if not api.send_verification_code(device):
            raise RuntimeError("Failed to send verification code")
        code = os.environ.get("ICLOUD_2FA_CODE") or input("Enter 2FA code: ")
        if not api.validate_verification_code(device, code):
            raise RuntimeError("Failed to verify 2FA code")
        try:
            api.trust_session()
        except Exception:
            pass
    return api


def _search(api: "PyiCloudService", when: datetime) -> list:
    start = when
    end = when + timedelta(days=1)
    return list(api.photos.search(start_date=start, end_date=end))


def _download(asset, dest: Path) -> None:
    file_name = f"{asset.id}.{asset.filename.split('.')[-1]}"
    path = dest / file_name
    asset.download().save(path)
    if not _is_interesting(path):
        path.unlink(missing_ok=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Manually fetch iCloud photos")
    parser.add_argument("--target-date", default=datetime.now().strftime("%Y-%m-%d"))
    parser.add_argument("--years-back", type=int, default=5)
    parser.add_argument("--output-dir", default="./debug_images")
    parser.add_argument("--download", action="store_true", help="Download images")
    args = parser.parse_args()

    username = os.environ.get("ICLOUD_USERNAME") or input("iCloud username: ")
    password = os.environ.get("ICLOUD_PASSWORD") or getpass("App-specific password: ")

    api = _login(username, password)
    date = datetime.strptime(args.target_date, "%Y-%m-%d")

    if args.download:
        out = Path(args.output_dir)
        out.mkdir(parents=True, exist_ok=True)

    for offset in range(1, args.years_back + 1):
        past = date.replace(year=date.year - offset)
        print(f"Searching {past.date()}...", end="")
        photos = _search(api, past)
        print(f" found {len(photos)} photos")
        if args.download:
            for p in photos:
                _download(p, out)

    if args.download:
        print(f"Saved images to {args.output_dir}")


if __name__ == "__main__":
    main()
