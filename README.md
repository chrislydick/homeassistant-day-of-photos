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

The Airflow DAG expects the `pyicloud-ipd`, `pillow`, `opencv-python`, and
`numpy` packages. Airflow itself should already be installed on the machine
executing the DAG.

## iCloud setup

1. Enable two-factor authentication on your Apple account.
2. Visit [appleid.apple.com](https://appleid.apple.com/) and create an
   **app-specific password**. This password is used by the script to access
your iCloud photos.
3. On the machine running the DAG, set environment variables or Airflow
   connection secrets with your Apple ID username and the app-specific
   password.
4. The first run may require a two-factor verification code. When prompted,
   obtain the code from your trusted device and run the task with the
   environment variable `ICLOUD_2FA_CODE` set to that code. Optionally set
   `ICLOUD_2FA_DEVICE` to choose the trusted device index (default `0`). After a
   successful login, the session cookie is saved and future runs will not need
   the code until the cookie expires.

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

To run the DAG manually from the command line:

```bash
airflow dags list          # confirm Airflow sees "icloud_day_photos"
airflow dags trigger icloud_day_photos
```

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

`icloud_dag.py` implements a basic `_is_interesting` helper. Images smaller than
`800x600` are discarded. If `opencv-python` is installed, the function attempts
face detection using a bundled Haar cascade and automatically keeps photos with
faces. For all other images, the script computes their grayscale entropy and
retains those above a small threshold (≈5.0). You can replace this logic with a
custom ML model if desired.

## Troubleshooting iCloud access

Use the `debug_icloud.py` script to verify your credentials and two-factor
authentication setup outside of Airflow. Run it from the project directory:

```bash
python debug_icloud.py --download --years-back 2
```

The script prompts for your Apple ID username and app-specific password (unless
`ICLOUD_USERNAME` and `ICLOUD_PASSWORD` environment variables are set). If
two-factor authentication is required, enter the code when prompted. If you
have multiple trusted devices and do not provide `ICLOUD_2FA_DEVICE`, the script
will list the available devices and ask you to choose one. Images are
downloaded into `./debug_images` by default so you can confirm everything works
before scheduling the DAG.

If the tool reports that no trusted devices are available, generate a
verification code manually on your iPhone or Mac (Settings → your name →
Password & Security → **Get Verification Code**) and pass it via the
`ICLOUD_2FA_CODE` environment variable.
