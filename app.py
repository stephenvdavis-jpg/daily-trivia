"""
Daily Trivia App
A minimalist trivia application with Google Sheets integration.
Features: Global History, Advanced Stats, Streak Tracking, Hall of Fame
"""

import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from datetime import datetime, timedelta
import time
from streamlit_gsheets import GSheetsConnection

# ============================================================================
# CONFIGURATION
# ============================================================================
NUM_QUESTIONS = 5  # Change this to 10 if you want more questions
TIMER_SECONDS = 60  # Change this to adjust quiz duration
QUIZ_DAYS = [0, 4]  # Monday=0, Friday=4 (days quizzes are released)

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================
st.set_page_config(
    page_title="Daily Trivia",
    page_icon="🧠",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ============================================================================
# CUSTOM CSS - With Background Image
# ============================================================================
# NOTE: Upload background.jpeg to your GitHub repo and update this URL
# Example: https://raw.githubusercontent.com/stephenvdavis-jpg/daily-trivia/main/background.jpeg
BACKGROUND_IMAGE_URL = "https://i.imgur.com/mEpKudh.jpeg"

st.markdown("""
<style>
    /* Import Helvetica-like font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global styles */
    html, body, [class*="css"] {
        font-family: 'Inter', 'Helvetica Neue', Helvetica, Arial, sans-serif;
    }
    
    /* Headers */
    h1, h2, h3, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        font-weight: 600;
        color: #000000 !important;
        letter-spacing: -0.02em;
    }
    
    /* Main title styling */
    .main-title {
        font-size: 2.5rem;
        font-weight: 700;
        text-align: center;
        margin-bottom: 0.5rem;
        color: #000000 !important;
    }
    
    .subtitle {
        font-size: 1rem;
        text-align: center;
        color: #666666 !important;
        margin-bottom: 2rem;
    }
    
    /* ========== TIMER DISPLAY - FORCE WHITE TEXT ========== */
    .timer-container,
    div.timer-container {
        background-color: #000000 !important;
        color: #ffffff !important;
        padding: 1rem 2rem;
        border-radius: 8px;
        text-align: center;
        font-size: 2rem;
        font-weight: 700;
        margin: 1rem 0;
        font-variant-numeric: tabular-nums;
    }
    
    .timer-container *,
    div.timer-container * {
        color: #ffffff !important;
    }
    
    .timer-warning,
    div.timer-warning {
        background-color: #333333 !important;
        animation: pulse 1s infinite;
    }
    
    .timer-warning *,
    div.timer-warning * {
        color: #ffffff !important;
    }

    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.7; }
    }
    
    /* Question cards */
    .question-card {
        background-color: #f8f8f8 !important;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 1.5rem;
        margin: 1rem 0;
    }
    
    .question-number {
        font-size: 0.875rem;
        font-weight: 600;
        color: #666666 !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.5rem;
    }
    
    .question-text {
        font-size: 1.125rem;
        font-weight: 500;
        color: #000000 !important;
        margin-bottom: 1rem;
    }
    
    /* ========== BUTTONS - FORCE WHITE TEXT ========== */
    .stButton > button,
    .stButton button,
    [data-testid="stButton"] button,
    [data-testid="baseButton-secondary"],
    [data-testid="baseButton-primary"] {
        background-color: #000000 !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 6px;
        padding: 0.75rem 2rem;
        font-weight: 500;
        font-size: 1rem;
        transition: all 0.2s ease;
        width: 100%;
    }
    
    /* Button text specifically */
    .stButton > button *,
    .stButton button *,
    [data-testid="stButton"] button *,
    .stButton > button p,
    .stButton > button span {
        color: #ffffff !important;
    }
    
    .stButton > button:hover,
    .stButton button:hover,
    [data-testid="stButton"] button:hover {
        background-color: #333333 !important;
        color: #ffffff !important;
    }
    
    .stButton > button:hover * {
        color: #ffffff !important;
    }

    /* Input fields */
    .stTextInput > div > div > input {
        border: 2px solid #000000 !important;
        border-radius: 6px;
        padding: 0.75rem;
        font-size: 1rem;
        background-color: #ffffff !important;
        color: #000000 !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #000000 !important;
        box-shadow: 0 0 0 1px #000000;
    }
    
    /* ========== RADIO BUTTONS - CRITICAL FIX ========== */
    .stRadio > div {
        background-color: transparent !important;
    }
    
    /* Radio button labels/options */
    .stRadio label, 
    .stRadio [data-testid="stMarkdownContainer"] p,
    .stRadio span,
    [data-testid="stRadio"] label,
    [data-testid="stRadio"] p,
    [data-testid="stRadio"] span {
        color: #000000 !important;
        background-color: transparent !important;
    }
    
    /* Radio option containers */
    .stRadio > div > label,
    [data-testid="stRadio"] > div > label {
        background-color: #f8f8f8 !important;
        border: 1px solid #e0e0e0 !important;
        border-radius: 6px;
        padding: 0.75rem 1rem;
        margin: 0.25rem 0;
        cursor: pointer;
        transition: all 0.2s ease;
        color: #000000 !important;
    }
    
    .stRadio > div > label:hover,
    [data-testid="stRadio"] > div > label:hover {
        background-color: #e8e8e8 !important;
        border-color: #000000 !important;
    }
    
    /* Selected radio option */
    .stRadio > div > label[data-checked="true"],
    [data-testid="stRadio"] > div > label[data-checked="true"] {
        background-color: #e0e0e0 !important;
        border-color: #000000 !important;
    }
    
    /* Leaderboard table */
    .leaderboard-container {
        margin-top: 2rem;
    }
    
    /* Dataframe/Table styling */
    .stDataFrame, [data-testid="stDataFrame"] {
        background-color: #ffffff !important;
    }
    
    .stDataFrame th, .stDataFrame td,
    [data-testid="stDataFrame"] th, 
    [data-testid="stDataFrame"] td {
        color: #000000 !important;
        background-color: #ffffff !important;
    }
    
    /* ========== SCORE DISPLAY - FORCE WHITE TEXT ========== */
    .score-display,
    div.score-display {
        background-color: #000000 !important;
        color: #ffffff !important;
        padding: 2rem;
        border-radius: 8px;
        text-align: center;
        margin: 2rem 0;
    }
    
    .score-display *,
    .score-display div,
    .score-display p,
    .score-display span,
    div.score-display *,
    div.score-display div,
    div.score-display p,
    div.score-display span {
        color: #ffffff !important;
    }
    
    .score-number,
    .score-display .score-number {
        font-size: 4rem;
        font-weight: 700;
        line-height: 1;
        color: #ffffff !important;
    }
    
    .score-label,
    .score-display .score-label {
        font-size: 1rem;
        color: #cccccc !important;
        margin-top: 0.5rem;
    }

    /* Error messages */
    .error-box {
        background-color: #f8f8f8 !important;
        border: 1px solid #cccccc;
        border-radius: 8px;
        padding: 1.5rem;
        text-align: center;
        color: #333333 !important;
    }
    
    /* Warning/Info boxes */
    .stAlert, [data-testid="stAlert"] {
        background-color: #f8f8f8 !important;
        color: #000000 !important;
    }
    
    .stAlert p, [data-testid="stAlert"] p {
        color: #000000 !important;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Divider */
    hr {
        border: none;
        border-top: 1px solid #e0e0e0;
        margin: 2rem 0;
    }
    
    /* ========== STAT CARDS ========== */
    .stat-card {
        background-color: #f8f8f8 !important;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 1.5rem;
        text-align: center;
        margin: 0.5rem 0;
    }
    
    .stat-card * {
        color: #000000 !important;
    }
    
    .stat-value {
        font-size: 2rem;
        font-weight: 700;
        color: #000000 !important;
        line-height: 1.2;
    }
    
    .stat-label {
        font-size: 0.875rem;
        color: #666666 !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-top: 0.5rem;
    }
    
    .stat-sublabel {
        font-size: 0.75rem;
        color: #999999 !important;
        margin-top: 0.25rem;
    }
    
    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        color: #000000 !important;
        font-weight: 500;
    }
    
    .stTabs [aria-selected="true"] {
        color: #000000 !important;
        border-bottom-color: #000000 !important;
    }
</style>
""", unsafe_allow_html=True)

# Apply background image with f-string
st.markdown(f"""
<style>
    /* ========== BACKGROUND IMAGE ========== */
    .stApp, [data-testid="stAppViewContainer"] {{
        background-image: url('{BACKGROUND_IMAGE_URL}');
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}
    
    [data-testid="stHeader"] {{
        background-color: transparent !important;
    }}
    
    /* ========== CONTENT CARD WITH READABLE BACKGROUND ========== */
    .block-container {{
        background-color: rgba(255, 255, 255, 0.93) !important;
        border-radius: 16px;
        padding: 2rem !important;
        margin: 1rem auto;
        max-width: 800px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
    }}
    
    /* Force text to be dark on the white overlay */
    .stApp p, .stApp div, .stApp label {{
        color: #000000 !important;
    }}
    
    /* Exclude button text */
    .stApp .stButton p, 
    .stApp .stButton span, 
    .stApp .stButton div,
    .stButton button p,
    .stButton button span,
    .stButton button div {{
        color: #ffffff !important;
    }}
    
    /* Exclude score-display */
    .stApp .score-display,
    .stApp .score-display *,
    .stApp .score-number,
    .stApp .score-label {{
        color: #ffffff !important;
    }}
    
    .stApp .score-label {{
        color: #cccccc !important;
    }}
    
    /* Exclude timer-container */
    .stApp .timer-container,
    .stApp .timer-container *,
    .stApp .timer-warning,
    .stApp .timer-warning * {{
        color: #ffffff !important;
    }}
</style>
""", unsafe_allow_html=True)


# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================
def init_session_state():
    """Initialize all session state variables."""
    defaults = {
        'player_name': '',
        'game_started': False,
        'start_time': None,
        'questions': None,
        'answers': {},
        'submitted': False,
        'score': 0,
        'time_taken': 0,
        'connection_error': None,
        'questions_total': NUM_QUESTIONS
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


# ============================================================================
# GOOGLE SHEETS CONNECTION
# ============================================================================
@st.cache_resource(ttl=60)
def get_connection():
    """Create and cache the Google Sheets connection."""
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        return conn, None
    except Exception as e:
        return None, str(e)


def fetch_questions(conn):
    """Fetch trivia questions from the Questions sheet."""
    try:
        df = conn.read(
            worksheet="Questions",
            usecols=list(range(6)),  # Columns A-F
            ttl=60  # Cache for 60 seconds
        )
        # Clean the dataframe
        df = df.dropna(how='all')
        
        # Validate required columns
        required_cols = ['Question', 'Option_A', 'Option_B', 'Option_C', 'Option_D', 'Correct_Answer']
        if not all(col in df.columns for col in required_cols):
            return None, f"Missing columns. Required: {required_cols}"
        
        # Get random questions (based on NUM_QUESTIONS config)
        n_questions = min(NUM_QUESTIONS, len(df))
        if n_questions == 0:
            return None, "No questions found in the sheet."
        
        questions = df.sample(n=n_questions).reset_index(drop=True)
        st.session_state.questions_total = n_questions
        return questions, None
    except Exception as e:
        return None, f"Error fetching questions: {str(e)}"


def append_to_leaderboard(conn, name, score, time_taken):
    """Append a new entry to the Leaderboard sheet (weekly view)."""
    try:
        # Read existing leaderboard
        existing = conn.read(worksheet="Leaderboard", ttl=1)
        
        # Create new entry
        new_entry = pd.DataFrame([{
            'Name': name,
            'Score': score,
            'Time_Taken': time_taken,
            'Timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }])
        
        # Combine with existing data
        if existing is not None and not existing.empty:
            existing = existing.dropna(how='all')
            updated = pd.concat([existing, new_entry], ignore_index=True)
        else:
            updated = new_entry
        
        # Write back to sheet
        conn.update(worksheet="Leaderboard", data=updated)
        return True, None
    except Exception as e:
        return False, f"Error saving score: {str(e)}"


def append_to_global_history(conn, name, score, time_taken, questions_total):
    """Append a new entry to the Global_History sheet (permanent archive)."""
    try:
        # Read existing history
        existing = conn.read(worksheet="Global_History", ttl=1)
        
        # Create new entry with all fields
        new_entry = pd.DataFrame([{
            'Name': name,
            'Score': score,
            'Time_Taken': time_taken,
            'Questions_Total': questions_total,
            'Timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'Date': datetime.now().strftime('%Y-%m-%d')
        }])
        
        # Combine with existing data
        if existing is not None and not existing.empty:
            existing = existing.dropna(how='all')
            updated = pd.concat([existing, new_entry], ignore_index=True)
        else:
            updated = new_entry
        
        # Write back to sheet
        conn.update(worksheet="Global_History", data=updated)
        return True, None
    except Exception as e:
        return False, f"Error saving to history: {str(e)}"


def get_leaderboard(conn):
    """Fetch the current leaderboard."""
    try:
        df = conn.read(worksheet="Leaderboard", ttl=1)
        if df is None or df.empty:
            return pd.DataFrame(columns=['Name', 'Score', 'Time_Taken', 'Timestamp'])
        
        df = df.dropna(how='all')
        # Sort by score (desc) then time (asc)
        if 'Score' in df.columns and 'Time_Taken' in df.columns:
            df = df.sort_values(
                by=['Score', 'Time_Taken'],
                ascending=[False, True]
            ).reset_index(drop=True)
        return df
    except Exception as e:
        return pd.DataFrame(columns=['Name', 'Score', 'Time_Taken', 'Timestamp'])


def get_global_history(conn):
    """Fetch the global history for stats calculations."""
    try:
        df = conn.read(worksheet="Global_History", ttl=5)
        if df is None or df.empty:
            return pd.DataFrame(columns=['Name', 'Score', 'Time_Taken', 'Questions_Total', 'Timestamp', 'Date'])
        
        df = df.dropna(how='all')
        
        # Ensure Questions_Total exists and handle missing values (assume 5 for old data)
        if 'Questions_Total' not in df.columns:
            df['Questions_Total'] = 5
        else:
            df['Questions_Total'] = df['Questions_Total'].fillna(5)
        
        # Ensure Date column exists
        if 'Date' not in df.columns and 'Timestamp' in df.columns:
            df['Date'] = pd.to_datetime(df['Timestamp']).dt.strftime('%Y-%m-%d')
        
        return df
    except Exception as e:
        return pd.DataFrame(columns=['Name', 'Score', 'Time_Taken', 'Questions_Total', 'Timestamp', 'Date'])


# ============================================================================
# ADVANCED STATS CALCULATIONS
# ============================================================================
def calculate_sharpshooter(df):
    """
    Calculate accuracy stats for each user.
    Formula: (Sum of all User's Scores / Sum of all User's Questions_Total) * 100
    """
    if df.empty:
        return pd.DataFrame(columns=['Name', 'Accuracy', 'Total_Correct', 'Total_Questions', 'Games_Played'])
    
    # Ensure numeric types
    df['Score'] = pd.to_numeric(df['Score'], errors='coerce').fillna(0)
    df['Questions_Total'] = pd.to_numeric(df['Questions_Total'], errors='coerce').fillna(5)
    
    # Group by user
    stats = df.groupby('Name').agg({
        'Score': 'sum',
        'Questions_Total': 'sum',
        'Name': 'count'
    }).rename(columns={'Name': 'Games_Played', 'Score': 'Total_Correct', 'Questions_Total': 'Total_Questions'})
    
    # Calculate accuracy
    stats['Accuracy'] = (stats['Total_Correct'] / stats['Total_Questions'] * 100).round(1)
    
    # Sort by accuracy (desc), then by games played (desc) for tiebreaker
    stats = stats.sort_values(by=['Accuracy', 'Games_Played'], ascending=[False, False])
    
    return stats.reset_index()


def calculate_speed_demon(df):
    """
    Calculate average time stats for each user.
    Lower average time = faster = better.
    """
    if df.empty:
        return pd.DataFrame(columns=['Name', 'Avg_Time', 'Fastest_Time', 'Games_Played'])
    
    # Ensure numeric type
    df['Time_Taken'] = pd.to_numeric(df['Time_Taken'], errors='coerce').fillna(60)
    
    # Group by user
    stats = df.groupby('Name').agg({
        'Time_Taken': ['mean', 'min', 'count']
    })
    
    stats.columns = ['Avg_Time', 'Fastest_Time', 'Games_Played']
    stats['Avg_Time'] = stats['Avg_Time'].round(1)
    
    # Sort by average time (asc) - faster is better
    stats = stats.sort_values(by='Avg_Time', ascending=True)
    
    return stats.reset_index()


def calculate_monthly_leaderboard(df):
    """
    Filter data to current month and calculate monthly stats.
    """
    if df.empty:
        return pd.DataFrame(columns=['Name', 'Total_Score', 'Avg_Score', 'Games_Played'])
    
    # Parse dates
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    
    # Filter to current month
    now = datetime.now()
    current_month = df[
        (df['Date'].dt.year == now.year) & 
        (df['Date'].dt.month == now.month)
    ]
    
    if current_month.empty:
        return pd.DataFrame(columns=['Name', 'Total_Score', 'Avg_Score', 'Games_Played'])
    
    # Ensure numeric
    current_month['Score'] = pd.to_numeric(current_month['Score'], errors='coerce').fillna(0)
    
    # Group by user
    stats = current_month.groupby('Name').agg({
        'Score': ['sum', 'mean', 'count']
    })
    
    stats.columns = ['Total_Score', 'Avg_Score', 'Games_Played']
    stats['Avg_Score'] = stats['Avg_Score'].round(1)
    stats['Total_Score'] = stats['Total_Score'].astype(int)
    
    # Sort by total score (desc)
    stats = stats.sort_values(by='Total_Score', ascending=False)
    
    return stats.reset_index()


def get_play_window(date):
    """
    Determine which play window a date falls into.
    
    Window A (Early Week): Monday (0) through Thursday (3)
    Window B (Weekend): Friday (4) through Sunday (6)
    
    Returns a tuple of (year, week_number, window_letter) for comparison.
    """
    if isinstance(date, str):
        date = pd.to_datetime(date).date()
    elif hasattr(date, 'date'):
        date = date.date()
    
    weekday = date.weekday()  # Monday=0, Sunday=6
    year, week_num, _ = date.isocalendar()
    
    if weekday <= 3:  # Monday-Thursday = Window A
        return (year, week_num, 'A')
    else:  # Friday-Sunday = Window B
        return (year, week_num, 'B')


def get_all_windows_in_order():
    """
    Generate a list of all possible windows from a start date to now,
    in reverse chronological order (most recent first).
    """
    windows = []
    current_date = datetime.now().date()
    
    # Go back about 1 year (52 weeks * 2 windows)
    start_date = current_date - timedelta(days=365)
    
    # Generate all windows
    check_date = start_date
    while check_date <= current_date:
        window = get_play_window(check_date)
        if window not in windows:
            windows.append(window)
        check_date += timedelta(days=1)
    
    # Return in reverse order (most recent first)
    return list(reversed(windows))


def calculate_streak(df, user_name):
    """
    Calculate a user's consecutive play streak using the window system.
    
    Window A (Early Week): Monday through Thursday
    Window B (Weekend): Friday through Sunday
    
    A user maintains their streak if they have at least one submission
    in consecutive windows.
    """
    if df.empty:
        return 0
    
    # Get this user's play dates
    user_df = df[df['Name'] == user_name].copy()
    if user_df.empty:
        return 0
    
    user_df['Date'] = pd.to_datetime(user_df['Date'], errors='coerce')
    user_dates = user_df['Date'].dropna().dt.date.unique()
    
    if len(user_dates) == 0:
        return 0
    
    # Get the windows the user played in
    user_windows = set()
    for date in user_dates:
        user_windows.add(get_play_window(date))
    
    # Get current window
    current_window = get_play_window(datetime.now().date())
    
    # Get all windows in order (most recent first)
    all_windows = get_all_windows_in_order()
    
    # Find where current window is in the list
    try:
        current_idx = all_windows.index(current_window)
    except ValueError:
        return 0
    
    # Count consecutive windows starting from current (or most recent played)
    streak = 0
    
    # First check if they played in current window
    if current_window in user_windows:
        streak = 1
        start_idx = current_idx + 1
    else:
        # Check if they played in the previous window (grace period)
        if current_idx + 1 < len(all_windows):
            prev_window = all_windows[current_idx + 1]
            if prev_window in user_windows:
                streak = 1
                start_idx = current_idx + 2
            else:
                return 0  # Missed both current and previous window
        else:
            return 0
    
    # Count backwards through consecutive windows
    for i in range(start_idx, len(all_windows)):
        window = all_windows[i]
        if window in user_windows:
            streak += 1
        else:
            break  # Streak broken
    
    return streak


def calculate_all_streaks(df):
    """
    Calculate streaks for all users using the window system.
    """
    if df.empty:
        return pd.DataFrame(columns=['Name', 'Current_Streak', 'Last_Played'])
    
    # Get unique users
    users = df['Name'].unique()
    
    streaks = []
    for user in users:
        streak = calculate_streak(df, user)
        
        # Get last played date
        user_df = df[df['Name'] == user].copy()
        user_df['Date'] = pd.to_datetime(user_df['Date'], errors='coerce')
        last_played = user_df['Date'].max()
        
        streaks.append({
            'Name': user,
            'Current_Streak': streak,
            'Last_Played': last_played.strftime('%Y-%m-%d') if pd.notna(last_played) else 'N/A'
        })
    
    streak_df = pd.DataFrame(streaks)
    streak_df = streak_df.sort_values(by='Current_Streak', ascending=False)
    
    return streak_df.reset_index(drop=True)


# ============================================================================
# TIMER COMPONENT
# ============================================================================
def display_timer():
    """Display and manage the countdown timer."""
    if st.session_state.start_time is None:
        return TIMER_SECONDS
    
    elapsed = time.time() - st.session_state.start_time
    remaining = max(0, TIMER_SECONDS - int(elapsed))
    
    # Style based on time remaining
    timer_class = "timer-container"
    if remaining <= 10:
        timer_class += " timer-warning"
    
    minutes = remaining // 60
    seconds = remaining % 60
    
    st.markdown(
        f'<div class="{timer_class}">{minutes:02d}:{seconds:02d}</div>',
        unsafe_allow_html=True
    )
    
    return remaining


# ============================================================================
# GAME SCREENS
# ============================================================================
def show_welcome_screen():
    """Display the welcome/name entry screen."""
    st.markdown('<h1 class="main-title">Btown Brief Trivia</h1>', unsafe_allow_html=True)
    st.markdown(f'<p class="subtitle">Test your knowledge in {TIMER_SECONDS} seconds</p>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("**Enter your name to begin.** Write the same UNIQUE name every week so your score gets tracked.")
        name = st.text_input(
            "Your name",
            placeholder="Your name...",
            key="name_input",
            label_visibility="collapsed"
        )
        st.caption("⚠️ Only play once per quiz please!")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("Start Quiz", use_container_width=True):
            if name.strip():
                st.session_state.player_name = name.strip()
                st.session_state.game_started = True
                st.session_state.start_time = time.time()
                
                # Fetch questions
                conn, error = get_connection()
                if error:
                    st.session_state.connection_error = error
                else:
                    questions, error = fetch_questions(conn)
                    if error:
                        st.session_state.connection_error = error
                    else:
                        st.session_state.questions = questions
                
                st.rerun()
            else:
                st.warning("Please enter your name to continue.")
    
    # Instructions
    st.markdown("---")
    st.markdown(f"""
    **How to Play:**
    - **The Challenge:** Answer {NUM_QUESTIONS} trivia questions.
    - **Beat the Clock:** You have {TIMER_SECONDS} seconds to complete (must stay on the page!).
    - **Get on the Board:** Your score and time are recorded.
    - **Top the Charts:** Compete for the #1 spot in Btown.
    """)
    
    # Hall of Fame link
    st.markdown("---")
    if st.button("🏆 View Hall of Fame", use_container_width=True):
        st.session_state.show_hall_of_fame = True
        st.rerun()


def show_quiz_screen():
    """Display the quiz questions."""
    st.markdown(f'<h1 class="main-title">Good luck, {st.session_state.player_name}!</h1>', unsafe_allow_html=True)
    
    # Check for connection error
    if st.session_state.connection_error:
        st.markdown(
            f'<div class="error-box">⚠️ {st.session_state.connection_error}</div>',
            unsafe_allow_html=True
        )
        if st.button("Try Again"):
            st.session_state.game_started = False
            st.session_state.connection_error = None
            st.rerun()
        return
    
    # Check for questions
    if st.session_state.questions is None:
        st.markdown(
            '<div class="error-box">⚠️ No questions loaded. Please try again.</div>',
            unsafe_allow_html=True
        )
        if st.button("Go Back"):
            st.session_state.game_started = False
            st.rerun()
        return
    
    # Timer display (TOP)
    remaining = display_timer()
    
    # Auto-submit if time runs out
    if remaining <= 0 and not st.session_state.submitted:
        submit_quiz()
        return
    
    st.markdown("---")
    
    # Display questions
    questions = st.session_state.questions
    total_questions = len(questions)
    midpoint = total_questions // 2  # Calculate midpoint for middle timer
    
    for idx, row in questions.iterrows():
        st.markdown(f'<div class="question-number">Question {idx + 1} of {total_questions}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="question-text">{row["Question"]}</div>', unsafe_allow_html=True)
        
        options = [
            f"A) {row['Option_A']}",
            f"B) {row['Option_B']}",
            f"C) {row['Option_C']}",
            f"D) {row['Option_D']}"
        ]
        
        answer = st.radio(
            f"Select answer for Q{idx + 1}",
            options=options,
            key=f"q_{idx}",
            index=None,  # No default selection
            label_visibility="collapsed"
        )
        
        # Store the answer letter (A, B, C, or D) only if user selected something
        if answer:
            st.session_state.answers[idx] = answer[0]  # Get just the letter
        
        st.markdown("---")
        
        # Add MIDDLE timer after the midpoint question
        if idx == midpoint - 1:
            st.markdown("#### ⏱️ Time Check:")
            display_timer()
            st.markdown("---")
    
    # Timer display (BOTTOM - before submit button)
    st.markdown("#### ⏱️ Time Remaining:")
    display_timer()
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Submit button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("Submit Answers — Wait 5 secs", use_container_width=True):
            submit_quiz()
    
    # Auto-refresh for timer (every second)
    if remaining > 0:
        time.sleep(0.1)
        st.rerun()


def submit_quiz():
    """Calculate score and submit to leaderboard and global history."""
    # Calculate time taken
    time_taken = int(time.time() - st.session_state.start_time)
    time_taken = min(time_taken, TIMER_SECONDS)  # Cap at timer limit
    st.session_state.time_taken = time_taken
    
    # Calculate score
    score = 0
    questions = st.session_state.questions
    
    if questions is not None:
        for idx, row in questions.iterrows():
            correct = str(row['Correct_Answer']).strip().upper()
            given = st.session_state.answers.get(idx, '').strip().upper()
            if given == correct:
                score += 1
    
    st.session_state.score = score
    
    # Save to both sheets
    conn, error = get_connection()
    if conn and not error:
        # Save to weekly leaderboard
        append_to_leaderboard(
            conn,
            st.session_state.player_name,
            score,
            time_taken
        )
        
        # Save to global history (permanent archive)
        append_to_global_history(
            conn,
            st.session_state.player_name,
            score,
            time_taken,
            st.session_state.questions_total
        )
    
    st.session_state.submitted = True
    st.rerun()


def show_results_screen():
    """Display the results and leaderboard."""
    # Force scroll to top using JavaScript in an iframe
    components.html("""
        <script>
            // Scroll parent window to top
            window.parent.document.querySelector('[data-testid="stAppViewContainer"]').scrollTo(0, 0);
            window.parent.document.querySelector('section.main').scrollTo(0, 0);
            window.parent.scrollTo(0, 0);
        </script>
    """, height=0, scrolling=False)
    
    st.markdown('<h1 class="main-title">Quiz Complete!</h1>', unsafe_allow_html=True)
    
    # Score display
    st.markdown(f"""
    <div class="score-display">
        <div class="score-number">{st.session_state.score}/{st.session_state.questions_total}</div>
        <div class="score-label">Correct Answers</div>
        <div class="score-label" style="margin-top: 1rem;">
            Completed in {st.session_state.time_taken} seconds
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Show correct answers
    st.markdown("### Your Answers")
    questions = st.session_state.questions
    
    if questions is not None:
        for idx, row in questions.iterrows():
            correct_letter = str(row['Correct_Answer']).strip().upper()
            given_letter = st.session_state.answers.get(idx, '').strip().upper()
            
            # Map letters to actual answer text
            answer_map = {
                'A': str(row['Option_A']),
                'B': str(row['Option_B']),
                'C': str(row['Option_C']),
                'D': str(row['Option_D'])
            }
            
            # Get the actual answer text
            given_text = answer_map.get(given_letter, 'No answer')
            correct_text = answer_map.get(correct_letter, '')
            
            is_correct = given_letter == correct_letter
            icon = "✓" if is_correct else "✗"
            
            if is_correct:
                st.markdown(f"""
                **Q{idx + 1}: {row['Question']}**  
                Your answer: **{given_text}** {icon}
                """)
            else:
                if given_letter:
                    st.markdown(f"""
                    **Q{idx + 1}: {row['Question']}**  
                    Your answer: **{given_text}** {icon}  
                    Correct answer: **{correct_text}**
                    """)
                else:
                    st.markdown(f"""
                    **Q{idx + 1}: {row['Question']}**  
                    Your answer: **No answer** {icon}  
                    Correct answer: **{correct_text}**
                    """)
    
    st.markdown("---")
    
    # This Quiz's Leaderboard (shown first)
    st.markdown("### 🏅 This Quiz's Leaderboard")
    show_weekly_leaderboard()
    
    st.divider()
    
    # Hall of Fame / Career Stats (shown below)
    st.markdown("### 🏆 Hall of Fame — Career Stats")
    show_hall_of_fame_content()
    
    st.markdown("---")
    
    # Big visual reminder to scroll up
    components.html("""
    <div style="
        background-color: #000000;
        color: #ffffff;
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        margin: 1rem 0;
        font-family: 'Inter', 'Helvetica Neue', Helvetica, Arial, sans-serif;
    ">
        <p style="font-size: 1.8rem; font-weight: 800; margin: 0; color: #ffffff;">
            ☝️ SCROLL UP TO SEE YOUR SCORE! ☝️
        </p>
        <p style="font-size: 1rem; margin-top: 0.5rem; color: #cccccc;">
            Your results and correct answers are at the top of this page
        </p>
    </div>
    """, height=130)
    
    st.markdown("---")
    
    # Share section
    st.markdown("### 📤 Share the Fun!")
    st.markdown("Challenge your friends to beat your score!")
    
    quiz_url = "https://daily-trivia-candbtjrukyyht8qqfmmmr.streamlit.app/"
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        # Copy link button using components.html for working JavaScript
        components.html(f"""
            <div style="text-align: center; font-family: 'Inter', 'Helvetica Neue', Helvetica, Arial, sans-serif;">
                <button id="copyBtn" onclick="copyToClipboard()" style="
                    background-color: #000000;
                    color: #ffffff;
                    border: none;
                    border-radius: 6px;
                    padding: 0.75rem 2rem;
                    font-weight: 500;
                    font-size: 1rem;
                    cursor: pointer;
                    width: 100%;
                    font-family: inherit;
                ">🔗 Copy Link to Send to Friends</button>
                <p id="copy-confirm" style="display: none; color: #28a745; margin-top: 0.5rem; font-size: 0.9rem;">✓ Link copied to clipboard!</p>
            </div>
            <script>
                function copyToClipboard() {{
                    const url = "{quiz_url}";
                    navigator.clipboard.writeText(url).then(function() {{
                        document.getElementById('copy-confirm').style.display = 'block';
                        document.getElementById('copyBtn').innerText = '✓ Copied!';
                        setTimeout(function() {{
                            document.getElementById('copy-confirm').style.display = 'none';
                            document.getElementById('copyBtn').innerText = '🔗 Copy Link to Send to Friends';
                        }}, 2500);
                    }}).catch(function() {{
                        // Fallback for older browsers
                        const textArea = document.createElement('textarea');
                        textArea.value = url;
                        document.body.appendChild(textArea);
                        textArea.select();
                        document.execCommand('copy');
                        document.body.removeChild(textArea);
                        document.getElementById('copy-confirm').style.display = 'block';
                        document.getElementById('copyBtn').innerText = '✓ Copied!';
                        setTimeout(function() {{
                            document.getElementById('copy-confirm').style.display = 'none';
                            document.getElementById('copyBtn').innerText = '🔗 Copy Link to Send to Friends';
                        }}, 2500);
                    }});
                }}
            </script>
        """, height=100)
    
    st.markdown("---")
    
    # Homepage promo
    st.markdown("""
    <div style="text-align: center; padding: 1rem; background-color: #f8f8f8; border-radius: 8px;">
        <p style="margin-bottom: 0.5rem;"><strong>Want more Btown content?</strong></p>
        <p style="color: #666666; margin-bottom: 1rem;">Check out the full newsletter for local news, events, and more!</p>
        <a href="https://BtownBrief.com" target="_blank" style="
            display: inline-block;
            background-color: #000000;
            color: #ffffff !important;
            padding: 0.75rem 2rem;
            border-radius: 6px;
            text-decoration: none;
            font-weight: 500;
        ">Visit BtownBrief.com →</a>
    </div>
    """, unsafe_allow_html=True)


def show_weekly_leaderboard():
    """Display the weekly leaderboard."""
    conn, error = get_connection()
    if conn and not error:
        leaderboard = get_leaderboard(conn)
        
        if not leaderboard.empty:
            # Display top 10
            display_df = leaderboard.head(10).copy()
            display_df.index = range(1, len(display_df) + 1)
            display_df.index.name = 'Rank'
            
            # Format for display
            if 'Timestamp' in display_df.columns:
                display_df = display_df[['Name', 'Score', 'Time_Taken']]
            
            display_df.columns = ['Name', 'Score', 'Time (s)']
            
            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=False
            )
        else:
            st.info("No entries in the leaderboard yet. You're the first!")
    else:
        st.warning("Could not load leaderboard.")


def show_hall_of_fame_content():
    """Display the Hall of Fame with advanced stats."""
    conn, error = get_connection()
    
    if error or not conn:
        st.warning("Could not load stats. Please try again later.")
        return
    
    # Get global history
    history = get_global_history(conn)
    
    if history.empty:
        st.info("No historical data yet. Play some games to see stats!")
        return
    
    # Sub-tabs for different stats
    stat_tab1, stat_tab2, stat_tab3, stat_tab4 = st.tabs([
        "🎯 Sharpshooters", "⚡ Speed Demons", "📅 Monthly Leaders", "🔥 Streaks"
    ])
    
    with stat_tab1:
        st.markdown("#### 🎯 Sharpshooter Rankings")
        st.markdown("*Highest accuracy across all games*")
        
        accuracy_df = calculate_sharpshooter(history)
        
        if not accuracy_df.empty:
            display_df = accuracy_df.head(10).copy()
            display_df.index = range(1, len(display_df) + 1)
            display_df.index.name = 'Rank'
            display_df = display_df[['Name', 'Accuracy', 'Total_Correct', 'Total_Questions', 'Games_Played']]
            display_df.columns = ['Name', 'Accuracy %', 'Correct', 'Total Qs', 'Games']
            
            st.dataframe(display_df, use_container_width=True, hide_index=False)
        else:
            st.info("No data available yet.")
    
    with stat_tab2:
        st.markdown("#### ⚡ Speed Demon Rankings")
        st.markdown("*Fastest average completion time*")
        
        speed_df = calculate_speed_demon(history)
        
        if not speed_df.empty:
            display_df = speed_df.head(10).copy()
            display_df.index = range(1, len(display_df) + 1)
            display_df.index.name = 'Rank'
            display_df = display_df[['Name', 'Avg_Time', 'Fastest_Time', 'Games_Played']]
            display_df.columns = ['Name', 'Avg Time (s)', 'Best Time (s)', 'Games']
            
            st.dataframe(display_df, use_container_width=True, hide_index=False)
        else:
            st.info("No data available yet.")
    
    with stat_tab3:
        current_month = datetime.now().strftime('%B %Y')
        st.markdown(f"#### 📅 Monthly Leaderboard")
        st.markdown(f"*Top performers for {current_month}*")
        
        monthly_df = calculate_monthly_leaderboard(history)
        
        if not monthly_df.empty:
            display_df = monthly_df.head(10).copy()
            display_df.index = range(1, len(display_df) + 1)
            display_df.index.name = 'Rank'
            display_df = display_df[['Name', 'Total_Score', 'Avg_Score', 'Games_Played']]
            display_df.columns = ['Name', 'Total Score', 'Avg Score', 'Games']
            
            st.dataframe(display_df, use_container_width=True, hide_index=False)
        else:
            st.info(f"No games played in {current_month} yet.")
    
    with stat_tab4:
        st.markdown("#### 🔥 Streak Leaders")
        st.markdown("*Consecutive windows played (Mon-Thu & Fri-Sun)*")
        
        streak_df = calculate_all_streaks(history)
        
        if not streak_df.empty:
            display_df = streak_df.head(10).copy()
            display_df.index = range(1, len(display_df) + 1)
            display_df.index.name = 'Rank'
            display_df.columns = ['Name', 'Current Streak', 'Last Played']
            
            st.dataframe(display_df, use_container_width=True, hide_index=False)
        else:
            st.info("No streak data available yet.")


def show_hall_of_fame_standalone():
    """Display Hall of Fame as a standalone page."""
    st.markdown('<h1 class="main-title">🏆 Hall of Fame</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Btown Brief Trivia — Career Stats & All-Time Rankings</p>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    show_hall_of_fame_content()
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("← Back to Quiz", use_container_width=True):
            st.session_state.show_hall_of_fame = False
            st.rerun()


# ============================================================================
# MAIN APP
# ============================================================================
def main():
    """Main application entry point."""
    init_session_state()
    
    # Check if showing Hall of Fame standalone
    if st.session_state.get('show_hall_of_fame', False):
        show_hall_of_fame_standalone()
    elif not st.session_state.game_started:
        show_welcome_screen()
    elif st.session_state.submitted:
        show_results_screen()
    else:
        show_quiz_screen()


if __name__ == "__main__":
    main()
