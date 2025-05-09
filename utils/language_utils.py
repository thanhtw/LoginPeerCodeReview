"""
Language utilities for Java Peer Review Training System.

This module provides utilities for handling language selection and translation.
"""

import streamlit as st
import os
import logging
import sys
from typing import Dict, Any, Optional

# Add the parent directory to the path to allow absolute imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

# Import language package
from language import get_translations, get_llm_prompt_instructions, SUPPORTED_LANGUAGES, DEFAULT_LANGUAGE

# Configure logging
logger = logging.getLogger(__name__)

def init_language():
    """Initialize language selection in session state."""
    if "language" not in st.session_state:
        st.session_state.language = DEFAULT_LANGUAGE

def set_language(lang: str):
    """
    Set the application language.
    
    Args:
        lang: Language code (e.g., 'en', 'zh-tw')
    """
    # Check if language is actually changing
    current_lang = get_current_language()
    if lang == current_lang:
        # No change needed
        return
    
    if lang in SUPPORTED_LANGUAGES:
        # Store the old language for logging
        old_lang = st.session_state.language
        # Update the language
        st.session_state.language = lang
        logger.info(f"Changed language from {old_lang} to {lang}")
        
        # Set a flag to indicate language has changed
        st.session_state.language_changed = True
    else:
        logger.warning(f"Unsupported language: {lang}, using default: {DEFAULT_LANGUAGE}")
        st.session_state.language = DEFAULT_LANGUAGE

def get_current_language() -> str:
    """
    Get the current language.
    
    Returns:
        Current language code
    """
    return st.session_state.get("language", DEFAULT_LANGUAGE)

def t(key: str) -> str:
    """
    Translate a text key to the current language.
    
    Args:
        key: Text key to translate
        
    Returns:
        Translated text
    """
    current_lang = get_current_language()
    translations = get_translations(current_lang)
    
    # Return the translation if found, otherwise return the key itself
    return translations.get(key, key)

def get_llm_instructions() -> str:
    """
    Get the LLM instructions for the current language.
    
    Returns:
        Instructions string for LLM
    """
    current_lang = get_current_language()
    return get_llm_prompt_instructions(current_lang)

def render_language_selector():
    """Render a language selector in the sidebar."""
    with st.sidebar:
        st.subheader(t("language"))
        cols = st.columns([1, 1])
        
        with cols[0]:
            if st.button("English", use_container_width=True, 
                         disabled=get_current_language() == "en"):
                # Set the language
                set_language("en")
                # Force UI refresh to apply the language change
                #st.session_state.provider_selection["setup_complete"] = False
                #st.session_state.provider_selection["show_setup_modal"] = True
                st.rerun()
                
        with cols[1]:
            if st.button("繁體中文", use_container_width=True, 
                         disabled=get_current_language() == "zh-tw"):
                # Set the language
                set_language("zh-tw")
                #st.session_state.provider_selection["setup_complete"] = False
                #st.session_state.provider_selection["show_setup_modal"] = True
                # Force UI refresh to apply the language change
                st.rerun()
        
        # Add a more visible indicator for the current language
        current_lang = get_current_language()
        lang_display = "English" if current_lang == "en" else "繁體中文"
        st.markdown(f"""
        <div style="text-align: center; padding: 5px; background-color: rgba(76, 104, 215, 0.1); 
                    border-radius: 5px; margin-top: 5px;">
        <small>{t("current_language")}: <strong>{lang_display}</strong></small>
        </div>
        """, unsafe_allow_html=True)

def get_field_value(data: dict, english_name: str, default=None):
    """
    Get a field value with language awareness.
    
    Args:
        data: Dictionary containing the data
        english_name: The field name in English
        default: Default value to return if field not found
        
    Returns:
        The field value or default if not found
    """
    # Check if the data is None
    if data is None:
        return default
        
    # If field exists with English name, return it
    if english_name in data:
        return data[english_name]
        
    # Common Chinese translations for field names
    chinese_mappings = {
        "identified_count": ["已識別數量", "識別數量"],
        "total_problems": ["總問題數", "問題總數"],
        "identified_percentage": ["識別百分比", "識別百分率"],
        "review_sufficient": ["審查充分", "審查足夠"],
        "feedback": ["反饋", "回饋"],
        "identified_problems": ["已識別問題", "識別問題"],
        "missed_problems": ["遺漏問題", "漏掉的問題"],
        "false_positives": ["誤報", "假陽性"],
        "review_quality_score": ["審查質量得分", "審查質量分數"],
        "accuracy_percentage": ["準確率百分比", "準確率"],
        "missed_count": ["遺漏數量", "漏掉的數量"],
        "false_positive_count": ["誤報數量", "假陽性數量"],
        "valid": ["有效", "有效性"],
        "error": ["錯誤", "錯誤訊息"],
        "original_error_count": ["原始錯誤數量", "原始錯誤計數"]
    }
    
    # Try possible Chinese field names
    if english_name in chinese_mappings:
        for chinese_name in chinese_mappings[english_name]:
            if chinese_name in data:
                return data[chinese_name]
                
    # Return default if field not found
    return default