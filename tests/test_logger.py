"""Tests for the logger module."""

import json
import os
import tempfile
from pathlib import Path
from unittest import TestCase

from github_org_user_removal.logger import RemovalLogger, RemovalStatus


class TestRemovalLogger(TestCase):
    """Test the RemovalLogger class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.log_dir = self.temp_dir.name
    
    def tearDown(self):
        """Tear down test fixtures."""
        self.temp_dir.cleanup()
    
    def test_log_removal_json(self):
        """Test logging a user removal operation in JSON format."""
        # Create logger
        logger = RemovalLogger(log_format="json", log_dir=self.log_dir)
        
        # Log some removals
        logger.log_removal("user1", RemovalStatus.SUCCESS)
        logger.log_removal(
            "user2", 
            RemovalStatus.FAILED, 
            error_message="User not found"
        )
        logger.log_removal(
            "user3", 
            RemovalStatus.SKIPPED, 
            error_message="Not a member", 
            extra_data={"reason": "skip"}
        )
        
        # Save log
        log_path = logger.save_log()
        
        # Verify log file was created
        self.assertTrue(os.path.exists(log_path))
        
        # Read log file
        with open(log_path, 'r') as f:
            log_data = json.load(f)
        
        # Verify log contents
        self.assertEqual(3, len(log_data))
        
        # Check first record
        self.assertEqual("user1", log_data[0]["username"])
        self.assertEqual(RemovalStatus.SUCCESS.value, log_data[0]["status"])
        
        # Check second record
        self.assertEqual("user2", log_data[1]["username"])
        self.assertEqual(RemovalStatus.FAILED.value, log_data[1]["status"])
        self.assertEqual("User not found", log_data[1]["error_message"])
        
        # Check third record
        self.assertEqual("user3", log_data[2]["username"])
        self.assertEqual("skip", log_data[2]["reason"])
    
    def test_log_removal_csv(self):
        """Test logging a user removal operation in CSV format."""
        # Create logger
        logger = RemovalLogger(log_format="csv", log_dir=self.log_dir)
        
        # Log some removals
        logger.log_removal("user1", RemovalStatus.SUCCESS)
        logger.log_removal(
            "user2", 
            RemovalStatus.FAILED, 
            error_message="User not found"
        )
        
        # Save log
        log_path = logger.save_log()
        
        # Verify log file was created
        self.assertTrue(os.path.exists(log_path))
        
        # Read log file contents
        with open(log_path, 'r') as f:
            contents = f.read()
        
        # Verify CSV header
        self.assertIn("timestamp", contents)
        self.assertIn("username", contents)
        self.assertIn("status", contents)
        
        # Verify records
        self.assertIn("user1", contents)
        self.assertIn("SUCCESS", contents)
        self.assertIn("user2", contents)
        self.assertIn("FAILED", contents)
        self.assertIn("User not found", contents)