"""
Daily Trivia App
A minimalist trivia application with Google Sheets integration.
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import time
from streamlit_gsheets import GSheetsConnection

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
# CUSTOM CSS - Minimalist Black & White with Helvetica
# ============================================================================
st.markdown("""
<style>
    /* Import Helvetica-like font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* ========== FORCE LIGHT THEME ========== */
    /* Override any dark mode settings */
    .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        background-color: #ffffff !important;
        color: #000000 !important;
    }
    
    /* Force all text to be dark - EXCEPT inside buttons and score-display */
    .stApp p, .stApp div, .stApp label {
        color: #000000 !important;
    }
    
    /* Exclude button text from the dark text rule */
    .stApp .stButton p, 
    .stApp .stButton span, 
    .stApp .stButton div,
    .stButton button p,
    .stButton button span,
    .stButton button div {
        color: #ffffff !important;
    }
    
    /* Exclude score-display from dark text rule */
    .stApp .score-display,
    .stApp .score-display *,
    .stApp .score-display p,
    .stApp .score-display div,
    .stApp .score-display span,
    .stApp .score-number,
    .stApp .score-label {
        color: #ffffff !important;
    }
    
    .stApp .score-label {
        color: #cccccc !important;
    }
    
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
    
    /* Timer display */
    .timer-container {
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
    
    .timer-warning {
        background-color: #333333 !important;
        animation: pulse 1s infinite;
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
        'connection_error': None
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
        
        # Get 5 random questions (or all if less than 5)
        n_questions = min(5, len(df))
        if n_questions == 0:
            return None, "No questions found in the sheet."
        
        questions = df.sample(n=n_questions).reset_index(drop=True)
        return questions, None
    except Exception as e:
        return None, f"Error fetching questions: {str(e)}"


def append_to_leaderboard(conn, name, score, time_taken):
    """Append a new entry to the Leaderboard sheet."""
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


# ============================================================================
# TIMER COMPONENT
# ============================================================================
def display_timer():
    """Display and manage the countdown timer."""
    if st.session_state.start_time is None:
        return 60
    
    elapsed = time.time() - st.session_state.start_time
    remaining = max(0, 60 - int(elapsed))
    
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
    st.markdown('<h1 class="main-title">Daily Trivia</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Test your knowledge in 60 seconds</p>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        name = st.text_input(
            "Enter your name to begin",
            placeholder="Your name...",
            key="name_input",
            label_visibility="visible"
        )
        
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
    st.markdown("""
    **How to Play:**
    - Answer 5 trivia questions
    - You have 60 seconds to complete
    - Your score and time will be recorded
    - Compete for the top of the leaderboard!
    """)


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
    
    # Timer display
    remaining = display_timer()
    
    # Auto-submit if time runs out
    if remaining <= 0 and not st.session_state.submitted:
        submit_quiz()
        return
    
    st.markdown("---")
    
    # Display questions
    questions = st.session_state.questions
    
    for idx, row in questions.iterrows():
        st.markdown(f'<div class="question-number">Question {idx + 1} of {len(questions)}</div>', unsafe_allow_html=True)
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
            label_visibility="collapsed"
        )
        
        # Store the answer letter (A, B, C, or D)
        if answer:
            st.session_state.answers[idx] = answer[0]  # Get just the letter
        
        st.markdown("---")
    
    # Submit button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("Submit Answers", use_container_width=True):
            submit_quiz()
    
    # Auto-refresh for timer (every second)
    if remaining > 0:
        time.sleep(0.1)
        st.rerun()


def submit_quiz():
    """Calculate score and submit to leaderboard."""
    # Calculate time taken
    time_taken = int(time.time() - st.session_state.start_time)
    time_taken = min(time_taken, 60)  # Cap at 60 seconds
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
    
    # Save to leaderboard
    conn, error = get_connection()
    if conn and not error:
        append_to_leaderboard(
            conn,
            st.session_state.player_name,
            score,
            time_taken
        )
    
    st.session_state.submitted = True
    st.rerun()


def show_results_screen():
    """Display the results and leaderboard."""
    st.markdown('<h1 class="main-title">Quiz Complete!</h1>', unsafe_allow_html=True)
    
    # Score display
    st.markdown(f"""
    <div class="score-display">
        <div class="score-number">{st.session_state.score}/5</div>
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
    
    # Leaderboard
    st.markdown("### 🏆 Leaderboard")
    
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
    
    st.markdown("---")
    
    # Play again button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("Play Again", use_container_width=True):
            # Reset session state
            for key in ['game_started', 'start_time', 'questions', 'answers', 
                       'submitted', 'score', 'time_taken', 'connection_error']:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()


# ============================================================================
# MAIN APP
# ============================================================================
def main():
    """Main application entry point."""
    init_session_state()
    
    if not st.session_state.game_started:
        show_welcome_screen()
    elif st.session_state.submitted:
        show_results_screen()
    else:
        show_quiz_screen()


if __name__ == "__main__":
    main()
