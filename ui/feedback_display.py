"""
Feedback Display UI module for Java Peer Review Training System.

This module provides the FeedbackDisplayUI class for displaying feedback on student reviews.
"""

import streamlit as st
import logging
import pandas as pd
import matplotlib.pyplot as plt
from typing import List, Dict, Any, Optional, Tuple, Callable
from utils.language_utils import t, get_current_language, get_field_value, get_state_attribute  # Add get_state_attribute

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class FeedbackDisplayUI:
    """
    UI Component for displaying feedback on student reviews.
    
    This class handles displaying analysis results, review history,
    and feedback on student reviews.
    """
    
    def render_results(self, 
                      comparison_report: str = None,
                      review_summary: str = None,
                      review_analysis: Dict[str, Any] = None,
                      review_history: List[Dict[str, Any]] = None,
                      on_reset_callback: Callable[[], None] = None) -> None:
        """
        Render the analysis results and feedback with improved review visibility.
        
        Args:
            comparison_report: Comparison report text
            review_summary: Review summary text
            review_analysis: Analysis of student review
            review_history: History of review iterations
            on_reset_callback: Callback function when reset button is clicked
        """
        if not comparison_report and not review_summary and not review_analysis:
            st.info(t("no_analysis_results"))
            return
        
        # First show performance summary metrics at the top
        if review_history and len(review_history) > 0 and review_analysis:
            self._render_performance_summary(review_analysis, review_history)
        
        # Display the comparison report
        if comparison_report:
            st.subheader(t("educational_feedback"))
            st.markdown(
                f'<div class="comparison-report">{comparison_report}</div>',
                unsafe_allow_html=True
            )
        
        # Always show review history for better visibility
        if review_history and len(review_history) > 0:
            st.subheader(t("your_review"))
            
            # First show the most recent review prominently
            if review_history:
                latest_review = review_history[-1]
                review_analysis = get_field_value(latest_review, "review_analysis", {})
                iteration = get_field_value(latest_review, "iteration_number", 0)
                
                st.markdown(f"#### {t('your_final_review').format(iteration=iteration)}")
                
                # Format the review text with syntax highlighting
                st.markdown("```text\n" + get_field_value(latest_review, "student_review", "") + "\n```")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    # Use get_field_value for language-aware access
                    identified_count = get_field_value(review_analysis, "identified_count", 0)
                    total_problems = get_field_value(review_analysis, "total_problems", 0)
                    st.metric(
                        t("issues_found"), 
                        f"{identified_count} {t('of')} {total_problems}",
                        delta=None
                    )
                with col2:
                    # Use get_field_value for language-aware access
                    accuracy = get_field_value(review_analysis, "accuracy_percentage", 0)
                    st.metric(
                        t("accuracy"), 
                        f"{accuracy:.1f}%",
                        delta=None
                    )
                with col3:
                    # Use get_field_value for language-aware access
                    false_positives = len(get_field_value(review_analysis, "false_positives", []))
                    st.metric(
                        t("false_positives"), 
                        false_positives,
                        delta=None
                    )
            
            # Show earlier reviews in an expander if there are multiple
            if len(review_history) > 1:
                with st.expander(t("review_history"), expanded=False):
                    tabs = st.tabs([f"{t('attempt')} {get_field_value(rev, 'iteration_number', i+1)}" for i, rev in enumerate(review_history)])
                    
                    for i, (tab, review) in enumerate(zip(tabs, review_history)):
                        with tab:
                            review_analysis = get_field_value(review, "review_analysis", {})
                            st.markdown("```text\n" + get_field_value(review, "student_review", "") + "\n```")
                            
                            # Use get_field_value for language-aware access
                            identified_count = get_field_value(review_analysis, "identified_count", 0)
                            total_problems = get_field_value(review_analysis, "total_problems", 0)
                            accuracy = get_field_value(review_analysis, "accuracy_percentage", 0)
                            
                            st.write(f"**{t('found')}:** {identified_count} {t('of')} "
                                    f"{total_problems} {t('issues')} "
                                    f"({accuracy:.1f}% {t('accuracy')})")
        
        # Display analysis details in an expander
        if review_summary or review_analysis:
            with st.expander(t("detailed_analysis"), expanded=True):
                tabs = st.tabs([t("identified_issues"), t("missed_issues")])
                
                with tabs[0]:  # Identified Issues
                    self._render_identified_issues(review_analysis)
                
                with tabs[1]:  # Missed Issues
                    self._render_missed_issues(review_analysis)

        # Start over button
        st.markdown("---")
            
    def _render_performance_summary(self, review_analysis: Dict[str, Any], review_history: List[Dict[str, Any]]):
        """Render performance summary metrics and charts with proper Chinese font support"""
        st.subheader(t("review_performance_summary"))
        
        # Create performance metrics using the original error count if available
        col1, col2, col3 = st.columns(3)
        
        # Get the correct total_problems count from original_error_count if available
        original_error_count = get_field_value(review_analysis, "original_error_count", 0)
        if original_error_count <= 0:
            # Fallback to total_problems if original_error_count is not available
            original_error_count = get_field_value(review_analysis, "total_problems", 0)
        
        # If still zero, make a final check with the found and missed counts
        if original_error_count <= 0:
            identified_count = get_field_value(review_analysis, "identified_count", 0)
            missed_count = len(get_field_value(review_analysis, "missed_problems", []))
            original_error_count = identified_count + missed_count
        
        # Now calculate the accuracy using the original count for consistency
        identified_count = get_field_value(review_analysis, "identified_count", 0)
        accuracy = (identified_count / original_error_count * 100) if original_error_count > 0 else 0
        
        with col1:
            st.metric(
                t("overall_accuracy"), 
                f"{accuracy:.1f}%",
                delta=None
            )
                
        with col2:
            st.metric(
                t("issues_identified"), 
                f"{identified_count}/{original_error_count}",
                delta=None
            )
                
        with col3:
            false_positives = len(get_field_value(review_analysis, "false_positives", []))
            st.metric(
                t("false_positives"), 
                f"{false_positives}",
                delta=None
            )
                
        # Could add other visualization code here if needed
    
    def _render_identified_issues(self, review_analysis: Dict[str, Any]):
        """Render identified issues section with language support"""
        # Use get_field_value for language-aware access
        identified_problems = get_field_value(review_analysis, "identified_problems", [])
        
        if not identified_problems:
            st.info(t("no_identified_issues"))
            return
                
        st.subheader(f"{t('correctly_identified_issues')} ({len(identified_problems)})")
        
        for i, issue in enumerate(identified_problems, 1):
            issue_text = issue
            if isinstance(issue, dict):
                issue_text = get_field_value(issue, "problem", str(issue))
            
            st.markdown(
                f"""
                <div style="border-left: 4px solid #4CAF50; padding: 10px; margin: 10px 0; border-radius: 4px;">
                <strong>✓ {i}. {issue_text}</strong>
                </div>
                """, 
                unsafe_allow_html=True
            )

    def _render_missed_issues(self, review_analysis: Dict[str, Any]):
        """Render missed issues section with language support"""
        # Use get_field_value for language-aware access
        missed_problems = get_field_value(review_analysis, "missed_problems", [])
        
        if not missed_problems:
            st.success(t("all_issues_found"))
            return
                
        st.subheader(f"{t('issues_missed')} ({len(missed_problems)})")
        
        for i, issue in enumerate(missed_problems, 1):
            issue_text = issue
            if isinstance(issue, dict):
                issue_text = get_field_value(issue, "problem", str(issue))
                
            st.markdown(
                f"""
                <div style="border-left: 4px solid #f44336; padding: 10px; margin: 10px 0; border-radius: 4px;">
                <strong>✗ {i}. {issue_text}</strong>
                </div>
                """, 
                unsafe_allow_html=True
            )