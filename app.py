import subprocess
import sys

def install_package(package):
    """Install package if not available"""
    try:
        __import__(package)
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# Install required packages
try:
    install_package("groq")
    install_package("python-dotenv")
except:
    pass

import os
import gradio as gr
import requests
from groq import Groq
import json
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import re

# Get API keys from Hugging Face secrets (environment variables)
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
BLACKBOX_API_KEY = os.getenv('BLACKBOX_API_KEY')

# Initialize Groq client
client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

# BLACKBOX API configuration
BLACKBOX_API_URL = "https://api.blackbox.ai/v1/chat/completions"

def comprehensive_code_review(code: str) -> Dict[str, str]:
    """
    Perform comprehensive automated code review using Groq + Llama
    """
    if not client:
        return {
            "groq_review": "Error: Groq API key not configured. Please set GROQ_API_KEY in environment variables.",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "model": "error"
        }
    
    try:
        # Enhanced prompt for comprehensive code review
        review_prompt = f"""
        Perform a comprehensive automated code review for the following code:
        
        ```
        {code}
        ```
        
        Provide detailed analysis in the following categories:
        
        1. **CODE QUALITY ASSESSMENT**
           - Overall code quality score (1-10)
           - Readability and maintainability
           - Code structure and organization
        
        2. **STYLE & BEST PRACTICES**
           - Coding style compliance
           - Naming conventions
           - Best practices adherence
           - Documentation quality
        
        3. **BUG DETECTION**
           - Syntax errors
           - Logic errors
           - Potential runtime issues
           - Edge case handling
        
        4. **SECURITY ANALYSIS**
           - Security vulnerabilities
           - Input validation issues
           - Authentication/authorization concerns
           - Data exposure risks
        
        5. **PERFORMANCE OPTIMIZATION**
           - Performance bottlenecks
           - Memory usage optimization
           - Algorithm efficiency
           - Database query optimization (if applicable)
        
        6. **IMPROVEMENT SUGGESTIONS**
           - Specific code improvements
           - Refactoring recommendations
           - Alternative implementations
           - Testing suggestions
        
        7. **REVIEW COMMENTS**
           - Line-by-line review comments
           - Priority levels (Critical, High, Medium, Low)
           - Actionable recommendations
        
        Format your response with clear headings and provide specific examples where possible.
        """
        
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a senior software engineer and code review expert. Provide detailed, constructive, and actionable code review feedback."
                },
                {
                    "role": "user",
                    "content": review_prompt
                }
            ],
            model="llama3-8b-8192",
            temperature=0.1,
            max_tokens=2000,
            top_p=1,
            stream=False,
        )
        
        return {
            "groq_review": chat_completion.choices[0].message.content,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "model": "llama3-8b-8192"
        }
        
    except Exception as e:
        return {
            "groq_review": f"Error performing code review: {str(e)}",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "model": "error"
        }

def enhanced_blackbox_review(code: str, groq_review: str) -> str:
    """
    Enhanced BLACKBOX.AI review with focus on automated review features
    """
    if not BLACKBOX_API_KEY:
        return "Error: BLACKBOX API key not configured. Please set BLACKBOX_API_KEY in environment variables."
    
    try:
        headers = {
            "Authorization": f"Bearer {BLACKBOX_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "blackbox",
            "messages": [
                {
                    "role": "system",
                    "content": "You are BLACKBOX.AI, an expert automated code review assistant. Focus on providing additional insights, alternative solutions, and integration recommendations."
                },
                {
                    "role": "user",
                    "content": f"""
                    Original Code:
                    ```
                    {code}
                    ```
                    
                    Previous Review Analysis:
                    {groq_review}
                    
                    Please provide additional automated code review insights:
                    
                    1. **ADVANCED PATTERNS & ARCHITECTURE**
                       - Design pattern suggestions
                       - Architecture improvements
                       - SOLID principles compliance
                    
                    2. **FRAMEWORK-SPECIFIC RECOMMENDATIONS**
                       - Framework best practices
                       - Library usage optimization
                       - Integration patterns
                    
                    3. **SCALABILITY & MAINTAINABILITY**
                       - Long-term maintainability
                       - Scalability considerations
                       - Technical debt assessment
                    
                    4. **AUTOMATED TESTING SUGGESTIONS**
                       - Unit test recommendations
                       - Integration test strategies
                       - Mock and stub suggestions
                    
                    5. **DEPLOYMENT & DEVOPS CONSIDERATIONS**
                       - CI/CD pipeline compatibility
                       - Containerization readiness
                       - Configuration management
                    
                    Provide concrete, actionable recommendations with code examples where appropriate.
                    """
                }
            ],
            "temperature": 0.2,
            "max_tokens": 1500
        }
        
        response = requests.post(BLACKBOX_API_URL, headers=headers, json=payload)
        
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            return f"BLACKBOX.AI enhancement unavailable (Status: {response.status_code})"
            
    except Exception as e:
        return f"Error enhancing review with BLACKBOX.AI: {str(e)}"

def generate_review_summary(groq_review: str, blackbox_review: str) -> Dict[str, any]:
    """
    Generate a comprehensive review summary with metrics
    """
    # Extract key metrics (simplified implementation)
    issues_found = groq_review.count("issue") + groq_review.count("error") + groq_review.count("problem")
    suggestions_made = groq_review.count("suggest") + groq_review.count("recommend") + groq_review.count("improve")
    
    # Determine overall rating based on content analysis
    critical_keywords = ["critical", "security", "vulnerability", "bug", "error"]
    critical_issues = sum(1 for keyword in critical_keywords if keyword in groq_review.lower())
    
    if critical_issues > 3:
        overall_rating = "Needs Significant Improvement"
    elif critical_issues > 1:
        overall_rating = "Needs Improvement"
    elif issues_found > 5:
        overall_rating = "Good with Minor Issues"
    else:
        overall_rating = "Excellent"
    
    return {
        "overall_rating": overall_rating,
        "issues_found": issues_found,
        "suggestions_made": suggestions_made,
        "critical_issues": critical_issues,
        "review_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

def unified_code_analysis(code: str, analysis_type: str) -> Tuple[str, str, str, str, Dict]:
    """
    Unified analysis combining original functionality with automated code review
    """
    if analysis_type.lower() == "automated_review":
        # Perform comprehensive automated code review
        review_result = comprehensive_code_review(code)
        groq_analysis = review_result["groq_review"]
        
        # Enhance with BLACKBOX.AI
        blackbox_enhancement = enhanced_blackbox_review(code, groq_analysis)
        
        # Generate summary metrics
        summary_metrics = generate_review_summary(groq_analysis, blackbox_enhancement)
        
        # Create combined report
        combined_analysis = f"""
        # 🔍 Automated Code Review Report
        
        **Review Date:** {summary_metrics['review_date']}
        **Overall Rating:** {summary_metrics['overall_rating']}
        **Issues Found:** {summary_metrics['issues_found']}
        **Suggestions Made:** {summary_metrics['suggestions_made']}
        **Critical Issues:** {summary_metrics['critical_issues']}
        
        ---
        
        ## 🤖 Primary AI Review (Groq + Llama)
        {groq_analysis}
        
        ---
        
        ## 🚀 Enhanced Review (BLACKBOX.AI)
        {blackbox_enhancement}
        
        ---
        
        ## 📊 Review Summary
        This automated code review has identified **{summary_metrics['issues_found']} potential issues** and provided **{summary_metrics['suggestions_made']} improvement suggestions**. The code has been rated as **{summary_metrics['overall_rating']}**.
        """
        
        return groq_analysis, blackbox_enhancement, combined_analysis, f"**Review Rating:** {summary_metrics['overall_rating']}", summary_metrics
    
    else:
        return "Invalid analysis type", "", "", "Error", {}

def create_gradio_interface():
    """
    Create Gradio interface with proper markdown rendering
    """
    
    def analyze_code_interface(code_input: str, analysis_type: str) -> Tuple[str, str, str]:
        """
        Interface function for Gradio - Updated for 3 outputs only
        """
        if not code_input.strip():
            return "Please enter code to analyze.", "", ""
        
        # Check API configuration
        if not GROQ_API_KEY:
            error_msg = "⚠️ GROQ API key not configured. Please set GROQ_API_KEY in environment variables."
            return error_msg, error_msg, error_msg
            
        if not BLACKBOX_API_KEY:
            error_msg = "⚠️ BLACKBOX API key not configured. Please set BLACKBOX_API_KEY in environment variables."
            return error_msg, error_msg, error_msg
        
        try:
            groq_result, blackbox_result, combined_result, summary, metrics = unified_code_analysis(
                code_input, analysis_type.lower().replace(" ", "_")
            )
            return groq_result, combined_result, summary
        except Exception as e:
            error_msg = f"Analysis failed: {str(e)}"
            return error_msg, error_msg, error_msg
    
    # Create Gradio interface
    with gr.Blocks(
        title="🧠 AI Code Assistant - Automated Review",
        theme=gr.themes.Soft(),
        css="""
        .gradio-container {
            max-width: 1400px !important;
        }
        .code-input {
            font-family: 'Courier New', monospace;
            font-size: 14px;
        }
        .review-summary {
            background-color: #f0f8ff;
            padding: 10px;
            border-radius: 5px;
            border-left: 4px solid #4CAF50;
        }
        .markdown-output {
            max-height: 600px;
            overflow-y: auto;
            padding: 15px;
            background-color: #2d2d2d;
            border-radius: 8px;
            border: 1px solid #404040;
        }
        .markdown-output h1, .markdown-output h2, .markdown-output h3, .markdown-output h4, .markdown-output h5, .markdown-output h6 {
            color: #ffffff !important;
            font-weight: bold !important;
        }
        .markdown-output p, .markdown-output li {
            color: #e0e0e0 !important;
            line-height: 1.6 !important;
        }
        .markdown-output strong {
            color: #ffeb3b !important;
            font-weight: bold !important;
        }
        .markdown-output code {
            background-color: #1e1e1e !important;
            color: #4fc3f7 !important;
            padding: 2px 6px !important;
            border-radius: 4px !important;
        }
        .markdown-output pre {
            background-color: #1e1e1e !important;
            color: #4fc3f7 !important;
            padding: 10px !important;
            border-radius: 6px !important;
            overflow-x: auto !important;
        }
        """
    ) as demo:
        
        gr.Markdown("""
        # 🧠 AI Code Assistant
        ### Powered by BLACKBOX.AI, Groq API, and Llama Models
        
        **Features:**
        - 🤖 **Automated Code Review**: Comprehensive quality assessment and review comments
        - 🛡️ **Security Analysis**: Vulnerability detection and security recommendations
        - 📊 **Performance Optimization**: Intelligent suggestions for better performance
        - 📝 **Review Comments**: Generate detailed review comments for team collaboration
        """)
        
        with gr.Row():
            with gr.Column(scale=1):
                code_input = gr.Textbox(
                    label="📝 Enter Your Code",
                    placeholder="Paste your code here for automated review...",
                    lines=18,
                    elem_classes=["code-input"]
                )
                
                analysis_type = gr.Radio(
                    label="🔍 Analysis Type",
                    choices=["Automated Review"],
                    value="Automated Review",
                    info="Automated code review with comprehensive analysis"
                )
                
                analyze_btn = gr.Button("🚀 Analyze Code", variant="primary", size="lg")
                
                # Review summary box
                summary_box = gr.Textbox(
                    label="📊 Quick Summary",
                    lines=2,
                    interactive=False,
                    elem_classes=["review-summary"]
                )
                
            with gr.Column(scale=2):
                gr.Markdown("## 📊 Analysis Results")
                
                with gr.Tabs():
                    with gr.TabItem("🤖 Groq + Llama Analysis"):
                        groq_output = gr.Markdown(
                            value="Analysis results will appear here...",
                            elem_classes=["markdown-output"]
                        )
                    
                    with gr.TabItem("📋 Comprehensive Report"):
                        combined_output = gr.Markdown(
                            value="Comprehensive report will appear here...",
                            elem_classes=["markdown-output"]
                        )
        
        # Event handlers
        analyze_btn.click(
            fn=analyze_code_interface,
            inputs=[code_input, analysis_type],
            outputs=[groq_output, combined_output, summary_box]
        )
        
        # Example codes section
        gr.Markdown("## 📚 Example Codes for Testing")
        
        enhanced_examples = [
            ["Python - Security Vulnerability", """
import sqlite3
import os

def get_user_data(user_id):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    # SQL Injection vulnerability
    query = f"SELECT * FROM users WHERE id = {user_id}"
    cursor.execute(query)
    
    result = cursor.fetchone()
    conn.close()
    return result

def authenticate_user(username, password):
    # Hardcoded credentials - security issue
    if username == "admin" and password == "password123":
        return True
    return False

# No input validation
user_data = get_user_data(input("Enter user ID: "))
print(user_data)
"""],
            
            ["JavaScript - Performance Issues", """
// Inefficient DOM manipulation
function updateUserList(users) {
    const container = document.getElementById('user-list');
    container.innerHTML = ''; // Clearing DOM
    
    for (let i = 0; i < users.length; i++) {
        const div = document.createElement('div');
        div.innerHTML = `
            <h3>${users[i].name}</h3>
            <p>${users[i].email}</p>
            <button onclick="deleteUser(${users[i].id})">Delete</button>
        `;
        container.appendChild(div); // Multiple DOM operations
    }
}

// Memory leak potential
let globalCache = {};
function cacheUserData(userId, data) {
    globalCache[userId] = data; // Never cleaned up
}

// No error handling
async function fetchUserData(userId) {
    const response = await fetch(`/api/users/${userId}`);
    const data = response.json(); // Missing await
    return data;
}
"""],
            
            ["Python - Code Quality Issues", """
# Poor naming conventions and structure
def func1(x, y, z):
    # No docstring
    a = x + y
    b = a * z
    if b > 100:
        c = b / 2
    else:
        c = b * 2
    
    # Magic numbers
    d = c + 42
    e = d - 17
    
    # Nested conditions
    if e > 50:
        if e < 200:
            if e % 2 == 0:
                return e
            else:
                return e + 1
        else:
            return 200
    else:
        return 50

# Global variables
counter = 0
data_list = []

def process_data():
    global counter, data_list
    counter += 1
    data_list.append(counter)
    
    # Long function with multiple responsibilities
    for item in data_list:
        if item % 2 == 0:
            print(f"Even: {item}")
        else:
            print(f"Odd: {item}")
    
    # No error handling
    result = 10 / (counter - 10)  # Potential division by zero
    return result
"""]
        ]
        
        with gr.Row():
            for title, code in enhanced_examples:
                gr.Button(title, size="sm").click(
                    lambda c=code: c,
                    outputs=code_input
                )
        
        # Usage instructions
        gr.Markdown("""
        ## 🎯 How to Use the Automated Code Review
        
        ### 🤖 Automated Code Review
        - **Purpose**: Comprehensive code quality assessment and review comments
        - **Features**: Security analysis, performance optimization, style checking, bug detection
        - **Output**: Detailed review report with proper formatting and actionable suggestions
        
        ### 💡 Pro Tips
        - Use this tool for comprehensive code assessment before team reviews
        - Try the example codes to see different types of analysis
        - Results are properly formatted with bold headings and clear structure
        - Focus on **Critical** and **High** priority issues first
        
        ### 📊 What You'll Get
        - **Primary AI Analysis**: Detailed code review from Groq + Llama with proper formatting
        - **Comprehensive Report**: Combined analysis with actionable insights
        - **Quick Summary**: Overview of issues found and overall code rating
        """)
    
    return demo

# Launch the application
if __name__ == "__main__":
    demo = create_gradio_interface()
    demo.launch()
