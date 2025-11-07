# Quick Start Guide

## 🚀 Get Started in 5 Minutes

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up API Key

You have two options:

**Option A: Use environment variable**
```bash
# Windows PowerShell
$env:GOOGLE_API_KEY="your_api_key_here"

# Windows CMD
set GOOGLE_API_KEY=your_api_key_here

# Linux/Mac
export GOOGLE_API_KEY=your_api_key_here
```

### 3. Run the Application

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

### 4. Use the Application

1. **Select Model**
   - Choose your preferred Gemini model from the sidebar dropdown

2. **Upload Files** (supports multiple files per document type)
   - **Analysis Sheet**: The concept list with columns (image/PDF)
   - **Question Paper**: The exam questions (image/PDF)
   - **Answer Sheet**: Student's answers (image/PDF)

3. **Analyze**
   - Click the "Analyze Performance" button
   - Wait for analysis (typically 2-5 minutes depending on document size)

4. **View Results**
   - See summary statistics
   - Expand each concept for detailed analysis
   - View Response 1: Test frequency and mistake count
   - View Response 2: Detailed error descriptions

5. **Download Reports**
   - Click "Download Excel Report" for Excel format
   - Click "Download PDF Report" for PDF format

## 📝 Example Output

For each concept, you'll get:

**Response 1 (Summary):**
```
Tested 8 times - Mistakes 4 times (Q.No 2, 4, 9, 10)
```

**Response 2 (Details):**
```
Q2: Wrong integration of tan²x - forgot to use substitution
Q4: Incorrect integration of log x - missing integration by parts
Q9: Incorrect substitution in sec²(3x+5)
Q10: Failed to apply chain rule properly
```

## 🐛 Troubleshooting

### "No module named 'google.generativeai'"
```bash
pip install --upgrade google-generativeai
```

### "pdf2image requires poppler"
**Windows**: Download poppler from [here](https://github.com/oschwartz10612/poppler-windows/releases/)

**Linux**:
```bash
sudo apt-get install poppler-utils
```

**Mac**:
```bash
brew install poppler
```

### "API Key Error"
- Verify your API key is correct
- Check you have API quota remaining
- Get a new key from [Google AI Studio](https://makersuite.google.com/app/apikey)

## 🌐 Deploy to Render

See [DEPLOYMENT.md](DEPLOYMENT.md) for complete deployment instructions.

Quick steps:
1. Push code to GitHub
2. Create new Web Service on Render
3. Connect your repository
4. Add `GOOGLE_API_KEY` environment variable
5. Deploy!

## 📚 File Structure

```
.
├── app.py                      # Main Streamlit application
├── gemini_analyzer.py          # Gemini AI integration
├── document_processor.py       # Image/PDF processing
├── report_generator.py         # Excel/PDF report generation
├── requirements.txt            # Python dependencies
├── render.yaml                 # Render deployment config
├── packages.txt                # System packages for Render
├── .streamlit/config.toml      # Streamlit configuration
├── README.md                   # Full documentation
├── DEPLOYMENT.md               # Deployment guide
└── QUICKSTART.md               # This file
```

## 💡 Tips

- **Better Results**: Use clear, high-resolution images/PDFs
- **Speed**: gemini-2.5-flash is faster, gemini-2.5-pro is more accurate
- **Cost**: Monitor your API usage on Google AI Studio
- **Accuracy**: Review and verify AI-generated analysis

## 🆘 Need Help?

- Check the [README.md](README.md) for detailed information
- Review [DEPLOYMENT.md](DEPLOYMENT.md) for deployment issues
- Check logs in the terminal for error messages
- Verify all files are uploaded correctly before analyzing

## 🎯 Next Steps

1. Test with sample documents
2. Review the generated reports
3. Deploy to Render for easy access
4. Share the URL with users

Happy analyzing! 📊

1. Create a new Web Service on Render
2. Connect your GitHub repository
3. Set the following:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `streamlit run app.py --server.port=$PORT --server.address=0.0.0.0`
4. Add environment variable: `GOOGLE_API_KEY` with your API key
5. Deploy!