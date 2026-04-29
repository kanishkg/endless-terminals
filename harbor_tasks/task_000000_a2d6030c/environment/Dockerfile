FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    python3.11 \
    python3-pip \
    git \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install pytest pyyaml

RUN mkdir -p /home/user && chmod 0777 /home/user

WORKDIR /home/user/releaser

RUN mkdir -p /home/user/releaser/project

RUN cat > /home/user/releaser/semver.py << 'EOF'
"""
Semantic versioning utilities for the releaser tool.
"""

import re


class Version:
    """Represents a semantic version (major.minor.patch)."""

    VERSION_PATTERN = re.compile(r'^v?(\d+)\.(\d+)\.(\d+)(?:-(.+))?$')

    def __init__(self, version_string, config=None):
        """Parse a version string into components."""
        self.config = config or {}
        self.original = version_string

        match = self.VERSION_PATTERN.match(version_string)
        if not match:
            raise ValueError(f"Invalid version string: {version_string}")

        self.major = int(match.group(1))
        self.minor = int(match.group(2))
        self.patch = int(match.group(3))
        self.prerelease = match.group(4)

    def __str__(self):
        """Return the version as a string."""
        base = f"{self.major}.{self.minor}.{self.patch}"
        if self.prerelease:
            return f"{base}-{self.prerelease}"
        return base

    def __repr__(self):
        return f"Version('{self}')"

    def __eq__(self, other):
        if not isinstance(other, Version):
            return False
        return (self.major, self.minor, self.patch) == (other.major, other.minor, other.patch)

    def __lt__(self, other):
        """Compare versions for sorting."""
        if not isinstance(other, Version):
            return NotImplemented
        return (self.major, self.minor, self.patch) < (other.major, other.minor, other.patch)

    def __le__(self, other):
        return self == other or self < other

    def __gt__(self, other):
        if not isinstance(other, Version):
            return NotImplemented
        return (self.major, self.minor, self.patch) > (other.major, other.minor, other.patch)

    def __ge__(self, other):
        return self == other or self > other

    def can_bump_major(self):
        """
        Check if a major version bump is allowed by policy.

        The max_minor_before_major config option prevents accidental major bumps
        until the minor version reaches a certain threshold.
        """
        max_minor = self.config.get('max_minor_before_major', '9')
        # Compare minor version against threshold
        return str(self.minor) < str(max_minor)

    def bump_major(self):
        """Return a new Version with major incremented, minor and patch reset."""
        new_version = Version(f"{self.major + 1}.0.0", self.config)
        return new_version

    def bump_minor(self):
        """Return a new Version with minor incremented, patch reset."""
        new_version = Version(f"{self.major}.{self.minor + 1}.0", self.config)
        return new_version

    def bump_patch(self):
        """Return a new Version with patch incremented."""
        new_version = Version(f"{self.major}.{self.minor}.{self.patch + 1}", self.config)
        return new_version


def parse_version(version_string, config=None):
    """Parse a version string and return a Version object."""
    return Version(version_string, config)


def compare_versions(v1, v2):
    """
    Compare two version strings.
    Returns: -1 if v1 < v2, 0 if equal, 1 if v1 > v2
    """
    ver1 = Version(v1) if isinstance(v1, str) else v1
    ver2 = Version(v2) if isinstance(v2, str) else v2

    if ver1 < ver2:
        return -1
    elif ver1 > ver2:
        return 1
    return 0
EOF

RUN cat > /home/user/releaser/test_semver.py << 'EOF'
"""
Unit tests for semver.py - version parsing and comparison.
"""

import pytest
from semver import Version, parse_version, compare_versions


class TestVersionParsing:
    """Tests for version string parsing."""

    def test_parse_simple_version(self):
        v = Version("1.2.3")
        assert v.major == 1
        assert v.minor == 2
        assert v.patch == 3

    def test_parse_version_with_v_prefix(self):
        v = Version("v1.2.3")
        assert v.major == 1
        assert v.minor == 2
        assert v.patch == 3

    def test_parse_version_with_prerelease(self):
        v = Version("1.2.3-alpha")
        assert v.major == 1
        assert v.minor == 2
        assert v.patch == 3
        assert v.prerelease == "alpha"

    def test_parse_invalid_version_raises(self):
        with pytest.raises(ValueError):
            Version("not-a-version")

    def test_parse_incomplete_version_raises(self):
        with pytest.raises(ValueError):
            Version("1.2")


class TestVersionComparison:
    """Tests for version comparison operations."""

    def test_equal_versions(self):
        v1 = Version("1.2.3")
        v2 = Version("1.2.3")
        assert v1 == v2

    def test_less_than_major(self):
        v1 = Version("1.0.0")
        v2 = Version("2.0.0")
        assert v1 < v2

    def test_less_than_minor(self):
        v1 = Version("1.1.0")
        v2 = Version("1.2.0")
        assert v1 < v2

    def test_less_than_patch(self):
        v1 = Version("1.1.1")
        v2 = Version("1.1.2")
        assert v1 < v2

    def test_greater_than(self):
        v1 = Version("2.0.0")
        v2 = Version("1.9.9")
        assert v1 > v2

    def test_compare_versions_function(self):
        assert compare_versions("1.0.0", "2.0.0") == -1
        assert compare_versions("2.0.0", "1.0.0") == 1
        assert compare_versions("1.0.0", "1.0.0") == 0


class TestVersionBumping:
    """Tests for version bump operations."""

    def test_bump_major(self):
        v = Version("1.2.3")
        new_v = v.bump_major()
        assert str(new_v) == "2.0.0"

    def test_bump_minor(self):
        v = Version("1.2.3")
        new_v = v.bump_minor()
        assert str(new_v) == "1.3.0"

    def test_bump_patch(self):
        v = Version("1.2.3")
        new_v = v.bump_patch()
        assert str(new_v) == "1.2.4"


class TestVersionString:
    """Tests for version string representation."""

    def test_str_simple(self):
        v = Version("1.2.3")
        assert str(v) == "1.2.3"

    def test_str_with_prerelease(self):
        v = Version("1.2.3-beta.1")
        assert str(v) == "1.2.3-beta.1"

    def test_repr(self):
        v = Version("1.2.3")
        assert repr(v) == "Version('1.2.3')"
EOF

RUN cat > /home/user/releaser/parse_commits.py << 'EOF'
"""
Conventional commit parser for the releaser tool.
"""

import subprocess
import re


CONVENTIONAL_COMMIT_PATTERN = re.compile(
    r'^(?P<type>\w+)(?P<breaking>!)?\s*(?:\((?P<scope>[^)]+)\))?\s*:\s*(?P<description>.+)$'
)

BREAKING_CHANGE_FOOTER = re.compile(r'^BREAKING[ -]CHANGE:\s*', re.MULTILINE)


def get_commits_since_tag(tag, repo_path='.'):
    """Get all commit messages since the given tag."""
    try:
        result = subprocess.run(
            ['git', 'log', f'{tag}..HEAD', '--pretty=format:%B%n---COMMIT_SEPARATOR---'],
            capture_output=True,
            text=True,
            cwd=repo_path,
            check=True
        )
        commits = result.stdout.split('---COMMIT_SEPARATOR---')
        return [c.strip() for c in commits if c.strip()]
    except subprocess.CalledProcessError as e:
        print(f"Error getting commits: {e}")
        return []


def parse_commit(message):
    """
    Parse a conventional commit message.

    Returns a dict with:
    - type: commit type (feat, fix, etc.)
    - scope: optional scope
    - description: commit description
    - breaking: True if this is a breaking change
    - body: commit body if present
    """
    lines = message.strip().split('\n')
    first_line = lines[0] if lines else ''

    match = CONVENTIONAL_COMMIT_PATTERN.match(first_line)
    if not match:
        return {
            'type': 'other',
            'scope': None,
            'description': first_line,
            'breaking': False,
            'body': '\n'.join(lines[1:]).strip() if len(lines) > 1 else ''
        }

    body = '\n'.join(lines[1:]).strip() if len(lines) > 1 else ''

    # Check for breaking change in footer
    has_breaking_footer = bool(BREAKING_CHANGE_FOOTER.search(body))

    return {
        'type': match.group('type'),
        'scope': match.group('scope'),
        'description': match.group('description'),
        'breaking': bool(match.group('breaking')) or has_breaking_footer,
        'body': body
    }


def determine_bump_type(commits):
    """
    Determine the version bump type based on commits.

    Returns: 'major', 'minor', or 'patch'
    """
    has_breaking = False
    has_feature = False
    has_fix = False

    for commit_msg in commits:
        parsed = parse_commit(commit_msg)

        if parsed['breaking']:
            has_breaking = True

        if parsed['type'] == 'feat':
            has_feature = True
        elif parsed['type'] == 'fix':
            has_fix = True

    if has_breaking:
        return 'major'
    elif has_feature:
        return 'minor'
    elif has_fix:
        return 'patch'

    return 'patch'  # Default to patch for unknown commit types


def get_bump_type_since_tag(tag, repo_path='.'):
    """Get the recommended bump type based on commits since a tag."""
    commits = get_commits_since_tag(tag, repo_path)
    return determine_bump_type(commits)
EOF

RUN cat > /home/user/releaser/changelog.py << 'EOF'
"""
Changelog generation for the releaser tool.
"""

import os
from datetime import datetime
from parse_commits import get_commits_since_tag, parse_commit


def generate_changelog_entry(version, commits, repo_path='.'):
    """
    Generate a changelog entry for a new version.

    Returns a string with the formatted changelog section.
    """
    date_str = datetime.now().strftime('%Y-%m-%d')

    sections = {
        'breaking': [],
        'feat': [],
        'fix': [],
        'other': []
    }

    for commit_msg in commits:
        parsed = parse_commit(commit_msg)

        if parsed['breaking']:
            sections['breaking'].append(parsed)
        elif parsed['type'] == 'feat':
            sections['feat'].append(parsed)
        elif parsed['type'] == 'fix':
            sections['fix'].append(parsed)
        else:
            sections['other'].append(parsed)

    lines = [f"## [{version}] - {date_str}", ""]

    if sections['breaking']:
        lines.append("### ⚠ BREAKING CHANGES")
        lines.append("")
        for item in sections['breaking']:
            scope = f"**{item['scope']}:** " if item['scope'] else ""
            lines.append(f"* {scope}{item['description']}")
        lines.append("")

    if sections['feat']:
        lines.append("### Features")
        lines.append("")
        for item in sections['feat']:
            scope = f"**{item['scope']}:** " if item['scope'] else ""
            lines.append(f"* {scope}{item['description']}")
        lines.append("")

    if sections['fix']:
        lines.append("### Bug Fixes")
        lines.append("")
        for item in sections['fix']:
            scope = f"**{item['scope']}:** " if item['scope'] else ""
            lines.append(f"* {scope}{item['description']}")
        lines.append("")

    return '\n'.join(lines)


def update_changelog(changelog_path, new_entry):
    """
    Update the changelog file with a new entry.

    Inserts the new entry after the header.
    """
    if os.path.exists(changelog_path):
        with open(changelog_path, 'r') as f:
            existing = f.read()
    else:
        existing = "# Changelog\n\nAll notable changes to this project will be documented in this file.\n\n"

    # Find where to insert (after the header)
    header_end = existing.find('\n\n', existing.find('# '))
    if header_end == -1:
        header_end = len(existing)
    else:
        header_end += 2

    new_content = existing[:header_end] + new_entry + '\n' + existing[header_end:]

    # Ensure directory exists
    os.makedirs(os.path.dirname(changelog_path) or '.', exist_ok=True)

    with open(changelog_path, 'w') as f:
        f.write(new_content)

    return changelog_path
EOF

RUN cat > /home/user/releaser/release.py << 'EOF'
#!/usr/bin/env python3
"""
Release automation tool - main entry point.
"""

import os
import subprocess
import yaml

from semver import Version
from parse_commits import get_commits_since_tag, determine_bump_type
from changelog import generate_changelog_entry, update_changelog


def load_config(config_path='releaser.yaml'):
    """Load configuration from YAML file."""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def get_latest_tag(repo_path='.', prefix='v'):
    """Get the latest version tag from the repository."""
    try:
        result = subprocess.run(
            ['git', 'tag', '-l', f'{prefix}*', '--sort=-v:refname'],
            capture_output=True,
            text=True,
            cwd=repo_path,
            check=True
        )
        tags = result.stdout.strip().split('\n')
        return tags[0] if tags and tags[0] else None
    except subprocess.CalledProcessError:
        return None


def main():
    """Main release workflow."""
    # Load configuration
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(script_dir, 'releaser.yaml')
    config = load_config(config_path)

    repo_path = os.path.join(script_dir, 'project')
    tag_prefix = config.get('tag_prefix', 'v')
    changelog_path = config.get('changelog_path', './CHANGELOG.md')

    # Make changelog path absolute relative to script dir
    if not os.path.isabs(changelog_path):
        changelog_path = os.path.join(script_dir, changelog_path)

    # Get current version from latest tag
    latest_tag = get_latest_tag(repo_path, tag_prefix)
    if not latest_tag:
        print("No existing version tag found, starting at 0.1.0")
        current_version = Version("0.0.0", config)
        latest_tag = "v0.0.0"
    else:
        print(f"Current version: {latest_tag}")
        current_version = Version(latest_tag, config)

    # Get commits since last tag
    commits = get_commits_since_tag(latest_tag, repo_path)
    if not commits:
        print("No new commits since last release")
        return

    print(f"Found {len(commits)} commit(s) since {latest_tag}")

    # Determine bump type
    bump_type = determine_bump_type(commits)
    print(f"Recommended bump type: {bump_type}")

    # Check if major bump is allowed by policy
    if bump_type == 'major' and not current_version.can_bump_major():
        print(f"Warning: major bump requested but blocked by policy, using minor")
        bump_type = 'minor'

    # Calculate new version
    if bump_type == 'major':
        new_version = current_version.bump_major()
    elif bump_type == 'minor':
        new_version = current_version.bump_minor()
    else:
        new_version = current_version.bump_patch()

    print(f"New version: {new_version}")

    # Generate changelog entry
    changelog_entry = generate_changelog_entry(str(new_version), commits, repo_path)

    # Update changelog
    update_changelog(changelog_path, changelog_entry)
    print(f"Updated changelog at {changelog_path}")

    print(f"\nRelease {new_version} prepared successfully!")
    print(f"Next steps:")
    print(f"  1. Review the changelog")
    print(f"  2. Commit the changes")
    print(f"  3. Create tag: git tag {tag_prefix}{new_version}")
    print(f"  4. Push: git push && git push --tags")


if __name__ == '__main__':
    main()
EOF

RUN cat > /home/user/releaser/releaser.yaml << 'EOF'
max_minor_before_major: "9"
changelog_path: ./project/CHANGELOG.md
tag_prefix: v
EOF

WORKDIR /home/user/releaser/project

RUN git init && \
    git config user.email "dev@example.com" && \
    git config user.name "Developer"

RUN echo "# Test Project" > README.md && \
    git add README.md && \
    git commit -m "Initial commit"

RUN echo "version 1" >> README.md && \
    git add README.md && \
    git commit -m "feat: initial release" && \
    git tag v1.0.0

RUN echo "version 2" >> README.md && \
    git add README.md && \
    git commit -m "feat!: major redesign" && \
    git tag v2.0.0

RUN for i in 1 2 3 4 5 6 7 8 9; do \
        echo "minor $i" >> README.md && \
        git add README.md && \
        git commit -m "feat: feature $i" && \
        git tag v2.$i.0; \
    done

RUN echo "patch 1" >> README.md && \
    git add README.md && \
    git commit -m "fix: bug fix 1" && \
    git tag v2.9.1

RUN echo "patch 2" >> README.md && \
    git add README.md && \
    git commit -m "fix: bug fix 2" && \
    git tag v2.9.2

RUN echo "patch 3" >> README.md && \
    git add README.md && \
    git commit -m "fix: bug fix 3" && \
    git tag v2.9.3

RUN echo "token fix" >> README.md && \
    git add README.md && \
    git commit -m "fix: correct token expiry"

RUN echo "oauth support" >> README.md && \
    git add README.md && \
    git commit -m "feat: add oauth support"

RUN echo "auth redesign" >> README.md && \
    git add README.md && \
    git commit -m "feat!: redesign authentication API"

WORKDIR /home/user/releaser

RUN chown -R 1000:1000 /home/user && \
    chmod -R 0777 /home/user

USER 1000

WORKDIR /home/user/releaser

CMD ["/bin/bash"]
