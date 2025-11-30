"""
Focus Buddy Agent - Gemini Implementation
Main agent orchestration using Google Gemini API
"""

import os
import json
from typing import List, Dict, Any
from dotenv import load_dotenv
import google.generativeai as genai

from tools import (
    Task, ScheduledBlock,
    parse_tasks, prioritize_tasks, create_focus_schedule
)

# Load environment variables
load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))


class FocusBuddyAgent:
    """Main agent class orchestrating Focus Buddy workflow"""
    
    def __init__(self):
        """Initialize the agent with tools and system prompt"""
        
        # Load system prompt
        with open('agent_spec.md', 'r') as f:
            self.system_prompt = f.read()
        
        # Define function schemas for Gemini
        self.tools = [{
            "function_declarations": [
                {
                    "name": "parse_tasks",
                    "description": "Parse messy task text into structured Task objects with title, estimated_minutes, and optional deadline",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "raw_text": {
                                "type": "string",
                                "description": "Raw task input from user in any format"
                            }
                        },
                        "required": ["raw_text"]
                    }
                },
                {
                    "name": "prioritize_tasks",
                    "description": "Sort tasks by priority score based on urgency, importance, and time estimates. Returns tasks sorted by priority.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "tasks": {
                                "type": "array",
                                "description": "List of task dictionaries to prioritize",
                                "items": {"type": "object"}
                            }
                        },
                        "required": ["tasks"]
                    }
                },
                {
                    "name": "create_focus_schedule",
                    "description": "Create a time-bounded schedule that fits within available minutes. Returns schedule blocks with start/end times.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "tasks": {
                                "type": "array",
                                "description": "Prioritized task list",
                                "items": {"type": "object"}
                            },
                            "available_minutes": {
                                "type": "integer",
                                "description": "Available time window in minutes",
                                "default": 25
                            }
                        },
                        "required": ["tasks"]
                    }
                }
            ]
        }]
        
        # Create model with tools
        self.model = genai.GenerativeModel(
            model_name='gemini-2.0-flash-exp',  # Free tier model
            tools=self.tools,
            system_instruction=self.system_prompt
        )
        
        # Session memory
        self.session_memory = {}
    
    def execute_function(self, function_name: str, function_args: Dict[str, Any]) -> Any:
        """
        Execute a tool function and return results.
        
        Args:
            function_name: Name of the function to call
            function_args: Dictionary of function arguments
            
        Returns:
            Function execution result (serializable)
        """
        if function_name == "parse_tasks":
            tasks = parse_tasks(function_args["raw_text"])
            result = [task.dict() for task in tasks]
            # Store in memory
            self.session_memory["parsed_tasks"] = result
            return result
        
        elif function_name == "prioritize_tasks":
            # Convert dicts back to Task objects
            tasks = [Task(**t) for t in function_args["tasks"]]
            prioritized = prioritize_tasks(tasks)
            result = [task.dict() for task in prioritized]
            # Store in memory
            self.session_memory["prioritized_tasks"] = result
            return result
        
        elif function_name == "create_focus_schedule":
            # Convert dicts back to Task objects
            tasks = [Task(**t) for t in function_args["tasks"]]
            available_minutes = function_args.get("available_minutes", 25)
            schedule = create_focus_schedule(tasks, available_minutes)
            result = [block.dict() for block in schedule]
            # Store in memory
            self.session_memory["current_focus_plan"] = result
            return result
        
        else:
            return {"error": f"Unknown function: {function_name}"}
    
    def chat(self, user_message: str, verbose: bool = True) -> str:
        """
        Send a message to the agent and get response.
        
        Args:
            user_message: User's input text
            verbose: Whether to print tool calls
            
        Returns:
            Agent's final text response
        """
        # Start or continue chat
        if not hasattr(self, 'chat_session'):
            self.chat_session = self.model.start_chat()
        
        # Send message
        response = self.chat_session.send_message(user_message)
        
        # Handle function calls (may be multiple iterations)
        max_iterations = 10
        iteration = 0
        
        while iteration < max_iterations:
            # Check if response contains function calls
            if not response.candidates:
                break
                
            parts = response.candidates[0].content.parts
            if not parts or not hasattr(parts[0], 'function_call'):
                break
            
            # Process all function calls in this response
            function_responses = []
            
            for part in parts:
                if hasattr(part, 'function_call'):
                    function_call = part.function_call
                    function_name = function_call.name
                    function_args = dict(function_call.args)
                    
                    if verbose:
                        print(f"🔧 Calling: {function_name}")
                    
                    # Execute the function
                    result = self.execute_function(function_name, function_args)
                    
                    # Prepare response for Gemini
                    function_responses.append(
                        genai.protos.Part(
                            function_response=genai.protos.FunctionResponse(
                                name=function_name,
                                response={"result": result}
                            )
                        )
                    )
            
            # Send function results back to model
            if function_responses:
                response = self.chat_session.send_message(
                    genai.protos.Content(parts=function_responses)
                )
            else:
                break
            
            iteration += 1
        
        # Extract final text response
        if response.candidates and response.candidates[0].content.parts:
            final_text = ""
            for part in response.candidates[0].content.parts:
                if hasattr(part, 'text'):
                    final_text += part.text
            return final_text
        
        return "No response generated"


def main():
    """Interactive demo of Focus Buddy agent"""
    print("=" * 60)
    print("*FOCUS BUDDY - Your 25-Minute Productivity Coach")
    print("=" * 60)
    print("\nPowered by Google Gemini 2.0 Flash\n")
    print("Type 'quit' to exit\n")
    
    agent = FocusBuddyAgent()
    
    while True:
        user_input = input("\nYou: ").strip()
        
        if user_input.lower() in ['quit', 'exit', 'bye']:
            print("\nGood luck with your focus work! Come back anytime.")
            break
        
        if not user_input:
            continue
        
        print("\n" + "-" * 60)
        response = agent.chat(user_input, verbose=True)
        print("-" * 60)
        print(f"\nFocus Buddy:\n{response}\n")


if __name__ == "__main__":
    main()