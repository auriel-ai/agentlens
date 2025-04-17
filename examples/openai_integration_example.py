"""
Example demonstrating the OpenAI client integration for AgentLens.

Note: You will need to install openai to run this example:
pip install openai
"""

import os
from agentlens import AgentLens
from agentlens.integrations.openai import OpenAILens

def run_openai_integration_example():
    """Run an example demonstrating the OpenAI integration."""
    try:
        import openai
    except ImportError:
        print("This example requires openai. Install with: pip install openai")
        return

    # Check if OPENAI_API_KEY is set
    if "OPENAI_API_KEY" not in os.environ:
        print("Please set your OPENAI_API_KEY environment variable to run this example.")
        print("Example: export OPENAI_API_KEY='your-key-here'")
        return

    print("\n=== OpenAI Integration Example ===\n")

    # Initialize AgentLens and OpenAILens
    lens = AgentLens(log_file="openai_integration_runs.jsonl")
    openai_lens = OpenAILens(lens=lens)

    print("1. Modern OpenAI Client Example")
    print("-----------------------------")
    
    # Modern client setup
    client = openai.OpenAI()
    
    # Wrap the client
    wrapped_client = openai_lens.wrap_client(client)
    
    # Example 1: Chat completion
    print("Running chat completion...")
    chat_response = wrapped_client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Explain the concept of debugging in software development in one paragraph."}
        ]
    )
    
    print(f"Response: {chat_response.choices[0].message.content}\n")
    
    # Example 2: Completion
    print("Running completion...")
    completion_response = wrapped_client.completions.create(
        model="gpt-3.5-turbo-instruct",
        prompt="Write a short function in Python to calculate the Fibonacci sequence.",
        max_tokens=150
    )
    
    print(f"Response: {completion_response.choices[0].text}\n")
    
    # Example 3: Tool calling with function calling
    print("Running function calling example...")
    try:
        function_response = wrapped_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "What's the weather like in New York?"}
            ],
            tools=[{
                "type": "function",
                "function": {
                    "name": "get_weather",
                    "description": "Get the current weather in a given location",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "location": {
                                "type": "string",
                                "description": "The city and state, e.g. San Francisco, CA"
                            },
                            "unit": {
                                "type": "string",
                                "enum": ["celsius", "fahrenheit"]
                            }
                        },
                        "required": ["location"]
                    }
                }
            }],
            tool_choice="auto"
        )
        print("Function call detected:")
        
        if len(function_response.choices) > 0 and function_response.choices[0].message.tool_calls:
            tool_call = function_response.choices[0].message.tool_calls[0]
            print(f"Function: {tool_call.function.name}")
            print(f"Arguments: {tool_call.function.arguments}\n")
        else:
            print("No function call in the response\n")
            
    except Exception as e:
        print(f"Function calling failed (may not be available in your model): {e}\n")

    # Now demonstrate the replay and analysis features
    print("\n=== Replay, Analysis and Cost Tracking ===\n")
    
    # Replay the runs
    print("Replaying the chat completion run:")
    lens.replay(run_id=1)
    
    # Analyze the runs
    print("\nAnalyzing the chat completion run:")
    lens.analyze(run_id=1)
    
    # Show cost analysis for all runs
    print("\nCalculating costs for all runs:")
    lens.costs(all_runs=True)

if __name__ == "__main__":
    # Create examples directory if it doesn't exist
    os.makedirs("examples", exist_ok=True)
    run_openai_integration_example() 