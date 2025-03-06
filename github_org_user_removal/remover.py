"""Core functionality for removing users from GitHub organizations."""

import csv
import time
from pathlib import Path
from typing import List, Optional

from github import Github, GithubException

from github_org_user_removal.logger import RemovalLogger, RemovalStatus
from github_org_user_removal.validator import UsernameValidator


class GitHubOrgUserRemover:
    """Handles the removal of users from GitHub organizations."""
    
    def __init__(
        self,
        github_token: str,
        org_name: str,
        logger: Optional[RemovalLogger] = None,
        delay: float = 1.0
    ):
        """Initialize the remover with GitHub credentials and settings.
        
        Args:
            github_token: Personal Access Token with admin:org scope
            org_name: Name of the GitHub organization
            logger: Logger instance for removal operations
            delay: Delay in seconds between API calls to avoid rate limiting
        """
        self.github = Github(github_token)
        self.org_name = org_name
        self.delay = delay
        
        # Initialize the organization
        try:
            self.organization = self.github.get_organization(org_name)
        except GithubException as e:
            raise ValueError(f"Could not access organization '{org_name}': {e}")
        
        # Initialize logger if not provided
        self.logger = logger or RemovalLogger()
        
        # Initialize validator
        self.validator = UsernameValidator(self.github, org_name)
    
    def read_usernames_from_csv(self, csv_path: str) -> List[str]:
        """Read usernames from a CSV file.
        
        Args:
            csv_path: Path to the CSV file containing usernames
            
        Returns:
            List of usernames read from the file
        """
        if not Path(csv_path).exists():
            raise FileNotFoundError(f"CSV file not found: {csv_path}")
        
        usernames = []
        with open(csv_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                if row and row[0].strip():
                    usernames.append(row[0].strip())
        
        return usernames
    
    def remove_user(self, username: str) -> bool:
        """Remove a single user from the organization.
        
        Args:
            username: GitHub username to remove
            
        Returns:
            True if removal was successful, False otherwise
        """
        # Validate username
        is_valid, error = self.validator.validate_username(username)
        
        if not is_valid:
            self.logger.log_removal(
                username=username,
                status=RemovalStatus.INVALID,
                error_message=error
            )
            return False
        
        # Proceed with removal
        try:
            user = self.github.get_user(username)
            self.organization.remove_from_members(user)
            
            self.logger.log_removal(
                username=username,
                status=RemovalStatus.SUCCESS
            )
            return True
            
        except GithubException as e:
            error_message = f"Failed to remove user: {e}"
            self.logger.log_removal(
                username=username,
                status=RemovalStatus.FAILED,
                error_message=error_message
            )
            return False
    
    def remove_users(self, usernames: List[str]) -> None:
        """Remove multiple users from the organization.
        
        Args:
            usernames: List of GitHub usernames to remove
        """
        success_count = 0
        fail_count = 0
        
        for i, username in enumerate(usernames):
            # Add delay to avoid rate limiting (except for first request)
            if i > 0 and self.delay > 0:
                time.sleep(self.delay)
            
            if self.remove_user(username):
                success_count += 1
            else:
                fail_count += 1
        
        # Log summary
        self.logger.logger.info(
            f"Removal complete. Success: {success_count}, Failed: {fail_count}, Total: {len(usernames)}"
        )
    
    def remove_users_from_csv(self, csv_path: str) -> None:
        """Read usernames from CSV and remove them from the organization.
        
        Args:
            csv_path: Path to CSV file containing usernames
        """
        usernames = self.read_usernames_from_csv(csv_path)
        
        if not usernames:
            self.logger.logger.warning(f"No usernames found in {csv_path}")
            return
        
        self.logger.logger.info(f"Removing {len(usernames)} users from {self.org_name}")
        self.remove_users(usernames)
        
        # Save the log
        log_path = self.logger.save_log()
        self.logger.logger.info(f"Operation log saved to {log_path}")