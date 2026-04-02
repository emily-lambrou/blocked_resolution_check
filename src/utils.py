import re

# Comment template used when a blocking issue is resolved
COMMENT_TEMPLATE = (
    "The issue {url} has been resolved. "
    "Please check if you can proceed."
)


def extract_blockers(issue_body):
    """
    Extract blocker references from the 'Blocked by' section.

    Supported formats:
      - ## Blocked by
      - ### Blocked By:
      - Blocked by:
      - **Blocked by**
      - **Blocked By:**
      - BLOCKED BY:
      - Any capitalization or markdown variation

    Supported references:
      - #123
      - repo#456
      - org/repo#789
      - Full GitHub or GitHub Enterprise URLs
    """
    if not issue_body:
        return []

    lines = issue_body.splitlines()
    blockers = []
    in_section = False

    for line in lines:
        stripped = line.strip()

        # Detect the start of the "Blocked by" section
        if re.match(
            r"^(?:#{1,6}\s*)?(?:\*\*|__)?\s*Blocked\s+By\s*:?(?:\*\*|__)?\s*$",
            stripped,
            re.IGNORECASE,
        ):
            in_section = True
            continue

        # Stop parsing when another section begins
        if in_section and re.match(
            r"^(?:#{1,6}\s+|\*\*.*\*\*|__.*__)",
            stripped
        ):
            break

        if not in_section:
            continue

        # Remove bullet points and extra whitespace
        stripped = re.sub(r"^[-*•\s]+", "", stripped)

        if not stripped:
            continue

        # Extract full GitHub or GitHub Enterprise URLs
        url_matches = re.findall(
            r"https?://[^/]+/[\w\-.]+/[\w\-.]+/issues/\d+",
            stripped,
        )
        blockers.extend(url_matches)

        # Extract issue references such as #123, repo#123, org/repo#123
        ref_matches = re.findall(
            r"(?:[\w\-.]+\/[\w\-.]+#\d+|[\w\-.]+#\d+|#\d+)",
            stripped,
        )
        blockers.extend(ref_matches)

    # Remove duplicates while preserving order
    unique_blockers = list(dict.fromkeys(blockers))
    return unique_blockers


def build_comment(blocker_number, blocker_url, assignees):
    """
    Build the notification comment when a blocker is resolved.

    Args:
        blocker_number (int): The resolved blocker issue number.
        blocker_url (str): The full URL of the resolved issue.
        assignees (list): List of assignee usernames.

    Returns:
        tuple:
            base_message (str): Used for duplicate detection.
            full_message (str): Includes assignee mentions.
    """
    base_message = COMMENT_TEMPLATE.format(url=blocker_url)

    if assignees:
        mentions = " ".join(f"@{assignee}" for assignee in assignees)
        full_message = f"{mentions} {base_message}"
    else:
        full_message = base_message

    return base_message, full_message


def comment_exists(comments, message):
    """
    Check if a similar comment already exists on the issue.

    Args:
        comments (list): List of existing issue comments.
        message (str): Base message to search for.

    Returns:
        bool: True if the comment already exists, False otherwise.
    """
    return any(
        message in comment.get("body", "")
        for comment in comments
    )
