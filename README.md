# Student Performance Analyzer

An AI-powered application that analyzes student performance by comparing answer sheets against question papers, tracking concept-wise mistakes, and generating detailed reports using Google's Gemini AI.

## Features

- Upload analysis sheets (concept lists), question papers, and answer sheets in image or PDF format
- AI-powered analysis using Google Gemini 2.5 models with vision capabilities
- Concept-wise performance tracking
- Detailed mistake analysis for each question
- Export results to Excel or PDF format
- Deployed on Render for easy access

## Setup Instructions

### Prerequisites

- Python 3.9 or higher
- Google Gemini API key ([Get it here](https://makersuite.google.com/app/apikey))

### Local Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd Task-2
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
```
Edit `.env` and add your Google Gemini API key.

4. Run the application:
```bash
streamlit run app.py
```

5. Open your browser and navigate to `http://localhost:8501`

## Usage

1. **Set API Key**: Ensure GOOGLE_API_KEY environment variable is set
2. **Upload Files**:
   - Analysis Sheet: Contains the concept list with columns (supports multiple files)
   - Question Paper: The exam questions (supports multiple files)
   - Answer Sheet: Student's solutions (supports multiple files)
3. **Select Model**: Choose the Gemini model from the sidebar dropdown
4. **Click Analyze**: Start the AI-powered analysis
5. **View Results**: See concept-wise performance breakdown
6. **Download Reports**: Export as Excel or PDF

## Output Format

For each concept in the analysis sheet:

**Response 1**: Summary statistics
```
Tested X times - Mistakes Y times (Q.No 2, 4, 9, 10)
```

**Response 2**: Detailed mistake analysis
```
- Q2: Wrong integration of tan^2 dx
- Q4: Wrong integration of log x
- Q9: Incorrect substitution in sec^2(3x+5)
```

## Deployment on Render

This application is configured for deployment on [Render](https://render.com/).

## Technology Stack

- **Frontend**: Streamlit
- **AI Model**: Google Gemini 2.5 (Flash/Pro)
- **Document Processing**: Pillow, pdf2image, pypdf
- **Report Generation**: openpyxl (Excel), fpdf2 (PDF)
- **Deployment**: Render

## License

MIT License

