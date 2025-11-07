"""
Gemini AI Integration Module
Handles all interactions with Google's Gemini AI API for document analysis
"""

import google.generativeai as genai
from typing import List, Dict, Any, Optional
import json
import time
from PIL import Image


class GeminiAnalyzer:
    """Analyze student performance using Google Gemini AI"""
    
    def __init__(self, api_key: str, model_name: str = "gemini-2.5-pro"):
        """
        Initialize Gemini Analyzer
        
        Args:
            api_key: Google Gemini API key
            model_name: Name of the Gemini model to use
        """
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)
        self.generation_config = {
            "temperature": 0.2,  # Lower temperature for more consistent results
            "top_p": 0.8,
            "top_k": 40,
            "max_output_tokens": 8192,
        }
    
    def extract_concepts(self, analysis_sheet_images: List[Image.Image]) -> List[str]:
        """
        Extract concepts from the analysis sheet
        
        Args:
            analysis_sheet_images: List of PIL Images of the analysis sheet
            
        Returns:
            List of concept names
        """
        prompt = """
        Analyze this analysis sheet and extract ALL concepts listed in the "Concept (With Explanation)" column.
        
        Return ONLY a JSON array of concept names, like this:
        ["Basic Formulas", "Application of Formulae", "Basic Trigonometric Ratios Integration", ...]
        
        Extract every single concept from the sheet. Be thorough and precise.
        Return ONLY the JSON array, nothing else.
        """
        
        try:
            response = self.model.generate_content(
                [prompt] + analysis_sheet_images,
                generation_config=self.generation_config
            )
            
            # Parse the JSON response
            response_text = response.text.strip()
            # Remove markdown code blocks if present
            if response_text.startswith("```json"):
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif response_text.startswith("```"):
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            concepts = json.loads(response_text)
            return concepts
        except Exception as e:
            raise ValueError(f"Error extracting concepts: {str(e)}")
    
    def analyze_question_paper(
        self, 
        question_paper_images: List[Image.Image],
        concepts: List[str]
    ) -> Dict[str, List[int]]:
        """
        Analyze question paper to map questions to concepts
        
        Args:
            question_paper_images: List of PIL Images of the question paper
            concepts: List of concept names to look for
            
        Returns:
            Dictionary mapping concept names to list of question numbers
        """
        concepts_str = "\n".join([f"{i+1}. {concept}" for i, concept in enumerate(concepts)])
        
        prompt = f"""
        Analyze this question paper and identify which questions test which concepts.
        
        Here are the concepts to look for:
        {concepts_str}
        
        For each concept, identify ALL question numbers that test or require that concept.
        A single question may test multiple concepts.
        
        Return your analysis as a JSON object where keys are concept names and values are arrays of question numbers:
        {{
            "Basic Formulas": [1, 3, 5],
            "Application of Formulae": [2, 4, 6, 8],
            ...
        }}
        
        Include ALL concepts from the list, even if no questions test them (use empty array []).
        Be thorough - analyze every question carefully.
        Return ONLY the JSON object, nothing else.
        """
        
        try:
            response = self.model.generate_content(
                [prompt] + question_paper_images,
                generation_config=self.generation_config
            )
            
            # Parse the JSON response
            response_text = response.text.strip()
            if response_text.startswith("```json"):
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif response_text.startswith("```"):
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            concept_questions = json.loads(response_text)
            return concept_questions
        except Exception as e:
            raise ValueError(f"Error analyzing question paper: {str(e)}")
    
    def analyze_student_performance(
        self,
        question_paper_images: List[Image.Image],
        answer_sheet_images: List[Image.Image],
        concept: str,
        question_numbers: List[int]
    ) -> Dict[str, Any]:
        """
        Analyze student's performance for a specific concept
        
        Args:
            question_paper_images: List of PIL Images of the question paper
            answer_sheet_images: List of PIL Images of the answer sheet
            concept: Name of the concept to analyze
            question_numbers: List of question numbers that test this concept
            
        Returns:
            Dictionary with 'mistakes' (list of Q numbers) and 'details' (dict of Q: error description)
        """
        if not question_numbers:
            return {
                "mistakes": [],
                "details": {}
            }
        
        questions_str = ", ".join(map(str, question_numbers))
        
        prompt = f"""
        Analyze the student's performance for the concept: "{concept}"
        
        Questions that test this concept: {questions_str}
        
        Compare the student's answers (in the answer sheet) with the correct approach for each question.
        Specifically focus on how the student applied (or failed to apply) the concept: "{concept}"
        
        For each question:
        1. Did the student make a mistake related to this concept?
        2. If yes, what exactly was the mistake?
        
        Return your analysis as a JSON object:
        {{
            "mistakes": [2, 5, 8],  // Question numbers where mistakes were made
            "details": {{
                "2": "Wrong integration of tan²x - forgot to use substitution",
                "5": "Incorrect formula application - used wrong power rule",
                "8": "Failed to apply chain rule during integration"
            }}
        }}
        
        Be specific about the mistakes. Only include questions where the student made errors related to "{concept}".
        If no mistakes were made, return empty arrays/objects.
        Return ONLY the JSON object, nothing else.
        """
        
        try:
            # Combine all images for context
            all_images = question_paper_images + answer_sheet_images
            
            response = self.model.generate_content(
                [prompt] + all_images,
                generation_config=self.generation_config
            )
            
            # Parse the JSON response
            response_text = response.text.strip()
            if response_text.startswith("```json"):
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif response_text.startswith("```"):
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            performance = json.loads(response_text)
            return performance
        except Exception as e:
            raise ValueError(f"Error analyzing student performance for {concept}: {str(e)}")
    
    def analyze_all_concepts(
        self,
        analysis_sheet_images: List[Image.Image],
        question_paper_images: List[Image.Image],
        answer_sheet_images: List[Image.Image],
        progress_callback=None
    ) -> List[Dict[str, Any]]:
        """
        Perform complete analysis for all concepts
        
        Args:
            analysis_sheet_images: Images of the analysis sheet
            question_paper_images: Images of the question paper
            answer_sheet_images: Images of the answer sheet
            progress_callback: Optional callback function for progress updates
            
        Returns:
            List of dictionaries with concept analysis results
        """
        results = []
        
        # Step 1: Extract concepts
        if progress_callback:
            progress_callback("Extracting concepts from analysis sheet...")
        concepts = self.extract_concepts(analysis_sheet_images)
        
        # Step 2: Analyze question paper
        if progress_callback:
            progress_callback(f"Analyzing question paper for {len(concepts)} concepts...")
        concept_questions = self.analyze_question_paper(question_paper_images, concepts)
        
        # Step 3: Analyze student performance for each concept
        total_concepts = len(concepts)
        for idx, concept in enumerate(concepts):
            if progress_callback:
                progress_callback(f"Analyzing concept {idx+1}/{total_concepts}: {concept}")
            
            question_numbers = concept_questions.get(concept, [])
            
            if not question_numbers:
                # Concept not tested
                results.append({
                    "concept": concept,
                    "tested_count": 0,
                    "mistakes_count": 0,
                    "mistake_questions": [],
                    "details": {}
                })
            else:
                # Analyze performance
                performance = self.analyze_student_performance(
                    question_paper_images,
                    answer_sheet_images,
                    concept,
                    question_numbers
                )
                
                results.append({
                    "concept": concept,
                    "tested_count": len(question_numbers),
                    "mistakes_count": len(performance["mistakes"]),
                    "mistake_questions": performance["mistakes"],
                    "details": performance["details"]
                })
            
            # Small delay to avoid rate limiting
            time.sleep(0.5)
        
        if progress_callback:
            progress_callback("Analysis complete!")
        
        return results
    
    @staticmethod
    def format_response_1(result: Dict[str, Any]) -> str:
        """
        Format Response 1 (summary statistics)
        
        Args:
            result: Analysis result dictionary
            
        Returns:
            Formatted string for Response 1
        """
        tested = result["tested_count"]
        mistakes = result["mistakes_count"]
        
        if tested == 0:
            return "Not tested in this paper"
        
        if mistakes == 0:
            return f"Tested {tested} times - No mistakes"
        
        questions = ", ".join(map(str, result["mistake_questions"]))
        return f"Tested {tested} times - Mistakes {mistakes} times (Q.No {questions})"
    
    @staticmethod
    def format_response_2(result: Dict[str, Any]) -> str:
        """
        Format Response 2 (detailed mistake analysis)
        
        Args:
            result: Analysis result dictionary
            
        Returns:
            Formatted string for Response 2
        """
        if not result["details"]:
            return "No detailed analysis needed (no mistakes)"
        
        details_list = []
        for q_num in sorted(result["mistake_questions"]):
            detail = result["details"].get(str(q_num), "Error not specified")
            details_list.append(f"Q{q_num}: {detail}")
        
        return "\n".join(details_list)

