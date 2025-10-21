Let's build an MCP client / server implementation. We will start with the client. The client should accept a natural language search for papers from arXiv. An example might be "find me 10 recent papers about LLM red teaming as it applies to security of AI agents". The client should take the query and use an Anthropic API key to turn that query into a JSON object with the following schema: 
```json
{
    "search_terms": 
        {
            "type": str,
            "desc": "list of words to search arxiv for, most relevant terms for the search based on user query",
            "optional", false
        }, 
    "min_date": 
        {
            "type": str,
            "desc": "YYYY-MM-DD minimum date pulled from user query (e.g. if user says 'find papers from last 6 months', it would be the YYYY-MM-DD that would be 6 months prior from the current date",
            "optional", true
        },
    "max_results":
        {
            "type": int,
            "default": 10,
            "desc": "Maximum number of papers to return to user",
            "optional", true
        }
}
```

Then it will call the server's `find_papers` tool which will take in the above keys with the relevant default values. Don't implement any of the server yet, just the client. Assume the API key will be passed to the client.

When the results are returned from the server, the client will then use the LLM again to check the summary with the user's original query and ensure it is relevant. It will assign a relevance score to each and sort them in order of relevance.
