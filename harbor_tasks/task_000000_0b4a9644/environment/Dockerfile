FROM ubuntu:22.04

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install pytest PyYAML

RUN mkdir -p /home/user/releaser && chmod 0777 /home/user

WORKDIR /home/user/releaser

RUN cat > /home/user/releaser/config.yaml << 'EOF'
version_rules:
  major_triggers: [BREAKING]
  minor_triggers: [FEATURE, ENHANCEMENT]
  patch_triggers: [BUGFIX, SECURITY, DOCS]

changelog_sections:
  Breaking Changes: [BREAKING]
  Features: [FEATURE, ENHANCEMENT]
  Bug Fixes: [BUGFIX]
  Security: [SECURITY]
  Documentation: [DOCS]
EOF

RUN cat > /home/user/releaser/commits.json << 'EOF'
[{"hash": "abc123", "message": "SECURITY: Fix auth bypass vulnerability", "tag": "SECURITY"}]
EOF

RUN echo "2.3.1" > /home/user/releaser/VERSION

RUN cat > /home/user/releaser/CHANGELOG.md << 'EOF'
# Changelog

## [2.3.1] - 2024-01-15

### Bug Fixes
- Fixed minor UI glitch

## [2.3.0] - 2024-01-10

### Features
- Added new dashboard widget

## [2.2.0] - 2024-01-05

### Features
- Initial release with core functionality
EOF

RUN cat > /home/user/releaser/utils.py << 'UTILSEOF'
"""
Utility functions for the release tooling.
"""

import yaml


def _normalize_keys(obj):
    """
    Recursively normalize dictionary keys to lowercase for consistency.
    This ensures config keys are always lowercase regardless of how they're written.
    """
    if isinstance(obj, dict):
        return {k.lower(): _normalize_keys(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_normalize_keys(item) for item in obj]
    else:
        return obj


def load_config(filepath):
    """
    Load configuration from a YAML file.
    Keys are normalized to lowercase to ensure consistency.
    """
    with open(filepath, 'r') as f:
        raw_config = yaml.safe_load(f)
    # Normalize keys for consistency
    return _normalize_keys(raw_config)


def read_file(filepath):
    """Read and return file contents."""
    with open(filepath, 'r') as f:
        return f.read().strip()


def write_file(filepath, content):
    """Write content to file."""
    with open(filepath, 'w') as f:
        f.write(content)
UTILSEOF

RUN cat > /home/user/releaser/semver.py << 'SEMVEREOF'
"""
Semantic versioning logic for the release tooling.
"""


def parse_version(version_str):
    """Parse a version string into (major, minor, patch) tuple."""
    parts = version_str.strip().split('.')
    return int(parts[0]), int(parts[1]), int(parts[2])


def format_version(major, minor, patch):
    """Format version tuple back to string."""
    return f"{major}.{minor}.{patch}"


def bump_major(version_str):
    """Bump the major version, reset minor and patch."""
    major, minor, patch = parse_version(version_str)
    return format_version(major + 1, 0, 0)


def bump_minor(version_str):
    """Bump the minor version, reset patch."""
    major, minor, patch = parse_version(version_str)
    return format_version(major, minor + 1, 0)


def bump_patch(version_str):
    """Bump the patch version."""
    major, minor, patch = parse_version(version_str)
    return format_version(major, minor, patch + 1)


def bump_version(current, commit_tags, config):
    """
    Determine the appropriate version bump based on commit tags and config rules.

    Priority: major > minor > patch
    Iterates through commit tags and checks against rules.
    """
    rules = config['version_rules']

    # Check from highest to lowest priority
    for tag in commit_tags:
        # Normalize tag to uppercase for comparison
        normalized_tag = tag.upper()

        if normalized_tag in rules['major_triggers']:
            return bump_major(current)
        if normalized_tag in rules['minor_triggers']:
            return bump_minor(current)
        if normalized_tag in rules['patch_triggers']:
            return bump_patch(current)

    # No matching rule found
    return None
SEMVEREOF

RUN cat > /home/user/releaser/changelog.py << 'CHANGELOGEOF'
"""
Changelog generation logic for the release tooling.
"""

from datetime import datetime


def get_section_for_tag(tag, config):
    """
    Determine which changelog section a commit tag belongs to.
    Returns the section name or 'Other' if no match found.
    """
    sections = config['changelog_sections']

    # Normalize tag for comparison
    normalized_tag = tag.upper()

    for section_name, section_tags in sections.items():
        if normalized_tag in section_tags:
            return section_name

    # Default section if no match
    return 'Features'


def generate_changelog_entry(version, commits, config):
    """
    Generate a changelog entry for the given version and commits.
    Groups commits by their appropriate sections.
    """
    sections = {}

    for commit in commits:
        tag = commit.get('tag', 'OTHER')
        message = commit.get('message', '')

        section = get_section_for_tag(tag, config)

        if section not in sections:
            sections[section] = []
        sections[section].append(message)

    # Build the changelog entry
    date_str = datetime.now().strftime('%Y-%m-%d')
    entry_lines = [f"\n## [{version}] - {date_str}\n"]

    # Order sections consistently
    section_order = ['Breaking Changes', 'Features', 'Bug Fixes', 'Security', 'Documentation', 'Other']

    for section_name in section_order:
        if section_name in sections:
            entry_lines.append(f"\n### {section_name}\n")
            for msg in sections[section_name]:
                entry_lines.append(f"- {msg}\n")

    return ''.join(entry_lines)


def update_changelog(changelog_path, new_entry):
    """
    Update the changelog file by inserting the new entry after the header.
    """
    with open(changelog_path, 'r') as f:
        content = f.read()

    # Find the position after "# Changelog" header
    header = "# Changelog"
    if header in content:
        pos = content.find(header) + len(header)
        new_content = content[:pos] + new_entry + content[pos:]
    else:
        new_content = header + new_entry + "\n" + content

    with open(changelog_path, 'w') as f:
        f.write(new_content)
CHANGELOGEOF

RUN cat > /home/user/releaser/release.py << 'RELEASEPYEOF'
#!/usr/bin/env python3
"""
Main release script that coordinates version bumping and changelog generation.
"""

import json
import os
import sys

from utils import load_config, read_file, write_file
from semver import bump_version
from changelog import generate_changelog_entry, update_changelog


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(SCRIPT_DIR, 'config.yaml')
VERSION_PATH = os.path.join(SCRIPT_DIR, 'VERSION')
CHANGELOG_PATH = os.path.join(SCRIPT_DIR, 'CHANGELOG.md')
COMMITS_PATH = os.path.join(SCRIPT_DIR, 'commits.json')


def load_commits():
    """Load commits from the commits.json file."""
    with open(COMMITS_PATH, 'r') as f:
        return json.load(f)


def get_commit_tags(commits):
    """Extract tags from commits."""
    return [commit.get('tag', 'OTHER') for commit in commits]


def main():
    """Main release process."""
    # Load configuration
    config = load_config(CONFIG_PATH)

    # Load current version
    current_version = read_file(VERSION_PATH)
    print(f"Current version: {current_version}")

    # Load commits
    commits = load_commits()
    commit_tags = get_commit_tags(commits)
    print(f"Commit tags: {commit_tags}")

    # Determine new version
    new_version = bump_version(current_version, commit_tags, config)

    if new_version is None:
        # Unknown tag type - default to minor bump
        # This handles cases where commits don't match any configured trigger
        print(f"Warning: No matching version rule for tags {commit_tags}, defaulting to minor bump")
        from semver import bump_minor
        new_version = bump_minor(current_version)

    print(f"New version: {new_version}")

    # Update VERSION file
    write_file(VERSION_PATH, new_version)
    print(f"Updated VERSION file to {new_version}")

    # Generate and update changelog
    changelog_entry = generate_changelog_entry(new_version, commits, config)
    update_changelog(CHANGELOG_PATH, changelog_entry)
    print(f"Updated CHANGELOG.md with new entry")

    print("Release complete!")
    return 0


if __name__ == '__main__':
    sys.exit(main())
RELEASEPYEOF

RUN chmod 0777 /home/user/releaser && \
    chmod 0666 /home/user/releaser/config.yaml && \
    chmod 0666 /home/user/releaser/commits.json && \
    chmod 0666 /home/user/releaser/VERSION && \
    chmod 0666 /home/user/releaser/CHANGELOG.md && \
    chmod 0666 /home/user/releaser/utils.py && \
    chmod 0666 /home/user/releaser/semver.py && \
    chmod 0666 /home/user/releaser/changelog.py && \
    chmod 0755 /home/user/releaser/release.py

WORKDIR /home/user
