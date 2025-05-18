"""Playground server for Knowledge Base Agent

This sets up a web interface for interacting with our knowledge base agent.
"""

from agno.agent import Agent
from agno.playground import Playground, serve_playground_app
from agno.storage.sqlite import SqliteStorage
from agno.tools.mcp import MCPTools
from mcp import StdioServerParameters
from agno.models.openrouter import OpenRouter
import dotenv
import os

dotenv.load_dotenv()

# Load environment variables
arango_url = os.getenv("ARANGO_URL")
arango_db = os.getenv("ARANGO_DB")
arango_username = os.getenv("ARANGO_USERNAME")
arango_password = os.getenv("ARANGO_PASSWORD")
open_router_api_key = os.getenv("OPEN_ROUTER_API_KEY")

# Initialize the MCP server for ArangoDB
server_params = StdioServerParameters(
    command="npx",
    args=["arango-server"],
    env={
        "ARANGO_URL": arango_url,
        "ARANGO_DB": arango_db,
        "ARANGO_USERNAME": arango_username,
        "ARANGO_PASSWORD": arango_password
    }
)

agent_storage: str = "tmp/agents.db"

knowledge_agent = Agent(
    name="Knowledge Assistant",
    model=OpenRouter(id="google/gemini-2.0-flash-001", api_key=open_router_api_key),
    tools=[MCPTools(server_params=server_params)],
    instructions="""You are a knowledge base assistant. Help users store and retrieve information.

    - Store information in a structured way using entities and relations
    - Use clear and descriptive entity types
    - Create meaningful relations between entities
    - Search and retrieve relevant information
    - Be concise and focus on relevant information
    """,
    storage=SqliteStorage(table_name="knowledge_agent", db_file=agent_storage),
    add_datetime_to_instructions=True,
    add_history_to_messages=True,
    num_history_responses=5,
    markdown=True,
    show_tool_calls=True,
)

# Create the playground app with our knowledge agent
app = Playground(agents=[knowledge_agent]).get_app()

if __name__ == "__main__":
    serve_playground_app("playground:app", reload=True) 