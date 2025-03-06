"""Logging utilities for the GitHub user removal operations."""

import csv
import json
import logging
import os
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional


class RemovalStatus(Enum):
    """Enumeration of possible removal status values."""
    
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"
    INVALID = "INVALID"


class RemovalLogger:
    """Logger for GitHub organization user removal operations."""
    
    def __init__(
        self, 
        log_format: str = "json", 
        log_dir: str = "logs"
    ):
        """Initialize the removal logger.
        
        Args:
            log_format: Format for log files ("json" or "csv").
            log_dir: Directory to store log files.
        """
        self.log_format = log_format.lower()
        self.log_dir = log_dir
        
        # Validate log format
        if self.log_format not in ["json", "csv"]:
            raise ValueError(f"Invalid log format: {log_format}. Must be 'json' or 'csv'")
        
        # Create log directory if it doesn't exist
        Path(self.log_dir).mkdir(parents=True, exist_ok=True)
        
        # Generate log filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_filename = f"org_user_removal_{timestamp}.{self.log_format}"
        self.log_path = os.path.join(self.log_dir, self.log_filename)
        
        # Initialize records list
        self.records: List[Dict[str, Any]] = []
        
        # Set up console logger
        self.logger = logging.getLogger("github_removal")
        self.logger.setLevel(logging.INFO)
        
        # Add console handler if not already added
        if not self.logger.handlers:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)
    
    def log_removal(
        self,
        username: str,
        status: RemovalStatus,
        error_message: Optional[str] = None,
        extra_data: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log a user removal operation.
        
        Args:
            username: The GitHub username being processed
            status: Status of the removal operation
            error_message: Error message (if any)
            extra_data: Additional data to log
        """
        timestamp = datetime.now().isoformat()
        
        record = {
            "timestamp": timestamp,
            "username": username,
            "status": status.value,
        }
        
        if error_message:
            record["error_message"] = error_message
        
        if extra_data:
            record.update(extra_data)
        
        self.records.append(record)
        
        # Log to console
        log_message = f"{username}: {status.value}"
        if error_message:
            log_message += f" - {error_message}"
        
        if status in [RemovalStatus.SUCCESS, RemovalStatus.SKIPPED]:
            self.logger.info(log_message)
        else:
            self.logger.error(log_message)
    
    def save_log(self) -> str:
        """Save the log to a file and return the file path."""
        if self.log_format == "json":
            self._save_json_log()
        else:  # csv
            self._save_csv_log()
        
        self.logger.info(f"Log saved to {self.log_path}")
        return self.log_path
    
    def _save_json_log(self) -> None:
        """Save logs in JSON format."""
        with open(self.log_path, 'w', encoding='utf-8') as file:
            json.dump(self.records, file, indent=2)
    
    def _save_csv_log(self) -> None:
        """Save logs in CSV format."""
        if not self.records:
            # Create empty file with headers
            with open(self.log_path, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(["timestamp", "username", "status", "error_message"])
            return
        
        # Get all fields from the records
        fieldnames = set()
        for record in self.records:
            fieldnames.update(record.keys())
        
        with open(self.log_path, 'w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=sorted(fieldnames))
            writer.writeheader()
            writer.writerows(self.records)