import streamlit as st
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from database import save_chat_message, get_chat_history
from openai import OpenAI

# ── Auth Guard ────────────────────────────────────────────────────────────────
if "authenticated" not in st.session_state or not st.session_state.authenticated:
    st.warning("Please sign in to access this page.")
    st.stop()

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="AI Chatbot — MindWave", page_icon="💬", layout="wide")

# ── Shared CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:ital,wght@0,300;0,400;0,500;1,300&display=swap');
:root {
    --bg:#0a0a0f; --surface:#12121a; --surface2:#1a1a28;
    --border:#2a2a40; --accent:#7c6aff; --accent2:#ff6a9e;
    --accent3:#6affda; --text:#e8e8f0; --muted:#6b6b8a;
}
html,body,[data-testid="stAppViewContainer"]{background:var(--bg)!important;color:var(--text)!important;font-family:'DM Sans',sans-serif!important;}
[data-testid="stSidebar"]{background:var(--surface)!important;border-right:1px solid var(--border)!important;}
#MainMenu,footer,header{visibility:hidden;}
h1,h2,h3{font-family:'Syne',sans-serif!important;}
[data-testid="stButton"]>button{background:linear-gradient(135deg,var(--accent),var(--accent2))!important;color:white!important;border:none!important;border-radius:10px!important;font-family:'Syne',sans-serif!important;font-weight:600!important;}
[data-testid="stButton"]>button:hover{transform:translateY(-2px)!important;box-shadow:0 8px 25px rgba(124,106,255,0.35)!important;}
[data-testid="stSelectbox"]>div>div{background:var(--surface2)!important;border:1px solid var(--border)!important;border-radius:10px!important;color:var(--text)!important;}
.stChatMessage{background:var(--surface)!important;border:1px solid var(--border)!important;border-radius:16px!important;}
[data-testid="stChatInput"]{background:var(--surface2)!important;border:1px solid var(--border)!important;border-radius:16px!important;}
.grad{background:linear-gradient(135deg,var(--accent),var(--accent2));-webkit-background-clip:text;-webkit-text-fill-color:transparent;}
.model-badge{display:inline-block;background:var(--surface2);border:1px solid var(--border);border-radius:50px;padding:0.2rem 0.8rem;font-size:0.78rem;color:var(--muted);font-family:'Syne',sans-serif;}
</style>
""", unsafe_allow_html=True)

# ── Config ────────────────────────────────────────────────────────────────────
API_KEY = "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"
client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=API_KEY)

MODELS = {
    "🦙 Llama 3.1 8B (Fast)": "meta-llama/llama-3.1-8b-instruct",
    "💎 Gemma 2 9B": "google/gemma-2-9b-it",
    "🤖 DeepSeek Chat": "deepseek/deepseek-chat"
}

PERSONAS = {
    "🧠 Emotional Support": (
        "You are MindWave, a warm, empathetic AI emotional support companion. "
        "You listen deeply, validate feelings without judgment, and gently offer perspectives. "
        "You never dismiss emotions, always ask thoughtful follow-up questions, and suggest "
        "professional help when appropriate. Keep responses concise but heartfelt."
    ),
    "🤝 Life Coach": (
        "You are an experienced life coach. You help users set goals, identify obstacles, "
        "and take actionable steps. You're motivating, direct, and solution-focused while "
        "remaining empathetic. You ask powerful questions that help users discover their own answers."
    ),
    "💡 General Assistant": "You are a helpful, knowledgeable, and friendly AI assistant.",
    "🧘 Mindfulness Guide": (
        "You are a mindfulness and meditation guide. You help users with breathing exercises, "
        "grounding techniques, and mindfulness practices. You speak calmly and gently, "
        "always bringing the user back to the present moment."
    ),
}

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    user = st.session_state.user
    st.markdown(f"""
    <div style="background:var(--surface2);border:1px solid var(--border);border-radius:50px;
                padding:0.5rem 1rem;display:flex;align-items:center;gap:0.6rem;margin-bottom:1.5rem">
        <span style="font-size:1.3rem">👤</span>
        <div>
            <div style="font-family:'Syne',sans-serif;font-weight:600;font-size:0.9rem">{user['username']}</div>
            <div style="font-size:0.75rem;color:var(--muted)">{user['email']}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='font-family:Syne,sans-serif;font-size:0.7rem;text-transform:uppercase;letter-spacing:0.12em;color:var(--muted);margin-bottom:0.5rem'>Navigation</div>", unsafe_allow_html=True)
    st.page_link("main.py", label="🏠 Home")
    st.page_link("pages/1_💬_Chatbot.py", label="💬 AI Chatbot")
    st.page_link("pages/2_🎵_Music_Recommender.py", label="🎵 Music Recommender")
    st.page_link("pages/3_😊_Emotion_Detector.py", label="😊 Emotion Detector")

    st.markdown("<hr style='border-color:var(--border);margin:1rem 0'>", unsafe_allow_html=True)
    st.markdown("<div style='font-family:Syne,sans-serif;font-size:0.7rem;text-transform:uppercase;letter-spacing:0.12em;color:var(--muted);margin-bottom:0.5rem'>Settings</div>", unsafe_allow_html=True)

    selected_model_name = st.selectbox("AI Model", list(MODELS.keys()))
    selected_persona_name = st.selectbox("Persona", list(PERSONAS.keys()))
    selected_model = MODELS[selected_model_name]
    system_prompt = PERSONAS[selected_persona_name]

    st.markdown("<hr style='border-color:var(--border);margin:1rem 0'>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🧹 Clear", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
    with col2:
        if st.button("Sign Out", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.user = None
            st.rerun()

# ── Session State ─────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    # Load from DB
    history = get_chat_history(st.session_state.user["id"])
    st.session_state.messages = history if history else []

if "last_persona" not in st.session_state:
    st.session_state.last_persona = selected_persona_name

# Reset messages if persona changed
if st.session_state.last_persona != selected_persona_name:
    st.session_state.messages = []
    st.session_state.last_persona = selected_persona_name

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown(f"""
<h1 style="font-family:'Syne',sans-serif;font-size:2rem;font-weight:800;margin-bottom:0.2rem">
    💬 AI <span class="grad">Chatbot</span>
</h1>
<div style="display:flex;align-items:center;gap:0.75rem;margin-bottom:1.5rem">
    <span class="model-badge">{selected_model_name}</span>
    <span class="model-badge">{selected_persona_name}</span>
</div>
""", unsafe_allow_html=True)

# ── Chat Display ──────────────────────────────────────────────────────────────
if not st.session_state.messages:
    st.markdown(f"""
    <div style="text-align:center;padding:3rem 1rem;color:var(--muted)">
        <div style="font-size:3rem;margin-bottom:1rem">🧠</div>
        <div style="font-family:'Syne',sans-serif;font-size:1.1rem;font-weight:600;
                    color:var(--text);margin-bottom:0.5rem">
            Start a conversation
        </div>
        <div style="font-size:0.9rem">
            You're chatting with the <strong>{selected_persona_name}</strong> persona.<br>
            Type anything to begin.
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

# ── Input ─────────────────────────────────────────────────────────────────────
user_input = st.chat_input("Share what's on your mind...")

if user_input:
    st.chat_message("user").write(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})
    save_chat_message(st.session_state.user["id"], "user", user_input)

    api_messages = [{"role": "system", "content": system_prompt}] + st.session_state.messages

    try:
        with st.spinner(""):
            response = client.chat.completions.create(
                model=selected_model,
                messages=api_messages
            )
        bot_reply = response.choices[0].message.content
    except Exception as e:
        bot_reply = f"⚠️ Something went wrong: {str(e)}"

    st.chat_message("assistant").write(bot_reply)
    st.session_state.messages.append({"role": "assistant", "content": bot_reply})
    save_chat_message(st.session_state.user["id"], "assistant", bot_reply)