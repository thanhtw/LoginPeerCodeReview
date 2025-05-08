"""
Language utilities for Java Peer Review Training System.

This module provides utilities for handling language selection and translation.
"""

import sys
import os
import streamlit as st
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from translations import get_text

def init_language():
    """Initialize language selection in session state."""
    if "language" not in st.session_state:
        st.session_state.language = "en"

def set_language(lang):
    """
    Set the application language.
    
    Args:
        lang: Language code (en or zh-tw)
    """
    st.session_state.language = lang

def get_current_language():
    """
    Get the current language.
    
    Returns:
        Current language code
    """
    return st.session_state.get("language", "en")

def t(key):
    """
    Translate a text key to the current language.
    Shorthand function for get_text with current language.
    
    Args:
        key: Text key to translate
        
    Returns:
        Translated text
    """
    return get_text(key, get_current_language())

def render_language_selector():
    """Render a language selector in the sidebar."""
    with st.sidebar:
        cols = st.columns([1, 1])
        with cols[0]:
            if st.button("English", use_container_width=True, disabled=get_current_language() == "en"):
                set_language("en")
                st.rerun()
        with cols[1]:
            if st.button("繁體中文", use_container_width=True, disabled=get_current_language() == "zh-tw"):
                set_language("zh-tw")
                st.rerun()