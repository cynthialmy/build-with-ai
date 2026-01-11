#!/usr/bin/env python3
"""
Extract structured data from CVPR 2024 HTML file.
Extracts paper titles, authors, and links to PDFs, supplementary materials, and arXiv.
"""

import json
import re
from datetime import datetime
from pathlib import Path
from urllib.parse import urljoin

from bs4 import BeautifulSoup

# Base URL for converting relative URLs to absolute
BASE_URL = "https://openaccess.thecvf.com"


def extract_papers(html_file_path):
    """
    Extract paper data from CVPR HTML file.

    Args:
        html_file_path: Path to CVPR.html file

    Returns:
        List of dictionaries containing paper data
    """
    with open(html_file_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    # Use html.parser (built-in) instead of lxml for better compatibility
    soup = BeautifulSoup(html_content, 'html.parser')

    papers = []

    # Find all paper title elements
    paper_titles = soup.find_all('dt', class_='ptitle')

    for title_elem in paper_titles:
        paper_data = {}

        # Extract title and HTML URL
        title_link = title_elem.find('a')
        if title_link:
            # Clean title: strip and normalize whitespace
            title = title_link.get_text()
            paper_data['title'] = ' '.join(title.split())  # Normalize whitespace
            html_url = title_link.get('href', '')
            if html_url:
                paper_data['html_url'] = urljoin(BASE_URL, html_url)
            else:
                paper_data['html_url'] = None
        else:
            continue  # Skip if no title link found

        # Find the next sibling <dd> elements
        current = title_elem.find_next_sibling('dd')

        # First <dd> contains authors
        authors = []
        if current:
            # Find all form elements with author names
            author_forms = current.find_all('form', class_='authsearch')
            for form in author_forms:
                input_elem = form.find('input', {'name': 'query_author'})
                if input_elem:
                    author_name = input_elem.get('value', '').strip()
                    if author_name:
                        authors.append(author_name)

            paper_data['authors'] = authors

            # Move to next <dd> for links
            current = current.find_next_sibling('dd')

        # Second <dd> contains links (PDF, supplementary, arXiv) and BibTeX
        pdf_url = None
        supplementary_url = None
        arxiv_url = None
        bibtex = None

        if current:
            # Find all links
            links = current.find_all('a')
            for link in links:
                href = link.get('href', '')
                link_text = link.get_text(strip=True).lower()

                if 'pdf' in link_text and '/papers/' in href:
                    pdf_url = urljoin(BASE_URL, href)
                elif 'supp' in link_text and '/supplemental/' in href:
                    supplementary_url = urljoin(BASE_URL, href)
                elif 'arxiv' in link_text or 'arxiv.org' in href:
                    arxiv_url = href  # arXiv URLs are already absolute

            # Extract BibTeX
            bibtex_div = current.find('div', class_='bibref')
            if bibtex_div:
                bibtex = bibtex_div.get_text(strip=True)
                # Clean up BibTeX (remove extra whitespace)
                bibtex = re.sub(r'\s+', ' ', bibtex)

        paper_data['pdf_url'] = pdf_url
        paper_data['supplementary_url'] = supplementary_url if supplementary_url else None
        paper_data['arxiv_url'] = arxiv_url if arxiv_url else None
        paper_data['bibtex'] = bibtex if bibtex else None

        papers.append(paper_data)

    return papers


def main():
    """Main function to extract data and save to JSON."""
    html_file = Path('CVPR.html')

    if not html_file.exists():
        print(f"Error: {html_file} not found!")
        return

    print(f"Extracting data from {html_file}...")
    papers = extract_papers(html_file)

    print(f"Extracted {len(papers)} papers")

    # Create output structure with metadata
    output = {
        'metadata': {
            'total_papers': len(papers),
            'extraction_date': datetime.now().isoformat(),
            'source': 'CVPR 2024',
            'source_url': 'https://openaccess.thecvf.com/CVPR2024?day=all'
        },
        'papers': papers
    }

    # Save to JSON file
    output_file = Path('cvpr2024_papers.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"Data saved to {output_file}")
    print(f"Total papers: {len(papers)}")

    # Print some statistics
    papers_with_supp = sum(1 for p in papers if p.get('supplementary_url'))
    papers_with_arxiv = sum(1 for p in papers if p.get('arxiv_url'))

    print(f"Papers with supplementary materials: {papers_with_supp}")
    print(f"Papers with arXiv links: {papers_with_arxiv}")


if __name__ == '__main__':
    main()
