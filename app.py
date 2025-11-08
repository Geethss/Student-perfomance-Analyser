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
    st.markdown('<div class="sub-header">AI-Powered Concept-Wise Performance Analysis</div>', unsafe_allow_html=True)
    
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
        1. Upload all required files (can upload multiple images per document)
        2. Click 'Analyze Performance'
        3. Download the reports
        """)
        
        st.markdown("---")
        st.markdown("### About")
        st.markdown("""
        This tool analyzes student performance by:
        - Extracting concepts from analysis sheet
        - Mapping questions to concepts
        - Identifying mistakes in answers
        - Generating detailed reports
        """)
    
    # Main content area
    st.markdown("### Upload Documents")
    
    # File uploaders in columns
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="upload-section">', unsafe_allow_html=True)
        st.markdown("**Analysis Sheet**")
        st.caption("Upload the concept list (can upload multiple files)")
        analysis_sheets = st.file_uploader(
            "Analysis Sheet",
            type=["png", "jpg", "jpeg", "pdf"],
            key="analysis_sheet",
            label_visibility="collapsed",
            accept_multiple_files=True
        )
        if analysis_sheets:
            st.success(f"{len(analysis_sheets)} file(s) uploaded")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
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
    
    with col3:
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
        
        if not all([analysis_sheets, question_papers, answer_sheets]):
            st.error("Error: Please upload all three required documents")
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
                
                analysis_images = []
                for file in analysis_sheets:
                    analysis_images.extend(processor.process_uploaded_file(file))
                progress_bar.progress(20)
                
                question_images = []
                for file in question_papers:
                    question_images.extend(processor.process_uploaded_file(file))
                progress_bar.progress(30)
                
                answer_images = []
                for file in answer_sheets:
                    answer_images.extend(processor.process_uploaded_file(file))
                progress_bar.progress(40)
                
                status_text.text("Documents processed successfully")
                
                # Initialize Gemini analyzer
                status_text.text("Initializing AI model...")
                analyzer = GeminiAnalyzer(api_key, model_name=model_choice)
                progress_bar.progress(50)
                
                # Define progress callback
                def update_progress(message):
                    status_text.text(f"{message}")
                
                # Perform analysis
                status_text.text("Analyzing performance (this may take a few minutes)...")
                results = analyzer.analyze_all_concepts(
                    analysis_images,
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
        total_concepts = len(results)
        tested_concepts = sum(1 for r in results if r["tested_count"] > 0)
        total_mistakes = sum(r["mistakes_count"] for r in results)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Concepts", total_concepts)
        with col2:
            st.metric("Concepts Tested", tested_concepts)
        with col3:
            st.metric("Total Mistakes", total_mistakes)
        
        # Detailed results in expandable sections
        st.markdown("### Detailed Analysis by Concept")
        
        for idx, result in enumerate(results, 1):
            with st.expander(f"{idx}. {result['concept']} - {result['tested_count']} questions, {result['mistakes_count']} mistakes"):
                st.markdown("**Performance Summary:**")
                st.write(GeminiAnalyzer.format_response_1(result))
                
                # Show concept reasoning (how Gemini mapped questions to this concept)
                if result.get("concept_reasoning"):
                    st.markdown("---")
                    st.markdown("**How Gemini Mapped Questions to This Concept:**")
                    for reasoning in result["concept_reasoning"]:
                        q_num = reasoning.get("question", "?")
                        summary = reasoning.get("summary", "")
                        confidence = reasoning.get("confidence", "medium")
                        
                        st.markdown(f"**Question {q_num}** *({confidence} confidence)*")
                        st.caption(summary)
                        
                        # Show concept alignments
                        alignments = reasoning.get("concept_alignments", [])
                        for alignment in alignments:
                            if alignment.get("concept") == result["concept"]:
                                st.info(f"**Rationale:** {alignment.get('rationale', 'N/A')}")
                        
                        # Show rejected concepts if any
                        rejected = reasoning.get("considered_but_rejected", [])
                        if rejected:
                            st.caption(f"Also considered but rejected: {', '.join(rejected)}")
                
                if result["mistakes_count"] > 0:
                    st.markdown("---")
                    st.markdown("**Detailed Mistake Analysis:**")
                    st.write(GeminiAnalyzer.format_response_2(result))
                    
                    # Show performance reasoning (how Gemini evaluated the student's answers)
                    if result.get("performance_reasoning"):
                        st.markdown("---")
                        st.markdown("**How Gemini Evaluated Each Answer:**")
                        for perf_reasoning in result["performance_reasoning"]:
                            q_num = perf_reasoning.get("question", "?")
                            observation = perf_reasoning.get("observation", "")
                            concept_eval = perf_reasoning.get("concept_evaluation", "")
                            conclusion = perf_reasoning.get("conclusion", "")
                            confidence = perf_reasoning.get("confidence", "medium")
                            
                            with st.container():
                                st.markdown(f"**Question {q_num}** *({confidence} confidence)*")
                                st.markdown(f"**Observation:** {observation}")
                                st.markdown(f"**Concept Application:** {concept_eval}")
                                st.markdown(f"**Conclusion:** {conclusion}")
                                st.markdown("")
                
                # Show evaluation notes if any
                if result.get("performance_notes"):
                    st.markdown("---")
                    st.markdown("**Additional Evaluation Notes:**")
                    for note in result["performance_notes"]:
                        st.info(note)
        
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

