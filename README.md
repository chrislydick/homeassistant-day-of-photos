# homeassistant-day-of-photos

This repository contains utilities for fetching "on this day" photos from
cloud providers and copying them into Home Assistant's `media_source`. The
original scripts used Google Photos, but `icloud_dag.py` demonstrates how to
retrieve images from iCloud using Apache Airflow.

## Requirements

Install dependencies in a Python environment:

```bash
pip install -r requirements.txt
```

The Airflow DAG expects the `pyicloud-ipd` and `pillow` packages. Airflow itself
should already be installed on the machine executing the DAG.

## iCloud setup

1. Enable two-factor authentication on your Apple account.
2. Visit [appleid.apple.com](https://appleid.apple.com/) and create an
   **app-specific password**. This password is used by the script to access
your iCloud photos.
3. On the machine running the DAG, set environment variables or Airflow
   connection secrets with your Apple ID username and the app-specific
   password.
4. The first execution may prompt for the two-factor code. After the session is
   cached, subsequent runs will use the stored session cookies.

## Airflow usage

The file `icloud_dag.py` defines a simple DAG named `icloud_day_photos`. It
fetches photos from the same day over the last several years and stores them in
an output directory. The DAG uses the `fetch_photos` function, which accepts:

- `target_date`: date string (YYYY-MM-DD) for the day of interest.
- `years_back`: how many years in the past to search.
- `output_dir`: path where downloaded images are stored.
- `username` and `password`: iCloud credentials.

Example Airflow configuration:

```python
from icloud_dag import create_dag

dag = create_dag(
    name="icloud_day_photos",
    schedule="0 5 * * *",
    years_back=5,
    output_dir="/srv/homeassistant/media/day_photos",
    username="{{ var.value.ICLOUD_USERNAME }}",
    password="{{ var.value.ICLOUD_PASSWORD }}",
)
```

Place the file in your Airflow `dags/` folder. Airflow will run the task each
morning and populate the output directory with photos.

## Home Assistant configuration

Ensure the `media_source` integration is enabled. Copy or mount the output
folder from the Airflow machine to your Home Assistant instance. In `configuration.yaml`:

```yaml
homeassistant:
  allowlist_external_dirs:
    - /media/day_photos
```

Restart Home Assistant after updating the configuration. In WallPanel, set the
background or image source to the media path containing the downloaded photos.

## Filtering photos

`icloud_dag.py` contains a placeholder `_is_interesting` function. It currently
keeps images with a resolution greater than `800x600`. Replace this function
with your preferred ML model or scoring logic to select only photos suitable for
display.
