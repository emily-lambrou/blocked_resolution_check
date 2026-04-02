import re
import requests
from config import HEADERS, GRAPHQL_URL, OWNER, REPO, PROJECT_NUMBER
from logger import info


def run_query(query, variables=None):
    """Execute a GraphQL query."""
    response = requests.post(
        GRAPHQL_URL,
        json={"query": query, "variables": variables or {}},
        headers=HEADERS,
    )
    response.raise_for_status()
    return response.json()


def resolve_issue_reference(reference):
    """
    Resolve issue references such as:
    - #123
    - repo#456
    - org/repo#789
    - Full GitHub or GitHub Enterprise URLs
    """
    reference = reference.strip()

    # Handle full GitHub/GitHub Enterprise URLs
    url_match = re.match(
        r"https?://[^/]+/(?P<org>[\w\-.]+)/(?P<repo>[\w\-.]+)/issues/(?P<number>\d+)",
        reference,
    )

    if url_match:
        org = url_match.group("org")
        repo = url_match.group("repo")
        number = int(url_match.group("number"))
    else:
        # Handle #123, repo#123, org/repo#123
        match = re.match(
            r"(?:(?P<org>[\w\-.]+)/)?(?:(?P<repo>[\w\-.]+))?#(?P<number>\d+)",
            reference,
        )

        if not match:
            info(f"Invalid issue reference: {reference}")
            return None

        org = match.group("org") or OWNER
        repo = match.group("repo") or REPO
        number = int(match.group("number"))

    query = """
    query($owner: String!, $repo: String!, $number: Int!) {
      repository(owner: $owner, name: $repo) {
        issue(number: $number) {
          id
          number
          state
          url
        }
      }
    }
    """

    variables = {
        "owner": org,
        "repo": repo,
        "number": number,
    }

    data = run_query(query, variables)

    return (
        data.get("data", {})
        .get("repository", {})
        .get("issue")
    )


def get_blocked_project_issues():
    """Fetch open issues where Project Status = Blocked."""
    query = """
    query($owner: String!, $projectNumber: Int!) {
      organization(login: $owner) {
        projectV2(number: $projectNumber) {
          items(first: 100) {
            nodes {
              content {
                ... on Issue {
                  id
                  number
                  state
                  body
                  assignees(first: 10) {
                    nodes {
                      login
                    }
                  }
                }
              }
              fieldValueByName(name: "Status") {
                ... on ProjectV2ItemFieldSingleSelectValue {
                  name
                }
              }
            }
          }
        }
      }
    }
    """

    variables = {
        "owner": OWNER,
        "projectNumber": PROJECT_NUMBER,
    }

    data = run_query(query, variables)
    issues = []

    items = data["data"]["organization"]["projectV2"]["items"]["nodes"]

    for item in items:
        content = item.get("content")
        if not content:
            continue

        status = item.get("fieldValueByName")
        if (
            content["state"] == "OPEN"
            and status
            and status["name"].lower() == "blocked"
        ):
            issues.append(content)

    info(f"Found {len(issues)} blocked issues from project.")
    return issues


def get_blocked_label_issues():
    """Fetch open issues with label 'blocked'."""
    query = """
    query($owner: String!, $repo: String!) {
      repository(owner: $owner, name: $repo) {
        issues(first: 100, states: OPEN, labels: ["blocked"]) {
          nodes {
            id
            number
            state
            body
            assignees(first: 10) {
              nodes {
                login
              }
            }
          }
        }
      }
    }
    """

    variables = {"owner": OWNER, "repo": REPO}
    data = run_query(query, variables)

    issues = data["data"]["repository"]["issues"]["nodes"]
    info(f"Found {len(issues)} blocked issues by label.")
    return issues


def get_issue_state(issue_number):
    """Fetch the state of a specific issue in the current repository."""
    query = """
    query($owner: String!, $repo: String!, $number: Int!) {
      repository(owner: $owner, name: $repo) {
        issue(number: $number) {
          state
        }
      }
    }
    """

    variables = {
        "owner": OWNER,
        "repo": REPO,
        "number": issue_number,
    }

    data = run_query(query, variables)
    return data["data"]["repository"]["issue"]["state"]


def get_issue_comments(issue_id):
    """Fetch comments of an issue."""
    query = """
    query($id: ID!) {
      node(id: $id) {
        ... on Issue {
          comments(first: 100) {
            nodes {
              body
            }
          }
        }
      }
    }
    """

    data = run_query(query, {"id": issue_id})
    return data["data"]["node"]["comments"]["nodes"]


def add_issue_comment(issue_id, body):
    """Add a comment to an issue."""
    mutation = """
    mutation($subjectId: ID!, $body: String!) {
      addComment(input: {subjectId: $subjectId, body: $body}) {
        clientMutationId
      }
    }
    """

    run_query(mutation, {"subjectId": issue_id, "body": body})
