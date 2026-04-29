https://devteam-ai-pbzhsfqzakzw8frf5wwpl7.streamlit.app/
# DevTeam AI - Autonomous AI Software Engineer

DevTeam AI is a production-grade, autonomous software engineering platform that can generate complete, professional, full-stack projects directly from a text prompt.

## Features

- **Multi-Agent Architecture**: Uses a stateful LangGraph pipeline orchestrating multiple specialized agents.
- **Enterprise-Grade**: Outputs full codebase architectures with professional folder structure.
- **Dynamic File Generation**: Generates APIs, frontend, configs, database models, etc.
- **Interactive UI**: A stunning, premium glassmorphism dark-mode UI to enter prompts and view live logs.
- **Exporting**: Download the generated source code as a professional ZIP package.

## Agents

The AI team is composed of the following autonomous agents:
1. **Requirement Analyzer**: Extracts features and tech stack.
2. **Architect**: Designs project structure and module logic.
3. **Coder**: Generates valid code files.
4. **Reviewer**: Inspects code for quality and standards.
5. **Debugger**: Corrects syntactic or logical issues.
6. **Tester**: Generates unit and integration tests.
7. **Documentation**: Writes READMEs and setup guides.
8. **Packager**: Saves files to disk and builds a downloadable ZIP.

## Setup Instructions

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Environment Variables**:
   Create a `.env` file in the root directory and add your Groq API key:
   ```env
   GROQ_API_KEY=your_groq_api_key_here
   ```

3. **Run the Server**:
   ```bash
   python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

4. **Access the Application**:
   Open `http://localhost:8000` in your web browser.

## API Documentation

- `POST /generate`: Start a new project generation workflow.
- `GET /status/{run_id}`: Check live status and logs of the running workflow.
- `GET /files/{run_id}`: Retrieve generated files in JSON format.
- `GET /download/{run_id}`: Download the full source code as a ZIP.
- `GET /preview/{run_id}`: Get a code preview in JSON format.
