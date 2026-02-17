# Contributor Onboarding Checklist

Welcome to AstraGuard AI! This checklist will guide you through your first contribution.

---

## 📋 Pre-Contribution Setup

### Environment Setup
- [ ] **Fork the repository** to your GitHub account
- [ ] **Clone your fork** locally:
  ```bash
  git clone https://github.com/YOUR-USERNAME/AstraGuard-AI-Apertre-3.0.git
  cd AstraGuard-AI-Apertre-3.0
  ```
- [ ] **Set up development environment**:
  - Windows: Run `.\setup-dev.ps1` (PowerShell)
  - Linux/Mac: Run `./setup-dev.sh`
- [ ] **Install dependencies**:
  ```bash
  pip install -r Requirements.txt
  npm install  # if working on frontend
  ```
- [ ] **Verify installation** by running tests:
  ```bash
  pytest tests/
  ```

### Configure Git
- [ ] **Set up your identity**:
  ```bash
  git config user.name "Your Name"
  git config user.email "your.email@example.com"
  ```
- [ ] **Add upstream remote**:
  ```bash
  git remote add upstream https://github.com/sr-857/AstraGuard-AI-Apertre-3.0.git
  ```

---

## 📚 Understanding the Project

### Documentation Review
- [ ] Read [README.md](../README.md) for project overview
- [ ] Review [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines
- [ ] Understand [Mission Phases](CONTRIBUTING.md#understanding-mission-phases) (LAUNCH, DEPLOYMENT, NOMINAL_OPS, PAYLOAD_OPS, SAFE_MODE)
- [ ] Check [Technical Documentation](TECHNICAL.md) for architecture details
- [ ] Review [Code of Conduct](CODE_OF_CONDUCT.md)

### Identify Your Role
- [ ] **Frontend Developer** (React/Streamlit) - UI/UX, dashboards, visualizations
- [ ] **Backend Developer** (Node.js/FastAPI/Python) - APIs, data aggregation, authentication
- [ ] **Security Engineer** - Anomaly detection, memory engine, fault classifiers
- [ ] **Policy Contributor** - Mission-phase policies, YAML configurations
- [ ] **Documentation Writer** - Guides, tutorials, API documentation
- [ ] **Testing/QA** - Test cases, bug reports, quality assurance

---

## 🎯 Finding Your First Issue

### Browse Issues
- [ ] Visit [Issues page](https://github.com/sr-857/AstraGuard-AI-Apertre-3.0/issues)
- [ ] Filter by labels relevant to you:
  - `good first issue` - Perfect for newcomers
  - `easy` - 2-4 hour tasks
  - `community` - Community-driven tasks
  - `role:frontend`, `role:backend`, `role:security` - Role-specific
  - `apertre3.0` - Winter of Code event tasks

### Good First Issues
- [ ] Review [Good First Issue Criteria](GOOD_FIRST_ISSUE_CRITERIA.md)
- [ ] Choose an issue that matches your skill level
- [ ] Verify the issue has:
  - Clear description and acceptance criteria
  - No existing assignee or active work
  - Recent activity (not stale)

### Claim the Issue
- [ ] **Comment on the issue**: "I'd like to work on this issue"
- [ ] Wait for maintainer approval or assignment
- [ ] Ask clarifying questions if anything is unclear

---

## 💻 Development Workflow

### Create a Feature Branch
- [ ] **Sync with upstream**:
  ```bash
  git fetch upstream
  git checkout main
  git merge upstream/main
  ```
- [ ] **Create a feature branch**:
  ```bash
  git checkout -b feature/issue-NUMBER-short-description
  ```
  Example: `git checkout -b feature/issue-698-onboarding-checklist`

### Make Changes
- [ ] **Write clean, documented code**:
  - Add docstrings to functions/classes
  - Use type hints (Python)
  - Follow existing code style
- [ ] **Consider mission-phase awareness** (if applicable):
  - Update `config/mission_phase_response_policy.yaml` for new features
  - Test across multiple mission phases
  - Document phase-specific behavior
- [ ] **Keep commits focused and atomic**:
  ```bash
  git add .
  git commit -m "feat: add contributor onboarding checklist (closes #698)"
  ```

### Testing
- [ ] **Write tests** for your changes:
  - Unit tests: `tests/test_*.py`
  - Integration tests if needed
  - Cover edge cases
- [ ] **Run all tests locally**:
  ```bash
  pytest tests/
  ```
- [ ] **Check code quality**:
  ```bash
  mypy .  # Type checking
  flake8  # Linting (if configured)
  ```
- [ ] **Test across mission phases** (if feature is phase-aware)

### Documentation
- [ ] **Update relevant documentation**:
  - Add/update docstrings
  - Update README if adding major features
  - Add examples/usage guides
  - Update API documentation
- [ ] **Create changelog entry** (if applicable):
  - Add entry to `docs/changelogs/`

---

## 🚀 Submitting Your Contribution

### Pre-Submission Checklist
- [ ] **Code is complete** and addresses all acceptance criteria
- [ ] **All tests pass** locally
- [ ] **Documentation is updated**
- [ ] **No debugging code** (console.log, print statements) left behind
- [ ] **Commits are clean** and follow conventional commit format
- [ ] **Branch is up to date** with upstream main:
  ```bash
  git fetch upstream
  git rebase upstream/main
  ```

### Create Pull Request
- [ ] **Push your branch** to your fork:
  ```bash
  git push origin feature/issue-NUMBER-short-description
  ```
- [ ] **Open Pull Request** on GitHub
- [ ] **Fill out PR template** with:
  - Clear title: "feat: add contributor onboarding checklist"
  - Description of changes
  - Link to issue: "Closes #698"
  - Screenshots (if UI changes)
  - Testing performed
  - Mission-phase impact (if applicable)
- [ ] **Request review** from relevant maintainers
- [ ] **Link PR to issue** (GitHub will auto-link with "Closes #698")

### Code Review Process
- [ ] **Respond to review comments** promptly
- [ ] **Make requested changes**:
  ```bash
  # Make changes
  git add .
  git commit -m "fix: address review feedback"
  git push origin feature/issue-NUMBER-short-description
  ```
- [ ] **Be respectful and professional** in all interactions
- [ ] **Ask for clarification** if feedback is unclear
- [ ] **Update your PR** based on feedback

### After Merge
- [ ] **Celebrate!** 🎉 Your contribution is merged!
- [ ] **Delete your feature branch**:
  ```bash
  git checkout main
  git branch -d feature/issue-NUMBER-short-description
  ```
- [ ] **Update your fork**:
  ```bash
  git fetch upstream
  git merge upstream/main
  git push origin main
  ```
- [ ] **Look for your next issue!**

---

## 🆘 Getting Help

### Resources
- [ ] **Read the documentation** in the `docs/` folder
- [ ] **Search existing issues** for similar questions
- [ ] **Check closed PRs** for examples of good contributions
- [ ] **Review the codebase** for patterns and conventions

### Ask Questions
- [ ] **Comment on the issue** you're working on
- [ ] **Ask in PR comments** for code-specific questions
- [ ] **Be specific** about what you've tried and what's blocking you
- [ ] **Share error messages** and relevant code snippets

### Contact
- [ ] **Tag maintainers** in comments: @sr-857
- [ ] **Be patient** - maintainers are volunteers
- [ ] **Check response times** - usually 24-48 hours

---

## 🌟 Recognition & Growth

### After Your First PR
- [ ] You'll be added to [CONTRIBUTORS.md](../CONTRIBUTORS.md) as a **New Contributor** 🌱
- [ ] Your name appears in the contributor graph
- [ ] You'll receive a first-contribution badge

### Continued Contributions
Track your progress through contributor tiers:
- **Active Contributor** (2-4 merged PRs) ⭐
- **Regular Contributor** (5-19 merged PRs) 💎
- **Core Contributor** (20+ merged PRs) 🌟

### Contribution Types Valued
All contributions matter:
- 💻 **Code** - Features, bug fixes, optimizations
- 📝 **Documentation** - Guides, tutorials, API docs
- 🎨 **Design** - UI/UX improvements
- 🧪 **Testing** - Test cases, QA, bug reports
- 🤝 **Community** - Helping others, issue triaging
- 🔍 **Code Review** - Reviewing other contributors' PRs

---

## ✅ Quick Reference

### Common Commands
```bash
# Sync with upstream
git fetch upstream && git merge upstream/main

# Create feature branch
git checkout -b feature/issue-NUMBER-description

# Run tests
pytest tests/

# Commit changes
git add . && git commit -m "type: description"

# Push to your fork
git push origin feature/issue-NUMBER-description

# Update from main after changes
git fetch upstream && git rebase upstream/main
```

### Commit Types
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation only
- `test:` - Adding tests
- `refactor:` - Code restructuring
- `style:` - Formatting, no code change
- `chore:` - Maintenance tasks

### Need Help?
- 📖 Read [CONTRIBUTING.md](CONTRIBUTING.md)
- 🎯 Check [Good First Issue Criteria](GOOD_FIRST_ISSUE_CRITERIA.md)
- 💬 Comment on your issue
- 👥 Tag maintainers: @sr-857

---

**Welcome to the AstraGuard AI community! We're excited to have you contribute.** 🚀

For questions about this checklist, please open an issue or comment on #698.
