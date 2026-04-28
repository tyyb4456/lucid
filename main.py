"""
LUCID - Main Entry Point
========================
Invokes the main orchestrator agent in a loop that handles
HumanInTheLoop interruptions from sub-agents.

Flow:
  1. User types a request.
  2. Agent runs until it either:
       a) Returns a final answer  →  print and loop back for next input.
       b) Hits an interrupt       →  show pending tool call, ask approve/reject,
                                     resume agent with Command(resume=decision).
  3. Repeat step 2 until final answer.
"""

import sys
from typing import Any

from langgraph.types import Command

# ── The compiled LangGraph agent (must expose .invoke / .stream with interrupt support) ──
from main_agent import agent



# ─────────────────────────────────────────────────────────────────────────────
# Core invocation loop
# ─────────────────────────────────────────────────────────────────────────────

def run_with_interrupts(user_input: str, thread_id: str = "default") -> str:
    """
    Invoke the main agent and handle any number of HumanInTheLoop interrupts
    before returning the final answer text.

    LangGraph surfaces interrupts as GraphInterrupt exceptions (or by returning
    a state whose '__interrupt__' key is non-empty). We handle both patterns.
    """
    config = {"configurable": {"thread_id": thread_id}}

    result = agent.invoke(
        {"messages": [{"role": "user", "content": user_input}]},
        config=config,
        version="v2",
    )

    while result.interrupts:

        print("Interrupt detected:", result.interrupts[0].value)
        # Extract interrupt information
        interrupt_value = result.interrupts[0].value
        action_requests = interrupt_value["action_requests"]
        review_configs = interrupt_value["review_configs"]

        print("Action requests:", action_requests)
        print("Review configs:", review_configs)
        # Create a lookup map from tool name to review config
        config_map = {cfg["action_name"]: cfg for cfg in review_configs}

        # Display the pending actions to the user
        for action in action_requests:
            review_config = config_map[action["name"]]
            print(f"\nTool: {action['name']}")
            print(f"Arguments: {action['args']}")
            print(f"Allowed decisions: {review_config['allowed_decisions']}")

        # Get user decisions (one per action_request, in order)
        input_decision = input("\nApprove or reject? ").strip().lower()
        decisions = [
            {"type": input_decision}  # User approved the deletion
        ]

        # Resume execution with decisions
        result = agent.invoke(
            Command(resume={"decisions": decisions}),
            config=config,  # Must use the same config!
            version="v2",
        )

        # Process final result
    # print(result.value["messages"][-1].content)

    value = result.value
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        messages = value.get("messages", [])
        if messages:
            last = messages[-1]
            return last.content if hasattr(last, "content") else str(last)
    return str(value)

# ─────────────────────────────────────────────────────────────────────────────
# CLI entry point
# ─────────────────────────────────────────────────────────────────────────────

def main():
    print("╔══════════════════════════════════════════════╗")
    print("║         LUCID  –  AI Desktop Assistant       ║")
    print("║   Type your request. Ctrl+C / 'exit' to quit ║")
    print("╚══════════════════════════════════════════════╝\n")

    thread_id = "session-2"

    while True:
        try:
            user_input = input("You: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye.")
            sys.exit(0)

        if not user_input:
            continue
        if user_input.lower() in {"exit", "quit", "bye"}:
            print("LUCID: Goodbye!")
            sys.exit(0)

        try:
            answer = run_with_interrupts(user_input, thread_id=thread_id)
            print(f"\nLUCID: {answer}\n")
        except KeyboardInterrupt:
            print("\n[Interrupted by user]\n")
        except Exception as exc:
            print(f"\n[Error] {type(exc).__name__}: {exc}\n")


if __name__ == "__main__":
    main()
