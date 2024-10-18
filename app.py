# app.py

from swarm.repl import run_demo_loop
from agents.router_agent import router_agent

if __name__ == "__main__":
    run_demo_loop(router_agent)

