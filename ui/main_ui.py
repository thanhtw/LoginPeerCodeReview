"""
Main UI components for Java Peer Review Training System.

This module provides the primary UI functions for the Streamlit interface,
including tab rendering, LLM logs, and sidebar components.
"""

import streamlit as st
import os
import logging
import re
import io
import zipfile
import base64
import time
from typing import Dict, List, Any, Optional, Callable

from utils.llm_logger import LLMInteractionLogger
from llm_manager import LLMManager
from state_schema import WorkflowState
from utils.language_utils import t, get_current_language, get_field_value, get_state_attribute  # Add get_field_value and get_state_attribute

# Configure logging
logging.getLogger('streamlit').setLevel(logging.ERROR)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def init_session_state():
    """Initialize session state with default values."""
    # Initialize workflow state if not present
    if 'workflow_state' not in st.session_state:
        st.session_state.workflow_state = WorkflowState()
    
    # Initialize active tab if not present
    if 'active_tab' not in st.session_state:
        st.session_state.active_tab = 0
    
    # Initialize error state if not present
    if 'error' not in st.session_state:
        st.session_state.error = None
    
    # Initialize workflow steps if not present
    if 'workflow_steps' not in st.session_state:
        st.session_state.workflow_steps = []
        
    # Initialize sidebar state if not present
    if 'sidebar_tab' not in st.session_state:
        st.session_state.sidebar_tab = "Status"
    
    if 'user_level' not in st.session_state:
        st.session_state.user_level = None
        
    # Initialize current step if needed - directly in workflow_state
    if hasattr(st.session_state, 'workflow_state') and not hasattr(st.session_state.workflow_state, 'current_step'):
        st.session_state.workflow_state.current_step = "generate"
        
    # Initialize evaluation attempts if needed - directly in workflow_state
    if hasattr(st.session_state, 'workflow_state') and not hasattr(st.session_state.workflow_state, 'evaluation_attempts'):
        st.session_state.workflow_state.evaluation_attempts = 0
        
    # Initialize max evaluation attempts if needed - directly in workflow_state
    if hasattr(st.session_state, 'workflow_state') and not hasattr(st.session_state.workflow_state, 'max_evaluation_attempts'):
        st.session_state.workflow_state.max_evaluation_attempts = 3
    
    # Initialize LLM logger if not present
    if 'llm_logger' not in st.session_state:
        st.session_state.llm_logger = LLMInteractionLogger()
        
    # Ensure code_snippet is never accessed directly, but through workflow_state
    if 'code_snippet' in st.session_state:
        # Transfer any existing code_snippet to workflow_state and remove direct reference
        if 'workflow_state' in st.session_state and not hasattr(st.session_state.workflow_state, 'code_snippet'):
            st.session_state.workflow_state.code_snippet = st.session_state.code_snippet
        # Remove the direct reference to avoid confusion
        del st.session_state.code_snippet

def render_llm_logs_tab():
    """Render the LLM logs tab with detailed log information and file browsing capabilities with full translation support and language filtering."""
    st.subheader(t("llm_logs_title") or "LLM Interaction Logs")
    
    if hasattr(st, 'session_state') and 'llm_logger' in st.session_state:
        llm_logger = st.session_state.llm_logger
        
        # Get current language
        current_language = get_current_language()
        
        # Add refresh button at the top
        col1, col2, col3 = st.columns([4, 1, 1])
        with col2:
            if st.button(t("refresh_logs") or "Refresh Logs", key="refresh_logs_btn"):
                st.rerun()
        
        with col1:
            # Make the log count configurable
            log_count = st.slider(t("logs_to_display") or "Number of logs to display", min_value=5, max_value=30, value=10, step=5)
        
        with col3:
            # Add an option to filter logs by language
            language_filter = st.checkbox(t("filter_by_language") or "Filter by language", value=True)
        
        # Get logs (will now include both in-memory and disk logs)
        logs = llm_logger.get_recent_logs(log_count * 3)  # Get more logs to allow for filtering
        
        if logs:
            # Add filter for log types - use get_field_value for log type access
            log_types = sorted(list(set(get_field_value(log, "type", "unknown") for log in logs)))
            log_type_filter = st.multiselect(t("filter_by_type") or "Filter by log type:", log_types, default=log_types)
            
            # Date filter - use get_field_value for timestamp access
            timestamps = [get_field_value(log, "timestamp", "") for log in logs if "timestamp" in log or "時間戳記" in log]
            if timestamps:
                # Extract dates from timestamps
                dates = sorted(set(ts.split("T")[0] for ts in timestamps if "T" in ts))
                if dates:
                    selected_dates = st.multiselect(t("filter_by_date") or "Filter by date:", dates, default=dates)
                    # Apply date filter - use get_field_value for timestamp access
                    logs = [log for log in logs if get_field_value(log, "timestamp", "").split("T")[0] in selected_dates]
            
            # Filter logs by type - use get_field_value for type access
            filtered_logs = [log for log in logs if get_field_value(log, "type", "unknown") in log_type_filter]
            
            # Filter logs by language if option is selected
            if language_filter:
                # Helper function to detect language in prompt text
                def is_language_match(text, lang_code):
                    if not text:
                        return True  # Include logs with empty text
                    
                    if lang_code == "en":
                        # Check for English instructions
                        return "Please respond in English" in text
                    elif lang_code == "zh-tw":
                        # Check for Traditional Chinese instructions
                        return "請用繁體中文回答" in text
                    return True  # Default to include
                
                language_filtered_logs = []
                for log in filtered_logs:
                    # Use get_field_value for prompt access
                    prompt = get_field_value(log, "prompt", "")
                    # Check if the prompt contains language-specific instructions
                    if is_language_match(prompt, current_language):
                        language_filtered_logs.append(log)
                
                # Use the language-filtered logs
                display_logs = language_filtered_logs
                st.info(f"{t('language_filtered_logs') or 'Showing logs in the current language'} ({len(language_filtered_logs)}/{len(filtered_logs)})")
            else:
                display_logs = filtered_logs
            
            if display_logs:
                st.success(t("displaying_logs").format(count=len(display_logs)) if t("displaying_logs") else 
                          f"Displaying {len(display_logs)} recent logs. Newest logs appear first.")
                
                # Display logs with improved UI
                for idx, log in enumerate(display_logs):
                    # Format timestamp for display - use get_field_value for timestamp access
                    timestamp = get_field_value(log, "timestamp", t("unknown_time") or "Unknown time")
                    if "T" in timestamp:
                        date, time = timestamp.split("T")
                        time = time.split(".")[0] if "." in time else time  # Remove milliseconds
                        display_time = f"{date} {time}"
                    else:
                        display_time = timestamp
                    
                    # Create expander title with log type and timestamp - use get_field_value for type access
                    log_type = get_field_value(log, "type", t("unknown_type") or "Unknown type").replace("_", " ").title()
                    expander_title = f"{log_type} - {display_time}"
                    
                    with st.expander(expander_title):
                        # Create tabs for different parts of the log
                        log_tabs = st.tabs([
                            t("prompt_tab") or "Prompt", 
                            t("response_tab") or "Response", 
                            t("metadata_tab") or "Metadata"
                        ])
                        
                        # Prompt tab - use get_field_value for prompt access
                        with log_tabs[0]:
                            st.text_area(
                                t("prompt_sent") or "Prompt sent to LLM:", 
                                value=get_field_value(log, "prompt", ""), 
                                height=250,
                                key=f"prompt_{idx}_{get_field_value(log, 'timestamp', '')}",
                                disabled=True
                            )
                        
                        # Response tab - use get_field_value for response access
                        with log_tabs[1]:
                            response = get_field_value(log, "response", "")
                            if response:
                                # Check if response contains code blocks and highlight them
                                if "```" in response:
                                    parts = response.split("```")
                                    for i, part in enumerate(parts):
                                        if i % 2 == 0:  # Regular text
                                            if part.strip():
                                                st.markdown(part)
                                        else:  # Code block
                                            language = ""
                                            if part.strip() and "\n" in part:
                                                language_line, code = part.split("\n", 1)
                                                if language_line.strip():
                                                    language = language_line.strip()
                                                    part = code
                                            
                                            # Display code with syntax highlighting if language is specified
                                            if language:
                                                st.code(part, language=language)
                                            else:
                                                st.code(part)
                                else:
                                    # Show as plain text
                                    st.text_area(
                                        t("response_label") or "Response:", 
                                        value=response, 
                                        height=300,
                                        key=f"response_{idx}_{get_field_value(log, 'timestamp', '')}",
                                        disabled=True
                                    )
                            else:
                                st.info(t("no_response") or "No response available")
                        
                        # Metadata tab - use get_field_value for metadata access
                        with log_tabs[2]:
                            metadata = get_field_value(log, "metadata", {})
                            if metadata:
                                st.json(metadata)
                            else:
                                st.info(t("no_metadata") or "No metadata available")
            else:
                st.info(t("no_logs_match") or "No logs match the selected filters.")
        else:
            st.info(t("no_logs_found") or "No logs found. Generate code or submit reviews to create log entries.")
            
            # Add helper information about log location
            st.markdown(t("log_info_markdown") or """
            ### Log Information
            
            Log files are stored in the `llm_logs` directory, with subdirectories for each interaction type:
            
            - code_generation
            - code_regeneration
            - code_evaluation
            - review_analysis
            - summary_generation
            
            Each log is stored as both a `.json` file (for programmatic use) and a `.txt` file (for easier reading).
            """)
    else:
        st.info(t("llm_logger_not_initialized") or "LLM logger not initialized.")
    
    # Add clear logs button with confirmation
    st.markdown("---")
    if st.button(t("clear_logs") or "Clear Logs"):
        st.warning(t("clear_logs_warning") or "This will remove in-memory logs. Log files on disk will be preserved.")
        confirm_key = "confirm_clear_logs"
        if confirm_key not in st.session_state:
            st.session_state[confirm_key] = False
        
        if st.session_state[confirm_key] or st.button(t("confirm_clear_logs") or "Confirm Clear Logs", key="confirm_clear_btn"):
            if hasattr(st, 'session_state') and 'llm_logger' in st.session_state:
                st.session_state.llm_logger.clear_logs()
                st.session_state[confirm_key] = False
                st.success(t("logs_cleared") or "Logs cleared.")
                st.rerun()
            else:
                st.error(t("llm_logger_not_initialized") or "LLM logger not initialized.")

def render_sidebar(llm_manager, workflow):
    """
    Render the sidebar with application info and model status.
    
    Args:
        llm_manager: LLMManager instance
        workflow: JavaCodeReviewGraph workflow
    """
    with st.sidebar:
        # LLM Provider info
        st.subheader(f"LLM {t('provider')}")
        provider = llm_manager.provider.capitalize()
        
        if provider == "Ollama":
            connection_status, message = llm_manager.check_ollama_connection()
            status = f"✅ {t('connected')}" if connection_status else "❌ Disconnected"
            st.markdown(f"**{t('provider')}:** {provider}  \n**{t('status')}:** {status}")
            
            if not connection_status:
                st.error(f"Error: {message}")
                st.markdown("""
                Make sure Ollama is running:
                ```bash
                ollama serve
                ```
                """)
        elif provider == "Groq":
            connection_status, message = llm_manager.check_groq_connection()
            status = f"✅ {t('connected')}" if connection_status else "❌ Disconnected"
            st.markdown(f"**{t('provider')}:** {provider}  \n**{t('status')}:** {status}")
            
            if not connection_status:
                st.error(f"Error: {message}")                
        
        # Add separator
        # st.markdown("---")
        
        # # # Reset button
        # # if st.button("Reset Application", use_container_width=True):
        # #     # Reset the session state
        # #     for key in list(st.session_state.keys()):
        # #         # Keep provider selection and error categories
        # #         if key not in ["provider", "selected_error_categories"]:
        # #             del st.session_state[key]
            
        #     # Reinitialize session state
        #     init_session_state()
            
        #     # Set active tab to generate
        #     st.session_state.active_tab = 0
            
        #     # Rerun app
        #     st.rerun()

def create_enhanced_tabs(labels: List[str]):
    """
    Create enhanced UI tabs with tab switching capability.
    
    Args:
        labels: List of tab labels
        
    Returns:
        List of tab objects
    """
    # Create tabs with enhanced styling
    tabs = st.tabs(labels)
    
    # Handle tab switching based on session state
    current_tab = st.session_state.active_tab
    
    # Check if we need to block access to feedback tab
    if hasattr(st.session_state, 'workflow_state'):
        state = st.session_state.workflow_state
        # Determine if review is completed
        review_completed = False
        
        # ENHANCED: Check if max iterations reached or review is sufficient or all errors identified
        if hasattr(state, 'current_iteration') and hasattr(state, 'max_iterations'):
            # Use get_state_attribute for language-aware state access
            current_iteration = get_state_attribute(state, 'current_iteration', 1)
            max_iterations = get_state_attribute(state, 'max_iterations', 3)
            
            if current_iteration > max_iterations:
                review_completed = True
                logger.info("Review completed: max iterations reached")
            elif get_state_attribute(state, 'review_sufficient', False):
                review_completed = True
                logger.info("Review completed: sufficient review")
            
            # ENHANCED: Check for all errors identified based on the latest review analysis
            elif hasattr(state, 'review_history') and state.review_history:
                latest_review = state.review_history[-1]
                if hasattr(latest_review, 'analysis'):
                    analysis = latest_review.analysis
                    # Use get_field_value for dictionary access
                    identified_count = get_field_value(analysis, "identified_count", 0)
                    total_problems = get_field_value(analysis, "total_problems", 0)
                    if identified_count == total_problems and total_problems > 0:
                        review_completed = True
                        # Ensure state is updated for consistency
                        state.review_sufficient = True
                        logger.info(f"Review completed: all {total_problems} issues identified")
        
        # Block access to feedback tab (index 2) if review not completed
        if current_tab == 2 and not review_completed:
            st.warning(t("complete_review_first"))
            # Reset to review tab
            st.session_state.active_tab = 1
            current_tab = 1
    
    # Force-select the active tab
    if current_tab != 0:
        # This doesn't actually change the UI, but it helps with logic elsewhere
        st.session_state.active_tab = current_tab
    
    return tabs