"""
A quickstart example showing the basic AgentLens functionality.
This example doesn't require any API keys or dependencies.
"""

from agentlens import AgentLens

def some_function(query):
    """Simulate an agent function."""
    return f"The answer to '{query}' is 42."

def run_quickstart():
    """Demonstrate the core functionality of AgentLens as shown in the README."""
    print("\n=== AgentLens Quickstart Example ===\n")
    
    # Initialize AgentLens
    lens = AgentLens(log_file="quickstart_runs.jsonl")
    
    # 1. Record agent runs with a decorator
    @lens.record
    def my_agent_function(query, model="example-model"):
        print(f"Agent processing: {query}")
        # Your agent implementation would go here
        return f"Response to: {query}"
    
    # Use your agent normally - AgentLens records in the background
    print("\n1. Using the decorator to record a run:")
    response = my_agent_function("Process this data")
    print(f"Got response: {response}\n")
    
    # 2. Or use the context manager for more control
    print("2. Using the context manager for more control:")
    with lens.context_record(model="gpt-4") as recording:
        # Your agent code here
        query = "Tell me something interesting"
        print(f"Agent processing: {query}")
        result = some_function(query)
        print(f"Agent result: {result}")
        
        recording.log_run(
            input_data=query,
            output_data=result,
            token_usage={"prompt_tokens": 10, "completion_tokens": 20}
        )
    print()
    
    # 3. Replay the last recorded run
    print("3. Replaying the last recorded run:")
    lens.replay()
    
    # 4. Analyze failures in the last run
    print("\n4. Analyzing the last run:")
    lens.analyze()
    
    # 5. Track estimated costs
    print("\n5. Tracking estimated costs:")
    lens.costs(all_runs=True)

if __name__ == "__main__":
    run_quickstart() 