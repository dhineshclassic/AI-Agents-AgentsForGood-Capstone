import re
from typing import Dict, List, Tuple
from collections import Counter


class ATSScorer:
    """
    ATS (Applicant Tracking System) scorer that provides deterministic scoring
    based on keyword matching, formatting, and skill coverage.
    """
    
    # Common ATS-friendly keywords by category
    ACTION_VERBS = [
        'achieved', 'accomplished', 'administered', 'analyzed', 'built', 'collaborated',
        'contributed', 'coordinated', 'created', 'delivered', 'designed', 'developed',
        'directed', 'enhanced', 'established', 'executed', 'generated', 'implemented',
        'improved', 'increased', 'initiated', 'launched', 'led', 'managed', 'optimized',
        'organized', 'oversaw', 'planned', 'produced', 'reduced', 'resolved', 'streamlined',
        'supervised', 'trained', 'transformed'
    ]
    
    IMPORTANT_SECTIONS = [
        'experience', 'education', 'skills', 'summary', 'objective'
    ]
    
    FORMATTING_ISSUES = {
        'tables': (r'\|.*\|.*\|', -5),
        'special_chars': (r'[^\w\s\.\,\;\:\-\(\)\@\/\'\"\!\?\#\&\*\+\=]', -2),
        'excessive_caps': (r'[A-Z]{10,}', -3),
    }

    def __init__(self):
        pass

    def calculate_keyword_score(self, resume_text: str, job_description: str = None) -> Tuple[float, Dict]:
        """
        Calculate keyword matching score.
        If job description is provided, match against it.
        Otherwise, use general ATS best practices.
        """
        resume_lower = resume_text.lower()
        details = {
            'action_verbs_found': [],
            'action_verbs_missing': [],
            'keyword_density': 0,
            'matched_keywords': [],
            'missing_keywords': []
        }
        
        # Check action verbs
        for verb in self.ACTION_VERBS:
            if re.search(r'\b' + verb + r'\b', resume_lower):
                details['action_verbs_found'].append(verb)
            else:
                details['action_verbs_missing'].append(verb)
        
        action_verb_score = min(len(details['action_verbs_found']) / 10, 1) * 25
        
        # If job description provided, match keywords
        jd_match_score = 0
        if job_description:
            jd_lower = job_description.lower()
            # Extract significant words from JD (excluding common words)
            common_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'shall', 'can', 'need', 'dare', 'ought', 'used', 'this', 'that', 'these', 'those', 'we', 'you', 'they', 'it', 'i', 'he', 'she', 'who', 'what', 'which', 'when', 'where', 'why', 'how', 'all', 'each', 'every', 'both', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 'just', 'also', 'as', 'if', 'then', 'because', 'while', 'although', 'though', 'after', 'before', 'since', 'until', 'unless', 'about', 'above', 'across', 'against', 'along', 'among', 'around', 'behind', 'below', 'beneath', 'beside', 'between', 'beyond', 'during', 'except', 'inside', 'into', 'near', 'off', 'onto', 'out', 'outside', 'over', 'past', 'through', 'throughout', 'toward', 'under', 'underneath', 'up', 'upon', 'within', 'without'}
            
            jd_words = set(re.findall(r'\b[a-z]{3,}\b', jd_lower)) - common_words
            resume_words = set(re.findall(r'\b[a-z]{3,}\b', resume_lower))
            
            matched = jd_words & resume_words
            missing = jd_words - resume_words
            
            details['matched_keywords'] = list(matched)[:20]
            details['missing_keywords'] = list(missing)[:20]
            
            if jd_words:
                jd_match_score = (len(matched) / len(jd_words)) * 25
        else:
            jd_match_score = 15  # Default score without JD
        
        # Calculate keyword density
        words = resume_text.split()
        if words:
            keyword_count = sum(1 for word in words if len(word) > 5)
            details['keyword_density'] = round(keyword_count / len(words) * 100, 1)
        
        total_score = action_verb_score + jd_match_score
        return total_score, details

    def calculate_formatting_score(self, resume_text: str) -> Tuple[float, Dict]:
        """
        Calculate formatting score based on ATS-friendly formatting.
        """
        score = 25  # Start with full formatting score
        details = {
            'issues': [],
            'suggestions': [],
            'section_status': {}
        }
        
        # Check for important sections
        text_lower = resume_text.lower()
        sections_found = 0
        for section in self.IMPORTANT_SECTIONS:
            pattern = r'\b' + section + r's?\b'
            if re.search(pattern, text_lower):
                details['section_status'][section] = True
                sections_found += 1
            else:
                details['section_status'][section] = False
                details['suggestions'].append(f"Add a '{section.title()}' section")
        
        section_score = (sections_found / len(self.IMPORTANT_SECTIONS)) * 10
        
        # Check for formatting issues
        penalty = 0
        for issue_name, (pattern, penalty_value) in self.FORMATTING_ISSUES.items():
            matches = re.findall(pattern, resume_text)
            if matches:
                penalty += min(abs(penalty_value) * len(matches), 10)
                details['issues'].append(f"Found {len(matches)} {issue_name.replace('_', ' ')} instances")
        
        # Check word count
        word_count = len(resume_text.split())
        if word_count < 200:
            penalty += 5
            details['suggestions'].append("Resume appears too short. Add more details about your experience.")
        elif word_count > 1500:
            penalty += 3
            details['suggestions'].append("Resume may be too long. Consider condensing to 1-2 pages.")
        
        # Check for bullet points (good for ATS)
        bullet_patterns = [r'•', r'\*\s', r'-\s+[A-Z]', r'\d+\.']
        has_bullets = any(re.search(p, resume_text) for p in bullet_patterns)
        if not has_bullets:
            details['suggestions'].append("Use bullet points to list achievements and responsibilities")
            penalty += 2
        
        final_score = max(0, score + section_score - penalty)
        return min(final_score, 25), details

    def calculate_skill_coverage(self, skills: List[str], job_description: str = None) -> Tuple[float, Dict]:
        """
        Calculate skill coverage score.
        """
        details = {
            'total_skills': len(skills),
            'skill_categories': {},
            'recommendations': []
        }
        
        # Categorize skills
        categories = {
            'programming': ['python', 'java', 'javascript', 'c++', 'c#', 'ruby', 'go', 'rust', 'typescript'],
            'data_science': ['machine learning', 'deep learning', 'data analysis', 'tensorflow', 'pytorch', 'pandas', 'numpy'],
            'web': ['html', 'css', 'react', 'angular', 'vue', 'node.js', 'django', 'flask'],
            'cloud': ['aws', 'azure', 'gcp', 'docker', 'kubernetes'],
            'database': ['sql', 'mysql', 'postgresql', 'mongodb', 'redis'],
            'soft_skills': ['leadership', 'communication', 'teamwork', 'problem solving', 'project management']
        }
        
        skills_lower = [s.lower() for s in skills]
        
        for category, category_skills in categories.items():
            matched = [s for s in category_skills if s in skills_lower]
            details['skill_categories'][category] = {
                'found': matched,
                'count': len(matched)
            }
        
        # Calculate score based on skill diversity and count
        base_score = min(len(skills) / 10, 1) * 15
        
        # Bonus for skill diversity
        categories_with_skills = sum(1 for cat in details['skill_categories'].values() if cat['count'] > 0)
        diversity_bonus = (categories_with_skills / len(categories)) * 10
        
        # Recommendations
        if details['skill_categories']['programming']['count'] == 0:
            details['recommendations'].append("Add programming languages to your skills")
        if details['skill_categories']['soft_skills']['count'] == 0:
            details['recommendations'].append("Include soft skills like leadership and communication")
        if len(skills) < 5:
            details['recommendations'].append("Add more relevant skills to improve your profile")
        
        total_score = base_score + diversity_bonus
        return min(total_score, 25), details

    def calculate_experience_quality(self, resume_text: str) -> Tuple[float, Dict]:
        """
        Calculate experience quality score based on quantifiable achievements.
        """
        details = {
            'metrics_found': [],
            'achievements': 0,
            'suggestions': []
        }
        
        # Look for quantifiable metrics
        metric_patterns = [
            (r'\d+%', 'percentage'),
            (r'\$[\d,]+[KMB]?', 'monetary'),
            (r'\d+\s*(?:users?|customers?|clients?)', 'user_impact'),
            (r'\d+\s*(?:projects?|applications?|systems?)', 'project_count'),
            (r'(?:increased|decreased|improved|reduced|grew|saved)\s+(?:by\s+)?\d+', 'improvement'),
            (r'\d+\s*(?:team|people|employees|members)', 'team_size'),
            (r'\d+\s*(?:years?|months?)\s*(?:experience|of)', 'experience_duration')
        ]
        
        for pattern, metric_type in metric_patterns:
            matches = re.findall(pattern, resume_text, re.IGNORECASE)
            if matches:
                details['metrics_found'].extend([(m, metric_type) for m in matches[:3]])
                details['achievements'] += len(matches)
        
        # Base score on metrics found
        metrics_score = min(len(details['metrics_found']) / 5, 1) * 15
        
        # Check for result-oriented language
        result_patterns = [
            r'result(?:ed|ing)?', r'achiev(?:ed|ing)?', r'accomplish(?:ed|ing)?',
            r'deliver(?:ed|ing)?', r'complet(?:ed|ing)?', r'success(?:ful)?'
        ]
        
        result_count = sum(len(re.findall(p, resume_text, re.IGNORECASE)) for p in result_patterns)
        result_bonus = min(result_count / 5, 1) * 10
        
        # Suggestions
        if not details['metrics_found']:
            details['suggestions'].append("Add quantifiable achievements (e.g., 'Increased sales by 25%')")
        if result_count < 3:
            details['suggestions'].append("Use more result-oriented language to describe achievements")
        
        total_score = metrics_score + result_bonus
        return min(total_score, 25), details

    def calculate_ats_score(self, resume_text: str, skills: List[str], job_description: str = None) -> Dict:
        """
        Calculate comprehensive ATS score.
        Returns a dictionary with total score and breakdown.
        """
        # Calculate individual scores
        keyword_score, keyword_details = self.calculate_keyword_score(resume_text, job_description)
        formatting_score, formatting_details = self.calculate_formatting_score(resume_text)
        skill_score, skill_details = self.calculate_skill_coverage(skills, job_description)
        experience_score, experience_details = self.calculate_experience_quality(resume_text)
        
        # Calculate total score (out of 100)
        total_score = keyword_score + formatting_score + skill_score + experience_score
        total_score = min(max(round(total_score), 0), 100)
        
        # Determine grade
        if total_score >= 85:
            grade = 'A'
            grade_text = 'Excellent'
        elif total_score >= 70:
            grade = 'B'
            grade_text = 'Good'
        elif total_score >= 55:
            grade = 'C'
            grade_text = 'Average'
        elif total_score >= 40:
            grade = 'D'
            grade_text = 'Needs Improvement'
        else:
            grade = 'F'
            grade_text = 'Poor'
        
        # Compile all suggestions
        all_suggestions = []
        all_suggestions.extend(formatting_details.get('suggestions', []))
        all_suggestions.extend(skill_details.get('recommendations', []))
        all_suggestions.extend(experience_details.get('suggestions', []))
        
        return {
            'total_score': total_score,
            'grade': grade,
            'grade_text': grade_text,
            'breakdown': {
                'keyword_score': round(keyword_score, 1),
                'formatting_score': round(formatting_score, 1),
                'skill_score': round(skill_score, 1),
                'experience_score': round(experience_score, 1)
            },
            'details': {
                'keywords': keyword_details,
                'formatting': formatting_details,
                'skills': skill_details,
                'experience': experience_details
            },
            'suggestions': all_suggestions[:10],
            'missing_keywords': keyword_details.get('missing_keywords', [])[:15]
        }

    def calculate_job_match(self, resume_text: str, resume_skills: List[str], job_description: str) -> Dict:
        """
        Calculate how well the resume matches a specific job description.
        """
        jd_lower = job_description.lower()
        resume_lower = resume_text.lower()
        
        # Extract key requirements from JD
        common_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'will', 'would', 'should', 'must', 'can', 'this', 'that', 'we', 'you', 'they', 'it', 'your', 'our', 'their', 'who', 'what', 'which', 'when', 'where', 'as', 'if', 'about', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'between', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'all', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'not', 'only', 'same', 'than', 'too', 'very', 'just', 'also', 'work', 'working', 'job', 'position', 'role', 'looking', 'seeking', 'required', 'requirements', 'qualifications', 'responsibilities', 'experience', 'years', 'ability', 'skills', 'strong', 'excellent', 'preferred', 'including', 'etc', 'plus', 'bonus'}
        
        # Get JD keywords
        jd_words = [w for w in re.findall(r'\b[a-z]{3,}\b', jd_lower) if w not in common_words]
        jd_word_freq = Counter(jd_words)
        important_keywords = [word for word, count in jd_word_freq.most_common(30)]
        
        # Match keywords
        matched_keywords = []
        missing_keywords = []
        
        for keyword in important_keywords:
            if keyword in resume_lower:
                matched_keywords.append(keyword)
            else:
                missing_keywords.append(keyword)
        
        # Calculate skill match
        resume_skills_lower = [s.lower() for s in resume_skills]
        jd_skills = []
        
        skill_indicators = ['python', 'java', 'javascript', 'react', 'angular', 'node', 'sql', 'aws', 'azure', 'docker', 'kubernetes', 'machine learning', 'data', 'analysis', 'excel', 'communication', 'leadership', 'agile', 'scrum', 'git', 'api', 'rest', 'cloud', 'linux', 'tensorflow', 'pytorch']
        
        for skill in skill_indicators:
            if skill in jd_lower:
                jd_skills.append(skill)
        
        matched_skills = [s for s in jd_skills if any(s in rs for rs in resume_skills_lower)]
        missing_skills = [s for s in jd_skills if not any(s in rs for rs in resume_skills_lower)]
        
        # Calculate match percentage
        keyword_match = len(matched_keywords) / max(len(important_keywords), 1) * 100
        skill_match = len(matched_skills) / max(len(jd_skills), 1) * 100 if jd_skills else 50
        
        overall_match = (keyword_match * 0.6 + skill_match * 0.4)
        
        # Determine match level
        if overall_match >= 75:
            match_level = 'Strong Match'
            recommendation = 'Your resume is well-aligned with this position. Consider applying!'
        elif overall_match >= 50:
            match_level = 'Moderate Match'
            recommendation = 'You have relevant experience. Tailor your resume to highlight matching skills.'
        elif overall_match >= 30:
            match_level = 'Partial Match'
            recommendation = 'Some skills align. Focus on transferable skills and consider upskilling.'
        else:
            match_level = 'Low Match'
            recommendation = 'This role may require significant skill development. Consider related positions.'
        
        return {
            'overall_match': round(overall_match, 1),
            'match_level': match_level,
            'keyword_match': round(keyword_match, 1),
            'skill_match': round(skill_match, 1),
            'matched_keywords': matched_keywords[:15],
            'missing_keywords': missing_keywords[:15],
            'matched_skills': matched_skills,
            'missing_skills': missing_skills[:10],
            'recommendation': recommendation
        }
