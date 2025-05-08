"""
Error Selector UI module for Java Peer Review Training System.

This module provides the ErrorSelectorUI class for selecting Java error categories
to include in the generated code problems.
"""

import streamlit as st
import logging
import random
from typing import List, Dict, Any, Optional, Tuple, Callable

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ErrorSelectorUI:
    """
    UI Component for selecting Java error categories.
    
    This class handles displaying and selecting Java error categories
    from java errors.
    """
    
    def __init__(self):
        """Initialize the ErrorSelectorUI component with empty selections."""
        # Track selected categories - initialize with empty collections if not in session state
        if "selected_error_categories" not in st.session_state:
            st.session_state.selected_error_categories = {
               "java_errors": []
            }
        elif not isinstance(st.session_state.selected_error_categories, dict):
            # Fix if it's not a proper dictionary
            st.session_state.selected_error_categories = {
                "java_errors": []
            }
        elif "java_errors" not in st.session_state.selected_error_categories:
            # Make sure java_errors key exists
            st.session_state.selected_error_categories["java_errors"] = []
        
        # Track error selection mode
        if "error_selection_mode" not in st.session_state:
            st.session_state.error_selection_mode = "advanced"
        
        # Track expanded categories
        if "expanded_categories" not in st.session_state:
            st.session_state.expanded_categories = {}
            
        # Track selected specific errors - initialize as empty list
        if "selected_specific_errors" not in st.session_state:
            st.session_state.selected_specific_errors = []
    
    def render_category_selection(self, all_categories: Dict[str, List[str]]) -> Dict[str, List[str]]:
        """
        Render the error category selection UI for advanced mode with enhanced debugging.
        Each error category from Java_code_review_errors.json is displayed as a checkbox.
        
        Args:
            all_categories: Dictionary with 'java_errors' categories
            
        Returns:
            Dictionary with selected categories
        """
        st.subheader("Select Specific Error Categories")
        
        # Add help text explaining how this mode works
        st.info("""
        **Advanced Mode**: Select specific error categories to include in the generated code. 
        When you select a category, the system will randomly choose errors from that category 
        to include in the generated code.
        """)
        
        java_error_categories = all_categories.get("java_errors", [])
        
        # Ensure the session state structure is correct
        if "selected_error_categories" not in st.session_state:
            st.session_state.selected_error_categories = {"java_errors": []}
        if "java_errors" not in st.session_state.selected_error_categories:
            st.session_state.selected_error_categories["java_errors"] = []
        
        
        # Create a multi-column layout for categories
        cols = st.columns(2)
        
        # Get the current selection state from session
        current_selections = st.session_state.selected_error_categories.get("java_errors", [])
        
        # Split the categories into two columns
        half_length = len(java_error_categories) // 2
        for i, col in enumerate(cols):
            start_idx = i * half_length
            end_idx = start_idx + half_length if i == 0 else len(java_error_categories)
            
            with col:
                for category in java_error_categories[start_idx:end_idx]:
                    # Create a unique key for this category
                    category_key = f"java_{category}"
                    
                    # Check if category is already selected from session state
                    is_selected = category in current_selections
                    
                    # Create the checkbox
                    selected = st.checkbox(
                        category,
                        key=category_key,
                        value=is_selected
                    )
                    
                    # Update selection state based on checkbox
                    if selected:
                        if category not in current_selections:
                            current_selections.append(category)
                    else:
                        if category in current_selections:
                            current_selections.remove(category)
        
        # Update selections in session state
        st.session_state.selected_error_categories["java_errors"] = current_selections
        
        # Selection summary
        st.write("### Selected Categories")
        if not current_selections:
            st.warning("No categories selected. You must select at least one category to generate code.")
        
        if current_selections:
            st.write("Java Error Categories:")
            for category in current_selections:
                st.markdown(f"<div class='error-category'>{category}</div>", unsafe_allow_html=True)
        
        return st.session_state.selected_error_categories
    
    def render_specific_error_selection(self, error_repository) -> List[Dict[str, Any]]:
        """
        Render UI for selecting specific errors to include in generated code.
        Each group in Java_code_review_errors.json is displayed as a tab.
        
        Args:
            error_repository: Repository for accessing Java error data
            
        Returns:
            List of selected specific errors
        """
        st.subheader("Select Specific Errors")
        
        # Get all categories
        all_categories = error_repository.get_all_categories()
        java_error_categories = all_categories.get("java_errors", [])
        
        # Container for selected errors
        if "selected_specific_errors" not in st.session_state:
            st.session_state.selected_specific_errors = []
            
        # Create tabs for each error category
        error_tabs = st.tabs(java_error_categories)
        # For each category tab
        for i, category in enumerate(java_error_categories):
            with error_tabs[i]:
                # Get errors for this category
                errors = error_repository.get_category_errors(category)
                if not errors:
                    st.info(f"No errors found in {category} category.")
                    continue
                    
                # Display each error with a select button
                for error in errors:
                    error_name = error.get("error_name", "Unknown")
                    description = error.get("description", "")
                    
                    # Check if already selected
                    is_selected = any(
                        e["name"] == error_name and e["category"] == category
                        for e in st.session_state.selected_specific_errors
                    )
                    
                    # Add select button
                    col1, col2 = st.columns([5, 1])
                    with col1:
                        st.markdown(f"**{error_name}**")
                        st.markdown(f"*{description}*")
                    with col2:
                        if not is_selected:
                            if st.button("Select", key=f"java_{category}_{error_name}"):
                                st.session_state.selected_specific_errors.append({
                                    "type": "java_error",
                                    "category": category,
                                    "name": error_name,
                                    "description": description,
                                    "implementation_guide": error.get("implementation_guide", "")
                                })
                                st.rerun()
                        else:
                            st.success("Selected")
                    
                    st.markdown("---")
        
        # Show selected errors
        st.subheader("Selected Issues")
        
        if not st.session_state.selected_specific_errors:
            st.info("No specific issue selected. Random errors will be used based on categories.")
        else:
            for idx, error in enumerate(st.session_state.selected_specific_errors):
                col1, col2 = st.columns([5, 1])
                with col1:
                    st.markdown(f"**{error['category']} - {error['name']}**")
                    st.markdown(f"*{error['description']}*")
                with col2:
                    if st.button("Remove", key=f"remove_{idx}"):
                        st.session_state.selected_specific_errors.pop(idx)
                        st.rerun()
        
        return st.session_state.selected_specific_errors
        
    def render_mode_selector(self) -> str:
        """
        Render the mode selector UI with improved mode switching behavior.
        
        Returns:
            Selected mode ("advanced" or "specific")
        """
        st.markdown("#### Error Selection Mode")
        
        # Create a more descriptive selection with radio buttons
        mode_options = [
            "Advanced: Select by error categories",
            "Specific: Choose exact errors to include"
        ]
        
        # Convert session state to index
        current_mode = st.session_state.error_selection_mode
        current_index = 0
        if current_mode == "specific":
            current_index = 1
        
        # Error selection mode radio buttons with CSS class for styling
        st.markdown('<div class="error-mode-radio">', unsafe_allow_html=True)
        selected_option = st.radio(
            "How would you like to select errors?",
            options=mode_options,
            index=current_index,
            key="error_mode_radio",
            label_visibility="collapsed",
            horizontal=True
        )
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Update error selection mode based on selection
        new_mode = st.session_state.error_selection_mode
        if "Advanced" in selected_option and st.session_state.error_selection_mode != "advanced":
            new_mode = "advanced"
        elif "Specific" in selected_option and st.session_state.error_selection_mode != "specific":
            new_mode = "specific"
        
        # Only update if the mode has changed
        if new_mode != st.session_state.error_selection_mode:
            # Store previous mode for reference
            previous_mode = st.session_state.error_selection_mode
            
            # Update the mode
            st.session_state.error_selection_mode = new_mode
                
            # Initialize or reset appropriate selections when mode changes
            if new_mode == "specific":
                # Make sure selected_specific_errors exists
                if "selected_specific_errors" not in st.session_state:
                    st.session_state.selected_specific_errors = []
        
              
        # Show help text for the selected mode
        if st.session_state.error_selection_mode == "advanced":
            st.info("Advanced mode: Select specific error categories like LogicalErrors or NamingConventionChecks. The system will randomly select errors from these categories.")
        else:
            st.info("Specific mode: Choose exactly which errors will appear in the generated code.")
        
        return st.session_state.error_selection_mode
    
    def get_code_params_for_level(self, user_level: str = None) -> Dict[str, str]:
        """
        Get code generation parameters automatically based on user level
        without displaying UI controls.
        """
        # Normalize the user level to lowercase and default to medium if None
        normalized_level = user_level.lower() if user_level else "medium"
        
        # Set appropriate difficulty based on normalized user level
        difficulty_mapping = {
            "basic": "easy",
            "medium": "medium", 
            "senior": "hard"
        }
        difficulty_level = difficulty_mapping.get(normalized_level, "medium")
        
        # Set code length based on difficulty
        length_mapping = {
            "easy": "short",
            "medium": "medium",
            "hard": "long"
        }
        code_length = length_mapping.get(difficulty_level, "medium")
        
        # Update session state for consistency
        st.session_state.difficulty_level = difficulty_level.capitalize()
        st.session_state.code_length = code_length.capitalize()
        
        return {
            "difficulty_level": difficulty_level,
            "code_length": code_length
        }
    