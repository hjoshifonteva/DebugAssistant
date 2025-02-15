# AI Debug Assistant

An intelligent debug assistant powered by GPT-4 that can help with code analysis, voice commands, and system automation.

## Features

- 🎙️ Voice Commands & Chat Interface
- 🔍 Code Analysis & Debugging
- 🖥️ System Control (VS Code, Browsers)
- 🗣️ Text-to-Speech Responses
- 📷 Screen Reading Capability
- 🧠 GPT-4 Integration

## Setup

1. Clone the repository:
```bash
git clone https://github.com/hjoshifonteva/DebugAssistant.git
cd DebugAssistant
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# OR
.venv\Scripts\activate     # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file with your OpenAI API key:
```
OPENAI_API_KEY=your_api_key_here
```

5. Install Tesseract OCR:
- Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki
- Linux: `sudo apt-get install tesseract-ocr`
- Mac: `brew install tesseract`

## Usage

1. Start the assistant:
```bash
python start_assistant.py
```

2. Available Commands:
- **Voice Control:**
  - "stop talking" - Interrupt speech
  - "read screen" - Read text from screen
  - "read code" - Read and analyze code

- **VS Code Control:**
  - "open vs code"
  - "create workspace python_project"
  - "open file example.py"

- **Browser Control:**
  - "open chrome"
  - "go to github.com"
  - "open firefox in private mode"

- **Window Management:**
  - "maximize vs code"
  - "minimize chrome"

- **General:**
  - Ask anything! AI will help
  - "help" - Show help
  - "quit" - Exit

## Requirements

- Python 3.8+
- OpenAI API key
- Tesseract OCR
- Windows/Linux/Mac OS

## Project Structure

```
ai_debug_assistant/
├── src/
│   ├── ai/               # AI integration
│   ├── utils/            # Utility functions
│   ├── command_processor.py
│   ├── system_controller.py
│   ├── voice_manager.py
│   └── main.py
├── requirements.txt
└── start_assistant.py
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.