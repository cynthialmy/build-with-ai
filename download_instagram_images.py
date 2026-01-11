#!/usr/bin/env python3
"""
Download images from Instagram URLs.
Handles rate limiting, retries, and proper file naming.
"""

import os
import re
import time
from pathlib import Path
from urllib.parse import urlparse, parse_qs
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


def create_session():
    """
    Create a requests session with retry strategy and proper headers.

    Returns:
        Configured requests.Session object
    """
    session = requests.Session()

    # Retry strategy
    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    # Set headers to mimic a browser
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Referer': 'https://www.instagram.com/',
        'Sec-Fetch-Dest': 'image',
        'Sec-Fetch-Mode': 'no-cors',
        'Sec-Fetch-Site': 'cross-site',
    })

    return session


def get_filename_from_url(url, index=None):
    """
    Generate a filename from URL.

    Args:
        url: Image URL
        index: Optional index number for filename

    Returns:
        Filename string
    """
    # Try to extract filename from URL
    parsed = urlparse(url)
    path = parsed.path

    # Extract the image ID from Instagram URLs
    # Pattern: /v/t51.XXXXX-15/IMAGEID_filename.jpg
    match = re.search(r'/(\d+_\d+_\d+_n\.(jpg|jpeg|png|webp))', path)
    if match:
        filename = match.group(1)
    else:
        # Fallback: use last part of path
        filename = os.path.basename(path)
        if not filename or '.' not in filename:
            # Generate filename from query params or hash
            filename = f"image_{hash(url) % 1000000}.jpg"

    # Add index prefix if provided
    if index is not None:
        filename = f"{index:04d}_{filename}"

    return filename


def download_image(session, url, output_dir, index=None, delay=0.5):
    """
    Download a single image.

    Args:
        session: requests.Session object
        url: Image URL
        output_dir: Directory to save image
        index: Optional index for filename
        delay: Delay between requests (seconds)

    Returns:
        Tuple (success: bool, filename: str or None, error: str or None)
    """
    try:
        filename = get_filename_from_url(url, index)
        filepath = Path(output_dir) / filename

        # Skip if already exists
        if filepath.exists():
            return True, filename, None

        # Download with timeout
        response = session.get(url, timeout=30, stream=True)
        response.raise_for_status()

        # Check content type
        content_type = response.headers.get('Content-Type', '')
        if 'image' not in content_type:
            return False, None, f"Not an image: {content_type}"

        # Save file
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        # Rate limiting
        time.sleep(delay)

        return True, filename, None

    except requests.exceptions.RequestException as e:
        return False, None, str(e)
    except Exception as e:
        return False, None, str(e)


def download_images_from_file(urls_file, output_dir='instagram_images', delay=0.5):
    """
    Download all images from a file containing URLs (one per line).

    Args:
        urls_file: Path to file with URLs (one per line)
        output_dir: Directory to save images
        delay: Delay between requests (seconds)
    """
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    # Read URLs
    urls = []
    with open(urls_file, 'r', encoding='utf-8') as f:
        for line in f:
            url = line.strip()
            if url and url.startswith('http'):
                urls.append(url)

    if not urls:
        print("No URLs found in file!")
        return

    print(f"Found {len(urls)} URLs to download")
    print(f"Saving to: {output_path.absolute()}")
    print(f"Delay between requests: {delay}s\n")

    # Create session
    session = create_session()

    # Download images
    successful = 0
    failed = 0

    for i, url in enumerate(urls, 1):
        print(f"[{i}/{len(urls)}] Downloading...", end=' ', flush=True)

        success, filename, error = download_image(session, url, output_path, index=i, delay=delay)

        if success:
            print(f"✓ Saved: {filename}")
            successful += 1
        else:
            print(f"✗ Failed: {error}")
            failed += 1

    print(f"\n{'='*60}")
    print(f"Download complete!")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    print(f"Total: {len(urls)}")


def main():
    """Main function."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Download Instagram images from URLs file'
    )
    parser.add_argument(
        'urls_file',
        type=str,
        help='Path to file containing URLs (one per line)'
    )
    parser.add_argument(
        '-o', '--output',
        type=str,
        default='instagram_images',
        help='Output directory (default: instagram_images)'
    )
    parser.add_argument(
        '-d', '--delay',
        type=float,
        default=0.5,
        help='Delay between requests in seconds (default: 0.5)'
    )

    args = parser.parse_args()

    urls_path = Path(args.urls_file)
    if not urls_path.exists():
        print(f"Error: {args.urls_file} not found!")
        return

    download_images_from_file(args.urls_file, args.output, args.delay)


if __name__ == '__main__':
    main()
