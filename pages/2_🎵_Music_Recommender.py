import streamlit as st
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import pickle
import requests

# ── Auth Guard ────────────────────────────────────────────────────────────────
if "authenticated" not in st.session_state or not st.session_state.authenticated:
    st.warning("Please sign in to access this page.")
    st.stop()

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="Music Recommender — MindWave", page_icon="🎵", layout="wide")

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
[data-testid="stSelectbox"]>div>div{background:var(--surface2)!important;border:1px solid var(--border)!important;border-radius:10px!important;color:var(--text)!important;}
.grad{background:linear-gradient(135deg,var(--accent),var(--accent2));-webkit-background-clip:text;-webkit-text-fill-color:transparent;}
.song-card{background:var(--surface);border:1px solid var(--border);border-radius:16px;padding:1rem;transition:all 0.25s;text-align:center;}
.song-card:hover{border-color:var(--accent);transform:translateY(-4px);box-shadow:0 12px 30px rgba(124,106,255,0.15);}
.song-title{font-family:'Syne',sans-serif;font-weight:700;font-size:0.85rem;margin-top:0.75rem;line-height:1.3;}
.emotion-chip{display:inline-block;padding:0.3rem 0.9rem;border-radius:50px;font-size:0.8rem;font-family:'Syne',sans-serif;font-weight:600;margin:0.2rem;cursor:pointer;border:2px solid transparent;transition:all 0.2s;}
</style>
""", unsafe_allow_html=True)

# ── Emotion → mood tag mapping ────────────────────────────────────────────────
EMOTION_MOOD = {
    "happy":    {"label": "😊 Happy",    "color": "#fbbf24", "desc": "Upbeat & joyful songs"},
    "sadness":  {"label": "😢 Sad",      "color": "#60a5fa", "desc": "Comforting, reflective songs"},
    "anger":    {"label": "😠 Angry",    "color": "#f87171", "desc": "Intense, powerful songs"},
    "fear":     {"label": "😨 Fearful",  "color": "#a78bfa", "desc": "Calming, soothing songs"},
    "surprise": {"label": "😲 Surprised","color": "#34d399", "desc": "Dynamic, energetic songs"},
    "disgust":  {"label": "🤢 Disgusted","color": "#6b7280", "desc": "Chill, laid-back songs"},
    "contempt": {"label": "😒 Contempt", "color": "#f59e0b", "desc": "Empowering, confident songs"},
    "neutral":  {"label": "😐 Neutral",  "color": "#94a3b8", "desc": "Balanced, all-genre songs"},
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
    if st.button("Sign Out", use_container_width=True):
        st.session_state.authenticated = False
        st.session_state.user = None
        st.rerun()

# ── Load Data ─────────────────────────────────────────────────────────────────
@st.cache_resource
def load_data():
    music = pickle.load(open('df.pkl', 'rb'))
    similarity = pickle.load(open('similarity.pkl', 'rb'))
    return music, similarity

try:
    music, similarity = load_data()
    data_loaded = True
except Exception as e:
    data_loaded = False
    st.error(f"Could not load music data: {e}")

# ── iTunes Cover Fetch ────────────────────────────────────────────────────────
@st.cache_data
def get_song_album_cover_url(song_name, artist_name):
    try:
        response = requests.get(
            "https://itunes.apple.com/search",
            params={"term": f"{song_name} {artist_name}", "media": "music", "entity": "song", "limit": 10}
        )
        results = response.json().get("results", [])
        if not results:
            return "https://i.imgur.com/8RKXAIV.jpg"
        for result in results:
            track = result.get("trackName", "").lower()
            artist = result.get("artistName", "").lower()
            if (song_name.lower() in track or track in song_name.lower()) and \
               (artist_name.lower() in artist or artist in artist_name.lower()):
                return result["artworkUrl100"].replace("100x100", "500x500")
        for result in results:
            track = result.get("trackName", "").lower()
            if song_name.lower() in track or track in song_name.lower():
                return result["artworkUrl100"].replace("100x100", "500x500")
        return results[0]["artworkUrl100"].replace("100x100", "500x500")
    except:
        return "https://i.imgur.com/8RKXAIV.jpg"

def recommend(song):
    index = music[music['song'] == song].index[0]
    distance = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    names, posters = [], []
    for i in distance[1:6]:
        artist = music.iloc[i[0]].artist
        song_name = music.iloc[i[0]].song
        names.append(song_name)
        posters.append(get_song_album_cover_url(song_name, artist))
    return names, posters

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<h1 style="font-family:'Syne',sans-serif;font-size:2rem;font-weight:800;margin-bottom:0.25rem">
    🎵 Music <span class="grad">Recommender</span>
</h1>
<p style="color:var(--muted);font-size:0.95rem;margin-bottom:1.5rem">
    Discover songs that match your vibe — pick a mood or search by song.
</p>
""", unsafe_allow_html=True)

if data_loaded:
    # ── Mood from Emotion Detector ────────────────────────────────────────────
    detected_emotion = st.session_state.get("detected_emotion", None)
    if detected_emotion:
        mood_info = EMOTION_MOOD.get(detected_emotion, EMOTION_MOOD["neutral"])
        st.markdown(f"""
        <div style="background:var(--surface2);border:1px solid var(--border);border-radius:14px;
                    padding:1rem 1.25rem;margin-bottom:1.5rem;display:flex;align-items:center;gap:1rem">
            <div style="font-size:1.8rem">{mood_info['label'].split()[0]}</div>
            <div>
                <div style="font-family:'Syne',sans-serif;font-weight:600;font-size:0.9rem">
                    Emotion detected: <span style="color:{mood_info['color']}">{detected_emotion.capitalize()}</span>
                </div>
                <div style="color:var(--muted);font-size:0.82rem">
                    Showing songs suited for your mood · {mood_info['desc']}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── Song Selector ─────────────────────────────────────────────────────────
    selected_music = st.selectbox(
        "🔍 Search or select a song",
        music['song'].values,
        key="music_select"
    )

    if st.button("🎵 Get Recommendations", use_container_width=False):
        with st.spinner("Finding your perfect songs..."):
            names, posters = recommend(selected_music)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"""
        <div style="font-family:'Syne',sans-serif;font-weight:700;font-size:1rem;
                    margin-bottom:1rem;color:var(--muted)">
            Because you like <span style="color:var(--text)">"{selected_music}"</span>
        </div>
        """, unsafe_allow_html=True)

        cols = st.columns(5)
        for i in range(5):
            with cols[i]:
                st.markdown(f'<div class="song-card">', unsafe_allow_html=True)
                st.image(posters[i], use_container_width=True)
                st.markdown(f'<div class="song-title">{names[i]}</div></div>', unsafe_allow_html=True)