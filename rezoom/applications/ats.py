from __future__ import annotations

def _norm_list(xs):
    return [x.strip().lower() for x in (xs or []) if str(x).strip()]

def score_profile_against_job(profile, job) -> tuple[int, dict]:
    """
    Returns (score_0_100, summary_dict)
    Heuristic blend:
      - skills vs req_quals/tools (70%)
      - projects (10%)
      - github link (5%)
      - simple visa sanity (15% cap adjustment)
    """
    p_skills = set(_norm_list(profile.skills))
    p_projects = profile.projects or []
    p_has_github = bool((profile.github_url or "").strip())

    j_req = set(_norm_list(job.req_quals))
    j_tools = set(_norm_list(job.tools))

    # Skills/Tools match
    req_total = max(1, len(j_req))
    tools_total = max(1, len(j_tools))
    req_match = len(p_skills & j_req) / req_total    # 0..1
    tools_match = len(p_skills & j_tools) / tools_total

    # Projects signal: counts + overlap of tech strings inside each project
    proj_count = min(5, len(p_projects))
    proj_bonus = 0.0
    for p in p_projects[:5]:
        techs = set(_norm_list(p.get("technologies", [])))
        if techs & (j_req | j_tools):
            proj_bonus += 0.02  # +2% per relevant project, up to +10%

    base = (
        0.50 * req_match +   # 50%
        0.20 * tools_match + # 20%
        0.10 * (proj_count / 5.0) +  # up to 10%
        0.05 * (1.0 if p_has_github else 0.0)  # 5%
    )

    score = int(round(base * 100))

    # Visa sanity: if job doesn’t sponsor and profile likely needs it → cap score
    visa_cap_applied = False
    prof_visa = (profile.visa_status or "").lower()
    if not job.visa_sponsorship and ("sponsor" in prof_visa or "visa" in prof_visa):
        if score > 50:
            score = 50
            visa_cap_applied = True

    summary = {
        "req_match": round(req_match * 100),
        "tools_match": round(tools_match * 100),
        "proj_bonus_pct": int(proj_bonus * 100),
        "github": p_has_github,
        "visa_cap_applied": visa_cap_applied,
    }
    return max(0, min(100, score)), summary