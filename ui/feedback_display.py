"""
Feedback Display UI module for Java Peer Review Training System.

This module provides the FeedbackDisplayUI class for displaying feedback on student reviews.
"""

import streamlit as st
import logging
import pandas as pd
import matplotlib.pyplot as plt
from typing import List, Dict, Any, Optional, Tuple, Callable
from utils.language_utils import t, get_current_language

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
                review_analysis = latest_review.get("review_analysis", {})
                iteration = latest_review.get("iteration_number", 0)
                
                st.markdown(f"#### {t('your_final_review').format(iteration=iteration)}")
                
                # Format the review text with syntax highlighting
                st.markdown("```text\n" + latest_review.get("student_review", "") + "\n```")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric(
                        t("issues_found"), 
                        f"{review_analysis.get('identified_count', 0)} {t('of')} {review_analysis.get('total_problems', 0)}",
                        delta=None
                    )
                with col2:
                    st.metric(
                        t("accuracy"), 
                        f"{review_analysis.get('accuracy_percentage', 0):.1f}%",
                        delta=None
                    )
                with col3:
                    false_positives = len(review_analysis.get('false_positives', []))
                    st.metric(
                        t("false_positives"), 
                        false_positives,
                        delta=None
                    )
            
            # Show earlier reviews in an expander if there are multiple
            if len(review_history) > 1:
                with st.expander(t("review_history"), expanded=False):
                    tabs = st.tabs([f"{t('attempt')} {rev.get('iteration_number', i+1)}" for i, rev in enumerate(review_history)])
                    
                    for i, (tab, review) in enumerate(zip(tabs, review_history)):
                        with tab:
                            review_analysis = review.get("review_analysis", {})
                            st.markdown("```text\n" + review.get("student_review", "") + "\n```")
                            
                            st.write(f"**{t('found')}:** {review_analysis.get('identified_count', 0)} {t('of')} "
                                    f"{review_analysis.get('total_problems', 0)} {t('issues')} "
                                    f"({review_analysis.get('accuracy_percentage', 0):.1f}% {t('accuracy')})")
        
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
        original_error_count = review_analysis.get("original_error_count", 0)
        if original_error_count <= 0:
            # Fallback to total_problems if original_error_count is not available
            original_error_count = review_analysis.get("total_problems", 0)
        
        # If still zero, make a final check with the found and missed counts
        if original_error_count <= 0:
            identified_count = review_analysis.get("identified_count", 0)
            missed_count = len(review_analysis.get("missed_problems", []))
            original_error_count = identified_count + missed_count
        
        # Now calculate the accuracy using the original count for consistency
        identified_count = review_analysis.get("identified_count", 0)
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
            false_positives = len(review_analysis.get("false_positives", []))
            st.metric(
                t("false_positives"), 
                f"{false_positives}",
                delta=None
            )
                
        # Create a progress chart if multiple iterations
        if len(review_history) > 1:
            # Extract data for chart
            iterations = []
            identified_counts = []
            accuracy_percentages = []
            
            for review in review_history:
                analysis = review.get("review_analysis", {})
                iterations.append(review.get("iteration_number", 0))
                
                # Use consistent error count for all iterations
                review_identified = analysis.get("identified_count", 0)
                identified_counts.append(review_identified)
                
                # Calculate accuracy consistently
                review_accuracy = (review_identified / original_error_count * 100) if original_error_count > 0 else 0
                accuracy_percentages.append(review_accuracy)
            
            # Configure matplotlib for Chinese text support
            import matplotlib.font_manager as fm
            import matplotlib as mpl
            import platform
            import locale
            import os
            
            # First try to set font based on operating system
            system = platform.system()
            default_font = None
            
            try:
                # Different font defaults based on OS
                if system == 'Windows':
                    chinese_fonts = ['Microsoft YaHei', 'SimHei', 'SimSun', 'Arial Unicode MS']
                elif system == 'Darwin':  # macOS
                    chinese_fonts = ['PingFang TC', 'STHeiti', 'Heiti TC', 'Apple LiGothic', 'Hiragino Sans GB']
                else:  # Linux and others
                    chinese_fonts = ['WenQuanYi Zen Hei', 'Droid Sans Fallback', 'Noto Sans CJK TC', 'Noto Sans TC']
                
                # Try to find a suitable font that exists
                for font_name in chinese_fonts:
                    font_path = None
                    for f in fm.findSystemFonts():
                        if font_name.lower() in os.path.basename(f).lower():
                            font_path = f
                            break
                    
                    if font_path:
                        # Add font to matplotlib's font manager
                        fm.fontManager.addfont(font_path)
                        default_font = font_name
                        break
                
                # Configure matplotlib to use the font
                if default_font:
                    mpl.rcParams['font.family'] = ['sans-serif']
                    mpl.rcParams['font.sans-serif'] = [default_font, 'DejaVu Sans', 'Arial Unicode MS']
                else:
                    # Fallback to system locale-based detection
                    current_locale = locale.getlocale()[0]
                    if current_locale and ('zh' in current_locale.lower() or 'tw' in current_locale.lower()):
                        # For Chinese locales, use a more aggressive approach with common Chinese fonts
                        mpl.rcParams['font.family'] = ['sans-serif']
                        mpl.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans', 'Bitstream Vera Sans', 'Arial Unicode MS'] 
                    
                # Prevent minus sign from being rendered as a Unicode character
                mpl.rcParams['axes.unicode_minus'] = False
            
            except Exception as e:
                # Log the error but continue without crashing
                logger.warning(f"Error configuring matplotlib fonts: {str(e)}")
                # Safe fallback for matplotlib configuration
                mpl.rcParams['font.family'] = ['sans-serif']
            
            # Create a DataFrame with renamed columns - use English labels for internal processing
            # This ensures compatibility with matplotlib
            chart_data = pd.DataFrame({
                "Attempt": iterations,
                "Issues Found": identified_counts,
                "Accuracy (%)": accuracy_percentages
            })
            
            # Display the chart with two y-axes
            st.subheader(t("progress_across_iterations"))
            
            # Create plot with English labels initially
            fig, ax1 = plt.subplots(figsize=(10, 4))
            
            color = 'tab:blue'
            ax1.set_xlabel('Iteration')  # Use English initially
            ax1.set_ylabel('Issues Found', color=color)  # Use English initially
            ax1.plot(chart_data["Attempt"], chart_data["Issues Found"], marker='o', color=color)
            ax1.tick_params(axis='y', labelcolor=color)
            ax1.grid(True, linestyle='--', alpha=0.7)
            
            ax2 = ax1.twinx()  # Create a second y-axis
            color = 'tab:red'
            ax2.set_ylabel('Accuracy (%)', color=color)  # Use English initially
            ax2.plot(chart_data["Attempt"], chart_data["Accuracy (%)"], marker='s', color=color)
            ax2.tick_params(axis='y', labelcolor=color)
            
            # Now update the labels with translated text
            ax1.set_xlabel(t('iteration'))
            ax1.set_ylabel(t('issues_found'), color='tab:blue')
            ax2.set_ylabel(f"{t('accuracy')} (%)", color='tab:red')
            
            # Add a title with translated text
            plt.title(t("progress_across_iterations"))
            
            fig.tight_layout()
            st.pyplot(fig)
    
    def _render_identified_issues(self, review_analysis: Dict[str, Any]):
        """Render identified issues section with language support"""
        # Use translated field name for display but English field name for access
        identified_problems = review_analysis.get("identified_problems", [])
        
        if not identified_problems:
            st.info(t("no_identified_issues"))
            return
                
        st.subheader(f"{t('correctly_identified_issues')} ({len(identified_problems)})")
        
        for i, issue in enumerate(identified_problems, 1):
            st.markdown(
                f"""
                <div style="border-left: 4px solid #4CAF50; padding: 10px; margin: 10px 0; border-radius: 4px;">
                <strong>✓ {i}. {issue}</strong>
                </div>
                """, 
                unsafe_allow_html=True
        )

    def _render_missed_issues(self, review_analysis: Dict[str, Any]):
        """Render missed issues section with language support"""
        # Use translated field name for display but English field name for access
        missed_problems = review_analysis.get("missed_problems", [])
        
        if not missed_problems:
            st.success(t("all_issues_found"))
            return
                
        st.subheader(f"{t('issues_missed')} ({len(missed_problems)})")
        
        for i, issue in enumerate(missed_problems, 1):
            st.markdown(
                f"""
                <div style="border-left: 4px solid #f44336; padding: 10px; margin: 10px 0; border-radius: 4px;">
                <strong>✗ {i}. {issue}</strong>
                </div>
                """, 
                unsafe_allow_html=True
            )