"""
Basic example of using AgentLens to record, replay, and analyze AI agent runs.
"""

import os
import time
from agentlens import AgentLens

# Initialize AgentLens
lens = AgentLens(log_file="example_runs.jsonl")

# Example 1: Using the decorator to record a function
@lens.record
def simple_agent(query, model="gpt-3.5-turbo"):
    """Simulate a simple agent that processes a query."""
    print(f"Agent processing: {query}")
    time.sleep(1)  # Simulate processing time
    
    # Simulate a response with token usage (like OpenAI's response format)
    response = {
        "choices": [{
            "message": {
                "content": f"Response to: {query}"
            }
        }],
        "usage": {
            "prompt_tokens": len(query.split()),
            "completion_tokens": 5,  
            "total_tokens": len(query.split()) + 5
        }
    }
    return response

# Example 2: Using the context manager approach
def another_agent_call(query, model="gpt-4"):
    """Simulate another type of agent call using the context manager."""
    print(f"Another agent processing: {query}")
    time.sleep(1.5)  # Simulate processing time
    
    # Simulate some error for demonstration
    success = len(query) > 10
    
    # Create a response
    if success:
        result = f"Detailed response to: {query}"
        token_usage = {"prompt_tokens": len(query.split()), "completion_tokens": 10, "total_tokens": len(query.split()) + 10}
        error = None
    else:
        result = ""
        token_usage = {"prompt_tokens": len(query.split()), "completion_tokens": 0, "total_tokens": len(query.split())}
        error = "Input query too short"
    
    return success, result, token_usage, error

def run_examples():
    """Run the examples and demonstrate AgentLens features."""
    print("\n=== AgentLens Basic Example ===\n")
    
    # Example 1: Using the decorator
    print("Running example with decorator...")
    response = simple_agent("What is the weather today?")
    print(f"Got response: {response['choices'][0]['message']['content']}\n")
    
    # Example 2: Using the context manager
    print("Running example with context manager...")
    with lens.context_record(model="gpt-4") as recording:
        query = "Tell me a short story"
        success, result, token_usage, error = another_agent_call(query)
        recording.log_run(
            input_data=query,
            output_data=result,
            token_usage=token_usage,
            error=error
        )
        print(f"Got result: {'Success' if success else 'Failed'}\n")
    
    # Example 3: Using context manager with a failing call
    print("Running example with a failing call...")
    with lens.context_record(model="gpt-4") as recording:
        query = "Hi"  # Short query that will "fail"
        success, result, token_usage, error = another_agent_call(query)
        recording.log_run(
            input_data=query,
            output_data=result,
            token_usage=token_usage,
            error=error
        )
        print(f"Got result: {'Success' if success else 'Failed'}\n")
    
    # Now demonstrate the replay and analysis features
    print("\n=== Replaying Runs ===\n")
    lens.replay(run_id=1)  # Replay first run
    
    print("\n=== Analyzing Runs ===\n")
    lens.analyze(run_id=3)  # Analyze the failing run
    
    print("\n=== Cost Analysis ===\n")
    lens.costs(all_runs=True)

if __name__ == "__main__":
    # Create examples directory if it doesn't exist
    os.makedirs("examples", exist_ok=True)
    run_examples() 