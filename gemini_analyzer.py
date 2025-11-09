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
    
    def identify_questions(self, question_paper_images: List[Image.Image]) -> List[int]:
        """
        Identify all question numbers in the question paper
        
        Args:
            question_paper_images: List of PIL Images of the question paper
            
        Returns:
            List of question numbers
        """
        prompt = """
        Analyze this question paper and identify all question numbers.
        
        Return ONLY a JSON array of question numbers (as integers), like this:
        [1, 2, 3, 4, 5, ...]
        
        List every single question number you can find in the paper.
        Return ONLY the JSON array, nothing else.
        """
        
        try:
            response = self.model.generate_content(
                [prompt] + question_paper_images,
                generation_config=self.generation_config
            )
            
            # Parse the JSON response
            response_text = response.text.strip()
            # Remove markdown code blocks if present
            if response_text.startswith("```json"):
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif response_text.startswith("```"):
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            question_numbers = json.loads(response_text)
            return question_numbers
        except Exception as e:
            raise ValueError(f"Error identifying questions: {str(e)}")
    
    def analyze_single_question(
        self,
        question_paper_images: List[Image.Image],
        answer_sheet_images: List[Image.Image],
        question_number: int
    ) -> Dict[str, Any]:
        """
        Analyze a single question: extract question text, Gemini's solution,
        student's answer, and identify mistakes
        
        Args:
            question_paper_images: List of PIL Images of the question paper
            answer_sheet_images: List of PIL Images of the answer sheet
            question_number: The question number to analyze
            
        Returns:
            Dictionary containing:
                - 'question_number': The question number
                - 'question_text': Extracted question text
                - 'gemini_solution': How Gemini solves the question (step-by-step)
                - 'student_answer': The student's answer/approach
                - 'has_mistake': Boolean indicating if there's a mistake
                - 'mistake_description': Description of the mistake (if any)
        """
        prompt = f"""
        Analyze Question {question_number} from the question paper and the student's answer to it.
        
        Please provide a comprehensive analysis with the following components:
        
        1. **Question Text**: Extract and write out the complete text of Question {question_number}.
           - Include all mathematical expressions exactly as written
           - Preserve the mathematical notation
        
        2. **Gemini's Solution**: Provide a detailed step-by-step solution showing how to correctly solve this question.
           - Be clear, thorough, and pedagogical in your explanation
           - Put each mathematical equation or formula on a NEW LINE
           - Use proper mathematical notation
           - Format each step clearly with line breaks between equations
           - Example format:
             Step 1: Apply the power rule for integration
             
             ∫ x² dx = x^(2+1)/(2+1) + C
             
             Step 2: Simplify
             
             = x³/3 + C
        
        3. **Student's Answer**: Extract and describe what the student wrote for Question {question_number} in the answer sheet.
           - Include their approach, steps, and final answer
           - Show any equations they wrote on separate lines
           - Preserve mathematical notation exactly as written
        
        4. **Evaluation**: Compare the student's answer with the correct solution and determine:
           - Is there a mistake? (yes/no)
           - If yes, what exactly is the mistake? Be specific about what they did wrong and what they should have done.
           - If no, confirm that their answer is correct.
        
        IMPORTANT FORMATTING RULES:
        - Each mathematical equation should be on its own line
        - Add line breaks (\\n) between steps and equations
        - Preserve mathematical symbols: ∫, ², ³, √, π, etc.
        
        Return ONLY a valid JSON object with this exact structure:
        {{
            "question_number": {question_number},
            "question_text": "<complete question text with equations on separate lines>",
            "gemini_solution": "<detailed step-by-step solution with each equation on a new line>",
            "student_answer": "<student's answer with equations on separate lines>",
            "has_mistake": true or false,
            "mistake_description": "<detailed description of mistake, or 'No mistakes' if correct>"
        }}
        
        Do not include markdown code fences. Return only valid JSON.
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
            
            analysis = json.loads(response_text)
            
            # Validate required fields
            required_fields = ["question_number", "question_text", "gemini_solution", 
                             "student_answer", "has_mistake", "mistake_description"]
            for field in required_fields:
                if field not in analysis:
                    analysis[field] = f"<{field} not available>"
            
            # Ensure has_mistake is boolean
            if not isinstance(analysis["has_mistake"], bool):
                analysis["has_mistake"] = str(analysis["has_mistake"]).lower() in ["true", "yes", "1"]
            
            return analysis
        except Exception as e:
            # Return a fallback structure if parsing fails
            return {
                "question_number": question_number,
                "question_text": f"Error extracting question {question_number}",
                "gemini_solution": f"Error generating solution: {str(e)}",
                "student_answer": "Error extracting student answer",
                "has_mistake": False,
                "mistake_description": f"Error during analysis: {str(e)}"
            }
    
    def analyze_questions_and_answers(
        self,
        question_paper_images: List[Image.Image],
        answer_sheet_images: List[Image.Image],
        progress_callback=None
    ) -> List[Dict[str, Any]]:
        """
        Perform complete analysis for all questions in the paper
        
        Args:
            question_paper_images: Images of the question paper
            answer_sheet_images: Images of the answer sheet
            progress_callback: Optional callback function for progress updates
            
        Returns:
            List of dictionaries with analysis results for each question
        """
        results = []
        
        # Step 1: Identify all questions
        if progress_callback:
            progress_callback("Identifying questions in the paper...")
        question_numbers = self.identify_questions(question_paper_images)
        
        if not question_numbers:
            raise ValueError("No questions found in the question paper")
        
        # Step 2: Analyze each question
        total_questions = len(question_numbers)
        for idx, question_num in enumerate(question_numbers):
            if progress_callback:
                progress_callback(f"Analyzing question {idx+1}/{total_questions} (Question #{question_num})...")
            
            analysis = self.analyze_single_question(
                question_paper_images,
                answer_sheet_images,
                question_num
            )
            
            results.append(analysis)
            
            # Small delay to avoid rate limiting
            time.sleep(0.5)
        
        if progress_callback:
            progress_callback("Analysis complete!")
        
        return results
