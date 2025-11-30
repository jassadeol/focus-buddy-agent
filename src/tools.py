"""
Focus Buddy Tools
Simple Python functions for parsing, prioritizing, and scheduling tasks.
"""

from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
import re


class Task(BaseModel):
    """Structured task representation"""
    title: str
    estimated_minutes: int = 10
    deadline: Optional[str] = None
    priority_score: float = 0.0
    completed: bool = False


class ScheduledBlock(BaseModel):
    """A time block in the focus schedule"""
    start_minute: int
    end_minute: int
    task_title: str


def parse_tasks(raw_text: str) -> List[Task]:
    """
    Parse messy task input into structured Task objects.
    
    Handles bullet points, numbers, and natural language.
    Attempts to extract time estimates like "(15 min)" or "30m".
    """
    tasks = []
    
    # Split by common delimiters
    lines = re.split(r'[\n\r]+|(?:^|\s)[-•*]\s+|\d+\.\s+', raw_text)
    
    for line in lines:
        line = line.strip()
        if not line or len(line) < 3:
            continue
            
        # Extract time estimates
        time_match = re.search(r'\((\d+)\s*min\)|\b(\d+)m\b', line, re.IGNORECASE)
        estimated_minutes = 10  # default
        
        if time_match:
            estimated_minutes = int(time_match.group(1) or time_match.group(2))
            line = re.sub(r'\(?\d+\s*min?\)?', '', line, flags=re.IGNORECASE).strip()
        
        # Extract deadline hints
        deadline = None
        deadline_match = re.search(r'\b(due|deadline|by)\s+([a-zA-Z]+\s+\d+|\d+/\d+|today|tomorrow)', line, re.IGNORECASE)
        if deadline_match:
            deadline = deadline_match.group(2)
        
        tasks.append(Task(
            title=line,
            estimated_minutes=estimated_minutes,
            deadline=deadline
        ))
    
    return tasks


def prioritize_tasks(tasks: List[Task]) -> List[Task]:
    """
    Sort tasks by priority score combining urgency, impact, and time.
    
    Priority rules:
    1. Tasks with deadlines today/soon get +3 points
    2. Quick tasks (< 10 min) get +2 points (quick wins)
    3. Keywords like "urgent", "important", "blocking" get +2 points
    4. Shorter tasks get slight boost (encourages momentum)
    """
    for task in tasks:
        score = 0.0
        
        # Deadline urgency
        if task.deadline:
            deadline_lower = task.deadline.lower()
            if 'today' in deadline_lower or 'urgent' in deadline_lower:
                score += 3
            elif 'tomorrow' in deadline_lower:
                score += 2
        
        # Quick win bonus
        if task.estimated_minutes <= 10:
            score += 2
        
        # Keyword scanning
        title_lower = task.title.lower()
        if any(word in title_lower for word in ['urgent', 'important', 'blocking', 'asap', 'critical']):
            score += 2
        if any(word in title_lower for word in ['bug', 'fix', 'broken', 'error']):
            score += 1.5
        
        # Time-based tie-breaker (shorter = slightly higher)
        score += (60 - min(task.estimated_minutes, 60)) / 100
        
        task.priority_score = score
    
    # Sort descending by priority
    return sorted(tasks, key=lambda t: t.priority_score, reverse=True)


def create_focus_schedule(tasks: List[Task], available_minutes: int = 25) -> List[ScheduledBlock]:
    """
    Build a realistic schedule that fits in available_minutes.
    
    Rules:
    - Never schedule more time than available
    - Limit to 2-5 blocks max (avoid context switching)
    - Leave 2-5 min buffer at the end for wrap-up
    """
    schedule = []
    current_minute = 0
    buffer_minutes = 3
    usable_minutes = available_minutes - buffer_minutes
    
    for task in tasks:
        if current_minute + task.estimated_minutes > usable_minutes:
            # Try to fit a smaller slice if it's the last task
            remaining = usable_minutes - current_minute
            if remaining >= 5:
                schedule.append(ScheduledBlock(
                    start_minute=current_minute,
                    end_minute=current_minute + remaining,
                    task_title=f"{task.title} (partial - {remaining} min)"
                ))
                current_minute += remaining
            break
        
        schedule.append(ScheduledBlock(
            start_minute=current_minute,
            end_minute=current_minute + task.estimated_minutes,
            task_title=task.title
        ))
        current_minute += task.estimated_minutes
        
        # Limit to 4 main blocks
        if len(schedule) >= 4:
            break
    
    # Add wrap-up block if there's time
    if current_minute < available_minutes:
        schedule.append(ScheduledBlock(
            start_minute=current_minute,
            end_minute=available_minutes,
            task_title="Wrap up & notes for next session"
        ))
    
    return schedule