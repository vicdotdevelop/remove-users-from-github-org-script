"""Tests for the crypto module."""

import os
from unittest import TestCase

from github_org_user_removal.crypto import TokenManager


class TestTokenManager(TestCase):
    """Test the TokenManager class."""

    def setUp(self):
        """Set up test fixtures."""
        # Use a fixed salt for testing
        self.test_salt = b'\x00' * 16
        self.token_manager = TokenManager(salt=self.test_salt)
        self.test_token = "ghp_abcdefghijklmnopqrstuvwxyz0123456789"
        self.test_password = "test-password"
    
    def test_encrypt_decrypt_token(self):
        """Test that tokens can be encrypted and then decrypted."""
        # Encrypt the token
        encrypted_data = self.token_manager.encrypt_token(self.test_token, self.test_password)
        
        # Verify the salt is included
        self.assertEqual(self.test_salt, encrypted_data[:16])
        
        # Decrypt the token
        decrypted_token = self.token_manager.decrypt_token(encrypted_data, self.test_password)
        
        # Verify the decrypted token matches the original
        self.assertEqual(self.test_token, decrypted_token)
    
    def test_decrypt_with_wrong_password(self):
        """Test that decryption fails with wrong password."""
        # Encrypt the token
        encrypted_data = self.token_manager.encrypt_token(self.test_token, self.test_password)
        
        # Try to decrypt with wrong password
        with self.assertRaises(Exception):
            self.token_manager.decrypt_token(encrypted_data, "wrong-password")
    
    def test_different_salt_produces_different_ciphertext(self):
        """Test that using different salt produces different ciphertext."""
        # Create a token manager with different salt
        different_salt = b'\x01' * 16
        different_token_manager = TokenManager(salt=different_salt)
        
        # Encrypt the same token with different managers
        encrypted1 = self.token_manager.encrypt_token(self.test_token, self.test_password)
        encrypted2 = different_token_manager.encrypt_token(self.test_token, self.test_password)
        
        # Verify the encrypted data is different (excluding the salt)
        self.assertNotEqual(encrypted1[16:], encrypted2[16:])