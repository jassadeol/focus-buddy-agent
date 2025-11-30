# Focus Buddy – AI Concierge Agent for 25-Minute Focus Sessions

A multi-agent system powered by Google Gemini that transforms messy to-do lists into realistic 25-minute deep work plans.

**Track:** Concierge Agents  
**AI Model:** Google Gemini 2.0 Flash (Free Tier)  
**Concepts:** Multi-agent systems, Function calling, Session memory
---

##  Problem Statement

Knowledge workers face decision fatigue when choosing what to work on in short time windows. A long to-do list combined with limited time leads to:

- **Analysis paralysis** - spending 10 minutes deciding what to do in the next 20
- **Poor prioritization** - choosing easy tasks over important ones
- **Unrealistic planning** - cramming too much into too little time
- **Context switching** - starting multiple things and finishing nothing

Traditional to-do apps store tasks but don't help users make smart, time-bounded decisions about what to do *right now*.

---

##  Solution

**Focus Buddy** is an AI concierge agent that acts as your personal productivity coach. It:

1. **Understands messy input** - paste your tasks in any format
2. **Prioritizes intelligently** - considers urgency, impact, and your energy level
3. **Creates realistic plans** - schedules work that actually fits in 25 minutes
4. **Tracks progress** - checks in after sessions and learns from outcomes

---

##  Architecture

### Multi-Agent System

The system uses **two cooperating agent roles** orchestrated by a single Gemini model:

** Planner Agent**
- Parses unstructured task input into structured data
- Calculates priority scores based on urgency, impact, and time
- Generates time-bounded schedules with realistic task limits

** Coach Agent**  
- Presents plans in actionable, motivating format
- Confirms plans fit user context and energy
- Conducts post-session check-ins and tracks completion

### Function Calling (Tools)

Three Python functions enable structured workflow:

| Function | Input | Output | Purpose |
|----------|-------|--------|---------|
| `parse_tasks()` | Raw text | Task objects | Convert messy lists into structured data |
| `prioritize_tasks()` | Task list | Sorted tasks | Score and rank by urgency/importance |
| `create_focus_schedule()` | Tasks + time | Schedule blocks | Build timeline that fits available time |

### Session Memory

The agent maintains state across a focus session:
- Original task list
- Prioritized task queue  
- Current focus plan
- Completion status
- User energy level and preferences

This enables:
- Continuity between planning and check-in
- Learning from what gets completed vs. what doesn't
- Suggesting improvements for the next session

---

## 🎓 Course Concepts Demonstrated

### 1. Multi-Agent Systems
- Single LLM playing coordinated roles (Planner + Coach)
- Shared context and memory between roles
- Clear separation of concerns (analysis vs. interaction)

### 2. Function Calling / Tool Use
- Three custom Python tools with structured schemas
- Deterministic logic wrapped by AI orchestration
- Tool chaining (parse → prioritize → schedule)

### 3. Session Memory & State Management
- Persistent storage of focus plans across turns
- Tracking task completion between sessions
- Context retention for multi-sprint workflows

### 4. Evaluation Loop
- Post-session analysis of what worked
- Feedback-driven plan adjustments
- Continuous improvement of time estimates

---

## 🚀 Setup & Installation

### Prerequisites
- Python 3.10+
- Google Gemini API key (free tier available)

### Step 1: Get Your Free API Key

1. Go to https://aistudio.google.com/app/apikey
2. Click "Create API Key"
3. Copy the key (format: `AIzaSy...`)

### Step 2: Install Dependencies
```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/focus-buddy-agent.git
cd focus-buddy-agent

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install packages
pip install -r requirements.txt
```

### Step 3: Configure API Key
```bash
# Copy example environment file
cp .env.example .env

# Edit .env and add your key
echo "GEMINI_API_KEY=your_key_here" > .env
```

---

## Testing

### Test 1: Verify Tools Work
```bash
python tests/test_tools.py
```

**Expected output:**
```
Test 1: Parsing tasks...
✓ Parsed 4 tasks
  - Review 3 pull requests (10 min)
  - Fix authentication bug (15 min)
  - Write API documentation (10 min)
  - Reply to Sarah about Q4 planning (10 min)

Test 2: Prioritizing...
✓ Top priority: Fix authentication bug (score: 3.65)

Test 3: Creating schedule...
✓ Created 4 time blocks:
  0-15 min: Fix authentication bug
  15-25 min: Review 3 pull requests
  25-28 min: Wrap up & notes for next session
  
All tools working!
```

### Test 2: Run Full Agent
```bash
python tests/test_agent.py
```

### Test 3: Interactive Session
```bash
python src/gemini_agent.py
```

---

## Example Usage

### Input
```
User: I have 25 minutes before my next meeting and I'm pretty tired. 
Here's what I need to do:

- Review 3 open pull requests
- Fix the authentication bug (it's blocking QA)
- Write API documentation for the /users endpoint  
- Reply to Sarah about Q4 planning meeting
- Prep slides for Friday's demo (need about 10 slides)
```

### Output

**Summary:** We'll fix the auth bug and review one PR—both unblock your team and are manageable when tired.

**Timeline:**
- 0-15 min: Deep focus on authentication bug (find root cause + implement fix)
- 15-22 min: Review the simplest PR from the 3 open
- 22-25 min: Write quick handoff note on bug status

**Checklist:**
- ☐ Fix authentication bug or document blocker
- ☐ Review and approve/comment on 1 PR
- ☐ Leave 2-sentence handoff note

**Check-in:** Come back in 25 minutes and let me know what you got done! 🚀

---

## Architecture Diagrams

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for detailed visual diagrams including:
- System mindmap
- Agent workflow flowchart
- Technical architecture
- Tool execution sequence

---

## Value Proposition

### For Individual Contributors
- **Less overwhelm:** Clear guidance on what to do next
- **Better decisions:** Data-driven prioritization vs. gut feel
- **More momentum:** Completing small wins beats perfect plans that never start
- **Realistic expectations:** Plans that fit actual available time

### For Teams
- **Reduced context switching:** Focused sprints instead of task-hopping
- **Better time estimates:** Learn what actually takes 25 minutes
- **Unblocking others:** Prioritizes tasks that enable teammates
- **Repeatable process:** Works for Pomodoro cycles, meeting gaps, or deep work blocks

### Ideal For
- Software developers juggling tickets, reviews, and documentation
- Students balancing assignments, reading, and projects
- Writers managing research, drafting, and editing
- Anyone who struggles with "what should I work on right now?"

---

## Future Enhancements

- **Calendar integration:** Auto-detect available time blocks from Google Calendar
- **Learning system:** Improve time estimates based on historical completion data
- **Team mode:** Coordinate focus sessions across team members
- **Slack/Discord bot:** Check in without leaving your workflow
- **Voice interface:** Hands-free planning and check-ins
- **Pomodoro timer:** Built-in countdown with break suggestions


---

## Acknowledgments

- Built for the [Google AI Agents Intensive](https://www.kaggle.com/competitions/agents-intensive-capstone-project)
- Powered by [Google Gemini API](https://ai.google.dev/)
- Inspired by Pomodoro Technique and Getting Things Done methodology