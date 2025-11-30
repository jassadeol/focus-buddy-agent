import os
import asyncio
from google.adk.models.google_llm import Gemini
from google.adk import Agent
from google.adk.runners import InMemoryRunner
from tools import parse_tasks, prioritize_tasks, create_focus_schedule, Task, ScheduledBlock

# Configure API key
os.environ['GOOGLE_API_KEY'] = os.environ.get('GEMINI_API_KEY', '')

# Session memory
session_memory = {
    "current_focus_plan": None,
    "tasks": [],
    "completed": []
}

# Read agent spec
with open('src/agent_spec.md', 'r') as f:
    AGENT_SPEC = f.read()

# Define tools for ADK
def parse_tasks_tool(raw_text: str) -> str:
    """Parse messy task text into structured Task objects."""
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
    """Prioritize tasks from session memory."""
    if not session_memory["tasks"]:
        return "No tasks to prioritize. Call parse_tasks first."
    
    prioritized = prioritize_tasks(session_memory["tasks"])
    session_memory["tasks"] = prioritized
    
    result = "Tasks prioritized (urgent/deadline first, then by time):\n"
    for i, task in enumerate(prioritized, 1):
        result += f"{i}. {task.title} ({task.estimated_minutes} min)\n"
    return result

def create_schedule_tool(available_minutes: int = 25) -> str:
    """Create a focus schedule from prioritized tasks."""
    if not session_memory["tasks"]:
        return "No tasks available. Call parse_tasks and prioritize_tasks first."
    
    schedule = create_focus_schedule(session_memory["tasks"], available_minutes)
    session_memory["current_focus_plan"] = schedule
    
    result = f"Created {available_minutes}-minute focus plan with {len(schedule)} blocks:\n"
    for block in schedule:
        result += f"  {block.start_minute}-{block.end_minute} min: {block.task_title}\n"
    return result

# Create model
model = Gemini(model="gemini-2.5-flash-lite")

# Create ADK Agent
agent = Agent(
    name="FocusBuddy",
    model=model,
    instruction=AGENT_SPEC + """

You must follow this workflow:
1. Call parse_tasks_tool with the user's task list
2. Call prioritize_tasks_tool to sort them
3. Call create_schedule_tool with the available minutes
4. Present the final plan with: Summary, Timeline, Checklist, Check-in""",
    tools=[parse_tasks_tool, prioritize_tasks_tool, create_schedule_tool]
)

# Create runner
runner = InMemoryRunner(agent=agent)

async def run_focus_buddy(user_input: str, available_minutes: int = 25):
    """Main agent loop using ADK with InMemoryRunner."""
    
    print("="*60)
    print("FOCUS BUDDY AGENT - Multi-Agent Session")
    print("="*60)
    
    # Reset memory for new session
    session_memory["tasks"] = []
    session_memory["current_focus_plan"] = None
    
    # Build the prompt
    prompt = f"""I have these tasks to do in the next {available_minutes} minutes:

{user_input}

Please create my focus plan."""
    
    print("\n🤖 Agent working...\n")
    
    # Run the agent with runner
    response = await runner.run_debug(prompt)
    
    return response

# Example usage
if __name__ == "__main__":
    example_tasks = """
    - Review pull requests (20 min)
    - Write unit tests for auth module
    - Update documentation due: today
    - Reply to 3 urgent emails (15 min)
    - Plan sprint retrospective
    """
    
    async def main():
        try:
            result = await run_focus_buddy(example_tasks, available_minutes=30)
            print("\n" + "="*60)
            print("RESULT:")
            print("="*60)
            print(result)
            
            # Save example output
            with open('example_output.txt', 'w') as f:
                f.write(str(result))
            
            print("\n✅ Output saved to example_output.txt")
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
    
    # Run async main
    asyncio.run(main())