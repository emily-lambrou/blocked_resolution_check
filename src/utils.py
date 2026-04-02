import re

COMMENT_TEMPLATE = (
    "The issue number #{blocker} has been resolved. "
    "Please check if you can proceed."
)


def extract_blockers(issue_body):
    """
    Extract blocker references from the 'Blocked by' section.

    Supported formats:
      - #123
      - repo#456
      - org/repo#789
      - Full GitHub URLs:
        https://github.example.com/org/repo/issues/123
    """
    if not issue_body:
        return []

    # Extract the "Blocked by" section
    section_match = re.search(
        r"##\s*Blocked\s+By:?\s*(.*?)(\n##|\Z)",        
        issue_body,
        re.IGNORECASE | re.DOTALL,
    )

    if not section_match:
        return []

    section = section_match.group(1)

    references = set()

    # Match org/repo#123, repo#123, or #123
    pattern = r"(?:[\w\-.]+\/[\w\-.]+#\d+|[\w\-.]+#\d+|#\d+)"
    references.update(re.findall(pattern, section))

    # Match full GitHub or GitHub Enterprise URLs
    url_pattern = r"https?://[^/]+/([\w\-.]+)/([\w\-.]+)/issues/(\d+)"
    for owner, repo, number in re.findall(url_pattern, section):
        references.add(f"{owner}/{repo}#{number}")

    return sorted(references)


def build_comment(blocker_number, assignees):
    """
    Build the notification comment.

    Returns:
        tuple:
            base_message: Used for duplicate detection.
            full_message: Includes assignee mentions.
    """
    base_message = COMMENT_TEMPLATE.format(blocker=blocker_number)

    if not assignees:
        return base_message, base_message

    mentions = " ".join(f"@{assignee}" for assignee in assignees)
    full_message = f"{mentions} {base_message}"

    return base_message, full_message


def comment_exists(comments, message):
    """
    Check if a comment already exists to prevent duplicates.
    Duplicate detection is based only on the base message,
    ignoring assignee mentions.
    """
    return any(message in comment.get("body", "") for comment in comments)
