"""Tests for the username validator module."""

from unittest import TestCase
from unittest.mock import MagicMock, patch

from github_org_user_removal.validator import UsernameValidator


class TestUsernameValidator(TestCase):
    """Test the UsernameValidator class."""

    def test_valid_username_format(self):
        """Test validation of username formats."""
        # Mock dependencies
        github_client = MagicMock()
        org = MagicMock()
        github_client.get_organization.return_value = org
        
        validator = UsernameValidator(github_client, "test-org")
        
        # Valid usernames
        self.assertTrue(validator.is_valid_username_format("user123"))
        self.assertTrue(validator.is_valid_username_format("user-name"))
        self.assertTrue(validator.is_valid_username_format("a1b2c3"))
        
        # Invalid usernames
        self.assertFalse(validator.is_valid_username_format(""))
        self.assertFalse(validator.is_valid_username_format("-user"))  # Starts with hyphen
        self.assertFalse(validator.is_valid_username_format("user-"))  # Ends with hyphen
        self.assertFalse(validator.is_valid_username_format("user--name"))  # Double hyphen
        self.assertFalse(validator.is_valid_username_format("user$name"))  # Invalid character
        self.assertFalse(validator.is_valid_username_format("user name"))  # Contains space
    
    @patch("github_org_user_removal.validator.UsernameValidator.is_org_member")
    @patch("github_org_user_removal.validator.UsernameValidator.is_valid_username_format")
    def test_validate_username(self, mock_valid_format, mock_is_member):
        """Test the validate_username method."""
        # Mock dependencies
        github_client = MagicMock()
        org = MagicMock()
        github_client.get_organization.return_value = org
        
        validator = UsernameValidator(github_client, "test-org")
        
        # Test valid username
        mock_valid_format.return_value = True
        mock_is_member.return_value = True
        is_valid, error = validator.validate_username("validuser")
        self.assertTrue(is_valid)
        self.assertIsNone(error)
        
        # Test invalid format
        mock_valid_format.return_value = False
        mock_is_member.return_value = True
        is_valid, error = validator.validate_username("invalid$user")
        self.assertFalse(is_valid)
        self.assertIn("Invalid username format", error)
        
        # Test not a member
        mock_valid_format.return_value = True
        mock_is_member.return_value = False
        is_valid, error = validator.validate_username("notmember")
        self.assertFalse(is_valid)
        self.assertIn("not a member", error)