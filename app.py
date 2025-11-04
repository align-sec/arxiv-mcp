#!/usr/bin/env python3
"""
ArXiv Paper Search - Streamlit App

A cute and simple interface for searching arXiv papers using natural language.
"""

import streamlit as st
from arxiv_client_simple import ArxivClient


# Page configuration
st.set_page_config(
    page_title="ArXiv Paper Search",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for aesthetic styling
st.markdown("""
<style>
    /* Main title styling */
    .main-title {
        text-align: center;
        color: #1f77b4;
        font-size: 3em;
        font-weight: bold;
        margin-bottom: 0.2em;
    }
    
    .subtitle {
        text-align: center;
        color: #666;
        font-size: 1.2em;
        margin-bottom: 2em;
    }
    
    /* Paper tile styling */
    .paper-tile {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 15px;
        padding: 20px;
        margin: 15px 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        transition: transform 0.2s;
        color: white;
    }
    
    .paper-tile:hover {
        transform: translateY(-5px);
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
    }
    
    .relevance-badge {
        background: rgba(255, 255, 255, 0.3);
        border-radius: 20px;
        padding: 5px 15px;
        display: inline-block;
        font-weight: bold;
        font-size: 0.9em;
        margin-bottom: 10px;
    }
    
    .paper-title {
        font-size: 1.3em;
        font-weight: bold;
        margin: 10px 0;
        color: white;
    }
    
    .paper-meta {
        font-size: 0.9em;
        opacity: 0.9;
        margin: 5px 0;
    }
    
    .paper-summary {
        margin-top: 15px;
        line-height: 1.6;
        opacity: 0.95;
        font-size: 0.95em;
    }
    
    .paper-link {
        display: inline-block;
        margin-top: 10px;
        padding: 8px 20px;
        background: rgba(255, 255, 255, 0.2);
        border-radius: 20px;
        text-decoration: none;
        color: white;
        font-weight: bold;
        transition: background 0.2s;
    }
    
    .paper-link:hover {
        background: rgba(255, 255, 255, 0.3);
    }
    
    /* Sidebar styling */
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%);
    }
    
    /* Success/info boxes */
    .stAlert {
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)


def render_paper_tile(paper, index):
    """Render a single paper as an aesthetic tile."""
    # Generate gradient colors based on relevance score
    score = paper.get('relevance_score', 0)
    if score >= 0.8:
        gradient = "linear-gradient(135deg, #667eea 0%, #764ba2 100%)"
    elif score >= 0.6:
        gradient = "linear-gradient(135deg, #f093fb 0%, #f5576c 100%)"
    elif score >= 0.4:
        gradient = "linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)"
    else:
        gradient = "linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)"
    
    # Format authors
    authors = paper.get('authors', [])
    author_text = ', '.join(authors[:3])
    if len(authors) > 3:
        author_text += f" +{len(authors) - 3} more"
    
    # Format date
    published = paper.get('published', '')[:10]
    
    # Truncate summary
    summary = paper.get('summary', '')
    if len(summary) > 300:
        summary = summary[:297] + "..."
    
    # Create tile HTML
    tile_html = f"""
    <div style="background: {gradient}; border-radius: 15px; padding: 20px; margin: 15px 0; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); color: white;">
        <div style="background: rgba(255, 255, 255, 0.3); border-radius: 20px; padding: 5px 15px; display: inline-block; font-weight: bold; font-size: 0.9em; margin-bottom: 10px;">
            ⭐ Relevance: {score:.2f}
        </div>
        <div style="font-size: 1.3em; font-weight: bold; margin: 10px 0;">
            {index}. {paper.get('title', 'Untitled')}
        </div>
        <div style="font-size: 0.9em; opacity: 0.9; margin: 5px 0;">
            👥 {author_text}
        </div>
        <div style="font-size: 0.9em; opacity: 0.9; margin: 5px 0;">
            📅 Published: {published} | 🏷️ {paper.get('arxiv_id', 'N/A')}
        </div>
        <div style="margin-top: 15px; line-height: 1.6; opacity: 0.95; font-size: 0.95em;">
            {summary}
        </div>
        <a href="{paper.get('url', '#')}" target="_blank" style="display: inline-block; margin-top: 10px; padding: 8px 20px; background: rgba(255, 255, 255, 0.2); border-radius: 20px; text-decoration: none; color: white; font-weight: bold;">
            📄 View on arXiv →
        </a>
    </div>
    """
    
    st.markdown(tile_html, unsafe_allow_html=True)


def search_papers(api_key, query):
    """Search for papers (synchronous, fast)."""
    client = ArxivClient(anthropic_api_key=api_key)
    return client.search_papers(query)


def main():
    """Main Streamlit app."""
    
    # Header
    st.markdown('<div class="main-title">📚 ArXiv Paper Search</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Find research papers using natural language ✨</div>', unsafe_allow_html=True)
    
    # Sidebar for inputs
    with st.sidebar:
        st.header("🔑 Configuration")
        
        # API Key input
        api_key = st.text_input(
            "Anthropic API Key",
            type="password",
            help="Enter your Anthropic API key to use Claude for query parsing and relevance scoring"
        )
        
        st.markdown("---")
        
        st.header("🔍 Search Query")
        
        # Query input
        query = st.text_area(
            "What papers are you looking for?",
            placeholder="Example: find me 10 recent papers about LLM red teaming as it applies to security of AI agents",
            height=120,
            help="Describe what you're looking for in natural language"
        )
        
        # Search button
        search_button = st.button("🚀 Search Papers", type="primary", use_container_width=True)
        
        st.markdown("---")
        
        st.header("📄 Direct Paper Link")
        
        # Paper link input
        paper_link = st.text_input(
            "Enter arXiv paper link",
            placeholder="Example: https://arxiv.org/abs/2301.07041",
            help="Enter a direct link to an arXiv paper to process it"
        )
        
        # Process link button
        process_link_button = st.button("📥 Process Paper Link", use_container_width=True)
        
        st.markdown("---")
        
        # Info section
        with st.expander("ℹ️ How it works"):
            st.markdown("""
            1. **Enter your query** in natural language
            2. **Claude parses** your query to extract search terms and parameters
            3. **arXiv API** is queried for matching papers
            4. **AI scores** each paper for relevance
            5. **Results** are sorted by relevance score
            
            **Example queries:**
            - "find recent papers on transformers"
            - "papers about quantum computing from last year"
            - "5 papers on neural network optimization"
            """)
    
    # Main content area
    if process_link_button:
        if not api_key:
            st.error("⚠️ Please enter your Anthropic API key in the sidebar")
            return
        
        if not paper_link:
            st.error("⚠️ Please enter a paper link in the sidebar")
            return
        
        # Show loading state
        print(f"\n[APP] User submitted paper link: {paper_link}")
        
        with st.spinner("📥 Processing paper link..."):
            try:
                client = ArxivClient(anthropic_api_key=api_key)
                
                # Process the paper link
                result = client.process_paper_link(paper_link)
                
                if result:
                    st.success("✅ Paper link processed successfully!")
                    st.json(result)
                else:
                    st.warning("😔 Could not process the paper link. Please check if it's a valid arXiv URL.")
                    
            except Exception as e:
                st.error(f"❌ An error occurred: {str(e)}")
                st.info("💡 Make sure the link is a valid arXiv URL and your API key is valid")
    
    elif search_button:
        if not api_key:
            st.error("⚠️ Please enter your Anthropic API key in the sidebar")
            return
        
        if not query:
            st.error("⚠️ Please enter a search query in the sidebar")
            return
        
        # Show loading state
        print(f"\n[APP] User submitted query: {query[:100]}...")
        
        # Parse query first to show what's being sent
        with st.spinner("🔮 Parsing your query with AI..."):
            try:
                print("[APP] Calling search_papers function...")
                client = ArxivClient(anthropic_api_key=api_key)
                
                # Parse query and show parameters
                params = client.parse_query_with_claude(query)
                
                # Display parsed parameters
                st.info("📋 **Query Parameters Sent to Server:**")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Search Terms", len(params.get('search_terms', [])))
                    with st.expander("View terms"):
                        for term in params.get('search_terms', []):
                            st.write(f"• {term}")
                with col2:
                    st.metric("Max Results", params.get('max_results', 10))
                with col3:
                    min_date = params.get('min_date', 'None')
                    st.metric("Min Date", min_date if min_date else "Any")
                
                # Now search with those parameters
                st.spinner("🔍 Searching arXiv...")
                results = client.search_papers(query)
                print(f"[APP] search_papers returned {len(results) if results else 0} results")
                
                # Display results
                if results:
                    st.success(f"✅ Found {len(results)} papers! Results sorted by relevance:")
                    
                    # Render each paper as a tile
                    for i, paper in enumerate(results, 1):
                        render_paper_tile(paper, i)
                    
                else:
                    st.warning("😔 No papers found matching your query. Try different search terms!")
                    
            except Exception as e:
                st.error(f"❌ An error occurred: {str(e)}")
                st.info("💡 Make sure the server is accessible and your API key is valid")
    
    else:
        # Welcome message when no search has been performed
        st.info("👈 Enter your API key and search query in the sidebar, then click 'Search Papers' to get started!")
        
        # Show example
        st.markdown("### 💡 Example")
        st.markdown("Try searching for: *'find me 5 recent papers about transformer architectures'*")
        
        # Show features
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div style="text-align: center; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 15px; color: white;">
                <div style="font-size: 2em; margin-bottom: 10px;">🤖</div>
                <div style="font-weight: bold; margin-bottom: 5px;">AI-Powered</div>
                <div style="font-size: 0.9em; opacity: 0.9;">Natural language understanding</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div style="text-align: center; padding: 20px; background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); border-radius: 15px; color: white;">
                <div style="font-size: 2em; margin-bottom: 10px;">⭐</div>
                <div style="font-weight: bold; margin-bottom: 5px;">Relevance Scoring</div>
                <div style="font-size: 0.9em; opacity: 0.9;">Best matches first</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div style="text-align: center; padding: 20px; background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); border-radius: 15px; color: white;">
                <div style="font-size: 2em; margin-bottom: 10px;">📚</div>
                <div style="font-weight: bold; margin-bottom: 5px;">arXiv Access</div>
                <div style="font-size: 0.9em; opacity: 0.9;">Millions of papers</div>
            </div>
            """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
