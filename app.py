"""
Student Performance Analyzer - Streamlit Application
Main application file for the student performance analysis system
"""

import streamlit as st
import os
from dotenv import load_dotenv
from document_processor import DocumentProcessor
from gemini_analyzer import GeminiAnalyzer
from report_generator import ReportGenerator
import traceback

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Student Performance Analyzer",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #366092;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .upload-section {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .error-box {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    /* Better formatting for mathematical content */
    .stMarkdown p {
        white-space: pre-wrap;
        line-height: 1.8;
    }
    /* Ensure equations are displayed clearly */
    code {
        font-family: 'Courier New', monospace;
        background-color: #f5f5f5;
        padding: 2px 4px;
        border-radius: 3px;
    }
    </style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables"""
    if 'analysis_complete' not in st.session_state:
        st.session_state.analysis_complete = False
    if 'results' not in st.session_state:
        st.session_state.results = None
    if 'excel_data' not in st.session_state:
        st.session_state.excel_data = None
    if 'pdf_data' not in st.session_state:
        st.session_state.pdf_data = None

def main():
    """Main application function"""
    initialize_session_state()
    
    # Header
    st.markdown('<div class="main-header">Student Performance Analyzer</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">AI-Powered Question-by-Question Performance Analysis</div>', unsafe_allow_html=True)
    
    # Sidebar for Configuration
    with st.sidebar:
        st.header("Configuration")
        
        # Model selection
        model_choice = st.selectbox(
            "Select Gemini Model",
            ["gemini-2.5-pro", "gemini-2.5-flash", "gemini-2.0-flash-exp"],
            index=0,
            help="Choose the Gemini model for analysis"
        )
        
        # Get API key from environment
        api_key = os.getenv("GOOGLE_API_KEY", "")
        
        st.markdown("---")
        st.markdown("### Instructions")
        st.markdown("""
        1. Upload question paper and answer sheet (can upload multiple images per document)
        2. Click 'Analyze Performance'
        3. Review each question's analysis
        4. Download the reports
        """)
        
        st.markdown("---")
        st.markdown("### About")
        st.markdown("""
        This tool analyzes student performance by:
        - Extracting questions from the question paper
        - Showing Gemini's solution approach
        - Comparing with student's answers
        - Identifying and explaining mistakes
        """)
    
    # Main content area
    st.markdown("### Upload Documents")
    
    # File uploaders in columns (only 2 now)
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="upload-section">', unsafe_allow_html=True)
        st.markdown("**Question Paper**")
        st.caption("Upload the exam questions (can upload multiple files)")
        question_papers = st.file_uploader(
            "Question Paper",
            type=["png", "jpg", "jpeg", "pdf"],
            key="question_paper",
            label_visibility="collapsed",
            accept_multiple_files=True
        )
        if question_papers:
            st.success(f"{len(question_papers)} file(s) uploaded")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="upload-section">', unsafe_allow_html=True)
        st.markdown("**Answer Sheet**")
        st.caption("Upload student's solutions (can upload multiple files)")
        answer_sheets = st.file_uploader(
            "Answer Sheet",
            type=["png", "jpg", "jpeg", "pdf"],
            key="answer_sheet",
            label_visibility="collapsed",
            accept_multiple_files=True
        )
        if answer_sheets:
            st.success(f"{len(answer_sheets)} file(s) uploaded")
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Analyze button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        analyze_button = st.button(
            "Analyze Performance",
            use_container_width=True,
            type="primary"
        )
    
    # Process analysis
    if analyze_button:
        # Validation
        if not api_key:
            st.error("Error: Google Gemini API key not found. Please set GOOGLE_API_KEY environment variable.")
            return
        
        if not all([question_papers, answer_sheets]):
            st.error("Error: Please upload both question paper and answer sheet")
            return
        
        try:
            # Create progress container
            progress_container = st.container()
            
            with progress_container:
                st.info("Starting analysis...")
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # Initialize document processor
                processor = DocumentProcessor()
                
                # Process documents (handle multiple files)
                status_text.text("Processing documents...")
                progress_bar.progress(10)
                
                question_images = []
                for file in question_papers:
                    question_images.extend(processor.process_uploaded_file(file))
                progress_bar.progress(30)
                
                answer_images = []
                for file in answer_sheets:
                    answer_images.extend(processor.process_uploaded_file(file))
                progress_bar.progress(50)
                
                status_text.text("Documents processed successfully")
                
                # Initialize Gemini analyzer
                status_text.text("Initializing AI model...")
                analyzer = GeminiAnalyzer(api_key, model_name=model_choice)
                progress_bar.progress(60)
                
                # Define progress callback
                def update_progress(message):
                    status_text.text(f"{message}")
                
                # Perform analysis
                status_text.text("Analyzing questions and answers (this may take a few minutes)...")
                results = analyzer.analyze_questions_and_answers(
                    question_images,
                    answer_images,
                    progress_callback=update_progress
                )
                progress_bar.progress(90)
                
                # Generate reports
                status_text.text("Generating reports...")
                excel_data, _ = ReportGenerator.create_downloadable_excel(results)
                pdf_data, _ = ReportGenerator.create_downloadable_pdf(results)
                progress_bar.progress(100)
                
                # Store results in session state
                st.session_state.results = results
                st.session_state.excel_data = excel_data
                st.session_state.pdf_data = pdf_data
                st.session_state.analysis_complete = True
                
                status_text.text("Analysis complete!")
                
            st.success("Analysis completed successfully!")
            
        except Exception as e:
            st.error(f"An error occurred during analysis:")
            st.error(str(e))
            with st.expander("Show error details"):
                st.code(traceback.format_exc())
            return
    
    # Display results if analysis is complete
    if st.session_state.analysis_complete and st.session_state.results:
        st.markdown("---")
        st.markdown("### Analysis Results")
        
        # Summary statistics
        results = st.session_state.results
        total_questions = len(results)
        questions_with_mistakes = sum(1 for r in results if r.get("has_mistake", False))
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Questions Analyzed", total_questions)
        with col2:
            st.metric("Questions with Mistakes", questions_with_mistakes)
        
        # Detailed results for each question
        st.markdown("### Question-by-Question Analysis")
        
        for idx, result in enumerate(results, 1):
            question_num = result.get("question_number", idx)
            has_mistake = result.get("has_mistake", False)
            
            # Color-code the expander based on whether there's a mistake
            status_text = "Mistake Found" if has_mistake else "Correct"
            
            with st.expander(f"Question {question_num} - {status_text}"):
                # 1. Display the Question
                st.markdown("### 1. Question")
                question_text = result.get("question_text", "Question text not extracted")
                st.markdown("---")
                st.write(question_text)
                
                st.markdown("---")
                
                # 2. Show how Gemini solves it
                st.markdown("### 2. How Gemini Solves This")
                st.markdown("---")
                gemini_solution = result.get("gemini_solution", "Solution not available")
                # Display solution with proper line breaks for equations
                st.write(gemini_solution)
                
                st.markdown("---")
                
                # 3. Show the student's answer
                st.markdown("### 3. Student's Answer")
                st.markdown("---")
                student_answer = result.get("student_answer", "Student answer not extracted")
                st.write(student_answer)
                
                st.markdown("---")
                
                # 4. Show the mistake (if any)
                st.markdown("### 4. Mistake Done")
                st.markdown("---")
                if has_mistake:
                    mistake_description = result.get("mistake_description", "Mistake detected but not described")
                    st.error(f"**Mistake:** {mistake_description}")
                else:
                    st.success("**No mistakes found.** The student's answer is correct!")
        
        # Download buttons
        st.markdown("---")
        st.markdown("### Download Reports")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.download_button(
                label="Download Excel Report",
                data=st.session_state.excel_data,
                file_name="student_performance_analysis.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        
        with col2:
            st.download_button(
                label="Download PDF Report",
                data=st.session_state.pdf_data,
                file_name="student_performance_analysis.pdf",
                mime="application/pdf",
                use_container_width=True
            )

if __name__ == "__main__":
    main()

