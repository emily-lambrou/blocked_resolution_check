from config import DRY_RUN
from logger import info
from utils import extract_blockers, build_comment, comment_exists
from graphql import (
    get_blocked_project_issues,
    get_blocked_label_issues,
    get_issue_state,
    get_issue_comments,
    add_issue_comment,
)


def main():
    info("Starting blocked issue resolution check...")

    project_issues = get_blocked_project_issues()
    label_issues = get_blocked_label_issues()

    # Merge and remove duplicates
    issues = {issue["number"]: issue for issue in project_issues + label_issues}.values()

    info(f"Processing {len(issues)} blocked issues.")

    for issue in issues:
        issue_number = issue["number"]
        issue_id = issue["id"]
        issue_body = issue.get("body", "")

        info(f"Checking Issue #{issue_number}")

        blockers = extract_blockers(issue_body)
        if not blockers:
            info("No blockers found.")
            continue

        comments = get_issue_comments(issue_id)

        for blocker in blockers:
            state = get_issue_state(blocker)

            if state == "CLOSED":
                message = build_comment(blocker)

                if not comment_exists(comments, message):
                    if DRY_RUN:
                        info(f"[DRY RUN] Would comment on #{issue_number}: {message}")
                    else:
                        add_issue_comment(issue_id, message)
                        info(f"Comment added to Issue #{issue_number}")
                else:
                    info(f"Comment already exists for blocker #{blocker}")

    info("Blocked issue resolution check completed.")


if __name__ == "__main__":
    main()
