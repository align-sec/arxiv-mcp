# ArXiv MCP Client & Server

A complete Model Context Protocol (MCP) implementation for searching arXiv papers using natural language queries powered by Claude.

## Overview

This project includes a client, server, and web interface:

- **Client** (`arxiv_client.py`): Accepts natural language queries, uses Claude to parse them into structured parameters, calls the server, and scores results by relevance
- **Server** (`arxiv_server.py`): Implements the `find_papers` tool that queries the arXiv API and returns matching papers
- **Web App** (`app.py`): Beautiful Streamlit interface for easy paper searching

## Features

- **Natural Language Processing**: Uses Claude to understand queries like "find me 10 recent papers about LLM red teaming as it applies to security of AI agents"
- **Intelligent Parameter Extraction**: Automatically extracts:
  - Search terms (keywords for arXiv search)
  - Date ranges (e.g., "recent" → last 6 months, "past year" → 1 year ago)
  - Number of results (defaults to 10 if not specified)
- **Smart Relevance Scoring**: After retrieving papers from the server:
  - Calculates relevance score based on search term matches in title and summary
  - Scores are computed client-side (no additional API calls)
  - Results sorted by relevance score (highest first)
- **MCP Integration**: Ready to connect to an MCP server implementing the `find_papers` tool

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set your Anthropic API key (for command-line usage):
```bash
export ANTHROPIC_API_KEY="your-api-key-here"
```

## Quick Start - Web Interface 🌟

The easiest way to use the system is through the Streamlit web app:

```bash
streamlit run app.py
```

Then:
1. Enter your Anthropic API key in the sidebar
2. Type your search query (e.g., "find me 10 recent papers about transformers")
3. Click "Search Papers"
4. View beautifully formatted, relevance-scored results!

The web app features:
- 🎨 Beautiful gradient tiles for each paper (color-coded by relevance)
- ⭐ Visual relevance scores (0.00 to 1.00)
- 📱 Responsive design that works on all devices
- 🔗 Direct links to arXiv papers
- 💡 Example queries and help text
- 🔒 Secure API key input (not stored)
- ⚡ **FAST**: Only ONE API call (query parsing), everything else is instant!

**Note**: The Streamlit app uses `arxiv_client_simple.py` which calls the server functions directly (in-process) for better performance and reliability in a web environment. For true MCP client/server architecture over stdio, see the examples below.

**Alternative launcher:**
```bash
./run_app.sh
```

## Usage

### As a Library

```python
import asyncio
from arxiv_client import ArxivMCPClient

async def search_papers():
    # Initialize client with your API key
    client = ArxivMCPClient(anthropic_api_key="your-api-key")
    
    # Parse a natural language query
    query = "find me 10 recent papers about LLM red teaming"
    params = client.parse_query_with_claude(query)
    print(params)
    # Output: {
    #   "search_terms": ["LLM", "red teaming", "language models", "security"],
    #   "min_date": "2024-04-21",
    #   "max_results": 10
    # }
    
    # When server is available, connect and search:
    # from mcp import StdioServerParameters
    # server_params = StdioServerParameters(
    #     command="python",
    #     args=["arxiv_server.py"]
    # )
    # await client.connect_to_server(server_params)
    # results = await client.search_papers(query)
    # # Results are automatically scored and sorted by relevance
    # for paper in results:
    #     print(f"Score: {paper['relevance_score']:.2f} - {paper['title']}")
    # await client.disconnect()

asyncio.run(search_papers())
```

### Command Line Demo

Run the included demo (query parsing only, no server):
```bash
python arxiv_client.py
```

### Integration Test

Run the full client-server integration test:
```bash
export ANTHROPIC_API_KEY="your-api-key"
python test_integration.py
```

This will:
1. Start the server
2. Parse a natural language query
3. Query arXiv API
4. Score papers for relevance
5. Display sorted results

## Query Examples

The client can understand various natural language queries:

- `"find me 10 recent papers about LLM red teaming as it applies to security of AI agents"`
- `"search for papers on quantum computing from the last year"`
- `"get 5 papers about neural networks published in the last 3 months"`
- `"find papers on transformer architectures"`

## Parsed Parameters Schema

The client extracts queries into the following JSON structure:

```json
{
    "search_terms": ["list", "of", "keywords"],
    "min_date": "YYYY-MM-DD",  // optional
    "max_results": 10           // defaults to 10
}
```

### Parameters

- **search_terms** (required): List of relevant keywords extracted from the query
- **min_date** (optional): Minimum publication date in YYYY-MM-DD format
  - "recent" without specifics → 6 months ago
  - "last year" → 1 year ago
  - "past 3 months" → 3 months ago
- **max_results** (optional): Number of papers to return (default: 10)

## Relevance Scoring

After retrieving papers from the server, the client automatically:

1. **Calculates relevance** by matching search terms against paper titles and summaries
   - Title matches are weighted more heavily (60%)
   - Summary matches contribute 40%
   - All done client-side with no additional API calls
2. **Assigns a relevance score** from 0.0 to 1.0 based on match percentage
3. **Sorts results** by relevance score (highest first)

This ensures that the most relevant papers appear at the top of the results, even if the arXiv search returned them in a different order.

**Performance**: Only ONE API call is made (to parse the query). Everything else is fast client-side processing.

## Server Implementation

The included `arxiv_server.py` implements an MCP server with the following features:

### `find_papers` Tool

Accepts parameters:
- `search_terms` (required): List of keywords to search for
- `min_date` (optional): Minimum publication date (YYYY-MM-DD)
- `max_results` (optional): Maximum number of results (default: 10)

Returns papers with:
- `title`: Paper title
- `summary`: Paper abstract
- `authors`: List of author names
- `published`: Publication date
- `updated`: Last update date
- `arxiv_id`: arXiv identifier
- `url`: Full arXiv URL
- `categories`: arXiv categories

### arXiv API Integration

The server queries the arXiv API using:
- Search query built from search terms (searches all fields)
- Results sorted by submission date (most recent first)
- XML response parsing with proper namespace handling
- Date filtering applied after retrieval

## Running the Complete System

### Start the Server

In one terminal:
```bash
python arxiv_server.py
```

### Run the Client

Update `arxiv_client.py` to uncomment the server connection code in the `main()` function, then:
```bash
export ANTHROPIC_API_KEY="your-api-key"
python arxiv_client.py
```

### Full Integration Example

```python
import asyncio
from arxiv_client import ArxivMCPClient
from mcp import StdioServerParameters

async def search_with_server():
    # Initialize client
    client = ArxivMCPClient(anthropic_api_key="your-key")
    
    # Configure server connection
    server_params = StdioServerParameters(
        command="python",
        args=["arxiv_server.py"]
    )
    
    # Connect and search
    await client.connect_to_server(server_params)
    
    query = "find me 10 recent papers about LLM red teaming"
    results = await client.search_papers(query)
    
    # Results are automatically scored and sorted by relevance
    for i, paper in enumerate(results, 1):
        print(f"\n{i}. [{paper['relevance_score']:.2f}] {paper['title']}")
        print(f"   Authors: {', '.join(paper['authors'][:3])}")
        print(f"   Published: {paper['published'][:10]}")
        print(f"   URL: {paper['url']}")
    
    await client.disconnect()

asyncio.run(search_with_server())
```

## Requirements

- Python 3.8+
- Anthropic API key
- MCP-compatible server (for full functionality)

## License

MIT
