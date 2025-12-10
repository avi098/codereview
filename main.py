from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from strands import Agent, tool
from strands.models import BedrockModel
from dotenv import load_dotenv
import os
import json
import asyncio
import re

load_dotenv()

os.environ['AWS_ACCESS_KEY_ID'] = os.getenv('AWS_ACCESS_KEY_ID')
os.environ['AWS_SECRET_ACCESS_KEY'] = os.getenv('AWS_SECRET_ACCESS_KEY')
os.environ['AWS_DEFAULT_REGION'] = os.getenv('AWS_REGION', 'us-east-1')

app = FastAPI(title="Code Review Assistant")

# Initialize Jinja2 templates
templates = Jinja2Templates(directory="templates")

bedrock = BedrockModel(
    model_id=os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-5-sonnet-20240620-v1:0"),
    region_name=os.getenv("AWS_REGION", "us-east-1")
)

@tool
def analyze_security_patterns(code: str, pattern_type: str) -> dict:
    """
    Analyzes code for specific security vulnerability patterns.
    
    Args:
        code: The code snippet to analyze
        pattern_type: Type of security pattern (sql_injection, xss, auth, secrets, csrf, input_validation)
    
    Returns:
        Dictionary containing vulnerability findings with severity and recommendations
    """
    patterns = {
        'sql_injection': {
            'indicators': ['execute(', 'query(', 'raw(', 'filter(', 'SELECT', 'INSERT', 'UPDATE', 'DELETE'],
            'severity': 'Critical',
            'description': 'Potential SQL injection vulnerability detected'
        },
        'xss': {
            'indicators': ['innerHTML', 'dangerouslySetInnerHTML', 'document.write', 'eval('],
            'severity': 'High',
            'description': 'Potential XSS vulnerability detected'
        },
        'auth': {
            'indicators': ['password', 'token', 'session', 'auth', 'login', 'credential'],
            'severity': 'High',
            'description': 'Authentication/Authorization pattern detected'
        },
        'secrets': {
            'indicators': ['api_key', 'secret', 'password =', 'token =', 'AWS_', 'SECRET_KEY'],
            'severity': 'Critical',
            'description': 'Potential hardcoded secrets detected'
        },
        'csrf': {
            'indicators': ['POST', 'PUT', 'DELETE', 'form', 'csrf'],
            'severity': 'Medium',
            'description': 'CSRF protection check required'
        },
        'input_validation': {
            'indicators': ['input(', 'request.', 'params', 'query', 'body'],
            'severity': 'High',
            'description': 'Input validation required'
        }
    }
    
    if pattern_type not in patterns:
        return {'error': f'Unknown pattern type: {pattern_type}'}
    
    pattern = patterns[pattern_type]
    findings = []
    
    for indicator in pattern['indicators']:
        if indicator.lower() in code.lower():
            findings.append({
                'indicator': indicator,
                'severity': pattern['severity'],
                'description': pattern['description'],
                'found': True
            })
    
    return {
        'pattern_type': pattern_type,
        'findings': findings,
        'total_findings': len(findings),
        'severity': pattern['severity'] if findings else 'None'
    }

@tool
def calculate_complexity_metrics(code: str) -> dict:
    """
    Calculates code complexity metrics for performance analysis.
    
    Args:
        code: The code to analyze
    
    Returns:
        Dictionary containing complexity metrics and performance indicators
    """
    lines = code.split('\n')
    total_lines = len(lines)
    
    nested_loops = 0
    loops = ['for ', 'while ', 'foreach']
    db_queries = code.lower().count('query') + code.lower().count('select') + code.lower().count('find(')
    
    nesting_level = 0
    max_nesting = 0
    for line in lines:
        if any(loop in line.lower() for loop in loops):
            nesting_level += 1
            max_nesting = max(max_nesting, nesting_level)
            if nesting_level > 1:
                nested_loops += 1
        if '}' in line or 'end' in line.lower():
            nesting_level = max(0, nesting_level - 1)
    
    async_operations = code.lower().count('async') + code.lower().count('await') + code.lower().count('promise')
    blocking_operations = code.lower().count('sleep') + code.lower().count('thread.') + code.lower().count('lock')
    
    complexity_score = (
        (nested_loops * 3) + 
        (db_queries * 2) + 
        (blocking_operations * 4) + 
        (max_nesting * 2)
    )
    
    if complexity_score > 20:
        complexity_level = 'High'
        impact = 'Significant performance issues likely'
    elif complexity_score > 10:
        complexity_level = 'Medium'
        impact = 'Moderate performance concerns'
    else:
        complexity_level = 'Low'
        impact = 'Good performance characteristics'
    
    return {
        'total_lines': total_lines,
        'nested_loops': nested_loops,
        'database_queries': db_queries,
        'async_operations': async_operations,
        'blocking_operations': blocking_operations,
        'max_nesting_level': max_nesting,
        'complexity_score': complexity_score,
        'complexity_level': complexity_level,
        'performance_impact': impact
    }

@tool
def assess_code_quality_metrics(code: str) -> dict:
    """
    Assesses readability and maintainability metrics.
    
    Args:
        code: The code to analyze
    
    Returns:
        Dictionary containing quality metrics and improvement suggestions
    """
    lines = code.split('\n')
    total_lines = len([l for l in lines if l.strip()])
    comment_lines = len([l for l in lines if l.strip().startswith('#') or l.strip().startswith('//')])
    
    long_lines = len([l for l in lines if len(l) > 100])
    
    function_count = (
        code.lower().count('def ') + 
        code.lower().count('function ') + 
        code.lower().count('const ') +
        code.lower().count('let ') +
        code.lower().count('var ')
    )
    
    avg_function_length = total_lines / max(function_count, 1)
    
    naming_issues = []
    if any(char in code for char in ['a=', 'b=', 'x=', 'y=', 'temp=', 'tmp=']):
        naming_issues.append('Short/unclear variable names detected')
    
    has_error_handling = 'try' in code.lower() and ('catch' in code.lower() or 'except' in code.lower())
    has_documentation = '"""' in code or '///' in code or '/**' in code
    
    comment_ratio = comment_lines / max(total_lines, 1) * 100
    
    quality_score = 0
    quality_score += min(30, comment_ratio * 3)
    quality_score += 20 if has_error_handling else 0
    quality_score += 15 if has_documentation else 0
    quality_score += 20 if avg_function_length < 30 else 10 if avg_function_length < 50 else 0
    quality_score += 15 if long_lines < total_lines * 0.1 else 5
    
    return {
        'total_lines': total_lines,
        'comment_lines': comment_lines,
        'comment_ratio': round(comment_ratio, 2),
        'long_lines': long_lines,
        'function_count': function_count,
        'avg_function_length': round(avg_function_length, 2),
        'has_error_handling': has_error_handling,
        'has_documentation': has_documentation,
        'naming_issues': naming_issues,
        'quality_score': round(quality_score, 2),
        'quality_level': 'High' if quality_score > 70 else 'Medium' if quality_score > 40 else 'Low'
    }

code_review_agent = Agent(
    model=bedrock,
    tools=[
        analyze_security_patterns,
        calculate_complexity_metrics,
        assess_code_quality_metrics
    ],
    system_prompt="""You are an expert Code Review Assistant. You must provide a structured analysis with EXACTLY these four sections:

## SECURITY ANALYSIS
Use analyze_security_patterns tool to check all pattern types: sql_injection, xss, auth, secrets, csrf, input_validation.
Provide clear findings with severity levels and specific recommendations.

## PERFORMANCE ANALYSIS
Use calculate_complexity_metrics tool to evaluate performance.
Discuss complexity, bottlenecks, and optimization opportunities.

## READABILITY ANALYSIS
Use assess_code_quality_metrics tool to assess code quality.
Discuss maintainability, documentation, and coding standards.

## COMPREHENSIVE SUMMARY
Provide:
1. Overall Code Quality Score (1-10)
2. Critical Issues
3. High Priority Recommendations
4. Medium Priority Improvements
5. Overall Assessment

You MUST use these exact section headers with ## prefix. Complete all sections in a single response."""
)

def extract_text_from_result(result) -> str:
    """Extract text content from Strands Agent result"""
    try:
        if isinstance(result, str):
            return result
        
        if hasattr(result, 'last_message'):
            msg = result.last_message
            if isinstance(msg, str):
                return msg
            if isinstance(msg, dict):
                if 'content' in msg:
                    content = msg['content']
                    if isinstance(content, list) and len(content) > 0:
                        if isinstance(content[0], dict) and 'text' in content[0]:
                            return content[0]['text']
                    return str(content)
                if 'text' in msg:
                    return str(msg['text'])
            if isinstance(msg, list) and len(msg) > 0:
                if isinstance(msg[0], dict) and 'text' in msg[0]:
                    return msg[0]['text']
        
        if hasattr(result, 'message'):
            msg = result.message
            if isinstance(msg, str):
                return msg
            if isinstance(msg, dict):
                if 'content' in msg:
                    return str(msg['content'])
                if 'text' in msg:
                    return str(msg['text'])
        
        if isinstance(result, dict):
            if 'last_message' in result:
                return str(result['last_message'])
            if 'message' in result:
                return str(result['message'])
            if 'content' in result:
                return str(result['content'])
            if 'text' in result:
                return str(result['text'])
        
        return str(result)
        
    except Exception as e:
        return str(result)

def parse_sections(full_response: str) -> dict:
    """Parse the agent's response into sections"""
    sections = {
        'security': '',
        'performance': '',
        'readability': '',
        'summary': ''
    }
    
    if not isinstance(full_response, str):
        full_response = str(full_response)
    
    pattern = r'##\s+(SECURITY ANALYSIS|PERFORMANCE ANALYSIS|READABILITY ANALYSIS|COMPREHENSIVE SUMMARY)'
    parts = re.split(pattern, full_response, flags=re.IGNORECASE)
    
    for i in range(1, len(parts), 2):
        if i + 1 < len(parts):
            section_name = parts[i].strip().upper()
            section_content = parts[i + 1].strip()
            
            if 'SECURITY' in section_name:
                sections['security'] = section_content
            elif 'PERFORMANCE' in section_name:
                sections['performance'] = section_content
            elif 'READABILITY' in section_name:
                sections['readability'] = section_content
            elif 'SUMMARY' in section_name or 'COMPREHENSIVE' in section_name:
                sections['summary'] = section_content
    
    return sections

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

async def generate_review_stream(code: str):
    """Generate streaming code review"""
    try:
        query = f"""Analyze this code following the exact structure with all four sections:

Code to analyze:
```
{code}
```

Provide your analysis with these exact section headers:
## SECURITY ANALYSIS
## PERFORMANCE ANALYSIS
## READABILITY ANALYSIS
## COMPREHENSIVE SUMMARY"""

        result = code_review_agent(query)
        full_analysis = extract_text_from_result(result)
        sections = parse_sections(full_analysis)
        
        section_order = ['security', 'performance', 'readability', 'summary']
        
        for section_name in section_order:
            yield f"data: {json.dumps({'type': 'section_start', 'section': section_name})}\n\n"
            
            content = sections[section_name].strip()
            if content:
                for i in range(0, len(content), 50):
                    chunk = content[i:i+50]
                    yield f"data: {json.dumps({'type': 'content', 'section': section_name, 'content': chunk})}\n\n"
                    await asyncio.sleep(0.01)
            else:
                yield f"data: {json.dumps({'type': 'content', 'section': section_name, 'content': 'No specific issues found in this category.'})}\n\n"
            
            yield f"data: {json.dumps({'type': 'section_complete', 'section': section_name})}\n\n"
        
        yield f"data: {json.dumps({'type': 'complete'})}\n\n"
        
    except Exception as e:
        error_message = f"{type(e).__name__}: {str(e)}"
        yield f"data: {json.dumps({'type': 'error', 'message': error_message})}\n\n"

@app.post("/review")
async def review_code(code: str = Form(...)):
    return StreamingResponse(
        generate_review_stream(code),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no"
        }
    )

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "Code Review Assistant",
        "model_provider": "Amazon Bedrock",
        "model_id": os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-5-sonnet-20240620-v1:0"),
        "region": os.getenv("AWS_REGION", "us-east-1")
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8080)