# Search Engine Redirect Bookmarklet

A bookmarklet that extracts your current search query from Google and opens the same search on DuckDuckGo in a new tab.

## What is a Bookmarklet?

A bookmarklet is a bookmark that contains JavaScript code instead of a traditional URL. When you click the bookmarklet, the JavaScript code executes in the context of the current page, allowing you to automate tasks or modify web pages directly from your browser.

## How It Works

1. **Query Extraction**: The bookmarklet parses the current page URL to extract the search query parameter (typically `q` for Google searches)
2. **URL Construction**: It constructs a new DuckDuckGo search URL with the extracted query
3. **New Tab Opening**: It opens the DuckDuckGo search results in a new tab, leaving your original search page intact

## Installation Instructions

### Step 1: Get the Bookmarklet Code

Open the `search_redirect_bookmarklet.js` file and copy the minified version. The minified code is:

```javascript
javascript:(function(){'use strict';function extractSearchQuery(){try{const urlParams=new URLSearchParams(window.location.search);let query=urlParams.get('q');if(!query){query=urlParams.get('query')||urlParams.get('search')||urlParams.get('text');}if(!query){const pathMatch=window.location.pathname.match(/\/search\/(.+)/);if(pathMatch){query=decodeURIComponent(pathMatch[1].replace(/\+/g,' '));}}return query;}catch(error){console.error('Error extracting search query:',error);return null;}}function buildDuckDuckGoUrl(query){if(!query){return null;}const encodedQuery=encodeURIComponent(query);return 'https://duckduckgo.com/?q='+encodedQuery;}function redirectToDuckDuckGo(){const query=extractSearchQuery();if(!query){alert('No search query found on this page. Please navigate to a search results page first.');return;}const duckDuckGoUrl=buildDuckDuckGoUrl(query);if(duckDuckGoUrl){window.open(duckDuckGoUrl,'_blank');}else{alert('Error: Could not construct DuckDuckGo URL.');}}redirectToDuckDuckGo();})();
```

**Important**: Copy the entire line above, including the `javascript:` prefix at the beginning.

### Step 2: Create the Bookmark

#### For Chrome/Edge/Brave:

1. Click the three-dot menu (⋮) in the top-right corner
2. Select **Bookmarks** → **Bookmark Manager** (or press `Ctrl+Shift+O` / `Cmd+Shift+O`)
3. Click the three-dot menu in the Bookmark Manager
4. Select **Add new bookmark**
5. In the **Name** field, enter: `Search on DuckDuckGo`
6. In the **URL** field, paste the entire bookmarklet code (starting with `javascript:`)
7. Click **Save**

#### For Firefox:

1. Click the bookmarks icon in the toolbar (or press `Ctrl+Shift+B` / `Cmd+Shift+B`)
2. Right-click on the Bookmarks Toolbar (or any bookmark folder)
3. Select **New Bookmark...**
4. In the **Name** field, enter: `Search on DuckDuckGo`
5. In the **Location** field, paste the entire bookmarklet code (starting with `javascript:`)
6. Click **Save**

#### For Safari:

1. Click **Bookmarks** in the menu bar
2. Select **Add Bookmark...** (or press `Cmd+D`)
3. In the **Name** field, enter: `Search on DuckDuckGo`
4. In the **Address** field, paste the entire bookmarklet code (starting with `javascript:`)
5. Choose where to save it (e.g., Favorites Bar)
6. Click **Add**

### Step 3: Access Your Bookmarklet

- **Chrome/Edge/Brave**: The bookmarklet will appear in your bookmarks bar or bookmarks menu
- **Firefox**: The bookmarklet will appear in your Bookmarks Toolbar or bookmarks menu
- **Safari**: The bookmarklet will appear in your Favorites Bar or bookmarks menu

## Usage

1. Perform a search on Google (or any search engine that uses the `q` parameter)
2. Once you're on the search results page, click your **Search on DuckDuckGo** bookmarklet
3. A new tab will open with the same search query on DuckDuckGo

## Example

1. Go to Google and search for "JavaScript bookmarklets"
2. You'll see the URL: `https://www.google.com/search?q=JavaScript+bookmarklets`
3. Click your bookmarklet
4. A new tab opens with: `https://duckduckgo.com/?q=JavaScript%20bookmarklets`

## Supported Search Engines

The bookmarklet primarily supports:
- **Google** (uses `q` parameter)
- **Bing** (uses `q` parameter)
- **Yahoo** (uses `p` parameter - may need extension)

It also attempts to extract queries from other common parameter names (`query`, `search`, `text`) and from URL paths.

## Troubleshooting

### "No search query found on this page"

This message appears when the bookmarklet cannot find a search query in the current page URL. Make sure you:
- Are on a search results page (not the search engine's homepage)
- The URL contains a query parameter (like `?q=your+search+terms`)

### Bookmarklet doesn't work

1. **Check the code**: Make sure you copied the entire bookmarklet code, including the `javascript:` prefix
2. **Browser compatibility**: Ensure you're using a modern browser that supports `URLSearchParams` and `window.open()`
3. **Pop-up blockers**: Some browsers may block the new tab. Check your pop-up blocker settings
4. **HTTPS**: Some browsers require HTTPS pages for bookmarklets to work properly

### New tab doesn't open

- Check if your browser is blocking pop-ups
- Try allowing pop-ups for the current domain
- Some browsers require user interaction (clicking) to open new tabs

## Technical Details

### How the Bookmarklet Works

1. **Query Extraction** (`extractSearchQuery`):
   - Uses `URLSearchParams` to parse the current page URL
   - First tries the `q` parameter (Google, Bing)
   - Falls back to `query`, `search`, or `text` parameters
   - As a last resort, tries to extract from URL paths

2. **URL Construction** (`buildDuckDuckGoUrl`):
   - Takes the extracted query
   - URL-encodes it using `encodeURIComponent()`
   - Constructs the DuckDuckGo search URL

3. **Tab Opening** (`redirectToDuckDuckGo`):
   - Validates that a query was found
   - Opens DuckDuckGo in a new tab using `window.open(url, '_blank')`
   - Shows an error message if no query is found

### Browser Compatibility

The bookmarklet uses standard JavaScript APIs:
- `URLSearchParams` - Supported in all modern browsers (Chrome 49+, Firefox 44+, Safari 10.1+, Edge 17+)
- `window.open()` - Universal browser support
- `encodeURIComponent()` - Universal browser support

## Customization

To modify the bookmarklet for a different search engine, edit the `buildDuckDuckGoUrl` function in `search_redirect_bookmarklet.js`:

```javascript
function buildDuckDuckGoUrl(query) {
    if (!query) {
        return null;
    }
    const encodedQuery = encodeURIComponent(query);
    // Change this URL to your preferred search engine
    return `https://duckduckgo.com/?q=${encodedQuery}`;
}
```

Examples:
- **Bing**: `https://www.bing.com/search?q=${encodedQuery}`
- **Yahoo**: `https://search.yahoo.com/search?p=${encodedQuery}`
- **Startpage**: `https://www.startpage.com/sp/search?query=${encodedQuery}`

After modifying, you'll need to minify the code again for use as a bookmarklet.

## Security and Privacy

- The bookmarklet runs entirely in your browser - no data is sent to external servers
- It only reads the current page URL to extract the search query
- It doesn't access or modify any other page content
- DuckDuckGo is known for its privacy-focused search engine

## License

This bookmarklet is provided as-is for educational and personal use.
