/**
 * Search Engine Redirect Bookmarklet
 *
 * This bookmarklet extracts the search query from the current page (Google)
 * and opens the same query on DuckDuckGo in a new tab.
 *
 * To use as a bookmarklet:
 * 1. Copy the minified version below
 * 2. Create a new bookmark in your browser
 * 3. In the URL field, paste: javascript:[minified_code_here]
 * 4. Save the bookmark
 * 5. Click the bookmark while on a Google search results page
 */

(function() {
    'use strict';

    // Extract search query from current page URL
    function extractSearchQuery() {
        try {
            const urlParams = new URLSearchParams(window.location.search);
            let query = urlParams.get('q');

            // If 'q' parameter not found, try other common parameter names
            if (!query) {
                query = urlParams.get('query') || urlParams.get('search') || urlParams.get('text');
            }

            // If still no query found, try to extract from URL path or other sources
            if (!query) {
                // For some search engines, the query might be in the path
                const pathMatch = window.location.pathname.match(/\/search\/(.+)/);
                if (pathMatch) {
                    query = decodeURIComponent(pathMatch[1].replace(/\+/g, ' '));
                }
            }

            return query;
        } catch (error) {
            console.error('Error extracting search query:', error);
            return null;
        }
    }

    // Construct DuckDuckGo search URL
    function buildDuckDuckGoUrl(query) {
        if (!query) {
            return null;
        }

        // Encode the query for URL
        const encodedQuery = encodeURIComponent(query);
        return `https://duckduckgo.com/?q=${encodedQuery}`;
    }

    // Main function
    function redirectToDuckDuckGo() {
        const query = extractSearchQuery();

        if (!query) {
            alert('No search query found on this page. Please navigate to a search results page first.');
            return;
        }

        const duckDuckGoUrl = buildDuckDuckGoUrl(query);

        if (duckDuckGoUrl) {
            // Open DuckDuckGo search in a new tab
            window.open(duckDuckGoUrl, '_blank');
        } else {
            alert('Error: Could not construct DuckDuckGo URL.');
        }
    }

    // Execute the redirect
    redirectToDuckDuckGo();
})();

/**
 * MINIFIED VERSION FOR BOOKMARKLET USE:
 *
 * Copy the code below (it already includes the "javascript:" prefix):
 *
 * javascript:(function(){'use strict';function extractSearchQuery(){try{const urlParams=new URLSearchParams(window.location.search);let query=urlParams.get('q');if(!query){query=urlParams.get('query')||urlParams.get('search')||urlParams.get('text');}if(!query){const pathMatch=window.location.pathname.match(/\/search\/(.+)/);if(pathMatch){query=decodeURIComponent(pathMatch[1].replace(/\+/g,' '));}}return query;}catch(error){console.error('Error extracting search query:',error);return null;}}function buildDuckDuckGoUrl(query){if(!query){return null;}const encodedQuery=encodeURIComponent(query);return 'https://duckduckgo.com/?q='+encodedQuery;}function redirectToDuckDuckGo(){const query=extractSearchQuery();if(!query){alert('No search query found on this page. Please navigate to a search results page first.');return;}const duckDuckGoUrl=buildDuckDuckGoUrl(query);if(duckDuckGoUrl){window.open(duckDuckGoUrl,'_blank');}else{alert('Error: Could not construct DuckDuckGo URL.');}}redirectToDuckDuckGo();})();
 *
 * Paste this entire line (including "javascript:") into the URL field when creating a bookmark.
 */
