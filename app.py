import streamlit as st
from scraper import CareerPageScraper
from llm_handler import LLMHandler
import validators
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Page config
st.set_page_config(
    page_title="AI Career Page Finder",
    page_icon="💼",
    layout="wide"
)

# Initialize LLM Handler
@st.cache_resource
def get_llm_handler():
    return LLMHandler(GEMINI_API_KEY)

llm = get_llm_handler()

# Title and description
st.title("AI Career Page Finder")
st.markdown("🤖 **Ask me in natural language to find career pages!**")

# Sidebar info
with st.sidebar:
    st.header("ℹHow it works")
    st.markdown("""
    **Just ask naturally!** 
    
    Examples:
    - "Find career pages from google.com"
    - "Show me jobs at netflix.com"
    - "Does spotify have job openings?"
    - "Search hiring info on github.com"
    
    **Powered by:**
    - Google Gemini 2.5 Flash
    - Playwright (Web Scraping)
    - ⚡ Streamlit
    """)
    
    st.markdown("---")
    st.info("💡 Tip: You can type the website name naturally, I'll figure out the URL!")

# Main input section
st.markdown("### Ask Me Anything")

user_prompt = st.text_input(
    "Your Request",
    placeholder="Find career pages from google.com",
    label_visibility="collapsed"
)

search_button = st.button("🔍 Search", type="primary", use_container_width=True)

# Search logic
if search_button:
    if not user_prompt:
        st.error("Please enter your request")
    else:
        # Step 1: Use LLM to understand intent and extract URL
        with st.spinner('Understanding your request...'):
            llm_result = llm.extract_url_and_intent(user_prompt)
        
        # Show what LLM understood
        with st.expander("What I Understood", expanded=False):
            st.write("**Intent:**", llm_result.get('intent', 'unknown'))
            st.write("**URL:**", llm_result.get('url', 'None'))
            st.code(llm_result.get('raw_response', ''))
        
        # Check if intent is to find careers
        if llm_result['intent'] == 'find_careers':
            website_url = llm_result['url']
            
            if not website_url:
                st.error("❌ I couldn't find a website URL in your message. Please include a website!")
            elif not validators.url(website_url):
                st.error(f"❌ '{website_url}' doesn't seem to be a valid URL")
            else:
                st.success(f"✅ Got it! Searching for career pages on: **{website_url}**")
                
                # Step 2: Scrape the website
                with st.spinner(f'Scraping {website_url}... This may take 30-60 seconds'):
                    scraper = CareerPageScraper()
                    result = scraper.scrape_career_pages(website_url)
                
                # Step 3: Display results
                if 'error' in result:
                    st.error(f"❌ Error: {result['error']}")
                elif result['success']:
                    st.success(f"Scan complete! Found {result['count']} career page(s)")
                    
                    # Stats
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Total Links Scanned", result['total_links_found'])
                    with col2:
                        st.metric("Career Pages Found", result['count'])
                    with col3:
                        verified_count = sum(1 for page in result['career_pages'] if page['verified'])
                        st.metric("Verified Pages", verified_count)
                    
                    st.markdown("---")
                    
                    # Display career pages
                    if result['career_pages']:
                        st.markdown("### Career Pages Found")
                        
                        for idx, page in enumerate(result['career_pages'], 1):
                            with st.expander(f"**{idx}. {page['title']}**", expanded=True):
                                st.markdown(f"**🔗 URL:** [{page['url']}]({page['url']})")
                                st.markdown(f"**Link Text:** {page['link_text']}")
                                
                                if page['verified']:
                                    st.success("✓ Verified - Contains job-related content")
                                else:
                                    st.info("⚠️ Unverified - Matched by URL/text pattern only")
                                
                                st.markdown("---")
                    else:
                        st.warning("No career pages found on this website")
                        st.info("💡 The website might not have a careers section or it might be named differently")
        
        elif llm_result['intent'] == 'unknown':
            st.warning("🤔 I'm not sure what you want me to do. Try asking like:")
            st.info("'Find career pages from netflix.com' or 'Show me jobs at google.com'")
        
        elif llm_result['intent'] == 'error':
            st.error(f"LLM Error: {llm_result.get('error', 'Unknown error')}")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: gray;'>
    <small>Built using Google Gemini 2.5 Flash, Playwright & Streamlit</small>
    </div>
    """,
    unsafe_allow_html=True
)
