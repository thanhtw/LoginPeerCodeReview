"""
English translations for Java Peer Review Training System.

This module provides English translations for the UI and system messages.
"""

# LLM instructions for responding in English
llm_instructions = """
Please respond in English. Use clear, concise language appropriate for programming education.
Format code examples, error explanations, and feedback in a way that's easy to understand for 
programming students.
"""

# English translations
translations = {
    # General
    "app_title": "Java Code Review Training System",
    "app_subtitle": "Learn and practice Java code review skills with AI-generated exercises",
    
    # Login/Register
    "login": "Login",
    "register": "Register",
    "email": "Email",
    "password": "Password",
    "confirm_password": "Confirm Password",
    "display_name": "Display Name",
    "experience_level": "Your Experience Level",
    "demo_mode": "Demo Mode",
    "continue_demo": "Continue in Demo Mode (No Login Required)",
    "login_failed": "Login failed",
    "invalid_credentials": "Invalid email or password",
    "registration_failed": "Registration failed",
    "fill_all_fields": "Please fill in all fields",
    "passwords_mismatch": "Passwords do not match",
    "email_in_use": "Email already in use",
    "hi": "Hi",
    "level": "Your level",
    "review_times": "Review Times",
    "score": "Your Score",
    "about": "About",
    "about_app": "This application helps you learn and practice Java code review skills by generating code with intentional errors for you to identify.",
    
    #Provide sections
    'llm_provider_setup':'LLM Provider Setup',
    'please_select_LLM':'Please select the LLM provider you want to use',
    'select_LLM':'Select the LLM provider',
    'select_ollama': 'Ollama will use locally hosted models running on your machine.',
    'ollama_error':'Cannot connect to Ollama: Failed to connect to Ollama at http://localhost:11434',
    'use_ollama':'Use Olama',
    'connected_ollama':'Connected to Ollama',
    'groq_api_message':'Groq API uses cloud-hosted models and requires an API key',
    'groq_api_key':'Groq API Key ',
    'test_connection':'Test Connection',
    'api_key_required': 'API key is required for Groq',
    'connect_groq_success':'Connected to Groq API successfully',
    'connect_groq_failed':'Failed to connect to Groq API. Please check your API key',
    'ollama_mode':'Ollama (Local)',
    'groq_mode':'Groq API (Cloud)',
    'change_provider':'Change Provider',
    'provider':'Provider',
    'status':'Status',
    'using_groq': 'Using Groq API (cloud)',
    'connected_groq':'Connected to Groq API',
    'connected':'Connected',



    # Code Generation
    "generate_problem": "Generate Java Code Review Problem",
    "error_selection_mode": "Error Selection Mode",
    "error_selection_prompt": "How would you like to select errors?",
    "advanced_mode": "Advanced: Select by error categories",
    "specific_mode": "Specific: Choose exact errors to include",
    "select_error_categories": "Select Error Categories",
    "advanced_mode_help": "Advanced Mode: Select specific error categories to include in the generated code. The system will randomly choose errors from your selected categories.",
    "no_categories": "No categories selected. You must select at least one category to generate code.",
    "selected_categories": "Selected Categories",
    "select_specific_errors": "Select Specific Errors",
    "error_details": "Error Details",
    "error_categories": "Error Categories",
    "code_params": "Code Parameters (Based on Your Level)",
    "difficulty": "Difficulty Level",
    "code_length": "Code Length",
    "params_based_on_level": "These parameters are automatically set based on your experience level",
    "generate_code_button": "Generate Code Problem",
    "generating_code": "Generating and evaluating code...",
    "code_generation_process": "Code Generation Process",
    "step1": "1. Generate Code",
    "step2": "2. Evaluate Code",
    "step3": "3. Regenerate",
    "step4": "4. Ready for Review",
    "generation_stats": "Generation Stats",
    "quality": "Quality",
    "errors_found": "Errors Found",
    "generation_attempts": "Generation Attempts",
    "generate_new": "Generate New Problem",
    "generated_java_code": "Generated Java Code",
    "starting_new_session": "Starting a new code review session. Please configure and generate a new problem.",
    "generated_initial_code": "Generated initial code",
    "evaluated_code": "Evaluated code for requested errors",
    "regenerating_code": "Regenerating code",
    "reevaluated_code": "Re-evaluated regenerated code",
    "reevaluating_code": "Re-evaluating code...",
    "code_generation_completed": "Code generation process completed successfully",
    "evaluating_code": "Evaluating generated code for errors...",
    "code_generation_complete": "Code generation complete! Proceeding to review tab...",
    "workflow_not_initialized": "Workflow state not initialized. Please refresh the page.",
    "process_details": "Process Details",
    "no_process_details": "No process details available.",
    "code_quality": "Code Quality",
    "found": "Found",
    "of": "of",
    "requested_errors": "requested errors",
    "improving_code": "Improving code quality",
    "all_errors_implemented": "All requested errors successfully implemented!",
    "good_quality": "Good quality code generated with",
    "partial_quality": "Code generated with",
    "added": "Added",
    "new_errors": "new errors in this attempt!",
    "completed": "completed",
    "attempts": "attempts",
    "no_errors_found": "No errors found in",
    "category": "category",
    "selected": "Selected",
    "select": "Select",
    "remove": "Remove",
    "selected_issues": "Selected Issues",
    "no_specific_issues": "No specific issue selected. Random errors will be used based on categories.",
    'easy':'Easy',
    'medium': 'Medium',
    'hard':'Hard',
    'short':'Short',
    'long':'Long',
    
    # Review
    "review_java_code": "Review Java Code",
    "no_code_generated": "No code has been generated yet. Please go to the 'Generate Problem' tab first.",
    "submit_review": "Submit Your Code Review",
    "attempt": "Attempt",
    "of": "of",
    "review_guidelines": "Review Guidelines",
    "how_to_write": "How to Write an Effective Code Review:",
    "be_specific": "Be Specific: Point out exact lines or areas where problems occur",
    "be_comprehensive": "Be Comprehensive: Look for different types of issues",
    "be_constructive": "Be Constructive: Suggest improvements, not just criticisms",
    "check_for": "Check for:",
    "review_example": "Examples of Good Review Comments:",
    "enter_review": "Enter your review comments here",
    "submit_review_button": "Submit Review",
    "clear": "Clear",
    "review_guidance": "Review Guidance",
    "previous_results": "Previous Results",
    "previous_review": "Previous Review",
    "processing_review": "Processing your review...",
    "view_feedback": "View Feedback",
    "all_errors_found": "🎉 Congratulations! You've found all the errors! Proceed to the feedback tab to see your results.",
    "iterations_completed": "You have completed all {max_iterations} review iterations. View feedback in the next tab.",
    
    # Feedback
    "educational_feedback": "Educational Feedback:",
    "your_review": "Your Review:",
    "your_final_review": "Your Final Review (Attempt {iteration})",
    "issues_found": "Issues Found",
    "accuracy": "Accuracy",
    "false_positives": "False Positives",
    "review_history": "Review History",
    "detailed_analysis": "Detailed Analysis",
    "identified_issues": "Identified Issues",
    "missed_issues": "Missed Issues",
    "new_session": "Ready for another review?",
    "new_session_desc": "Start a new code review session to practice with different errors.",
    "start_new_session": "Start New Session",
    "complete_review_first":"Please complete all review attempts before accessing feedback.",
    "current_process_review1":"Current progress",
    "current_process_review2":"attempts completed",

    
    # Tabs
    "tab_generate": "1. Generate Problem",
    "tab_review": "2. Submit Review",
    "tab_feedback": "3. View Feedback",
    "tab_logs": "4. LLM Logs",
    
    # Error categories
    "logical": "Logical",
    "syntax": "Syntax",
    "code_quality": "Code Quality",
    "standard_violation": "Standard Violation",
    "java_specific": "Java Specific",
    
    # Error category descriptions
    "logical_desc": "Issues with program logic, calculations, and flow control",
    "syntax_desc": "Java language syntax and structure errors",
    "code_quality_desc": "Style, readability, and maintainability issues",
    "standard_violation_desc": "Violations of Java conventions and best practices",
    "java_specific_desc": "Issues specific to Java language features",
    
    # Language selection
    "language": "Language",
    "english": "English",
    "chinese": "Traditional Chinese",

    # LLM logs
    "llm_logs_title": "LLM Interaction Logs",
    "refresh_logs": "Refresh Logs",
    "logs_to_display": "Number of logs to display",
    "filter_by_type": "Filter by log type:",
    "filter_by_date": "Filter by date:",
    "displaying_logs": "Displaying {count} recent logs. Newest logs appear first.",
    "unknown_time": "Unknown time",
    "unknown_type": "Unknown type",
    "prompt_tab": "Prompt",
    "response_tab": "Response",
    "metadata_tab": "Metadata",
    "prompt_sent": "Prompt sent to LLM:",
    "response_label": "Response:",
    "no_response": "No response available",
    "no_metadata": "No metadata available",
    "no_logs_match": "No logs match the selected filters.",
    "no_logs_found": "No logs found. Generate code or submit reviews to create log entries.",
    "log_info_markdown": """
    ### Log Information

    Log files are stored in the `llm_logs` directory, with subdirectories for each interaction type:

    - code_generation
    - code_regeneration
    - code_evaluation
    - review_analysis
    - summary_generation

    Each log is stored as both a `.json` file (for programmatic use) and a `.txt` file (for easier reading).
    """,
    "llm_logger_not_initialized": "LLM logger not initialized.",
    "clear_logs": "Clear Logs",
    "clear_logs_warning": "This will remove in-memory logs. Log files on disk will be preserved.",
    "confirm_clear_logs": "Confirm Clear Logs",
    "logs_cleared": "Logs cleared."
}