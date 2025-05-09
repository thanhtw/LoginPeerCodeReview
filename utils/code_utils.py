"""
Utility functions for code generation and processing in the Java Code Review System.

This module provides shared functionality for generating prompts, 
extracting code from responses, and handling error comments.
"""

import re
import random
import os
import logging
from typing import List, Dict, Any, Optional, Tuple
from langchain_core.language_models import BaseLanguageModel
from utils.language_utils import get_llm_instructions, get_current_language, get_field_value, get_state_attribute  # Add imports

# Import prompt templates
from prompts import get_prompt_template

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def add_line_numbers(code: str) -> str:
    """Add line numbers to code snippet."""
    lines = code.splitlines()
    max_line_num = len(lines)
    padding = len(str(max_line_num))
    
    # Create a list of lines with line numbers
    numbered_lines = []
    for i, line in enumerate(lines, 1):
        # Format line number with consistent padding
        line_num = str(i).rjust(padding)
        numbered_lines.append(f"{line_num} | {line}")
    
    return "\n".join(numbered_lines)

def create_code_generation_prompt(code_length: str, difficulty_level: str, selected_errors: list, domain: str = None, include_error_annotations: bool = True) -> str:
    """Create a concise prompt for generating Java code with intentional errors."""
    # Define code complexity by length
    complexity = {
        "short": "1 simple class with 1-2 basic methods (15-30 lines total)",
        "medium": "1 class with 3-5 methods of moderate complexity (40-80 lines total)",
        "long": "1-2 classes with 4-8 methods and clear relationships (100-150 lines total)"
    }.get(str(code_length).lower(), "1 class with methods")
    
    # Count the number of errors
    error_count = len(selected_errors)
    
    # Format errors concisely with only essential information
    error_list = []
    for i, error in enumerate(selected_errors, 1):
        error_type = get_field_value(error, "type", "unknown").upper()
        name = get_field_value(error, "name", "unknown")
        description = get_field_value(error, "description", "")
        implementation_guide = get_field_value(error, "implementation_guide", "")
        
        error_entry = f"{i}. {error_type} - {name}: {description}"
        if implementation_guide:
            error_entry += f"\nImplementation: {implementation_guide}"
        
        error_list.append(error_entry)
    
    # Join errors with clear separation
    error_instructions = "\n\n".join(error_list)
    
    # Get language-specific difficulty instructions template
    if difficulty_level.lower() == "easy":
        difficulty_instructions = get_prompt_template("beginner_instructions")
    elif difficulty_level.lower() == "medium":
        difficulty_instructions = get_prompt_template("intermediate_instructions")
    else:  # hard
        difficulty_instructions = get_prompt_template("advanced_instructions")
    
    domain_str = domain or "general"
    
    # Get language-specific instructions
    language_instructions = get_llm_instructions()
    
    # Get language-specific template
    template = get_prompt_template("code_generation_template")
    
    # Create the prompt by filling in the template safely
    prompt = f"{language_instructions}. " + format_template_safely(
        template,
        code_length=code_length,
        domain_str=domain_str,
        error_count=len(selected_errors),
        complexity=complexity,
        difficulty_instructions=difficulty_instructions,
        error_instructions=error_instructions,
        difficulty_level=difficulty_level
    )

    return prompt

def format_template_safely(template: str, **kwargs) -> str:
    """Format a template string safely, handling potential formatting errors."""
    try:
        # First attempt: use standard string formatting
        return template.format(**kwargs)
    except KeyError as e:
        # If we get a KeyError, log it and try a fallback approach
        logger.warning(f"Template formatting error: missing key {e}")
        # Replace problematic placeholders with their string values
        for key, value in kwargs.items():
            placeholder = "{" + key + "}"
            template = template.replace(placeholder, str(value))
        return template
    except Exception as e:
        # For any other error, log and return a basic formatted string
        logger.error(f"Template formatting error: {str(e)}")
        # Create a basic output with the key information
        return (f"Code evaluation for {kwargs.get('error_count', '?')} errors:\n\n"
                f"Code to evaluate:\n{kwargs.get('code', '')}\n\n"
                f"Errors to find:\n{kwargs.get('error_instructions', '')}")

def create_evaluation_prompt(code: str, requested_errors: list) -> str:
    """Create a clear and concise prompt for evaluating whether code contains required errors."""
    # Count the exact number of requested errors
    error_count = len(requested_errors)
    
    # Format requested errors clearly with language-aware field access
    error_list = []
    for i, error in enumerate(requested_errors, 1):
        # Get error type and name with language-aware access
        error_type = get_field_value(error, "type", "").upper()
        name = get_field_value(error, "name", "")
        description = get_field_value(error, "description", "")
        
        # If we still don't have a name, use a fallback
        if not name:
            name = "Unknown Error"
            
        error_list.append(f"{i}. {error_type} - {name}: {description}")
    
    error_instructions = "\n".join(error_list)

    # Get language-specific instructions
    language_instructions = get_llm_instructions()

    # Get language-specific template
    template = get_prompt_template("evaluation_template")
    
    # Create the prompt by filling in the template safely
    prompt = f"{language_instructions}. " + format_template_safely(
        template,
        code=code,
        error_count=error_count,
        error_instructions=error_instructions
    )
    
    return prompt

def create_regeneration_prompt(code: str, domain: str, missing_errors: list, found_errors: list, requested_errors: list) -> str:
    """Create a focused prompt for regenerating code with missing errors and removing extra errors."""
    # Total requested errors count
    total_requested = len(requested_errors)
    
    # Format missing and found errors
    missing_text = "\n".join(f"- {instr}" for instr in missing_errors) if missing_errors else "No missing errors - all requested errors are already implemented."
    found_text = "\n".join(f"- {err}" for err in found_errors) if found_errors else "No correctly implemented errors found."
    
    # Get language-specific instructions
    language_instructions = get_llm_instructions()
    
    # Get language-specific template
    template = get_prompt_template("regeneration_template")

    # Create the prompt by filling in the template safely
    prompt = f"{language_instructions}. " + format_template_safely(
        template,
        code=code,
        domain=domain,
        missing_text=missing_text,
        found_text=found_text,
        total_requested=total_requested
    )
    
    return prompt

def create_review_analysis_prompt(code: str, known_problems: list, student_review: str) -> str:
    """Create an optimized prompt for analyzing student code reviews."""
    # Count known problems
    problem_count = len(known_problems)
    
    # Format known problems clearly
    problems_text = "\n".join(f"- {problem}" for problem in known_problems)

    # Get language-specific instructions
    language_instructions = get_llm_instructions()

    # Get language-specific template
    template = get_prompt_template("review_analysis_template")
   
    # Create the prompt by filling in the template safely
    prompt = f"{language_instructions}. " + format_template_safely(
        template,
        code=code,
        problem_count=problem_count,
        problems_text=problems_text,
        student_review=student_review
    )
    
    return prompt

def create_feedback_prompt(code: str, known_problems: list, review_analysis: dict) -> str:
    """Create an optimized prompt for generating concise, focused guidance on student reviews."""
    # Extract data from review analysis with language-aware access
    identified = get_field_value(review_analysis, "identified_count", 0)
    total = get_field_value(review_analysis, "total_problems", len(known_problems))
    accuracy = get_field_value(review_analysis, "identified_percentage", 0)
    iteration = get_field_value(review_analysis, "iteration_count", 1)
    max_iterations = get_field_value(review_analysis, "max_iterations", 3)
    remaining = get_field_value(review_analysis, "remaining_attempts", max_iterations - iteration)
    
    # Format identified problems
    identified_problems = get_field_value(review_analysis, "identified_problems", [])
    identified_text = ""
    for problem in identified_problems:
        if isinstance(problem, dict):
            problem_text = get_field_value(problem, "problem", "")
            identified_text += f"- {problem_text}\n"
        else:
            identified_text += f"- {problem}\n"
    
    # Format missed problems
    missed_problems = get_field_value(review_analysis, "missed_problems", [])
    missed_text = ""
    for problem in missed_problems:
        if isinstance(problem, dict):
            problem_text = get_field_value(problem, "problem", "")
            missed_text += f"- {problem_text}\n"
        else:
            missed_text += f"- {problem}\n"

    # Get language-specific instructions
    language_instructions = get_llm_instructions()

    # Get language-specific template
    template = get_prompt_template("feedback_template")

    # Create the prompt by filling in the template safely
    prompt = f"{language_instructions}. " + format_template_safely(
        template,
        iteration=iteration,
        max_iterations=max_iterations,
        identified=identified,
        total=total,
        accuracy=accuracy,
        remaining=remaining,
        identified_text=identified_text or "None",
        missed_text=missed_text or "None - great job!"
    )
    
    return prompt

def generate_comparison_report(evaluation_errors: List[str], review_analysis: Dict[str, Any], 
                              review_history: List[Dict[str, Any]] = None, llm = None) -> str:
    """Generate a comparison report with proper language handling."""
    # If LLM is provided, use it to generate the report with correct language
    if llm:
        try:
            # Create the prompt for the LLM
            prompt = create_comparison_report_prompt(evaluation_errors, review_analysis, review_history)
            
            # Generate the report with the LLM
            response = llm.invoke(prompt)
            
            # Process the response
            if hasattr(response, 'content'):
                report = response.content
            elif isinstance(response, dict) and 'content' in response:
                report = response['content']
            else:
                report = str(response)
            
            # Clean up the report
            report = report.replace('\\n', '\n')
            
            return report
        except Exception as e:
            # Log the error
            logger.error(f"Error generating comparison report with LLM: {str(e)}")
            
            # Fall back to static generation with translated field names
            from utils.language_utils import t
            
            # Get identified, missed and false positive info with language awareness
            identified_count = get_field_value(review_analysis, "identified_count", 0)
            total_problems = get_field_value(review_analysis, "total_problems", 0)
            accuracy = (identified_count / total_problems * 100) if total_problems > 0 else 0
            
            # Create a basic report with translated field names
            return (
                f"# {t('review_feedback')}\n\n"
                f"## {t('review_performance_summary')}\n\n"
                f"{t('you_found')} {identified_count} {t('of')} {total_problems} {t('issues')} "
                f"({accuracy:.1f}% {t('accuracy')}).\n\n"
                f"{t('check_detailed_analysis')}"
            )
    else:
        # If no LLM is provided, use static generation with translated field names
        from utils.language_utils import t
        
        # Get identified, missed and false positive info with language awareness
        identified_count = get_field_value(review_analysis, "identified_count", 0)
        total_problems = get_field_value(review_analysis, "total_problems", 0)
        accuracy = (identified_count / total_problems * 100) if total_problems > 0 else 0
        
        # Create a basic report with translated field names
        return (
            f"# {t('review_feedback')}\n\n"
            f"## {t('review_performance_summary')}\n\n"
            f"{t('you_found')} {identified_count} {t('of')} {total_problems} {t('issues')} "
            f"({accuracy:.1f}% {t('accuracy')}).\n\n"
            f"{t('check_detailed_analysis')}"
        )

def extract_both_code_versions(response) -> Tuple[str, str]:
    """Extract both annotated and clean code versions from LLM response."""
    # Check for None or empty response
    if not response:
        return "", ""
    
    # Handle AIMessage or similar objects (from LangChain)
    if hasattr(response, 'content'):
        # Extract the content from the message object
        response_text = response.content
    elif isinstance(response, dict) and 'content' in response:
        # Handle dictionary-like response
        response_text = response['content']
    else:
        # Assume it's already a string
        response_text = str(response)
    
    # Handle Groq-specific response format
    # Groq often wraps content differently, so check for that pattern
    if "content=" in response_text and not response_text.startswith("```"):
        # Extract just the content part
        response_text = response_text.replace("content=", "")
        # Remove any leading/trailing quotes if present
        if (response_text.startswith('"') and response_text.endswith('"')) or \
           (response_text.startswith("'") and response_text.endswith("'")):
            response_text = response_text[1:-1]
    
    # Extract annotated version with java-annotated tag
    annotated_pattern = r'```java-annotated\s*(.*?)\s*```'
    annotated_matches = re.findall(annotated_pattern, response_text, re.DOTALL)
    annotated_code = annotated_matches[0] if annotated_matches else ""
    
    # Extract clean version with java-clean tag
    clean_pattern = r'```java-clean\s*(.*?)\s*```'
    clean_matches = re.findall(clean_pattern, response_text, re.DOTALL)
    clean_code = clean_matches[0] if clean_matches else ""
    
    # Fallbacks if specific tags aren't found
    if not annotated_code:
        # Try to find any java code block for annotated version
        java_pattern = r'```java\s*(.*?)\s*```'
        java_matches = re.findall(java_pattern, response_text, re.DOTALL)
        if java_matches:
            annotated_code = java_matches[0]
        else:
            # Last resort: look for any code block
            any_code_pattern = r'```\s*(.*?)\s*```'
            any_matches = re.findall(any_code_pattern, response_text, re.DOTALL)
            if any_matches:
                # Use the largest code block
                annotated_code = max(any_matches, key=len)
    
    # For Groq responses: If we found annotated but no clean code, create clean code by removing error comments
    if annotated_code and not clean_code:
        # Remove lines with error comments
        clean_lines = []
        for line in annotated_code.splitlines():
            if "// ERROR:" not in line:
                clean_lines.append(line)
        clean_code = "\n".join(clean_lines)
    
    # Log detailed information if extraction failed
    if not annotated_code:
        logger.warning(f"Failed to extract annotated code from response text: {response_text[:200]}...")
    if not clean_code:
        logger.warning(f"Failed to extract clean code from response text: {response_text[:200]}...")
    
    return annotated_code, clean_code

def process_llm_response(response):
    """Process LLM response to handle different formats from different providers."""
    # Handle None case
    if response is None:
        return ""
    
    try:
        # Extract content based on response type
        if hasattr(response, 'content'):
            # AIMessage or similar object from LangChain
            content = response.content
        elif isinstance(response, dict) and 'content' in response:
            # Dictionary with content key
            content = response['content']
        else:
            # Assume it's already a string
            content = str(response)
        
        # Fix common formatting issues:
        
        # 1. Remove any 'content=' prefix if present (common in Groq debug output)
        if content.startswith('content='):
            content = content.replace('content=', '', 1)
        
        # 2. Fix escaped newlines and quotes
        content = content.replace('\\n', '\n')
        content = content.replace('\\"', '"')
        content = content.replace('\\\'', '\'')
        
        # 3. Remove any surrounding quotes that might have been added
        if (content.startswith('"') and content.endswith('"')) or \
           (content.startswith("'") and content.endswith("'")):
            content = content[1:-1]
        
        # 4. Fix markdown formatting issues
        content = re.sub(r'\*\*(.+?)\*\*', r'**\1**', content)  # Fix bold formatting
        
        # 5. Clean up any raw escape sequences for newlines
        content = re.sub(r'(?<!\\)\\n', '\n', content)
        content = re.sub(r'\\\\n', '\\n', content)  # Preserve intentional \n in code
        
        # 6. Fix any metadata that might have leaked into the content
        content = re.sub(r'response_metadata=\{.*\}', '', content)
        content = re.sub(r'additional_kwargs=\{.*\}', '', content)
        
        return content
    except Exception as e:
        logger.error(f"Error processing LLM response: {str(e)}")
        # Return a safe default
        if response is not None:
            try:
                return str(response)
            except:
                pass
        return ""

def get_error_count_from_state(state: Any, difficulty_level: str = "medium") -> int:
    """
    Get error count from the state object or parameters.
    Replaces the fixed get_error_count_for_difficulty function.
    
    Args:
        state: State object that might contain error count info
        difficulty_level: Fallback difficulty level if state doesn't have count
        
    Returns:
        Number of errors to use
    """
    # First try to get error count from selected_specific_errors if available
    if get_state_attribute(state, 'selected_specific_errors') and len(get_state_attribute(state, 'selected_specific_errors', [])) > 0:
        return len(get_state_attribute(state, 'selected_specific_errors', []))
    
    # Next try to get from original_error_count if it's been set
    if get_state_attribute(state, 'original_error_count', 0) > 0:
        return get_state_attribute(state, 'original_error_count', 0)
    
    # If we have selected error categories, use their count
    if get_state_attribute(state, 'selected_error_categories'):
        selected_categories = get_state_attribute(state, 'selected_error_categories', {})
        if selected_categories:
            java_errors = get_field_value(selected_categories, "java_errors", [])
            # Use at least one error per selected category
            category_count = len(java_errors)
            if category_count > 0:
                return max(category_count, 2)  # Ensure at least 2 errors
    
    # Finally fall back to difficulty-based default if all else fails
    difficulty_map = {
        "easy": 2,
        "medium": 4,
        "hard": 6
    }
    return difficulty_map.get(str(difficulty_level).lower(), 4)