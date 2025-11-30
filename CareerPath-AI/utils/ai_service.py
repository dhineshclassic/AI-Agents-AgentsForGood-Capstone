import os
import json
from typing import Dict, List, Optional
from openai import OpenAI

# the newest OpenAI model is "gpt-5" which was released August 7, 2025.
# do not change this unless explicitly requested by the user

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")


class AIService:
    """
    AI service for generating career insights and roadmaps using OpenAI.
    """
    
    def __init__(self):
        self.client = None
        if OPENAI_API_KEY:
            self.client = OpenAI(api_key=OPENAI_API_KEY)
    
    def is_available(self) -> bool:
        """Check if AI service is available."""
        return self.client is not None
    
    def generate_career_roadmap(self, resume_data: Dict, job_description: Optional[str] = None, target_role: Optional[str] = None) -> Dict:
        """
        Generate a career roadmap based on resume and target role.
        """
        if not self.is_available():
            return self._generate_fallback_roadmap(resume_data, job_description, target_role)
        
        skills = resume_data.get('skills', [])
        sections = resume_data.get('sections', {})
        experience = sections.get('experience', 'Not provided')
        
        prompt = f"""Based on the following resume information, generate a comprehensive career roadmap.

Resume Skills: {', '.join(skills[:20]) if skills else 'Not specified'}

Experience Summary: {experience[:500] if experience else 'Not provided'}

Target Role: {target_role if target_role else 'Next career advancement'}

Job Description (if provided): {job_description[:800] if job_description else 'Not specified'}

Generate a JSON response with the following structure:
{{
    "current_level": "Your assessment of current career level",
    "target_role": "Recommended target role",
    "timeline": "Estimated time to reach target (e.g., 6-12 months)",
    "roadmap_steps": [
        {{
            "step": 1,
            "title": "Step title",
            "description": "What to do in this step",
            "duration": "Estimated duration",
            "skills_to_learn": ["skill1", "skill2"],
            "resources": ["resource1", "resource2"]
        }}
    ],
    "portfolio_ideas": ["idea1", "idea2", "idea3"],
    "learning_resources": [
        {{
            "name": "Resource name",
            "type": "Course/Book/Tutorial",
            "focus": "What it covers"
        }}
    ],
    "next_roles": ["Role 1", "Role 2", "Role 3"],
    "key_skills_to_develop": ["skill1", "skill2", "skill3"],
    "salary_insights": "Brief salary progression insight"
}}

Provide actionable, specific recommendations based on the resume content."""

        try:
            response = self.client.chat.completions.create(
                model="gpt-5",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert career counselor and technical recruiter. Provide specific, actionable career advice based on resume analysis. Always respond with valid JSON."
                    },
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                max_completion_tokens=2048
            )
            
            result = json.loads(response.choices[0].message.content)
            return result
            
        except Exception as e:
            print(f"AI roadmap generation error: {e}")
            return self._generate_fallback_roadmap(resume_data, job_description, target_role)
    
    def analyze_resume_with_ai(self, resume_text: str, skills: List[str]) -> Dict:
        """
        Get AI-powered analysis and suggestions for the resume.
        """
        if not self.is_available():
            return self._generate_fallback_analysis(skills)
        
        prompt = f"""Analyze this resume and provide improvement suggestions.

Resume Text (first 1500 chars): {resume_text[:1500]}

Extracted Skills: {', '.join(skills[:15]) if skills else 'None detected'}

Provide a JSON response with:
{{
    "overall_assessment": "Brief overall assessment",
    "strengths": ["strength1", "strength2", "strength3"],
    "weaknesses": ["weakness1", "weakness2"],
    "improvement_tips": [
        {{
            "area": "Area to improve",
            "suggestion": "Specific suggestion",
            "priority": "High/Medium/Low"
        }}
    ],
    "missing_skills": ["skill1", "skill2"],
    "industry_fit": ["Industry 1", "Industry 2"],
    "role_recommendations": ["Role 1", "Role 2", "Role 3"]
}}"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-5",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert resume reviewer and career advisor. Provide constructive, specific feedback. Always respond with valid JSON."
                    },
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                max_completion_tokens=1024
            )
            
            result = json.loads(response.choices[0].message.content)
            return result
            
        except Exception as e:
            print(f"AI analysis error: {e}")
            return self._generate_fallback_analysis(skills)
    
    def generate_interview_tips(self, job_description: str, resume_skills: List[str]) -> Dict:
        """
        Generate interview preparation tips based on job description.
        """
        if not self.is_available():
            return self._generate_fallback_interview_tips()
        
        prompt = f"""Based on this job description and candidate skills, provide interview preparation tips.

Job Description: {job_description[:1000]}

Candidate Skills: {', '.join(resume_skills[:15]) if resume_skills else 'General skills'}

Provide a JSON response with:
{{
    "key_topics": ["topic1", "topic2", "topic3"],
    "potential_questions": [
        {{
            "question": "Interview question",
            "tip": "How to approach this question"
        }}
    ],
    "skills_to_highlight": ["skill1", "skill2"],
    "company_research_tips": ["tip1", "tip2"],
    "questions_to_ask": ["question1", "question2"]
}}"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-5",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert interview coach. Provide practical interview preparation advice. Always respond with valid JSON."
                    },
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                max_completion_tokens=1024
            )
            
            result = json.loads(response.choices[0].message.content)
            return result
            
        except Exception as e:
            print(f"AI interview tips error: {e}")
            return self._generate_fallback_interview_tips()
    
    def _generate_fallback_roadmap(self, resume_data: Dict, job_description: Optional[str] = None, target_role: Optional[str] = None) -> Dict:
        """Generate a fallback roadmap when AI is unavailable."""
        skills = resume_data.get('skills', [])
        
        # Determine career direction based on skills
        if any(s.lower() in ['python', 'machine learning', 'tensorflow', 'pytorch', 'data analysis'] for s in skills):
            career_path = "Data Science / ML Engineering"
            next_roles = ["Data Scientist", "ML Engineer", "AI Engineer"]
            skills_to_learn = ["Deep Learning", "MLOps", "Cloud ML Services"]
        elif any(s.lower() in ['react', 'javascript', 'angular', 'vue', 'node.js'] for s in skills):
            career_path = "Full-Stack Development"
            next_roles = ["Senior Developer", "Tech Lead", "Engineering Manager"]
            skills_to_learn = ["System Design", "Cloud Architecture", "DevOps"]
        elif any(s.lower() in ['aws', 'azure', 'docker', 'kubernetes'] for s in skills):
            career_path = "Cloud / DevOps Engineering"
            next_roles = ["DevOps Engineer", "Cloud Architect", "SRE"]
            skills_to_learn = ["Terraform", "Security", "Cost Optimization"]
        else:
            career_path = "Software Engineering"
            next_roles = ["Software Engineer", "Senior Engineer", "Tech Lead"]
            skills_to_learn = ["System Design", "Algorithms", "Cloud Services"]
        
        return {
            "current_level": "Mid-level Professional",
            "target_role": target_role or next_roles[0],
            "timeline": "6-12 months",
            "roadmap_steps": [
                {
                    "step": 1,
                    "title": "Skill Assessment & Gap Analysis",
                    "description": "Identify key skills needed for your target role and assess current proficiency",
                    "duration": "2 weeks",
                    "skills_to_learn": ["Self-assessment", "Goal setting"],
                    "resources": ["LinkedIn Learning", "Coursera"]
                },
                {
                    "step": 2,
                    "title": "Core Skill Development",
                    "description": f"Focus on building expertise in {career_path}",
                    "duration": "2-3 months",
                    "skills_to_learn": skills_to_learn[:2],
                    "resources": ["Online courses", "Documentation", "Practice projects"]
                },
                {
                    "step": 3,
                    "title": "Portfolio Building",
                    "description": "Create projects that showcase your skills to potential employers",
                    "duration": "1-2 months",
                    "skills_to_learn": ["Project management", "Documentation"],
                    "resources": ["GitHub", "Personal website"]
                },
                {
                    "step": 4,
                    "title": "Networking & Job Search",
                    "description": "Connect with professionals in your target field and start applying",
                    "duration": "Ongoing",
                    "skills_to_learn": ["Networking", "Interview skills"],
                    "resources": ["LinkedIn", "Meetups", "Tech conferences"]
                }
            ],
            "portfolio_ideas": [
                "Build a full-stack web application",
                "Contribute to open source projects",
                "Create a technical blog"
            ],
            "learning_resources": [
                {"name": "Coursera", "type": "Course Platform", "focus": "Structured learning paths"},
                {"name": "LeetCode", "type": "Practice Platform", "focus": "Coding interviews"},
                {"name": "System Design Primer", "type": "GitHub Resource", "focus": "Architecture"}
            ],
            "next_roles": next_roles,
            "key_skills_to_develop": skills_to_learn,
            "salary_insights": "With the recommended skill development, expect 15-30% salary increase potential"
        }
    
    def _generate_fallback_analysis(self, skills: List[str]) -> Dict:
        """Generate fallback analysis when AI is unavailable."""
        return {
            "overall_assessment": "Your resume shows relevant technical experience. Consider adding more quantifiable achievements.",
            "strengths": [
                "Technical skills are clearly listed",
                "Professional format",
                "Relevant experience highlighted"
            ],
            "weaknesses": [
                "Could use more specific metrics",
                "Consider adding more soft skills"
            ],
            "improvement_tips": [
                {
                    "area": "Achievements",
                    "suggestion": "Add specific numbers and metrics to your accomplishments",
                    "priority": "High"
                },
                {
                    "area": "Keywords",
                    "suggestion": "Include more industry-specific keywords",
                    "priority": "Medium"
                }
            ],
            "missing_skills": ["Cloud certifications", "Agile methodologies"],
            "industry_fit": ["Technology", "Software Development", "IT Services"],
            "role_recommendations": ["Software Engineer", "Full Stack Developer", "Technical Lead"]
        }
    
    def _generate_fallback_interview_tips(self) -> Dict:
        """Generate fallback interview tips when AI is unavailable."""
        return {
            "key_topics": [
                "Technical fundamentals",
                "Problem-solving approach",
                "Past project experiences"
            ],
            "potential_questions": [
                {
                    "question": "Tell me about yourself",
                    "tip": "Prepare a 2-minute summary focusing on relevant experience"
                },
                {
                    "question": "Describe a challenging project",
                    "tip": "Use STAR method: Situation, Task, Action, Result"
                },
                {
                    "question": "Why are you interested in this role?",
                    "tip": "Research the company and connect your skills to their needs"
                }
            ],
            "skills_to_highlight": [
                "Problem-solving abilities",
                "Team collaboration",
                "Technical expertise"
            ],
            "company_research_tips": [
                "Review company website and recent news",
                "Check LinkedIn for employee insights",
                "Understand their products and services"
            ],
            "questions_to_ask": [
                "What does success look like in this role?",
                "How would you describe the team culture?",
                "What are the growth opportunities?"
            ]
        }
