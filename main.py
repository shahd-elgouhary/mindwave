import streamlit as st
from database import init_db, login_user, register_user
import re

# ── Init DB ──────────────────────────────────────────────────────────────────
init_db()

# ── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="MindWave — Emotional Support AI",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Global CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:ital,wght@0,300;0,400;0,500;1,300&display=swap');

/* ── Root Variables ── */
:root {
    --bg:        #0a0a0f;
    --surface:   #12121a;
    --surface2:  #1a1a28;
    --border:    #2a2a40;
    --accent:    #7c6aff;
    --accent2:   #ff6a9e;
    --accent3:   #6affda;
    --text:      #e8e8f0;
    --muted:     #6b6b8a;
    --success:   #4ade80;
    --error:     #f87171;
}

/* ── Base ── */
html, body, [data-testid="stAppViewContainer"] {
    background: var(--bg) !important;
    color: var(--text) !important;
    font-family: 'DM Sans', sans-serif !important;
}

[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
}

/* ── Hide default Streamlit elements ── */
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stDecoration"] { display: none; }

/* ── Headings ── */
h1, h2, h3, .syne { font-family: 'Syne', sans-serif !important; }

/* ── Inputs ── */
[data-testid="stTextInput"] input,
[data-testid="stTextInput"] input:focus {
    background: var(--surface2) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    color: var(--text) !important;
    font-family: 'DM Sans', sans-serif !important;
}
[data-testid="stTextInput"] input:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px rgba(124,106,255,0.15) !important;
}

/* ── Buttons ── */
[data-testid="stButton"] > button {
    background: linear-gradient(135deg, var(--accent), var(--accent2)) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 600 !important;
    letter-spacing: 0.03em !important;
    padding: 0.6rem 1.8rem !important;
    transition: all 0.25s ease !important;
}
[data-testid="stButton"] > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 25px rgba(124,106,255,0.35) !important;
}

/* ── Selectbox ── */
[data-testid="stSelectbox"] > div > div {
    background: var(--surface2) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    color: var(--text) !important;
}

/* ── Tabs ── */
[data-testid="stTabs"] [role="tab"] {
    font-family: 'Syne', sans-serif !important;
    color: var(--muted) !important;
}
[data-testid="stTabs"] [aria-selected="true"] {
    color: var(--accent) !important;
    border-bottom-color: var(--accent) !important;
}

/* ── Cards ── */
.card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 1.5rem;
    margin-bottom: 1rem;
    transition: border-color 0.2s;
}
.card:hover { border-color: var(--accent); }

/* ── Auth container ── */
.auth-wrap {
    max-width: 440px;
    margin: 4rem auto;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 24px;
    padding: 2.5rem 2.5rem 2rem;
}
.auth-logo {
    font-family: 'Syne', sans-serif;
    font-size: 2rem;
    font-weight: 800;
    background: linear-gradient(135deg, var(--accent), var(--accent2));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-align: center;
    margin-bottom: 0.25rem;
}
.auth-sub {
    text-align: center;
    color: var(--muted);
    font-size: 0.9rem;
    margin-bottom: 2rem;
}
.auth-divider {
    border: none;
    border-top: 1px solid var(--border);
    margin: 1.5rem 0;
}

/* ── Sidebar user pill ── */
.user-pill {
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 50px;
    padding: 0.5rem 1rem;
    display: flex;
    align-items: center;
    gap: 0.6rem;
    margin-bottom: 1.5rem;
}
.user-pill-name {
    font-family: 'Syne', sans-serif;
    font-weight: 600;
    font-size: 0.9rem;
}

/* ── Alert overrides ── */
[data-testid="stAlert"] {
    border-radius: 12px !important;
    border: none !important;
}

/* ── Gradient text utility ── */
.grad { 
    background: linear-gradient(135deg, var(--accent), var(--accent2));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.grad-teal {
    background: linear-gradient(135deg, var(--accent3), var(--accent));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

/* ── Noise overlay ── */
body::before {
    content: '';
    position: fixed;
    inset: 0;
    background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)' opacity='0.03'/%3E%3C/svg%3E");
    pointer-events: none;
    z-index: 9999;
    opacity: 0.4;
}

/* ── Glow orbs ── */
.orb {
    position: fixed;
    border-radius: 50%;
    filter: blur(120px);
    pointer-events: none;
    z-index: 0;
}
.orb-1 { width: 400px; height: 400px; background: rgba(124,106,255,0.08); top: -100px; right: -100px; }
.orb-2 { width: 300px; height: 300px; background: rgba(255,106,158,0.06); bottom: 100px; left: -80px; }
</style>

<div class="orb orb-1"></div>
<div class="orb orb-2"></div>
""", unsafe_allow_html=True)


# ── Session State Defaults ────────────────────────────────────────────────────
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user" not in st.session_state:
    st.session_state.user = None
if "auth_tab" not in st.session_state:
    st.session_state.auth_tab = "login"


# ── Auth UI ───────────────────────────────────────────────────────────────────
def validate_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

def show_auth():
    st.markdown("""
    <div class="auth-wrap">
        <div class="auth-logo">🧠 MindWave</div>
        <div class="auth-sub">Your AI-powered emotional support companion</div>
    </div>
    """, unsafe_allow_html=True)

    # Center the auth form
    _, col, _ = st.columns([1, 2, 1])
    with col:
        tab_login, tab_register = st.tabs(["Sign In", "Create Account"])

        # ── LOGIN ──
        with tab_login:
            st.markdown("<br>", unsafe_allow_html=True)
            username = st.text_input("Username", key="login_user", placeholder="your_username")
            password = st.text_input("Password", type="password", key="login_pass", placeholder="••••••••")
            st.markdown("<br>", unsafe_allow_html=True)

            if st.button("Sign In →", key="btn_login", use_container_width=True):
                if not username or not password:
                    st.error("Please fill in all fields.")
                else:
                    result = login_user(username, password)
                    if result["success"]:
                        st.session_state.authenticated = True
                        st.session_state.user = result["user"]
                        st.success(f"Welcome back, {result['user']['username']}! 👋")
                        st.rerun()
                    else:
                        st.error(result["message"])

        # ── REGISTER ──
        with tab_register:
            st.markdown("<br>", unsafe_allow_html=True)
            new_username = st.text_input("Username", key="reg_user", placeholder="choose_a_username")
            new_email = st.text_input("Email", key="reg_email", placeholder="you@example.com")
            new_pass = st.text_input("Password", type="password", key="reg_pass", placeholder="min. 6 characters")
            new_pass2 = st.text_input("Confirm Password", type="password", key="reg_pass2", placeholder="repeat password")
            st.markdown("<br>", unsafe_allow_html=True)

            if st.button("Create Account →", key="btn_register", use_container_width=True):
                if not all([new_username, new_email, new_pass, new_pass2]):
                    st.error("Please fill in all fields.")
                elif not validate_email(new_email):
                    st.error("Please enter a valid email address.")
                elif len(new_pass) < 6:
                    st.error("Password must be at least 6 characters.")
                elif new_pass != new_pass2:
                    st.error("Passwords do not match.")
                else:
                    result = register_user(new_username, new_email, new_pass)
                    if result["success"]:
                        st.success(result["message"] + " Please sign in.")
                    else:
                        st.error(result["message"])


# ── Sidebar (when authenticated) ─────────────────────────────────────────────
def show_sidebar():
    user = st.session_state.user
    with st.sidebar:
        st.markdown(f"""
        <div class="user-pill">
            <span style="font-size:1.3rem">👤</span>
            <div>
                <div class="user-pill-name">{user['username']}</div>
                <div style="font-size:0.75rem;color:var(--muted)">{user['email']}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div style="font-family:'Syne',sans-serif;font-size:0.7rem;
                    text-transform:uppercase;letter-spacing:0.12em;
                    color:var(--muted);margin-bottom:0.5rem;">Navigation</div>
        """, unsafe_allow_html=True)

        st.page_link("main.py", label="🏠 Home", icon=None)
        st.page_link("pages/1_💬_Chatbot.py", label="💬 AI Chatbot")
        st.page_link("pages/2_🎵_Music_Recommender.py", label="🎵 Music Recommender")
        st.page_link("pages/3_😊_Emotion_Detector.py", label="😊 Emotion Detector")

        st.markdown("<hr style='border-color:var(--border);margin:1.5rem 0'>", unsafe_allow_html=True)

        if st.button("Sign Out", use_container_width=True, key="signout"):
            st.session_state.authenticated = False
            st.session_state.user = None
            st.rerun()


# ── Main ──────────────────────────────────────────────────────────────────────
if not st.session_state.authenticated:
    show_auth()
else:
    show_sidebar()

    st.markdown("""
    <h1 style="font-family:'Syne',sans-serif;font-size:3rem;font-weight:800;margin-bottom:0.25rem;">
        Welcome to <span class="grad">MindWave</span>
    </h1>
    <p style="color:var(--muted);font-size:1.1rem;margin-bottom:2.5rem;">
        Your AI-powered emotional support companion — always here for you.
    </p>
    """, unsafe_allow_html=True)

    # Feature cards
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("""
        <div class="card">
            <div style="font-size:2rem;margin-bottom:0.75rem">💬</div>
            <div style="font-family:'Syne',sans-serif;font-weight:700;font-size:1.1rem;margin-bottom:0.5rem">
                AI Chatbot
            </div>
            <div style="color:var(--muted);font-size:0.9rem;line-height:1.6">
                Talk to an empathetic AI powered by advanced language models.
                Choose from multiple AI personalities.
            </div>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown("""
        <div class="card">
            <div style="font-size:2rem;margin-bottom:0.75rem">🎵</div>
            <div style="font-family:'Syne',sans-serif;font-weight:700;font-size:1.1rem;margin-bottom:0.5rem">
                Music Recommender
            </div>
            <div style="color:var(--muted);font-size:0.9rem;line-height:1.6">
                Discover songs tailored to your mood. 57,000+ songs with
                smart similarity matching.
            </div>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown("""
        <div class="card">
            <div style="font-size:2rem;margin-bottom:0.75rem">😊</div>
            <div style="font-family:'Syne',sans-serif;font-weight:700;font-size:1.1rem;margin-bottom:0.5rem">
                Emotion Detector
            </div>
            <div style="color:var(--muted);font-size:0.9rem;line-height:1.6">
                Real-time facial emotion recognition using EfficientNet-B3.
                Upload or use your webcam.
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Recent emotion history
    from database import get_emotion_history
    history = get_emotion_history(st.session_state.user["id"])
    if history:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""
        <div style="font-family:'Syne',sans-serif;font-weight:700;font-size:1.1rem;margin-bottom:1rem">
            📊 Recent Emotion History
        </div>
        """, unsafe_allow_html=True)

        emotion_icons = {
            "happy": "😊", "sadness": "😢", "anger": "😠",
            "fear": "😨", "surprise": "😲", "disgust": "🤢", "contempt": "😒"
        }
        cols = st.columns(min(len(history), 5))
        for i, entry in enumerate(history[:5]):
            with cols[i]:
                icon = emotion_icons.get(entry["emotion"], "🧠")
                st.markdown(f"""
                <div class="card" style="text-align:center;padding:1rem">
                    <div style="font-size:1.8rem">{icon}</div>
                    <div style="font-family:'Syne',sans-serif;font-weight:600;
                                font-size:0.85rem;margin-top:0.4rem;text-transform:capitalize">
                        {entry['emotion']}
                    </div>
                    <div style="color:var(--muted);font-size:0.75rem">
                        {round(entry['confidence']*100)}% confidence
                    </div>
                </div>
                """, unsafe_allow_html=True)