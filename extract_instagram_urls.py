#!/usr/bin/env python3
"""
Extract Instagram image URLs from network tab export data.
Filters out thumbnails and profile pictures to get only full-size post images.
"""

import re
from pathlib import Path
from urllib.parse import urlparse, parse_qs


def extract_urls_from_network_export(file_path):
    """
    Extract image URLs from network tab export (tab-separated format).

    Args:
        file_path: Path to the network export file (e.g., jpeg.txt)

    Returns:
        List of unique image URLs
    """
    urls = set()

    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            # Split by tab (network export format)
            parts = line.split('\t')
            if len(parts) < 2:
                continue

            url = parts[1].strip()
            if not url.startswith('http'):
                continue

            # Filter for Instagram CDN image URLs
            if 'instagram' in url or 'fbcdn.net' in url or 'cdninstagram.com' in url:
                # Skip profile pictures and thumbnails
                if is_full_size_image(url):
                    urls.add(url)

    return sorted(list(urls))


def is_full_size_image(url):
    """
    Determine if URL is a full-size image (not thumbnail or profile pic).

    Args:
        url: Image URL to check

    Returns:
        True if appears to be full-size post image
    """
    # Skip profile pictures (usually have specific patterns)
    if '/t51.2885-19/' in url:  # Profile picture pattern
        return False

    # Skip small thumbnails (check for size indicators in URL)
    if '_s150x150' in url or '_s100x100' in url or 's150x150' in url or 's100x100' in url:
        return False

    # Look for full-size indicators
    # Instagram full-size images often have patterns like:
    # - _p720x720, _p1080x1080, etc. (portrait)
    # - _s720x720, _s1080x1080, etc. (square)
    # - _e35 (encoding indicator)
    # - /t51.82787-15/, /t51.75761-15/, /t51.71878-15/ (post image patterns)

    # Check for post image patterns
    if any(pattern in url for pattern in ['/t51.82787-15/', '/t51.75761-15/', '/t51.71878-15/']):
        return True

    # Check for size indicators that suggest full-size
    if re.search(r'[ps]\d{3,4}x\d{3,4}', url):
        # Check if it's a reasonable size (not tiny)
        size_match = re.search(r'[ps](\d{3,4})x\d{3,4}', url)
        if size_match:
            size = int(size_match.group(1))
            if size >= 640:  # At least 640px width/height
                return True

    # If it's from Instagram CDN and doesn't match thumbnail patterns, include it
    if 'instagram' in url or 'fbcdn.net' in url:
        # Exclude obvious thumbnails
        if not any(pattern in url for pattern in ['_s150', '_s100', 's150x150', 's100x100']):
            return True

    return False


def extract_urls_from_text(file_path):
    """
    Alternative: Extract URLs from any text file (more flexible).
    Uses regex to find all Instagram image URLs.

    Args:
        file_path: Path to text file containing URLs

    Returns:
        List of unique image URLs
    """
    urls = set()

    # Pattern to match Instagram image URLs
    url_pattern = re.compile(
        r'https?://(?:[^/\s]+\.)?(?:instagram\.(?:com|fbcdn\.net)|fbcdn\.net|cdninstagram\.com)[^\s<>"\'\)]+'
    )

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        matches = url_pattern.findall(content)

        for url in matches:
            # Clean URL (remove trailing punctuation that might not be part of URL)
            url = url.rstrip('.,;:!?)')
            if is_full_size_image(url):
                urls.add(url)

    return sorted(list(urls))


def save_urls_to_file(urls, output_file):
    """
    Save URLs to a text file (one per line).

    Args:
        urls: List of URLs
        output_file: Path to output file
    """
    with open(output_file, 'w', encoding='utf-8') as f:
        for url in urls:
            f.write(url + '\n')

    print(f"Saved {len(urls)} URLs to {output_file}")


def main():
    """Main function."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Extract Instagram image URLs from network export or text file'
    )
    parser.add_argument(
        'input_file',
        type=str,
        help='Path to input file (network export or text file with URLs)'
    )
    parser.add_argument(
        '-o', '--output',
        type=str,
        default='instagram_urls.txt',
        help='Output file path (default: instagram_urls.txt)'
    )
    parser.add_argument(
        '--method',
        type=str,
        choices=['network', 'text', 'auto'],
        default='auto',
        help='Extraction method: network (tab-separated), text (regex), or auto (default: auto)'
    )

    args = parser.parse_args()

    input_path = Path(args.input_file)
    if not input_path.exists():
        print(f"Error: {args.input_file} not found!")
        return

    print(f"Extracting URLs from {args.input_file}...")

    # Try network format first, then fall back to text extraction
    if args.method == 'network':
        urls = extract_urls_from_network_export(input_path)
    elif args.method == 'text':
        urls = extract_urls_from_text(input_path)
    else:  # auto
        try:
            urls = extract_urls_from_network_export(input_path)
            if len(urls) < 5:  # If we got very few URLs, try text method
                print("Few URLs found with network method, trying text extraction...")
                urls = extract_urls_from_text(input_path)
        except Exception as e:
            print(f"Network extraction failed: {e}, trying text extraction...")
            urls = extract_urls_from_text(input_path)

    print(f"Found {len(urls)} unique full-size image URLs")

    if urls:
        save_urls_to_file(urls, args.output)
        print(f"\nSample URLs (first 5):")
        for url in urls[:5]:
            print(f"  {url}")
    else:
        print("No URLs found. Make sure the input file contains Instagram image URLs.")


if __name__ == '__main__':
    main()
