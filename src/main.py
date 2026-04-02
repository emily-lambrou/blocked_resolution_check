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

    # Fetch blocked issues from Project and Label
    project_issues = get_blocked_project_issues()
    label_issues = get_blocked_label_issues()

    # Merge and remove duplicates using issue number
    issues = {
        issue["number"]: issue
        for issue in project_issues + label_issues
    }.values()

    info(f"Processing {len(issues)} blocked issues.")

    for issue in issues:
        issue_number = issue["number"]
        issue_id = issue["id"]
        issue_body = issue.get("body", "")

        # Extract assignees
        assignee_nodes = issue.get("assignees", {}).get("nodes", [])
        assignees = [a["login"] for a in assignee_nodes]

        info(f"Checking Issue #{issue_number}")

        # Extract blockers from the "Blocked by" section
        blockers = extract_blockers(issue_body)
        if not blockers:
            info("No blockers found.")
            continue

        # Fetch existing comments to avoid duplicates
        comments = get_issue_comments(issue_id)

        for blocker_ref in blockers:
            info(f"Resolving blocker reference: {blocker_ref}")

            # Resolve issue reference (supports cross-repository issues)
            blocker_issue = resolve_issue_reference(blocker_ref)

            if not blocker_issue:
                info(f"Unable to resolve blocker reference: {blocker_ref}")
                continue

            blocker_number = blocker_issue["number"]
            blocker_state = blocker_issue["state"]

            info(
                f"Blocker #{blocker_number} resolved with state: {blocker_state}"
            )

            if blocker_state == "CLOSED":
                base_message, full_message = build_comment(
                    blocker_number, assignees
                )

                # Check duplicates using ONLY the base message
                if not comment_exists(comments, base_message):
                    if DRY_RUN:
                        info(
                            f"[DRY RUN] Would comment on "
                            f"#{issue_number}: {full_message}"
                        )
                    else:
                        add_issue_comment(issue_id, full_message)
                        info(
                            f"Comment added to Issue #{issue_number}"
                        )
                else:
                    info(
                        f"Comment already exists for blocker "
                        f"#{blocker_number}"
                    )

    info("Blocked issue resolution check completed.")


if __name__ == "__main__":
    main()
