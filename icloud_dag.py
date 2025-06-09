from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

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


def _is_interesting(image_path: Path) -> bool:
    """Simple heuristic to keep only reasonably large photos.

    Replace this function with a real model or scoring approach if available.
    """
    if Image is None:
        return True

    try:
        with Image.open(image_path) as img:
            width, height = img.size
        return width * height >= 800 * 600
    except Exception:
        return False


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

    api = PyiCloudService(username, password)

    if api.requires_2sa:
        raise RuntimeError(
            "Two-factor authentication is required. Set up a valid session before running.")

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
