# Instagram Image Downloader

A comprehensive solution for downloading all images from a public Instagram account. This project demonstrates how to work around Instagram's restrictions using browser developer tools and automation.

## Overview

Instagram imposes strict limitations on automated data extraction. This project provides multiple approaches:

1. **Manual Method**: Use browser developer tools to capture image URLs, then download them
2. **Semi-Automated Method**: Extract URLs from network tab exports
3. **Fully Automated Method**: Use Selenium to automate browser interaction

## Prerequisites

- Python 3.7 or higher
- Chrome browser (for automated method)
- ChromeDriver (for automated method)

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. For automated scraping, install ChromeDriver:
```bash
# macOS
brew install chromedriver

# Or use webdriver-manager (handles driver automatically)
pip install webdriver-manager
```

## Usage

### Method 1: Manual URL Extraction + Automated Download

This is the recommended approach as it's most reliable and respects Instagram's rate limits.

#### Step 1: Extract URLs from Browser Network Tab

1. Open the Instagram account in your browser (e.g., https://www.instagram.com/grapeot/)
2. Open Developer Tools (F12 or Cmd+Option+I on Mac)
3. Go to the **Network** tab
4. Filter by "Img" or search for "jpg", "jpeg", "png"
5. Scroll through the entire profile to load all images
6. Right-click in the Network tab → "Save all as HAR with content" or copy the network data
7. Save the data to a text file (e.g., `jpeg.txt`)

#### Step 2: Extract URLs from Network Data

```bash
python extract_instagram_urls.py jpeg.txt -o instagram_urls.txt
```

This script:
- Parses the network export file
- Filters out thumbnails and profile pictures
- Extracts only full-size post images
- Saves unique URLs to a text file

Options:
- `-o, --output`: Output file path (default: `instagram_urls.txt`)
- `--method`: Extraction method (`network`, `text`, or `auto`)

#### Step 3: Download Images

```bash
python download_instagram_images.py instagram_urls.txt -o instagram_images
```

This script:
- Downloads all images from the URLs file
- Saves them with proper filenames
- Handles rate limiting and retries
- Skips already downloaded images

Options:
- `-o, --output`: Output directory (default: `instagram_images`)
- `-d, --delay`: Delay between requests in seconds (default: 0.5)

### Method 2: Fully Automated (Selenium)

**Note**: This method is more complex and may be blocked by Instagram's anti-bot measures. Use with caution.

```bash
python instagram_scraper_automated.py grapeot -o instagram_images
```

Options:
- `username`: Instagram username (without @)
- `-o, --output`: Output directory (default: `instagram_images`)
- `--headless`: Run browser in headless mode

The automated script:
1. Opens Chrome browser
2. Navigates to the Instagram profile
3. Scrolls through the entire page to load all images
4. Extracts image URLs from the DOM
5. Saves URLs to `instagram_urls.txt`
6. You can then download using `download_instagram_images.py`

## Example Workflow

```bash
# 1. Extract URLs from network tab data
python extract_instagram_urls.py jpeg.txt -o urls.txt

# 2. Download all images
python download_instagram_images.py urls.txt -o images

# Or combine both steps
python extract_instagram_urls.py jpeg.txt -o urls.txt && \
python download_instagram_images.py urls.txt -o images
```

## File Structure

```
.
├── extract_instagram_urls.py      # Extract URLs from network tab data
├── download_instagram_images.py   # Download images from URLs
├── instagram_scraper_automated.py # Automated browser-based scraper
├── jpeg.txt                       # Example network tab export (your data)
├── instagram_urls.txt            # Extracted URLs (generated)
└── instagram_images/              # Downloaded images (generated)
```

## How It Works

### URL Extraction

The `extract_instagram_urls.py` script:

1. **Parses network export data**: Reads tab-separated or text format files
2. **Filters Instagram URLs**: Identifies URLs from Instagram CDN (`instagram.com`, `fbcdn.net`)
3. **Removes thumbnails**: Filters out small images (profile pics, thumbnails) by:
   - Checking URL patterns (`_s150x150`, `_s100x100`)
   - Identifying profile picture patterns (`/t51.2885-19/`)
   - Keeping only full-size post images

### Image Download

The `download_instagram_images.py` script:

1. **Creates HTTP session**: Uses proper headers to mimic browser requests
2. **Rate limiting**: Adds delays between requests to avoid being blocked
3. **Retry logic**: Automatically retries failed downloads
4. **Smart naming**: Extracts image IDs from URLs for meaningful filenames
5. **Skip existing**: Doesn't re-download already saved images

### Automated Scraper

The `instagram_scraper_automated.py` script:

1. **Browser automation**: Uses Selenium to control Chrome
2. **Infinite scroll**: Automatically scrolls through the profile
3. **DOM extraction**: Finds image elements and extracts URLs
4. **Network monitoring**: Attempts to capture URLs from network logs

## Troubleshooting

### No URLs Found

- Make sure the account is **public**
- Verify you scrolled through the entire profile
- Check that the network tab captured image requests
- Try the `--method text` option for more flexible extraction

### Download Failures

- Increase delay between requests: `-d 1.0`
- Check your internet connection
- Some URLs may expire; re-extract if needed
- Instagram may rate-limit; wait and retry

### Automated Scraper Issues

- Ensure ChromeDriver is installed and in PATH
- Try running without `--headless` to see what's happening
- Instagram may detect automation; use manual method instead
- Check that the account is public and accessible

## Ethical Considerations

- **Only scrape public accounts**: Don't attempt to access private content
- **Respect rate limits**: Use delays between requests
- **Follow Instagram's Terms of Service**: This is for educational purposes
- **Don't redistribute content**: Respect copyright and creator rights
- **Use responsibly**: Don't overload Instagram's servers

## Limitations

- Instagram actively blocks automated scraping
- URLs may expire after some time
- Rate limiting may slow down downloads
- Some images may be in stories or reels (not included)
- Private accounts cannot be accessed

## Alternative Approaches

If these methods don't work:

1. **Instagram API**: Apply for official API access (time-consuming)
2. **Third-party tools**: Use tools like `instaloader` (may violate ToS)
3. **Manual download**: Right-click and save images manually

## License

This project is for educational purposes. Use responsibly and in accordance with Instagram's Terms of Service.

## Credits

This project demonstrates:
- GUI to API transitions (Module 1)
- Understanding web technologies and developer tools
- AI-assisted programming and prompt management
- Creative problem-solving with platform restrictions
