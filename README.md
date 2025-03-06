# GitHub Enterprise Organization User Removal Utility

A Python command-line tool to programmatically remove users from a GitHub Enterprise Organization.

## Features

- Remove users from a GitHub Enterprise Organization using the GitHub API
- Accept usernames from a CSV file
- Validate GitHub usernames and organization membership
- Secure token management with encryption
- Comprehensive logging of all operations
- Rate limiting protection
- Dry-run mode to validate without removing users

## Installation

1. This project uses Poetry for dependency management. First, make sure you have Poetry installed:

```bash
# Install Poetry if you don't have it
curl -sSL https://install.python-poetry.org | python3 -
```

2. Clone the repository and install dependencies:

```bash
git clone <repository-url>
cd github-org-user-removal
poetry install
```

## Usage

### Encrypting Your GitHub Token

First, encrypt your GitHub Personal Access Token (requires `admin:org` and `read:user` scopes):

```bash
poetry run python -m github_org_user_removal --encrypt-token --token-file github_token.enc
```

### CSV Input Format

Create a CSV file with the list of GitHub usernames to remove (one username per line):

```
johndoe
janedoe
mikebrown
```

### Removing Users

To remove users from an organization:

```bash
poetry run python -m github_org_user_removal \
    --org-name "my-enterprise-org" \
    --input-file users_to_remove.csv \
    --token-file github_token.enc
```

### Using Environment Variables

You can also use a GitHub token from an environment variable:

```bash
export GITHUB_TOKEN=your_token_here
poetry run python -m github_org_user_removal \
    --org-name "my-enterprise-org" \
    --input-file users_to_remove.csv \
    --env-token GITHUB_TOKEN
```

### Dry Run Mode

To validate usernames without actually removing users:

```bash
poetry run python -m github_org_user_removal \
    --org-name "my-enterprise-org" \
    --input-file users_to_remove.csv \
    --token-file github_token.enc \
    --dry-run
```

### Log Formats

Choose between JSON and CSV log formats:

```bash
poetry run python -m github_org_user_removal \
    --org-name "my-enterprise-org" \
    --input-file users_to_remove.csv \
    --token-file github_token.enc \
    --log-format csv
```

## Command Line Options

```
  --org-name ORG_NAME    GitHub organization name
  --input-file INPUT_FILE
                        CSV file containing usernames to remove
  --token-file TOKEN_FILE
                        File containing encrypted GitHub token
  --env-token ENV_TOKEN
                        Environment variable name containing GitHub token
  --encrypt-token        Encrypt a GitHub token to a file
  --log-format {json,csv}
                        Format for log output (default: json)
  --log-dir LOG_DIR      Directory to store log files (default: logs)
  --delay DELAY          Delay in seconds between API calls to avoid rate limiting (default: 1.0)
  --dry-run              Validate inputs but don't actually remove users
```

## Security Considerations

- The GitHub token is encrypted using Fernet symmetric encryption with a password-based key derivation function
- The password is never stored
- Use a secure and memorable password to protect your GitHub token
- Consider using a token with limited scope and time duration

## License

[MIT License](LICENSE)