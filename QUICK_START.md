# Quick Start Guide

## Fastest Method: Manual URL Extraction

### Step 1: Capture URLs from Browser

1. Open Instagram account: https://www.instagram.com/grapeot/
2. Press `F12` (or `Cmd+Option+I` on Mac) to open Developer Tools
3. Click the **Network** tab
4. Filter by "Img" or search for "jpg"
5. Scroll through the entire profile to load all images
6. Right-click in Network tab → "Copy all as HAR" or save network data
7. Paste/save to a file (e.g., `network_data.txt`)

### Step 2: Extract URLs

```bash
python3 extract_instagram_urls.py network_data.txt -o urls.txt
```

### Step 3: Download Images

```bash
python3 download_instagram_images.py urls.txt -o images
```

## Using Your Existing Data

You already have `jpeg.txt` with network data. Run:

```bash
# Extract URLs (already done - 30 URLs found!)
python3 extract_instagram_urls.py jpeg.txt -o instagram_urls.txt

# Download the images
python3 download_instagram_images.py instagram_urls.txt -o instagram_images
```

## What You Have

- ✅ `extract_instagram_urls.py` - Extracts URLs from network data
- ✅ `download_instagram_images.py` - Downloads images from URLs
- ✅ `instagram_scraper_automated.py` - Automated browser scraper (optional)
- ✅ `instagram_urls.txt` - 30 extracted URLs ready to download

## Next Steps

1. **Download the images**:
   ```bash
   python3 download_instagram_images.py instagram_urls.txt -o instagram_images
   ```

2. **For more images**: Scroll through more of the Instagram profile and capture more network data, then re-run extraction.

3. **Check the full README**: See `INSTAGRAM_SCRAPER_README.md` for detailed documentation.
