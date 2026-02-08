# Med Help USA - Senior Care Voice Intake Agent

A LiveKit-based AI voice agent for Med Help USA that handles senior care intake calls with empathy and professionalism. The agent ("Sarah") speaks naturally, collects lead information, and saves it to Supabase.

## 🌟 Features

- **Natural Voice Interaction** - Uses OpenAI Realtime API for human-like conversation
- **Multi-Language Support** - English, Spanish, Arabic, French, Hindi, Italian
- **Senior-Friendly Design** - Slow speech, patient listening, clear confirmations
- **Spell-Back Verification** - Confirms names, phone numbers, and emails letter-by-letter
- **Supabase Integration** - Automatically saves intake leads to database
- **Emergency Protocol** - Detects emergencies and directs callers to 911

## 📋 Prerequisites

Before running this project, ensure you have:

- **Python 3.10+** (tested on Python 3.14)
- **OpenAI API Key** with Realtime API access
- **Supabase Account** (free tier works)
- **LiveKit Server** (local development server)

## 🚀 Quick Start

### Step 1: Clone & Navigate
```bash
cd medicare-01
```

### Step 2: Install Python Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Download LiveKit Server
1. Go to: https://github.com/livekit/livekit/releases
2. Download the latest release for your OS:
   - **Windows**: `livekit_X.X.X_windows_amd64.zip`
   - **macOS**: `livekit_X.X.X_darwin_amd64.tar.gz`
   - **Linux**: `livekit_X.X.X_linux_amd64.tar.gz`
3. Extract and place `livekit-server` executable in project folder

### Step 4: Create Environment File
Create a `.env` file in the project root:

```env
# OpenAI API Key (Required)
OPENAI_API_KEY=sk-your-openai-api-key-here

# Supabase Credentials (Required)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key-here
```

### Step 5: Setup Supabase Table (First Time Only)
```bash
python supabase_setup.py
```
Follow the on-screen instructions to create the `save_intake_lead` table in your Supabase dashboard.

### Step 6: Start LiveKit Server
Open a terminal and run:
```bash
# Windows
.\livekit-server.exe --dev

# macOS/Linux
./livekit-server --dev
```

### Step 7: Run the Voice Agent
In a new terminal:
```bash
python main.py console
```

## 📁 Project Structure

```
medicare-01/
├── main.py                 # Entry point - starts the voice agent
├── requirements.txt        # Python dependencies
├── supabase_client.py      # Supabase database client
├── supabase_setup.py       # Database table setup script
├── .env                    # Environment variables (create this)
├── agent/
│   ├── __init__.py
│   └── intake_agent.py     # Main agent logic & conversation flow
└── README.md               # This file
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENAI_API_KEY` | Your OpenAI API key | Yes |
| `SUPABASE_URL` | Your Supabase project URL | Yes |
| `SUPABASE_SERVICE_ROLE_KEY` | Supabase service role key | Yes |

### Agent Settings (in `agent/intake_agent.py`)

| Setting | Default | Description |
|---------|---------|-------------|
| `AGENT_VOICE_NAME` | `shimmer` | OpenAI voice (warm, female) |
| `SENIOR_PAUSE_THRESHOLD` | `0.8` | Seconds to wait before responding |

## 📞 Conversation Flow

The agent follows this structured flow:

1. **Warm Opener** - Greets caller, offers language options
2. **Safety Check** - Collects name and callback number (with spell-back)
3. **Deep Empathy** - Listens to caller's situation with validation
4. **Solution Pitch** - Explains Med Help USA services
5. **Email Collection** - Gets email for follow-up (with spell-back)
6. **Assessment** - 3 quick health questions (mobility, cognition, hygiene)
7. **Closing** - Confirms next steps, saves lead to database

## 🗄️ Database Schema

The `save_intake_lead` table stores:
- Caller name & callback number
- Language preference
- Email address & SMS consent
- Care recipient (self/loved one)
- Age group & health assessment
- Situation notes & timestamps

## 🔍 Troubleshooting

### Common Issues

| Error | Solution |
|-------|----------|
| `Missing Supabase credentials` | Create `.env` file with SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY |
| `OpenAI API key not found` | Add OPENAI_API_KEY to `.env` file |
| `Cannot connect to LiveKit` | Make sure livekit-server is running with `--dev` flag |
| `Module not found` | Run `pip install -r requirements.txt` |
| `Table does not exist` | Run `python supabase_setup.py` and create table in Supabase |

### Checking Your Setup
```bash
# Verify Python version (need 3.10+)
python --version

# Verify packages installed
pip list | grep livekit

# Test Supabase connection
python supabase_setup.py
```

## 📝 License

See [LICENSE](LICENSE) file.

## 🏢 About Med Help USA

Med Help USA provides premium private-pay senior care services, established in 2009. Based in Royal Oak, Michigan, serving families nationwide.

---

**Need Help?** Visit [MedHelpUSA.com](https://medhelpusa.com) or contact the development team.
