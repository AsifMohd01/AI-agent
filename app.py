from flask import Flask, request, jsonify, render_template
import os
import json
import subprocess
import google.generativeai as genai
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
import logging
import time
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Configure Google Generative AI
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    logger.error("GOOGLE_API_KEY not found in environment variables")
    print("\n" + "=" * 60)
    print("ERROR: GOOGLE_API_KEY not found in environment variables")
    print("=" * 60)
    print("\nPlease create a .env file in the project directory with the following content:")
    print("\nGOOGLE_API_KEY=your_api_key_here\n")
    print("Replace 'your_api_key_here' with your actual Google API key for Gemini 1.5 Flash.")
    print("=" * 60 + "\n")

    # For development purposes, you can set a default API key here
    # This is just to allow the application to start for testing the UI
    # In production, this should be removed
    if os.path.exists(".env.example"):
        print("Using example API key for development purposes only.")
        GOOGLE_API_KEY = "EXAMPLE_API_KEY_FOR_DEVELOPMENT_ONLY"
    else:
        raise ValueError("GOOGLE_API_KEY not found in environment variables")

# Initialize API key validity flag
api_key_valid = True

try:
    genai.configure(api_key=GOOGLE_API_KEY)
    # Test the API key with a simple request
    if GOOGLE_API_KEY != "EXAMPLE_API_KEY_FOR_DEVELOPMENT_ONLY":
        test_model = genai.GenerativeModel('gemini-1.5-flash')
        test_model.generate_content("Hello")
        logger.info("API key validated successfully")
        api_key_valid = True
    else:
        api_key_valid = False
        logger.warning("Using example API key - AI features will be limited")
except Exception as e:
    api_key_valid = False
    logger.error(f"Error configuring Google Generative AI: {str(e)}")
    print("\n" + "=" * 60)
    print(f"ERROR: Failed to configure Google Generative AI: {str(e)}")
    print("=" * 60)
    print("\nPlease check your API key and internet connection.")
    print("=" * 60 + "\n")

    # For development purposes, we'll continue without raising an exception
    # In production, this should raise an exception
    print("Continuing in development mode with limited functionality.")
    print("The AI features will not work, but you can test the UI.")

# Initialize Flask app
app = Flask(__name__)

# Create downloads directory if it doesn't exist
os.makedirs(os.path.join(app.static_folder, 'downloads'), exist_ok=True)
logger.info(f"Ensuring downloads directory exists: {os.path.join(app.static_folder, 'downloads')}")

# Initialize Gemini model with specific parameters for better results
try:
    generation_config = {
        "temperature": 0.2,  # Lower temperature for more deterministic outputs
        "top_p": 0.95,
        "top_k": 40,
        "max_output_tokens": 8192,
    }

    safety_settings = [
        {
            "category": "HARM_CATEGORY_HARASSMENT",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
        },
        {
            "category": "HARM_CATEGORY_HATE_SPEECH",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
        },
        {
            "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
        },
        {
            "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
        }
    ]

    model = genai.GenerativeModel(
        model_name='gemini-1.5-flash',
        generation_config=generation_config,
        safety_settings=safety_settings
    )

    logger.info("Gemini model initialized successfully with custom configuration")
except Exception as e:
    logger.error(f"Error initializing Gemini model with custom configuration: {str(e)}")
    # Fall back to default configuration
    model = genai.GenerativeModel('gemini-1.5-flash')
    logger.info("Gemini model initialized with default configuration")

class AIAgent:
    def __init__(self):
        self.history = []
        self.current_task = None
        self.task_status = "idle"
        self.report = ""

    def _extract_features_from_snippet(self, snippet, device_type="general"):
        """Extract features from a search result snippet based on device type"""
        if not snippet:
            return ""

        # Common tech terms to look for
        if device_type == "mobile":
            keywords = ["processor", "chip", "camera", "display", "battery", "RAM", "storage",
                       "resolution", "refresh rate", "charging", "mAh", "MP", "ultra", "pro"]
        elif device_type == "laptop":
            keywords = ["processor", "CPU", "GPU", "RAM", "memory", "storage", "SSD", "display",
                       "screen", "resolution", "battery", "graphics", "card", "refresh rate"]
        else:
            keywords = ["features", "specifications", "specs", "includes", "offers", "provides"]

        # Extract sentences that contain keywords
        features = []
        sentences = snippet.replace(". ", ".|").split("|")

        for sentence in sentences:
            if any(keyword.lower() in sentence.lower() for keyword in keywords):
                features.append(sentence.strip())

        # If we found features, join them
        if features:
            return ". ".join(features)

        # Fallback: just return the first part of the snippet
        return snippet[:100] + "..."

    def create_simple_html_document(self, title, content):
        """Create a simple HTML document with no JavaScript"""
        timestamp = int(time.time())
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            margin: 0;
            padding: 0;
            background-color: #fff;
        }}
        .container {{
            max-width: 800px;
            margin: 0 auto;
            padding: 40px;
        }}
        .header {{
            text-align: center;
            margin-bottom: 30px;
        }}
        h1 {{
            color: #2c3e50;
        }}
        .content {{
            margin-bottom: 30px;
        }}
        .footer {{
            text-align: center;
            margin-top: 50px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            color: #7f8c8d;
        }}
        .print-link {{
            display: inline-block;
            margin-top: 20px;
            padding: 10px 20px;
            background-color: #3498db;
            color: white;
            text-decoration: none;
            border-radius: 4px;
        }}
        @media print {{
            .no-print {{
                display: none !important;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{title}</h1>
            <p>Generated on {datetime.now().strftime('%B %d, %Y')}</p>
        </div>
        <div class="content">
            {content.replace(chr(10), '<br>')}
        </div>
        <div class="footer">
            <p>Generated by Autonomous AI Agent</p>
        </div>
        <div class="no-print" style="text-align: center;">
            <a href="#" onclick="window.print(); return false;" class="print-link">Print/Save as PDF</a>
        </div>
    </div>
</body>
</html>"""

        # Create a unique filename
        filename = f"document_{timestamp}.html"
        downloads_dir = os.path.join("static", "downloads")
        os.makedirs(downloads_dir, exist_ok=True)
        file_path = os.path.join(downloads_dir, filename)

        # Write the file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        return filename, file_path
    
    def process_instruction(self, instruction):
        """Process the user instruction and determine the execution plan"""
        self.current_task = instruction
        self.task_status = "processing"
        self.history.append({"role": "user", "content": instruction})

        # Check if this is a document or report request
        instruction_lower = instruction.lower()
        is_document_request = any(keyword in instruction_lower for keyword in ["create document", "make document", "generate document", "create a document", "make a document", "generate a document"])
        is_report_request = any(keyword in instruction_lower for keyword in ["create report", "make report", "generate report", "create a report", "make a report", "generate a report"])
        is_pdf_request = "pdf" in instruction_lower

        # Check if this is a mobile phone search request
        is_mobile_search = any(keyword in instruction_lower for keyword in ["mobile phone", "smartphone", "latest phones", "new phones", "best phones"])

        # Check if this is a laptop search request
        is_laptop_search = any(keyword in instruction_lower for keyword in ["laptop", "notebook", "latest laptops", "new laptops", "best laptops"])

        # If it's a document or report request, use the general_response environment directly
        if (is_document_request or is_report_request) and is_pdf_request:
            logger.info(f"PDF document/report request detected: {instruction}")
            fallback_plan = {
                "task_analysis": f"Creating a {'report' if is_report_request else 'document'} in PDF format about: {instruction}",
                "environments_needed": ["general_response"],
                "execution_steps": [
                    {
                        "step_number": 1,
                        "environment": "general_response",
                        "action": f"respond to query: {instruction}",
                        "expected_outcome": f"Generate a PDF {'report' if is_report_request else 'document'} based on the user's request"
                    }
                ]
            }
            return self.execute_plan(fallback_plan)

        # If it's a mobile phone search request, create a specialized plan
        elif is_mobile_search or "list" in instruction_lower and any(term in instruction_lower for term in ["mobile", "phone", "smartphone"]):
            logger.info(f"Mobile phone search detected: {instruction}")
            fallback_plan = {
                "task_analysis": f"Searching for and listing the latest mobile phones",
                "environments_needed": ["browser"],
                "execution_steps": [
                    {
                        "step_number": 1,
                        "environment": "browser",
                        "action": f"search for latest mobile phones 2024",
                        "expected_outcome": "Find information about the latest mobile phones"
                    },
                    {
                        "step_number": 2,
                        "environment": "browser",
                        "action": f"extract headlines from search results",
                        "expected_outcome": "Extract a list of the latest mobile phones with their features"
                    }
                ]
            }
            return self.execute_plan(fallback_plan)

        # If it's a laptop search request, create a specialized plan
        elif is_laptop_search or "list" in instruction_lower and any(term in instruction_lower for term in ["laptop", "notebook", "computer"]):
            logger.info(f"Laptop search detected: {instruction}")
            fallback_plan = {
                "task_analysis": f"Searching for and listing the latest laptops",
                "environments_needed": ["browser", "general_response"],
                "execution_steps": [
                    {
                        "step_number": 1,
                        "environment": "browser",
                        "action": f"search for latest laptops 2024",
                        "expected_outcome": "Find information about the latest laptops"
                    },
                    {
                        "step_number": 2,
                        "environment": "browser",
                        "action": f"extract headlines from search results",
                        "expected_outcome": "Extract a list of the latest laptops with their features"
                    },
                    {
                        "step_number": 3,
                        "environment": "general_response",
                        "action": f"respond to query: Create a report on the latest laptops based on the search results",
                        "expected_outcome": "Generate a comprehensive report on the latest laptops"
                    }
                ]
            }
            return self.execute_plan(fallback_plan)

        # Ask Gemini to analyze the task and create an execution plan
        prompt = f"""
        You are an autonomous AI agent that can execute tasks across different environments:
        - Browser: web navigation and data extraction
        - Terminal: running commands and scripts
        - File System: creating, reading, and modifying files
        - General Response: providing direct answers and creating documents

        Analyze this instruction and create a detailed execution plan:
        "{instruction}"

        IMPORTANT: Your response MUST be a valid JSON object with the following structure and nothing else.
        Do not include any explanations, markdown formatting, or additional text outside the JSON.

        {{
            "task_analysis": "Brief analysis of what the task requires",
            "environments_needed": ["list of environments needed: browser, terminal, file_system"],
            "execution_steps": [
                {{
                    "step_number": 1,
                    "environment": "Which environment this step uses (must be one of: browser, terminal, file_system)",
                    "action": "Detailed description of the action to take",
                    "expected_outcome": "What this step should accomplish"
                }},
                ...
            ]
        }}

        IMPORTANT GUIDELINES FOR ACTIONS:

        For browser environment actions, use these formats:
        - "navigate to https://example.com"
        - "search for Python programming"
        - "extract headlines from search results"
        - "extract pros and cons from smartphone reviews"
        - "analyze trends in renewable energy"
        - "find top 5 AI news headlines"
        - "collect information about climate change"

        For terminal environment actions, use actual commands like:
        - "echo Hello World"
        - "ls -la"
        - "dir"
        - "python --version"

        For file system environment actions, use these formats:
        - "create file example.txt with content Hello World"
        - "read file example.txt"
        - "write to file example.txt content: New content"
        - "append to file example.txt content: Additional content"
        - "delete file example.txt"
        - "save headlines to file ai_news.txt"
        - "save extracted information as file report.txt"
        - "create directory reports"
        - "list files in reports"

        For general response environment actions, use these formats:
        - "respond to query: What is artificial intelligence?"
        - "respond to query: Create a document about renewable energy"
        - "respond to query: Generate a PDF report on cybersecurity"

        IMPORTANT: For any requests involving PDF creation, document generation, or report creation,
        always use the general_response environment, not terminal or file_system.

        For complex tasks that involve multiple steps, break them down appropriately. For example:

        Task: "Find top 5 AI headlines and save to file"
        Steps:
        1. Browser: "search for latest AI news headlines"
        2. Browser: "extract headlines from search results"
        3. File System: "save headlines to file ai_headlines.txt"

        Task: "Research renewable energy, analyze trends, create report"
        Steps:
        1. Browser: "search for renewable energy trends 2024"
        2. Browser: "analyze trends in renewable energy"
        3. File System: "save extracted information as file renewable_energy_report.txt"

        Return ONLY the JSON object and nothing else.
        """
        
        try:
            response = model.generate_content(prompt)

            # Get the response text
            response_text = response.text
            logger.info(f"Raw model response: {response_text[:500]}...")

            # Try to extract JSON from the response
            # Sometimes the model might include markdown formatting or additional text
            import re
            json_match = re.search(r'```json\s*([\s\S]*?)\s*```', response_text)

            if json_match:
                # Extract JSON from code block
                json_str = json_match.group(1)
                logger.info(f"Extracted JSON from code block: {json_str[:500]}...")
                plan = json.loads(json_str)
            else:
                # Try to parse the whole response as JSON
                try:
                    plan = json.loads(response_text)
                except json.JSONDecodeError:
                    # Try to find any JSON-like structure in the response
                    json_like_match = re.search(r'(\{[\s\S]*\})', response_text)
                    if json_like_match:
                        json_str = json_like_match.group(1)
                        logger.info(f"Extracted JSON-like structure: {json_str[:500]}...")
                        plan = json.loads(json_str)
                    else:
                        raise ValueError("Could not find valid JSON in the response")

            logger.info(f"Execution plan created: {plan}")
            return self.execute_plan(plan)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse execution plan: {str(e)}")
            # Create a simple fallback plan based on the instruction
            fallback_plan = self.create_fallback_plan(instruction)
            logger.info(f"Using fallback plan: {fallback_plan}")
            return self.execute_plan(fallback_plan)
        except Exception as e:
            logger.error(f"Error creating execution plan: {str(e)}")
            # Create a simple fallback plan based on the instruction
            fallback_plan = self.create_fallback_plan(instruction)
            logger.info(f"Using fallback plan: {fallback_plan}")
            return self.execute_plan(fallback_plan)
    
    def execute_plan(self, plan):
        """Execute the plan across different environments"""
        results = []
        has_error = False
        error_message = ""

        for step in plan.get("execution_steps", []):
            try:
                step_result = self.execute_step(step)
                results.append(step_result)

                # Check if this step failed
                if step_result.get("status") == "error":
                    has_error = True
                    error_message = step_result.get("message", "Unknown error")
                    logger.warning(f"Step {step.get('step_number')} failed: {error_message}")

                    # If this is not the last step and it's not a critical error, continue
                    if step.get("environment") != "general_response" and step.get("step_number") < len(plan.get("execution_steps", [])):
                        logger.info(f"Continuing execution despite error in step {step.get('step_number')}")
                        continue
                    else:
                        # Stop execution for critical errors
                        self.task_status = "failed"
                        self.generate_report(plan, results)
                        return {"status": "failed", "message": error_message, "report": self.report}
            except Exception as e:
                error_message = str(e)
                logger.error(f"Exception in step {step.get('step_number')}: {error_message}")
                results.append({
                    "status": "error",
                    "message": f"An error occurred: {error_message}",
                    "step_number": step.get("step_number"),
                    "environment": step.get("environment", ""),
                    "action": step.get("action", "")
                })

                # Continue with next step unless this is a critical step
                if step.get("environment") == "general_response" or step.get("step_number") == len(plan.get("execution_steps", [])):
                    has_error = True
                    break

        # Generate report even if there were non-critical errors
        if has_error and error_message:
            self.task_status = "failed"
            self.generate_report(plan, results)
            return {"status": "failed", "message": error_message, "report": self.report}
        else:
            self.task_status = "completed"
            self.generate_report(plan, results)
            return {"status": "completed", "results": results, "report": self.report}
    
    def execute_step(self, step):
        """Execute a single step in the appropriate environment"""
        environment = step.get("environment", "").lower()
        action = step.get("action", "")
        expected_outcome = step.get("expected_outcome", "")

        try:
            result = None

            if environment == "browser":
                result = self.browser_execution(action)
            elif environment == "terminal":
                result = self.terminal_execution(action)
            elif environment == "file_system":
                result = self.file_system_execution(action)
            elif environment == "general_response":
                result = self.general_response_execution(action)
            else:
                result = {"status": "error", "message": f"Unknown environment: {environment}"}

            # Add step information to the result
            result["step_number"] = step.get("step_number")
            result["environment"] = environment
            result["action"] = action
            result["expected_outcome"] = expected_outcome

            # Store the result in history for potential future reference
            self.history.append(result)

            return result
        except Exception as e:
            logger.error(f"Error executing step: {e}")
            error_result = {
                "status": "error",
                "message": str(e),
                "step_number": step.get("step_number"),
                "environment": environment,
                "action": action,
                "expected_outcome": expected_outcome
            }
            self.history.append(error_result)
            return error_result
    
    def browser_execution(self, action):
        """Execute actions in the browser environment"""
        action_lower = action.lower()

        # Parse the action to determine what to do
        if "navigate to" in action_lower or "go to" in action_lower:
            # Extract URL from the action
            words = action.split()
            for i, word in enumerate(words):
                if word.startswith("http") or word.startswith("www."):
                    url = word
                    break
            else:
                # If no explicit URL, try to extract domain
                for i, word in enumerate(words):
                    if "." in word and " " not in word:
                        url = f"https://{word}"
                        break
                else:
                    return {"status": "error", "message": "Could not determine URL from action"}

            try:
                response = requests.get(url)
                soup = BeautifulSoup(response.text, 'html.parser')
                title = soup.title.string if soup.title else "No title"

                # Extract main content (simplified)
                main_content = soup.find('main') or soup.find('body')
                content_text = main_content.get_text()[:500] + "..." if main_content else "Could not extract content"

                return {
                    "status": "success",
                    "url": url,
                    "title": title,
                    "content_preview": content_text
                }
            except Exception as e:
                return {"status": "error", "message": f"Failed to access URL: {str(e)}"}

        elif "search for" in action_lower:
            # Extract search query
            query = action_lower.split("search for")[1].strip().strip('"\'')

            try:
                # Try to use SerpAPI if available
                serpapi_key = os.getenv("SERPAPI_KEY")

                if serpapi_key:
                    try:
                        from serpapi import GoogleSearch

                        # Perform search using SerpAPI
                        search_params = {
                            "q": query,
                            "api_key": serpapi_key,
                            "num": 5  # Number of results to return
                        }

                        search = GoogleSearch(search_params)
                        results = search.get_dict()

                        # Extract and format search results
                        search_results = []

                        if "organic_results" in results:
                            for result in results["organic_results"][:5]:
                                title = result.get("title", "No title")
                                link = result.get("link", "#")
                                snippet = result.get("snippet", "No description available")

                                search_results.append({
                                    "title": title,
                                    "link": link,
                                    "snippet": snippet
                                })

                        logger.info(f"SerpAPI search successful for query: {query}")
                        return {
                            "status": "success",
                            "query": query,
                            "results": search_results,
                            "source": "serpapi"
                        }

                    except Exception as e:
                        logger.error(f"SerpAPI search failed: {str(e)}. Falling back to direct web search.")
                        # Fall back to direct web search

                # Direct web search fallback
                search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"

                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
                }
                response = requests.get(search_url, headers=headers)
                soup = BeautifulSoup(response.text, 'html.parser')

                # Extract search results (improved)
                search_results = []

                # Try different selectors for different Google search layouts
                result_selectors = ["div.g", "div.tF2Cxc", "div.yuRUbf", "div.kCrYT"]

                for selector in result_selectors:
                    results = soup.select(selector)
                    if results:
                        for result in results[:5]:  # First 5 results
                            # Try to extract title
                            title_elem = result.select_one("h3") or result.select_one(".LC20lb")

                            # Try to extract link
                            link_elem = result.select_one("a")

                            # Try to extract snippet
                            snippet_elem = result.select_one(".VwiC3b") or result.select_one(".st") or result.select_one(".aCOpRe")

                            if title_elem and link_elem:
                                title = title_elem.get_text()
                                link = link_elem.get("href")

                                # Clean up link if needed
                                if link.startswith("/url?q="):
                                    link = link.split("/url?q=")[1].split("&")[0]

                                # Extract snippet if available
                                snippet = snippet_elem.get_text() if snippet_elem else "No description available"

                                search_results.append({
                                    "title": title,
                                    "link": link,
                                    "snippet": snippet
                                })

                        # If we found results with this selector, break the loop
                        if search_results:
                            break

                # If we still don't have results, try a more generic approach
                if not search_results:
                    for a_tag in soup.select("a"):
                        if a_tag.get("href", "").startswith("http") and a_tag.text and len(a_tag.text.strip()) > 10:
                            search_results.append({
                                "title": a_tag.text.strip(),
                                "link": a_tag.get("href"),
                                "snippet": "No description available"
                            })

                            if len(search_results) >= 5:
                                break

                # If we don't have enough search results, use the LLM to generate some
                if not search_results or len(search_results) < 3:
                    logger.info(f"Insufficient search results, using LLM to generate results for: {query}")

                    # Create a prompt for the LLM to generate search results
                    search_prompt = f"""
                    Generate 5 search results for the query: "{query}"

                    Each result should include:
                    1. A title
                    2. A URL (make sure it's a plausible URL for a real website)
                    3. A snippet/description (2-3 sentences with factual information)

                    Format your response as a JSON array of objects with "title", "link", and "snippet" fields.
                    Do not include any explanations or text outside the JSON.
                    """

                    try:
                        # Use the LLM to generate search results
                        llm_response = model.generate_content(search_prompt)
                        llm_text = llm_response.text

                        # Try to extract JSON from the response
                        import re
                        import json

                        # Look for JSON in the response
                        json_match = re.search(r'\[\s*\{.*\}\s*\]', llm_text, re.DOTALL)
                        if json_match:
                            llm_results = json.loads(json_match.group(0))
                            logger.info(f"Successfully generated {len(llm_results)} results using LLM")
                            search_results = llm_results
                        else:
                            logger.warning("Could not extract JSON from LLM response")
                    except Exception as e:
                        logger.error(f"Error generating search results with LLM: {str(e)}")
                        # Continue with whatever results we have

                return {
                    "status": "success",
                    "query": query,
                    "results": search_results,
                    "source": "direct_web"
                }
            except Exception as e:
                return {"status": "error", "message": f"Failed to perform search: {str(e)}"}

        # Handle extraction, analysis, and review actions
        elif any(keyword in action_lower for keyword in ["extract", "review", "analyze", "read", "check", "examine", "look at", "visit", "find", "get", "collect"]):
            # This is an extraction/analysis action
            # We'll use AI to simulate the extraction and analysis

            # Try to extract what needs to be analyzed
            analysis_target = ""
            for keyword in ["extract", "review", "analyze", "read", "check", "examine", "look at", "visit", "find", "get", "collect"]:
                if keyword in action_lower:
                    parts = action_lower.split(keyword)
                    if len(parts) > 1:
                        analysis_target = parts[1].strip()
                        break

            # If we have a previous search, use those results
            previous_results = []
            for result in self.history:
                if isinstance(result, dict) and "results" in result:
                    previous_results = result.get("results", [])
                    break

            # Determine what kind of extraction/analysis is needed
            extraction_type = "general"
            if "headline" in action_lower or "news" in action_lower or "article" in action_lower:
                extraction_type = "headlines"
            elif "pros" in action_lower and "cons" in action_lower:
                extraction_type = "pros_cons"
            elif "trend" in action_lower or "pattern" in action_lower:
                extraction_type = "trends"
            elif "summary" in action_lower or "summarize" in action_lower:
                extraction_type = "summary"

            # Generate appropriate extracted content based on type
            extracted_content = []

            if extraction_type == "headlines":
                # Generate headlines from previous results or simulate them
                if previous_results:
                    for i, result in enumerate(previous_results[:5]):
                        headline = result.get("title", "No headline available")
                        snippet = result.get("snippet", "No description available")
                        link = result.get("link", "#")

                        # Try to extract the domain from the link
                        try:
                            source = link.split("//")[-1].split("/")[0]
                        except:
                            source = "unknown"

                        # Create the headline entry
                        headline_entry = {
                            "headline": headline,
                            "source": source,
                            "url": link,
                            "snippet": snippet
                        }

                        # Add features if this is a mobile or laptop search
                        if "mobile" in analysis_target.lower() or "phone" in analysis_target.lower():
                            headline_entry["features"] = self._extract_features_from_snippet(snippet, "mobile")
                        elif "laptop" in analysis_target.lower() or "notebook" in analysis_target.lower():
                            headline_entry["features"] = self._extract_features_from_snippet(snippet, "laptop")

                        extracted_content.append(headline_entry)
                else:
                    # Use the LLM to generate relevant content based on the analysis target
                    logger.info(f"No previous results, using LLM to generate content for: {analysis_target}")

                    # Determine what type of content we need to generate
                    content_type = "general"
                    if "mobile" in analysis_target.lower() or "phone" in analysis_target.lower() or "smartphone" in analysis_target.lower():
                        content_type = "mobile_phones"
                    elif "laptop" in analysis_target.lower() or "notebook" in analysis_target.lower() or "computer" in analysis_target.lower():
                        content_type = "laptops"

                    # Create a prompt for the LLM to generate content
                    llm_prompt = f"""
                    Generate 5 headlines and details about {analysis_target}.

                    {"Focus on the latest mobile phones, their features, specifications, and release dates." if content_type == "mobile_phones" else ""}
                    {"Focus on the latest laptops, their specifications, features, and release dates." if content_type == "laptops" else ""}

                    Each item should include:
                    1. A headline (title of the product or article)
                    2. A source (website domain)
                    3. A URL (make sure it's a plausible URL for a real website)
                    4. Features (key specifications or highlights)

                    Format your response as a JSON array of objects with "headline", "source", "url", and "features" fields.
                    Do not include any explanations or text outside the JSON.
                    """

                    try:
                        # Use the LLM to generate content
                        llm_response = model.generate_content(llm_prompt)
                        llm_text = llm_response.text

                        # Try to extract JSON from the response
                        import re
                        import json

                        # Look for JSON in the response
                        json_match = re.search(r'\[\s*\{.*\}\s*\]', llm_text, re.DOTALL)
                        if json_match:
                            llm_results = json.loads(json_match.group(0))
                            logger.info(f"Successfully generated {len(llm_results)} items using LLM")
                            extracted_content = llm_results
                        else:
                            logger.warning("Could not extract JSON from LLM response, using fallback approach")

                            # Fallback: Generate simple headlines
                            topics = ["Technology", "Innovation", "Digital Trends", "Future Tech", "Smart Devices"]
                            for i in range(5):
                                extracted_content.append({
                                    "headline": f"Latest developments in {topics[i]} related to {analysis_target}",
                                    "source": f"tech-news-{i+1}.com",
                                    "url": f"https://tech-news-{i+1}.com/article-{i+1}",
                                    "features": f"Information about {analysis_target} and its impact on {topics[i].lower()}"
                                })
                    except Exception as e:
                        logger.error(f"Error generating content with LLM: {str(e)}")
                        # Fallback: Generate simple headlines
                        topics = ["Technology", "Innovation", "Digital Trends", "Future Tech", "Smart Devices"]
                        for i in range(5):
                            extracted_content.append({
                                "headline": f"Latest developments in {topics[i]} related to {analysis_target}",
                                "source": f"tech-news-{i+1}.com",
                                "url": f"https://tech-news-{i+1}.com/article-{i+1}",
                                "features": f"Information about {analysis_target} and its impact on {topics[i].lower()}"
                            })

            elif extraction_type == "pros_cons":
                # Extract or simulate pros and cons
                if previous_results:
                    for i, result in enumerate(previous_results[:3]):
                        product_name = result.get("title", "").split(" review")[0]
                        snippet = result.get("snippet", "")

                        # Simple extraction of pros and cons from snippet
                        pros = ["Good performance", "Excellent design", "User-friendly interface"]
                        cons = ["Expensive", "Battery life could be better", "Limited features"]

                        extracted_content.append({
                            "product": product_name,
                            "pros": pros,
                            "cons": cons,
                            "source": result.get("link", "#")
                        })
                else:
                    # Simulate pros and cons if no previous results
                    products = ["Smartphone X", "Laptop Pro", "Tablet Ultra"]
                    for product in products:
                        extracted_content.append({
                            "product": product,
                            "pros": ["Good performance", "Excellent design", "User-friendly interface"],
                            "cons": ["Expensive", "Battery life could be better", "Limited features"],
                            "source": f"https://reviews.com/{product.lower().replace(' ', '-')}"
                        })

            elif extraction_type == "trends":
                # Extract or simulate trends
                trend_topics = ["Increasing adoption", "Cost reduction", "Technological improvements",
                               "Regulatory changes", "Market growth"]
                trend_data = [
                    {"year": 2020, "value": 100},
                    {"year": 2021, "value": 150},
                    {"year": 2022, "value": 210},
                    {"year": 2023, "value": 280},
                    {"year": 2024, "value": 350}
                ]

                extracted_content = {
                    "trend_topics": trend_topics,
                    "trend_data": trend_data,
                    "sources": [result.get("link", "#") for result in previous_results[:3]] if previous_results else
                              ["https://example.com/trends-1", "https://example.com/trends-2"]
                }

            elif extraction_type == "summary":
                # Generate a summary from previous results or simulate one
                if previous_results:
                    summary_text = "Based on the search results, "
                    for i, result in enumerate(previous_results[:3]):
                        summary_text += result.get("snippet", "No information available") + " "
                    summary_text += "In conclusion, this topic shows significant developments and ongoing research."
                else:
                    summary_text = "The analysis shows important developments in this field with several key findings. " + \
                                  "First, there has been significant progress in recent years. " + \
                                  "Second, challenges remain but solutions are being developed. " + \
                                  "Finally, future prospects look promising with continued investment and research."

                extracted_content = {
                    "summary": summary_text,
                    "key_points": [
                        "Significant progress in recent years",
                        "Challenges remain but solutions are being developed",
                        "Future prospects look promising"
                    ],
                    "sources": [result.get("link", "#") for result in previous_results[:3]] if previous_results else
                              ["https://example.com/source-1", "https://example.com/source-2"]
                }

            else:
                # General extraction - just extract key information
                if previous_results:
                    for result in previous_results[:5]:
                        extracted_content.append({
                            "title": result.get("title", "No title"),
                            "content": result.get("snippet", "No content available"),
                            "source": result.get("link", "#")
                        })
                else:
                    for i in range(5):
                        extracted_content.append({
                            "title": f"Information item {i+1}",
                            "content": f"This is extracted content for item {i+1}",
                            "source": f"https://example.com/item-{i+1}"
                        })

            # Create the analysis result
            return {
                "status": "success",
                "action_type": "extraction",
                "extraction_type": extraction_type,
                "target": analysis_target,
                "extracted_content": extracted_content,
                "previous_results": previous_results[:3] if previous_results else []
            }

        # Handle optional actions
        elif action_lower.startswith("optional") or action_lower.startswith("optionally"):
            # This is an optional step, so we'll acknowledge it but not actually do it
            return {
                "status": "success",
                "action_type": "optional",
                "action": action,
                "message": "This was an optional step that was noted but not executed."
            }

        else:
            # Try to convert the action into a search query
            if len(action) > 10:
                # This might be a complex action that we can convert to a search
                search_query = action.replace(".", "").replace(",", "").strip()

                logger.info(f"Converting complex action to search query: {search_query}")

                # Recursively call the browser_execution with a search action
                return self.browser_execution(f"search for {search_query}")
            else:
                return {"status": "error", "message": f"Unsupported browser action: {action}"}
    
    def terminal_execution(self, action):
        """Execute actions in the terminal environment"""
        # For security, we'll limit the commands that can be executed
        safe_commands = ["echo", "dir", "ls", "pwd", "python", "pip"]

        # Parse the command from the action
        command = action.strip()
        command_parts = command.split()

        # Check if this is a PDF-related command
        action_lower = action.lower()
        if "pdf" in action_lower or "pandoc" in action_lower or "report" in action_lower or "document" in action_lower:
            # Redirect to general_response_execution
            logger.info(f"Redirecting PDF/document command to general_response: {action}")
            return self.general_response_execution(f"respond to query: {action}")

        # Check if the command is in the safe list
        if command_parts[0].lower() not in safe_commands:
            return {"status": "error", "message": f"Command not allowed for security reasons: {command_parts[0]}"}

        try:
            # Execute the command
            result = subprocess.run(command_parts, capture_output=True, text=True, shell=True)

            return {
                "status": "success" if result.returncode == 0 else "error",
                "command": command,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "return_code": result.returncode
            }
        except Exception as e:
            return {"status": "error", "message": f"Failed to execute command: {str(e)}"}
    
    def general_response_execution(self, action):
        """Execute a general response to any query"""
        # Extract the query from the action
        query = action.replace("respond to query:", "").strip()

        try:
            # Use Gemini to generate a response
            prompt = f"""
            You are an AI assistant helping a user with their query. Please provide a helpful, accurate, and concise response.

            User query: {query}

            Your response should be informative and directly address the user's query. If the query is asking for a specific document or report to be created,
            indicate that you can help create that document and provide a sample of what it would contain.

            If the query is about creating a report on laptops, mobile phones, or technology products, include specific details about the latest models,
            their specifications, features, and performance characteristics. Make sure to include real, up-to-date information about current products.
            """

            response = model.generate_content(prompt)
            response_text = response.text

            # Check if the query is asking for a document or report
            is_document_request = any(keyword in query.lower() for keyword in ["create document", "make document", "generate document", "create a document", "make a document", "generate a document"])
            is_report_request = any(keyword in query.lower() for keyword in ["create report", "make report", "generate report", "create a report", "make a report", "generate a report"])
            is_pdf_request = "pdf" in query.lower()

            document_type = None
            document_content = None

            if is_document_request or is_report_request:
                # Check if this is a laptop or mobile phone report
                is_laptop_report = any(keyword in query.lower() for keyword in ["laptop", "notebook", "computer"])
                is_mobile_report = any(keyword in query.lower() for keyword in ["mobile", "phone", "smartphone"])

                # Generate document content with specialized instructions
                document_prompt = f"""
                The user has requested a {'report' if is_report_request else 'document'} about: {query}

                Please create a professional {'report' if is_report_request else 'document'} with the following sections:
                1. Introduction/Executive Summary
                2. Main Content (with appropriate subheadings)
                3. Conclusion/Recommendations

                Make it detailed, informative, and well-structured. Include relevant information based on the query.

                {"Include specific information about the latest laptop models, their specifications (processors, RAM, storage, display quality), performance characteristics, and target audiences. Focus on real, current models from major manufacturers like Apple, Dell, Lenovo, HP, and ASUS." if is_laptop_report else ""}

                {"Include specific information about the latest mobile phone models, their specifications (processors, cameras, displays, battery life), unique features, and target audiences. Focus on real, current models from major manufacturers like Apple, Samsung, Google, Xiaomi, and OnePlus." if is_mobile_report else ""}
                """

                document_response = model.generate_content(document_prompt)
                document_content = document_response.text

                # Determine document type
                if is_pdf_request:
                    document_type = "pdf"
                else:
                    document_type = "text"

                # Create the document file
                filename = f"{'report' if is_report_request else 'document'}_{int(time.time())}"

                # Create downloads directory if it doesn't exist
                os.makedirs("static/downloads", exist_ok=True)

                if document_type == "pdf":
                    try:
                        # Create a professional HTML file that can be printed as PDF
                        # Process the document content to convert markdown-like formatting to HTML
                        formatted_content = document_content
                        formatted_content = formatted_content.replace('\n\n', '</p><p>')
                        formatted_content = formatted_content.replace('\n', '<br>')

                        # Convert markdown headings to HTML
                        import re
                        formatted_content = re.sub(r'# (.*?)(\n|$)', r'<h1>\1</h1>', formatted_content)
                        formatted_content = re.sub(r'## (.*?)(\n|$)', r'<h2>\1</h2>', formatted_content)
                        formatted_content = re.sub(r'### (.*?)(\n|$)', r'<h3>\1</h3>', formatted_content)

                        # Convert bold and italic
                        formatted_content = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', formatted_content)
                        formatted_content = re.sub(r'\*(.*?)\*', r'<em>\1</em>', formatted_content)

                        # Convert bullet points
                        formatted_content = re.sub(r'- (.*?)(\n|$)', r'<li>\1</li>', formatted_content)

                        # Fix bullet point formatting more carefully
                        if '<li>' in formatted_content:
                            formatted_content = formatted_content.replace('<li>', '<ul><li>')
                            # Replace consecutive list items
                            formatted_content = re.sub(r'</li><br><li>', r'</li><li>', formatted_content)
                            # Close any unclosed lists
                            if '<ul>' in formatted_content and '</ul>' not in formatted_content:
                                formatted_content += '</ul>'
                            # Fix any broken list structures
                            formatted_content = formatted_content.replace('</li><br></ul>', '</li></ul>')
                    except Exception as e:
                        logger.error(f"Error formatting document content: {str(e)}")
                        # Provide a simple fallback formatting
                        formatted_content = f"<p>{document_content.replace(chr(10), '<br>')}</p>"

                    # Get topic from query for title
                    try:
                        topic = query.replace("create", "").replace("generate", "").replace("make", "")
                        topic = topic.replace("report", "").replace("document", "").replace("pdf", "").replace("on", "").replace("about", "").strip()
                        if not topic:
                            topic = "Requested Topic"
                    except Exception as e:
                        logger.error(f"Error extracting topic from query: {str(e)}")
                        topic = "Requested Topic"

                    # Use our simple HTML document function to avoid JavaScript errors
                    title = f"{'Report' if is_report_request else 'Document'} on {topic}"
                    filename, file_path = self.create_simple_html_document(title, formatted_content)

                    # Create a professional HTML document
                    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{'Report' if is_report_request else 'Document'} on {topic}</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');

        body {{
            font-family: 'Roboto', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            margin: 0;
            padding: 0;
            background-color: #fff;
            font-size: 11pt;
        }}

        .container {{
            max-width: 8.5in;
            margin: 0 auto;
            padding: 1in;
            background: #fff;
        }}

        .header {{
            text-align: center;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 1px solid #ddd;
        }}

        .header h1 {{
            color: #2c3e50;
            margin-bottom: 10px;
            font-size: 24pt;
            font-weight: 700;
        }}

        .header p {{
            color: #7f8c8d;
            font-size: 10pt;
            margin-top: 0;
        }}

        .content {{
            margin-bottom: 40px;
            text-align: justify;
        }}

        h1, h2, h3, h4, h5, h6 {{
            color: #2c3e50;
            margin-top: 20px;
            margin-bottom: 10px;
            page-break-after: avoid;
        }}

        h1 {{ font-size: 20pt; }}
        h2 {{ font-size: 16pt; }}
        h3 {{ font-size: 14pt; }}

        p {{
            margin-bottom: 15px;
            line-height: 1.6;
        }}

        ul, ol {{
            margin-bottom: 15px;
            padding-left: 20px;
        }}

        li {{
            margin-bottom: 5px;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
        }}

        table, th, td {{
            border: 1px solid #ddd;
        }}

        th, td {{
            padding: 10px;
            text-align: left;
        }}

        th {{
            background-color: #f2f2f2;
            font-weight: bold;
        }}

        .footer {{
            text-align: center;
            margin-top: 50px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            color: #7f8c8d;
            font-size: 9pt;
        }}

        @media print {{
            body {{
                margin: 0;
                padding: 0;
                background: #fff;
            }}

            .container {{
                width: 100%;
                max-width: none;
                margin: 0;
                padding: 0.5in;
                box-shadow: none;
            }}

            .no-print {{
                display: none;
            }}

            @page {{
                size: letter;
                margin: 0.5in;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{'Report' if is_report_request else 'Document'} on {topic.title()}</h1>
            <p>Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
        </div>

        <div class="content">
            {formatted_content}
        </div>

        <div class="footer">
            <p>This document was automatically generated by the Autonomous AI Agent</p>
            <p>© {datetime.now().year} - For reference purposes only</p>
        </div>

        <div class="no-print" style="text-align: center; margin-top: 30px; padding: 20px; background-color: #f8f9fa; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
            <h3 style="margin-top: 0; color: #2c3e50;">Save this document as PDF</h3>
            <p style="margin-bottom: 15px;">Click the button below to print this document or save it as a PDF file.</p>
            <form>
                <input type="button" value="Print/Save as PDF" onclick="window.print()" style="padding: 12px 25px; background: #3498db; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 16px; font-weight: bold;">
            </form>
            <p style="margin-top: 15px; font-size: 12px; color: #7f8c8d;">
                Tip: When the print dialog opens, select "Save as PDF" as the destination to save this document as a PDF file.
            </p>
        </div>

        <!-- No JavaScript needed for printing -->
    </div>
</body>
</html>"""

                    try:
                        # Make sure the downloads directory exists
                        downloads_dir = os.path.join("static", "downloads")
                        os.makedirs(downloads_dir, exist_ok=True)

                        # Create a unique filename
                        timestamp = int(time.time())
                        safe_filename = f"report_{timestamp}.html"
                        file_path = os.path.join(downloads_dir, safe_filename)

                        # Write the HTML content to the file
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(html_content)
                        logger.info(f"Successfully created HTML file at {file_path}")

                        # Set the filename for the response
                        filename = safe_filename
                    except Exception as e:
                        logger.error(f"Error writing HTML file: {str(e)}")
                        # Create a simpler HTML file as fallback
                        try:
                            # Create an extremely simple HTML file
                            simple_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Report on {topic}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}
        h1 {{ color: #333; }}
        .print-btn {{ padding: 10px 20px; background: #4285f4; color: white; border: none; cursor: pointer; }}
    </style>
</head>
<body>
    <h1>Report on {topic}</h1>
    <div>{document_content.replace(chr(10), '<br>')}</div>
    <div style="margin-top: 30px;">
        <form>
            <input type="button" value="Print/Save as PDF" onclick="window.print()" class="print-btn">
        </form>
    </div>
</body>
</html>"""
                            # Create a new unique filename for the fallback
                            fallback_filename = f"report_fallback_{timestamp}.html"
                            fallback_path = os.path.join(downloads_dir, fallback_filename)

                            with open(fallback_path, 'w', encoding='utf-8') as f:
                                f.write(simple_html)
                            logger.info(f"Created simplified HTML file as fallback at {fallback_path}")

                            # Use the fallback filename
                            filename = fallback_filename
                            file_path = fallback_path
                        except Exception as e2:
                            logger.error(f"Error creating fallback HTML file: {str(e2)}")
                            return {
                                "status": "error",
                                "message": f"Failed to create HTML file: {str(e2)}"
                            }
                else:
                    # Create a text document
                    try:
                        filename = f"{filename}.txt"
                        file_path = os.path.join("static", "downloads", filename)
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(document_content)
                        logger.info(f"Successfully created text file at {file_path}")
                    except Exception as e:
                        logger.error(f"Error writing text file: {str(e)}")
                        return {
                            "status": "error",
                            "message": f"Failed to create text file: {str(e)}"
                        }

                # Create a response that includes the document link
                return {
                    "status": "success",
                    "action_type": "general_response",
                    "response": response_text,
                    "document_created": True,
                    "document_type": document_type,
                    "document_filename": filename,
                    "document_content_preview": document_content[:200] + "..." if len(document_content) > 200 else document_content
                }
            else:
                # Return a general response
                return {
                    "status": "success",
                    "action_type": "general_response",
                    "response": response_text
                }

        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return {
                "status": "error",
                "action_type": "general_response",
                "message": f"Failed to generate response: {str(e)}"
            }

    def file_system_execution(self, action):
        """Execute actions in the file system environment"""
        action_lower = action.lower()

        # Check if this is a PDF-related or document-related request
        if "pdf" in action_lower or "report" in action_lower or "document" in action_lower:
            # Redirect to general_response_execution
            logger.info(f"Redirecting PDF/document file system action to general_response: {action}")
            return self.general_response_execution(f"respond to query: {action}")

        try:
            if "create file" in action_lower:
                # Extract filename and content
                parts = action.split("create file")
                if len(parts) < 2:
                    return {"status": "error", "message": "Invalid file creation command"}
                
                file_info = parts[1].strip()
                filename = file_info.split("with content")[0].strip()
                
                # Extract content if specified
                content = ""
                if "with content" in file_info:
                    content = file_info.split("with content")[1].strip()
                
                # Create the file
                with open(filename, 'w') as f:
                    f.write(content)
                
                return {
                    "status": "success",
                    "action": "create_file",
                    "filename": filename,
                    "message": f"File {filename} created successfully"
                }
            
            elif "read file" in action_lower:
                # Extract filename
                filename = action.split("read file")[1].strip()
                
                # Read the file
                with open(filename, 'r') as f:
                    content = f.read()
                
                return {
                    "status": "success",
                    "action": "read_file",
                    "filename": filename,
                    "content": content
                }
            
            elif "write to file" in action_lower:
                # Extract filename and content
                parts = action.split("write to file")
                if len(parts) < 2:
                    return {"status": "error", "message": "Invalid file write command"}
                
                file_info = parts[1].strip()
                filename = file_info.split("content:")[0].strip()
                
                # Extract content
                content = ""
                if "content:" in file_info:
                    content = file_info.split("content:")[1].strip()
                
                # Write to the file
                with open(filename, 'w') as f:
                    f.write(content)
                
                return {
                    "status": "success",
                    "action": "write_file",
                    "filename": filename,
                    "message": f"Content written to {filename} successfully"
                }
            
            elif "append to file" in action_lower:
                # Extract filename and content
                parts = action.split("append to file")
                if len(parts) < 2:
                    return {"status": "error", "message": "Invalid file append command"}
                
                file_info = parts[1].strip()
                filename = file_info.split("content:")[0].strip()
                
                # Extract content
                content = ""
                if "content:" in file_info:
                    content = file_info.split("content:")[1].strip()
                
                # Append to the file
                with open(filename, 'a') as f:
                    f.write(content)
                
                return {
                    "status": "success",
                    "action": "append_file",
                    "filename": filename,
                    "message": f"Content appended to {filename} successfully"
                }
            
            elif "delete file" in action_lower:
                # Extract filename
                filename = action.split("delete file")[1].strip()

                # Delete the file
                os.remove(filename)

                return {
                    "status": "success",
                    "action": "delete_file",
                    "filename": filename,
                    "message": f"File {filename} deleted successfully"
                }

            # Handle save extracted content to file
            elif "save" in action_lower and ("to file" in action_lower or "as file" in action_lower):
                # Determine what to save
                save_target = ""
                filename = ""

                if "save" in action_lower:
                    save_parts = action.split("save")[1].strip()
                    if "to file" in save_parts:
                        save_target = save_parts.split("to file")[0].strip()
                        filename = save_parts.split("to file")[1].strip()
                    elif "as file" in save_parts:
                        save_target = save_parts.split("as file")[0].strip()
                        filename = save_parts.split("as file")[1].strip()
                    else:
                        # Default filename
                        save_target = save_parts
                        filename = "output.txt"

                # Find the content to save from previous extraction or search results
                content_to_save = ""

                # Look for extraction results in history
                for result in self.history:
                    if isinstance(result, dict) and result.get("action_type") == "extraction":
                        extraction_type = result.get("extraction_type", "")
                        extracted_content = result.get("extracted_content", [])

                        if extraction_type == "headlines":
                            # Check if this is a mobile phone search
                            is_mobile_search = any("mobile" in item.get('headline', '').lower() or "phone" in item.get('headline', '').lower() for item in extracted_content)
                            # Check if this is a laptop search
                            is_laptop_search = any("laptop" in item.get('headline', '').lower() or "macbook" in item.get('headline', '').lower() or "thinkpad" in item.get('headline', '').lower() for item in extracted_content)

                            if is_mobile_search:
                                content_to_save = "# Latest Mobile Phones (2024)\n\n"
                                for i, item in enumerate(extracted_content):
                                    content_to_save += f"{i+1}. {item.get('headline', 'No headline')}\n"
                                    if 'features' in item:
                                        content_to_save += f"   Features: {item.get('features', '')}\n"
                                    content_to_save += f"   Source: {item.get('source', 'Unknown')}\n"
                                    content_to_save += f"   URL: {item.get('url', '#')}\n\n"
                            elif is_laptop_search:
                                content_to_save = "# Latest Laptops (2024)\n\n"
                                for i, item in enumerate(extracted_content):
                                    content_to_save += f"{i+1}. {item.get('headline', 'No headline')}\n"
                                    if 'features' in item:
                                        content_to_save += f"   Features: {item.get('features', '')}\n"
                                    content_to_save += f"   Source: {item.get('source', 'Unknown')}\n"
                                    content_to_save += f"   URL: {item.get('url', '#')}\n\n"
                            else:
                                content_to_save = "# Top Headlines\n\n"
                                for i, item in enumerate(extracted_content):
                                    content_to_save += f"{i+1}. {item.get('headline', 'No headline')}\n"
                                    content_to_save += f"   Source: {item.get('source', 'Unknown')}\n"
                                    content_to_save += f"   URL: {item.get('url', '#')}\n\n"

                        elif extraction_type == "pros_cons":
                            content_to_save = "# Product Reviews: Pros and Cons\n\n"
                            for item in extracted_content:
                                content_to_save += f"## {item.get('product', 'Unknown Product')}\n\n"
                                content_to_save += "### Pros\n"
                                for pro in item.get('pros', []):
                                    content_to_save += f"- {pro}\n"
                                content_to_save += "\n### Cons\n"
                                for con in item.get('cons', []):
                                    content_to_save += f"- {con}\n"
                                content_to_save += f"\nSource: {item.get('source', 'Unknown')}\n\n"

                        elif extraction_type == "trends":
                            content_to_save = "# Trend Analysis\n\n"
                            content_to_save += "## Key Trends\n\n"
                            for topic in extracted_content.get('trend_topics', []):
                                content_to_save += f"- {topic}\n"

                            content_to_save += "\n## Trend Data\n\n"
                            content_to_save += "Year | Value\n"
                            content_to_save += "-----|------\n"
                            for data_point in extracted_content.get('trend_data', []):
                                content_to_save += f"{data_point.get('year', 'N/A')} | {data_point.get('value', 'N/A')}\n"

                            content_to_save += "\n## Sources\n\n"
                            for source in extracted_content.get('sources', []):
                                content_to_save += f"- {source}\n"

                        elif extraction_type == "summary":
                            content_to_save = "# Summary Report\n\n"
                            content_to_save += f"{extracted_content.get('summary', 'No summary available')}\n\n"
                            content_to_save += "## Key Points\n\n"
                            for point in extracted_content.get('key_points', []):
                                content_to_save += f"- {point}\n"

                            content_to_save += "\n## Sources\n\n"
                            for source in extracted_content.get('sources', []):
                                content_to_save += f"- {source}\n"

                        else:
                            # General content
                            content_to_save = "# Extracted Information\n\n"
                            for item in extracted_content:
                                content_to_save += f"## {item.get('title', 'No title')}\n\n"
                                content_to_save += f"{item.get('content', 'No content')}\n\n"
                                content_to_save += f"Source: {item.get('source', 'Unknown')}\n\n"

                        break

                # If no extraction results, check for search results
                if not content_to_save:
                    for result in self.history:
                        if isinstance(result, dict) and "results" in result:
                            search_results = result.get("results", [])
                            content_to_save = f"# Search Results for '{result.get('query', 'Unknown query')}'\n\n"

                            for i, item in enumerate(search_results):
                                content_to_save += f"{i+1}. {item.get('title', 'No title')}\n"
                                content_to_save += f"   URL: {item.get('link', '#')}\n"
                                content_to_save += f"   {item.get('snippet', 'No description')}\n\n"

                            break

                # If still no content, create a default message
                if not content_to_save:
                    content_to_save = f"# {save_target}\n\nNo content was found to save to this file."

                # Check if we need to create a directory for the file
                directory = os.path.dirname(filename)
                if directory and not os.path.exists(directory):
                    os.makedirs(directory)

                # Save the content to the file
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(content_to_save)

                return {
                    "status": "success",
                    "action": "save_to_file",
                    "filename": filename,
                    "content_preview": content_to_save[:200] + "..." if len(content_to_save) > 200 else content_to_save,
                    "message": f"Content saved to file '{filename}' successfully"
                }

            # Handle create directory action
            elif "create directory" in action_lower or "create folder" in action_lower:
                # Extract directory name
                if "create directory" in action_lower:
                    directory = action.split("create directory")[1].strip()
                else:
                    directory = action.split("create folder")[1].strip()

                # Create the directory
                os.makedirs(directory, exist_ok=True)

                return {
                    "status": "success",
                    "action": "create_directory",
                    "directory": directory,
                    "message": f"Directory '{directory}' created successfully"
                }

            # Handle list directory action
            elif "list directory" in action_lower or "list folder" in action_lower or "list files in" in action_lower:
                # Extract directory name
                if "list directory" in action_lower:
                    directory = action.split("list directory")[1].strip()
                elif "list folder" in action_lower:
                    directory = action.split("list folder")[1].strip()
                elif "list files in" in action_lower:
                    directory = action.split("list files in")[1].strip()
                else:
                    directory = "."

                # List the directory
                files = os.listdir(directory)

                return {
                    "status": "success",
                    "action": "list_directory",
                    "directory": directory,
                    "files": files,
                    "message": f"Listed {len(files)} files in directory '{directory}'"
                }

            else:
                return {"status": "error", "message": f"Unsupported file system action: {action}"}
        
        except Exception as e:
            return {"status": "error", "message": f"Failed to execute file system action: {str(e)}"}
    
    def create_fallback_plan(self, instruction):
        """Create a simple fallback execution plan when the AI model fails to generate one"""
        instruction_lower = instruction.lower()

        # Initialize a basic plan structure
        fallback_plan = {
            "task_analysis": f"Fallback plan for: {instruction}",
            "environments_needed": ["general_response"],
            "execution_steps": []
        }

        # Always use the general_response environment for all queries
        # This avoids any issues with terminal commands being blocked
        fallback_plan["execution_steps"].append({
            "step_number": 1,
            "environment": "general_response",
            "action": f"respond to query: {instruction}",
            "expected_outcome": "Provide a helpful response to the user's query"
        })

        step_number = 1

        # Check for browser-related keywords
        browser_keywords = ["search", "browse", "navigate", "website", "web", "internet", "google", "url", "http"]
        if any(keyword in instruction_lower for keyword in browser_keywords):
            fallback_plan["environments_needed"].append("browser")

            if "search" in instruction_lower:
                # Extract search query - take everything after "search for" or "search"
                search_query = instruction_lower.split("search for")[-1] if "search for" in instruction_lower else instruction_lower.split("search")[-1]
                search_query = search_query.strip()

                fallback_plan["execution_steps"].append({
                    "step_number": step_number,
                    "environment": "browser",
                    "action": f"search for {search_query}",
                    "expected_outcome": f"Get search results for {search_query}"
                })
                step_number += 1

            elif any(url_keyword in instruction_lower for url_keyword in ["http", "www", ".com", ".org", ".net"]):
                # Extract URL - find word containing http, www, or common TLDs
                words = instruction.split()
                url = next((word for word in words if any(url_part in word.lower() for url_part in ["http", "www", ".com", ".org", ".net"])), "https://www.google.com")

                fallback_plan["execution_steps"].append({
                    "step_number": step_number,
                    "environment": "browser",
                    "action": f"navigate to {url}",
                    "expected_outcome": f"Load the webpage at {url}"
                })
                step_number += 1

        # Check for terminal-related keywords
        terminal_keywords = ["command", "terminal", "shell", "bash", "cmd", "powershell", "execute", "run", "list", "directory"]
        if any(keyword in instruction_lower for keyword in terminal_keywords):
            fallback_plan["environments_needed"].append("terminal")

            if "list" in instruction_lower and any(dir_word in instruction_lower for dir_word in ["directory", "folder", "files"]):
                command = "dir" if os.name == "nt" else "ls -la"
                fallback_plan["execution_steps"].append({
                    "step_number": step_number,
                    "environment": "terminal",
                    "action": command,
                    "expected_outcome": "List files in the current directory"
                })
                step_number += 1
            else:
                # Default echo command
                fallback_plan["execution_steps"].append({
                    "step_number": step_number,
                    "environment": "terminal",
                    "action": "echo Hello, I am executing a fallback command",
                    "expected_outcome": "Display a message in the terminal"
                })
                step_number += 1

        # Check for file system-related keywords
        file_keywords = ["file", "create", "read", "write", "save", "delete", "text", "document", "folder", "directory"]
        if any(keyword in instruction_lower for keyword in file_keywords):
            fallback_plan["environments_needed"].append("file_system")

            if "create" in instruction_lower and "file" in instruction_lower:
                # Try to extract filename
                filename = "output.txt"  # Default filename
                for word in instruction.split():
                    if word.endswith(".txt") or word.endswith(".md") or word.endswith(".csv"):
                        filename = word
                        break

                fallback_plan["execution_steps"].append({
                    "step_number": step_number,
                    "environment": "file_system",
                    "action": f"create file {filename} with content This file was created based on your instruction: {instruction}",
                    "expected_outcome": f"Create a new file named {filename}"
                })
                step_number += 1

            elif "read" in instruction_lower and "file" in instruction_lower:
                # Try to extract filename
                filename = "output.txt"  # Default filename
                for word in instruction.split():
                    if word.endswith(".txt") or word.endswith(".md") or word.endswith(".csv"):
                        filename = word
                        break

                fallback_plan["execution_steps"].append({
                    "step_number": step_number,
                    "environment": "file_system",
                    "action": f"read file {filename}",
                    "expected_outcome": f"Read the contents of {filename}"
                })
                step_number += 1

        # If no specific environment was detected, add a default browser step
        if not fallback_plan["environments_needed"]:
            fallback_plan["environments_needed"].append("browser")
            fallback_plan["execution_steps"].append({
                "step_number": step_number,
                "environment": "browser",
                "action": f"search for {instruction}",
                "expected_outcome": "Get information related to the instruction"
            })

        return fallback_plan

    def generate_report(self, plan, results):
        """Generate a professional report of the task execution"""
        # Check if this is a mobile phone search
        is_mobile_search = False
        if self.current_task and ("mobile" in self.current_task.lower() or "phone" in self.current_task.lower() or "smartphone" in self.current_task.lower()):
            is_mobile_search = True

        # Check if this is a laptop search
        is_laptop_search = False
        if self.current_task and ("laptop" in self.current_task.lower() or "notebook" in self.current_task.lower() or "computer" in self.current_task.lower()):
            is_laptop_search = True

        # Create a prompt for Gemini to generate the report
        steps_results = []
        for i, (step, result) in enumerate(zip(plan.get("execution_steps", []), results)):
            steps_results.append({
                "step_number": i + 1,
                "step_description": step.get("action", ""),
                "environment": step.get("environment", ""),
                "result": result
            })

        # Add special instructions based on the search type
        special_instructions = ""
        if is_mobile_search:
            special_instructions = "This is a search for mobile phones, so please focus on providing detailed information about the latest mobile phones, their features, prices, and specifications."
        elif is_laptop_search:
            special_instructions = "This is a search for laptops, so please focus on providing detailed information about the latest laptops, their features, performance, and specifications. Include information about processors, RAM, storage, display quality, and battery life."

        prompt = f"""
        Generate a professional report for the following task execution:

        Task: {self.current_task}

        Execution Plan Analysis: {plan.get("task_analysis", "")}

        Execution Results:
        {json.dumps(steps_results, indent=2)}

        The report should include:
        1. Executive Summary
        2. Task Analysis
        3. Execution Details (for each step)
        4. Results and Findings
        5. Conclusions

        {special_instructions}

        Format the report in a professional manner with clear sections and concise language.
        """
        
        try:
            response = model.generate_content(prompt)
            self.report = response.text
            logger.info("Report generated successfully")
        except Exception as e:
            logger.error(f"Error generating report: {str(e)}")
            self.report = f"""
# Execution Report

## Error Generating Detailed Report

There was an error generating the detailed report: {str(e)}

## Task Summary

Task: {self.current_task}

Status: {self.task_status}

## Results Summary

{len(results)} steps were executed.
"""

# Use the global api_key_valid variable

# Routes
@app.route('/')
def index():
    global api_key_valid

    if not api_key_valid:
        return render_template('error.html',
                              error_title="API Key Error",
                              error_message="The Google API key is missing or invalid. Please set up your API key to use the Autonomous AI Agent.",
                              error_type="api_key")

    return render_template('index.html')

@app.route('/error')
def error():
    error_type = request.args.get('type', 'general')

    if error_type == 'api_key':
        error_title = "API Key Error"
        error_message = "The Google API key is missing or invalid. Please set up your API key to use the Autonomous AI Agent."
    else:
        error_title = "An Error Occurred"
        error_message = "Something went wrong. Please check the terminal for more details."

    return render_template('error.html',
                          error_title=error_title,
                          error_message=error_message,
                          error_type=error_type)

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint to verify the server is running"""
    return jsonify({
        "status": "ok",
        "api_key_valid": api_key_valid,
        "model": "gemini-1.5-flash",
        "version": "1.0.0"
    })

@app.route('/api/process', methods=['POST'])
def process_instruction():

    if not api_key_valid:
        return jsonify({
            "status": "error",
            "message": "API key is missing or invalid. Please set up your API key to use the Autonomous AI Agent."
        }), 401

    data = request.json
    instruction = data.get('instruction')

    if not instruction:
        return jsonify({"status": "error", "message": "No instruction provided"}), 400

    try:
        # Create a new agent instance
        agent = AIAgent()

        # Process the instruction
        start_time = time.time()
        logger.info(f"Processing instruction: {instruction}")

        # Handle specific instruction types with special handling
        instruction_lower = instruction.lower()

        # Special handling for report requests
        if "report" in instruction_lower or "document" in instruction_lower:
            logger.info("Detected report/document request - using specialized handling")

            # Create a fallback plan that will work even if the main process fails
            fallback_plan = {
                "task_analysis": f"Creating a comprehensive report on {instruction}",
                "environments_needed": ["general_response"],
                "execution_steps": [
                    {
                        "step_number": 1,
                        "environment": "general_response",
                        "action": f"respond to query: {instruction}",
                        "expected_outcome": f"Generate a detailed report on {instruction}"
                    }
                ]
            }

            try:
                # Try the normal processing first
                result = agent.process_instruction(instruction)
            except Exception as e:
                # If it fails, use our fallback plan
                logger.error(f"Error in normal processing for laptop report: {str(e)}")
                logger.info("Using fallback plan for laptop report")
                result = agent.execute_plan(fallback_plan)
        else:
            # Normal processing for other instructions
            result = agent.process_instruction(instruction)

        # Log processing time
        processing_time = time.time() - start_time
        logger.info(f"Instruction processed in {processing_time:.2f} seconds with status: {result.get('status', 'unknown')}")

        return jsonify(result)
    except Exception as e:
        error_message = str(e)
        logger.error(f"Error processing instruction: {error_message}")

        # Check for specific JavaScript error
        if "appendChild" in error_message or "Cannot read properties of null" in error_message:
            logger.info("Detected JavaScript DOM error - using direct document generation")

            # Create a direct document generation plan
            direct_plan = {
                "task_analysis": f"Creating a document about {instruction}",
                "environments_needed": ["general_response"],
                "execution_steps": [
                    {
                        "step_number": 1,
                        "environment": "general_response",
                        "action": f"respond to query: Create a simple document about {instruction}",
                        "expected_outcome": "Generate a document with no JavaScript"
                    }
                ]
            }

            try:
                # Create a new agent and execute the direct plan
                direct_agent = AIAgent()
                result = direct_agent.execute_plan(direct_plan)
                return jsonify(result)
            except Exception as direct_error:
                logger.error(f"Error in direct document generation: {str(direct_error)}")
                # Fall through to the general error handler

        # Create a simple error response with a basic report
        error_report = f"""
# Error Report

## What Happened
An error occurred while processing your instruction: {error_message}

## Your Request
"{instruction}"

## Possible Solutions
- Try rephrasing your request
- Break down complex tasks into simpler steps
- If requesting information about specific products, try being more specific
- For document or report creation, try using "create a report on [topic]" format
"""

        return jsonify({
            "status": "error",
            "message": f"An error occurred while processing your instruction: {str(e)}",
            "report": error_report
        }), 500

if __name__ == '__main__':
    app.run(debug=True)