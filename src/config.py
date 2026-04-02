import os

GH_TOKEN = os.getenv("INPUT_GH_TOKEN")
PROJECT_NUMBER = int(os.getenv("INPUT_PROJECT_NUMBER", "0"))
DRY_RUN = os.getenv("INPUT_DRY_RUN", "False").lower() == "true"
ENTERPRISE_GITHUB = os.getenv("INPUT_ENTERPRISE_GITHUB", "False")
REPOSITORY_OWNER_TYPE = os.getenv("INPUT_REPOSITORY_OWNER_TYPE", "organization")

GITHUB_REPOSITORY = os.getenv("GITHUB_REPOSITORY", "")
OWNER, REPO = GITHUB_REPOSITORY.split("/")

BASE_URL = "https://github.intranet.unicaf.org/api"
GRAPHQL_URL = f"{BASE_URL}/graphql"

notification_type = os.environ['INPUT_NOTIFICATION_TYPE']

if notification_type not in ['comment', 'email']:
    raise Exception(f'Unsupported notification type {notification_type}')
    

HEADERS = {
    "Authorization": f"Bearer {GH_TOKEN}",
    "Accept": "application/vnd.github+json"
}
