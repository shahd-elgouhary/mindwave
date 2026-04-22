import streamlit as st
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from database import log_emotion
import torch
import torch.nn as nn
import torchvision.transforms as T
import torchvision.models as models
from PIL import Image
import numpy as np

# ── Auth Guard ────────────────────────────────────────────────────────────────
if "authenticated" not in st.session_state or not st.session_state.authenticated:
    st.warning("Please sign in to access this page.")
    st.stop()

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="Emotion Detector — MindWave", page_icon="😊", layout="wide")

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');
:root{--bg:#0a0a0f;--surface:#12121a;--surface2:#1a1a28;--border:#2a2a40;--accent:#7c6aff;--accent2:#ff6a9e;--accent3:#6affda;--text:#e8e8f0;--muted:#6b6b8a;}
html,body,[data-testid="stAppViewContainer"]{background:var(--bg)!important;color:var(--text)!important;font-family:'DM Sans',sans-serif!important;}
[data-testid="stSidebar"]{background:var(--surface)!important;border-right:1px solid var(--border)!important;}
#MainMenu,footer,header{visibility:hidden;}
h1,h2,h3{font-family:'Syne',sans-serif!important;}
[data-testid="stButton"]>button{background:linear-gradient(135deg,var(--accent),var(--accent2))!important;color:white!important;border:none!important;border-radius:10px!important;font-family:'Syne',sans-serif!important;font-weight:600!important;transition:all 0.25s!important;}
[data-testid="stButton"]>button:hover{transform:translateY(-2px)!important;box-shadow:0 8px 25px rgba(124,106,255,0.35)!important;}
[data-testid="stTabs"] [role="tab"]{font-family:'Syne',sans-serif!important;color:var(--muted)!important;}
[data-testid="stTabs"] [aria-selected="true"]{color:var(--accent)!important;}
.grad{background:linear-gradient(135deg,var(--accent),var(--accent2));-webkit-background-clip:text;-webkit-text-fill-color:transparent;}
.emotion-result{background:var(--surface);border:1px solid var(--border);border-radius:20px;padding:2rem;text-align:center;margin-top:1rem;}
.emotion-icon{font-size:4rem;margin-bottom:0.5rem;}
.emotion-label{font-family:'Syne',sans-serif;font-size:1.8rem;font-weight:800;}
.confidence{color:var(--muted);font-size:0.9rem;margin-top:0.25rem;}
.action-card{background:var(--surface2);border:1px solid var(--border);border-radius:14px;padding:1rem 1.25rem;margin-top:0.75rem;cursor:pointer;transition:all 0.2s;}
.action-card:hover{border-color:var(--accent);}
</style>
""", unsafe_allow_html=True)

# ── Emotion Config ────────────────────────────────────────────────────────────
LABELS = ["anger", "contempt", "disgust", "fear", "happy", "sadness", "surprise"]

EMOTION_CONFIG = {
    "happy":    {"icon": "😊", "color": "#fbbf24", "msg": "You're radiating joy! Keep that energy going.",       "music_mood": "upbeat & energetic"},
    "sadness":  {"icon": "😢", "color": "#60a5fa", "msg": "It's okay to feel sad. Music can help you heal.",     "music_mood": "comforting & gentle"},
    "anger":    {"icon": "😠", "color": "#f87171", "msg": "Take a breath. Let music help release that tension.",  "music_mood": "intense & cathartic"},
    "fear":     {"icon": "😨", "color": "#a78bfa", "msg": "You're safe here. Let's find something soothing.",    "music_mood": "calm & reassuring"},
    "surprise": {"icon": "😲", "color": "#34d399", "msg": "Something caught you off guard! Ride that wave.",     "music_mood": "dynamic & exciting"},
    "disgust":  {"icon": "🤢", "color": "#6b7280", "msg": "Let's shift your vibe with some chill music.",        "music_mood": "relaxed & mellow"},
    "contempt": {"icon": "😒", "color": "#f59e0b", "msg": "Channel that confidence into something powerful.",    "music_mood": "empowering & bold"},
}

# ── Model ─────────────────────────────────────────────────────────────────────
@st.cache_resource
def load_model():
    model_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "best_phase2.pth")
    model = models.efficientnet_b3(weights=None)
    model.classifier[1] = nn.Linear(1536, 7)
    model.load_state_dict(torch.load(model_path, map_location="cpu"))
    model.eval()
    return model

transform = T.Compose([
    T.Resize((300, 300)),
    T.ToTensor(),
    T.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])

def predict(img):
    img = img.convert("RGB")
    x = transform(img).unsqueeze(0)
    with torch.no_grad():
        out = load_model()(x)
        probs = torch.softmax(out, dim=1)[0].numpy()
    return probs

def show_result(probs):
    emotion = LABELS[np.argmax(probs)]
    confidence = float(np.max(probs))
    cfg = EMOTION_CONFIG.get(emotion, {"icon": "🧠", "color": "#7c6aff", "msg": "", "music_mood": "varied"})

    # Save to session & DB
    st.session_state.detected_emotion = emotion
    log_emotion(st.session_state.user["id"], emotion, confidence)

    # Result card
    st.markdown(f"""
    <div class="emotion-result">
        <div class="emotion-icon">{cfg['icon']}</div>
        <div class="emotion-label" style="color:{cfg['color']}">{emotion.upper()}</div>
        <div class="confidence">{round(confidence * 100, 1)}% confidence</div>
        <div style="color:var(--muted);font-size:0.9rem;margin-top:1rem;max-width:320px;
                    margin-left:auto;margin-right:auto;line-height:1.6">
            {cfg['msg']}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Probability bars
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<div style='font-family:Syne,sans-serif;font-weight:600;font-size:0.9rem;margin-bottom:0.5rem'>Emotion Breakdown</div>", unsafe_allow_html=True)
    chart_data = {LABELS[i]: float(probs[i]) for i in range(7)}
    st.bar_chart(chart_data)

    # Go to music button
    st.markdown(f"""
    <div class="action-card">
        <div style="font-family:'Syne',sans-serif;font-weight:600;font-size:0.9rem">
            🎵 Get music for your mood
        </div>
        <div style="color:var(--muted);font-size:0.82rem;margin-top:0.25rem">
            We'll recommend <strong>{cfg['music_mood']}</strong> songs based on your emotion.
            Head to the Music Recommender page →
        </div>
    </div>
    """, unsafe_allow_html=True)

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
    if st.button("Sign Out", use_container_width=True):
        st.session_state.authenticated = False
        st.session_state.user = None
        st.rerun()

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<h1 style="font-family:'Syne',sans-serif;font-size:2rem;font-weight:800;margin-bottom:0.25rem">
    😊 Emotion <span class="grad">Detector</span>
</h1>
<p style="color:var(--muted);font-size:0.95rem;margin-bottom:1.5rem">
    Upload a photo or use your webcam — we'll detect your emotion and suggest music to match.
</p>
""", unsafe_allow_html=True)

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2 = st.tabs(["📁 Upload Image", "📷 Webcam"])

with tab1:
    uploaded = st.file_uploader("Upload a face photo", type=["jpg", "jpeg", "png"], label_visibility="collapsed")
    if uploaded:
        col1, col2 = st.columns([1, 1])
        with col1:
            img = Image.open(uploaded)
            st.image(img, caption="Your photo", use_container_width=True)
        with col2:
            if st.button("🔍 Detect Emotion", key="upload_predict", use_container_width=True):
                with st.spinner("Analyzing your expression..."):
                    try:
                        probs = predict(img)
                        show_result(probs)
                    except Exception as e:
                        st.error(f"Model not loaded or error: {e}\n\nMake sure best_phase2.pth is in the project root.")

with tab2:
    camera_img = st.camera_input("Take a photo", label_visibility="collapsed")
    if camera_img:
        col1, col2 = st.columns([1, 1])
        with col1:
            img = Image.open(camera_img)
            st.image(img, caption="Captured photo", use_container_width=True)
        with col2:
            if st.button("🔍 Detect Emotion", key="webcam_predict", use_container_width=True):
                with st.spinner("Analyzing your expression..."):
                    try:
                        probs = predict(img)
                        show_result(probs)
                    except Exception as e:
                        st.error(f"Model not loaded or error: {e}\n\nMake sure best_phase2.pth is in the project root.")