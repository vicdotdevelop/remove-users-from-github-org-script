"""Validation utilities for GitHub usernames."""

import re
from typing import List, Optional, Tuple

from github import Github, GithubException


class UsernameValidator:
    """Validates GitHub usernames and their organization membership."""

    # GitHub username pattern allows alphanumeric characters and single hyphens
    # between alphanumeric characters (cannot start or end with a hyphen)
    USERNAME_PATTERN = r'^[a-zA-Z0-9](?:[a-zA-Z0-9]|-(?=[a-zA-Z0-9])){0,38}$'
    
    def __init__(self, github_client: Github, org_name: str):
        """Initialize validator with GitHub client and organization name."""
        self.github_client = github_client
        self.org_name = org_name
        
        # Get the organization
        try:
            self.organization = self.github_client.get_organization(org_name)
        except GithubException as e:
            raise ValueError(f"Could not access organization '{org_name}': {e}")
    
    def is_valid_username_format(self, username: str) -> bool:
        """Check if the username has a valid GitHub username format."""
        return bool(re.match(self.USERNAME_PATTERN, username))
    
    def is_org_member(self, username: str) -> bool:
        """Check if the user is a member of the organization."""
        try:
            return self.organization.has_in_members(self.github_client.get_user(username))
        except GithubException:
            return False
    
    def validate_username(self, username: str) -> Tuple[bool, Optional[str]]:
        """Validate a username for format and membership.
        
        Returns a tuple of (is_valid, error_message)
        """
        # Check format
        if not username or not isinstance(username, str):
            return False, "Username is empty or not a string"
        
        username = username.strip()
        
        if not self.is_valid_username_format(username):
            return False, f"Invalid username format: '{username}'"
        
        # Check membership
        try:
            if not self.is_org_member(username):
                return False, f"User '{username}' is not a member of organization '{self.org_name}'"
        except GithubException as e:
            return False, f"Error checking membership for '{username}': {e}"
        
        return True, None
    
    def validate_usernames(self, usernames: List[str]) -> List[Tuple[str, bool, Optional[str]]]:
        """Validate a list of usernames.
        
        Returns a list of tuples containing (username, is_valid, error_message)
        """
        results = []
        
        for username in usernames:
            username = username.strip() if isinstance(username, str) else ""
            is_valid, error = self.validate_username(username)
            results.append((username, is_valid, error))
        
        return results