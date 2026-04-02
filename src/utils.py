import re

COMMENT_TEMPLATE = (
    "The issue number #{blocker} has been resolved. "
    "Please check if you can proceed."
)

def extract_blockers(issue_body):
    "def extract_blockers(issue_body):
    """
    Extract blocker references from the 'Blocked by' section.
    Supports:
      - #123
      - repo#456
      - org/repo#789
      - Full GitHub URLs
    """
    if not issue_body:
        return []

    # Extract the "Blocked by" section
    section_match = re.search(
        r"##\s*Blocked by(.*?)(\n##|\Z)",
        issue_body,
        re.IGNORECASE | re.DOTALL,
    )

    if not section_match:
        return []

    section = section_match.group(1)

    references = []

    # Match org/repo#123, repo#123, or #123
    pattern = r"(?:[\w\-.]+\/[\w\-.]+#\d+|[\w\-.]+#\d+|#\d+)"
    references.extend(re.findall(pattern, section))

    # Match full GitHub URLs
    url_pattern = r"https?://[^/]+/([\w\-.]+)/([\w\-.]+)/issues/(\d+)"
    for owner, repo, number in re.findall(url_pattern, section):
        references.append(f"{owner}/{repo}#{number}")

    return list(set(references))
    
def build_comment(blocker_number, assignees):
    base_message = (
        f"The issue number #{blocker_number} has been resolved. "
        f"Please check if you can proceed."
    )

    if not assignees:
        return base_message, base_message

    mentions = " ".join([f"@{a}" for a in assignees])
    full_message = f"{mentions} {base_message}"

    return base_message, full_message

def comment_exists(comments, message):
    return any(message in comment["body"] for comment in comments)
