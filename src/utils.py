import re

COMMENT_TEMPLATE = (
    "The issue number #{blocker} has been resolved. "
    "Please check if you can proceed."
)

def extract_blockers(issue_body):
    """Extract issue numbers from the 'Blocked by' section."""
    if not issue_body:
        return []

    match = re.search(
        r"Blocked by(.*?)(\n##|\Z)",
        issue_body,
        re.IGNORECASE | re.DOTALL
    )

    if not match:
        return []

    section = match.group(1)
    return [int(num.replace("#", "")) for num in re.findall(r"#\d+", section)]


def build_comment(blocker_number):
    return COMMENT_TEMPLATE.format(blocker=blocker_number)


def comment_exists(comments, message):
    return any(message in comment["body"] for comment in comments)
