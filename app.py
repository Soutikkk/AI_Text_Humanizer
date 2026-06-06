import streamlit as st
import streamlit.components.v1 as components
import json
from humanizer import humanize_text, _nltk_available

# Page configurations
st.set_page_config(
    page_title="AI Text Humanizer - Streamline & Soften AI Writing",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject Custom CSS for visual excellence (dark glassmorphism theme, modern typography)
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap');

/* Font application */
html, body, [class*="css"], .stMarkdown {
    font-family: 'Outfit', sans-serif;
}

/* Background overlay */
.main {
    background: radial-gradient(circle at 10% 20%, rgb(18, 12, 33) 0%, rgb(10, 6, 21) 90%);
    color: #e5def0;
}

/* Glassmorphism containers */
.glass-card {
    background: rgba(255, 255, 255, 0.02);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 16px;
    padding: 25px;
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);
    margin-bottom: 25px;
}

/* Beautiful Title Gradient */
.app-title {
    background: linear-gradient(90deg, #bfa1ff, #7f00ff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-weight: 800;
    font-size: 3rem;
    margin-bottom: 5px;
    text-align: center;
}

.app-subtitle {
    font-size: 1.15rem;
    color: #a395b8;
    text-align: center;
    margin-bottom: 35px;
}

/* Styled text area */
.stTextArea textarea {
    background-color: rgba(25, 15, 45, 0.4) !important;
    color: #f1eef8 !important;
    border: 1px solid rgba(138, 43, 226, 0.25) !important;
    border-radius: 12px !important;
    font-size: 15px !important;
    transition: all 0.3s ease !important;
}

.stTextArea textarea:focus {
    border-color: rgba(138, 43, 226, 0.7) !important;
    box-shadow: 0 0 12px rgba(138, 43, 226, 0.3) !important;
}

/* Streamlit button custom styles */
div.stButton > button:first-child {
    background: linear-gradient(135deg, #7f00ff, #5100a8) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 12px 30px !important;
    font-size: 16px !important;
    font-weight: 600 !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 15px rgba(127, 0, 255, 0.4) !important;
    width: 100% !important;
}

div.stButton > button:first-child:hover {
    background: linear-gradient(135deg, #9400ff, #6400d1) !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px rgba(127, 0, 255, 0.6) !important;
}

div.stButton > button:first-child:active {
    transform: translateY(0) !important;
}

/* Metrics label */
.metric-box {
    display: inline-block;
    background: rgba(138, 43, 226, 0.1);
    border: 1px solid rgba(138, 43, 226, 0.2);
    border-radius: 8px;
    padding: 5px 12px;
    margin-right: 10px;
    font-size: 0.85rem;
    font-weight: 500;
}

</style>
""", unsafe_allow_html=True)

# Helper function to render a secure HTML/JS copy to clipboard button
def copy_button_js(text_to_copy):
    html_code = f"""
    <button id="copy-btn" style="
        background: linear-gradient(135deg, #8a2be2, #4b0082);
        color: white;
        border: none;
        padding: 8px 16px;
        border-radius: 8px;
        cursor: pointer;
        font-weight: 600;
        font-family: sans-serif;
        font-size: 14px;
        box-shadow: 0 4px 10px rgba(138, 43, 226, 0.3);
        transition: all 0.2s ease;
        margin-bottom: 5px;
    ">📋 Copy to Clipboard</button>
    <script>
    document.getElementById('copy-btn').addEventListener('click', function() {{
        const el = document.createElement('textarea');
        el.value = {json.dumps(text_to_copy)};
        document.body.appendChild(el);
        el.select();
        document.execCommand('copy');
        document.body.removeChild(el);
        
        this.innerHTML = "✔ Copied!";
        this.style.background = "#2E7D32";
        this.style.boxShadow = "0 4px 10px rgba(46, 125, 50, 0.3)";
        setTimeout(() => {{
            this.innerHTML = "📋 Copy to Clipboard";
            this.style.background = "linear-gradient(135deg, #8a2be2, #4b0082)";
            this.style.boxShadow = "0 4px 10px rgba(138, 43, 226, 0.3)";
        }}, 2000);
    }});
    </script>
    """
    components.html(html_code, height=45)

# Page Layout
st.markdown("<h1 class='app-title'>✨ AI Text Humanizer</h1>", unsafe_allow_html=True)
st.markdown("<p class='app-subtitle'>Transform static, predictable machine copy into natural, conversational, humanized prose.</p>", unsafe_allow_html=True)

# Sidebar settings
with st.sidebar:
    st.markdown("### ⚙ Configuration")
    
    # Engine Selection
    engine = st.selectbox(
        "Processing Engine",
        options=["Local Heuristics", "OpenAI GPT Engine"],
        help="Local Heuristics runs offline. OpenAI GPT Engine delivers highly advanced rephrasing."
    )
    
    # Conditionally show OpenAI configuration
    openai_key = ""
    if engine == "OpenAI GPT Engine":
        openai_key = st.text_input(
            "OpenAI API Key",
            type="password",
            placeholder="sk-...",
            help="Your key is processed client-side and never saved."
        )
        if not openai_key:
            st.warning("Please provide your API key to run OpenAI humanization.")

    # Strength slider
    strength = st.select_slider(
        "Humanization Strength",
        options=["Low", "Medium", "High"],
        value="Medium",
        help="Low: minimal rephrasing. Medium: balanced flow and synonym replacements. High: maximum flow variations and conversational elements."
    )

    # Informational system diagnostics
    st.markdown("---")
    st.markdown("### 💻 Local Engine Diagnostics")
    if _nltk_available:
        st.success("NLTK WordNet: Connected")
    else:
        st.info("NLTK WordNet: Fallback Mode Active (Using built-in dictionaries)")

# Layout split
col1, col2 = st.columns(2)

with col1:
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.subheader("📝 Original AI-Generated Text")
    input_text = st.text_area(
        "Paste your text here:",
        height=320,
        placeholder="e.g., In conclusion, utilizing AI tools is important to note for optimization of workflows...",
        label_visibility="collapsed"
    )
    
    # Stats for input
    word_count_in = len(input_text.split())
    char_count_in = len(input_text)
    st.markdown(
        f"<span class='metric-box'>Words: {word_count_in}</span><span class='metric-box'>Characters: {char_count_in}</span>",
        unsafe_allow_html=True
    )
    st.markdown("</div>", unsafe_allow_html=True)

    # Process Button
    process_btn = st.button("✨ Humanize Text")

with col2:
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.subheader("🌿 Humanized Output Text")
    
    output_container = st.empty()
    
    # Processing trigger
    humanized_result = ""
    if process_btn:
        if not input_text.strip():
            st.error("Please enter some text in the input box first.")
        else:
            method_key = "openai" if engine == "OpenAI GPT Engine" else "local"
            
            if method_key == "openai" and not openai_key:
                st.error("API Key is missing for the OpenAI engine. Please enter it in the sidebar.")
            else:
                with st.spinner("Smoothing transitions and replacing robotic phrases..."):
                    try:
                        humanized_result = humanize_text(
                            input_text, 
                            strength=strength, 
                            method=method_key, 
                            openai_api_key=openai_key
                        )
                        st.session_state["humanized_text"] = humanized_result
                    except Exception as e:
                        st.error(f"Error during humanization: {e}")

    # Display result from session state if available
    saved_output = st.session_state.get("humanized_text", "")
    if saved_output:
        st.code(saved_output, language="text")
        
        # Stats for output
        word_count_out = len(saved_output.split())
        char_count_out = len(saved_output)
        
        # Word changes calculation
        word_diff = word_count_out - word_count_in
        diff_pct = (word_diff / word_count_in) * 100 if word_count_in > 0 else 0
        
        st.markdown(
            f"<span class='metric-box'>Words: {word_count_out} ({word_diff:+.0f} / {diff_pct:+.1f}%)</span>"
            f"<span class='metric-box'>Characters: {char_count_out}</span>",
            unsafe_allow_html=True
        )
        
        # Action layout
        btn_col1, btn_col2 = st.columns([1, 1])
        with btn_col1:
            copy_button_js(saved_output)
            
        with btn_col2:
            st.download_button(
                label="💾 Export to .txt File",
                data=saved_output,
                file_name="humanized_text.txt",
                mime="text/plain",
                help="Download your humanized text directly as a plain text file."
            )
    else:
        st.info("Humanized output will appear here after processing.")
    st.markdown("</div>", unsafe_allow_html=True)
