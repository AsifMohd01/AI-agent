# Autonomous AI Agent

## Description
The **Autonomous AI Agent** is an intelligent system capable of executing tasks across browser, terminal, and file system environments, powered by Google's Gemini 1.5 Flash model. This versatile AI assistant understands natural language instructions and performs complex tasks through a simple, intuitive interface.

## Features

### **Multi-Environment Task Execution**
- Seamlessly work across browser, terminal, and file system environments
- Execute commands and process their outputs
- Create, read, and manipulate files

### **Intelligent Document Generation**
- Create professional reports and documents with smart formatting
- Generate PDF-ready HTML documents with one-click export
- Include real-time data from the latest sources
- Use professional layouts for different document types

### **Advanced Web Search & Analysis**
- Collect and synthesize information from multiple websites
- Extract specific information like product specifications and statistics
- Compare different products, services, or concepts
- Condense large amounts of information into concise summaries

### **Natural Language Understanding**
- Process multi-step requests in natural language
- Maintain context throughout a conversation
- Break down complex tasks into manageable steps
- Tailor responses based on the specific query and context

### **Error-Resilient Processing**
- Handle JavaScript DOM manipulation errors gracefully
- Provide fallback mechanisms for content generation
- Implement robust error handling throughout the application

## Screenshots

### **Main Interface**
![Main Interface](/Screenshots/Interface.png)

### **Multi-Environment Execution**
![Multi-Environment Execution](/Screenshots/Environment.png)

### **Document Generation**
![Document Generation](/Screenshots/Execution-Report.png)

### **Web Search Results**
![Web Search Results](/Screenshots/web-search.png)

### **Natural Language Processing**
![Natural Language Processing](/Screenshots/Language.png)

## Tech Stack

### **Frontend**
- HTML, CSS, JavaScript
- Responsive design for desktop and tablet devices

### **Backend**
- Python with Flask web framework
- Google Generative AI API (Gemini 1.5 Flash model)
- RESTful API architecture

### **Document Generation**
- HTML with print-to-PDF capability
- Dynamic content formatting

## Installation

### **Prerequisites**
Make sure you have the following installed:
- Python 3.8+
- Flask web framework
- Google Generative AI API key for Gemini 1.5 Flash
- Modern web browser (Chrome or Firefox recommended)

### **Steps to Run**

#### 1. **Clone the repository**
```bash
git clone https://github.com/AsifMohd01/AI-agent.git
cd AI-agent
```

#### 2. **Create a virtual environment (recommended)**
```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

#### 3. **Install dependencies**
```bash
pip install -r requirements.txt
```

#### 4. **Configure Environment Variables**
Create a `.env` file in the project root with your Google API key:
```
GOOGLE_API_KEY=your_api_key_here
```

#### 5. **Start the server**
```bash
python app.py
```

The application should be accessible at `http://localhost:5000`.

#### 5. **To Start the server directly**
```bash
python run.py
```

The application should be accessible at `http://localhost:5000`.

## Usage

### **Basic Operation**
1. Enter your instruction in the text area
2. Click "Execute" to process your request
3. View the results in the appropriate environment section
4. Download or print any generated documents

### **Example Instructions**

#### Document Generation
- "Create a report on the latest smartphones"
- "Generate a comprehensive document about renewable energy trends"
- "Make a PDF comparing the top 5 electric vehicles of 2024"

#### Web Search & Analysis
- "Search for the top 5 laptops of 2024 and summarize their features"
- "Find information about climate change and extract the key statistics"
- "Compare the nutritional benefits of kale vs spinach"

#### Multi-Step Tasks
- "Search for the latest AI research papers, summarize the top 3, and create a report"
- "Find recipes for vegetarian pasta dishes, extract the ingredients, and save them to a file"
- "Research the history of electric cars, create a timeline, and generate a presentation"


## Troubleshooting

### **API Key Issues**
**Problem**: The application fails to start or returns errors about the API key.

**Solution**:
1. Verify your API key is correctly set in the `.env` file
2. Ensure the API key has access to the Gemini 1.5 Flash model
3. Check that the key hasn't expired or reached its quota limit

### **Document Generation Errors**
**Problem**: Documents fail to generate or display incorrectly.

**Solution**:
1. The application uses a simplified HTML approach to avoid JavaScript DOM manipulation errors
2. Try using the "Create a report on..." format for more reliable document generation
3. For complex documents, break down the request into simpler components

### **Browser Compatibility**
**Problem**: Some features don't work correctly in certain browsers.

**Solution**:
1. For best results, use Chrome or Firefox for PDF generation
2. Ensure JavaScript is enabled in your browser
3. Clear your browser cache if you encounter persistent issues



## Contact
For any inquiries or issues, please contact **[asif.mohd@campusuvce.in](mailto:asif.mohd@campusuvce.in)**.
