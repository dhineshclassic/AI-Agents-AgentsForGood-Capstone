# CareerPath AI - Kaggle Capstone Project

## Overview
CareerPath AI is a comprehensive career assistant web application that helps users analyze resumes, match jobs, generate ATS insights, and plan career paths using AI.

## Tech Stack
- **Frontend**: Streamlit with modern dashboard UI
- **Backend**: Python with Streamlit
- **AI Model**: OpenAI GPT-5 (with fallback recommendations when unavailable)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Document Parsing**: PyPDF2, pdfplumber, python-docx
- **Visualizations**: Plotly for interactive charts
- **Reports**: ReportLab for PDF generation

## Project Structure
```
├── app.py                  # Main Streamlit application
├── utils/
│   ├── __init__.py
│   ├── resume_parser.py    # PDF/DOCX text extraction
│   ├── ats_scorer.py       # ATS scoring algorithm
│   ├── ai_service.py       # OpenAI integration for career insights
│   └── database.py         # PostgreSQL database models and operations
├── .streamlit/
│   └── config.toml         # Streamlit configuration
└── replit.md               # Project documentation
```

## Core Features

### 1. Resume Analyzer
- Upload PDF or DOCX resumes
- Extract text reliably using multiple parsing methods
- Calculate deterministic ATS score based on:
  - Keyword matching (action verbs, industry terms)
  - Formatting evaluation (sections, bullet points)
  - Skill coverage and diversity
  - Quantifiable achievements detection
- Provide structured feedback and improvement suggestions

### 2. Job Matcher
- Paste job descriptions for comparison
- Match resume skills against job requirements
- Calculate keyword and skill match percentages
- Provide recommendations based on match level

### 3. Skill Gap Analysis (NEW)
- Interactive radar charts showing score breakdown
- Skills distribution by category (bar charts)
- ATS score gauge with color-coded ranges
- Job match skill comparison (pie charts)
- Prioritized improvement recommendations

### 4. Career Path Planner
- AI-powered career roadmap generation
- Step-by-step learning plans with timelines
- Portfolio project ideas
- Learning resource recommendations
- Next role suggestions

### 5. Batch Resume Analysis (NEW)
- Upload and analyze up to 10 resumes simultaneously
- Comparison bar charts for ATS scores
- Individual detailed results with expandable sections
- Error handling for failed extractions

### 6. Portfolio Analysis (NEW)
- GitHub profile analysis via API
- Repository statistics and language distribution
- Programming languages pie chart
- Portfolio improvement recommendations

### 7. Export Report (NEW)
- Generate PDF reports with selected sections
- Include ATS analysis, skills overview, suggestions
- Download formatted professional reports

### 8. Projects Section
- Dynamic display (only shows if resume contains projects)
- Project cards with names and descriptions
- Enhancement tips for portfolio improvement

## Database Schema
- **resume_analyses**: Stores ATS scores, skills, suggestions, breakdowns
- **job_matches**: Stores job match results, matched/missing skills
- **career_roadmaps**: Stores generated roadmaps, steps, target roles

## Running the Application
```bash
streamlit run app.py --server.port 5000
```

## Environment Variables Required
- `DATABASE_URL`: PostgreSQL connection string (auto-configured)
- `OPENAI_API_KEY`: OpenAI API key for AI features (optional - fallback available)

## Recent Changes
- Added Skill Gap Analysis with Plotly interactive visualizations
- Added Batch Resume Analysis for multiple file processing
- Added Portfolio Analysis with GitHub API integration
- Added PDF Export functionality with ReportLab
- Fixed database connection handling with connection pooling
- Enhanced session management and error handling

## User Preferences
- Modern dashboard UI with gradient colors
- Smooth animations and transitions
- Card-based layout with rounded panels
- Left sidebar navigation
- Professional Kaggle-project aesthetics
