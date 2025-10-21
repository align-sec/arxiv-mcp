#!/usr/bin/env python3
"""
ArXiv MCP Server (FastMCP version)

This server implements the find_papers tool that queries the arXiv API
and returns matching papers to the MCP client.
"""

import json
import sys
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Any, Dict, List, Optional

from mcp.server.fastmcp import FastMCP

# arXiv API endpoint
ARXIV_API_URL = "http://export.arxiv.org/api/query"

# XML namespaces used by arXiv API
NAMESPACES = {
    'atom': 'http://www.w3.org/2005/Atom',
    'arxiv': 'http://arxiv.org/schemas/atom'
}

# Create FastMCP server
mcp = FastMCP("arxiv-server")


def parse_arxiv_response(xml_data: str, min_date: Optional[str] = None) -> List[Dict[str, Any]]:
    """Parse the XML response from arXiv API."""
    print(f"[SERVER] Parsing XML response...", file=sys.stderr)
    root = ET.fromstring(xml_data)
    papers = []
    
    # Parse minimum date if provided
    min_datetime = None
    if min_date:
        try:
            min_datetime = datetime.strptime(min_date, "%Y-%m-%d")
        except ValueError:
            print(f"[SERVER] Warning: Invalid min_date format: {min_date}", file=sys.stderr)
    
    # Find all entry elements (papers)
    for entry in root.findall('atom:entry', NAMESPACES):
        paper = {}
        
        # Title
        title_elem = entry.find('atom:title', NAMESPACES)
        if title_elem is not None:
            paper['title'] = ' '.join(title_elem.text.split())
        
        # Summary (abstract)
        summary_elem = entry.find('atom:summary', NAMESPACES)
        if summary_elem is not None:
            paper['summary'] = ' '.join(summary_elem.text.split())
        
        # Published date
        published_elem = entry.find('atom:published', NAMESPACES)
        if published_elem is not None:
            published_date = published_elem.text
            paper['published'] = published_date
            
            # Filter by min_date if specified
            if min_datetime:
                try:
                    paper_date = datetime.strptime(published_date[:10], "%Y-%m-%d")
                    if paper_date < min_datetime:
                        continue  # Skip papers before min_date
                except ValueError:
                    pass
        
        # Authors
        authors = []
        for author_elem in entry.findall('atom:author', NAMESPACES):
            name_elem = author_elem.find('atom:name', NAMESPACES)
            if name_elem is not None:
                authors.append(name_elem.text)
        paper['authors'] = authors
        
        # arXiv ID
        id_elem = entry.find('atom:id', NAMESPACES)
        if id_elem is not None:
            arxiv_url = id_elem.text
            paper['arxiv_id'] = arxiv_url.split('/abs/')[-1]
            paper['url'] = arxiv_url
        
        # Categories
        categories = []
        for category_elem in entry.findall('atom:category', NAMESPACES):
            term = category_elem.get('term')
            if term:
                categories.append(term)
        paper['categories'] = categories
        
        # Updated date
        updated_elem = entry.find('atom:updated', NAMESPACES)
        if updated_elem is not None:
            paper['updated'] = updated_elem.text
        
        papers.append(paper)
    
    print(f"[SERVER] ✓ Parsed {len(papers)} papers", file=sys.stderr)
    return papers


@mcp.tool()
def find_papers(
    search_terms: list[str],
    min_date: str | None = None,
    max_results: int = 10
) -> str:
    """
    Search for papers on arXiv based on search terms, optional minimum date, and maximum number of results.
    
    Args:
        search_terms: List of search terms to query arXiv
        min_date: Minimum publication date in YYYY-MM-DD format (optional)
        max_results: Maximum number of results to return (default: 10)
    
    Returns:
        JSON string containing list of papers with title, summary, authors, dates, and URLs
    """
    print(f"\n[SERVER] find_papers called", file=sys.stderr)
    print(f"[SERVER] Search terms: {search_terms}", file=sys.stderr)
    print(f"[SERVER] Min date: {min_date}", file=sys.stderr)
    print(f"[SERVER] Max results: {max_results}", file=sys.stderr)
    
    # Build the search query
    # Use AND to find papers matching ALL search terms (more precise)
    # Use all: prefix to search in all fields (title, abstract, authors, etc.)
    query_parts = [f'all:"{term}"' for term in search_terms]
    search_query = " AND ".join(query_parts)
    print(f"[SERVER] Built query: {search_query}", file=sys.stderr)
    
    # Build the API URL
    params = {
        'search_query': search_query,
        'start': 0,
        'max_results': max_results,
        'sortBy': 'submittedDate',
        'sortOrder': 'descending'
    }
    
    url = f"{ARXIV_API_URL}?{urllib.parse.urlencode(params)}"
    print(f"[SERVER] API URL: {url[:100]}...", file=sys.stderr)
    
    # Make the API request
    print(f"[SERVER] Making HTTP request to arXiv...", file=sys.stderr)
    try:
        with urllib.request.urlopen(url) as response:
            xml_data = response.read().decode('utf-8')
        print(f"[SERVER] ✓ Received {len(xml_data)} bytes from arXiv", file=sys.stderr)
    except Exception as e:
        print(f"[SERVER] ✗ Failed to query arXiv API: {e}", file=sys.stderr)
        return json.dumps({"error": str(e)})
    
    # Parse the XML response
    papers = parse_arxiv_response(xml_data, min_date)
    
    print(f"[SERVER] ✓ Returning {len(papers)} papers to client", file=sys.stderr)
    return json.dumps(papers, indent=2)


if __name__ == "__main__":
    print(f"[SERVER] Python: {sys.executable}", file=sys.stderr)
    print(f"[SERVER] Starting FastMCP server...", file=sys.stderr)
    sys.stderr.flush()
    
    mcp.run()
