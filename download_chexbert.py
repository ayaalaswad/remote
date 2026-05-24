"""
Download CheXbert checkpoint from alternative sources.

The official Stanford Box link is often unavailable. This script tries multiple mirrors.
"""

import os
import sys
import requests
from pathlib import Path
from tqdm import tqdm

def download_file(url, output_path, description="Downloading"):
    """Download file with progress bar."""
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))

    with open(output_path, 'wb') as f, tqdm(
        desc=description,
        total=total_size,
        unit='B',
        unit_scale=True,
        unit_divisor=1024,
    ) as pbar:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
                pbar.update(len(chunk))

    return True

def main():
    # Output directory
    output_dir = Path("C:/Users/aya.alaswad/remote/checkpoints/stanford/chexbert")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "chexbert.pth"

    if output_file.exists():
        file_size = output_file.stat().st_size
        file_size_mb = file_size / (1024**2)

        # CheXbert should be ~438 MB. If file is too small, it's corrupted.
        if file_size_mb >= 400:
            print(f"✓ CheXbert checkpoint already exists: {output_file}")
            print(f"  Size: {file_size_mb:.1f} MB")
            return
        else:
            print(f"⚠ Existing file is corrupted (only {file_size_mb:.1f} MB, expected ~438 MB)")
            print(f"  Deleting and re-downloading...")
            output_file.unlink()

    # Try multiple sources
    # Note: Most public mirrors are down or require authentication
    # The working approach is to use the Google Drive link from the official repo
    sources = [
        {
            "name": "Direct download (Google Drive ID: 1DS6NYirOXQf8qYieSVMvqNwuOlgAbM_E)",
            "url": "https://drive.google.com/uc?export=download&id=1DS6NYirOXQf8qYieSVMvqNwuOlgAbM_E"
        }
    ]

    print("=" * 80)
    print("CheXbert Checkpoint Downloader")
    print("=" * 80)
    print(f"Output: {output_file}")
    print()

    for i, source in enumerate(sources, 1):
        print(f"\n[{i}/{len(sources)}] Trying {source['name']}...")
        print(f"URL: {source['url']}")

        try:
            # Check if URL is accessible
            response = requests.head(source['url'], allow_redirects=True, timeout=10)

            if response.status_code == 404:
                print(f"✗ 404 Not Found - skipping")
                continue
            elif response.status_code != 200:
                print(f"✗ HTTP {response.status_code} - skipping")
                continue

            # Download
            print(f"✓ Accessible! Downloading...")
            download_file(source['url'], output_file, f"CheXbert ({source['name']})")

            # Verify
            file_size = output_file.stat().st_size
            print(f"\n✓ Download complete!")
            print(f"  Size: {file_size / (1024**2):.1f} MB")

            # Basic validation - CheXbert should be ~430-450 MB
            if file_size < 400 * 1024 * 1024:
                print(f"⚠ Warning: File seems too small (expected ~438 MB)")
                output_file.unlink()
                continue

            print(f"\n{'='*80}")
            print(f"SUCCESS! CheXbert downloaded to:")
            print(f"  {output_file}")
            print(f"{'='*80}")
            return

        except requests.exceptions.Timeout:
            print(f"✗ Timeout - server not responding")
        except requests.exceptions.ConnectionError:
            print(f"✗ Connection error")
        except Exception as e:
            print(f"✗ Error: {e}")

    # All sources failed
    print("\n" + "="*80)
    print("ERROR: All download sources failed!")
    print("="*80)
    print("\nManual download instructions:")
    print("\nOption 1: Use gdown (recommended):")
    print("  pip install gdown")
    print("  gdown 1DS6NYirOXQf8qYieSVMvqNwuOlgAbM_E -O " + str(output_file))
    print("\nOption 2: Browser download:")
    print("  1. Open: https://drive.google.com/file/d/1DS6NYirOXQf8qYieSVMvqNwuOlgAbM_E/view")
    print("  2. Click 'Download' (top right)")
    print(f"  3. Move downloaded file to: {output_file}")
    print("\nOption 3: Check official repo:")
    print("  https://github.com/stanfordmlgroup/CheXbert")
    print("  (Look for latest download links in README)")
    sys.exit(1)

if __name__ == "__main__":
    main()
