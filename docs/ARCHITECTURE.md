# Focus Buddy Architecture Documentation

This document provides visual diagrams of the Focus Buddy agent system architecture and workflow.

---

## 1. System Mindmap

High-level overview of all components:
```mermaid
mindmap
  root((Focus Buddy<br/>Agent System))
    Multi-Agent Architecture
      Planner Agent
        Parse Tasks
        Prioritize
        Schedule
      Coach Agent
        Present Plan
        Motivate
        Check-in
    Tools Layer
      parse_tasks
        Input: Raw text
        Output: Task objects
        Logic: Regex parsing
      prioritize_tasks
        Input: Task list
        Output: Sorted tasks
        Logic: Score by urgency
      create_focus_schedule
        Input: Tasks + time
        Output: Time blocks
        Logic: Fit within limits
    Session Memory
      Current Plan
      Task Status
      User Preferences
      Completion History
    User Interaction
      Initial Request
        Messy task list
        Time available
        Energy level
      Review Plan
        Confirm schedule
        Request adjustments
      Post-Session
        Report completion
        Get next plan
    Value Delivered
      Reduced Fatigue
      Realistic Plans
      Quick Wins
      Momentum
```

---

## 2. Agent Workflow

Complete flow from user input to completion:
```mermaid
flowchart TD
    Start([User Starts Session]) --> Input[User provides:<br/>- Messy task list<br/>- Time available<br/>- Energy level]
    
    Input --> Orchestrator{Orchestrator<br/>Agent}
    
    Orchestrator -->|Activate| Planner[Planner Agent Role]
    
    Planner --> Tool1[Tool: parse_tasks]
    Tool1 -->|Raw text| Parse[Parse & Structure]
    Parse -->|Task objects| Tool2[Tool: prioritize_tasks]
    
    Tool2 --> Priority[Calculate Priority Scores:<br/>- Urgency +3<br/>- Quick wins +2<br/>- Keywords +2<br/>- Time factor]
    Priority -->|Sorted tasks| Tool3[Tool: create_focus_schedule]
    
    Tool3 --> Schedule[Build Timeline:<br/>- Fit in time window<br/>- Max 3-5 tasks<br/>- Leave buffer]
    Schedule -->|Schedule blocks| Memory[(Session Memory)]
    
    Memory -->|Store plan| Coach[Coach Agent Role]
    
    Coach --> Present[Present Plan:<br/>✓ Summary<br/>✓ Timeline<br/>✓ Checklist<br/>✓ Check-in time]
    
    Present --> Confirm{User<br/>Confirms?}
    
    Confirm -->|Too heavy/light| Adjust[Adjust plan]
    Adjust --> Tool3
    
    Confirm -->|Approved| Execute[User Executes<br/>25-min Sprint]
    
    Execute --> Wait[⏰ Timer: 25 minutes]
    
    Wait --> Return[User Returns<br/>with Results]
    
    Return --> Coach2[Coach Agent:<br/>Check-in Phase]
    
    Coach2 --> Track[Track Completion:<br/>- Mark done/not done<br/>- Store outcomes<br/>- Suggest improvements]
    
    Track --> Memory
    
    Track --> Decide{Continue<br/>Session?}
    
    Decide -->|Yes, more tasks| Planner
    Decide -->|No| End([Session Complete])
    
    style Orchestrator fill:#4A90E2,stroke:#2E5C8A,color:#fff
    style Planner fill:#7B68EE,stroke:#5A4BC7,color:#fff
    style Coach fill:#50C878,stroke:#3A9B5C,color:#fff
    style Coach2 fill:#50C878,stroke:#3A9B5C,color:#fff
    style Memory fill:#FFB84D,stroke:#CC8F3D,color:#000
    style Tool1 fill:#E8E8E8,stroke:#999
    style Tool2 fill:#E8E8E8,stroke:#999
    style Tool3 fill:#E8E8E8,stroke:#999
```

---

## 3. Technical Architecture

Component-level system design:
```mermaid
graph TB
    subgraph User_Layer[" 👤 User Interaction Layer "]
        User[User Input:<br/>Tasks + Context]
        Display[Response Display:<br/>Plan + Checklist]
    end
    
    subgraph Agent_Layer[" 🤖 Multi-Agent System "]
        Orchestrator[Orchestrator<br/>Claude Sonnet 4]
        
        subgraph Roles[" Agent Roles "]
            Planner[🎯 Planner Role:<br/>Task Analysis<br/>Prioritization<br/>Scheduling]
            Coach[💪 Coach Role:<br/>Plan Presentation<br/>Motivation<br/>Check-ins]
        end
    end
    
    subgraph Tool_Layer[" 🔧 Tool Execution Layer "]
        ParseTool[parse_tasks<br/>━━━━━━━━<br/>Regex parsing<br/>Extract time/deadlines<br/>Normalize format]
        
        PriorityTool[prioritize_tasks<br/>━━━━━━━━<br/>Score calculation<br/>Urgency detection<br/>Sort by priority]
        
        ScheduleTool[create_focus_schedule<br/>━━━━━━━━<br/>Time fitting<br/>Block creation<br/>Buffer management]
    end
    
    subgraph Memory_Layer[" 💾 Session State "]
        TaskList[(Task List)]
        CurrentPlan[(Current Plan)]
        CompletionLog[(Completion Log)]
    end
    
    subgraph Data_Models[" 📋 Data Structures "]
        TaskModel[Task Object:<br/>- title<br/>- estimated_minutes<br/>- deadline<br/>- priority_score]
        
        ScheduleModel[ScheduledBlock:<br/>- start_minute<br/>- end_minute<br/>- task_title]
    end
    
    User -->|Raw text| Orchestrator
    Orchestrator -->|System prompt| Planner
    Orchestrator -->|System prompt| Coach
    
    Planner -->|Tool call| ParseTool
    ParseTool -->|Task objects| TaskModel
    TaskModel -->|Store| TaskList
    
    Planner -->|Tool call| PriorityTool
    PriorityTool -->|Sorted tasks| TaskModel
    
    Planner -->|Tool call| ScheduleTool
    ScheduleTool -->|Schedule| ScheduleModel
    ScheduleModel -->|Store| CurrentPlan
    
    CurrentPlan -->|Retrieve| Coach
    Coach -->|Format response| Display
    Display -->|Show plan| User
    
    User -->|Completion report| Coach
    Coach -->|Update| CompletionLog
    CompletionLog -->|History| Orchestrator
    
    classDef userStyle fill:#E3F2FD,stroke:#1976D2,stroke-width:2px
    classDef agentStyle fill:#F3E5F5,stroke:#7B1FA2,stroke-width:2px
    classDef toolStyle fill:#FFF3E0,stroke:#F57C00,stroke-width:2px
    classDef memoryStyle fill:#E8F5E9,stroke:#388E3C,stroke-width:2px
    classDef dataStyle fill:#FFF,stroke:#666,stroke-width:1px,stroke-dasharray: 5 5
    
    class User,Display userStyle
    class Orchestrator,Planner,Coach agentStyle
    class ParseTool,PriorityTool,ScheduleTool toolStyle
    class TaskList,CurrentPlan,CompletionLog memoryStyle
    class TaskModel,ScheduleModel dataStyle
```

---

## 4. Tool Execution Sequence

Detailed sequence of tool calls for a sample session:
```mermaid
sequenceDiagram
    participant User
    participant Agent as Claude Agent<br/>(Orchestrator)
    participant Planner as Planner Role
    participant Tool1 as parse_tasks()
    participant Tool2 as prioritize_tasks()
    participant Tool3 as create_focus_schedule()
    participant Memory as Session Memory
    participant Coach as Coach Role
    
    User->>Agent: "I have these tasks:<br/>- Review PRs<br/>- Fix bug (15min)<br/>- Write docs<br/><br/>25 minutes, tired"
    
    Agent->>Planner: Activate Planner role
    
    Note over Planner: Analyze request<br/>Extract: time=25, energy=low
    
    Planner->>Tool1: parse_tasks(raw_text)
    Tool1-->>Tool1: Regex split by bullets/numbers
    Tool1-->>Tool1: Extract time estimates
    Tool1-->>Tool1: Detect deadlines
    Tool1-->>Planner: Return Task[] objects
    
    Note over Planner: Tasks parsed:<br/>3 tasks identified
    
    Planner->>Tool2: prioritize_tasks(tasks)
    Tool2-->>Tool2: Calculate scores:<br/>Bug fix: 3.5 (urgent + short)<br/>Review PRs: 2.0 (quick win)<br/>Write docs: 0.0 (long task)
    Tool2-->>Tool2: Sort by score (descending)
    Tool2-->>Planner: Return sorted Task[]
    
    Note over Planner: Priority order:<br/>1. Fix bug<br/>2. Review PRs<br/>3. Write docs
    
    Planner->>Tool3: create_focus_schedule(tasks, 25)
    Tool3-->>Tool3: current_min = 0<br/>buffer = 3 min<br/>usable = 22 min
    Tool3-->>Tool3: Add Bug fix: 0-15 min
    Tool3-->>Tool3: Add Review PRs: 15-22 min
    Tool3-->>Tool3: Skip docs (no time)
    Tool3-->>Tool3: Add wrap-up: 22-25 min
    Tool3-->>Planner: Return ScheduledBlock[]
    
    Planner->>Memory: Store current_focus_plan
    Memory-->>Planner: Confirmed
    
    Agent->>Coach: Activate Coach role<br/>with schedule
    
    Note over Coach: Format friendly response
    
    Coach->>User: **Summary:** Fix bug + quick PR review<br/><br/>**Timeline:**<br/>0-15: Fix authentication bug<br/>15-22: Review simplest PR<br/>22-25: Wrap up notes<br/><br/>**Checklist:**<br/>☐ Fix bug<br/>☐ Review 1 PR<br/>☐ Write handoff note<br/><br/>Come back in 25 min!
    
    User->>User: ⏰ Execute 25-min sprint
    
    Note over User: 25 minutes pass
    
    User->>Agent: "I fixed the bug and<br/>reviewed 1 PR!"
    
    Agent->>Coach: Activate Coach check-in
    
    Coach->>Memory: Retrieve current_focus_plan
    Memory-->>Coach: Return plan + tasks
    
    Coach->>Memory: Update:<br/>- Bug fix: ✓ done<br/>- PR review: ✓ done<br/>- Handoff note: ✗ not done
    
    Coach->>User: 🎉 Great work! Bug and PR done.<br/><br/>**For next time:**<br/>- Handoff note = 2 min<br/>- Schedule at start of next block<br/><br/>**Remaining tasks:**<br/>- 2 more PRs<br/>- Write docs<br/><br/>Want another 25-min plan?
    
    Note over User,Coach: Session continues or ends
```

---

## Key Concepts Demonstrated

### 1. Multi-Agent System
- **Orchestrator**: Routes between Planner and Coach roles
- **Planner**: Analytical role - parsing, prioritizing, scheduling
- **Coach**: Interactive role - presenting, motivating, tracking

### 2. Tool Use (Function Calling)
- `parse_tasks`: Converts unstructured text → Task objects
- `prioritize_tasks`: Applies scoring logic → Sorted list
- `create_focus_schedule`: Fits tasks into time → Schedule blocks

### 3. Session Memory
- Stores current focus plan across tool calls
- Tracks completion status between check-ins
- Enables continuity for multi-sprint sessions

---

## Design Principles

1. **Realistic Planning**: Never schedule more than fits in available time
2. **Energy-Aware**: Adjusts task selection based on user energy level
3. **Quick Wins**: Prioritizes short, high-impact tasks for momentum
4. **Continuous Improvement**: Learns from completion patterns to suggest better plans