# At the top of the file, update imports
import logging
import re
from typing import Dict, Any, List, Tuple, Optional

from state_schema import WorkflowState, CodeSnippet
from utils.code_utils import extract_both_code_versions, create_regeneration_prompt, get_error_count_from_state
import random
from utils.language_utils import t, get_field_value, get_state_attribute  # Add proper imports

# Configure logging
logger = logging.getLogger(__name__)

class WorkflowNodes:
    """
    Node implementations for the Java Code Review workflow.
    
    This class contains all node handlers that process state transitions
    in the LangGraph workflow, extracted for better separation of concerns.
    """
    
    def __init__(self, code_generator, code_evaluation, error_repository, llm_logger):
        """
        Initialize workflow nodes with required components.
        
        Args:
            code_generator: Component for generating Java code with errors
            code_evaluation: Component for evaluating generated code quality
            error_repository: Repository for accessing Java error data
            llm_logger: Logger for tracking LLM interactions
        """
        self.code_generator = code_generator
        self.code_evaluation = code_evaluation
        self.error_repository = error_repository
        self.llm_logger = llm_logger
    
    def generate_code_node(self, state: WorkflowState) -> WorkflowState:
        """
        Generate Java code with errors based on selected parameters.
        Ensures exact match between selected and generated errors.
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated workflow state with generated code
        """
        try:
            # Get parameters from state with language-aware access
            code_length = get_state_attribute(state, "code_length", "medium")
            difficulty_level = get_state_attribute(state, "difficulty_level", "medium")
            selected_error_categories = get_state_attribute(state, "selected_error_categories", {})
            selected_specific_errors = get_state_attribute(state, "selected_specific_errors", [])
            
            # Reset state for a fresh generation
            state.evaluation_attempts = 0
            state.evaluation_result = None
            state.code_generation_feedback = None

            # Randomly select a domain if not already set
            if not get_state_attribute(state, "domain", None):
                # Use the domains from code_generator if available
                if hasattr(self.code_generator, 'domains') and self.code_generator.domains:
                    state.domain = random.choice(self.code_generator.domains)
                else:
                    # Default domains if not available in code_generator
                    domains = [
                        "user_management", "file_processing", "data_validation", 
                        "calculation", "inventory_system", "notification_service",
                        "logging", "banking", "e-commerce", "student_management"
                    ]
                    state.domain = random.choice(domains)
                
                logger.info(f"Selected domain for code generation: {get_state_attribute(state, 'domain', 'general')}")
            
            # Use the domain from state
            domain = get_state_attribute(state, "domain", "general")
            
            # Determine whether we're using specific errors or categories
            using_specific_errors = len(selected_specific_errors) > 0
            
            # Get appropriate errors based on selection mode
            if using_specific_errors:
                # Using specific errors mode - IMPORTANT: Use the exact selected errors without modification
                if not selected_specific_errors:
                    state.error = t("no_specific_errors_selected")
                    return state
                        
                logger.info(f"Using specific errors mode with {len(selected_specific_errors)} errors")
                # Use the selected errors directly without applying count filtering
                selected_errors = selected_specific_errors
                # Store the original requested error count
                original_error_count = len(selected_errors)
            else:
                # Using category-based selection mode
                if not selected_error_categories or not get_field_value(selected_error_categories, "java_errors", []):
                    state.error = t("no_categories")
                    return state
                            
                logger.info(f"Using category-based mode with categories: {selected_error_categories}")
                
                # Get exact number based on difficulty
                required_error_count = get_error_count_from_state(state, difficulty_level)
                
                selected_errors, _ = self.error_repository.get_errors_for_llm(
                    selected_categories=selected_error_categories,
                    count=required_error_count,
                    difficulty=difficulty_level
                )
                
                # Make sure we have the right number of errors
                if len(selected_errors) < required_error_count:
                    logger.warning(f"Got fewer errors ({len(selected_errors)}) than requested ({required_error_count})")
                    # Don't modify the count in this case - use what we have
                    original_error_count = len(selected_errors)
                elif len(selected_errors) > required_error_count:
                    logger.warning(f"Got more errors ({len(selected_errors)}) than requested ({required_error_count})")
                    # Trim to exactly the required count
                    selected_errors = selected_errors[:required_error_count]
                    original_error_count = required_error_count
                else:
                    original_error_count = required_error_count
            
            # Log detailed information about selected errors for debugging
            self._log_selected_errors(selected_errors)
            logger.info(f"Final error count for generation: {len(selected_errors)}")
            
            # Generate code with selected errors
            response = self.code_generator._generate_with_llm(
                code_length=code_length,
                difficulty_level=difficulty_level,
                selected_errors=selected_errors,
                domain=domain
            )

            # Extract both annotated and clean versions
            annotated_code, clean_code = extract_both_code_versions(response)

            # Create code snippet object
            code_snippet = CodeSnippet(
                code=annotated_code,
                clean_code=clean_code,
                raw_errors={
                    "java_errors": selected_errors
                },
                expected_error_count=original_error_count
            )
                                    
            # Update state with the original error count for consistency
            state.original_error_count = original_error_count
            
            # Update state
            state.code_snippet = code_snippet
            state.current_step = "evaluate"
            return state
                    
        except Exception as e:           
            logger.error(f"{t('error')} generating code: {str(e)}", exc_info=True)
            state.error = f"{t('error')} generating code: {str(e)}"
            return state

    def evaluate_code_node(self, state: WorkflowState) -> WorkflowState:
        """
        Evaluate generated code to ensure it contains the requested errors.
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated workflow state with evaluation results
        """
        try:
            logger.info("Starting code evaluation node")
            
            # Validate code snippet
            code_snippet = get_state_attribute(state, "code_snippet", None)
            if not code_snippet:
                state.error = t("no_code_snippet_evaluation")
                return state
                    
            # Get the code with annotations
            code = code_snippet.code
            
            # Get requested errors from state
            requested_errors = self._extract_requested_errors(state)
            requested_count = len(requested_errors)
            
            # Ensure we're using the original error count for consistency
            original_error_count = get_state_attribute(state, "original_error_count", 0)
            if original_error_count == 0 and hasattr(code_snippet, 'expected_error_count'):
                # If not set in state, try to get it from code snippet
                original_error_count = code_snippet.expected_error_count
                # Update state with this count
                state.original_error_count = original_error_count
                
            # If we still don't have it, use the requested count
            if original_error_count == 0:
                original_error_count = requested_count
                state.original_error_count = original_error_count
                
            logger.info(f"Evaluating code for {original_error_count} expected errors")
            
            # Evaluate the code
            raw_evaluation_result = self.code_evaluation.evaluate_code(
                code, requested_errors
            )
            
            # IMPORTANT: Ensure evaluation_result is a dictionary
            if not isinstance(raw_evaluation_result, dict):
                logger.error(f"Expected dict for evaluation_result, got {type(raw_evaluation_result)}")
                # Create a default dictionary with the necessary structure
                evaluation_result = {
                    "found_errors": [],
                    "missing_errors": [f"{error.get('type', '').upper()} - {error.get('name', '')}" 
                                    for error in requested_errors],
                    "valid": False,
                    "feedback": f"Error in evaluation. Please ensure the code contains all {original_error_count} requested errors.",
                    "original_error_count": original_error_count  # Add original count for consistency
                }
            else:
                evaluation_result = raw_evaluation_result
                # Add the original error count to the evaluation result
                evaluation_result["original_error_count"] = original_error_count

                # IMPORTANT: Explicitly set valid flag based on missing errors
                missing_errors = get_field_value(evaluation_result, 'missing_errors', [])
                
                # Only valid if no missing errors
                has_missing = len(missing_errors) > 0               
                evaluation_result['valid'] = not has_missing
                
                # Log explicit validation status
                logger.info(f"Code validation: valid={evaluation_result['valid']}, " 
                        f"missing={len(missing_errors)}")
                
            # Update state with evaluation results
            state.evaluation_result = evaluation_result
            state.evaluation_attempts += 1
            
            # Log evaluation results
            found_count = len(get_field_value(evaluation_result, 'found_errors', []))
            missing_count = len(get_field_value(evaluation_result, 'missing_errors', []))
            logger.info(f"Code evaluation complete: {found_count}/{original_error_count} errors implemented, {missing_count} missing")
            
            feedback = None
            
            # If we have missing errors, we need to regenerate the code
            needs_regeneration = missing_count > 0
            
            # Generate feedback for regeneration
            if missing_count > 0:
                logger.warning(f"Missing {missing_count} out of {original_error_count} requested errors")
                
                # Use standard regeneration prompt but enhance it for clarity
                if hasattr(self.code_evaluation, 'generate_improved_prompt'):
                    feedback = self.code_evaluation.generate_improved_prompt(
                        code, requested_errors, evaluation_result
                    )
                else:
                  
                    # Use the regeneration prompt with emphasis on adding missing errors
                    feedback = create_regeneration_prompt(
                        code=code,
                        domain=get_state_attribute(state, "domain", "general"),
                        missing_errors=get_field_value(evaluation_result, 'missing_errors', []),
                        found_errors=get_field_value(evaluation_result, 'found_errors', []),
                        requested_errors=requested_errors
                    )
            else:
                # No missing errors - we're good!
                logger.info(f"All {original_error_count} requested errors implemented correctly")
                             
                feedback = create_regeneration_prompt(
                    code=code,
                    domain=get_state_attribute(state, "domain", "general"),
                    missing_errors=[],
                    found_errors=get_field_value(evaluation_result, 'found_errors', []),
                    requested_errors=requested_errors                    
                )
                    
            state.code_generation_feedback = feedback
          
            # Improved decision logic for next step
            evaluation_valid = get_field_value(evaluation_result, "valid", False)
            evaluation_attempts = get_state_attribute(state, "evaluation_attempts", 0) 
            max_evaluation_attempts = get_state_attribute(state, "max_evaluation_attempts", 3)
            
            if evaluation_valid:
                state.current_step = "review"
                logger.info("All errors successfully implemented, proceeding to review")
            elif needs_regeneration and evaluation_attempts < max_evaluation_attempts:
                # If we have missing errors and haven't reached max attempts, regenerate
                state.current_step = "regenerate"
                logger.info(f"Found {missing_count} missing errors, proceeding to regeneration")
            else:
                # Otherwise, we've either reached max attempts or have no more missing errors
                state.current_step = "review"
                if evaluation_attempts >= max_evaluation_attempts:
                    logger.warning(f"Reached maximum evaluation attempts ({max_evaluation_attempts}). Proceeding to review.")
                else:
                    logger.info("No missing errors to fix, proceeding to review")
            
            return state
            
        except Exception as e:
            logger.error(f"Error evaluating code: {str(e)}", exc_info=True)
            state.error = f"Error evaluating code: {str(e)}"
            return state

    def analyze_review_node(self, state: WorkflowState) -> WorkflowState:
        """
        Analyze student review and provide feedback.
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated workflow state with review analysis
        """
        try:
            # Validate review history
            review_history = get_state_attribute(state, "review_history", [])
            if not review_history:
                state.error = t("no_review_submitted")
                return state
                    
            latest_review = review_history[-1]
            student_review = latest_review.student_review
            
            # Validate code snippet
            code_snippet = get_state_attribute(state, "code_snippet", None)
            if not code_snippet:
                state.error = t("no_code_snippet_available")
                return state
                    
            code = code_snippet.code
            
            # Use evaluation result to extract problem information
            known_problems = []
            original_error_count = get_state_attribute(state, "original_error_count", 0)
            
            evaluation_result = get_state_attribute(state, "evaluation_result", {})
            if evaluation_result and 'found_errors' in evaluation_result:
                known_problems = get_field_value(evaluation_result, 'found_errors', [])
            
            # Get the student response evaluator
            evaluator = getattr(self, "evaluator", None)
            if not evaluator:
                state.error = t("student_evaluator_not_initialized")
                return state
            
            # Use the standard evaluation method
            analysis = evaluator.evaluate_review(
                code_snippet=code,
                known_problems=known_problems,
                student_review=student_review
            )
            
            # Update the analysis with the original error count for consistent metrics
            if original_error_count > 0:
                # Store the found problem count and original count
                found_problems_count = len(known_problems)
                
                # Use language-aware field value retrieval
                identified_count = get_field_value(analysis, "identified_count", 0)
                
                # Override total_problems to use original_error_count
                analysis["total_problems"] = original_error_count
                analysis["original_error_count"] = original_error_count
                
                # Recalculate percentages based on original count
                analysis["identified_percentage"] = (identified_count / original_error_count) * 100
                analysis["accuracy_percentage"] = (identified_count / original_error_count) * 100
                
                logger.info(f"Updated review analysis: {identified_count}/{original_error_count} " +
                        f"({analysis['identified_percentage']:.1f}%) [Found problems: {found_problems_count}]")
                
                # Mark review as sufficient if all errors are found
                if identified_count == original_error_count:
                    analysis["review_sufficient"] = True
                    logger.info("All errors found! Marking review as sufficient.")
                    
            # Update the review with analysis
            latest_review.analysis = analysis
            
            # Check if the review is sufficient
            review_sufficient = get_field_value(analysis, "review_sufficient", False)
            state.review_sufficient = review_sufficient
            
            # Generate targeted guidance if needed
            current_iteration = get_state_attribute(state, "current_iteration", 1)
            max_iterations = get_state_attribute(state, "max_iterations", 3)
            
            if not review_sufficient and current_iteration < max_iterations:
                targeted_guidance = evaluator.generate_targeted_guidance(
                    code_snippet=code,
                    known_problems=known_problems,
                    student_review=student_review,
                    review_analysis=analysis,
                    iteration_count=current_iteration,
                    max_iterations=max_iterations
                )
                latest_review.targeted_guidance = targeted_guidance
            
            # Increment iteration count
            state.current_iteration += 1
            
            # Update state
            state.current_step = "analyze"
            
            return state
        
        except Exception as e:
            logger.error(f"Error analyzing review: {str(e)}", exc_info=True)
            state.error = f"Error analyzing review: {str(e)}"
            return state

    def regenerate_code_node(self, state: WorkflowState) -> WorkflowState:
        """
        Regenerate code based on evaluation feedback.
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated workflow state with regenerated code
        """
        try:
            evaluation_attempts = get_state_attribute(state, "evaluation_attempts", 0)
            logger.info(f"Starting enhanced code regeneration (Attempt {evaluation_attempts})")
            
            # Use the code generation feedback to generate improved code
            feedback_prompt = get_state_attribute(state, "code_generation_feedback", "")
            
            # Generate code with feedback prompt
            if hasattr(self.code_generator, 'llm') and self.code_generator.llm:
                # Log the regeneration prompt before sending to LLM
                metadata = {
                    "code_length": get_state_attribute(state, "code_length", "medium"),
                    "difficulty_level": get_state_attribute(state, "difficulty_level", "medium"),
                    "domain": get_state_attribute(state, "domain", "general"),
                    "selected_errors": get_state_attribute(state, "selected_error_categories", {}),
                    "attempt": evaluation_attempts,
                    "max_attempts": get_state_attribute(state, "max_evaluation_attempts", 3)
                }
                
                # Log the prompt before it's sent to the LLM
                self.llm_logger.log_regeneration_prompt(feedback_prompt, metadata)
                
                # Generate the code
                response = self.code_generator.llm.invoke(feedback_prompt)
                
                # Log the full regeneration with response
                self.llm_logger.log_code_regeneration(feedback_prompt, response, metadata)
                
                # Process the response
                annotated_code, clean_code = extract_both_code_versions(response)                
                
                # Get requested errors from state
                requested_errors = self._extract_requested_errors(state)
                
                # Create updated code snippet
                state.code_snippet = CodeSnippet(
                    code=annotated_code,
                    clean_code=clean_code,
                    raw_errors={
                        "java_errors": requested_errors
                    }
                )
                
                # Move to evaluation step again
                state.current_step = "evaluate"
                logger.info(f"Code regenerated successfully on attempt {evaluation_attempts}")
                
                return state
            else:
                # If no LLM available, fall back to standard generation
                logger.warning("No LLM available for regeneration. Falling back to standard generation.")
                return self.generate_code_node(state)
            
        except Exception as e:                 
            logger.error(f"Error regenerating code: {str(e)}", exc_info=True)
            state.error = f"Error regenerating code: {str(e)}"
            return state
    
    def review_code_node(self, state: WorkflowState) -> WorkflowState:
        """
        Review code node - this is a placeholder since user input happens in the UI.
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated workflow state
        """
        # This node is primarily a placeholder since the actual review is submitted via the UI
        state.current_step = "review"
        return state
        
    def _extract_requested_errors(self, state: WorkflowState) -> List[Dict[str, Any]]:
        """
        Extract requested errors from the state with improved error handling and type safety.
        
        Args:
            state: Current workflow state
            
        Returns:
            List of requested errors
        """
        requested_errors = []
        
        # First check if code_snippet exists
        code_snippet = get_state_attribute(state, 'code_snippet', None)
        if not code_snippet:
            logger.warning("No code snippet in state for extracting requested errors")
            return requested_errors
        
        # Check if raw_errors exists and is a dictionary
        if hasattr(code_snippet, "raw_errors"):
            raw_errors = code_snippet.raw_errors
            
            # Type check for raw_errors
            if not isinstance(raw_errors, dict):
                logger.warning(f"Expected dict for raw_errors, got {type(raw_errors)}")
                return requested_errors
            
            # Extract errors from java_errors key
            java_errors = get_field_value(raw_errors, "java_errors", [])
            if not isinstance(java_errors, list):
                logger.warning(f"Expected list for java_errors, got {type(java_errors)}")
                return requested_errors
                
            # Process each error
            for error in java_errors:
                if not isinstance(error, dict):
                    logger.warning(f"Expected dict for error, got {type(error)}")
                    continue
                
                # Make sure the error has required fields
                if "type" not in error:
                    error["type"] = "java_error"  # Use a default type if not specified
                
                if "name" not in error and "error_name" in error:
                    error["name"] = error["error_name"]  # Use error_name as name if available
                
                if "name" not in error and "check_name" in error:
                    error["name"] = error["check_name"]  # Use check_name as name if available
                
                # Only add the error if it has a name
                if "name" in error:
                    requested_errors.append(error)
        
        # Alternative method: Check selected_specific_errors
        selected_specific_errors = get_state_attribute(state, 'selected_specific_errors', [])
        if not requested_errors and selected_specific_errors:
            # Check if it's a list
            if isinstance(selected_specific_errors, list):
                # Filter out non-dict entries
                for error in selected_specific_errors:
                    if isinstance(error, dict) and "name" in error and "type" in error:
                        requested_errors.append(error)
        
        # If we still don't have any errors, check selected_error_categories
        selected_error_categories = get_state_attribute(state, 'selected_error_categories', {})
        if not requested_errors and selected_error_categories:
            # Check if it's a dict
            if isinstance(selected_error_categories, dict):
                # This doesn't give us specific errors, but we can log that we found categories
                logger.info("Found selected_error_categories but no specific errors")
        
        logger.info(f"Extracted {len(requested_errors)} requested errors")
        return requested_errors
        
    def _log_selected_errors(self, selected_errors: List[Dict[str, Any]]) -> None:
        """
        Log detailed information about selected errors for debugging.
        
        Args:
            selected_errors: List of selected errors
        """
        if selected_errors:
            logger.debug("\n--- DETAILED ERROR LISTING ---")
            for i, error in enumerate(selected_errors, 1):
                logger.debug(f"  {i}. Type: {get_field_value(error, 'type', 'Unknown')}")
                logger.debug(f"     Name: {get_field_value(error, 'name', 'Unknown')}")
                logger.debug(f"     Category: {get_field_value(error, 'category', 'Unknown')}")
                logger.debug(f"     Description: {get_field_value(error, 'description', 'Unknown')}")
                implementation_guide = get_field_value(error, 'implementation_guide', '')
                if implementation_guide:
                    guide_display = implementation_guide[:100] + "..." if len(implementation_guide) > 100 else implementation_guide
                    logger.debug(f"     Implementation Guide: {guide_display}")