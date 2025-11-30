# Focus Buddy – Concierge Agent for 25-Minute Deep Work Sessions

A multi-agent concierge system that transforms messy to-do lists into realistic 25-minute focus plans, reducing decision fatigue and context switching for knowledge workers.

**Track:** Concierge Agents  
**Concepts Used:** Multi-agent systems, tool calling, session memory

---

## Problem Statement

Knowledge workers and students face a common challenge: they have long, messy to-do lists but struggle to decide what to tackle in the next 25-30 minutes. This decision fatigue leads to:
- Paralysis and procrastination
- Poor task selection (choosing easy over important)
- Context switching that kills deep work
- Unrealistic planning that leads to incomplete work and frustration

Traditional to-do apps don't solve this—they store tasks but don't help users make smart, time-bounded decisions about what to do *right now*.

---

## Solution & Architecture

**Focus Buddy** is a concierge AI agent that acts as your personal workflow assistant. It takes your messy task list and generates a realistic 25-minute deep work plan, then coaches you through execution.

### Multi-Agent System

The system uses **two cooperating agent roles**:

1. **Planner Agent**
   - Parses unstructured task input
   - Prioritizes by urgency, impact, and time estimates
   - Creates time-bounded schedules that actually fit in 25 minutes

2. **Coach Agent**
   - Presents the plan in friendly, actionable format
   - Confirms the plan fits user energy and context
   - Checks in after the session to track completion and suggest improvements

### Tools (Function Calling)

Three Python tools enable structured workflow:

- `parse_tasks(raw_text)` – Converts messy input into structured Task objects
- `prioritize_tasks(tasks)` – Sorts by urgency/importance and realistic time
- `create_focus_schedule(tasks, minutes)` – Builds a timeline that fits available time

### Session Memory

The agent maintains short-term memory across a focus session:
- Original task list
- Prioritized tasks
- Current focus plan
- Completion status after check-in

This enables continuity: "What got done?" → "Let's plan the next 25 minutes with what's left."

---

## Course Concepts Applied

1. **Multi-agent systems:** Planner and Coach roles coordinate through shared context
2. **Tool use:** Three custom Python functions for parsing, prioritizing, and scheduling
3. **Sessions & memory:** Persistent state tracks plans and outcomes within a work session
4. **Evaluation loop:** Check-in phase evaluates what worked and adjusts future plans

---

## Setup & Installation

### Requirements
```bash
pip install -r requirements.txt
```

You'll need:
- Python 3.10+
- Anthropic Claude API key (set as `ANTHROPIC_API_KEY` environment variable)
- Anthropic Agent Development Kit (ADK)

### Running the Agent

**Option 1: Jupyter Notebook**
```bash
jupyter notebook src/main.ipynb
```

**Option 2: Python Script**
```bash
python src/main.py
```

---

## Example Usage

### Input
```
User: I have so much to do. Here's my list:
- Review pull requests (3 open)
- Write docs for the new API endpoint
- Reply to Sarah about the Q4 planning meeting
- Fix bug in authentication flow
- Prep slides for Friday's demo

I have 25 minutes right now and I'm pretty tired.
```

### Agent Response
**Summary:** We'll tackle the authentication bug and one quick PR review—both unblock others and are doable when tired.

**Timeline:**
- 0-3 min: Skim the 3 PRs and pick the simplest one
- 3-18 min: Deep focus on authentication bug (aim for root cause + fix)
- 18-23 min: Review the simple PR and approve/comment
- 23-25 min: Write 2-sentence note on what's left for the bug

**Checklist:**
- [ ] Pick 1 PR to review
- [ ] Fix or document auth bug
- [ ] Complete PR review
- [ ] Quick handoff note

**Check-in:** Come back in 25 minutes and tell me what you finished!

---

## How It Works

1. **User provides tasks** (messy format is fine)
2. **Planner agent** calls `parse_tasks` → `prioritize_tasks` → `create_focus_schedule`
3. **Coach agent** presents the plan and gets user confirmation
4. **User executes** the 25-minute sprint
5. **Check-in** marks tasks complete and suggests next steps

The agent avoids over-planning (no more than 3-5 tasks per block) and respects user energy level (tired = smaller tasks, high energy = deep work).

---

## Value Proposition

- **Reduces cognitive load:** No more staring at a list wondering what to do
- **Realistic planning:** Fits actual available time instead of wishful thinking
- **Momentum:** Small wins in 25 minutes beat perfect plans that never start
- **Repeatable:** Works for Pomodoro cycles, short windows between meetings, or deep work sessions

Ideal for students, developers, writers, and anyone who struggles with task paralysis.

---

## Future Enhancements

- Calendar integration to auto-detect available time blocks
- Learning from past sessions to improve time estimates
- Slack/Teams integration for team-based focus sessions
- Voice interface for hands-free check-ins
