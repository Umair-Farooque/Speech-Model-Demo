# Speech-to-Speech Voice Agent Demo

A real-time voice-to-voice AI assistant powered by LiveKit, OpenAI Whisper (STT), GPT-4o-mini (LLM), and OpenAI TTS.

## 🚀 Quick Start

### Prerequisites
- Python 3.9 or higher
- Valid OpenAI API key
- LiveKit Cloud account (or use the demo instance)

### Installation

1. **Clone the repository** (if not already done)

2. **Create a virtual environment**
```bash
python -m venv .venv
.venv\Scripts\activate  # On Windows
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**
   - Copy `.env.example` to `.env`
   - Add your actual API keys:
     ```
     LIVEKIT_URL=wss://your-livekit-instance.livekit.cloud
     LIVEKIT_API_KEY=your_api_key_here
     LIVEKIT_API_SECRET=your_api_secret_here
     OPENAI_API_KEY=sk-proj-your_openai_api_key_here
     ```

### Running the Demo

You need to run **TWO processes** in separate terminal windows:

**Terminal 1 - Token Server (Backend)**
```bash
python services/token_server.py
```
This starts the FastAPI server on `http://localhost:8000`

**Terminal 2 - Voice Agent**
```bash
python agent/main.py start
```
This starts the LiveKit voice agent

**Terminal 3 - Open the Frontend**
Open your browser to: `http://localhost:8000`

## 🎯 How It Works

1. **User clicks "Start Conversation"**
2. Frontend fetches a LiveKit token from the backend
3. Connects to LiveKit room with voice capabilities enabled
4. Voice Agent processes:
   - Speech → Text (OpenAI Whisper STT)
   - Text → AI Response (GPT-4o-mini)
   - AI Response → Speech (OpenAI TTS)
5. Real-time bidirectional voice conversation!

## 🛠️ Architecture

```
frontend/
  ├── index.html      # Main UI
  ├── app.js          # LiveKit client logic
  └── styles.css      # Glassmorphism design

agent/
  ├── main.py         # Voice agent entrypoint
  ├── config.py       # Configuration management
  ├── prompts.py      # System prompts
  └── memory.py       # Conversation memory

services/
  ├── token_server.py # FastAPI server for tokens
  ├── llm.py         # OpenAI LLM configuration
  ├── stt.py         # Speech-to-Text service
  └── tts.py         # Text-to-Speech service
```

## 🔐 Security Notes

- **Never commit `.env` file** - it contains your API keys
- Use `.env.example` as a template only
- Regenerate API keys if accidentally exposed
- For production, use proper secrets management

## 🎨 Features

- ✅ Real-time voice-to-voice interaction
- ✅ Visual feedback (orb animation when speaking)
- ✅ Connection status indicators
- ✅ Disconnect functionality
- ✅ Error handling and user feedback
- ✅ Conversation memory (10 turns)
- ✅ Modern glassmorphism UI

## 🐛 Troubleshooting

**Connection Failed**
- Verify your `.env` file has correct API keys
- Ensure both servers are running
- Check browser console for errors

**No Audio**
- Check microphone permissions in browser
- Verify audio output is working
- Check LiveKit connection status

**Agent Not Responding**
- Check Terminal 2 for agent logs
- Verify OpenAI API key is valid
- Ensure agent process started successfully

## 📝 License

MIT
