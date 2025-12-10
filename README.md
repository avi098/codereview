# Code Review Assistant

An intelligent code review tool powered by AWS Bedrock and Claude AI that provides comprehensive security, performance, and quality analysis for your code.

## Features

- **Security Analysis**: Detects SQL injection, XSS, authentication issues, hardcoded secrets, CSRF vulnerabilities, and input validation problems
- **Performance Analysis**: Evaluates code complexity, nested loops, database queries, and blocking operations
- **Readability Analysis**: Assesses code quality, documentation, naming conventions, and maintainability
- **Real-time Streaming**: Progressive analysis delivery with live updates
- **Comprehensive Reports**: Detailed findings with severity levels and actionable recommendations

## Tech Stack

- **Framework**: FastAPI
- **AI Model**: Anthropic Claude 3.5 Sonnet via AWS Bedrock
- **Agent Framework**: Strands Agents
- **Frontend**: HTML, CSS, JavaScript with Server-Sent Events (SSE)
- **Cloud**: AWS Bedrock

## Prerequisites

- Python 3.8+
- AWS Account with Bedrock access
- AWS IAM credentials with Bedrock permissions

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/avi098/code-review-assistant.git
   cd code-review-assistant
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   
   Create a `.env` file in the project root:
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` with your AWS credentials:
   ```env
   BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20240620-v1:0
   AWS_REGION=us-east-1
   AWS_ACCESS_KEY_ID=your_access_key_here
   AWS_SECRET_ACCESS_KEY=your_secret_key_here
   APP_ENV=development
   LOG_LEVEL=INFO
   HOST=127.0.0.1
   PORT=8080
   DEBUG=True
   REQUEST_TIMEOUT=300
   MAX_TOKENS=4096
   TEMPERATURE=0.7
   ENABLE_CORS=True
   ```

## AWS Bedrock Setup

1. **Enable Claude model access in AWS Bedrock**:
   - Go to AWS Console → Bedrock → Model access
   - Request access to Anthropic Claude models
   - Wait for approval (usually instant)

2. **Create IAM credentials** with the following policy:
   ```json
   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Effect": "Allow",
         "Action": [
           "bedrock:InvokeModel",
           "bedrock:InvokeModelWithResponseStream"
         ],
         "Resource": "arn:aws:bedrock:*::foundation-model/anthropic.claude-*"
       }
     ]
   }
   ```

## Usage

1. **Start the server**
   ```bash
   python main.py
   ```
   
   Or using uvicorn:
   ```bash
   uvicorn main:app --host 127.0.0.1 --port 8080 --reload
   ```

2. **Access the application**
   
   Open your browser and go to: `http://127.0.0.1:8080`

3. **Analyze your code**
   - Paste your code into the text area
   - Click "Analyze Code"
   - Watch as the AI provides real-time analysis across four categories:
     - Security Analysis
     - Performance Analysis
     - Readability Analysis
     - Comprehensive Summary

## API Endpoints

### `GET /`
Returns the main web interface

### `POST /review`
- **Content-Type**: `application/x-www-form-urlencoded`
- **Parameter**: `code` (string) - The code to analyze
- **Response**: Server-Sent Events (SSE) stream with progressive analysis

### `GET /health`
Health check endpoint returning service status and configuration

Example response:
```json
{
  "status": "healthy",
  "service": "Code Review Assistant",
  "model_provider": "Amazon Bedrock",
  "model_id": "anthropic.claude-3-5-sonnet-20240620-v1:0",
  "region": "us-east-1"
}
```

## Project Structure

```
code-review-assistant/
├── main.py                 # FastAPI application and agent logic
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables (not in git)
├── .env.example           # Environment variables template
├── .gitignore             # Git ignore rules
├── templates/
│   └── index.html         # Web interface
└── README.md              # This file
```

## Tools Used by the Agent

The code review agent uses three specialized tools:

1. **analyze_security_patterns**: Detects security vulnerabilities
   - SQL Injection
   - Cross-Site Scripting (XSS)
   - Authentication issues
   - Hardcoded secrets
   - CSRF vulnerabilities
   - Input validation problems

2. **calculate_complexity_metrics**: Analyzes performance
   - Nested loops
   - Database query count
   - Async/await operations
   - Blocking operations
   - Nesting levels
   - Complexity scoring

3. **assess_code_quality_metrics**: Evaluates maintainability
   - Comment ratio
   - Function length
   - Naming conventions
   - Error handling
   - Documentation
   - Code quality scoring

## Security Considerations

⚠️ **Important**: Never commit your `.env` file or AWS credentials to version control!

- The `.gitignore` file is configured to exclude sensitive files
- Always use `.env.example` as a template
- Rotate AWS credentials regularly
- Use IAM roles with minimal required permissions
- Consider using AWS Secrets Manager for production deployments

## Development

### Running in development mode
```bash
uvicorn main:app --reload --host 127.0.0.1 --port 8080
```

### Environment variables
- `DEBUG=True`: Enable debug mode
- `LOG_LEVEL=INFO`: Set logging level (DEBUG, INFO, WARNING, ERROR)
- `REQUEST_TIMEOUT=300`: Request timeout in seconds

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/)
- Powered by [Anthropic Claude](https://www.anthropic.com/claude) via AWS Bedrock
- Agent framework by [Strands](https://github.com/strands-ai/strands)

## Support

For issues, questions, or contributions, please open an issue on GitHub.

---
