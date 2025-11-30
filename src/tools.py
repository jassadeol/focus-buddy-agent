"""
Focus Buddy Agent Tools
Simple Python functions that the agent can call to parse, prioritize, and schedule tasks.

IMPORTANT: This file should NOT import from gemini_agent.py to avoid circular imports.
"""
'''

from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime
import re


@dataclass
class Task:
    """Structured task representation"""
    title: str
    estimated_minutes: int = 10
    deadline: Optional[str] = None
    priority_score: float = 0.0


@dataclass
class ScheduledBlock:
    """A time block in the focus schedule"""
    start_minute: int
    end_minute: int
    task_title: str


def parse_tasks(raw_text: str) -> List[dict]:
    """
    Parse messy user text into structured tasks.
    
    Args:
        raw_text: Raw task list from user (bullets, paragraphs, etc.)
    
    Returns:
        List of task dictionaries with title, estimated_minutes, and optional deadline
    """
    tasks = []
    
    # Split by common delimiters
    lines = re.split(r'[\n•\-*]', raw_text)
    
    for line in lines:
        line = line.strip()
        if not line or len(line) < 3:
            continue
        
        # Extract time estimates (e.g., "30min", "1h", "2 hours")
        time_match = re.search(r'(\d+)\s*(min|mins|minute|minutes|h|hr|hrs|hour|hours)', line, re.IGNORECASE)
        estimated_minutes = 10  # default
        
        if time_match:
            value = int(time_match.group(1))
            unit = time_match.group(2).lower()
            if unit.startswith('h'):
                estimated_minutes = value * 60
            else:
                estimated_minutes = value
            # Remove time estimate from title
            line = re.sub(r'\d+\s*(min|mins|minute|minutes|h|hr|hrs|hour|hours)', '', line, flags=re.IGNORECASE).strip()
        
        # Extract deadline (e.g., "due Monday", "deadline: tomorrow")
        deadline = None
        deadline_match = re.search(r'(due|deadline|by)\s*:?\s*(\w+)', line, re.IGNORECASE)
        if deadline_match:
            deadline = deadline_match.group(2)
            line = re.sub(r'(due|deadline|by)\s*:?\s*\w+', '', line, flags=re.IGNORECASE).strip()
        
        # Clean up remaining punctuation
        line = re.sub(r'^[\-\*•:]+\s*', '', line).strip()
        line = re.sub(r'\s+', ' ', line)
        
        if line:
            tasks.append({
                "title": line,
                "estimated_minutes": estimated_minutes,
                "deadline": deadline
            })
    
    return tasks


def prioritize_tasks(tasks: List[dict]) -> List[dict]:
    """
    Sort tasks by urgency, importance, and estimated time.
    
    Args:
        tasks: List of task dictionaries
    
    Returns:
        Sorted list of tasks with priority_score added
    """
    def calculate_priority(task: dict) -> float:
        score = 0.0
        
        # Has deadline = higher priority
        if task.get("deadline"):
            score += 10.0
            # Urgent keywords
            deadline_lower = task["deadline"].lower()
            if deadline_lower in ["today", "asap", "urgent", "now"]:
                score += 20.0
            elif deadline_lower in ["tomorrow", "soon"]:
                score += 10.0
        
        # Shorter tasks get slight boost (quick wins)
        est_mins = task.get("estimated_minutes", 10)
        if est_mins <= 5:
            score += 5.0
        elif est_mins <= 15:
            score += 2.0
        
        # Important keywords in title
        title_lower = task["title"].lower()
        if any(word in title_lower for word in ["urgent", "important", "critical", "asap", "priority"]):
            score += 15.0
        if any(word in title_lower for word in ["review", "check", "quick", "simple"]):
            score += 3.0
        
        return score
    
    # Calculate priority scores
    for task in tasks:
        task["priority_score"] = calculate_priority(task)
    
    # Sort by priority (highest first), then by estimated time (shortest first)
    sorted_tasks = sorted(
        tasks,
        key=lambda t: (-t["priority_score"], t.get("estimated_minutes", 10))
    )
    
    return sorted_tasks


def create_focus_schedule(tasks: List[dict], available_minutes: int) -> List[dict]:
    """
    Create a realistic schedule that fits within available time.
    
    Args:
        tasks: Prioritized list of task dictionaries
        available_minutes: Total minutes available (e.g., 25)
    
    Returns:
        List of scheduled block dictionaries with start_minute, end_minute, task_title
    """
    schedule = []
    current_minute = 0
    
    # Reserve last 2-3 minutes for wrap-up
    buffer_minutes = min(3, available_minutes // 10)
    usable_minutes = available_minutes - buffer_minutes
    
    for task in tasks:
        est_mins = task.get("estimated_minutes", 10)
        
        # Stop if we can't fit this task
        if current_minute + est_mins > usable_minutes:
            break
        
        schedule.append({
            "start_minute": current_minute,
            "end_minute": current_minute + est_mins,
            "task_title": task["title"]
        })
        
        current_minute += est_mins
        
        # Limit to 5 tasks max to avoid overwhelm
        if len(schedule) >= 5:
            break
    
    # Add wrap-up block if there's time
    if current_minute < available_minutes:
        schedule.append({
            "start_minute": current_minute,
            "end_minute": available_minutes,
            "task_title": "Wrap up & notes for next session"
        })
    
    return schedule


# Tool definitions for Gemini API
TOOL_DEFINITIONS = {
    "function_declarations": [
        {
            "name": "parse_tasks",
            "description": "Parse messy task text into structured format with titles, time estimates, and deadlines",
            "parameters": {
                "type": "object",
                "properties": {
                    "raw_text": {
                        "type": "string",
                        "description": "The raw task list text from the user"
                    }
                },
                "required": ["raw_text"]
            }
        },
        {
            "name": "prioritize_tasks",
            "description": "Sort tasks by urgency, importance, and estimated time, calculating priority scores",
            "parameters": {
                "type": "object",
                "properties": {
                    "tasks": {
                        "type": "array",
                        "description": "List of parsed task objects",
                        "items": {
                            "type": "object",
                            "properties": {
                                "title": {
                                    "type": "string",
                                    "description": "Task title"
                                },
                                "estimated_minutes": {
                                    "type": "number",
                                    "description": "Estimated minutes to complete"
                                },
                                "deadline": {
                                    "type": "string",
                                    "description": "Optional deadline"
                                }
                            },
                            "required": ["title"]
                        }
                    }
                },
                "required": ["tasks"]
            }
        },
        {
            "name": "create_focus_schedule",
            "description": "Create a realistic schedule of time blocks that fits within available time",
            "parameters": {
                "type": "object",
                "properties": {
                    "tasks": {
                        "type": "array",
                        "description": "Prioritized list of tasks to schedule",
                        "items": {
                            "type": "object",
                            "properties": {
                                "title": {
                                    "type": "string",
                                    "description": "Task title"
                                },
                                "estimated_minutes": {
                                    "type": "number",
                                    "description": "Estimated minutes to complete"
                                },
                                "deadline": {
                                    "type": "string",
                                    "description": "Optional deadline"
                                },
                                "priority_score": {
                                    "type": "number",
                                    "description": "Calculated priority score"
                                }
                            },
                            "required": ["title"]
                        }
                    },
                    "available_minutes": {
                        "type": "number",
                        "description": "Total minutes available for the focus session"
                    }
                },
                "required": ["tasks", "available_minutes"]
            }
        }
    ]
}


# Tool execution mapping
TOOL_FUNCTIONS = {
    "parse_tasks": parse_tasks,
    "prioritize_tasks": prioritize_tasks,
    "create_focus_schedule": create_focus_schedule
}
'''

from dataclasses import dataclass
from typing import List
import re

@dataclass
class Task:
    title: str
    deadline: str = ""
    estimated_minutes: int = 10

@dataclass
class ScheduledBlock:
    start_minute: int
    end_minute: int
    task_title: str

def parse_tasks(raw_text: str) -> List[Task]:
    """Parse messy task text into structured Task objects."""
    tasks = []
    lines = [line.strip() for line in raw_text.split('\n') if line.strip()]
    
    for line in lines:
        # Remove bullet points, dashes, numbers
        clean_line = re.sub(r'^[-*•\d.)\]]+\s*', '', line)
        
        # Extract time estimates if present (e.g., "30min", "1hr")
        time_match = re.search(r'(\d+)\s*(min|hour|hr)', clean_line, re.IGNORECASE)
        estimated_minutes = 10  # default
        if time_match:
            num = int(time_match.group(1))
            unit = time_match.group(2).lower()
            estimated_minutes = num if 'min' in unit else num * 60
            clean_line = re.sub(r'\d+\s*(min|hour|hr)', '', clean_line, flags=re.IGNORECASE)
        
        # Extract deadline if present
        deadline_match = re.search(r'(due|deadline|by)\s*:?\s*(\S+)', clean_line, re.IGNORECASE)
        deadline = deadline_match.group(2) if deadline_match else ""
        if deadline_match:
            clean_line = re.sub(r'(due|deadline|by)\s*:?\s*\S+', '', clean_line, flags=re.IGNORECASE)
        
        clean_line = clean_line.strip(' ,-:')
        if clean_line:
            tasks.append(Task(title=clean_line, deadline=deadline, estimated_minutes=estimated_minutes))
    
    return tasks

def prioritize_tasks(tasks: List[Task]) -> List[Task]:
    """Sort tasks by urgency (deadline present) then by estimated time."""
    def priority_key(task):
        has_deadline = 1 if task.deadline else 0
        return (-has_deadline, task.estimated_minutes)
    
    return sorted(tasks, key=priority_key)

def create_focus_schedule(tasks: List[Task], available_minutes: int) -> List[ScheduledBlock]:
    """Create a schedule that fits within available time."""
    schedule = []
    current_minute = 0
    
    for task in tasks:
        if current_minute + task.estimated_minutes <= available_minutes:
            schedule.append(ScheduledBlock(
                start_minute=current_minute,
                end_minute=current_minute + task.estimated_minutes,
                task_title=task.title
            ))
            current_minute += task.estimated_minutes
        else:
            # Try to fit a partial chunk if there's time left
            remaining = available_minutes - current_minute
            if remaining >= 5:
                schedule.append(ScheduledBlock(
                    start_minute=current_minute,
                    end_minute=available_minutes,
                    task_title=f"{task.title} (partial)"
                ))
            break
    
    return schedule