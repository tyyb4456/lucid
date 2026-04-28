from sub_agents.system_agent.agent import system_agent
from sub_agents.automation_agent.agent import automation_agent
from sub_agents.file_agent.agent import file_agent
from sub_agents.productivity_agent.agent import productivity_agent
from sub_agents.utility_agent.agent import utility_agent
from sub_agents.web_agent.agent import web_agent

from langgraph.checkpoint.memory import InMemorySaver

from deepagents import create_deep_agent

checkpointer = InMemorySaver()

from dotenv import load_dotenv
load_dotenv()


from langchain.agents.middleware import SummarizationMiddleware

SYSTEM_PROMPT = """You are LUCID, the main Orchestrator Agent.
Your job is to understand the user's request and intelligently delegate tasks to your specialized sub-agents.
Each sub-agent has a specific set of tools and expertise:
- system_agent: OS control, process management, power, system commands
- automation_agent: GUI automation, mouse, keyboard, clipboard control
- file_agent: Search, read, write, move, and copy files
- productivity_agent: TODO lists, note-taking, task management
- utility_agent: Math, time, unit conversions, JSON handling, weather
- web_agent: Web searches, opening URLs, downloading files, network checks

Coordinate these sub-agents to fulfill complex tasks efficiently. Think step-by-step and determine which sub-agent is best suited for each part of the user's request.
"""

agent = create_deep_agent(
    name="main_agent",
    model="google_genai:gemini-2.5-flash-lite",
    system_prompt=SYSTEM_PROMPT,
    subagents=[
        system_agent(),
        automation_agent(),
        file_agent(),
        productivity_agent(),
        utility_agent(),
        web_agent()
    ],
    checkpointer=checkpointer
)