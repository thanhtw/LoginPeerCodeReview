# First, update the imports at the top:
import streamlit as st
import logging
import time
from typing import Dict, Any, Optional, Callable
import os
from pathlib import Path
import base64

from auth.mysql_auth import MySQLAuthManager
from utils.language_utils import t, get_current_language, get_field_value  # Add get_field_value

# Then update the authentication methods:
class AuthUI:
    """
    UI Component for user authentication and profile management.
    
    This class handles the login, registration, and profile display interfaces
    for user authentication with a local JSON file.
    """
    def __init__(self):
        """Initialize the AuthUI component with local auth manager."""
        self.auth_manager = MySQLAuthManager()
        
        # Initialize session state for authentication
        if "auth" not in st.session_state:
            st.session_state.auth = {
                "is_authenticated": False,
                "user_id": None,
                "user_info": {}
            }
    
    def render_auth_page(self) -> bool:
        """
        Render the authentication page with login and registration forms.
        
        Returns:
            bool: True if user is authenticated, False otherwise
        """
        # Existing implementation...
        
        # For login functionality, update with get_field_value:
        if st.button(t("login"), use_container_width=True, key="login_button"):
            if not email or not password:
                st.error(t("fill_all_fields"))
            else:
                # Authenticate user
                result = self.auth_manager.authenticate_user(email, password)
                
                if get_field_value(result, "success", False):
                    # Set authenticated state
                    st.session_state.auth["is_authenticated"] = True
                    st.session_state.auth["user_id"] = get_field_value(result, "user_id")
                    st.session_state.auth["user_info"] = {
                        "display_name": get_field_value(result, "display_name"),
                        "email": get_field_value(result, "email"),
                        "level": get_field_value(result, "level", "basic")
                    }                     
                    st.success(t("login") + " " + t("login_failed"))
                    
                    # Force UI refresh
                    st.rerun()
                else:
                    st.error(f"{t('login_failed')}: {get_field_value(result, 'error', t('invalid_credentials'))}")
        
        # For registration, update similarly:
        if st.button(t("register"), use_container_width=True, key="register_button"):
            # Validate inputs
            if not display_name or not email or not password or not confirm_password:
                st.error(t("fill_all_fields"))
            elif password != confirm_password:
                st.error(t("passwords_mismatch"))
            else:
                # Register user
                result = self.auth_manager.register_user(
                    email=email,
                    password=password,
                    display_name=display_name,
                    level=level.lower()
                )
                
                if get_field_value(result, "success", False):
                    # Set authenticated state
                    st.session_state.auth["is_authenticated"] = True
                    st.session_state.auth["user_id"] = get_field_value(result, "user_id")
                    st.session_state.auth["user_info"] = {
                        "display_name": get_field_value(result, "display_name"),
                        "email": get_field_value(result, "email"),
                        "level": get_field_value(result, "level", "basic")
                    }
                    st.success(t("registration_failed"))
                    
                    # Force UI refresh
                    st.rerun()
                else:
                    st.error(f"{t('registration_failed')}: {get_field_value(result, 'error', t('email_in_use'))}")

    # Update render_user_profile method
    def render_user_profile(self):
        """Render the user profile section in the sidebar."""
        # Check if user is authenticated
        if not st.session_state.auth.get("is_authenticated", False):
            return
            
        # Get user info
        user_info = st.session_state.auth.get("user_info", {})
        display_name = get_field_value(user_info, "display_name", "User")
        level = get_field_value(user_info, "level", "basic").capitalize()     
        
        # Add styled profile section...
        
        # Get extended profile from database if user is not demo user
        if st.session_state.auth.get("user_id") != "demo-user":
            user_id = st.session_state.auth.get("user_id")
            try:
                profile = self.auth_manager.get_user_profile(user_id)
                if get_field_value(profile, "success", False):
                    # Display additional stats
                    reviews = get_field_value(profile, "reviews_completed", 0)
                    score = get_field_value(profile, "score", 0)                   
                    st.sidebar.markdown(f"""
                    <div class="profile-item">
                        <span class="profile-label">{t("review_times")}:</span>
                        <span class="profile-value">{reviews}</span>
                    </div>
                    <div class="profile-item">
                        <span class="profile-label">{t("score")}:</span>
                        <span class="profile-value">{score}</span>
                    </div>
                    """, unsafe_allow_html=True)   
            except Exception as e:
                logger.error(f"Error getting user profile: {str(e)}")

    # Update update_review_stats method
    def update_review_stats(self, accuracy: float, score: int = 0):
        """
        Update a user's review statistics after completing a review.
        
        Args:
            accuracy: The accuracy of the review (0-100 percentage)
            score: Number of errors detected in the review
        """
        # Check if user is authenticated
        if not st.session_state.auth.get("is_authenticated", False):
            return {"success": False, "error": "User not authenticated"}
                
        # Skip for demo user
        if st.session_state.auth.get("user_id") == "demo-user":
            return {"success": True, "message": "Demo user - no updates needed"}
                
        # Update stats in the database
        user_id = st.session_state.auth.get("user_id")
        
        # Ensure score is an integer
        score = int(score) if score else 0
        
        # Add debug logging
        logger.info(f"AuthUI: Updating stats for user {user_id}: accuracy={accuracy:.1f}%, score={score}")
        
        # IMPORTANT: Pass both accuracy AND score parameters to the auth manager
        result = self.auth_manager.update_review_stats(user_id, accuracy, score)

        if result and get_field_value(result, "success", False):
            logger.info(f"Updated user statistics: reviews={get_field_value(result, 'reviews_completed')}, " +
                    f"score={get_field_value(result, 'score')}")
            
            # Update session state if level changed
            if get_field_value(result, "level_changed", False):
                new_level = get_field_value(result, "new_level")
                if new_level and st.session_state.auth.get("user_info"):
                    st.session_state.auth["user_info"]["level"] = new_level
                    logger.info(f"Updated user level in session to: {new_level}")
        else:
            err_msg = get_field_value(result, 'error', 'Unknown error') if result else "No result returned"
            logger.error(f"Failed to update review stats: {err_msg}")
        
        return result

    # Update get_user_level method
    def get_user_level(self) -> str:
        """
        Get the user's level directly from the database.
        
        Returns:
            str: User's level (basic, medium, senior) or None if not authenticated
        """
        if not self.is_authenticated():
            return None
        
        user_id = st.session_state.auth.get("user_id")
        # Skip database query for demo users
        if user_id == "demo-user":
            return get_field_value(st.session_state.auth.get("user_info", {}), "level", "basic")
            
        try:
            # Query the database for the latest user info
            profile = self.auth_manager.get_user_profile(user_id)
            if get_field_value(profile, "success", False):
                # Update the session state with the latest level
                level = get_field_value(profile, "level", "basic")
                st.session_state.auth["user_info"]["level"] = level
                return level
            else:
                # Fallback to session state if query fails
                return get_field_value(st.session_state.auth.get("user_info", {}), "level", "basic")
        except Exception as e:
            logger.error(f"Error getting user level from database: {str(e)}")
            # Fallback to session state
            return get_field_value(st.session_state.auth.get("user_info", {}), "level", "basic")