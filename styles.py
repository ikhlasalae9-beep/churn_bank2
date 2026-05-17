APP_CSS = """
<style>
:root {
    --app-bg: #111318;
    --sidebar-bg: #171a21;
    --card-bg: #1e222b;
    --card-bg-soft: #242936;
    --border: #333947;
    --border-strong: #465064;
    --text: #f2f5f9;
    --text-muted: #a9b2c3;
    --blue: #2f81f7;
    --blue-hover: #1f6feb;
    --blue-soft: rgba(47, 129, 247, 0.16);
    --success: #2ea043;
    --warning: #d29922;
    --danger: #f85149;
}

.stApp {
    background: var(--app-bg);
    color: var(--text);
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 1280px;
}

[data-testid="stSidebar"] {
    background: var(--sidebar-bg);
    border-right: 1px solid var(--border);
}

[data-testid="stSidebar"] * {
    color: var(--text);
}

[data-testid="stSidebar"] [role="radiogroup"] label {
    border-radius: 6px;
    padding: 0.35rem 0.55rem;
    margin-bottom: 0.25rem;
}

[data-testid="stSidebar"] [role="radiogroup"] label:hover {
    background: var(--blue-soft);
}

h1, h2, h3, h4, h5, h6, p, li, label, span {
    color: var(--text);
    letter-spacing: 0;
}

a {
    color: var(--blue);
}

hr {
    border-color: var(--border);
}

.app-card,
.status-box,
.chart-panel {
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 1rem 1.1rem;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.18);
}

.home-hero {
    min-height: 360px;
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 3rem 2.5rem;
    margin-bottom: 1.5rem;
    display: flex;
    flex-direction: column;
    justify-content: center;
    background-image:
        linear-gradient(90deg, rgba(17, 19, 24, 0.94), rgba(17, 19, 24, 0.72), rgba(17, 19, 24, 0.35)),
        url("https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?auto=format&fit=crop&w=1800&q=80");
    background-size: cover;
    background-position: center;
    box-shadow: 0 16px 44px rgba(0, 0, 0, 0.28);
}

.home-hero h1 {
    max-width: 720px;
    font-size: 3rem;
    line-height: 1.08;
    margin: 0 0 1rem 0;
}

.home-hero p {
    max-width: 720px;
    color: var(--text-muted);
    font-size: 1.05rem;
    line-height: 1.7;
}

.hero-eyebrow {
    color: #79c0ff;
    font-size: 0.78rem;
    font-weight: 800;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin-bottom: 0.8rem;
}

.eda-header {
    text-align: center;
    margin: 3.4rem 0 2.1rem 0;
    position: relative;
}

.eda-header h2 {
    color: #eae4dc;
    font-size: 2.1rem;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 0.7rem;
}

.eda-header .accent-line {
    width: 120px;
    height: 4px;
    background: linear-gradient(90deg, transparent, #dcbd92, transparent);
    margin: 0 auto;
    border-radius: 2px;
}

.status-box {
    border-left: 4px solid var(--blue);
    margin-top: 1rem;
}

.status-box.success {
    border-left-color: var(--success);
}

.status-box.warning {
    border-left-color: var(--warning);
}

.status-box.danger {
    border-left-color: var(--danger);
}

.muted {
    color: var(--text-muted);
}

[data-testid="stMetric"] {
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 1rem;
}

[data-testid="stMetricLabel"],
[data-testid="stMetricDelta"] {
    color: var(--text-muted);
}

[data-testid="stMetricValue"] {
    color: var(--text);
    font-weight: 700;
}

.stButton > button,
.stDownloadButton > button,
button[kind="primary"] {
    background: var(--blue);
    color: #ffffff;
    border: 1px solid var(--blue);
    border-radius: 6px;
    font-weight: 700;
    min-height: 2.5rem;
}

.stButton > button:hover,
.stDownloadButton > button:hover,
button[kind="primary"]:hover {
    background: var(--blue-hover);
    border-color: var(--blue-hover);
    color: #ffffff;
}

.stButton > button:focus,
.stDownloadButton > button:focus,
button:focus {
    box-shadow: 0 0 0 0.2rem rgba(47, 129, 247, 0.35);
    border-color: var(--blue);
}

[data-testid="stNumberInput"] input,
[data-testid="stTextInput"] input,
[data-testid="stSelectbox"] div[data-baseweb="select"] > div,
[data-testid="stSlider"] [data-baseweb="slider"],
[data-testid="stFileUploader"] section {
    background: var(--card-bg-soft);
    color: var(--text);
    border-color: var(--border-strong);
}

[data-testid="stNumberInput"] button {
    background: var(--card-bg-soft);
    color: var(--text);
    border-color: var(--border-strong);
}

[data-testid="stSlider"] div[role="slider"] {
    background: var(--blue);
    border-color: var(--blue);
}

[data-testid="stSlider"] div[data-testid="stTickBar"] {
    color: var(--text-muted);
}

[data-testid="stDataFrame"],
[data-testid="stTable"] {
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 8px;
}

[data-testid="stAlert"] {
    background: var(--card-bg-soft);
    border: 1px solid var(--border);
    color: var(--text);
}

.stProgress > div > div > div > div {
    background: var(--blue);
}
</style>
"""
