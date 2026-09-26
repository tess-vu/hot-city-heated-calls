"""
Download bulk raster/archive inputs that are not stored in the repository.

These files are too large for Git (and were removed from Git LFS to stay within
the storage budget), so they are fetched on demand instead.

Usage:
    python scripts/fetch_data.py            # fetch anything missing
    python scripts/fetch_data.py --force    # re-download even if present
    python scripts/fetch_data.py --list     # show what is expected and where
"""

import argparse
import sys
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# Landsat 8 Collection 2 Level-2 surface reflectance scene, path 013 / row 032,
# acquired 2025-07-29. Used by the NLCD / land-surface-temperature notebooks.
#
# USGS EarthExplorer requires an account, so there is no stable direct link.
# Set LANDSAT_SR_URL to a download URL you control (S3, Drive, institutional
# share) to make this fully automatic; otherwise the script prints instructions.
DATASETS = [
    {
        "name": "Landsat 8 SR scene (2025-07-29)",
        "path": "notebooks/data/LC08_L2SP_013032_20250729_20250807_02_T1_SR.zip",
        "url": None,
        "approx_size": "163 MB",
        "manual_source": (
            "https://earthexplorer.usgs.gov/ - search Landsat 8-9 OLI/TIRS C2 L2, "
            "scene LC08_L2SP_013032_20250729_20250807_02_T1"
        ),
    },
]


def download(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(dest.suffix + ".part")

    def progress(block_num, block_size, total_size):
        if total_size <= 0:
            return
        pct = min(100, block_num * block_size * 100 // total_size)
        print(f"\r  {pct:3d}%", end="", flush=True)

    urllib.request.urlretrieve(url, tmp, reporthook=progress)
    print()
    tmp.replace(dest)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--force", action="store_true", help="re-download existing files")
    parser.add_argument("--list", action="store_true", help="list datasets and exit")
    args = parser.parse_args()

    if args.list:
        for item in DATASETS:
            print(f"{item['name']}  ({item['approx_size']})")
            print(f"  -> {item['path']}")
        return 0

    missing_manual = []

    for item in DATASETS:
        dest = REPO_ROOT / item["path"]

        if dest.exists() and not args.force:
            print(f"ok      {item['path']}")
            continue

        if not item["url"]:
            missing_manual.append(item)
            print(f"MANUAL  {item['path']}")
            continue

        print(f"fetch   {item['path']}  ({item['approx_size']})")
        try:
            download(item["url"], dest)
        except Exception as exc:
            print(f"  failed: {exc}", file=sys.stderr)
            return 1

    if missing_manual:
        print("\nThe following files need to be downloaded manually:\n")
        for item in missing_manual:
            print(f"  {item['name']} ({item['approx_size']})")
            print(f"    source: {item['manual_source']}")
            print(f"    save to: {item['path']}\n")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
