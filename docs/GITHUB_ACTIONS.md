# GitHub Actions Workflow

This document describes the automated CI/CD pipeline using GitHub Actions for this project.

## Overview

The GitHub Actions workflow automatically handles testing, versioning, and releases based on commit messages and branch structure.

## Workflow Triggers

The workflow is triggered on:
- Push to `dev` branch
- Pull requests to `dev` branch
- Weekly schedule (Mondays at 06:00 UTC) — validation only
- Manual dispatch

## Workflow Steps

### 1. Validation

Runs on every trigger (including the weekly schedule):

1. **Hassfest**: Home Assistant integration validation
2. **HACS**: HACS marketplace validation

### 2. Test Execution

Runs after validation passes (skipped on the weekly schedule):

1. **Checkout code**: Retrieve the latest code from the repository
2. **Setup Python**: Configure the Python runtime
3. **Run tests**: Execute the test suite
   - Logic tests (`tests/test_logic.py`)
   - Calendar tests (`tests/test_calendar.py`)
   - Protocol drift tests (`tests/test_protocol_drift.py`)
   - Todo entity tests (`tests/test_todo.py`)

### 2. Release Process

The release process is triggered when a commit on the `dev` branch has the type `release:`.

#### Version Calculation

1. **Analyze commits**: Examine all commits since the last release
2. **Determine bump type**: Identify the highest priority commit type:
   - MAJOR: Any commit with `BREAKING CHANGE` or `!`
   - MINOR: Any `feat` or `perf` commits
   - PATCH: Any `fix` commits
   - REVISION: Only `docs`, `refactor`, `test`, `chore`, `style`, `ci`, `build` commits
3. **Calculate new version**: Bump the version based on the highest priority type
4. **Amend commit message**: Update the release commit message to include the calculated version
5. **Create tag**: Generate the appropriate tag format:
   - `vX.Y.Z` for MAJOR/MINOR/PATCH bumps
   - `vX.Y.Z.N` for REVISION-only bumps

#### Merge to Main

On successful test completion and release trigger:

1. **Merge dev to main**: Automatically merge the `dev` branch into `main`
2. **Push tag**: Create and push the version tag to the repository
3. **Generate changelog**: Update the changelog with the new version information

## Commit Message Requirements

### Standard Commits

All commits should follow the Conventional Commits format as specified in `VERSIONING.md`:

```
<type>(<scope>): <description>

<optional body>
```

### Release Trigger

To trigger a release, use the `release:` commit type:

```
release: prepare release
```

The commit message will be automatically amended by GitHub Actions to include the calculated version:

```
release: v0.1.1
```

This ensures clean git history with visible version numbers in commit messages.

## Example Workflow

### Development Workflow

1. Developer creates feature branch from `dev`
2. Makes changes and commits with conventional commit messages
3. Pushes feature branch and creates PR to `dev`
4. GitHub Actions runs tests on the PR
5. If tests pass, PR requires manual review and approval before merging to `dev`

### Release Workflow

1. All features for the release are merged to `dev`
2. Developer creates release commit: `chore: prepare release [release]`
3. If working via PR: Create PR to `dev`, wait for tests to pass, get manual approval, then merge
4. If working directly on `dev` (maintainers only): Push commit directly to `dev`
5. GitHub Actions runs tests on `dev`
6. If tests pass:
   - Version is calculated based on commits since last release
   - Tag is created (e.g., `v0.1.1`)
   - `dev` is merged to `main`
   - Tag is pushed to repository
7. If tests fail: No release is created, developer fixes issues

## Failure Handling

- **Test failures**: Workflow stops, no release is created, developer must fix issues
- **Merge conflicts**: Workflow fails, manual intervention required to resolve conflicts
- **Invalid commit messages**: Commitlint should catch these before they reach the release stage

## Configuration Files

The workflow is defined in `.github/workflows/` directory:

- `test-and-release.yml` - Single workflow with chained jobs: validate → test → release

## Environment Variables

Required environment variables (configure in repository settings):

- `GITHUB_TOKEN` - Automatically provided by GitHub Actions
- Any other secrets needed for deployment or notifications

## Notifications

Configure notifications for:
- Workflow failures
- Successful releases
- PR status changes

## Best Practices

1. **Always test on dev**: Ensure all tests pass on `dev` before triggering releases
2. **Clear release messages**: Use descriptive commit messages for release triggers
3. **Monitor workflow runs**: Check Actions tab for workflow status
4. **Keep dev clean**: Regularly merge completed features to keep `dev` releasable
5. **Review changelog**: Verify the generated changelog after each release
