"""
Feedback Tab UI module for Java Peer Review Training System.

This module provides the functions for rendering the feedback and analysis tab.
"""

import streamlit as st
import logging
from typing import Dict, List, Any, Optional, Callable
from utils.code_utils import generate_comparison_report


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def render_feedback_tab(workflow, feedback_display_ui, auth_ui=None):
    """
    Render the feedback and analysis tab with enhanced visualization 
    and user statistics updating.
    
    Args:
        workflow: The JavaCodeReviewGraph workflow instance
        feedback_display_ui: FeedbackDisplayUI instance for rendering feedback
        auth_ui: Optional AuthUI instance for updating user statistics
    """
    state = st.session_state.workflow_state

    # Check if review process is completed
    review_completed = False
    if hasattr(state, 'current_iteration') and hasattr(state, 'max_iterations'):
        if state.current_iteration > state.max_iterations:
            review_completed = True
        elif hasattr(state, 'review_sufficient') and state.review_sufficient:
            review_completed = True

    # Block access if review not completed
    if not review_completed:
        st.warning("Please complete all review attempts before accessing feedback.")
        st.info(f"Current progress: {state.current_iteration-1}/{state.max_iterations} attempts completed")
        
        # Add button to go back to review tab
        if st.button("Go to Review Tab"):
            st.session_state.active_tab = 1
            st.rerun()
        return
    
    # Get the latest review analysis and history
    latest_review = None
    review_history = []
    
    # Make sure we have review history
    if state.review_history:
        latest_review = state.review_history[-1]
        
        # Convert review history to the format expected by FeedbackDisplayUI
        for review in state.review_history:
            review_history.append({
                "iteration_number": review.iteration_number,
                "student_review": review.student_review,
                "review_analysis": review.analysis
            })
    
    # If we have review history but no comparison report, generate one
    if latest_review and latest_review.analysis and not state.comparison_report:
        try:
            # Get the known problems from the evaluation result instead of code_snippet.known_problems
            if state.evaluation_result and 'found_errors' in state.evaluation_result:
                found_errors = state.evaluation_result.get('found_errors', [])
                
                # Generate a comparison report if it doesn't exist
                state.comparison_report = generate_comparison_report(
                    found_errors,
                    latest_review.analysis
                )
                logger.info("Generated comparison report for feedback tab")
        except Exception as e:
            logger.error(f"Error generating comparison report: {str(e)}")
            if not state.comparison_report:
                state.comparison_report = (
                    "# Review Feedback\n\n"
                    "There was an error generating a detailed comparison report. "
                    "Please check your review history for details."
                )
    
    # Check if we have reviews but no feedback to display
    if review_history and not state.comparison_report and not state.review_summary:
        st.warning("Review data is available but no feedback generated. Generating feedback now...")
        
        # Extract latest analysis for display
        latest_analysis = latest_review.analysis if latest_review else None
        
        # Generate a basic summary if nothing else is available
        if latest_analysis:
            identified_count = latest_analysis.get("identified_count", 0)
            total_problems = latest_analysis.get("total_problems", 0)
            identified_percentage = latest_analysis.get("identified_percentage", 0)
            
            state.review_summary = (
                f"# Review Summary\n\n"
                f"You found {identified_count} out of {total_problems} issues "
                f"({identified_percentage:.1f}% accuracy).\n\n"
                f"Check the detailed analysis below for more information."
            )
            
            logger.info("Generated basic review summary for feedback tab")
    
    # If no feedback generated yet but we have reviews, display a message
    if not state.comparison_report and not state.review_summary and not review_history:
        st.info("Please submit your review in the 'Submit Review' tab first.")
        return
    
    # Get the latest review analysis
    latest_analysis = latest_review.analysis if latest_review else None
    
    # Update user statistics if AuthUI is provided
    if auth_ui and latest_analysis and "stats_updated" not in st.session_state:
        try:
            # Extract accuracy from the latest review
            accuracy = latest_analysis.get("identified_percentage", 0)
            
            # Update user stats
            auth_ui.update_review_stats(accuracy)
            
            # Mark as updated to avoid multiple updates
            st.session_state.stats_updated = True
            
            logger.info(f"Updated user statistics with accuracy: {accuracy:.1f}%")
        except Exception as e:
            logger.error(f"Error updating user statistics: {str(e)}")
    
    # Display feedback results
    feedback_display_ui.render_results(
        comparison_report=state.comparison_report,
        review_summary=state.review_summary,
        review_analysis=latest_analysis,
        review_history=review_history        
    )
    
    # Add a button to start a new session
    st.markdown("---")
    new_session_col1, new_session_col2 = st.columns([3, 1])
    with new_session_col1:
        st.markdown("### Ready for another review?")
        st.markdown("Start a new code review session to practice with different errors.")
    with new_session_col2:
        if st.button("Start New Session", use_container_width=True):
            # Clear the stats_updated flag
            if "stats_updated" in st.session_state:
                del st.session_state.stats_updated
                
            # Set the full reset flag
            st.session_state.full_reset = True
            
            # Return to the generate tab
            st.session_state.active_tab = 0
            
            # Force UI refresh
            st.rerun()