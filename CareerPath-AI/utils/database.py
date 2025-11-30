import os
from datetime import datetime
from contextlib import contextmanager
from sqlalchemy import create_engine, Column, Integer, String, Text, Float, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool

DATABASE_URL = os.environ.get("DATABASE_URL")

Base = declarative_base()


class ResumeAnalysis(Base):
    """Model for storing resume analysis results."""
    __tablename__ = 'resume_analyses'
    
    id = Column(Integer, primary_key=True)
    session_id = Column(String(100), index=True)
    filename = Column(String(255))
    ats_score = Column(Integer)
    grade = Column(String(2))
    skills = Column(JSON)
    score_breakdown = Column(JSON)
    suggestions = Column(JSON)
    missing_keywords = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)


class JobMatch(Base):
    """Model for storing job match results."""
    __tablename__ = 'job_matches'
    
    id = Column(Integer, primary_key=True)
    session_id = Column(String(100), index=True)
    job_title = Column(String(255))
    job_description = Column(Text)
    overall_match = Column(Float)
    match_level = Column(String(50))
    matched_skills = Column(JSON)
    missing_skills = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)


class CareerRoadmap(Base):
    """Model for storing career roadmap results."""
    __tablename__ = 'career_roadmaps'
    
    id = Column(Integer, primary_key=True)
    session_id = Column(String(100), index=True)
    target_role = Column(String(255))
    current_level = Column(String(100))
    timeline = Column(String(100))
    roadmap_steps = Column(JSON)
    next_roles = Column(JSON)
    key_skills = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)


class DatabaseManager:
    """Manager class for database operations."""
    
    def __init__(self):
        self.engine = None
        self.Session = None
        if DATABASE_URL:
            try:
                self.engine = create_engine(
                    DATABASE_URL,
                    poolclass=QueuePool,
                    pool_size=5,
                    max_overflow=10,
                    pool_timeout=30,
                    pool_recycle=1800,
                    pool_pre_ping=True
                )
                Base.metadata.create_all(self.engine)
                self.Session = sessionmaker(bind=self.engine)
            except Exception as e:
                print(f"Database connection error: {e}")
    
    @contextmanager
    def get_session(self):
        """Context manager for database sessions."""
        if not self.is_available():
            yield None
            return
        
        session = self.Session()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def is_available(self) -> bool:
        """Check if database is available."""
        return self.engine is not None and self.Session is not None
    
    def save_resume_analysis(self, session_id: str, filename: str, ats_result: dict, skills: list) -> bool:
        """Save resume analysis to database."""
        if not self.is_available():
            return False
        
        try:
            with self.get_session() as session:
                if session is None:
                    return False
                analysis = ResumeAnalysis(
                    session_id=session_id,
                    filename=filename,
                    ats_score=ats_result.get('total_score', 0),
                    grade=ats_result.get('grade', 'N/A'),
                    skills=skills,
                    score_breakdown=ats_result.get('breakdown', {}),
                    suggestions=ats_result.get('suggestions', []),
                    missing_keywords=ats_result.get('missing_keywords', [])
                )
                session.add(analysis)
            return True
        except Exception as e:
            print(f"Error saving resume analysis: {e}")
            return False
    
    def save_job_match(self, session_id: str, job_title: str, job_description: str, match_result: dict) -> bool:
        """Save job match result to database."""
        if not self.is_available():
            return False
        
        try:
            with self.get_session() as session:
                if session is None:
                    return False
                match = JobMatch(
                    session_id=session_id,
                    job_title=job_title,
                    job_description=job_description[:5000],
                    overall_match=match_result.get('overall_match', 0),
                    match_level=match_result.get('match_level', 'Unknown'),
                    matched_skills=match_result.get('matched_skills', []),
                    missing_skills=match_result.get('missing_skills', [])
                )
                session.add(match)
            return True
        except Exception as e:
            print(f"Error saving job match: {e}")
            return False
    
    def save_career_roadmap(self, session_id: str, roadmap_data: dict) -> bool:
        """Save career roadmap to database."""
        if not self.is_available():
            return False
        
        try:
            with self.get_session() as session:
                if session is None:
                    return False
                roadmap = CareerRoadmap(
                    session_id=session_id,
                    target_role=roadmap_data.get('target_role', 'Not specified'),
                    current_level=roadmap_data.get('current_level', 'Not specified'),
                    timeline=roadmap_data.get('timeline', 'Not specified'),
                    roadmap_steps=roadmap_data.get('roadmap_steps', []),
                    next_roles=roadmap_data.get('next_roles', []),
                    key_skills=roadmap_data.get('key_skills_to_develop', [])
                )
                session.add(roadmap)
            return True
        except Exception as e:
            print(f"Error saving career roadmap: {e}")
            return False
    
    def get_session_history(self, session_id: str) -> dict:
        """Get analysis history for a session."""
        if not self.is_available():
            return {'analyses': [], 'matches': [], 'roadmaps': []}
        
        try:
            with self.get_session() as session:
                if session is None:
                    return {'analyses': [], 'matches': [], 'roadmaps': []}
                
                analyses = session.query(ResumeAnalysis).filter_by(session_id=session_id).order_by(ResumeAnalysis.created_at.desc()).limit(10).all()
                matches = session.query(JobMatch).filter_by(session_id=session_id).order_by(JobMatch.created_at.desc()).limit(10).all()
                roadmaps = session.query(CareerRoadmap).filter_by(session_id=session_id).order_by(CareerRoadmap.created_at.desc()).limit(10).all()
                
                result = {
                    'analyses': [
                        {
                            'filename': a.filename,
                            'ats_score': a.ats_score,
                            'grade': a.grade,
                            'created_at': a.created_at.isoformat() if a.created_at else None
                        }
                        for a in analyses
                    ],
                    'matches': [
                        {
                            'job_title': m.job_title,
                            'overall_match': m.overall_match,
                            'match_level': m.match_level,
                            'created_at': m.created_at.isoformat() if m.created_at else None
                        }
                        for m in matches
                    ],
                    'roadmaps': [
                        {
                            'target_role': r.target_role,
                            'timeline': r.timeline,
                            'created_at': r.created_at.isoformat() if r.created_at else None
                        }
                        for r in roadmaps
                    ]
                }
                
            return result
        except Exception as e:
            print(f"Error getting session history: {e}")
            return {'analyses': [], 'matches': [], 'roadmaps': []}
