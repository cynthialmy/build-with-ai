#!/usr/bin/env python3
"""
Automated Instagram image scraper using Selenium.
Opens browser, scrolls through account, captures image URLs, and downloads them.

Note: This requires Selenium and a browser driver (Chrome/Firefox).
"""

import time
import json
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import requests


def setup_driver(headless=False):
    """
    Set up Chrome WebDriver.

    Args:
        headless: Run browser in headless mode

    Returns:
        WebDriver instance
    """
    chrome_options = Options()

    if headless:
        chrome_options.add_argument('--headless')

    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

    # Disable images to speed up loading (we'll get URLs from network)
    # chrome_options.add_argument('--blink-settings=imagesEnabled=false')

    try:
        driver = webdriver.Chrome(options=chrome_options)
        return driver
    except Exception as e:
        print(f"Error setting up Chrome driver: {e}")
        print("\nMake sure you have:")
        print("1. Chrome browser installed")
        print("2. ChromeDriver installed (brew install chromedriver on macOS)")
        print("3. Or use: pip install webdriver-manager")
        raise


def extract_image_urls_from_network_logs(driver):
    """
    Extract image URLs from browser network logs.

    Args:
        driver: WebDriver instance

    Returns:
        Set of image URLs
    """
    urls = set()

    try:
        # Get performance logs (requires Chrome with logging enabled)
        logs = driver.get_log('performance')

        for log in logs:
            message = json.loads(log['message'])
            if message['message']['method'] == 'Network.responseReceived':
                response = message['message']['params']['response']
                url = response.get('url', '')

                # Check if it's an image
                mime_type = response.get('mimeType', '')
                if 'image' in mime_type and ('instagram' in url or 'fbcdn.net' in url):
                    # Filter for full-size images
                    if not any(pattern in url for pattern in ['_s150x150', '_s100x100', '/t51.2885-19/']):
                        urls.add(url)
    except Exception as e:
        print(f"Note: Could not extract from network logs: {e}")
        print("Falling back to DOM extraction...")

    return urls


def extract_image_urls_from_dom(driver):
    """
    Extract image URLs from page DOM.

    Args:
        driver: WebDriver instance

    Returns:
        Set of image URLs
    """
    urls = set()

    try:
        # Find all img elements
        images = driver.find_elements(By.TAG_NAME, 'img')

        for img in images:
            src = img.get_attribute('src')
            srcset = img.get_attribute('srcset')

            # Check src attribute
            if src and ('instagram' in src or 'fbcdn.net' in src):
                if not any(pattern in src for pattern in ['_s150x150', '_s100x100', '/t51.2885-19/']):
                    urls.add(src)

            # Check srcset attribute
            if srcset:
                for src_url in srcset.split(','):
                    src_url = src_url.strip().split()[0]  # Get URL part
                    if 'instagram' in src_url or 'fbcdn.net' in src_url:
                        if not any(pattern in src_url for pattern in ['_s150x150', '_s100x100', '/t51.2885-19/']):
                            urls.add(src_url)
    except Exception as e:
        print(f"Error extracting from DOM: {e}")

    return urls


def scroll_and_load_all(driver, max_scrolls=50, scroll_delay=2):
    """
    Scroll through Instagram profile to load all images.

    Args:
        driver: WebDriver instance
        max_scrolls: Maximum number of scrolls
        scroll_delay: Delay between scrolls (seconds)

    Returns:
        Number of scrolls performed
    """
    print("Scrolling to load all images...")

    last_height = driver.execute_script("return document.body.scrollHeight")
    scrolls = 0

    while scrolls < max_scrolls:
        # Scroll down
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(scroll_delay)

        # Calculate new scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")

        if new_height == last_height:
            # No new content loaded, try scrolling a bit more
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight - 1000);")
            time.sleep(1)
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(scroll_delay)

            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                print("Reached end of page")
                break

        last_height = new_height
        scrolls += 1

        if scrolls % 5 == 0:
            print(f"  Scrolled {scrolls} times...")

    print(f"Finished scrolling ({scrolls} scrolls)")
    return scrolls


def scrape_instagram_account(username, output_dir='instagram_images', headless=False):
    """
    Scrape all images from an Instagram account.

    Args:
        username: Instagram username (without @)
        output_dir: Directory to save images
        headless: Run browser in headless mode
    """
    url = f"https://www.instagram.com/{username}/"

    print(f"Opening Instagram account: {url}")

    driver = None
    try:
        # Setup driver
        driver = setup_driver(headless=headless)
        driver.get(url)

        # Wait for page to load
        print("Waiting for page to load...")
        time.sleep(5)

        # Check if account exists
        if "Sorry, this page isn't available" in driver.page_source:
            print(f"Error: Account @{username} not found or is private!")
            return

        # Scroll to load all images
        scroll_and_load_all(driver, max_scrolls=50, scroll_delay=2)

        # Extract image URLs
        print("Extracting image URLs...")
        urls = extract_image_urls_from_dom(driver)

        # Also try network logs
        network_urls = extract_image_urls_from_network_logs(driver)
        urls.update(network_urls)

        print(f"Found {len(urls)} unique image URLs")

        if urls:
            # Save URLs to file
            urls_file = Path('instagram_urls.txt')
            with open(urls_file, 'w', encoding='utf-8') as f:
                for url in sorted(urls):
                    f.write(url + '\n')

            print(f"URLs saved to {urls_file}")
            print(f"\nNow run: python download_instagram_images.py {urls_file} -o {output_dir}")
        else:
            print("No image URLs found!")
            print("\nTroubleshooting:")
            print("1. Make sure the account is public")
            print("2. Try scrolling manually in the browser")
            print("3. Check browser console for errors")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

    finally:
        if driver:
            print("\nClosing browser...")
            driver.quit()


def main():
    """Main function."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Automated Instagram image scraper using Selenium'
    )
    parser.add_argument(
        'username',
        type=str,
        help='Instagram username (without @)'
    )
    parser.add_argument(
        '-o', '--output',
        type=str,
        default='instagram_images',
        help='Output directory for images (default: instagram_images)'
    )
    parser.add_argument(
        '--headless',
        action='store_true',
        help='Run browser in headless mode'
    )

    args = parser.parse_args()

    scrape_instagram_account(args.username, args.output, args.headless)


if __name__ == '__main__':
    main()
