# Branch Workflow

This document describes the branching strategy and workflow for this project.

## Overview

This project uses a simplified branch workflow with two main branches and feature branches:

- **`main`** - The latest stable, released code
- **`dev`** - The ongoing development branch
- **Feature branches** (e.g. `automations`) - Branched from `dev` for specific features, merged back into `dev` when ready

## Branch Structure

### Main Branch (`main`)

- **Purpose**: Contains the latest stable, released code
- **Protection**: Fully protected - no direct pushes allowed
- **Updates**: Only updated via GitHub Actions after successful test completion
- **Status**: Always represents a releasable state
- **Tags**: Release tags are created from commits on this branch

### Development Branch (`dev`)

- **Purpose**: Contains ongoing development work and feature integration
- **Protection**: Protected - requires PR for merging
- **Updates**: Updated via merged feature branches and direct commits from maintainers
- **Status**: May contain unreleased features and work-in-progress code
- **Triggers**: Triggers CI/CD pipeline on push

## Workflow

### Feature Development

1. **Create feature branch**
   ```bash
   git checkout dev
   git pull origin dev
   git checkout -b feature/your-feature-name
   ```

2. **Make changes**
   - Write code following project conventions
   - Commit with conventional commit messages
   - Test locally

3. **Push and create PR**
   ```bash
   git push origin feature/your-feature-name
   ```
   - Create pull request to `dev` branch
   - Include description of changes
   - Reference related issues

4. **Review and merge**
   - Team reviews the PR
   - GitHub Actions runs tests automatically
   - If tests pass, PR still requires manual approval
   - Once approved, merge to `dev`

### Release Process

1. **Prepare release**
   - Ensure all desired features are merged to `dev`
   - Verify all tests pass on `dev`
   - Update any necessary documentation

2. **Trigger release**
   
   **Option A - Via PR (recommended for teams):**
   ```bash
   git checkout dev
   git pull origin dev
   git checkout -b release/prepare
   git commit -m "release: prepare release"
   git push origin release/prepare
   ```
   - Create PR to `dev`
   - Wait for tests to pass
   - Get manual approval
   - Merge to `dev`
   - GitHub Actions will amend commit to include version: `release: v0.1.1`

   **Option B - Direct commit (maintainers only):**
   ```bash
   git checkout dev
   git pull origin dev
   git commit -m "release: prepare release"
   git push origin dev
   ```
   - GitHub Actions will amend commit to include version: `release: v0.1.1`

3. **Automated release**
   - GitHub Actions detects `[release]` in commit message
   - Runs full test suite on `dev`
   - If tests pass:
     - Calculates version based on commit history
     - Creates appropriate tag
     - Merges `dev` to `main`
     - Pushes tag to repository
   - If tests fail: No release is created

### Hotfix Process

For urgent fixes that need to be released quickly:

1. **Create hotfix branch from `main`**
   ```bash
   git checkout main
   git pull origin main
   git checkout -b hotfix/urgent-fix
   ```

2. **Implement fix**
   - Make minimal changes to fix the issue
   - Commit with conventional commit message
   - Test thoroughly

3. **Create PR to `dev`**
   - Push hotfix branch
   - Create PR to `dev` (not directly to `main`)
   - Include "hotfix" in PR title

4. **Merge and release**
   - Merge hotfix to `dev`
   - Trigger release with `release: prepare release` commit
   - GitHub Actions handles the rest

## Branch Protection Rules

### Main Branch

- **Require pull request before merging**: Enabled
- **Require status checks to pass before merging**: Enabled
- **Require branches to be up to date before merging**: Enabled
- **Do not allow bypassing the above settings**: Enabled
- **Restrict who can push**: Only GitHub Actions (via token)
- **Require linear history**: Enabled

### Dev Branch

- **Require pull request before merging**: Enabled
- **Require status checks to pass before merging**: Enabled
- **Require branches to be up to date before merging**: Enabled
- **Require approval from**: Configure required reviewers (at least 1)
- **Allow administrators to bypass**: Optional (based on team preference)
- **Allow force pushes**: Enabled (required for GitHub Actions to amend release commit messages)

## Branch Naming Conventions

- **Feature branches**: `feature/feature-name` or `feat/feature-name`
- **Bugfix branches**: `fix/bug-description` or `bugfix/bug-description`
- **Hotfix branches**: `hotfix/urgent-fix-description`
- **Release branches**: `release/prepare` (for release preparation)
- **Documentation branches**: `docs/documentation-update`
- **Refactoring branches**: `refactor/component-name`

## Commit Guidelines

- All commits should follow the Conventional Commits specification
- See `VERSIONING.md` for detailed commit message format
- Use descriptive commit messages that explain the "why" not just the "what"
- Avoid committing directly to `main` - it should only be updated by GitHub Actions

## Best Practices

1. **Keep branches focused**: Each branch should address a single feature or fix
2. **Regular updates**: Keep feature branches synced with `dev` to avoid conflicts
3. **Small PRs**: Break large changes into smaller, reviewable PRs
4. **Test before pushing**: Run tests locally before pushing to avoid CI failures
5. **Manual approval required**: Even when tests pass, all PRs require manual approval before merging
6. **Clean history**: Squash or rebase commits to maintain clean history (optional)
7. **Delete merged branches**: Remove feature branches after merging to keep repository clean
8. **Never push to main**: Always go through the proper release process

## Emergency Procedures

### If GitHub Actions fails

1. Check the Actions tab for failure details
2. Fix the issue in a new branch
3. Create PR to `dev`
4. Trigger release again after fix is merged

### If merge conflict occurs during release

1. GitHub Actions will fail on merge conflict
2. Manually resolve conflict in `dev` branch
3. Trigger release again with `[release]` commit

### If incorrect release is created

1. Create hotfix to address the issue
2. Follow hotfix process to release correct version
3. Consider deleting incorrect tag if necessary (use with caution)

## Tools and Integration

- **GitHub Actions**: Automated CI/CD and release management
- **Branch protection**: Enforces workflow rules
- **Pull requests**: Code review and integration process
- **Status checks**: Ensure quality before merging

## Summary

This workflow ensures:
- `main` always contains stable, released code
- All changes go through proper testing and review
- All PRs require manual approval even when tests pass
- Releases are automated and consistent
- Team collaboration is structured and clear
- Emergency fixes can be handled quickly while maintaining process integrity
