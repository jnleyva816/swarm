# agents/user_agent.py

from swarm import Agent
from utils.db_utils import db, run_mongodb_query

def transfer_back_to_router_agent():
    from agents.router_agent import router_agent
    return router_agent

def process_user_request(user_request):
    user_request_lower = user_request.lower()
    if "users" in user_request_lower or "user" in user_request_lower:
        projection = {'password_hash': 0}  # Exclude sensitive data
        return run_mongodb_query('users', {}, projection)
    else:
        return transfer_back_to_router_agent()

def get_data_agent_instructions():
    return """You are a data expert who helps the user with data related to users."""

user_agent = Agent(
    name="User Agent",
    instructions=get_data_agent_instructions(),
    functions=[process_user_request, transfer_back_to_router_agent]
)

