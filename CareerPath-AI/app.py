import streamlit as st
import time
import uuid
import io
import base64
from streamlit_lottie import st_lottie
from streamlit_extras.add_vertical_space import add_vertical_space
from streamlit_extras.colored_header import colored_header
import requests
import plotly.express as px
import plotly.graph_objects as go
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

from utils.resume_parser import ResumeParser
from utils.ats_scorer import ATSScorer
from utils.ai_service import AIService
from utils.database import DatabaseManager

# Page configuration
st.set_page_config(
    page_title="CareerPath AI",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize services
@st.cache_resource
def init_services():
    return {
        'parser': ResumeParser(),
        'scorer': ATSScorer(),
        'ai': AIService(),
        'db': DatabaseManager()
    }

services = init_services()

# Session state initialization
if 'session_id' not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if 'resume_data' not in st.session_state:
    st.session_state.resume_data = None
if 'ats_result' not in st.session_state:
    st.session_state.ats_result = None
if 'job_match_result' not in st.session_state:
    st.session_state.job_match_result = None
if 'roadmap_data' not in st.session_state:
    st.session_state.roadmap_data = None
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'Resume Analyzer'
if 'batch_results' not in st.session_state:
    st.session_state.batch_results = []
if 'github_profile' not in st.session_state:
    st.session_state.github_profile = None

# Custom CSS for modern dashboard styling
st.markdown("""
<style>
    /* Main container styling */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }
    
    /* Global box sizing */
    * {
        box-sizing: border-box;
    }
    
    /* Card styling */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 16px;
        padding: 1.5rem;
        color: white;
        box-shadow: 0 10px 40px rgba(102, 126, 234, 0.3);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        animation: slideIn 0.5s ease-out;
        width: 100%;
        box-sizing: border-box;
        min-height: 280px;
        display: flex !important;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        text-align: center;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 50px rgba(102, 126, 234, 0.4);
    }
    
    .result-card {
        background: white;
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
        border: 1px solid #e8e8e8;
        margin-bottom: 1rem;
        animation: fadeIn 0.6s ease-out;
        color: #1f1f1f;
        width: 100%;
        box-sizing: border-box;
    }
    
    .result-card h3, .result-card h4, .result-card p, .result-card * {
        color: #1f1f1f;
        word-wrap: break-word;
        overflow-wrap: break-word;
    }
    
    .result-card h3, .result-card h4 {
        margin: 0 0 0.5rem 0;
        width: 100%;
        text-decoration: underline;
        text-decoration-thickness: 2px;
        text-underline-offset: 4px;
    }
    
    .skill-tag {
        display: inline-block;
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        color: white;
        padding: 0.4rem 0.8rem;
        border-radius: 20px;
        margin: 0.2rem;
        font-size: 0.85rem;
        font-weight: 500;
        animation: popIn 0.3s ease-out;
    }
    
    .missing-skill-tag {
        display: inline-block;
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 0.4rem 0.8rem;
        border-radius: 20px;
        margin: 0.2rem;
        font-size: 0.85rem;
        font-weight: 500;
    }
    
    .score-circle {
        width: 120px;
        height: 120px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 2rem;
        font-weight: bold;
        color: white;
        margin: 0 auto;
        animation: scaleIn 0.5s ease-out;
    }
    
    .score-excellent { background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); }
    .score-good { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
    .score-average { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); }
    .score-poor { background: linear-gradient(135deg, #ee0979 0%, #ff6a00 100%); }
    
    .roadmap-step {
        background: white;
        border-left: 4px solid #667eea;
        padding: 1rem 1.5rem;
        margin: 1rem 0;
        border-radius: 0 12px 12px 0;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
        animation: slideInLeft 0.5s ease-out;
        color: #1f1f1f;
        width: 100%;
        box-sizing: border-box;
    }
    
    .roadmap-step h4, .roadmap-step p, .roadmap-step strong {
        color: #1f1f1f;
        width: 100%;
        margin: 0.5rem 0;
    }
    
    .roadmap-step h4 {
        margin: 0 0 0.5rem 0;
    }
    
    .project-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        border-radius: 12px;
        padding: 1.2rem;
        margin: 0.5rem 0;
        transition: transform 0.3s ease;
        animation: fadeInUp 0.5s ease-out;
        color: #1f1f1f;
    }
    
    .project-card h4, .project-card p, .project-card strong {
        color: #1f1f1f;
    }
    
    .project-card:hover {
        transform: scale(1.02);
    }
    
    /* Animations */
    @keyframes slideIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    
    @keyframes popIn {
        0% { opacity: 0; transform: scale(0.8); }
        100% { opacity: 1; transform: scale(1); }
    }
    
    @keyframes scaleIn {
        from { opacity: 0; transform: scale(0.5); }
        to { opacity: 1; transform: scale(1); }
    }
    
    @keyframes slideInLeft {
        from { opacity: 0; transform: translateX(-30px); }
        to { opacity: 1; transform: translateX(0); }
    }
    
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
    }
    
    /* Header styling */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.5rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
    }
    
    .sub-header {
        color: #6c757d;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    
    /* Progress bar styling */
    .stProgress > div > div > div > div {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.6rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4);
    }
    
    /* Match percentage styling */
    .match-high { color: #11998e; }
    .match-medium { color: #667eea; }
    .match-low { color: #f5576c; }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


def load_lottie_url(url: str):
    """Load Lottie animation from URL."""
    try:
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            return r.json()
    except:
        pass
    return None


def animated_metric(value, label, delay=0):
    """Display animated metric with counting effect."""
    placeholder = st.empty()
    if isinstance(value, (int, float)):
        for i in range(0, int(value) + 1, max(1, int(value) // 20)):
            time.sleep(0.02)
            placeholder.metric(label, f"{i}")
        placeholder.metric(label, f"{value}")
    else:
        placeholder.metric(label, value)


def get_score_class(score):
    """Get CSS class based on score."""
    if score >= 75:
        return "score-excellent"
    elif score >= 55:
        return "score-good"
    elif score >= 40:
        return "score-average"
    return "score-poor"


def display_skills_tags(skills, tag_class="skill-tag"):
    """Display skills as styled tags."""
    if skills:
        tags_html = " ".join([f'<span class="{tag_class}">{skill}</span>' for skill in skills])
        st.markdown(f'<div style="margin: 1rem 0;">{tags_html}</div>', unsafe_allow_html=True)


# Sidebar Navigation
with st.sidebar:
    st.markdown('<h1 style="color: #1f1f1f; text-align: center;">🚀 CareerPath AI</h1>', unsafe_allow_html=True)
    st.markdown('<p style="color: #1f1f1f; text-align: center; margin-bottom: 2rem;">Your AI Career Assistant</p>', unsafe_allow_html=True)
    
    add_vertical_space(1)
    
    # Navigation buttons with icons
    nav_items = [
        ('📄', 'Resume Analyzer'),
        ('🎯', 'Job Matcher'),
        ('📊', 'Skill Gap Analysis'),
        ('🗺️', 'Career Roadmap'),
        ('📦', 'Batch Analysis'),
        ('🐙', 'Portfolio Analysis'),
        ('📥', 'Export Report')
    ]
    
    for icon, option in nav_items:
        # Skip Projects if not available
        if option == 'Projects' and (not st.session_state.resume_data or not st.session_state.resume_data.get('has_projects')):
            continue
        if st.button(f"{icon} {option}", key=f"nav_{option}", use_container_width=True):
            st.session_state.current_page = option
            st.rerun()
    
    # Only show Projects if resume has projects
    if st.session_state.resume_data and st.session_state.resume_data.get('has_projects'):
        if st.button("💼 Projects", key="nav_Projects", use_container_width=True):
            st.session_state.current_page = 'Projects'
            st.rerun()
    
    add_vertical_space(2)
    
    # Status indicators
    st.markdown("---")
    st.markdown("### 📊 Status")
    
    if st.session_state.resume_data:
        st.success("✅ Resume Uploaded")
    else:
        st.info("📤 Upload a resume to start")
    
    if services['ai'].is_available():
        st.success("✅ AI Service Ready")
    else:
        st.warning("⚠️ AI Service Unavailable")
    
    if services['db'].is_available():
        st.success("✅ Database Connected")


# Main Content Area
def resume_analyzer_page():
    """Resume Analyzer page."""
    colored_header(
        label="Resume Analyzer",
        description="Upload your resume for ATS scoring and analysis",
        color_name="violet-70"
    )
    
    add_vertical_space(1)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 📤 Upload Resume")
        uploaded_file = st.file_uploader(
            "Choose a PDF or DOCX file",
            type=['pdf', 'docx'],
            help="Upload your resume in PDF or DOCX format for analysis"
        )
        
        if uploaded_file:
            with st.spinner("Analyzing your resume..."):
                # Show progress bar
                progress_bar = st.progress(0)
                
                try:
                    # Read file content
                    file_content = uploaded_file.read()
                    progress_bar.progress(20)
                    
                    # Parse resume
                    resume_data = services['parser'].parse_resume(file_content, uploaded_file.name)
                    progress_bar.progress(50)
                    
                    # Calculate ATS score
                    ats_result = services['scorer'].calculate_ats_score(
                        resume_data['raw_text'],
                        resume_data['skills']
                    )
                    progress_bar.progress(80)
                    
                    # Store in session state
                    st.session_state.resume_data = resume_data
                    st.session_state.ats_result = ats_result
                    
                    # Save to database
                    services['db'].save_resume_analysis(
                        st.session_state.session_id,
                        uploaded_file.name,
                        ats_result,
                        resume_data['skills']
                    )
                    
                    progress_bar.progress(100)
                    time.sleep(0.3)
                    progress_bar.empty()
                    
                    st.success("✅ Resume analyzed successfully!")
                    
                except Exception as e:
                    progress_bar.empty()
                    st.error(f"❌ Error analyzing resume: {str(e)}")
    
    with col2:
        # Lottie animation
        lottie_url = "https://assets5.lottiefiles.com/packages/lf20_v1yudlrx.json"
        lottie_json = load_lottie_url(lottie_url)
        if lottie_json:
            st_lottie(lottie_json, height=200, key="resume_lottie")
    
    # Display Results
    if st.session_state.ats_result:
        add_vertical_space(2)
        
        st.markdown("---")
        st.markdown("### 📊 Analysis Results")
        
        ats = st.session_state.ats_result
        
        # ATS Score at top (full width)
        score_class = get_score_class(ats['total_score'])
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 16px; padding: 1.5rem; color: white; box-shadow: 0 10px 40px rgba(102, 126, 234, 0.3); width: 100%; min-height: 280px; display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center; box-sizing: border-box;">
            <div class="score-circle {score_class}">{ats['total_score']}</div>
            <h4 style="margin-top: 1rem; margin-bottom: 0; color: white;">ATS Score</h4>
            <p style="margin: 0.5rem 0 0 0; color: white;">Grade: {ats['grade']} ({ats['grade_text']})</p>
        </div>
        """, unsafe_allow_html=True)
        
        add_vertical_space(1)
        
        # Keywords, Formatting, Skills below (3 columns)
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 16px; padding: 1.5rem; color: white; box-shadow: 0 10px 40px rgba(102, 126, 234, 0.3); width: 100%; min-height: 280px; display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center; box-sizing: border-box;">
                <h3>📝 Keywords</h3>
                <h2>{ats['breakdown']['keyword_score']}/25</h2>
                <p>Action verbs & keywords</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 16px; padding: 1.5rem; color: white; box-shadow: 0 10px 40px rgba(102, 126, 234, 0.3); width: 100%; min-height: 280px; display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center; box-sizing: border-box;">
                <h3>📐 Formatting</h3>
                <h2>{ats['breakdown']['formatting_score']}/25</h2>
                <p>Structure & sections</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 16px; padding: 1.5rem; color: white; box-shadow: 0 10px 40px rgba(102, 126, 234, 0.3); width: 100%; min-height: 280px; display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center; box-sizing: border-box;">
                <h3>💼 Skills</h3>
                <h2>{ats['breakdown']['skill_score']}/25</h2>
                <p>Coverage & diversity</p>
            </div>
            """, unsafe_allow_html=True)
        
        add_vertical_space(2)
        
        # Skills detected and Suggestions
        col1, col2 = st.columns(2)
        
        # Add custom spacing between columns
        st.markdown("""
        <style>
        [data-testid="column"]:nth-child(1) { margin-right: 2rem; }
        [data-testid="column"]:nth-child(2) { margin-left: 2rem; }
        </style>
        """, unsafe_allow_html=True)
        
        with col1:
            skills_html = '<div class="result-card" style="display: flex; flex-direction: column;"><h4 style="margin: 0 0 1rem 0; color: #667eea; text-decoration: underline; text-decoration-thickness: 2px; text-underline-offset: 4px;">✅ Skills Detected</h4>'
            if st.session_state.resume_data['skills']:
                skills_list = " ".join([f'<span class="skill-tag">{skill}</span>' for skill in st.session_state.resume_data['skills'][:15]])
                skills_html += f'<div style="display: flex; flex-wrap: wrap; gap: 0.5rem;">{skills_list}</div>'
            else:
                skills_html += '<p style="color: #1f1f1f;">No specific skills detected</p>'
            skills_html += '</div>'
            st.markdown(skills_html, unsafe_allow_html=True)
        
        with col2:
            suggestions_html = '<div class="result-card" style="display: flex; flex-direction: column;"><h4 style="margin: 0 0 1rem 0; color: #667eea; text-decoration: underline; text-decoration-thickness: 2px; text-underline-offset: 4px;">💡 Suggestions</h4><div style="display: flex; flex-direction: column; gap: 0.75rem;">'
            if ats['suggestions']:
                for suggestion in ats['suggestions'][:5]:
                    suggestions_html += f'<p style="margin: 0; color: #1f1f1f;">• {suggestion}</p>'
            else:
                suggestions_html += '<p style="margin: 0; color: #1f1f1f;">Your resume looks great!</p>'
            suggestions_html += '</div></div>'
            st.markdown(suggestions_html, unsafe_allow_html=True)


def job_matcher_page():
    """Job Matcher page."""
    colored_header(
        label="Job Matcher",
        description="Compare your skills with job requirements",
        color_name="blue-70"
    )
    
    add_vertical_space(1)
    
    if not st.session_state.resume_data:
        st.warning("📤 Please upload your resume first in the Resume Analyzer section.")
        return
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 📋 Job Description")
        job_description = st.text_area(
            "Paste the job description here",
            height=200,
            placeholder="Paste the full job description to compare with your resume..."
        )
        
        job_title = st.text_input("Job Title (optional)", placeholder="e.g., Senior Software Engineer")
        
        if st.button("🎯 Analyze Match", use_container_width=True):
            if job_description:
                with st.spinner("Analyzing job match..."):
                    progress_bar = st.progress(0)
                    
                    for i in range(0, 60, 10):
                        time.sleep(0.1)
                        progress_bar.progress(i)
                    
                    match_result = services['scorer'].calculate_job_match(
                        st.session_state.resume_data['raw_text'],
                        st.session_state.resume_data['skills'],
                        job_description
                    )
                    
                    progress_bar.progress(80)
                    
                    st.session_state.job_match_result = match_result
                    
                    # Save to database
                    services['db'].save_job_match(
                        st.session_state.session_id,
                        job_title or "Untitled Position",
                        job_description,
                        match_result
                    )
                    
                    progress_bar.progress(100)
                    time.sleep(0.2)
                    progress_bar.empty()
            else:
                st.warning("Please enter a job description to analyze.")
    
    with col2:
        lottie_url = "https://assets9.lottiefiles.com/packages/lf20_kkflmtur.json"
        lottie_json = load_lottie_url(lottie_url)
        if lottie_json:
            st_lottie(lottie_json, height=200, key="job_lottie")
    
    # Display Match Results
    if st.session_state.job_match_result:
        add_vertical_space(2)
        st.markdown("---")
        
        match = st.session_state.job_match_result
        
        # Overall match display
        col1, col2, col3 = st.columns(3)
        
        with col1:
            match_class = "match-high" if match['overall_match'] >= 70 else "match-medium" if match['overall_match'] >= 50 else "match-low"
            st.markdown(f"""
            <div class="metric-card" style="text-align: center;">
                <h1 class="{match_class}" style="font-size: 3rem; -webkit-text-fill-color: white;">{match['overall_match']}%</h1>
                <h3 style="color: #1f1f1f;">Overall Match</h3>
                <p style="color: #1f1f1f;">{match['match_level']}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <h3 style="color: #1f1f1f;">🔑 Keyword Match</h3>
                <h2 style="color: #1f1f1f;">{match['keyword_match']}%</h2>
                <p style="color: #1f1f1f;">Job description keywords</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <h3 style="color: #1f1f1f;">💻 Skill Match</h3>
                <h2 style="color: #1f1f1f;">{match['skill_match']}%</h2>
                <p style="color: #1f1f1f;">Required skills coverage</p>
            </div>
            """, unsafe_allow_html=True)
        
        add_vertical_space(1)
        st.markdown("### 📊 Match Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            matched_html = '<div class="result-card" style="display: flex; flex-direction: column;"><h4 style="margin: 0 0 0.8rem 0; color: #667eea; text-decoration: underline; text-decoration-thickness: 2px; text-underline-offset: 4px;">✅ Matched Skills</h4>'
            if match['matched_skills']:
                matched_html += '<div style="display: flex; flex-wrap: wrap; gap: 0.5rem;">'
                for skill in match['matched_skills']:
                    matched_html += f'<span class="skill-tag">{skill}</span>'
                matched_html += '</div>'
            else:
                matched_html += '<p style="margin: 0; color: #1f1f1f;">No direct skill matches found</p>'
            matched_html += '</div>'
            st.markdown(matched_html, unsafe_allow_html=True)
        
        with col2:
            missing_html = '<div class="result-card" style="display: flex; flex-direction: column;"><h4 style="margin: 0 0 0.8rem 0; color: #667eea; text-decoration: underline; text-decoration-thickness: 2px; text-underline-offset: 4px;">⚠️ Missing Skills</h4>'
            if match['missing_skills']:
                missing_html += '<div style="display: flex; flex-wrap: wrap; gap: 0.5rem;">'
                for skill in match['missing_skills']:
                    missing_html += f'<span class="missing-skill-tag">{skill}</span>'
                missing_html += '</div>'
            else:
                missing_html += '<p style="margin: 0; color: #1f1f1f;">You have all required skills!</p>'
            missing_html += '</div>'
            st.markdown(missing_html, unsafe_allow_html=True)
        
        add_vertical_space(1)
        
        # Recommendation
        rec_html = '<div class="result-card" style="display: flex; flex-direction: column;"><h4 style="margin: 0 0 0.8rem 0; color: #667eea; text-decoration: underline; text-decoration-thickness: 2px; text-underline-offset: 4px;">💡 Recommendation</h4>'
        rec_html += f'<p style="margin: 0; color: #1f1f1f;">{match["recommendation"]}</p>'
        rec_html += '</div>'
        st.markdown(rec_html, unsafe_allow_html=True)


def career_roadmap_page():
    """Career Roadmap page."""
    colored_header(
        label="Career Path Planner",
        description="Get a personalized roadmap to your dream career",
        color_name="green-70"
    )
    
    add_vertical_space(1)
    
    if not st.session_state.resume_data:
        st.warning("📤 Please upload your resume first in the Resume Analyzer section.")
        return
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        target_role = st.text_input(
            "Target Role",
            placeholder="e.g., Senior Data Scientist, Engineering Manager"
        )
        
        job_description = st.text_area(
            "Job Description (optional)",
            height=150,
            placeholder="Paste a job description for more tailored recommendations..."
        )
        
        if st.button("🗺️ Generate Career Roadmap", use_container_width=True):
            with st.spinner("Generating your personalized career roadmap..."):
                progress_bar = st.progress(0)
                
                for i in range(0, 70, 5):
                    time.sleep(0.05)
                    progress_bar.progress(i)
                
                roadmap = services['ai'].generate_career_roadmap(
                    st.session_state.resume_data,
                    job_description if job_description else None,
                    target_role if target_role else None
                )
                
                progress_bar.progress(90)
                
                st.session_state.roadmap_data = roadmap
                
                # Save to database
                services['db'].save_career_roadmap(
                    st.session_state.session_id,
                    roadmap
                )
                
                progress_bar.progress(100)
                time.sleep(0.2)
                progress_bar.empty()
    
    with col2:
        lottie_url = "https://assets2.lottiefiles.com/packages/lf20_inti4oxf.json"
        lottie_json = load_lottie_url(lottie_url)
        if lottie_json:
            st_lottie(lottie_json, height=200, key="roadmap_lottie")
    
    # Display Roadmap
    if st.session_state.roadmap_data:
        add_vertical_space(2)
        st.markdown("---")
        
        roadmap = st.session_state.roadmap_data
        
        # Overview metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <h3>📍 Current Level</h3>
                <h4>{roadmap.get('current_level', 'Not specified')}</h4>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <h3>🎯 Target Role</h3>
                <h4>{roadmap.get('target_role', 'Not specified')}</h4>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <h3>⏱️ Timeline</h3>
                <h4>{roadmap.get('timeline', 'Not specified')}</h4>
            </div>
            """, unsafe_allow_html=True)
        
        add_vertical_space(2)
        
        # Roadmap Steps
        st.markdown("### 🛤️ Your Career Roadmap")
        
        steps = roadmap.get('roadmap_steps', [])
        for i, step in enumerate(steps):
            time.sleep(0.2)  # Staggered animation
            st.markdown(f"""
            <div class="roadmap-step" style="animation-delay: {i * 0.2}s;">
                <h4>Step {step.get('step', i+1)}: {step.get('title', 'Step')}</h4>
                <p><strong>Duration:</strong> {step.get('duration', 'TBD')}</p>
                <p>{step.get('description', '')}</p>
                <p><strong>Skills to learn:</strong> {', '.join(step.get('skills_to_learn', []))}</p>
            </div>
            """, unsafe_allow_html=True)
        
        add_vertical_space(1)
        
        col1, col2 = st.columns(2)
        
        with col1:
            roles_html = '<div class="result-card" style="display: flex; flex-direction: column;"><h4 style="margin: 0 0 0.8rem 0; color: #667eea; text-decoration: underline; text-decoration-thickness: 2px; text-underline-offset: 4px;">🚀 Next Possible Roles</h4><div style="display: flex; flex-direction: column; gap: 0.5rem;">'
            next_roles = roadmap.get('next_roles', [])
            for role in next_roles:
                roles_html += f'<p style="margin: 0; color: #1f1f1f;">• {role}</p>'
            roles_html += '</div></div>'
            st.markdown(roles_html, unsafe_allow_html=True)
        
        with col2:
            skills_html = '<div class="result-card" style="display: flex; flex-direction: column;"><h4 style="margin: 0 0 0.8rem 0; color: #667eea; text-decoration: underline; text-decoration-thickness: 2px; text-underline-offset: 4px;">📚 Key Skills</h4>'
            skills = roadmap.get('key_skills_to_develop', [])
            skills_tags = " ".join([f'<span class="skill-tag">{skill}</span>' for skill in skills])
            skills_html += f'<div style="display: flex; flex-wrap: wrap; gap: 0.5rem;">{skills_tags}</div></div>'
            st.markdown(skills_html, unsafe_allow_html=True)
        
        add_vertical_space(1)
        
        # Portfolio Ideas
        portfolio_html = '<div class="result-card" style="display: flex; flex-direction: column;"><h4 style="margin: 0 0 0.8rem 0; color: #667eea; text-decoration: underline; text-decoration-thickness: 2px; text-underline-offset: 4px;">💡 Portfolio Ideas</h4><div style="display: flex; flex-direction: column; gap: 0.5rem;">'
        portfolio_ideas = roadmap.get('portfolio_ideas', [])
        for idea in portfolio_ideas:
            portfolio_html += f'<p style="margin: 0; color: #1f1f1f;">• {idea}</p>'
        portfolio_html += '</div></div>'
        st.markdown(portfolio_html, unsafe_allow_html=True)
        
        add_vertical_space(1)
        
        # Learning Resources
        resources_html = '<div class="result-card" style="display: flex; flex-direction: column;"><h4 style="margin: 0 0 0.8rem 0; color: #667eea; text-decoration: underline; text-decoration-thickness: 2px; text-underline-offset: 4px;">📖 Learning Resources</h4><div style="display: flex; flex-direction: column; gap: 0.5rem;">'
        resources = roadmap.get('learning_resources', [])
        for resource in resources:
            if isinstance(resource, dict):
                resources_html += f'<p style="margin: 0; color: #1f1f1f;">• <strong>{resource.get("name", "Resource")}</strong> ({resource.get("type", "Resource")})</p>'
            else:
                resources_html += f'<p style="margin: 0; color: #1f1f1f;">• {resource}</p>'
        resources_html += '</div></div>'
        st.markdown(resources_html, unsafe_allow_html=True)


def projects_page():
    """Projects page - only shown if resume has projects."""
    colored_header(
        label="Your Projects",
        description="Projects extracted from your resume",
        color_name="orange-70"
    )
    
    add_vertical_space(1)
    
    if not st.session_state.resume_data:
        st.warning("📤 Please upload your resume first.")
        return
    
    projects = st.session_state.resume_data.get('projects', [])
    
    if not projects:
        st.info("No projects were detected in your resume.")
        return
    
    st.markdown(f"### 💼 {len(projects)} Project(s) Found")
    
    add_vertical_space(1)
    
    for i, project in enumerate(projects):
        time.sleep(0.15)  # Staggered animation
        st.markdown(f"""
        <div class="project-card" style="animation-delay: {i * 0.15}s;">
            <h4>🔹 {project.get('name', 'Untitled Project')}</h4>
            <p>{project.get('description', 'No description available')}</p>
        </div>
        """, unsafe_allow_html=True)
    
    add_vertical_space(1)
    
    # Project enhancement suggestions
    tips_html = '''<div class="result-card" style="display: flex; flex-direction: column;"><h4 style="margin: 0 0 0.8rem 0; color: #667eea; text-decoration: underline; text-decoration-thickness: 2px; text-underline-offset: 4px;">💡 Project Enhancement Tips</h4><div style="display: flex; flex-direction: column; gap: 0.5rem;">
    <p style="margin: 0;">• Add GitHub links to your projects for credibility</p>
    <p style="margin: 0;">• Include metrics and outcomes (e.g., "Improved performance by 40%")</p>
    <p style="margin: 0;">• Highlight technologies used in each project</p>
    <p style="margin: 0;">• Add live demo links if available</p>
    <p style="margin: 0;">• Consider creating a portfolio website to showcase your work</p>
    </div></div>'''
    st.markdown(tips_html, unsafe_allow_html=True)


def skill_gap_analysis_page():
    """Skill Gap Analysis page with interactive visualizations."""
    colored_header(
        label="Skill Gap Analysis",
        description="Visualize your skill gaps with interactive charts",
        color_name="red-70"
    )
    
    add_vertical_space(1)
    
    if not st.session_state.ats_result:
        st.warning("📤 Please upload and analyze your resume first in the Resume Analyzer section.")
        return
    
    ats = st.session_state.ats_result
    resume_data = st.session_state.resume_data
    
    # ATS Score Breakdown Radar Chart
    st.markdown("### 📊 ATS Score Breakdown")
    
    categories = ['Keywords', 'Formatting', 'Skills', 'Experience']
    scores = [
        ats['breakdown']['keyword_score'],
        ats['breakdown']['formatting_score'],
        ats['breakdown']['skill_score'],
        ats['breakdown']['experience_score']
    ]
    max_score = 25
    
    fig_radar = go.Figure()
    fig_radar.add_trace(go.Scatterpolar(
        r=scores + [scores[0]],
        theta=categories + [categories[0]],
        fill='toself',
        name='Your Score',
        line_color='#667eea',
        fillcolor='rgba(102, 126, 234, 0.3)'
    ))
    fig_radar.add_trace(go.Scatterpolar(
        r=[max_score] * 5,
        theta=categories + [categories[0]],
        fill='toself',
        name='Maximum Score',
        line_color='#11998e',
        fillcolor='rgba(17, 153, 142, 0.1)'
    ))
    fig_radar.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 30])),
        showlegend=True,
        title="Score Distribution (out of 25 each)",
        height=400
    )
    st.plotly_chart(fig_radar, use_container_width=True)
    
    add_vertical_space(1)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Skills by Category Bar Chart
        st.markdown("### 💼 Skills by Category")
        skill_details = ats['details']['skills']
        categories_data = skill_details.get('skill_categories', {})
        
        cat_names = []
        cat_counts = []
        for cat, data in categories_data.items():
            cat_names.append(cat.replace('_', ' ').title())
            cat_counts.append(data.get('count', 0))
        
        fig_bar = px.bar(
            x=cat_names,
            y=cat_counts,
            color=cat_counts,
            color_continuous_scale=['#f5576c', '#f093fb', '#667eea', '#11998e'],
            labels={'x': 'Category', 'y': 'Skills Count'},
            title='Skills Distribution by Category'
        )
        fig_bar.update_layout(height=350, showlegend=False)
        st.plotly_chart(fig_bar, use_container_width=True)
    
    with col2:
        # Score Gauge Chart
        st.markdown("### 🎯 Overall ATS Score")
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=ats['total_score'],
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "ATS Compatibility"},
            delta={'reference': 70, 'increasing': {'color': "#11998e"}},
            gauge={
                'axis': {'range': [None, 100], 'tickwidth': 1},
                'bar': {'color': "#667eea"},
                'bgcolor': "white",
                'borderwidth': 2,
                'bordercolor': "gray",
                'steps': [
                    {'range': [0, 40], 'color': '#f5576c'},
                    {'range': [40, 55], 'color': '#f093fb'},
                    {'range': [55, 70], 'color': '#667eea'},
                    {'range': [70, 100], 'color': '#11998e'}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 70
                }
            }
        ))
        fig_gauge.update_layout(height=350)
        st.plotly_chart(fig_gauge, use_container_width=True)
    
    add_vertical_space(1)
    
    # Job Match Comparison (if available)
    if st.session_state.job_match_result:
        st.markdown("### 🎯 Job Match Skill Comparison")
        match = st.session_state.job_match_result
        
        matched = len(match.get('matched_skills', []))
        missing = len(match.get('missing_skills', []))
        
        fig_pie = px.pie(
            values=[matched, missing],
            names=['Matched Skills', 'Missing Skills'],
            color_discrete_sequence=['#11998e', '#f5576c'],
            title='Skills Match Overview'
        )
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        fig_pie.update_layout(height=350)
        st.plotly_chart(fig_pie, use_container_width=True)
        
        # Skill gap details
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="result-card">', unsafe_allow_html=True)
            st.markdown("#### ✅ Skills You Have")
            display_skills_tags(match.get('matched_skills', []))
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="result-card">', unsafe_allow_html=True)
            st.markdown("#### ❌ Skills to Develop")
            display_skills_tags(match.get('missing_skills', []), "missing-skill-tag")
            st.markdown('</div>', unsafe_allow_html=True)
    
    # Improvement Recommendations
    st.markdown("### 💡 Improvement Recommendations")
    
    recommendations = []
    if ats['breakdown']['keyword_score'] < 15:
        recommendations.append(("Keywords", "Add more action verbs and industry-specific keywords to your resume.", "High"))
    if ats['breakdown']['formatting_score'] < 15:
        recommendations.append(("Formatting", "Improve resume structure with clear sections and bullet points.", "High"))
    if ats['breakdown']['skill_score'] < 15:
        recommendations.append(("Skills", "Expand your skills section with more technical and soft skills.", "Medium"))
    if ats['breakdown']['experience_score'] < 15:
        recommendations.append(("Experience", "Add quantifiable achievements and metrics to your experience.", "High"))
    
    if recommendations:
        for area, suggestion, priority in recommendations:
            priority_color = "#f5576c" if priority == "High" else "#f093fb"
            st.markdown(f"""
            <div class="result-card" style="border-left: 4px solid {priority_color}; display: flex; flex-direction: column;">
                <strong style="color: #1f1f1f;">{area}</strong> <span style="color: {priority_color}; font-size: 0.9rem;">({priority} Priority)</span>
                <p style="margin: 0.5rem 0 0 0; color: #1f1f1f;">{suggestion}</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.success("Your resume is well-optimized! Keep updating it with new achievements.")


def batch_analysis_page():
    """Batch Resume Analysis page."""
    colored_header(
        label="Batch Resume Analysis",
        description="Analyze multiple resumes at once",
        color_name="yellow-70"
    )
    
    add_vertical_space(1)
    
    st.markdown("### 📦 Upload Multiple Resumes")
    st.info("Upload up to 10 resumes for batch analysis. Supported formats: PDF, DOCX")
    
    uploaded_files = st.file_uploader(
        "Choose resume files",
        type=['pdf', 'docx'],
        accept_multiple_files=True,
        help="Upload multiple resumes for batch analysis"
    )
    
    if uploaded_files:
        if len(uploaded_files) > 10:
            st.warning("Maximum 10 files allowed. Only the first 10 will be processed.")
            uploaded_files = uploaded_files[:10]
        
        if st.button("🔍 Analyze All Resumes", use_container_width=True):
            results = []
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for i, file in enumerate(uploaded_files):
                status_text.text(f"Analyzing {file.name}...")
                try:
                    file_content = file.read()
                    resume_data = services['parser'].parse_resume(file_content, file.name)
                    ats_result = services['scorer'].calculate_ats_score(
                        resume_data['raw_text'],
                        resume_data['skills']
                    )
                    
                    results.append({
                        'filename': file.name,
                        'ats_score': ats_result['total_score'],
                        'grade': ats_result['grade'],
                        'skills_count': len(resume_data['skills']),
                        'skills': resume_data['skills'][:10],
                        'suggestions': ats_result['suggestions'][:3]
                    })
                except Exception as e:
                    results.append({
                        'filename': file.name,
                        'error': str(e)
                    })
                
                progress_bar.progress((i + 1) / len(uploaded_files))
            
            progress_bar.empty()
            status_text.empty()
            st.session_state.batch_results = results
            st.success(f"✅ Analyzed {len(results)} resumes!")
    
    # Display batch results
    if st.session_state.batch_results:
        st.markdown("---")
        st.markdown("### 📊 Batch Analysis Results")
        
        # Summary chart
        valid_results = [r for r in st.session_state.batch_results if 'error' not in r]
        
        if valid_results:
            fig = px.bar(
                x=[r['filename'][:20] for r in valid_results],
                y=[r['ats_score'] for r in valid_results],
                color=[r['ats_score'] for r in valid_results],
                color_continuous_scale=['#f5576c', '#f093fb', '#667eea', '#11998e'],
                labels={'x': 'Resume', 'y': 'ATS Score'},
                title='ATS Scores Comparison'
            )
            fig.update_layout(height=350)
            st.plotly_chart(fig, use_container_width=True)
        
        # Detailed results
        for result in st.session_state.batch_results:
            if 'error' in result:
                st.markdown(f"""
                <div class="result-card" style="border-left: 4px solid #f5576c;">
                    <h4>❌ {result['filename']}</h4>
                    <p style="color: #f5576c;">Error: {result['error']}</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                score_color = "#11998e" if result['ats_score'] >= 70 else "#667eea" if result['ats_score'] >= 55 else "#f5576c"
                st.markdown(f"""
                <div class="result-card" style="display: flex; flex-direction: column;">
                    <h4 style="margin: 0 0 0.8rem 0; color: #667eea;">📄 {result['filename']}</h4>
                    <p style="margin: 0.3rem 0; color: #1f1f1f;"><strong>ATS Score:</strong> <span style="color: {score_color}; font-size: 1.2rem; font-weight: bold;">{result['ats_score']}</span> (Grade: {result['grade']})</p>
                    <p style="margin: 0.3rem 0; color: #1f1f1f;"><strong>Skills Found:</strong> {result['skills_count']}</p>
                </div>
                """, unsafe_allow_html=True)
                
                with st.expander(f"View details for {result['filename'][:30]}"):
                    st.markdown("**Top Skills:**")
                    display_skills_tags(result['skills'])
                    st.markdown("**Top Suggestions:**")
                    for suggestion in result['suggestions']:
                        st.markdown(f"• {suggestion}")


def portfolio_analysis_page():
    """GitHub/Kaggle Portfolio Analysis page."""
    colored_header(
        label="Portfolio Analysis",
        description="Analyze your GitHub or Kaggle profile for portfolio recommendations",
        color_name="green-70"
    )
    
    add_vertical_space(1)
    
    st.markdown("### 🐙 GitHub Profile Analysis")
    
    github_username = st.text_input(
        "Enter your GitHub username",
        placeholder="e.g., octocat"
    )
    
    if st.button("🔍 Analyze GitHub Profile", use_container_width=True):
        if github_username:
            with st.spinner("Fetching GitHub profile..."):
                try:
                    # Fetch GitHub profile
                    response = requests.get(f"https://api.github.com/users/{github_username}", timeout=10)
                    
                    if response.status_code == 200:
                        user_data = response.json()
                        
                        # Fetch repos
                        repos_response = requests.get(
                            f"https://api.github.com/users/{github_username}/repos?sort=updated&per_page=10",
                            timeout=10
                        )
                        repos = repos_response.json() if repos_response.status_code == 200 else []
                        
                        st.session_state.github_profile = {
                            'user': user_data,
                            'repos': repos
                        }
                        st.success("✅ Profile analyzed successfully!")
                    else:
                        st.error("❌ GitHub user not found. Please check the username.")
                except Exception as e:
                    st.error(f"❌ Error fetching profile: {str(e)}")
        else:
            st.warning("Please enter a GitHub username.")
    
    # Display GitHub profile
    if st.session_state.github_profile:
        user = st.session_state.github_profile['user']
        repos = st.session_state.github_profile['repos']
        
        add_vertical_space(1)
        st.markdown("---")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <h3>📦 Repositories</h3>
                <h2>{user.get('public_repos', 0)}</h2>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <h3>👥 Followers</h3>
                <h2>{user.get('followers', 0)}</h2>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <h3>👤 Following</h3>
                <h2>{user.get('following', 0)}</h2>
            </div>
            """, unsafe_allow_html=True)
        
        add_vertical_space(2)
        
        # Recent repositories
        st.markdown("### 📂 Recent Repositories")
        
        if repos:
            # Language distribution
            languages = {}
            for repo in repos:
                lang = repo.get('language')
                if lang:
                    languages[lang] = languages.get(lang, 0) + 1
            
            if languages:
                fig = px.pie(
                    values=list(languages.values()),
                    names=list(languages.keys()),
                    title='Programming Languages Distribution',
                    color_discrete_sequence=px.colors.qualitative.Set3
                )
                fig.update_layout(
                    height=400,
                    font=dict(size=12, color='#1f1f1f', family='Arial'),
                    title_font_size=16,
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)'
                )
                fig.update_traces(
                    textposition='auto',
                    textinfo='label+percent',
                    textfont=dict(size=11, color='#1f1f1f')
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # Repository cards
            for repo in repos[:5]:
                stars = repo.get('stargazers_count', 0)
                forks = repo.get('forks_count', 0)
                lang = repo.get('language', 'Unknown')
                
                st.markdown(f"""
                <div class="project-card">
                    <h4>📁 {repo.get('name', 'Unnamed')}</h4>
                    <p>{repo.get('description', 'No description')}</p>
                    <p>⭐ {stars} | 🍴 {forks} | 💻 {lang}</p>
                </div>
                """, unsafe_allow_html=True)
        
        # Portfolio recommendations
        recommendations = []
        if user.get('public_repos', 0) < 5:
            recommendations.append("Create more public repositories to showcase your work")
        if not user.get('bio'):
            recommendations.append("Add a bio to your GitHub profile")
        if user.get('followers', 0) < 10:
            recommendations.append("Engage more with the community to gain followers")
        
        total_stars = sum(repo.get('stargazers_count', 0) for repo in repos)
        if total_stars < 10:
            recommendations.append("Work on projects that can gain more stars")
        
        if not recommendations:
            recommendations = ["Your GitHub profile looks great!", "Keep contributing to open source", "Document your projects well"]
        
        rec_html = '<div class="result-card" style="display: flex; flex-direction: column;"><h4 style="margin: 0 0 0.8rem 0; color: #667eea;">💡 Portfolio Recommendations</h4><div style="display: flex; flex-direction: column; gap: 0.5rem;">'
        for rec in recommendations:
            rec_html += f'<p style="margin: 0; color: #1f1f1f;">• {rec}</p>'
        rec_html += '</div></div>'
        st.markdown(rec_html, unsafe_allow_html=True)
    
    add_vertical_space(1)
    
    # Kaggle section
    st.markdown("### 📊 Kaggle Profile")
    st.info("For Kaggle profile analysis, please visit your Kaggle profile and review your competitions, datasets, and notebooks. Add these achievements to your resume for better visibility.")


def export_report_page():
    """Export Analysis Report page."""
    colored_header(
        label="Export Report",
        description="Download your analysis results as a PDF report",
        color_name="blue-70"
    )
    
    add_vertical_space(1)
    
    if not st.session_state.ats_result:
        st.warning("📤 Please analyze your resume first before exporting a report.")
        return
    
    st.markdown("### 📥 Generate PDF Report")
    st.info("Export your complete analysis including ATS score, skill analysis, and recommendations.")
    
    report_options = st.multiselect(
        "Select sections to include:",
        ["ATS Score Analysis", "Skills Overview", "Improvement Suggestions", "Job Match Results", "Career Roadmap"],
        default=["ATS Score Analysis", "Skills Overview", "Improvement Suggestions"]
    )
    
    if st.button("📄 Generate PDF Report", use_container_width=True):
        with st.spinner("Generating PDF report..."):
            try:
                pdf_buffer = generate_pdf_report(report_options)
                
                st.success("✅ Report generated successfully!")
                
                st.download_button(
                    label="📥 Download PDF Report",
                    data=pdf_buffer,
                    file_name="careerpath_ai_report.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"❌ Error generating report: {str(e)}")
    
    add_vertical_space(2)
    
    # Preview section
    st.markdown("### 👁️ Report Preview")
    
    if st.session_state.ats_result and st.session_state.resume_data:
        ats = st.session_state.ats_result
        resume_data = st.session_state.resume_data
        
        skills_list = resume_data.get('skills', [])
        skills_text = ", ".join(skills_list[:10]) if skills_list else "No skills detected"
        recommendations_list = ats.get('suggestions', [])
        
        # Display sections based on selected options
        if "ATS Score Analysis" in report_options:
            st.markdown('<div class="result-card" style="display: flex; flex-direction: column;"><h4 style="margin: 0 0 1rem 0; color: #667eea; text-decoration: underline; text-decoration-thickness: 2px; text-underline-offset: 4px;">Overall ATS Score</h4><p style="color: #1f1f1f; margin: 0; line-height: 1.6;">Your ATS compatibility score is <strong>' + str(ats['total_score']) + '/100 (Grade: ' + ats['grade'] + ')</strong>. This score reflects how well your resume is optimized for applicant tracking systems. <strong>' + ats['grade_text'] + '</strong> resume quality with room for improvement.</p></div>', unsafe_allow_html=True)
            st.markdown("")
        
        if "Skills Overview" in report_options:
            st.markdown('<div class="result-card" style="display: flex; flex-direction: column;"><h4 style="margin: 0 0 1rem 0; color: #667eea; text-decoration: underline; text-decoration-thickness: 2px; text-underline-offset: 4px;">Skills Overview</h4><p style="color: #1f1f1f; margin: 0; line-height: 1.6;">We detected <strong>' + str(len(skills_list)) + ' key skills</strong> in your resume: ' + skills_text + '</p></div>', unsafe_allow_html=True)
            st.markdown("")
        
        if "Improvement Suggestions" in report_options:
            suggestions_html = '<div class="result-card" style="display: flex; flex-direction: column;"><h4 style="margin: 0 0 1rem 0; color: #667eea; text-decoration: underline; text-decoration-thickness: 2px; text-underline-offset: 4px;">Improvement Suggestions</h4><div style="display: flex; flex-direction: column; gap: 0.5rem;">'
            if recommendations_list:
                for rec in recommendations_list[:4]:
                    suggestions_html += f'<p style="color: #1f1f1f; margin: 0.5rem 0; line-height: 1.6;">• {rec}</p>'
            else:
                suggestions_html += '<p style="color: #1f1f1f; margin: 0; line-height: 1.6;">Your resume looks great! Keep improving with targeted updates.</p>'
            suggestions_html += '</div></div>'
            st.markdown(suggestions_html, unsafe_allow_html=True)
            st.markdown("")
        
        if "Job Match Results" in report_options and st.session_state.job_match_result:
            match = st.session_state.job_match_result
            job_match_html = '<div class="result-card" style="display: flex; flex-direction: column;"><h4 style="margin: 0 0 1rem 0; color: #667eea; text-decoration: underline; text-decoration-thickness: 2px; text-underline-offset: 4px;">Job Match Results</h4>'
            job_match_html += f'<p style="color: #1f1f1f; margin: 0 0 0.5rem 0; line-height: 1.6;"><strong>Overall Match:</strong> {match["overall_match"]}%</p>'
            job_match_html += f'<p style="color: #1f1f1f; margin: 0 0 0.5rem 0; line-height: 1.6;"><strong>Match Level:</strong> {match["match_level"]}</p>'
            job_match_html += f'<p style="color: #1f1f1f; margin: 0 0 0.5rem 0; line-height: 1.6;"><strong>Matched Skills:</strong> {", ".join(match["matched_skills"][:5]) if match["matched_skills"] else "None"}</p>'
            job_match_html += f'<p style="color: #1f1f1f; margin: 0; line-height: 1.6;"><strong>Missing Skills:</strong> {", ".join(match["missing_skills"][:5]) if match["missing_skills"] else "None"}</p>'
            job_match_html += '</div>'
            st.markdown(job_match_html, unsafe_allow_html=True)
            st.markdown("")
        
        if "Career Roadmap" in report_options and st.session_state.roadmap_data:
            roadmap = st.session_state.roadmap_data
            next_roles = roadmap.get('next_roles', [])
            roles_text = ", ".join(next_roles[:3]) if next_roles else "N/A"
            roadmap_html = '<div class="result-card" style="display: flex; flex-direction: column;"><h4 style="margin: 0 0 1rem 0; color: #667eea; text-decoration: underline; text-decoration-thickness: 2px; text-underline-offset: 4px;">Career Roadmap</h4>'
            roadmap_html += f'<p style="color: #1f1f1f; margin: 0 0 0.5rem 0; line-height: 1.6;"><strong>Target Role:</strong> {roadmap.get("target_role", "N/A")}</p>'
            roadmap_html += f'<p style="color: #1f1f1f; margin: 0 0 0.5rem 0; line-height: 1.6;"><strong>Timeline:</strong> {roadmap.get("timeline", "N/A")}</p>'
            roadmap_html += f'<p style="color: #1f1f1f; margin: 0; line-height: 1.6;"><strong>Next Roles:</strong> {roles_text}</p>'
            roadmap_html += '</div>'
            st.markdown(roadmap_html, unsafe_allow_html=True)
    else:
        st.info("📤 Please analyze your resume first to see the report preview.")


def generate_pdf_report(sections):
    """Generate PDF report with selected sections in plain text style."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
    
    styles = getSampleStyleSheet()
    
    # Define custom styles matching the dashboard
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        textColor=colors.HexColor('#667eea'),
        alignment=1
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=10,
        spaceBefore=5,
        textColor=colors.HexColor('#667eea'),
        fontName='Helvetica-Bold'
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=8,
        textColor=colors.HexColor('#1f1f1f'),
        leading=16
    )
    
    story = []
    
    # Title
    story.append(Paragraph("CareerPath AI Analysis Report", title_style))
    story.append(Spacer(1, 20))
    
    ats = st.session_state.ats_result
    resume_data = st.session_state.resume_data
    
    # ATS Score Analysis
    if "ATS Score Analysis" in sections:
        story.append(Paragraph("Overall ATS Score", heading_style))
        score_text = f"Your ATS compatibility score is <b>{ats['total_score']}/100 (Grade: {ats['grade']})</b>. This score reflects how well your resume is optimized for applicant tracking systems. <b>{ats['grade_text']}</b> resume quality with room for improvement."
        story.append(Paragraph(score_text, normal_style))
        story.append(Spacer(1, 12))
        
        story.append(Paragraph("Score Breakdown", heading_style))
        breakdown_text = f"<b>Keywords:</b> {ats['breakdown']['keyword_score']}/25 | <b>Formatting:</b> {ats['breakdown']['formatting_score']}/25 | <b>Skills:</b> {ats['breakdown']['skill_score']}/25 | <b>Experience:</b> {ats['breakdown']['experience_score']}/25"
        story.append(Paragraph(breakdown_text, normal_style))
        story.append(Spacer(1, 16))
    
    # Skills Overview
    if "Skills Overview" in sections:
        story.append(Paragraph("Skills Detected", heading_style))
        skills_text = ", ".join(resume_data['skills'][:20]) if resume_data['skills'] else "No skills detected"
        skills_content = f"We detected <b>{len(resume_data['skills'])} key skills</b> in your resume: {skills_text}"
        story.append(Paragraph(skills_content, normal_style))
        story.append(Spacer(1, 16))
    
    # Improvement Suggestions
    if "Improvement Suggestions" in sections:
        story.append(Paragraph("Key Recommendations", heading_style))
        if ats['suggestions']:
            for i, suggestion in enumerate(ats['suggestions'][:5], 1):
                story.append(Paragraph(f"<b>{i}.</b> {suggestion}", normal_style))
        else:
            story.append(Paragraph("Your resume looks great! Keep improving with targeted updates.", normal_style))
        story.append(Spacer(1, 16))
    
    # Job Match Results
    if "Job Match Results" in sections and st.session_state.job_match_result:
        match = st.session_state.job_match_result
        story.append(Paragraph("Job Match Results", heading_style))
        
        match_text = f"<b>Overall Match:</b> {match['overall_match']}% | <b>Match Level:</b> {match['match_level']}"
        story.append(Paragraph(match_text, normal_style))
        story.append(Spacer(1, 8))
        
        matched_skills_text = f"<b>Matched Skills:</b> {', '.join(match['matched_skills'][:10]) if match['matched_skills'] else 'None'}"
        story.append(Paragraph(matched_skills_text, normal_style))
        story.append(Spacer(1, 8))
        
        missing_skills_text = f"<b>Missing Skills:</b> {', '.join(match['missing_skills'][:10]) if match['missing_skills'] else 'None'}"
        story.append(Paragraph(missing_skills_text, normal_style))
        story.append(Spacer(1, 16))
    
    # Career Roadmap
    if "Career Roadmap" in sections and st.session_state.roadmap_data:
        roadmap = st.session_state.roadmap_data
        story.append(Paragraph("Career Roadmap", heading_style))
        
        roadmap_text = f"<b>Target Role:</b> {roadmap.get('target_role', 'N/A')} | <b>Timeline:</b> {roadmap.get('timeline', 'N/A')}"
        story.append(Paragraph(roadmap_text, normal_style))
        story.append(Spacer(1, 8))
        
        next_roles = roadmap.get('next_roles', [])
        if next_roles:
            roles_text = f"<b>Next Roles:</b> {', '.join(next_roles[:3])}"
            story.append(Paragraph(roles_text, normal_style))
        
        story.append(Spacer(1, 16))
    
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()


# Page Router
if st.session_state.current_page == 'Resume Analyzer':
    resume_analyzer_page()
elif st.session_state.current_page == 'Job Matcher':
    job_matcher_page()
elif st.session_state.current_page == 'Skill Gap Analysis':
    skill_gap_analysis_page()
elif st.session_state.current_page == 'Career Roadmap':
    career_roadmap_page()
elif st.session_state.current_page == 'Batch Analysis':
    batch_analysis_page()
elif st.session_state.current_page == 'Portfolio Analysis':
    portfolio_analysis_page()
elif st.session_state.current_page == 'Export Report':
    export_report_page()
elif st.session_state.current_page == 'Projects':
    projects_page()
