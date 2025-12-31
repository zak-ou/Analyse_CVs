class ScoringService:
    def __init__(self):
        pass

    def calculate_score(self, candidate_skills, required_skills):
        """
        Calculates a score based on the intersection of candidate skills and required skills.
        
        Args:
            candidate_skills (list): List of skills extracted from the resume.
            required_skills (list): List of required skills for the job.
            
        Returns:
            float: A score between 0 and 100.
        """
        if not candidate_skills or not required_skills:
            return 0.0

        # Normalize to lowercase for better matching
        c_skills = {s.lower() for s in candidate_skills if s}
        r_skills = {s.lower() for s in required_skills if s}

        if not r_skills:
            return 0.0

        matches = c_skills.intersection(r_skills)
        score = (len(matches) / len(r_skills)) * 100
        return round(score, 2)
