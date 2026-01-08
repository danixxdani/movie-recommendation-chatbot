import streamlit as st
import requests

# Page Config
st.set_page_config(page_title="CineMatch AI", page_icon="🎬", layout="centered")

# Custom CSS for enhanced chat bubbles
st.markdown("""
    <style>
    /* Main container styling */
    .main {
        background: #0f0f0f;
    }
    
    /* Title styling */
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
        color: #9ca3af;
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
    
    /* Force equal column widths */
    div[data-testid="column"] {
        flex: 1 1 0 !important;
        min-width: 0 !important;
        padding: 0 5px !important;
    }
    
    /* Streamlit buttons styling */
    .stButton {
        width: 100% !important;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #2a2a2a 0%, #1f1f1f 100%) !important;
        color: #a78bfa !important;
        border: 1px solid #3a3a3a !important;
        border-radius: 20px !important;
        padding: 12px 16px !important;
        font-size: 0.88em !important;
        font-weight: 500 !important;
        transition: all 0.2s ease !important;
        white-space: normal !important;
        height: auto !important;
        min-height: 50px !important;
        width: 100% !important;
        line-height: 1.4 !important;
        text-align: center !important;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
        color: white;
        border-color: #8b5cf6;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(139, 92, 246, 0.4);
    }
    
    /* Divider */
    hr {
        border: none;
        border-top: 1px solid #2a2a2a;
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
    
    /* Assistant message bubble - Left aligned */
    .stChatMessage[data-testid="assistant-message"] {
        background: #1f1f1f;
        border-radius: 18px 18px 18px 4px;
        padding: 12px 18px;
        margin: 8px 10px 8px 0;
        max-width: 85%;
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.3);
        display: block;
        width: fit-content;
        border: 1px solid #2a2a2a;
    }
    
    .stChatMessage[data-testid="assistant-message"] p {
        color: #e5e7eb !important;
        margin: 0 !important;
    }
    
    /* Keyword tags styling - Purple theme */
    code {
        background: linear-gradient(135deg, #8b5cf6 0%, #a78bfa 100%) !important;
        color: white !important;
        padding: 6px 14px !important;
        border-radius: 20px !important;
        font-weight: 600 !important;
        margin: 4px !important;
        display: inline-block !important;
        box-shadow: 0 2px 8px rgba(139, 92, 246, 0.3);
        font-size: 0.9em !important;
    }
    
    /* Chat input styling */
    .stChatInputContainer {
        border-top: 1px solid #2a2a2a;
        padding-top: 15px;
        margin-top: 20px;
        background: #0f0f0f;
    }
    
    .stChatInput textarea {
        background: #1f1f1f !important;
        color: white !important;
        border: 2px solid #3a3a3a !important;
        border-radius: 20px !important;
        padding: 12px 18px !important;
        font-size: 0.95em !important;
        transition: border-color 0.2s ease !important;
    }
    
    .stChatInput textarea:focus {
        border-color: #8b5cf6 !important;
        box-shadow: none !important;
        outline: none !important;
    }
    
    /* Spinner styling */
    .stSpinner > div {
        border-top-color: #8b5cf6 !important;
    }
    
    /* Warning and error styling */
    .stWarning {
        background: #292524;
        border-radius: 12px;
        border-left: 4px solid #f59e0b;
        color: #fbbf24;
    }
    
    .stError {
        background: #292524;
        border-radius: 12px;
        border-left: 4px solid #ef4444;
        color: #fca5a5;
    }
    
    /* Markdown in messages */
    .stChatMessage strong {
        color: #c4b5fd;
        font-weight: 700;
    }
    
    .stChatMessage em {
        color: #a78bfa;
        font-style: italic;
    }
    
    /* Horizontal rule in messages */
    .stChatMessage hr {
        border: none;
        border-top: 1px solid #3a3a3a;
        margin: 12px 0;
    }
    
    /* Scrollbar styling */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #1f1f1f;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #8b5cf6;
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #7c3aed;
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

# Display Quick Starters with equal-width columns
st.markdown("### 🎯 Quick Starters")

# First row - 4 buttons
col1, col2, col3, col4 = st.columns(4)
with col1:
    if st.button(STARTER_PROMPTS[0], key="starter_0"):
        st.session_state.trigger_prompt = STARTER_PROMPTS[0]
        st.rerun()
with col2:
    if st.button(STARTER_PROMPTS[1], key="starter_1"):
        st.session_state.trigger_prompt = STARTER_PROMPTS[1]
        st.rerun()
with col3:
    if st.button(STARTER_PROMPTS[2], key="starter_2"):
        st.session_state.trigger_prompt = STARTER_PROMPTS[2]
        st.rerun()
with col4:
    if st.button(STARTER_PROMPTS[3], key="starter_3"):
        st.session_state.trigger_prompt = STARTER_PROMPTS[3]
        st.rerun()

# Second row - 4 buttons
col1, col2, col3, col4 = st.columns(4)
with col1:
    if st.button(STARTER_PROMPTS[4], key="starter_4"):
        st.session_state.trigger_prompt = STARTER_PROMPTS[4]
        st.rerun()
with col2:
    if st.button(STARTER_PROMPTS[5], key="starter_5"):
        st.session_state.trigger_prompt = STARTER_PROMPTS[5]
        st.rerun()
with col3:
    if st.button(STARTER_PROMPTS[6], key="starter_6"):
        st.session_state.trigger_prompt = STARTER_PROMPTS[6]
        st.rerun()
with col4:
    if st.button(STARTER_PROMPTS[7], key="starter_7"):
        st.session_state.trigger_prompt = STARTER_PROMPTS[7]
        st.rerun()

st.markdown("---")

# Backend API URL
BACKEND_URL = "http://localhost:8000/recommend"

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
        with st.spinner("Analyzing your mood..."):
            try:
                response = requests.post(BACKEND_URL, json={"user_input": prompt})
                
                if response.status_code == 200:
                    data = response.json()
                    rec_keywords = data.get("recommended_keywords", [])
                    llm_keywords = data.get("llm_generated_keywords", [])
                    
                    if rec_keywords:
                        ai_message = f"Based on your vibe, I've analyzed the mood as: *{', '.join(llm_keywords)}*.\n\n"
                        ai_message += "Here are the **best matching keywords** from our library for your search:\n\n"
                        keyword_tags = " ".join([f"`{k}`" for k in rec_keywords])
                        ai_message += f"{keyword_tags}\n\n"
                        ai_message += "--- \n"
                        ai_message += "💡 **Pro-tip:** You can use these keywords on Netflix or Google to find specific titles!"
                        
                        st.markdown(ai_message)
                        st.session_state.messages.append({"role": "assistant", "content": ai_message})
                    else:
                        error_msg = "I understood your mood but couldn't find exact matches in our library. Could you try a different description?"
                        st.warning(error_msg)
                        st.session_state.messages.append({"role": "assistant", "content": error_msg})
                else:
                    st.error("Oops! Something went wrong with my brain (Backend Error).")
            except Exception as e:
                st.error("Connection failed. Is the backend server running?")

# User Input
if prompt := st.chat_input("E.g., Chill Sunday morning, intense psychological thriller vibe..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate Response
    with st.chat_message("assistant"):
        with st.spinner("Analyzing your mood..."):
            try:
                response = requests.post(BACKEND_URL, json={"user_input": prompt})
                
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
                        ai_message += "--- \n"
                        ai_message += "💡 **Pro-tip:** You can use these keywords on Netflix or Google to find specific titles!"
                        
                        st.markdown(ai_message)
                        st.session_state.messages.append({"role": "assistant", "content": ai_message})
                    else:
                        error_msg = "I understood your mood but couldn't find exact matches in our library. Could you try a different description?"
                        st.warning(error_msg)
                        st.session_state.messages.append({"role": "assistant", "content": error_msg})
                else:
                    st.error("Oops! Something went wrong with my brain (Backend Error).")
            except Exception as e:
                st.error("Connection failed. Is the backend server running?")