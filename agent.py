"""
LangChain Agent Definition
Defines the LLM agent, memory, and bindings
"""

from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import AIMessage, HumanMessage
from tools import TOOLS
from rich.console import Console
from rich.panel import Panel
import os

console = Console()


class LangChainAgent:
    """LangChain Tools Agent with conversational memory"""
    
    def __init__(self):
        """Initialize the agent with LLM, tools, and memory"""
        
        print("Initializing LLM...")
        
        # Get API key
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise ValueError("OPENROUTER_API_KEY not found in environment variables")
        
        # Initialize OpenRouter LLM
        self.llm = ChatOpenAI(
            model="openai/gpt-3.5-turbo",
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1",
            temperature=0.7,
            default_headers={
                "HTTP-Referer": "http://localhost:3000",
                "X-Title": "LangChain Tools Agent"
            }
        )
        
        print("Binding tools to LLM...")
        
        # Bind tools to the LLM
        self.llm_with_tools = self.llm.bind_tools(TOOLS)
        
        # Create prompt template
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a helpful AI assistant with access to tools.

Available tools:
- search_tool: Search the internet for current information using Tavily
- math_tool: Evaluate mathematical expressions safely
- custom_ticker_info: Get stock ticker information (mock data)

Guidelines:
1. Think step by step about what tool to use
2. Use tools when needed to provide accurate information
3. Provide clear, concise responses
4. Remember previous conversation context
5. For calculations, always use the math_tool
6. For current information, use the search_tool
7. Be friendly and helpful"""),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        print("Creating agent...")
        
        # Create the agent
        self.agent = create_tool_calling_agent(
            llm=self.llm_with_tools,
            tools=TOOLS,
            prompt=self.prompt
        )
        
        # Create agent executor
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=TOOLS,
            verbose=False,
            handle_parsing_errors=True,
            max_iterations=5,
            return_intermediate_steps=True
        )
        
        # In-memory conversation history
        self.chat_history = []
        
        print("Agent initialized successfully!\n")
    
    def run(self, user_input: str) -> str:
        """
        Execute the agent with user input
        
        Args:
            user_input: The user's query or message
            
        Returns:
            The agent's response
        """
        try:
            # Run the agent with chat history (no input logging)
            response = self.agent_executor.invoke({
                "input": user_input,
                "chat_history": self.chat_history
            })
            
            # Extract the output
            output = response.get("output", "No response generated")
            
            # Update chat history
            self.chat_history.append(HumanMessage(content=user_input))
            self.chat_history.append(AIMessage(content=output))
            
            # Keep only last 10 messages to manage memory
            if len(self.chat_history) > 10:
                self.chat_history = self.chat_history[-10:]
            
            return output
        
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            console.print(f"{error_msg}")
            return error_msg
    
    def _log_invocation(self, title: str, content: str, color: str):
        """Print structured logs to terminal"""
        try:
            console.print(Panel(
                content,
                title=title,
                border_style=color,
                padding=(1, 2)
            ))
        except Exception:
            # Fallback to simple print if Rich fails
            print(f"\n=== {title} ===")
            print(content)
            print("=" * 50)
    
    def clear_history(self):
        """Clear the conversation history"""
        self.chat_history = []
        console.print("Conversation history cleared.")