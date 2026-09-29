# 📝 Changelog

> All notable changes to **[Project Name]** will be documented here.
> Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)
> Versioning follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html): `MAJOR.MINOR.PATCH`

---

## Versioning Guide

```
MAJOR (1.x.x) → Breaking changes (API incompatible, DB schema overhaul)
MINOR (x.1.x) → New features (backward compatible)
PATCH (x.x.1) → Bug fixes, security patches, performance

Labels:
  ✨ Added     — New features
  🔄 Changed   — Changes to existing features
  🗑️ Deprecated — Soon-to-be removed features
  🗃️ Removed   — Removed features
  🐛 Fixed     — Bug fixes
  🔒 Security  — Vulnerability fixes
  ⚡ Performance — Speed / optimization improvements
  📚 Docs      — Documentation only changes
```

---

## [Unreleased]
> Changes that are done but not yet in a release

### ✨ Added
- [ ] [Feature description]

### 🐛 Fixed
- [ ] [Bug description]

---

## [0.1.0] — YYYY-MM-DD 🎉 Initial Release

### ✨ Added
- Initial project setup with Next.js + Node.js
- User authentication (register, login, logout)
- JWT access tokens + HttpOnly refresh token cookies
- Password hashing with bcrypt (12 rounds)
- Email verification flow
- Forgot password / reset password flow
- User profile (view + update)
- `[Feature]` CRUD endpoints
- Pagination + filtering on list endpoints
- Input validation with Zod
- Rate limiting on auth routes (10 req/15min)
- Security headers via Helmet.js
- CORS configuration
- Docker + docker-compose setup
- PostgreSQL database with Prisma ORM
- Redis for session management
- GitHub Actions CI/CD pipeline
- Sentry error monitoring integration
- Winston logging
- Health check endpoint (`/health`)

### 📚 Docs
- `README.md` with setup instructions
- `00_PRD.md` — Product requirements
- `01_ARCHITECTURE.md` — System architecture
- `02_DATABASE.md` — Database schema
- `03_API.md` — API documentation
- `04_UI_UX.md` — Design guide
- `05_TESTING.md` — Testing strategy
- `06_DEPLOYMENT.md` — Deployment guide
- `07_SECURITY.md` — Security guidelines
- `CONTRIBUTING.md` — Contribution guide

---

## Changelog Entry Template

> Copy this template when making a new release:

```markdown
## [X.Y.Z] — YYYY-MM-DD

### ✨ Added
- [New feature description]
- [Another new feature]

### 🔄 Changed
- [What changed and why]

### 🐛 Fixed
- [Bug description] — fixes #[issue number]
- [Another bug fix]

### 🔒 Security
- [Security vulnerability fixed]
- [CVE-YYYY-XXXXX — Description]

### 🗑️ Deprecated
- [Feature X] will be removed in v[X+1].0.0

### 🗃️ Removed
- [Removed feature] (deprecated since v[X.Y])

### ⚡ Performance
- [Optimization description] — [X]% improvement

### 📚 Docs
- Updated [document name]
```

---

## Release Process

```bash
# 1. Update CHANGELOG.md (move Unreleased → new version)
# 2. Bump version in package.json
npm version patch   # 0.1.0 → 0.1.1 (bug fix)
npm version minor   # 0.1.1 → 0.2.0 (new feature)
npm version major   # 0.2.0 → 1.0.0 (breaking change)

# 3. Commit changelog + version bump
git add CHANGELOG.md package.json
git commit -m "chore: release v[X.Y.Z]"

# 4. Create git tag
git tag -a v[X.Y.Z] -m "Release v[X.Y.Z]"
git push origin main --tags

# 5. GitHub Release is auto-created by CI (or create manually)
```

---

## Version History

| Version | Date | Type | Summary |
|---------|------|------|---------|
| 0.1.0 | YYYY-MM-DD | 🎉 Initial | First release |
| — | — | — | — |



> 💡 **Tip:** Har PR merge ke baad `[Unreleased]` section update karo. Release ke time sirf move karna hai — already likhkha hoga!
