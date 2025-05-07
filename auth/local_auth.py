"""
Local file-based authentication for Java Peer Review Training System.

This module provides authentication functions using a local JSON file
instead of Firebase, making it simpler to set up and use.
"""

import os
import json
import logging
import datetime
import hashlib
import uuid
from typing import Dict, Any, List, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class LocalAuthManager:
    """
    Manager for local file-based authentication and user management.
    
    This class handles user registration, authentication, and profile management
    using a local JSON file as the database.
    """
    
    _instance = None
    
    def __new__(cls):
        """Ensure singleton instance."""
        if cls._instance is None:
            cls._instance = super(LocalAuthManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, users_file: str = "data/users.json"):
        """
        Initialize the LocalAuthManager.
        
        Args:
            users_file: Path to the JSON file storing user data
        """
        if self._initialized:
            return
            
        self.users_file = users_file
        self.users_data = self._load_users_data()
        self._initialized = True
    
    def _load_users_data(self) -> Dict[str, Dict[str, Any]]:
        """
        Load user data from the JSON file.
        
        Returns:
            Dictionary of user data, indexed by user_id
        """
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(self.users_file), exist_ok=True)
        
        # If the file doesn't exist, create it with empty data
        if not os.path.exists(self.users_file):
            empty_data = {}
            with open(self.users_file, 'w') as f:
                json.dump(empty_data, f, indent=2)
            return empty_data
        
        # Load existing data
        try:
            with open(self.users_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            logger.error(f"Error loading users data: {str(e)}")
            return {}
    
    def _save_users_data(self) -> bool:
        """
        Save user data to the JSON file.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.users_file), exist_ok=True)
            
            # Save the data
            with open(self.users_file, 'w') as f:
                json.dump(self.users_data, f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Error saving users data: {str(e)}")
            return False
    
    def _hash_password(self, password: str) -> str:
        """
        Hash a password using a simple SHA-256 algorithm.
        
        Args:
            password: Plain text password
            
        Returns:
            Hashed password string
        """
        # In a production system, you would use a more secure hashing method with salt
        return hashlib.sha256(password.encode()).hexdigest()
    
    def register_user(self, email: str, password: str, display_name: str, level: str = "basic") -> Dict[str, Any]:
        """
        Register a new user.
        
        Args:
            email: User's email address
            password: User's password
            display_name: User's display name
            level: User's level (basic, medium, senior)
            
        Returns:
            Dictionary with user information or error message
        """
        # Check if email is already in use
        for user_id, user_data in self.users_data.items():
            if user_data.get("email") == email:
                return {"success": False, "error": "Email already in use"}
        
        # Generate a unique user ID
        user_id = str(uuid.uuid4())
        
        # Hash the password
        hashed_password = self._hash_password(password)
        
        # Create the user data
        user_data = {
            "uid": user_id,
            "email": email,
            "display_name": display_name,
            "password": hashed_password,
            "level": level,
            "created_at": datetime.datetime.now().isoformat(),
            "reviews_completed": 0,
            "average_accuracy": 0.0
        }
        
        # Add to users data
        self.users_data[user_id] = user_data
        
        # Save the data
        if self._save_users_data():
            logger.info(f"Registered new user: {email} (ID: {user_id})")
            return {
                "success": True,
                "user_id": user_id,
                "email": email,
                "display_name": display_name,
                "level": level
            }
        else:
            return {"success": False, "error": "Error saving user data"}
    
    def authenticate_user(self, email: str, password: str) -> Dict[str, Any]:
        """
        Authenticate a user.
        
        Args:
            email: User's email address
            password: User's password
            
        Returns:
            Dictionary with user information or error message
        """
        # Hash the password for comparison
        hashed_password = self._hash_password(password)
        
        # Check each user
        for user_id, user_data in self.users_data.items():
            if user_data.get("email") == email and user_data.get("password") == hashed_password:
                logger.info(f"User authenticated: {email}")
                return {
                    "success": True,
                    "user_id": user_id,
                    "email": email,
                    "display_name": user_data.get("display_name"),
                    "level": user_data.get("level", "basic")
                }
        
        return {"success": False, "error": "Invalid email or password"}
    
    def get_user_profile(self, user_id: str) -> Dict[str, Any]:
        """
        Get a user's profile.
        
        Args:
            user_id: User's ID
            
        Returns:
            Dictionary with user profile or error message
        """
        if user_id in self.users_data:
            user_data = self.users_data[user_id]
            return {
                "success": True,
                "user_id": user_id,
                "email": user_data.get("email"),
                "display_name": user_data.get("display_name"),
                "level": user_data.get("level", "basic"),
                "reviews_completed": user_data.get("reviews_completed", 0),
                "average_accuracy": user_data.get("average_accuracy", 0.0)
            }
        
        return {"success": False, "error": "User not found"}
    
    def update_user_profile(self, user_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update a user's profile.
        
        Args:
            user_id: User's ID
            updates: Dictionary with fields to update
            
        Returns:
            Dictionary with success status or error message
        """
        if user_id not in self.users_data:
            return {"success": False, "error": "User not found"}
        
        # Ensure we don't update sensitive fields
        safe_updates = {k: v for k, v in updates.items() if k in [
            "display_name", "level", "reviews_completed", "average_accuracy"
        ]}
        
        # Update the user data
        self.users_data[user_id].update(safe_updates)
        
        # Save the data
        if self._save_users_data():
            return {"success": True}
        else:
            return {"success": False, "error": "Error saving user data"}
    
    def update_review_stats(self, user_id: str, accuracy: float) -> Dict[str, Any]:
        """
        Update a user's review statistics.
        
        Args:
            user_id: User's ID
            accuracy: Accuracy of the latest review (0-100)
            
        Returns:
            Dictionary with success status or error message
        """
        if user_id not in self.users_data:
            return {"success": False, "error": "User not found"}
        
        # Get current stats
        current_reviews = self.users_data[user_id].get("reviews_completed", 0)
        current_accuracy = self.users_data[user_id].get("average_accuracy", 0.0)
        
        # Calculate new stats
        new_reviews = current_reviews + 1
        new_accuracy = ((current_accuracy * current_reviews) + accuracy) / new_reviews
        
        # Update the user data
        self.users_data[user_id]["reviews_completed"] = new_reviews
        self.users_data[user_id]["average_accuracy"] = new_accuracy
        
        # Save the data
        if self._save_users_data():
            return {
                "success": True,
                "reviews_completed": new_reviews,
                "average_accuracy": new_accuracy
            }
        else:
            return {"success": False, "error": "Error saving user data"}
    
    def get_all_users(self) -> List[Dict[str, Any]]:
        """
        Get a list of all users.
        
        Returns:
            List of user data dictionaries
        """
        users = []
        for user_id, user_data in self.users_data.items():
            # Remove sensitive data
            user_info = {
                "user_id": user_id,
                "email": user_data.get("email"),
                "display_name": user_data.get("display_name"),
                "level": user_data.get("level", "basic"),
                "created_at": user_data.get("created_at"),
                "reviews_completed": user_data.get("reviews_completed", 0),
                "average_accuracy": user_data.get("average_accuracy", 0.0)
            }
            users.append(user_info)
        
        return users