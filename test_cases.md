# Test Cases for Autonomous AI Agent

## General Response Test Cases

1. **Ask general knowledge questions**
   - Input: "What is machine learning?"
   - Expected Output: Informative response about machine learning

2. **Ask for explanations of complex topics**
   - Input: "Explain quantum computing in simple terms"
   - Expected Output: Clear, simplified explanation of quantum computing

3. **Ask for comparisons**
   - Input: "Compare and contrast different renewable energy sources"
   - Expected Output: Structured comparison of various renewable energy sources

## Document Creation Test Cases

1. **Create a text document**
   - Input: "Create a document about artificial intelligence"
   - Expected Output: Well-structured text document about AI with download option

2. **Generate a formal report**
   - Input: "Generate a report on cybersecurity best practices"
   - Expected Output: Formal report with sections on cybersecurity practices

3. **Create a PDF report**
   - Input: "Create a PDF report on renewable energy"
   - Expected Output: HTML file formatted for PDF printing with proper styling and sections

## Original Test Cases

1. **Find top 5 AI headlines and save to file**
   - Expected Output: Text file with 5 current AI news headlines

2. **Search smartphone reviews, extract pros/cons, create summary**
   - Expected Output: Document with organized review data

3. **Research renewable energy, analyze trends, create report**
   - Expected Output: Comprehensive report on renewable energy trends

4. **Find the latest AI research papers, extract abstracts, and create a summary**
   - Expected Output: Document with research paper summaries

5. **Search for information about climate change, analyze findings, and create a presentation outline**
   - Expected Output: Structured outline for a presentation on climate change

## How to Run the Tests

1. Start the application with `python run.py`
2. Enter each test case as an instruction in the input field
3. Click "Execute" and verify that the results match the expected output

### For PDF Reports

When testing PDF report creation:
1. Click on the "Open & Print PDF" button to open the HTML file
2. Use your browser's print function (Ctrl+P or Cmd+P)
3. Select "Save as PDF" as the destination
4. Save the file to your desired location

## Expected Results

### For General Questions
- The agent should provide a helpful, informative response directly in the UI
- The response should be well-formatted and easy to read

### For Document Creation
- The agent should generate a well-structured document with appropriate sections
- The document should be saved and available for download
- The UI should display a preview of the document content

### For PDF Reports
- The agent should generate an HTML file that can be printed as a PDF
- The HTML file should be well-formatted with proper styling
- The UI should provide clear instructions on how to save the file as a PDF
- A "Print/Save as PDF" button should be available in the HTML file

## Troubleshooting

If a test case fails:

1. Check the server logs for errors
2. Verify that the API keys are valid
3. Make sure all dependencies are installed correctly
4. Try simplifying the instruction and running it again
5. For PDF generation issues, make sure the static/downloads directory exists and is writable