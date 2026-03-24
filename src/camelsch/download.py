"""Download and extract the CAMELS-CH dataset."""

from __future__ import annotations

import logging
import shutil
import zipfile
from pathlib import Path
from urllib.request import urlopen

from rich.progress import (
    BarColumn,
    DownloadColumn,
    Progress,
    TextColumn,
    TransferSpeedColumn,
)

logger = logging.getLogger(__name__)

CAMELS_CH_URL = "https://zenodo.org/api/records/15025258/files/camels_ch.zip/content"
ZIP_FILENAME = "camels_ch.zip"
EXTRACTED_DIR = "CAMELS_CH"


def download_camels_ch(
    dest: Path | str = Path("./data/CAMELS_CH"),
    url: str = CAMELS_CH_URL,
    force: bool = False,
) -> Path:
    """Download and extract CAMELS-CH. Returns path to extracted dir.

    Args:
        dest: Target directory for the extracted dataset.
        url: URL to download from.
        force: Re-download even if already exists.

    Returns:
        Path to the extracted dataset directory.
    """
    dest = Path(dest)

    if dest.exists() and not force:
        logger.debug("Dataset already exists at %s, skipping download", dest)
        return dest

    dest.parent.mkdir(parents=True, exist_ok=True)
    zip_path = dest.parent / ZIP_FILENAME

    # Download with rich progress bar
    if not zip_path.exists() or force:
        logger.debug("Downloading CAMELS-CH from %s", url)
        _download_with_progress(url, zip_path)

    # Extract
    _extract_and_rename(zip_path, dest)

    # Clean up zip
    zip_path.unlink(missing_ok=True)

    return dest


def _validate_zip_members(zf: zipfile.ZipFile, target: Path) -> None:
    """Raise ValueError if any zip member would extract outside *target*."""
    resolved = target.resolve()
    for member in zf.namelist():
        member_path = (target / member).resolve()
        if not str(member_path).startswith(str(resolved) + "/") and member_path != resolved:
            msg = f"Zip member {member!r} would escape target directory"
            raise ValueError(msg)


def _download_with_progress(url: str, zip_path: Path) -> None:
    """Download a file with a rich progress bar."""
    response = urlopen(url, timeout=30)
    total = int(response.headers.get("Content-Length", 0))

    with Progress(
        TextColumn("[bold blue]{task.description}"),
        BarColumn(),
        DownloadColumn(),
        TransferSpeedColumn(),
    ) as progress:
        task = progress.add_task("Downloading CAMELS-CH", total=total or None)
        with open(zip_path, "wb") as f:
            while chunk := response.read(8192):
                f.write(chunk)
                progress.update(task, advance=len(chunk))


def _extract_and_rename(zip_path: Path, dest: Path) -> None:
    """Extract zip and rename extracted folder to dest."""
    extract_to = dest.parent
    with zipfile.ZipFile(zip_path, "r") as zf:
        _validate_zip_members(zf, extract_to)
        zf.extractall(extract_to)

    # Auto-detect extracted folder (starts with "camels" or "CAMELS")
    for item in extract_to.iterdir():
        if item.is_dir() and item.name.lower().startswith("camels"):
            if item.resolve() == dest.resolve():
                # Already in the right place (e.g. case-insensitive FS)
                return
            if dest.exists():
                shutil.rmtree(dest)
            shutil.move(str(item), str(dest))
            return

    # If extraction produced files directly (no subfolder), dest should already exist
    if not dest.exists():
        msg = f"Could not find extracted CAMELS-CH folder in {extract_to}"
        raise FileNotFoundError(msg)
