# match_engine.py
from typing import List, Dict, Tuple

# Example weights for scoring
WEIGHTS = {
    'education': 0.3,
    'skills': 0.4,
    'sector': 0.2,
    'location': 0.1
}

def normalize_edu_score(user_edu: str, intern_edu: str) -> float:
    # Simple placeholder normalization (can be replaced with actual logic)
    diff = abs(len(user_edu) - len(intern_edu))
    max_rank = max(len(user_edu), len(intern_edu))
    return max(0.0, 1.0 - (diff / (max_rank if max_rank else 1)))

def skill_score(user_skills: List[str], intern_skills: List[str]) -> Tuple[float, List[str]]:
    user_set = set(s.strip().lower() for s in user_skills if s)
    intern_set = set(s.strip().lower() for s in intern_skills if s)
    if not intern_set:
        return 0.0, []
    matched = user_set.intersection(intern_set)
    score = len(matched) / len(intern_set)
    return score, sorted(list(matched))

def sector_score(user_sector: str, intern_sector: str) -> float:
    if not user_sector:
        return 0.0
    return 1.0 if user_sector.strip().lower() in intern_sector.strip().lower() else 0.0

def location_score(user_state: str, intern_state: str, user_remote_pref: bool, intern_remote_flag: str) -> float:
    intern_remote = (intern_remote_flag.strip().lower() == 'yes')
    # If either is remote, treat as full match
    if user_remote_pref or intern_remote:
        return 1.0
    if not user_state or not intern_state:
        return 0.0
    return 1.0 if user_state.strip().lower() == intern_state.strip().lower() else 0.0

def score_internship(user_profile: Dict, intern: Dict, weights: Dict = WEIGHTS) -> Dict:
    """Return a dict with score (0-100) and explanation."""
    edu_s = normalize_edu_score(user_profile.get('education', ''), intern.get('min_education', ''))
    sk_s, matched_skills = skill_score(user_profile.get('skills', []), intern.get('skills', []))
    sec_s = sector_score(user_profile.get('sector', ''), intern.get('sector', ''))
    loc_s = location_score(
        user_profile.get('state', ''),
        intern.get('state', ''),
        user_profile.get('remote', False),
        intern.get('remote', 'no')
    )

    combined = (
        weights['education'] * edu_s +
        weights['skills'] * sk_s +
        weights['sector'] * sec_s +
        weights['location'] * loc_s
    )
    percent = round(combined * 100, 1)

    reasons = []
    if matched_skills:
        reasons.append(f"Skills matched: {', '.join(matched_skills)}")
    if sec_s > 0:
        reasons.append(f"Sector matches ({intern.get('sector')})")
    if loc_s > 0:
        reasons.append(f"Location OK ({intern.get('state') or intern.get('location')})")
    reasons.append(f"Education similarity: {round(edu_s * 100)}%")

    return {
        'score': percent,
        'reasons': reasons,
        'matched_count': len(matched_skills)
    }

def recommend(user_profile: Dict, internships: List[Dict], top_n: int = 5) -> List[Dict]:
    results = []
    for intern in internships:
        # ensure skills field is a list
        intern_copy = intern.copy()
        intern_copy['skills'] = [
            s.strip() for s in str(intern.get('skills', '')).split(';') if s.strip()
        ]
        res = score_internship(user_profile, intern_copy)
        intern_copy.update(res)
        results.append(intern_copy)

    # sort by score desc, then by matched_count
    results_sorted = sorted(results, key=lambda x: (x['score'], x['matched_count']), reverse=True)
    return results_sorted[:top_n]
