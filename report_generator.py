"""
Report Generation Module
Generates Excel and PDF reports from analysis results
"""

import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, Border, Side, PatternFill
from openpyxl.utils import get_column_letter
from fpdf import FPDF
import io
from typing import List, Dict, Any
from datetime import datetime
import unicodedata
import re


class ReportGenerator:
    """Generate formatted reports in Excel and PDF formats"""
    
    @staticmethod
    def sanitize_for_pdf(text: str) -> str:
        """
        Sanitize text for PDF output by replacing/removing Unicode characters
        that aren't supported by standard PDF fonts
        
        Args:
            text: Input text that may contain Unicode characters
            
        Returns:
            Sanitized text safe for PDF rendering
        """
        # Common mathematical symbol replacements
        replacements = {
            '∫': 'integral',
            '∑': 'sum',
            '∏': 'product',
            '√': 'sqrt',
            '∞': 'infinity',
            '≈': '~',
            '≠': '!=',
            '≤': '<=',
            '≥': '>=',
            '°': ' degrees',
            'π': 'pi',
            'θ': 'theta',
            'α': 'alpha',
            'β': 'beta',
            'γ': 'gamma',
            'δ': 'delta',
            'λ': 'lambda',
            'μ': 'mu',
            'σ': 'sigma',
            'φ': 'phi',
            'ψ': 'psi',
            'ω': 'omega',
            '²': '^2',
            '³': '^3',
            '¹': '^1',
            '⁴': '^4',
            '⁵': '^5',
            '⁶': '^6',
            '⁷': '^7',
            '⁸': '^8',
            '⁹': '^9',
            '⁰': '^0',
            '×': 'x',
            '÷': '/',
            '±': '+/-',
            '→': '->',
            '←': '<-',
            '↔': '<->',
            '•': '*',
            '·': '.',
        }
        
        # Apply replacements
        for unicode_char, ascii_equiv in replacements.items():
            text = text.replace(unicode_char, ascii_equiv)
        
        # Try to convert remaining Unicode to ASCII
        try:
            # Normalize to decomposed form and remove combining characters
            text = unicodedata.normalize('NFKD', text)
            text = text.encode('ascii', 'ignore').decode('ascii')
        except:
            # If all else fails, remove non-ASCII characters
            text = re.sub(r'[^\x00-\x7F]+', '', text)
        
        return text
    
    @staticmethod
    def generate_excel(results: List[Dict[str, Any]]) -> bytes:
        """
        Generate Excel report with formatted concept analysis
        
        Args:
            results: List of analysis results for each concept
            
        Returns:
            Excel file as bytes
        """
        # Create workbook
        wb = Workbook()
        ws = wb.active
        ws.title = "Performance Analysis"
        
        # Define styles
        header_font = Font(bold=True, size=12, color="FFFFFF")
        header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
        header_alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        
        cell_alignment = Alignment(vertical="top", wrap_text=True)
        border = Border(
            left=Side(style='thin'),
            right=Side(style='thin'),
            top=Side(style='thin'),
            bottom=Side(style='thin')
        )
        
        # Set column widths
        ws.column_dimensions['A'].width = 10
        ws.column_dimensions['B'].width = 40
        ws.column_dimensions['C'].width = 30
        ws.column_dimensions['D'].width = 60
        ws.column_dimensions['E'].width = 70
        
        # Write headers
        headers = ["Concept No.", "Concept (With Explanation)", "Example", "Status", "AI Evaluation Process"]
        for col_num, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col_num, value=header)
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = header_alignment
            cell.border = border
        
        # Write data
        for idx, result in enumerate(results, 2):
            # Concept Number
            cell = ws.cell(row=idx, column=1, value=idx-1)
            cell.alignment = Alignment(horizontal="center", vertical="top")
            cell.border = border
            
            # Concept Name
            cell = ws.cell(row=idx, column=2, value=result["concept"])
            cell.alignment = cell_alignment
            cell.border = border
            
            # Example (empty for now - could be filled from original sheet)
            cell = ws.cell(row=idx, column=3, value="")
            cell.alignment = cell_alignment
            cell.border = border
            
            # Status (Response 1 + Response 2)
            response_1 = ReportGenerator._format_response_1(result)
            response_2 = ReportGenerator._format_response_2(result)
            status_text = f"{response_1}\n\n{response_2}"
            
            cell = ws.cell(row=idx, column=4, value=status_text)
            cell.alignment = cell_alignment
            cell.border = border
            
            # AI Evaluation Process
            evaluation_text = ReportGenerator._format_evaluation_process(result)
            cell = ws.cell(row=idx, column=5, value=evaluation_text)
            cell.alignment = cell_alignment
            cell.border = border
            
            # Set row height based on content
            total_lines = max(len(status_text.split('\n')), len(evaluation_text.split('\n')))
            ws.row_dimensions[idx].height = max(60, total_lines * 15)
        
        # Freeze header row
        ws.freeze_panes = "A2"
        
        # Save to bytes
        excel_buffer = io.BytesIO()
        wb.save(excel_buffer)
        excel_buffer.seek(0)
        
        return excel_buffer.getvalue()
    
    @staticmethod
    def generate_pdf(results: List[Dict[str, Any]]) -> bytes:
        """
        Generate PDF report with formatted concept analysis
        
        Args:
            results: List of analysis results for each concept
            
        Returns:
            PDF file as bytes
        """
        pdf = FPDF()
        pdf.set_margins(left=15, top=15, right=15)
        pdf.set_auto_page_break(auto=True, margin=15)
        
        # Title page
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 16)
        pdf.cell(0, 20, "Student Performance Analysis Report", ln=True, align="C")
        
        pdf.set_font("Helvetica", "", 12)
        pdf.cell(0, 10, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True, align="C")
        pdf.ln(10)
        
        # Summary statistics
        total_concepts = len(results)
        tested_concepts = sum(1 for r in results if r["tested_count"] > 0)
        total_mistakes = sum(r["mistakes_count"] for r in results)
        
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 10, "Summary", ln=True)
        pdf.set_font("Helvetica", "", 10)
        pdf.cell(0, 7, f"Total Concepts: {total_concepts}", ln=True)
        pdf.cell(0, 7, f"Concepts Tested: {tested_concepts}", ln=True)
        pdf.cell(0, 7, f"Total Mistakes: {total_mistakes}", ln=True)
        pdf.ln(5)
        
        # Detailed analysis for each concept
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 10, "Detailed Analysis", ln=True)
        pdf.ln(5)
        
        for idx, result in enumerate(results, 1):
            # Concept header
            pdf.set_font("Helvetica", "B", 11)
            pdf.set_fill_color(54, 96, 146)
            pdf.set_text_color(255, 255, 255)
            concept_text = ReportGenerator.sanitize_for_pdf(f"{idx}. {result['concept']}")
            pdf.cell(0, 8, concept_text, ln=True, fill=True)
            pdf.set_text_color(0, 0, 0)
            
            # Response 1
            pdf.set_font("Helvetica", "B", 10)
            pdf.cell(0, 6, "Performance Summary:", ln=True)
            pdf.set_font("Helvetica", "", 10)
            response_1 = ReportGenerator._format_response_1(result)
            response_1 = ReportGenerator.sanitize_for_pdf(response_1)
            pdf.multi_cell(0, 5, response_1)
            
            # Response 2
            if result["mistakes_count"] > 0:
                pdf.set_font("Helvetica", "B", 10)
                pdf.cell(0, 6, "Detailed Mistake Analysis:", ln=True)
                pdf.set_font("Helvetica", "", 10)
                response_2 = ReportGenerator._format_response_2(result)
                response_2 = ReportGenerator.sanitize_for_pdf(response_2)
                pdf.multi_cell(0, 5, response_2)
            
            # AI Evaluation Process
            evaluation_text = ReportGenerator._format_evaluation_process(result)
            if evaluation_text and evaluation_text != "No evaluation data available":
                pdf.set_font("Helvetica", "B", 10)
                pdf.cell(0, 6, "AI Evaluation Process:", ln=True)
                pdf.set_font("Helvetica", "", 9)
                evaluation_text = ReportGenerator.sanitize_for_pdf(evaluation_text)
                pdf.multi_cell(0, 4, evaluation_text)
            
            pdf.ln(5)
            
            # Page break if needed
            if pdf.get_y() > 250:
                pdf.add_page()
        
        # Return PDF as bytes
        return bytes(pdf.output())
    
    @staticmethod
    def _format_response_1(result: Dict[str, Any]) -> str:
        """Format Response 1 text"""
        tested = result["tested_count"]
        mistakes = result["mistakes_count"]
        
        if tested == 0:
            return "Not tested in this paper"
        
        if mistakes == 0:
            return f"Tested {tested} times - No mistakes"
        
        questions = ", ".join(map(str, result["mistake_questions"]))
        return f"Tested {tested} times - Mistakes {mistakes} times (Q.No {questions})"
    
    @staticmethod
    def _format_response_2(result: Dict[str, Any]) -> str:
        """Format Response 2 text"""
        if not result["details"]:
            return "No mistakes found"
        
        details_list = []
        for q_num in sorted(result["mistake_questions"]):
            detail = result["details"].get(str(q_num), "Error not specified")
            details_list.append(f"  - Q{q_num}: {detail}")
        
        return "\n".join(details_list)
    
    @staticmethod
    def _format_evaluation_process(result: Dict[str, Any]) -> str:
        """Format AI evaluation process showing how Gemini analyzed the concept"""
        sections = []
        
        # Section 1: How questions were mapped to this concept
        concept_reasoning = result.get("concept_reasoning", [])
        if concept_reasoning:
            sections.append("=== QUESTION-TO-CONCEPT MAPPING ===")
            for reasoning in concept_reasoning:
                q_num = reasoning.get("question", "?")
                summary = reasoning.get("summary", "N/A")
                confidence = reasoning.get("confidence", "medium").upper()
                
                sections.append(f"\nQuestion {q_num} [{confidence} CONFIDENCE]:")
                sections.append(f"  Summary: {summary}")
                
                # Show concept alignments
                alignments = reasoning.get("concept_alignments", [])
                for alignment in alignments:
                    if alignment.get("concept") == result["concept"]:
                        sections.append(f"  Rationale: {alignment.get('rationale', 'N/A')}")
                
                # Show rejected concepts
                rejected = reasoning.get("considered_but_rejected", [])
                if rejected:
                    sections.append(f"  Also considered: {', '.join(rejected)}")
        
        # Section 2: How student performance was evaluated
        performance_reasoning = result.get("performance_reasoning", [])
        if performance_reasoning:
            if sections:
                sections.append("\n")
            sections.append("=== STUDENT ANSWER EVALUATION ===")
            for perf in performance_reasoning:
                q_num = perf.get("question", "?")
                observation = perf.get("observation", "N/A")
                concept_eval = perf.get("concept_evaluation", "N/A")
                conclusion = perf.get("conclusion", "N/A")
                confidence = perf.get("confidence", "medium").upper()
                
                sections.append(f"\nQuestion {q_num} [{confidence} CONFIDENCE]:")
                sections.append(f"  Observation: {observation}")
                sections.append(f"  Concept Application: {concept_eval}")
                sections.append(f"  Conclusion: {conclusion}")
        
        # Section 3: Additional notes
        performance_notes = result.get("performance_notes", [])
        if performance_notes:
            if sections:
                sections.append("\n")
            sections.append("=== EVALUATION NOTES ===")
            for note in performance_notes:
                sections.append(f"  - {note}")
        
        return "\n".join(sections) if sections else "No evaluation data available"
    
    @staticmethod
    def create_downloadable_excel(results: List[Dict[str, Any]], filename: str = "analysis_report.xlsx") -> tuple:
        """
        Create downloadable Excel file for Streamlit
        
        Args:
            results: Analysis results
            filename: Output filename
            
        Returns:
            Tuple of (file_bytes, filename)
        """
        excel_bytes = ReportGenerator.generate_excel(results)
        return excel_bytes, filename
    
    @staticmethod
    def create_downloadable_pdf(results: List[Dict[str, Any]], filename: str = "analysis_report.pdf") -> tuple:
        """
        Create downloadable PDF file for Streamlit
        
        Args:
            results: Analysis results
            filename: Output filename
            
        Returns:
            Tuple of (file_bytes, filename)
        """
        pdf_bytes = ReportGenerator.generate_pdf(results)
        return pdf_bytes, filename

