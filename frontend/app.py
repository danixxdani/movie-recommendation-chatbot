import streamlit as st
import requests
import os

# Page Config
st.set_page_config(
    page_title="CineMatch AI", 
    page_icon="🎬", 
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS for enhanced chat bubbles with theme support
st.markdown("""
    <style>
    /* Title styling - works in both themes */
    h1 {
        background: linear-gradient(90deg, #8b5cf6 0%, #a78bfa 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        text-align: center;
        margin-bottom: 0;
    }
    
    /* Caption styling */
    .stCaption {
        text-align: center;
        font-size: 1em;
        margin-bottom: 1rem;
    }
    
    /* Quick Starters section */
    h3 {
        color: #a78bfa;
        font-size: 1.1em;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
    }
    
    /* Container for starter buttons with flexbox */
    div[data-testid="stHorizontalBlock"]:has(.stButton) {
        display: flex !important;
        flex-wrap: wrap !important;
        gap: 10px !important;
        align-items: flex-start !important;
    }
    
    div[data-testid="stHorizontalBlock"]:has(.stButton) > div {
        flex: 0 0 auto !important;
        width: auto !important;
        min-width: 0 !important;
    }
    
    /* Streamlit buttons styling */
    .stButton {
        display: inline-block !important;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #8b5cf6 20%, #7c3aed 80%) !important;
        color: white !important;
        border: none !important;
        border-radius: 25px !important;
        padding: 12px 24px !important;
        font-size: 0.9em !important;
        font-weight: 500 !important;
        transition: all 0.2s ease !important;
        white-space: nowrap !important;
        height: auto !important;
        width: auto !important;
        line-height: 1.4 !important;
        text-align: center !important;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #7c3aed 20%, #6d28d9 80%) !important;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(139, 92, 246, 0.5);
    }
    
    /* Divider */
    hr {
        border: none;
        margin: 1.5rem 0;
    }
    
    /* Hide avatars for cleaner messenger look */
    .stChatMessage > div:first-child {
        display: none !important;
    }
    
    /* User message bubble - Right aligned */
    .stChatMessage[data-testid="user-message"] {
        background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
        border-radius: 18px 18px 4px 18px;
        padding: 12px 18px;
        margin: 8px 0 8px auto;
        max-width: 70%;
        box-shadow: 0 2px 12px rgba(139, 92, 246, 0.4);
        display: block;
        width: fit-content;
        margin-left: auto !important;
        margin-right: 10px !important;
    }
    
    .stChatMessage[data-testid="user-message"] > div {
        margin-left: auto;
    }
    
    .stChatMessage[data-testid="user-message"] p {
        color: white !important;
        font-weight: 500;
        margin: 0 !important;
        text-align: left;
    }
    
    /* Assistant message bubble - Left aligned - adapts to theme */
    .stChatMessage[data-testid="assistant-message"] {
        border-radius: 18px 18px 18px 4px;
        padding: 12px 18px;
        margin: 8px 10px 8px 0;
        max-width: 85%;
        display: block;
        width: fit-content;
    }
    
    /* Dark theme assistant bubble */
    [data-theme="dark"] .stChatMessage[data-testid="assistant-message"],
    .main .stChatMessage[data-testid="assistant-message"] {
        background: #1f1f1f;
        border: 1px solid #2a2a2a;
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.3);
    }
    
    [data-theme="dark"] .stChatMessage[data-testid="assistant-message"] p,
    .main .stChatMessage[data-testid="assistant-message"] p {
        color: #e5e7eb !important;
        margin: 0 !important;
    }
    
    /* Light theme assistant bubble */
    [data-theme="light"] .stChatMessage[data-testid="assistant-message"] {
        background: #f3f4f6;
        border: 1px solid #e5e7eb;
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
    }
    
    [data-theme="light"] .stChatMessage[data-testid="assistant-message"] p {
        color: #1f2937 !important;
        margin: 0 !important;
    }
    
    /* Keyword tags styling - Purple theme */
    code {
        background: linear-gradient(135deg, #8b5cf6 0%, #a78bfa 100%) !important;
        color: white !important;
        padding: 8px 16px !important;
        border-radius: 20px !important;
        font-weight: 600 !important;
        margin: 5px 5px 5px 0 !important;
        display: inline-block !important;
        box-shadow: 0 2px 8px rgba(139, 92, 246, 0.3) !important;
        font-size: 0.9em !important;
        white-space: nowrap !important;
        vertical-align: middle !important;
        line-height: 1.2 !important;
    }
    
    /* Chat input styling */
    .stChatInputContainer {
        padding-top: 15px;
        margin-top: 20px;
    }
    
    .stChatInput textarea {
        border-radius: 20px !important;
        padding: 12px 18px !important;
        font-size: 0.95em !important;
        transition: border-color 0.2s ease !important;
    }
    
    .stChatInput textarea:focus {
        border-color: #8b5cf6 !important;
        box-shadow: 0 0 0 2px rgba(139, 92, 246, 0.2) !important;
    }
    
    /* Spinner styling */
    .stSpinner > div {
        border-top-color: #8b5cf6 !important;
    }
    
    /* Markdown in messages - adapts to theme */
    .stChatMessage strong {
        color: #a78bfa;
        font-weight: 700;
    }
    
    .stChatMessage em {
        color: #8b5cf6;
        font-style: italic;
    }
    
    /* Horizontal rule in messages */
    .stChatMessage hr {
        border: none;
        margin: 12px 0;
    }
    
    /* Dark theme hr */
    [data-theme="dark"] .stChatMessage hr,
    .main .stChatMessage hr {
        border-top: 1px solid #3a3a3a;
    }
    
    /* Light theme hr */
    [data-theme="light"] .stChatMessage hr {
        border-top: 1px solid #e5e7eb;
    }
    
    /* Message container alignment fixes */
    .stChatMessage {
        margin-bottom: 12px !important;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🎬 CineMatch AI")
st.caption("Your personalized movie mood scout. Tell me how you feel or what your vibe is.")

# Quick Starter Prompts
STARTER_PROMPTS = [
    "Something funny and upbeat",
    "90s nostalgia",
    "Intense love stories",
    "Mind-bending thriller",
    "Cozy rainy day movie",
    "Epic adventure",
    "Dark comedy",
    "Feel-good family film"
]

# Display Quick Starters with horizontal layout
st.markdown("### Quick Starters")

# Use st.columns with all buttons to enable horizontal block
cols = st.columns(len(STARTER_PROMPTS))
for idx, prompt_text in enumerate(STARTER_PROMPTS):
    with cols[idx]:
        if st.button(prompt_text, key=f"starter_{idx}"):
            st.session_state.trigger_prompt = prompt_text
            st.rerun()

st.markdown("---")

# Backend API URL - 환경 변수에서 가져오기
BACKEND_URL = os.getenv(
    "BACKEND_URL",
    "https://movie-recommendation-chatbot-production.up.railway.app/recommend"
)

# Initialize Chat History
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! I'm your movie mood agent. Tell me about your situation (e.g., 'Rainy Friday night with coffee') and I'll find the perfect keywords for your movie hunt!"}
    ]

# Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Check if a starter prompt was triggered
if "trigger_prompt" in st.session_state:
    prompt = st.session_state.trigger_prompt
    del st.session_state.trigger_prompt
    
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate Response
    with st.chat_message("assistant"):
        with st.spinner("🎬 Analyzing your mood..."):
            try:
                response = requests.post(BACKEND_URL, json={"user_input": prompt}, timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    rec_keywords = data.get("recommended_keywords", [])
                    llm_keywords = data.get("llm_generated_keywords", [])
                    
                    if rec_keywords:
                        ai_message = f"Based on your vibe, I've analyzed the mood as: *{', '.join(llm_keywords)}*.\n\n"
                        ai_message += "Here are the **best matching keywords** from our library for your search:\n\n"
                        keyword_tags = " ".join([f"`{k}`" for k in rec_keywords])
                        ai_message += f"{keyword_tags}\n\n"
                        
                        st.markdown(ai_message)
                        st.session_state.messages.append({"role": "assistant", "content": ai_message})
                    else:
                        error_msg = "I understood your mood but couldn't find exact matches in our library. Could you try a different description?"
                        st.warning(error_msg)
                        st.session_state.messages.append({"role": "assistant", "content": error_msg})
                else:
                    st.error(f"⚠️ Backend returned status code {response.status_code}")
            except requests.exceptions.Timeout:
                st.error("⏱️ Request timed out. The backend might be slow. Please try again.")
            except requests.exceptions.ConnectionError:
                st.error("🔌 Cannot connect to backend. Please check if the service is running.")
            except Exception as e:
                st.error(f"❌ An error occurred: {str(e)}")

# User Input
if prompt := st.chat_input("E.g., Chill Sunday morning, intense psychological thriller vibe..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate Response
    with st.chat_message("assistant"):
        with st.spinner("🎬 Analyzing your mood..."):
            try:
                response = requests.post(BACKEND_URL, json={"user_input": prompt}, timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    rec_keywords = data.get("recommended_keywords", [])
                    llm_keywords = data.get("llm_generated_keywords", [])
                    
                    if rec_keywords:
                        # Formatting the response
                        ai_message = f"Based on your vibe, I've analyzed the mood as: *{', '.join(llm_keywords)}*.\n\n"
                        ai_message += "Here are the **best matching keywords** from our library for your search:\n\n"
                        
                        # Display keywords as badges/tags
                        keyword_tags = " ".join([f"`{k}`" for k in rec_keywords])
                        ai_message += f"{keyword_tags}\n\n"
                        
                        st.markdown(ai_message)
                        st.session_state.messages.append({"role": "assistant", "content": ai_message})
                    else:
                        error_msg = "I understood your mood but couldn't find exact matches in our library. Could you try a different description?"
                        st.warning(error_msg)
                        st.session_state.messages.append({"role": "assistant", "content": error_msg})
                else:
                    st.error(f"⚠️ Backend returned status code {response.status_code}")
            except requests.exceptions.Timeout:
                st.error("⏱️ Request timed out. The backend might be slow. Please try again.")
            except requests.exceptions.ConnectionError:
                st.error("🔌 Cannot connect to backend. Please check if the service is running.")
            except Exception as e:
                st.error(f"❌ An error occurred: {str(e)}")
