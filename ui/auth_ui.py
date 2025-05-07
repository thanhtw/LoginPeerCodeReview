"""
Authentication UI module for Java Peer Review Training System.

This module provides the AuthUI class for handling user authentication,
registration, and profile management using local JSON files.
"""

import streamlit as st
import logging
import time
from typing import Dict, Any, Optional, Callable

from auth.mysql_auth import MySQLAuthManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

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
        st.title("")

        st.markdown("""
            <div style="text-align: center; margin-bottom: 20px;">
                <h1 style="color: rgb(178 185 213); margin-bottom: 5px;">Java Code Review Trainer - Login</h1>                
            </div>
            """, unsafe_allow_html=True)
        
        # Create columns for login and registration
        col1, col2 = st.columns(2)
        
        with col1:
            # Login form
            st.subheader("Login")
            
            email = st.text_input("Email", key="login_email")
            password = st.text_input("Password", type="password", key="login_password")
            
            if st.button("Login", use_container_width=True):
                if not email or not password:
                    st.error("Please enter both email and password")
                else:
                    # Authenticate user
                    result = self.auth_manager.authenticate_user(email, password)
                    
                    if result.get("success", False):
                        # Set authenticated state
                        st.session_state.auth["is_authenticated"] = True
                        st.session_state.auth["user_id"] = result.get("user_id")
                        st.session_state.auth["user_info"] = {
                            "display_name": result.get("display_name"),
                            "email": result.get("email"),
                            "level": result.get("level", "basic")
                        }                     
                        st.success("Login successful!")
                        
                        # Force UI refresh
                        st.rerun()
                    else:
                        st.error(f"Login failed: {result.get('error', 'Invalid credentials')}")
        
        with col2:
            # Registration form
            st.subheader("Register")
            
            display_name = st.text_input("Display Name", key="reg_name")
            email = st.text_input("Email", key="reg_email")
            password = st.text_input("Password", type="password", key="reg_password")
            confirm_password = st.text_input("Confirm Password", type="password", key="reg_confirm")
            
            # Student level selection
            level = st.selectbox(
                "Your Experience Level",
                options=["Basic", "Medium", "Senior"],
                index=0,
                key="reg_level"
            )
            
            if st.button("Register", use_container_width=True):
                # Validate inputs
                if not display_name or not email or not password or not confirm_password:
                    st.error("Please fill in all fields")
                elif password != confirm_password:
                    st.error("Passwords do not match")
                else:
                    # Register user
                    result = self.auth_manager.register_user(
                        email=email,
                        password=password,
                        display_name=display_name,
                        level=level.lower()
                    )
                    
                    if result.get("success", False):
                        # Set authenticated state
                        st.session_state.auth["is_authenticated"] = True
                        st.session_state.auth["user_id"] = result.get("user_id")
                        st.session_state.auth["user_info"] = {
                            "display_name": result.get("display_name"),
                            "email": result.get("email"),
                            "level": result.get("level", "basic")
                        }
                        st.success("Registration successful!")
                        
                        # Force UI refresh
                        st.rerun()
                    else:
                        st.error(f"Registration failed: {result.get('error', 'Unknown error')}")
        
        # Add a demo mode option
        st.markdown("---")
        st.subheader("Demo Mode")
        if st.button("Continue in Demo Mode (No Login Required)"):
            # Set a demo user for testing
            st.session_state.auth["is_authenticated"] = True
            st.session_state.auth["user_id"] = "demo-user"
            st.session_state.auth["user_info"] = {
                "display_name": "Demo User",
                "email": "demo@example.com",
                "level": "basic"
            }
            return True
        
        return st.session_state.auth["is_authenticated"]
    
    def render_user_profile(self):
        """Render the user profile section in the sidebar."""
        # Check if user is authenticated
        if not st.session_state.auth.get("is_authenticated", False):
            return
            
        # Get user info
        user_info = st.session_state.auth.get("user_info", {})
        display_name = user_info.get("display_name", "User")
        level = user_info.get("level", "basic").capitalize()
        
        # Display user info       
        st.sidebar.markdown(f"**Hi:** {display_name} - **Your level**: {level}")
     
        # Get extended profile from database if user is not demo user
        if st.session_state.auth.get("user_id") != "demo-user":
            user_id = st.session_state.auth.get("user_id")
            try:
                profile = self.auth_manager.get_user_profile(user_id)
                if profile.get("success", False):
                    # Display additional stats
                    reviews = profile.get("reviews_completed", 0)
                    score = profile.get("score", 0)                   
                    st.sidebar.markdown(f"**Review Times:** {reviews} - **Your Score:** {score}")   
            except Exception as e:
                logger.error(f"Error getting user profile: {str(e)}")
        
        # Add logout button
        # if st.sidebar.button("Logout"):
        #     # Clear authentication state
        #     st.session_state.auth = {
        #         "is_authenticated": False,
        #         "user_id": None,
        #         "user_info": {}
        #     }
        #     # Force UI refresh
        #     st.rerun()
    
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

        if result and result.get("success", False):
            logger.info(f"Updated user statistics: reviews={result.get('reviews_completed')}, " +
                    f"score={result.get('score')}")
        else:
            err_msg = result.get('error', 'Unknown error') if result else "No result returned"
            logger.error(f"Failed to update review stats: {err_msg}")
        
        return result
    
    def is_authenticated(self) -> bool:
        """
        Check if user is authenticated.
        
        Returns:
            bool: True if user is authenticated, False otherwise
        """
        return st.session_state.auth.get("is_authenticated", False)
    
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
            return st.session_state.auth.get("user_info", {}).get("level", "basic")
            
        try:
            # Query the database for the latest user info
            profile = self.auth_manager.get_user_profile(user_id)
            if profile.get("success", False):
                # Update the session state with the latest level
                level = profile.get("level", "basic")
                st.session_state.auth["user_info"]["level"] = level
                return level
            else:
                # Fallback to session state if query fails
                return st.session_state.auth.get("user_info", {}).get("level", "basic")
        except Exception as e:
            logger.error(f"Error getting user level from database: {str(e)}")
            # Fallback to session state
            return st.session_state.auth.get("user_info", {}).get("level", "basic")