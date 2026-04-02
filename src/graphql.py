import requests
from config import HEADERS, GRAPHQL_URL, OWNER, REPO, PROJECT_NUMBER
from logger import info


def run_query(query, variables=None):
    response = requests.post(
        GRAPHQL_URL,
        json={"query": query, "variables": variables or {}},
        headers=HEADERS,
    )
    response.raise_for_status()
    return response.json()


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
    """Fetch state of a specific issue."""
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
