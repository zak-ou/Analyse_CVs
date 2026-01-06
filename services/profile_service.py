import os

def calculate_candidate_completion(user_data, cv_data):
    """
    Calculates the completion percentage of a candidate profile.
    """
    # Convert Row to dict to support .get()
    if user_data is not None and not isinstance(user_data, dict):
        user_data = dict(user_data)
        
    score = 0
    total = 100
    
    if user_data:
        if user_data.get('nom') and user_data.get('prenom'): score += 5
        if user_data.get('email'): score += 5
        if user_data.get('num_tele'): score += 5
        if user_data.get('bio'): score += 5
    
    # Photo (10%)
    if user_data.get('photo_url'): score += 10
    
    # Social (10%)
    social_count = 0
    if user_data.get('linkedin_url'): social_count += 1
    if user_data.get('github_url'): social_count += 1
    if user_data.get('portfolio_url'): social_count += 1
    score += min(10, social_count * 4) # Max 10%
    
    # CV Data (Extracted or manually filled for generator)
    if cv_data:
        coords = cv_data.get('coordonnees')
        if coords is not None and not isinstance(coords, dict):
            coords = dict(coords)
            
        if coords:
            if coords.get('ville_region'): score += 10
            if coords.get('profil'): score += 10 # This is the summary in CV
        
        if cv_data.get('education'): score += 15
        if cv_data.get('experience'): score += 15
        
        skills = cv_data.get('skills')
        if skills is not None and not isinstance(skills, dict):
            skills = dict(skills)
            
        if skills and (skills.get('languages') or skills.get('soft_skills')):
            score += 10
            
    return min(100, score)

def calculate_recruiter_completion(user_data):
    """
    Calculates completion for recruiter.
    """
    # Convert Row to dict to support .get()
    if user_data is not None and not isinstance(user_data, dict):
        user_data = dict(user_data)
        
    score = 0
    if user_data:
        if user_data.get('nom'): score += 10
        if user_data.get('prenom'): score += 10
        if user_data.get('num_tele'): score += 10
        if user_data.get('photo_url'): score += 20
        if user_data.get('entreprise_nom'): score += 20
        if user_data.get('entreprise_site'): score += 10
        if user_data.get('entreprise_description'): score += 20
    return score
