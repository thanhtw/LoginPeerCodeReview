"""
Review Tab UI module for Java Peer Review Training System.

This module provides the functions for rendering the review submission tab
and handling student reviews.
"""

import streamlit as st
import logging
import time
from typing import Dict, List, Any, Optional, Callable
import datetime
from utils.language_utils import t, get_current_language, get_field_value, get_state_attribute

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# In ui/review_tab.py
def process_student_review(workflow, student_review: str):
    """
    Process a student review with progress indicator and improved error handling.
    Show immediate feedback to the student.
    
    Args:
        workflow: The JavaCodeReviewGraph workflow instance
        student_review: The student's review text
        
    Returns:
        bool: True if successful, False otherwise
    """
    # Show progress during analysis
    with st.status(t("processing_review"), expanded=True) as status:
        try:
            # Get current state
            if not hasattr(st.session_state, 'workflow_state'):
                status.update(label=f"{t('error')}: {t('workflow_not_initialized')}", state="error")
                st.session_state.error = t("please_generate_problem_first")
                return False
                
            state = st.session_state.workflow_state
            
            # Check if code snippet exists using get_state_attribute
            if not get_state_attribute(state, 'code_snippet', None):
                status.update(label=f"{t('error')}: {t('no_code_snippet_available')}", state="error")
                st.session_state.error = t("please_generate_problem_first")
                return False
            
            # Check if student review is empty
            if not student_review.strip():
                status.update(label=f"{t('error')}: {t('review_cannot_be_empty')}", state="error")
                st.session_state.error = t("please_enter_review")
                return False
            
            # Store the current review in session state for display consistency
            current_iteration = get_state_attribute(state, 'current_iteration', 1)
            st.session_state[f"submitted_review_{current_iteration}"] = student_review
            
            # Update status
            status.update(label=t("analyzing_review"), state="running")
            
            # Log submission attempt
            logger.info(f"Submitting review (iteration {current_iteration}): {student_review[:100]}...")
            
            # Create a placeholder for history display before submission processing
            # This ensures the UI shows the review even during processing
            if 'review_history_placeholder' not in st.session_state:
                st.session_state.review_history_placeholder = []
                
            # Add current review to temporary history for immediate display
            st.session_state.review_history_placeholder.append({
                "iteration_number": current_iteration,
                "student_review": student_review,
                "timestamp": datetime.datetime.now().isoformat()
            })
            
            # Submit the review and update the state
            updated_state = workflow.submit_review(state, student_review)
            
            # Clear the placeholder now that we have real data
            st.session_state.review_history_placeholder = []
            
            # Check for errors
            if get_state_attribute(updated_state, 'error', None):
                status.update(label=f"{t('error')}: {get_state_attribute(updated_state, 'error', '')}", state="error")
                st.session_state.error = get_state_attribute(updated_state, 'error', '')
                logger.error(f"{t('error')} during review analysis: {get_state_attribute(updated_state, 'error', '')}")
                return False
            
            # Update session state
            st.session_state.workflow_state = updated_state
            
            # ENHANCED: Check if all errors were found and transition to feedback tab
            all_errors_found = False
            if hasattr(updated_state, 'review_history') and get_state_attribute(updated_state, 'review_history', []):
                review_history = get_state_attribute(updated_state, 'review_history', [])
                if review_history:
                    latest_review = review_history[-1]
                    if hasattr(latest_review, 'analysis') and latest_review.analysis:
                        analysis = latest_review.analysis
                        identified_count = get_field_value(analysis, "identified_count", 0)
                        total_problems = get_field_value(analysis, "total_problems", 0)
                        
                        # If all errors are found, mark review as sufficient and set active tab
                        if identified_count == total_problems and total_problems > 0:
                            updated_state.review_sufficient = True
                            st.session_state.active_tab = 2  # Switch to feedback tab
                            all_errors_found = True
                            logger.info("All errors found! Automatically switching to feedback tab.")
            
            # Log successful analysis
            logger.info(f"Review analysis complete for iteration {current_iteration}")
            
            # Update status
            if all_errors_found:
                status.update(label=t("all_errors_found"), state="complete")
            else:
                status.update(label=t("analysis_complete"), state="complete")
            
            # Force UI refresh with a slight delay to ensure status message is displayed
            time.sleep(0.5)
            st.rerun()
            
            return True
            
        except Exception as e:
            error_msg = f"{t('error')} processing student review: {str(e)}"
            logger.error(error_msg)
            status.update(label=error_msg, state="error")
            st.session_state.error = error_msg
            return False

def render_review_tab(workflow, code_display_ui):
    """
    Render the review tab UI with proper state access.
    
    Args:
        workflow: JavaCodeReviewGraph workflow
        code_display_ui: CodeDisplayUI instance for displaying code
    """
    st.subheader(f"{t('review_java_code')}")
    
    # Access code from workflow_state instead of directly from session_state
    # This ensures we're using the correct state path
    if not hasattr(st.session_state, 'workflow_state') or not st.session_state.workflow_state:
        st.info(f"{t('no_code_generated')}")
        return
        
    # Check if we have a code snippet in the workflow state using get_state_attribute
    state = st.session_state.workflow_state
    if not get_state_attribute(state, 'code_snippet', None):
        st.info(f"{t('no_code_generated')}")
        return
    
    # Get known problems for instructor view
    known_problems = []
    
    # Extract known problems from evaluation result using get_state_attribute and get_field_value
    evaluation_result = get_state_attribute(state, 'evaluation_result', None)
    if evaluation_result and 'found_errors' in evaluation_result:
        found_errors = get_field_value(evaluation_result, 'found_errors', [])
        if found_errors:
            known_problems = found_errors
    
    # If we couldn't get known problems from evaluation, try to get from selected errors
    if not known_problems and hasattr(state, 'selected_specific_errors'):
        selected_errors = get_state_attribute(state, 'selected_specific_errors', [])
        if selected_errors:
            # Format selected errors to match expected format
            known_problems = [
                f"{error.get('type', '').upper()} - {error.get('name', '')}" 
                for error in selected_errors
            ]
    
    # As a last resort, try to extract from raw_errors in code_snippet
    code_snippet = get_state_attribute(state, 'code_snippet', None)
    if not known_problems and code_snippet and hasattr(code_snippet, 'raw_errors'):
        raw_errors = code_snippet.raw_errors
        if isinstance(raw_errors, dict):
            for error_type, errors in raw_errors.items():
                for error in errors:
                    if isinstance(error, dict):
                        error_type_str = error.get('type', error_type).upper()
                        error_name = error.get('name', error.get('error_name', error.get('check_name', 'Unknown')))
                        known_problems.append(f"{error_type_str} - {error_name}")
    
    # Always pass known_problems, the render_code_display function will handle showing
    # the instructor view based on session state and checkbox status
    code_display_ui.render_code_display(
        get_state_attribute(state, 'code_snippet', None),
        known_problems=known_problems
    )
    
    # Get current review state using get_state_attribute
    current_iteration = get_state_attribute(state, 'current_iteration', 1)
    max_iterations = get_state_attribute(state, 'max_iterations', 3)
    
    # Get the latest review if available
    latest_review = None
    targeted_guidance = None
    review_analysis = None
    
    review_history = get_state_attribute(state, 'review_history', [])
    if review_history and len(review_history) > 0:
        latest_review = review_history[-1]
        targeted_guidance = getattr(latest_review, 'targeted_guidance', None)
        review_analysis = getattr(latest_review, 'analysis', {})

    # ENHANCED: Check if all errors are found more reliably
    all_errors_found = False
    if review_analysis:
        identified_count = get_field_value(review_analysis, "identified_count", 0)
        total_problems = get_field_value(review_analysis, "total_problems", 0)
        if identified_count == total_problems and total_problems > 0:
            all_errors_found = True
            # Ensure state is updated when all errors are found
            state.review_sufficient = True
    
    # Only allow submission if we're under the max iterations
    review_sufficient = get_state_attribute(state, 'review_sufficient', False)
    if current_iteration <= max_iterations and not review_sufficient and not all_errors_found:
        # Get the current student review (empty for first iteration)
        student_review = ""
        if latest_review is not None:
            student_review = latest_review.student_review
        
        # Define submission callback
        def on_submit_review(review_text):
            logger.info(f"Submitting review (iteration {current_iteration})")
            
            # Make sure we access and update the workflow_state directly
            state = st.session_state.workflow_state
            
            # Update state with the new review
            updated_state = workflow.submit_review(state, review_text)
            
            # Update session state with the new state
            st.session_state.workflow_state = updated_state
            
            # Check if all errors found or this was the last iteration
            all_found = False
            review_history = get_state_attribute(updated_state, 'review_history', [])
            if review_history and len(review_history) > 0:
                latest = review_history[-1]
                if hasattr(latest, 'analysis'):
                    analysis = latest.analysis
                    identified = get_field_value(analysis, "identified_count", 0)
                    total = get_field_value(analysis, "total_problems", 0)
                    all_found = (identified == total and total > 0)
            
            # ENHANCED: Check if this was the last iteration or review is sufficient or all errors found
            current_iteration = get_state_attribute(updated_state, 'current_iteration', 1)
            max_iterations = get_state_attribute(updated_state, 'max_iterations', 3)
            review_sufficient = get_state_attribute(updated_state, 'review_sufficient', False)
            
            if (current_iteration > max_iterations or review_sufficient or all_found):
                logger.info(t("review_process_complete"))
                # Switch to feedback tab (index 2) and force rerun
                st.session_state.active_tab = 2
            
            # Force rerun to update UI
            st.rerun()
        
        # Render review input with current state
        code_display_ui.render_review_input(
            student_review=student_review,
            on_submit_callback=on_submit_review,
            iteration_count=current_iteration,
            max_iterations=max_iterations,
            targeted_guidance=targeted_guidance,
            review_analysis=review_analysis
        )
    else:
        # Display appropriate message based on why review is blocked
        review_sufficient = get_state_attribute(state, 'review_sufficient', False)
        if review_sufficient or all_errors_found:
            st.success(f"{t('all_errors_found')}")
            # ENHANCED: If all errors found, ensure we move to the feedback tab
            if st.session_state.active_tab != 2:
                st.session_state.active_tab = 2
                # Add a slight delay to ensure the status message is displayed
                time.sleep(0.5)
                st.rerun()
        else:
            st.warning(t("iterations_completed").format(max_iterations=max_iterations))
        
        if st.button(f"{t('view_feedback')}"):
            st.session_state.active_tab = 2  # 2 is the index of the feedback tab
            st.rerun()