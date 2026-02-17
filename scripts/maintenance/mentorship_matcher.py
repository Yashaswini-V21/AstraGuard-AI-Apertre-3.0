#!/usr/bin/env python3
"""
Mentorship Matching System for AstraGuard AI

This script automatically matches mentors with mentees based on:
- Skill and interest alignment
- Timezone compatibility
- Experience level matching
- Availability overlap
- Communication preferences

Usage:
    python mentorship_matcher.py --mentors mentors.json --mentees mentees.json --output matches.json

Requirements:
    pip install --no-deps (no external dependencies)
"""

import argparse
import json
import sys
from collections import defaultdict
from datetime import datetime
from typing import Dict, List, Tuple


def calculate_skill_overlap(mentor_skills: List[str], mentee_interests: List[str]) -> float:
    """
    Calculate overlap between mentor skills and mentee interests.
    
    Args:
        mentor_skills: List of mentor's skill areas
        mentee_interests: List of mentee's interest areas
        
    Returns:
        Score between 0.0 and 1.0 representing skill alignment
    """
    if not mentor_skills or not mentee_interests:
        return 0.0
    
    # Normalize skills to lowercase for comparison
    mentor_skills_normalized = {skill.lower() for skill in mentor_skills}
    mentee_interests_normalized = {interest.lower() for interest in mentee_interests}
    
    # Calculate Jaccard similarity
    intersection = len(mentor_skills_normalized & mentee_interests_normalized)
    union = len(mentor_skills_normalized | mentee_interests_normalized)
    
    return intersection / union if union > 0 else 0.0


def calculate_timezone_compatibility(mentor_tz: str, mentee_tz: str) -> float:
    """
    Calculate timezone compatibility score.
    
    Args:
        mentor_tz: Mentor's timezone (e.g., "UTC-5", "UTC+5:30")
        mentee_tz: Mentee's timezone
        
    Returns:
        Score between 0.0 and 1.0 (1.0 = same timezone, decreases with distance)
    """
    def parse_timezone_offset(tz_str: str) -> float:
        """Parse timezone string to hours offset from UTC."""
        try:
            tz_str = tz_str.upper().replace("UTC", "").strip()
            if not tz_str or tz_str == "":
                return 0.0
            
            # Handle formats like "+5", "-8", "+5:30"
            if ":" in tz_str:
                hours, minutes = tz_str.split(":")
                offset = float(hours) + (float(minutes) / 60)
            else:
                offset = float(tz_str)
            
            return offset
        except (ValueError, AttributeError):
            return 0.0
    
    mentor_offset = parse_timezone_offset(mentor_tz)
    mentee_offset = parse_timezone_offset(mentee_tz)
    
    # Calculate time difference (max 12 hours due to date line)
    diff = abs(mentor_offset - mentee_offset)
    if diff > 12:
        diff = 24 - diff
    
    # Convert to compatibility score (0 hours diff = 1.0, 12 hours = 0.0)
    return max(0.0, 1.0 - (diff / 12.0))


def calculate_experience_match(mentor_exp: str, mentee_level: str) -> float:
    """
    Calculate how well mentor experience matches mentee level.
    
    Args:
        mentor_exp: Mentor's contribution tier (e.g., "Regular", "Core")
        mentee_level: Mentee's experience level (e.g., "Beginner", "Intermediate")
        
    Returns:
        Score between 0.0 and 1.0
    """
    # Define ideal matchings
    ideal_matches = {
        ("Beginner", "Regular"): 1.0,
        ("Beginner", "Core"): 0.9,
        ("Beginner", "Legend"): 0.8,
        ("Beginner", "Active"): 0.7,
        ("Intermediate", "Core"): 1.0,
        ("Intermediate", "Regular"): 0.9,
        ("Intermediate", "Legend"): 0.8,
        ("Intermediate", "Active"): 0.6,
        ("Advanced", "Legend"): 1.0,
        ("Advanced", "Core"): 0.9,
        ("Advanced", "Regular"): 0.7,
    }
    
    return ideal_matches.get((mentee_level, mentor_exp), 0.5)


def calculate_comm_preference_match(mentor_prefs: List[str], mentee_prefs: List[str]) -> float:
    """
    Calculate communication preference overlap.
    
    Args:
        mentor_prefs: Mentor's preferred communication channels
        mentee_prefs: Mentee's preferred communication channels
        
    Returns:
        Score between 0.0 and 1.0
    """
    if not mentor_prefs or not mentee_prefs:
        return 0.5  # Neutral if no preferences specified
    
    mentor_set = {pref.lower() for pref in mentor_prefs}
    mentee_set = {pref.lower() for pref in mentee_prefs}
    
    # Any common preference is good
    if mentor_set & mentee_set:
        return 1.0
    
    return 0.3  # Low but not zero if no overlap


def calculate_match_score(
    mentor: Dict,
    mentee: Dict,
    weights: Dict[str, float]
) -> Tuple[float, Dict[str, float]]:
    """
    Calculate overall match score between a mentor and mentee.
    
    Args:
        mentor: Mentor profile dictionary
        mentee: Mentee profile dictionary
        weights: Weights for different scoring factors
        
    Returns:
        Tuple of (overall_score, component_scores)
    """
    # Calculate component scores
    skill_score = calculate_skill_overlap(
        mentor.get("skills", []),
        mentee.get("interests", [])
    )
    
    tz_score = calculate_timezone_compatibility(
        mentor.get("timezone", "UTC"),
        mentee.get("timezone", "UTC")
    )
    
    exp_score = calculate_experience_match(
        mentor.get("tier", "Regular"),
        mentee.get("experience_level", "Beginner")
    )
    
    comm_score = calculate_comm_preference_match(
        mentor.get("communication_prefs", ["GitHub"]),
        mentee.get("communication_prefs", ["GitHub"])
    )
    
    # Weighted average
    overall_score = (
        weights["skills"] * skill_score +
        weights["timezone"] * tz_score +
        weights["experience"] * exp_score +
        weights["communication"] * comm_score
    )
    
    component_scores = {
        "skills": round(skill_score, 3),
        "timezone": round(tz_score, 3),
        "experience": round(exp_score, 3),
        "communication": round(comm_score, 3)
    }
    
    return round(overall_score, 3), component_scores


def match_mentors_to_mentees(
    mentors: List[Dict],
    mentees: List[Dict],
    max_per_mentor: int = 2,
    min_match_score: float = 0.4
) -> Dict:
    """
    Match mentors to mentees using a greedy algorithm with quality threshold.
    
    Args:
        mentors: List of mentor profiles
        mentees: List of mentee profiles
        max_per_mentor: Maximum mentees per mentor
        min_match_score: Minimum acceptable match score
        
    Returns:
        Dictionary with match results
    """
    # Scoring weights
    weights = {
        "skills": 0.40,       # Most important: skill alignment
        "timezone": 0.25,     # Important for real-time communication
        "experience": 0.20,   # Good level matching
        "communication": 0.15 # Nice to have
    }
    
    matches = []
    unmatched_mentees = []
    mentor_assignments = defaultdict(list)
    
    # Calculate all possible matches
    all_match_scores = []
    for mentee in mentees:
        for mentor in mentors:
            score, components = calculate_match_score(mentor, mentee, weights)
            
            if score >= min_match_score:
                all_match_scores.append({
                    "mentor_id": mentor["username"],
                    "mentee_id": mentee["username"],
                    "score": score,
                    "components": components
                })
    
    # Sort by score (highest first)
    all_match_scores.sort(key=lambda x: x["score"], reverse=True)
    
    # Greedy assignment
    assigned_mentees = set()
    
    for match in all_match_scores:
        mentor_id = match["mentor_id"]
        mentee_id = match["mentee_id"]
        
        # Skip if mentee already assigned
        if mentee_id in assigned_mentees:
            continue
        
        # Skip if mentor at capacity
        if len(mentor_assignments[mentor_id]) >= max_per_mentor:
            continue
        
        # Assign match
        mentor_assignments[mentor_id].append(mentee_id)
        assigned_mentees.add(mentee_id)
        
        # Find mentor and mentee details
        mentor_details = next(m for m in mentors if m["username"] == mentor_id)
        mentee_details = next(m for m in mentees if m["username"] == mentee_id)
        
        matches.append({
            "mentor": {
                "username": mentor_id,
                "skills": mentor_details.get("skills", []),
                "tier": mentor_details.get("tier", "Unknown"),
                "availability": mentor_details.get("availability", "Unknown")
            },
            "mentee": {
                "username": mentee_id,
                "interests": mentee_details.get("interests", []),
                "experience_level": mentee_details.get("experience_level", "Unknown"),
                "availability": mentee_details.get("availability", "Unknown")
            },
            "match_score": match["score"],
            "score_breakdown": match["components"],
            "common_interests": list(
                set(mentor_details.get("skills", [])) &
                set(mentee_details.get("interests", []))
            ),
            "timezone_compatible": match["components"]["timezone"] > 0.7
        })
    
    # Find unmatched mentees
    for mentee in mentees:
        if mentee["username"] not in assigned_mentees:
            unmatched_mentees.append({
                "username": mentee["username"],
                "interests": mentee.get("interests", []),
                "reason": "No suitable mentor match found (score < {})".format(min_match_score)
            })
    
    # Find mentors with capacity
    mentors_with_capacity = []
    for mentor in mentors:
        assigned_count = len(mentor_assignments.get(mentor["username"], []))
        if assigned_count < max_per_mentor:
            mentors_with_capacity.append({
                "username": mentor["username"],
                "skills": mentor.get("skills", []),
                "current_mentees": assigned_count,
                "max_mentees": max_per_mentor,
                "available_slots": max_per_mentor - assigned_count
            })
    
    return {
        "generated_at": datetime.now().isoformat(),
        "total_mentors": len(mentors),
        "total_mentees": len(mentees),
        "total_matches": len(matches),
        "unmatched_mentees": len(unmatched_mentees),
        "mentors_with_capacity": len(mentors_with_capacity),
        "matches": matches,
        "unmatched_mentees_details": unmatched_mentees,
        "mentors_with_capacity_details": mentors_with_capacity,
        "matching_params": {
            "max_mentees_per_mentor": max_per_mentor,
            "min_match_score": min_match_score,
            "weights": weights
        }
    }


def load_json_file(filepath: str) -> List[Dict]:
    """Load and parse JSON file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: File not found: {filepath}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {filepath}: {e}")
        sys.exit(1)


def save_json_file(data: Dict, filepath: str):
    """Save data to JSON file."""
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"✅ Matches saved to: {filepath}")
    except IOError as e:
        print(f"Error: Could not write to {filepath}: {e}")
        sys.exit(1)


def print_match_summary(results: Dict):
    """Print a human-readable summary of matches."""
    print("\n" + "="*60)
    print("🎓 MENTORSHIP MATCHING RESULTS")
    print("="*60)
    
    print(f"\n📊 Summary:")
    print(f"  • Total Mentors: {results['total_mentors']}")
    print(f"  • Total Mentees: {results['total_mentees']}")
    print(f"  • Successful Matches: {results['total_matches']}")
    print(f"  • Unmatched Mentees: {results['unmatched_mentees']}")
    print(f"  • Mentors with Capacity: {results['mentors_with_capacity']}")
    
    print(f"\n🤝 Matches:")
    for i, match in enumerate(results['matches'], 1):
        print(f"\n  Match #{i}")
        print(f"    Mentor: @{match['mentor']['username']} ({match['mentor']['tier']})")
        print(f"    Mentee: @{match['mentee']['username']} ({match['mentee']['experience_level']})")
        print(f"    Match Score: {match['match_score']:.2f}")
        print(f"    Common Interests: {', '.join(match['common_interests'])}")
        print(f"    TZ Compatible: {'✅' if match['timezone_compatible'] else '⚠️'}")
    
    if results['unmatched_mentees_details']:
        print(f"\n⚠️  Unmatched Mentees:")
        for mentee in results['unmatched_mentees_details']:
            print(f"    • @{mentee['username']}")
            print(f"      Interests: {', '.join(mentee['interests'])}")
    
    if results['mentors_with_capacity_details']:
        print(f"\n📢 Mentors with Available Slots:")
        for mentor in results['mentors_with_capacity_details']:
            print(f"    • @{mentor['username']} - {mentor['available_slots']} slot(s) available")
    
    print("\n" + "="*60 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description="Match mentors with mentees for the AstraGuard AI Mentorship Program"
    )
    parser.add_argument(
        "--mentors",
        required=True,
        help="Path to mentors JSON file"
    )
    parser.add_argument(
        "--mentees",
        required=True,
        help="Path to mentees JSON file"
    )
    parser.add_argument(
        "--output",
        default="mentorship_matches.json",
        help="Output file for matches (default: mentorship_matches.json)"
    )
    parser.add_argument(
        "--max-per-mentor",
        type=int,
        default=2,
        help="Maximum mentees per mentor (default: 2)"
    )
    parser.add_argument(
        "--min-score",
        type=float,
        default=0.4,
        help="Minimum match score threshold (default: 0.4)"
    )
    parser.add_argument(
        "--summary",
        action="store_true",
        help="Print human-readable summary to console"
    )
    
    args = parser.parse_args()
    
    # Load data
    print(f"📂 Loading mentor profiles from: {args.mentors}")
    mentors = load_json_file(args.mentors)
    
    print(f"📂 Loading mentee profiles from: {args.mentees}")
    mentees = load_json_file(args.mentees)
    
    # Perform matching
    print(f"\n🔄 Matching {len(mentors)} mentors with {len(mentees)} mentees...")
    results = match_mentors_to_mentees(
        mentors,
        mentees,
        max_per_mentor=args.max_per_mentor,
        min_match_score=args.min_score
    )
    
    # Save results
    save_json_file(results, args.output)
    
    # Print summary if requested
    if args.summary:
        print_match_summary(results)
    
    print(f"\n✨ Matching complete! Created {results['total_matches']} matches.")


if __name__ == "__main__":
    main()
