import os
import asyncio
from google.adk.models.google_llm import Gemini
from google.adk import Agent
from google.adk.runners import InMemoryRunner
from tools import parse_tasks, prioritize_tasks, create_focus_schedule

os.environ['GOOGLE_API_KEY'] = os.environ.get('GEMINI_API_KEY', '')

session_memory = {"current_focus_plan": None, "tasks": [], "completed": []}

with open('src/agent_spec.md', 'r') as f:
    AGENT_SPEC = f.read()

def parse_tasks_tool(raw_text: str) -> str:
    tasks = parse_tasks(raw_text)
    session_memory["tasks"] = tasks
    result = f"Found {len(tasks)} tasks:\n"
    for i, task in enumerate(tasks, 1):
        result += f"{i}. {task.title} ({task.estimated_minutes} min"
        if task.deadline:
            result += f", due: {task.deadline}"
        result += ")\n"
    return result

def prioritize_tasks_tool() -> str:
    if not session_memory["tasks"]:
        return "No tasks to prioritize."
    prioritized = prioritize_tasks(session_memory["tasks"])
    session_memory["tasks"] = prioritized
    result = "Tasks prioritized:\n"
    for i, task in enumerate(prioritized, 1):
        result += f"{i}. {task.title} ({task.estimated_minutes} min)\n"
    return result

def create_schedule_tool(available_minutes: int = 25) -> str:
    if not session_memory["tasks"]:
        return "No tasks available."
    schedule = create_focus_schedule(session_memory["tasks"], available_minutes)
    session_memory["current_focus_plan"] = schedule
    result = f"Created {available_minutes}-minute focus plan:\n"
    for block in schedule:
        result += f"  {block.start_minute}-{block.end_minute} min: {block.task_title}\n"
    return result

model = Gemini(model="gemini-2.5-flash-lite")

agent = Agent(
    name="FocusBuddy",
    model=model,
    instruction=AGENT_SPEC + """
Follow this workflow:
1. Call parse_tasks_tool with the user's task list
2. Call prioritize_tasks_tool 
3. Call create_schedule_tool
4. Present: Summary, Timeline, Checklist, Check-in""",
    tools=[parse_tasks_tool, prioritize_tasks_tool, create_schedule_tool]
)

runner = InMemoryRunner(agent=agent)

async def main():
    example_tasks = """
    - Review pull requests (20 min)
    - Write unit tests for auth module
    - Update documentation due: today
    - Reply to 3 urgent emails (15 min)
    - Plan sprint retrospective
    """
    
    print("="*60)
    print("FOCUS BUDDY - Concierge Agent Demo")
    print("="*60)
    print("\n📋 Input Tasks:")
    print(example_tasks)
    
    session_memory["tasks"] = []
    session_memory["current_focus_plan"] = None
    
    prompt = f"I have these tasks for the next 30 minutes:\n{example_tasks}\nCreate my focus plan."
    
    print("\n🤖 Agent working...\n")
    response = await runner.run_debug(prompt)
    
    # Extract the final text response
    final_response = ""
    for event in response:
        if hasattr(event, 'content') and event.content and hasattr(event.content, 'parts'):
            for part in event.content.parts:
                if hasattr(part, 'text') and part.text:
                    final_response += part.text
    
    print("="*60)
    print("📊 FOCUS PLAN:")
    print("="*60)
    print(final_response)
    
    with open('example_output.txt', 'w') as f:
        f.write("FOCUS BUDDY - Example Output\n")
        f.write("="*60 + "\n\n")
        f.write("Input Tasks:\n")
        f.write(example_tasks + "\n\n")
        f.write("="*60 + "\n")
        f.write("Agent Response:\n")
        f.write("="*60 + "\n")
        f.write(final_response)
    
    print("\n✅ Saved to example_output.txt")

asyncio.run(main())