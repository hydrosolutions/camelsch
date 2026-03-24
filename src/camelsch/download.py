"""Download and extract the CAMELS-CH dataset."""

from __future__ import annotations

import logging
import shutil
import tempfile
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
        try:
            member_path.relative_to(resolved)
        except ValueError:
            msg = f"Zip member {member!r} would escape target directory"
            raise ValueError(msg) from None


def _download_with_progress(url: str, zip_path: Path) -> None:
    """Download a file with a rich progress bar."""
    part_path = zip_path.with_suffix(".zip.part")
    try:
        response = urlopen(url, timeout=30)
        total = int(response.headers.get("Content-Length", 0))

        with Progress(
            TextColumn("[bold blue]{task.description}"),
            BarColumn(),
            DownloadColumn(),
            TransferSpeedColumn(),
        ) as progress:
            task = progress.add_task("Downloading CAMELS-CH", total=total or None)
            with open(part_path, "wb") as f:
                while chunk := response.read(8192):
                    f.write(chunk)
                    progress.update(task, advance=len(chunk))
        part_path.rename(zip_path)
    except BaseException:
        part_path.unlink(missing_ok=True)
        raise


def _extract_and_rename(zip_path: Path, dest: Path) -> None:
    """Extract zip to a temp directory and move the result to dest."""
    with tempfile.TemporaryDirectory(dir=dest.parent) as tmp:
        tmp_path = Path(tmp)
        with zipfile.ZipFile(zip_path, "r") as zf:
            _validate_zip_members(zf, tmp_path)
            zf.extractall(tmp_path)

        # Auto-detect extracted folder (starts with "camels" or "CAMELS")
        extracted = None
        for item in tmp_path.iterdir():
            if item.is_dir() and item.name.lower().startswith("camels"):
                extracted = item
                break

        if extracted is None:
            if not any(tmp_path.iterdir()):
                msg = "Could not find extracted CAMELS-CH folder in zip"
                raise FileNotFoundError(msg)
            # Files extracted flat into tmp — use the whole tmp dir
            extracted = tmp_path

        if dest.exists():
            shutil.rmtree(dest)
        shutil.move(str(extracted), str(dest))
