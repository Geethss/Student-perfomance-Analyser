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
        self.last_question_reasoning: List[Dict[str, Any]] = []
        self.last_mapping_notes: List[str] = []
    
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
    ) -> Dict[str, Any]:
        """
        Analyze question paper to map questions to concepts
        
        Args:
            question_paper_images: List of PIL Images of the question paper
            concepts: List of concept names to look for
            
        Returns:
            Dictionary containing:
                - "concept_map": Mapping of concept names to question numbers
                - "question_reasoning": Step-by-step reasoning per question
                - "evaluation_notes": Optional high-level reasoning notes
        """
        concepts_str = "\n".join([f"{i+1}. {concept}" for i, concept in enumerate(concepts)])
        
        prompt = f"""
        Analyze this question paper and identify which questions test which concepts.
        
        Here are the concepts to look for:
        {concepts_str}
        
        Instructions:
        1. For EACH concept, list ALL question numbers that require or test that concept.
        2. Every concept from the list must appear in the output, even if no questions map to it (use an empty list).
        3. For EVERY question in the paper, provide a short structured explanation of how you evaluated the question, including:
           - A one sentence summary of what the question is asking.
           - The concepts that apply to that question with a short rationale and a confidence rating (low/medium/high).
           - Optionally, any concepts you considered but rejected, with a short reason.
        4. Provide optional high-level evaluation notes capturing your overall reasoning steps.
        
        Return ONLY a valid JSON object with the following shape:
        {{
            "concept_map": {{
                "Concept Name": [question_numbers...],
                ...
            }},
            "question_reasoning": [
                {{
                    "question": <number>,
                    "summary": "<short description of the question>",
                    "concept_alignments": [
                        {{
                            "concept": "<concept name>",
                            "rationale": "<why this concept applies>",
                            "confidence": "low|medium|high"
                        }}
                    ],
                    "considered_but_rejected": [
                        {{
                            "concept": "<concept name>",
                            "reason": "<why it was rejected>"
                        }}
                    ]
                }}
            ],
            "evaluation_notes": [
                "<high-level note about your reasoning process>",
                ...
            ]
        }}
        
        Always return valid JSON only. Do not wrap the response in markdown code fences.
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
            
            concept_analysis = json.loads(response_text)
            
            # Ensure required keys exist
            if "concept_map" not in concept_analysis:
                raise ValueError("Response missing 'concept_map'")
            if not isinstance(concept_analysis["concept_map"], dict):
                raise ValueError("'concept_map' must be an object/dictionary")
            if "question_reasoning" not in concept_analysis:
                concept_analysis["question_reasoning"] = []
            if "evaluation_notes" not in concept_analysis:
                concept_analysis["evaluation_notes"] = []
            
            # Guarantee all concepts are present in the concept_map
            for concept in concepts:
                concept_analysis["concept_map"].setdefault(concept, [])
            
            # Store latest reasoning metadata for optional external access
            self.last_question_reasoning = concept_analysis["question_reasoning"]
            self.last_mapping_notes = concept_analysis["evaluation_notes"]
            
            return concept_analysis
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
            Dictionary containing:
                - 'mistakes': list of question numbers with mistakes
                - 'details': mapping of question number (as string) to mistake description
                - 'reasoning': structured reasoning steps per question (optional)
                - 'evaluation_notes': optional list of high-level observations
        """
        if not question_numbers:
            return {
                "mistakes": [],
                "details": {},
                "reasoning": [],
                "evaluation_notes": []
            }
        
        questions_str = ", ".join(map(str, question_numbers))
        
        prompt = f"""
        Analyze the student's performance for the concept: "{concept}"
        
        Questions that test this concept: {questions_str}
        
        Compare the student's answers (in the answer sheet) with the correct approach for each question.
        Focus specifically on how the student applied (or failed to apply) the concept: "{concept}".
        
        For each question, determine whether a mistake related to this concept occurred and describe the reasoning process.
        
        Return ONLY a valid JSON object with the following structure:
        {{
            "mistakes": [<question numbers where the student made a concept-related mistake>],
            "details": {{
                "<question number>": "<concise description of the mistake and what should have been done>"
            }},
            "reasoning": [
                {{
                    "question": <number>,
                    "observation": "<what you saw in the student's answer>",
                    "concept_evaluation": "<how the concept was (or should have been) applied>",
                    "conclusion": "<did they use the concept correctly or make a mistake?>",
                    "confidence": "low|medium|high"
                }}
            ],
            "evaluation_notes": [
                "<optional high-level note about the concept performance>"
            ]
        }}
        
        Use empty lists/objects where appropriate. Do not include markdown fences or explanatory text outside the JSON.
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
            
            if not isinstance(performance, dict):
                raise ValueError("Performance response must be a JSON object")
            performance.setdefault("mistakes", [])
            performance.setdefault("details", {})
            performance.setdefault("reasoning", [])
            performance.setdefault("evaluation_notes", [])
            
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
            List of dictionaries with concept analysis results. Each dictionary includes:
                - concept: Concept name
                - tested_count: Number of questions mapped to the concept
                - mistakes_count: Number of mistakes detected for the concept
                - mistake_questions: List of question numbers with mistakes
                - details: Dict mapping question numbers (str) to mistake descriptions
                - concept_reasoning: Structured reasoning for how each mapped question relates to the concept
                - performance_reasoning: Reasoning about the student's performance per question
                - performance_notes: Optional high-level notes about the student's performance
        """
        results = []
        
        # Step 1: Extract concepts
        if progress_callback:
            progress_callback("Extracting concepts from analysis sheet...")
        concepts = self.extract_concepts(analysis_sheet_images)
        
        # Step 2: Analyze question paper
        if progress_callback:
            progress_callback(f"Analyzing question paper for {len(concepts)} concepts...")
        concept_analysis = self.analyze_question_paper(question_paper_images, concepts)
        concept_questions = concept_analysis.get("concept_map", {})
        question_reasoning = concept_analysis.get("question_reasoning", [])
        
        # Step 3: Analyze student performance for each concept
        total_concepts = len(concepts)
        for idx, concept in enumerate(concepts):
            if progress_callback:
                progress_callback(f"Analyzing concept {idx+1}/{total_concepts}: {concept}")
            
            question_numbers_raw = concept_questions.get(concept, [])
            question_numbers: List[int] = []
            for number in question_numbers_raw:
                if isinstance(number, int):
                    question_numbers.append(number)
                elif isinstance(number, str) and number.strip().isdigit():
                    question_numbers.append(int(number.strip()))
                else:
                    question_numbers.append(number)
            
            concept_reasoning = self._extract_concept_reasoning(question_reasoning, concept)
            
            if not question_numbers:
                # Concept not tested
                results.append({
                    "concept": concept,
                    "tested_count": 0,
                    "mistakes_count": 0,
                    "mistake_questions": [],
                    "details": {},
                    "concept_reasoning": concept_reasoning,
                    "performance_reasoning": [],
                    "performance_notes": []
                })
            else:
                # Analyze performance
                performance = self.analyze_student_performance(
                    question_paper_images,
                    answer_sheet_images,
                    concept,
                    question_numbers
                )
                
                mistakes_raw = performance.get("mistakes", [])
                mistake_questions: List[int] = []
                for number in mistakes_raw:
                    if isinstance(number, int):
                        mistake_questions.append(number)
                    elif isinstance(number, str) and number.strip().isdigit():
                        mistake_questions.append(int(number.strip()))
                    else:
                        mistake_questions.append(number)
                
                results.append({
                    "concept": concept,
                    "tested_count": len(question_numbers),
                    "mistakes_count": len(mistake_questions),
                    "mistake_questions": mistake_questions,
                    "details": performance["details"],
                    "concept_reasoning": concept_reasoning,
                    "performance_reasoning": performance.get("reasoning", []),
                    "performance_notes": performance.get("evaluation_notes", [])
                })
            
            # Small delay to avoid rate limiting
            time.sleep(0.5)
        
        if progress_callback:
            progress_callback("Analysis complete!")
        
        return results
    
    @staticmethod
    def _extract_concept_reasoning(
        question_reasoning: List[Dict[str, Any]],
        concept: str
    ) -> List[Dict[str, Any]]:
        """
        Filter question-level reasoning down to the steps relevant to a specific concept.
        
        Args:
            question_reasoning: List of reasoning objects from analyze_question_paper
            concept: Concept name to filter for
        
        Returns:
            Filtered list of reasoning entries specific to the concept
        """
        filtered_reasoning: List[Dict[str, Any]] = []
        
        for entry in question_reasoning or []:
            concept_alignments = entry.get("concept_alignments", [])
            if not isinstance(concept_alignments, list):
                continue
            
            matching_alignments = [
                alignment for alignment in concept_alignments
                if isinstance(alignment, dict) and alignment.get("concept") == concept
            ]
            
            if not matching_alignments:
                continue
            
            question_number = entry.get("question")
            if isinstance(question_number, str) and question_number.strip().isdigit():
                question_number = int(question_number.strip())
            
            # Determine overall confidence for this question-concept pair
            confidence_levels = [a.get("confidence", "medium") for a in matching_alignments]
            if "high" in confidence_levels:
                overall_confidence = "high"
            elif "medium" in confidence_levels:
                overall_confidence = "medium"
            else:
                overall_confidence = "low"
            
            filtered_entry = {
                "question": question_number,
                "summary": entry.get("summary", ""),
                "concept_alignments": matching_alignments,
                "confidence": overall_confidence
            }
            
            if "considered_but_rejected" in entry:
                rejected = entry.get("considered_but_rejected", [])
                # Extract just the concept names for display
                if isinstance(rejected, list):
                    rejected_names = [
                        r.get("concept", "") if isinstance(r, dict) else str(r)
                        for r in rejected
                    ]
                    filtered_entry["considered_but_rejected"] = [r for r in rejected_names if r]
            
            filtered_reasoning.append(filtered_entry)
        
        return filtered_reasoning
    
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

