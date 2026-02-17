# Mentorship Program Examples

This directory contains example profiles and matching results for the AstraGuard AI Mentorship Program.

## 📂 Files

- **`sample_mentors.json`** - Example mentor profiles
- **`sample_mentees.json`** - Example mentee profiles
- **`sample_matches.json`** - Example output from the matcher (generated)

## 🧪 Testing the Matcher

Run the mentorship matching algorithm with these sample profiles:

```bash
cd scripts/maintenance
python mentorship_matcher.py \
  --mentors ../../.github/mentorship_examples/sample_mentors.json \
  --mentees ../../.github/mentorship_examples/sample_mentees.json \
  --output ../../.github/mentorship_examples/sample_matches.json \
  --summary
```

## 📊 Expected Output

The matcher will create matches based on:
- **Skill alignment** (40% weight) - matching mentor skills with mentee interests
- **Timezone compatibility** (25% weight) - compatible working hours
- **Experience matching** (20% weight) - appropriate mentor level for mentee
- **Communication preferences** (15% weight) - preferred platforms

### Example Match:

```json
{
  "mentor": {
    "username": "experienced-backend-dev",
    "skills": ["Backend", "Python", "FastAPI", "API Development"],
    "tier": "Core"
  },
  "mentee": {
    "username": "new-python-learner",
    "interests": ["Backend", "Python", "API Development"],
    "experience_level": "Beginner"
  },
  "match_score": 0.89,
  "score_breakdown": {
    "skills": 0.75,
    "timezone": 0.92,
    "experience": 1.0,
    "communication": 1.0
  },
  "common_interests": ["Backend", "Python", "API Development"],
  "timezone_compatible": true
}
```

## 🎯 Understanding Match Scores

- **0.8 - 1.0**: Excellent match - strong alignment in all areas
- **0.6 - 0.79**: Good match - solid alignment, minor compromises
- **0.4 - 0.59**: Acceptable match - some alignment, workable
- **< 0.4**: Poor match - not recommended

## 🔧 Customizing Profiles

### Mentor Profile Format:

```json
{
  "username": "github-username",
  "tier": "Regular|Core|Legend",
  "skills": ["Skill1", "Skill2", ...],
  "timezone": "UTC±X or UTC±X:XX",
  "availability": "X hours/week",
  "communication_prefs": ["GitHub", "Discord", "Email"],
  "max_mentees": 1-3,
  "bio": "Brief description"
}
```

### Mentee Profile Format:

```json
{
  "username": "github-username",
  "experience_level": "Beginner|Intermediate|Advanced",
  "interests": ["Interest1", "Interest2", ...],
  "timezone": "UTC±X or UTC±X:XX",
  "availability": "X hours/week",
  "communication_prefs": ["GitHub", "Discord", "Email"],
  "goals": "What you want to learn",
  "prior_open_source": true|false
}
```

## 📚 Available Skill/Interest Areas

- **Backend**: Node.js, FastAPI, Python, API Development, Database Design
- **Frontend**: React, Streamlit, JavaScript, UI/UX, CSS
- **Security**: Anomaly Detection, AI Security, Threat Detection
- **Testing**: QA, Unit Testing, Integration Testing, Test Automation
- **Documentation**: Technical Writing, Markdown, API Docs
- **DevOps**: CI/CD, Infrastructure, Deployment, Docker

## 💡 Tips for Real Usage

1. **Create actual profiles** from mentorship application issues
2. **Export to JSON** using scripts or manually
3. **Run matcher** monthly or as needed
4. **Review matches** - matcher suggests, maintainers decide
5. **Notify participants** via GitHub issues or email
6. **Track outcomes** for program improvement

---

For more information, see [MENTORSHIP_PROGRAM.md](../../docs/MENTORSHIP_PROGRAM.md)
