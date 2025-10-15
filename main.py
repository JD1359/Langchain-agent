"""
Main Entry Point
Starts the continuous input loop for the LangChain Tools Agent
"""

from agent import LangChainAgent
from rich.console import Console
from rich.panel import Panel
from dotenv import load_dotenv
import os
import sys

console = Console()


def check_environment():
    """Check if required environment variables are set"""
    print("\nChecking environment variables...")
    
    required_vars = ["OPENROUTER_API_KEY", "TAVILY_API_KEY"]
    missing_vars = []
    
    for var in required_vars:
        value = os.getenv(var)
        if not value:
            missing_vars.append(var)
            print(f"{var}: NOT FOUND")
        else:
            # Show first 10 characters for verification
            print(f"{var}: {value[:10]}...")
    
    if missing_vars:
        console.print(f"Error: Missing environment variables: {', '.join(missing_vars)}")
        console.print("Please check your .env file in the current directory")
        console.print(f"Current directory: {os.getcwd()}")
        return False
    
    print("All environment variables found!\n")
    return True


def print_welcome():
    """Print welcome message"""
    welcome_text = """
🤖 LangChain Tools Agent - Interactive Terminal

Available Commands:
  • Type your question or request
  • 'exit' or 'quit' - Exit the program
  • 'clear' - Clear conversation history

Tools Available:
  ✓ Internet Search (Tavily API)
  ✓ Math Evaluator
  ✓ Stock Ticker Info (Mock Data)

Examples:
  • "What's the latest news on AI?"
  • "Calculate 156 * 42 + 890"
  • "Get ticker info for AAPL"
  • "My name is John" then "What's my name?"
"""
    try:
        console.print(Panel(welcome_text, style="white", padding=(1, 2)))
    except Exception:
        print(welcome_text)


def main():
    """Main execution function with while True loop"""
    
    print("=" * 80)
    print("LANGCHAIN TOOLS AGENT - STARTING UP")
    print("=" * 80)
    
    # Load environment variables from .env file
    print(f"\nLoading .env file from: {os.getcwd()}")
    load_dotenv()
    
    # Check environment setup
    if not check_environment():
        print("\nSetup incomplete. Please fix the issues above.")
        input("\nPress Enter to exit...")
        return
    
    # Print welcome message
    print_welcome()
    
    # Initialize the agent
    try:
        print("Initializing agent (this may take a few seconds)...\n")
        agent = LangChainAgent()
        console.print("Agent ready! You can start chatting now.\n")
    except Exception as e:
        console.print(f"Failed to initialize agent")
        console.print(f"Error: {str(e)}\n")
        import traceback
        traceback.print_exc()
        input("\nPress Enter to exit...")
        return
    
    print("=" * 80)
    print()
    
    # Main conversation loop
    while True:
        try:
            # Get user input
            user_input = input("You: ").strip()
            
            # Handle empty input
            if not user_input:
                continue
            
            # Handle exit commands
            if user_input.lower() in ["exit", "quit", "q"]:
                console.print("\nGoodbye! Thanks for using LangChain Tools Agent.")
                break
            
            # Handle clear command
            if user_input.lower() == "clear":
                agent.clear_history()
                continue
            
            # Handle help command
            if user_input.lower() in ["help", "?"]:
                print_welcome()
                continue
            
            print()  # Add spacing
            
            # Run the agent
            response = agent.run(user_input)
            
            # Print clean response
            print(f"Agent: {response}\n")
            print("-" * 80 + "\n")
        
        except KeyboardInterrupt:
            console.print("\n\nInterrupted by user (Ctrl+C)")
            console.print("Goodbye!")
            break
        
        except Exception as e:
            console.print(f"\n Unexpected error: {str(e)}\n")
            import traceback
            traceback.print_exc()
            continue


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n Fatal error: {str(e)}")
        import traceback
        traceback.print_exc()
        input("\nPress Enter to exit...")