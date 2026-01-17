# Branch Protection & Release Process

## Branch Protection Setup

To ensure code quality and maintain main branch stability, branch protection should be configured on GitHub.

### GitHub Settings Configuration

**Go to**: Repository Settings → Branches → Branch protection rules

#### Create protection rule for `main` branch with:

1. **Require pull request reviews before merging**
   - Required approving reviews: 1
   - ✓ Dismiss stale pull request approvals when new commits are pushed
   - ✓ Require review from code owners

2. **Require status checks to pass before merging**
   - ✓ Require branches to be up to date before merging
   - Status checks: (none configured yet - add CI if needed)

3. **Require branches to be up to date before merging**
   - ✓ Enable

4. **Require all conversations on code to be resolved before merging**
   - ✓ Enable

5. **Allow force pushes** 
   - ✗ Do not allow

6. **Allow deletions**
   - ✗ Do not allow

### Restrict Push Access

Under "Restrict who can push to matching branches":
- Only allow the repository owner (you) to push directly to main
- All others must use Pull Requests

## Development Workflow

### For Contributors

1. Create feature branch: `git checkout -b feature/description`
2. Make changes and commit
3. Push to their fork
4. Open Pull Request with clear description
5. Address review comments
6. PR merged when approved

### For Maintainers (Foster Lipkey)

1. Can push directly to main when needed (e.g., emergency hotfixes)
2. Should still use PRs for visibility: `git checkout -b feature/description`
3. Merge via "Squash and merge" or "Create a merge commit" as appropriate

## Release Process

When ready to release a new version:

1. Update version in relevant files (if applicable)
2. Update CHANGELOG (if created)
3. Create release tag: `git tag -a v1.0.0 -m "Release version 1.0.0"`
4. Push tag: `git push origin v1.0.0`
5. Create GitHub Release with notes

## Code Review Checklist

Before approving PRs, verify:
- [ ] Code follows project style
- [ ] Changes work in web interface
- [ ] 3D preview renders correctly
- [ ] STL export is valid
- [ ] Documentation is updated if needed
- [ ] No breaking changes without discussion

## Questions?

See CONTRIBUTING.md for contributor guidelines.
