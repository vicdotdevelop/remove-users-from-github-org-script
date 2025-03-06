"""Command-line interface for GitHub organization user removal."""

import argparse
import os
import sys
from typing import Optional

import colorama
from dotenv import load_dotenv

from github_org_user_removal.crypto import TokenManager
from github_org_user_removal.logger import RemovalLogger
from github_org_user_removal.remover import GitHubOrgUserRemover


def main() -> int:
    """Run the GitHub organization user removal utility."""
    colorama.init()
    
    # Load environment variables from .env file if it exists
    load_dotenv()
    
    parser = argparse.ArgumentParser(
        description="GitHub Enterprise Organization User Removal Utility",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Remove users using token from file
  python -m github_org_user_removal --org-name "my-enterprise-org" --input-file users_to_remove.csv --token-file github_token.enc
        
  # Remove users using token from environment variable
  python -m github_org_user_removal --org-name "my-enterprise-org" --input-file users_to_remove.csv --env-token GITHUB_TOKEN
        
  # Encrypt a token to a file
  python -m github_org_user_removal --encrypt-token --token-file github_token.enc
        """
    )
    
    parser.add_argument("--org-name", help="GitHub organization name")
    parser.add_argument("--input-file", help="CSV file containing usernames to remove")
    parser.add_argument("--token-file", help="File containing encrypted GitHub token")
    parser.add_argument("--env-token", help="Environment variable name containing GitHub token")
    parser.add_argument("--encrypt-token", action="store_true", help="Encrypt a GitHub token to a file")
    parser.add_argument(
        "--log-format", 
        choices=["json", "csv"], 
        default="json", 
        help="Format for log output (default: json)"
    )
    parser.add_argument(
        "--log-dir", 
        default="logs", 
        help="Directory to store log files (default: logs)"
    )
    parser.add_argument(
        "--delay", 
        type=float, 
        default=1.0, 
        help="Delay in seconds between API calls to avoid rate limiting (default: 1.0)"
    )
    parser.add_argument(
        "--dry-run", 
        action="store_true",
        help="Validate inputs but don't actually remove users"
    )
    
    args = parser.parse_args()
    
    # If encrypting a token, handle that and exit
    if args.encrypt_token:
        if not args.token_file:
            print("Error: --token-file is required with --encrypt-token")
            return 1
        
        token_manager = TokenManager()
        print("Enter the GitHub token to encrypt:")
        token = input().strip()
        
        if not token:
            print("Error: Token cannot be empty")
            return 1
        
        try:
            token_manager.save_encrypted_token(token, args.token_file)
            print(f"Token encrypted and saved to {args.token_file}")
            return 0
        except Exception as e:
            print(f"Error encrypting token: {e}")
            return 1
    
    # Validate required arguments for user removal
    if not args.org_name:
        print("Error: --org-name is required")
        return 1
    
    if not args.input_file:
        print("Error: --input-file is required")
        return 1
    
    if not args.token_file and not args.env_token:
        print("Error: Either --token-file or --env-token is required")
        return 1
    
    # Get the GitHub token
    github_token = get_github_token(args.token_file, args.env_token)
    if not github_token:
        return 1
    
    # Initialize logger
    logger = RemovalLogger(log_format=args.log_format, log_dir=args.log_dir)
    
    try:
        # Initialize remover
        remover = GitHubOrgUserRemover(
            github_token=github_token,
            org_name=args.org_name,
            logger=logger,
            delay=args.delay
        )
        
        if args.dry_run:
            print(f"DRY RUN: Would remove users from organization {args.org_name}")
            usernames = remover.read_usernames_from_csv(args.input_file)
            print(f"Found {len(usernames)} usernames in {args.input_file}")
            print("Validating usernames...")
            
            # Validate all usernames but don't remove them
            valid_count = 0
            for username in usernames:
                is_valid, error = remover.validator.validate_username(username)
                if is_valid:
                    valid_count += 1
                    print(f"✓ {username}")
                else:
                    print(f"✗ {username}: {error}")
            
            print(f"\nValidation complete. Valid: {valid_count}, Invalid: {len(usernames) - valid_count}")
            logger.save_log()
        else:
            # Remove users
            remover.remove_users_from_csv(args.input_file)
        
        return 0
    
    except Exception as e:
        print(f"Error: {e}")
        return 1


def get_github_token(token_file: Optional[str], env_token: Optional[str]) -> Optional[str]:
    """Get GitHub token from file or environment variable."""
    if token_file:
        try:
            if not os.path.exists(token_file):
                print(f"Error: Token file not found: {token_file}")
                return None
            
            token_manager = TokenManager()
            return token_manager.load_encrypted_token(token_file)
        except Exception as e:
            print(f"Error loading token from file: {e}")
            return None
    
    elif env_token:
        token = os.environ.get(env_token)
        if not token:
            print(f"Error: Environment variable {env_token} not found or empty")
            return None
        return token
    
    return None


if __name__ == "__main__":
    sys.exit(main())