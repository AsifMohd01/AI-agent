"""
Example usage of the Autonomous AI Agent.
This script demonstrates how to use the AI agent programmatically.
"""

from app import AIAgent
import json

def print_result(result):
    """Print the result in a readable format"""
    print("\n" + "=" * 60)
    print(f"Status: {result.get('status', 'unknown')}")
    print("=" * 60)
    
    if 'results' in result:
        print("\nExecution Results:")
        for i, step_result in enumerate(result['results']):
            print(f"\nStep {i+1}:")
            print(f"  Status: {step_result.get('status', 'unknown')}")
            
            # Print environment-specific details
            if 'url' in step_result:
                print(f"  Environment: Browser")
                print(f"  URL: {step_result.get('url')}")
                print(f"  Title: {step_result.get('title', 'No title')}")
            elif 'command' in step_result:
                print(f"  Environment: Terminal")
                print(f"  Command: {step_result.get('command')}")
                print(f"  Output: {step_result.get('stdout', '')[:100]}...")
            elif 'action' in step_result and step_result['action'] in ['create_file', 'read_file', 'write_file', 'append_file', 'delete_file']:
                print(f"  Environment: File System")
                print(f"  Action: {step_result.get('action')}")
                print(f"  Filename: {step_result.get('filename')}")
                if 'content' in step_result:
                    print(f"  Content: {step_result.get('content')[:100]}...")
    
    if 'message' in result:
        print(f"\nMessage: {result['message']}")
    
    if 'report' in result:
        print("\nReport Preview:")
        print(result['report'][:200] + "...")
    
    print("\n" + "=" * 60)

def example_browser_task():
    """Example of a browser task"""
    print("\n🌐 Example: Browser Task")
    agent = AIAgent()
    instruction = "Search for information about Python programming language and show the top 3 results"
    print(f"Instruction: {instruction}")
    result = agent.process_instruction(instruction)
    print_result(result)

def example_terminal_task():
    """Example of a terminal task"""
    print("\n💻 Example: Terminal Task")
    agent = AIAgent()
    instruction = "List all files in the current directory and count how many Python files there are"
    print(f"Instruction: {instruction}")
    result = agent.process_instruction(instruction)
    print_result(result)

def example_file_system_task():
    """Example of a file system task"""
    print("\n📁 Example: File System Task")
    agent = AIAgent()
    instruction = "Create a text file named 'todo.txt' with a list of 3 tasks: Buy groceries, Pay bills, Call mom"
    print(f"Instruction: {instruction}")
    result = agent.process_instruction(instruction)
    print_result(result)

def example_multi_environment_task():
    """Example of a task that uses multiple environments"""
    print("\n🔄 Example: Multi-Environment Task")
    agent = AIAgent()
    instruction = "Search for information about Flask web framework, save the top 3 results to a file named 'flask_info.txt', and create a summary report"
    print(f"Instruction: {instruction}")
    result = agent.process_instruction(instruction)
    print_result(result)

def custom_task(instruction):
    """Run a custom task with the given instruction"""
    print(f"\n🔍 Custom Task: {instruction}")
    agent = AIAgent()
    result = agent.process_instruction(instruction)
    print_result(result)

if __name__ == "__main__":
    print("=" * 60)
    print("Autonomous AI Agent - Example Usage")
    print("=" * 60)
    
    print("\nThis script demonstrates how to use the AI agent programmatically.")
    print("It will run several example tasks to show the agent's capabilities.")
    
    input("\nPress Enter to start the examples...")
    
    example_browser_task()
    input("\nPress Enter to continue to the next example...")
    
    example_terminal_task()
    input("\nPress Enter to continue to the next example...")
    
    example_file_system_task()
    input("\nPress Enter to continue to the next example...")
    
    example_multi_environment_task()
    
    print("\n" + "=" * 60)
    print("Examples completed!")
    print("=" * 60)
    
    # Allow the user to run a custom task
    print("\nWould you like to run a custom task?")
    run_custom = input("Enter 'y' to run a custom task, or any other key to exit: ")
    
    if run_custom.lower() == 'y':
        instruction = input("\nEnter your instruction: ")
        custom_task(instruction)
    
    print("\nThank you for using the Autonomous AI Agent!")