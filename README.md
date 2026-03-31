## Introduction

This GitHub Action identifies if a blocking issue has been resolved and notify the stakeholders in the blocked issue via comment. 
Blocked issue is an issue with project status "Blocked" or label "blocked".
If there are multiple blocking issues, it will not comment again if there is already a comment for an already close issue, but it will notify again if there is 
another blocking issue that has been resolved. 

### Prerequisites

Before you can start using this GitHub Action, you'll need to ensure you have the following:

1. A GitHub repository where you want to enable this action.
2. A GitHub project board.
3. "Status" field should be "Single select" type and has a value "Blocked"
4. "blocked" value as a label.
5. A Token (Classic) with permissions to repo:*, read:user, user:email, read:project

### Inputs

| Input                                | Description                                                                                      |
|--------------------------------------|--------------------------------------------------------------------------------------------------|
| `gh_token`                           | The GitHub Token                                                                                 |
| `project_number`                     | The project number                                                                               |                                                         
| `enterprise_github` _(optional)_     | `True` if you are using enterprise github and false if not. Default is `False`                   |
| `repository_owner_type` _(optional)_ | The type of the repository owner (oragnization or user). Default is `user`                       |
| `dry_run` _(optional)_               | `True` if you want to enable dry-run mode. Default is `False`                                    |


### Examples

#### Notify for close blocking issues with comment
To set up blocking issues comment notifications, you'll need to create or update a GitHub Actions workflow in your repository. Below is
an example of a workflow YAML file:

```yaml
name: Check Blocked Issues Resolution

on:
  schedule:
    - cron: '0 5,10 * * *'  # Runs twice daily at 05:00 and 10:00 UTC
  workflow_dispatch:

concurrency:
  group: blocked_resolution_check
  cancel-in-progress: true

jobs:
  check_blocked_resolution:
    runs-on: self-hosted
    timeout-minutes: 20

    steps:
      - name: Checkout Repository
        uses: actions/checkout@v3

      - name: Check Blocked Issues Resolution
        uses: emily-lambrou/blocked_resolution_check@v1.0
        with:
          gh_token: ${{ secrets.GH_TOKEN }}
          project_number: ${{ vars.PROJECT_NUMBER }}
          dry_run: ${{ vars.DRY_RUN }}
          enterprise_github: 'True'
          repository_owner_type: organization
        
```

