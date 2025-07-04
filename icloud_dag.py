from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional
import os

from airflow import DAG
from airflow.operators.python import PythonOperator

try:
    from pyicloud import PyiCloudService  # type: ignore
except ImportError:
    PyiCloudService = None  # placeholder for type checking

try:
    from PIL import Image
except ImportError:
    Image = None  # placeholder

try:
    import cv2  # type: ignore
    import numpy as np  # type: ignore
    _FACE_CASCADE = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )
except Exception:  # pragma: no cover - optional dependency
    cv2 = None  # type: ignore
    np = None  # type: ignore
    _FACE_CASCADE = None


def _entropy(img: "Image.Image") -> float:
    """Return the Shannon entropy of a Pillow image."""
    hist = img.histogram()
    pixels = sum(hist)
    if pixels == 0:
        return 0.0
    from math import log2

    return -sum((h / pixels) * log2(h / pixels) for h in hist if h)


def _is_interesting(image_path: Path) -> bool:
    """Heuristic to skip screenshots or low-quality photos."""
    if Image is None:
        return True

    try:
        with Image.open(image_path) as img:
            width, height = img.size
            if width < 800 or height < 600:
                return False

            img_rgb = img.convert("RGB")

            if cv2 is not None and np is not None and _FACE_CASCADE is not None:
                arr = cv2.cvtColor(np.array(img_rgb), cv2.COLOR_RGB2BGR)
                gray = cv2.cvtColor(arr, cv2.COLOR_BGR2GRAY)
                faces = _FACE_CASCADE.detectMultiScale(gray, 1.1, 5)
                if len(faces) > 0:
                    return True

            entropy = _entropy(img_rgb.convert("L"))
            return entropy >= 5.0
    except Exception:
        return False


def _login(username: str | None, password: str | None) -> "PyiCloudService":
    """Return an authenticated PyiCloudService instance, handling 2FA."""
    api = PyiCloudService(username, password)

    if api.requires_2sa:
        code = os.environ.get("ICLOUD_2FA_CODE")
        device_index = int(os.environ.get("ICLOUD_2FA_DEVICE", "0"))
        if not code:
            raise RuntimeError(
                "Two-factor code required. Set ICLOUD_2FA_CODE environment variable"
            )

        devices = api.trusted_devices
        if not devices:
            # Some accounts do not return devices. Allow manual verification
            # instead of failing immediately.
            if not api.validate_verification_code(None, code):
                raise RuntimeError(
                    "Two-factor code required but no trusted devices found. "
                    "Generate a code on a trusted device and set ICLOUD_2FA_CODE."
                )
            try:
                api.trust_session()
            except Exception:
                pass
            return api

        if device_index < 0 or device_index >= len(devices):
            raise RuntimeError("Invalid 2FA device index")


        device = devices[device_index]
        if not api.send_verification_code(device):
            raise RuntimeError("Failed to send verification code")
        if not api.validate_verification_code(device, code):
            raise RuntimeError("Failed to verify the provided 2FA code")
        try:
            api.trust_session()
        except Exception:
            pass

    return api


def fetch_photos(
    target_date: Optional[str] = None,
    years_back: int = 5,
    output_dir: str = "./images",
    username: Optional[str] = None,
    password: Optional[str] = None,
) -> None:
    """Fetch photos from iCloud and keep the interesting ones."""

    if PyiCloudService is None:
        raise RuntimeError(
            "pyicloud is not installed. Install it with `pip install pyicloud-ipd`."
        )

    api = _login(username, password)

    date = datetime.strptime(target_date, "%Y-%m-%d") if target_date else datetime.now()

    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    for year_offset in range(1, years_back + 1):
        past = date.replace(year=date.year - year_offset)
        start = past
        end = past + timedelta(days=1)

        photos = api.photos.search(start_date=start, end_date=end)
        for photo in photos:
            asset = photo.download()
            file_name = f"{photo.id}.{photo.filename.split('.')[-1]}"
            dest = out / file_name
            asset.save(dest)
            if not _is_interesting(dest):
                dest.unlink(missing_ok=True)


def create_dag(
    name: str,
    schedule: str = "0 5 * * *",
    years_back: int = 5,
    output_dir: str = "./images",
    username: Optional[str] = None,
    password: Optional[str] = None,
) -> DAG:
    """Create a DAG that fetches day-of photos from iCloud."""
    default_args = {"owner": "airflow", "retries": 1}
    dag = DAG(name, schedule_interval=schedule, start_date=datetime(2024, 1, 1), default_args=default_args)

    PythonOperator(
        task_id="fetch_icloud_photos",
        dag=dag,
        python_callable=fetch_photos,
        op_kwargs={
            "target_date": "{{ ds }}",
            "years_back": years_back,
            "output_dir": output_dir,
            "username": username,
            "password": password,
        },
    )

    return dag


dag = create_dag("icloud_day_photos")

