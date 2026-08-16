# Versioning Guide

This document outlines the versioning strategy and commit message conventions for this project. Following these guidelines ensures consistent versioning and automated changelog generation.

## Overview

* This project uses [Conventional Commits](https://www.conventionalcommits.org/) to drive automatic versioning and changelog generation.
* Semantic versioning (MAJOR.MINOR.PATCH) is used for functional changes.
* A REVISION number is added and incremented for commits that don't change the semantic version.
* Commit all changes unless specifically instructed otherwise.
* Use multiple commits when working across multiple unrelated files.
* Review commit messages before running git commands.
* Do not commit before being asked to do so.

## Commit Message Format

```
<type>(<scope>): <description>

<optional body>
```

* The **type** is mandatory and determines the version bump.
* The **scope** is optional but encouraged for clarity (e.g., `api`, `ui`, `database`, `config`).
  * Avoid overly broad scopes (e.g., avoid using just `backend` for a large system).
* The **description** should be lowercase, imperative mood, and concise.
* The **body** is optional but encouraged for providing additional context.
  * Bullet points are preferred for multi-line body text.

### Footers

Avoid adding non-functional footers such as tool-generated attribution text to commit messages. These add noise to the changelog and are not part of the conventional commit format.

Functional footers are allowed when they carry meaning for the project:
* `BREAKING CHANGE:` to signal a breaking change
* `Closes #123` or `Fixes #456` to reference issue trackers
* `Signed-off-by:` if the project requires DCO sign-off

## Commit Types and Version Impact

| Type | Version Bump Priority | Changelog Group |
|------|----------------------|-----------------|
| `feat` | **MINOR** | Features |
| `fix` | **PATCH** | Bug Fixes |
| `docs` | **REVISION** | Documentation |
| `refactor` | **REVISION** | Code Refactoring |
| `test` | **REVISION** | Tests |
| `chore` | **REVISION** | Maintenance |
| `style` | **REVISION** | Style Changes (no logic change) |
| `perf` | **MINOR** | Performance Improvements |
| `ci` | **REVISION** | CI/CD |
| `build` | **REVISION** | Build System |
| `revert` | varies (based on reverted commit type) | Reverts |
| `release` | **Trigger** | Release |
| any + `BREAKING CHANGE` footer or `!` | **MAJOR** | Breaking Changes |

**Priority order**: MAJOR > MINOR > PATCH > REVISION

The version bumps once per release based on the highest priority commit type since the last release.

The version is calculated based on the highest priority commit type since the last release. Individual commits don't increment the version - only the `release:` commit trigger causes version calculation and tag creation.

## Breaking Changes

To signal a breaking change, use one of these methods:

1. Add `BREAKING CHANGE:` in the commit body footer:
   ```
   feat(api)!: redesign endpoint structure
   
   BREAKING CHANGE: The v1 endpoints are no longer available. Migrate to v2.
   ```

2. Add `!` after the type/scope:
   ```
   feat(api)!: remove deprecated user endpoints
   ```

Breaking changes always trigger a MAJOR version bump and reset the revision to 0.

## Examples

**Commit examples** (these don't individually bump version, but contribute to the next release calculation):
```
feat(auth): add OAuth2 authentication support
fix(database): resolve connection timeout issue
docs(readme): update installation instructions
refactor(user): extract user validation logic to separate module
test(api): add integration tests for payment endpoints
chore(deps): update dependencies to latest versions
style: format code according to project linting rules
perf(cache): implement response caching for API endpoints
ci(github): add automated testing workflow
build(webpack): optimize production bundle size
revert: feat(api)!: remove experimental API changes
release: prepare release

feat(api)!: redesign endpoint structure

BREAKING CHANGE: The v1 endpoints are no longer available. All clients must migrate to v2 endpoints by the next release.
```

**Release workflow example**:
1. Multiple commits are made: `fix(auth)`, `fix(database)`, `docs(readme)`
2. Release commit: `release: prepare release`
3. GitHub Actions calculates highest bump type (PATCH from the `fix` commits)
4. GitHub Actions amends the commit message to: `release: v0.1.1`
5. Version bumps from `0.1.0` to `0.1.1` and tag `v0.1.1` is created

## Versioning Scheme

This project follows [Semantic Versioning](https://semver.org/) with an optional REVISION component: `MAJOR.MINOR.PATCH[.REVISION]`

* **MAJOR**: Incompatible API changes (breaking changes)
* **MINOR**: New functionality in a backwards-compatible manner (features, performance improvements)
* **PATCH**: Backwards-compatible bug fixes
* **REVISION**: Added only when the highest priority since last release is non-functional (docs, refactor, test, chore, style, ci, build)

Version format:
- `X.Y.Z` when highest priority is MAJOR, MINOR, or PATCH
- `X.Y.Z.N` when highest priority is REVISION only

**Initial version**: Projects start at `0.1.0` to indicate initial development phase. Version `1.0.0` is reserved for the first stable release.

**Version bump examples** (per release, based on highest change type):
- `0.1.0` → `0.1.0.1` (only `docs`, `refactor`, `test`, `chore`, `style`, `ci`, or `build` commits)
- `0.1.0` → `0.1.1` (at least one `fix` commit, no higher-priority changes)
- `0.1.0` → `0.2.0` (at least one `feat` or `perf` commit, no breaking changes)
- `0.1.0` → `1.0.0` (at least one breaking change)

**Multiple commits example**:
- Commits since last release: `fix(auth)`, `fix(api)`, `docs(readme)` → `0.1.0` → `0.1.1` (PATCH bump)
- Commits since last release: `fix(auth)`, `feat(ui)`, `chore(deps)` → `0.1.0` → `0.2.0` (MINOR bump)
- Commits since last release: `docs(api)`, `refactor(user)`, `test(auth)` → `0.1.0` → `0.1.0.1` (REVISION bump)

## Version Calculation

Version is calculated when a release is triggered (commit type is `release:`):

1. Read all git tags matching the version pattern (e.g., `vX.Y.Z` or `vX.Y.Z.N`)
2. Use the latest tag as the base version
3. Analyze all commits since the last release to determine the "highest" version bump type
4. Bump the version by that highest bump type only once:
   - If any commit has a breaking change: increment MAJOR, reset MINOR, PATCH, and REVISION to 0
   - Else if any commit is `feat` or `perf`: increment MINOR, reset PATCH and REVISION to 0
   - Else if any commit is `fix`: increment PATCH, reset REVISION to 0
   - Else (only `docs`, `refactor`, `test`, `chore`, `style`, `ci`, `build`): increment REVISION only
5. Output the resolved version
6. Amend the release commit message to include the calculated version (e.g., `release: v0.1.1`)

**Key concept**: The version bumps only once per release based on the most significant change, not per commit. For example:
- 4 `fix` commits since last release → PATCH bump (0.1.0 → 0.1.1)
- 2 `fix` + 1 `feat` commits → MINOR bump (0.1.0 → 0.2.0)
- 1 `fix` + 1 breaking change → MAJOR bump (0.1.0 → 1.0.0)
- 5 `docs` commits → REVISION bump (0.1.0 → 0.1.0.1)

If no tags exist, versioning starts at `v0.1.0`.

## Tagging

Tags are automatically created by GitHub Actions when a commit type is `release:`. The tag format depends on the highest priority commit type since the last release:

* If highest priority is MAJOR, MINOR, or PATCH: tag as `vX.Y.Z` (e.g., `v0.1.1`)
* If highest priority is REVISION only: tag as `vX.Y.Z.N` (e.g., `v0.1.0.1`)

Example commit that triggers tag creation:
```
release: prepare release
```

After GitHub Actions processes it, the commit message is automatically amended to:
```
release: v0.1.1
```

The GitHub Actions workflow:
1. Detects `release:` commit type
2. Analyzes commits since last release to determine highest priority bump type
3. Calculates the new version based on that highest priority
4. Amends the release commit message to include the calculated version
5. Creates the appropriate tag format based on whether it's a REVISION-only bump
6. Pushes the amended commit and tag to the repository

Tags serve as fixed reference points. All commits after a tag will be analyzed for the next release.

## Scopes

Scopes are project-specific and should reflect the areas of the codebase being modified. Common scopes include:

* `api` - API endpoints and interfaces
* `ui` - User interface components
* `database` - Database schema and queries
* `auth` - Authentication and authorization
* `config` - Configuration files
* `docs` - Documentation
* `tests` - Test files
* `build` - Build configuration and scripts
* `ci` - CI/CD pipelines

Use scopes that best describe the area of change for your project. Scopes are not enforced but provide valuable context in the changelog.

## Changelog Generation

The changelog is automatically generated from the commit history following the Conventional Commits specification. Commits are grouped by type and scope, with breaking changes highlighted prominently.

## Best Practices

* Write clear, descriptive commit messages that explain the "why" not just the "what"
* Keep commits atomic and focused on a single change
* Avoid mixing unrelated changes in a single commit
* Use the body to provide context for complex changes
* Reference related issues in commit footers when applicable
* Tag releases consistently and communicate breaking changes clearly

## Tools and Automation

Consider using tools to enforce these conventions:

* **Commitlint**: Validates commit messages against the conventional commit format
* **Husky**: Git hooks for running commitlint before commits
* **GitHub Actions**: Automates version calculation, commit message amendment, and tag creation when `release:` commits are detected
* **Standard Version**: Can be customized to handle the 4-component versioning scheme
* **Semantic Release**: Can be configured with custom plugins to support the revision component
* **Custom version script**: For full control over the revision logic, implement a custom version calculation script

Configure these tools according to your project's build system and requirements. The revision logic and `release:` commit processing should be integrated into your GitHub Actions workflow.
