from config import DRY_RUN
from logger import info
from utils import extract_blockers, build_comment, comment_exists
from graphql import (
    get_blocked_project_issues,
    get_blocked_label_issues,
    get_issue_comments,
    add_issue_comment,
    resolve_issue_reference,
)


def main():
    info("Starting blocked issue resolution check...")

    # Fetch issues blocked via Project Status
    project_issues = get_blocked_project_issues()

    # Fetch issues blocked via Label
    label_issues = get_blocked_label_issues()

    # Merge and remove duplicates
    issues = {
        issue["number"]: issue
        for issue in project_issues + label_issues
    }.values()

    info(f"Processing {len(issues)} blocked issues.")

    for issue in issues:
        issue_number = issue["number"]
        issue_id = issue["id"]
        issue_body = issue.get("body", "")

        assignee_nodes = issue.get("assignees", {}).get("nodes", [])
        assignees = [a["login"] for a in assignee_nodes]

        info(f"Checking Issue #{issue_number}")

        blockers = extract_blockers(issue_body)
        if not blockers:
            info("No blockers found.")
            continue

        comments = get_issue_comments(issue_id)

        for blocker_ref in blockers:
            info(f"Resolving blocker reference: {blocker_ref}")

            blocker_issue = resolve_issue_reference(blocker_ref)
            if not blocker_issue:
                info(f"Could not resolve blocker: {blocker_ref}")
                continue

            blocker_number = blocker_issue["number"]
            blocker_state = blocker_issue["state"]
            blocker_url = blocker_issue["url"]

            if blocker_state == "CLOSED":
                base_message, full_message = build_comment(
                    blocker_number,
                    blocker_url,
                    assignees,
                )

                # Prevent duplicate comments
                if not comment_exists(comments, base_message):
                    if DRY_RUN:
                        info(
                            f"[DRY RUN] Would comment on #{issue_number}: "
                            f"{full_message}"
                        )
                    else:
                        add_issue_comment(issue_id, full_message)
                        info(f"Comment added to Issue #{issue_number}")
                else:
                    info(
                        f"Comment already exists for blocker #{blocker_number}"
                    )

    info("Blocked issue resolution check completed.")


if __name__ == "__main__":
    main()
