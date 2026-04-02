import re

COMMENT_TEMPLATE = (
    "The issue {url} has been resolved. "
    "Please check if you can proceed."
)


def extract_blockers(issue_body):
    """
    Extract blocker references from the 'Blocked by' section.

    Supports:
      - #123
      - repo#456
      - org/repo#789
      - Full GitHub or GitHub Enterprise URLs
    """
    if not issue_body:
        return []

    # Match variations of "Blocked by"
    section_match = re.search(
        r"##\s*Blocked\s*By:?\s*(.*?)(\n##|\Z)",
        issue_body,
        re.IGNORECASE | re.DOTALL,
    )

    if not section_match:
        return []

    section = section_match.group(1)
    references = set()

    # Match issue references like #123, repo#123, org/repo#123
    pattern = r"(?:[\w\-.]+\/[\w\-.]+#\d+|[\w\-.]+#\d+|#\d+)"
    references.update(re.findall(pattern, section))

    # Match full GitHub URLs
    url_pattern = r"https?://[^/]+/[\w\-.]+/[\w\-.]+/issues/\d+"
    references.update(re.findall(url_pattern, section))

    return list(references)


def build_comment(blocker_number, blocker_url, assignees):
    """
    Build the notification comment.

    Returns:
        base_message: Used to detect duplicates.
        full_message: Includes assignee mentions.
    """
    base_message = COMMENT_TEMPLATE.format(url=blocker_url)

    if assignees:
        mentions = " ".join(f"@{assignee}" for assignee in assignees)
        full_message = f"{mentions} {base_message}"
    else:
        full_message = base_message

    return base_message, full_message


def comment_exists(comments, message):
    """Check if a similar comment already exists."""
    return any(message in comment.get("body", "") for comment in comments)
