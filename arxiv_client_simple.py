#!/usr/bin/env python3
"""
Simplified ArXiv Client - calls server directly without MCP stdio transport

This version is optimized for use in Streamlit where stdio transport can be problematic.
"""

import json
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional

from anthropic import Anthropic

# Import the server's find_papers function directly
from arxiv_server_fast import find_papers


class ArxivClient:
    """Simplified client for searching arXiv papers."""
    
    def __init__(self, anthropic_api_key: str):
        """
        Initialize the ArXiv Client.
        
        Args:
            anthropic_api_key: API key for Anthropic Claude
        """
        self.anthropic_client = Anthropic(api_key=anthropic_api_key)
        print(f"[CLIENT] Client initialized", file=sys.stderr)
    
    def _calculate_relevance_score(self, search_terms: List[str], paper: Dict[str, Any]) -> float:
        """Calculate relevance score based on search term matches."""
        title = paper.get('title', '').lower()
        summary = paper.get('summary', '').lower()
        
        if not search_terms:
            return 0.5
        
        title_matches = sum(1 for term in search_terms if term.lower() in title)
        summary_matches = sum(1 for term in search_terms if term.lower() in summary)
        
        total_terms = len(search_terms)
        title_score = (title_matches / total_terms) * 0.6
        summary_score = (summary_matches / total_terms) * 0.4
        
        return max(0.0, min(1.0, title_score + summary_score))
    
    def parse_query_with_claude(self, user_query: str) -> Dict[str, Any]:
        """Use Claude to parse a natural language query into structured parameters."""
        current_date = datetime.now().strftime("%Y-%m-%d")
        
        system_prompt = f"""You are a helpful assistant that extracts structured information from natural language queries about arXiv papers.

Current date: {current_date}

Given a user query, extract the following information and return ONLY a valid JSON object (no markdown, no explanation):

{{
    "search_terms": ["list", "of", "key", "terms"],
    "min_date": "YYYY-MM-DD or null if not specified",
    "max_results": integer (default 10 if not specified)
}}

Rules:
- search_terms: Extract 2-4 KEY terms only. Be selective and avoid redundancy. Focus on the core concepts.
  * Use specific technical terms when present (e.g., "transformer", "BERT", "quantum computing")
  * Avoid generic words like "papers", "research", "about"
  * Don't include synonyms or related terms - pick the most important one
  * Combine related concepts into single terms when possible
  * Example: "LLM red teaming for AI agent security" → ["LLM", "red teaming", "AI agents"]
- min_date: If the user mentions a time period (e.g., "last 6 months", "recent", "past year"), calculate the date. If "recent" without specifics, use 6 months ago. If not mentioned, use null.
- max_results: Extract the number of papers requested. Default to 10 if not specified.

Return ONLY the JSON object, nothing else."""

        print(f"[CLIENT] Calling Anthropic API to parse query...", file=sys.stderr)
        response = self.anthropic_client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
            system=system_prompt,
            messages=[{"role": "user", "content": user_query}]
        )
        print(f"[CLIENT] ✓ Received response from Anthropic API", file=sys.stderr)
        
        response_text = response.content[0].text.strip()
        
        # Remove markdown code blocks if present
        if response_text.startswith("```"):
            lines = response_text.split("\n")
            response_text = "\n".join(lines[1:-1]) if len(lines) > 2 else response_text
            if response_text.startswith("json"):
                response_text = response_text[4:].strip()
        
        try:
            parsed_data = json.loads(response_text)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse Claude's response as JSON: {response_text}") from e
        
        result = {
            "search_terms": parsed_data.get("search_terms", []),
            "max_results": parsed_data.get("max_results", 10)
        }
        
        min_date = parsed_data.get("min_date")
        if min_date and min_date != "null":
            result["min_date"] = min_date
            
        return result
    
    def search_papers(self, user_query: str) -> List[Dict[str, Any]]:
        """
        Search for arXiv papers based on a natural language query.
        
        Args:
            user_query: Natural language query from the user
            
        Returns:
            List of papers matching the search criteria
        """
        print(f"[CLIENT] Step 1/4: Parsing query with Claude...", file=sys.stderr)
        params = self.parse_query_with_claude(user_query)
        print(f"[CLIENT] ✓ Query parsed: {json.dumps(params)}", file=sys.stderr)
        
        print(f"[CLIENT] Step 2/4: Calling server's find_papers...", file=sys.stderr)
        result_json = find_papers(
            search_terms=params.get("search_terms", []),
            min_date=params.get("min_date"),
            max_results=params.get("max_results", 10)
        )
        print(f"[CLIENT] ✓ Received response from server", file=sys.stderr)
        
        print(f"[CLIENT] Step 3/4: Processing server response...", file=sys.stderr)
        papers = json.loads(result_json)
        print(f"[CLIENT] Found {len(papers)} papers", file=sys.stderr)
        
        if papers:
            print(f"[CLIENT] Step 4/4: Scoring papers for relevance (client-side)...", file=sys.stderr)
            search_terms = params.get('search_terms', [])
            
            for i, paper in enumerate(papers, 1):
                score = self._calculate_relevance_score(search_terms, paper)
                paper['relevance_score'] = score
                print(f"[CLIENT]   {i}/{len(papers)}: Score {score:.2f}", file=sys.stderr)
            
            papers.sort(key=lambda p: p.get('relevance_score', 0), reverse=True)
            print(f"[CLIENT] ✓ Papers sorted by relevance", file=sys.stderr)
        
        print(f"[CLIENT] ✓ Search complete! Returning {len(papers)} papers", file=sys.stderr)
        return papers


if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    
    client = ArxivClient(api_key)
    results = client.search_papers("find 3 papers about transformers")
    
    print(f"\nFound {len(results)} papers:")
    for i, paper in enumerate(results, 1):
        print(f"{i}. [{paper['relevance_score']:.2f}] {paper['title']}")
