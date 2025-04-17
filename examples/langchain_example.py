"""
Example showing how to use AgentLens with LangChain.

Note: You will need to install langchain and openai to run this example:
pip install langchain openai
"""

import os
from agentlens import AgentLens

# Initialize AgentLens
lens = AgentLens(log_file="langchain_runs.jsonl")

def run_langchain_example():
    """Run a simple LangChain example with AgentLens recording."""
    try:
        from langchain.llms import OpenAI
        from langchain.agents import initialize_agent, Tool
        from langchain.agents import AgentType
        from langchain.chains import LLMChain
        from langchain.prompts import PromptTemplate
    except ImportError:
        print("This example requires langchain and openai. Install with: pip install langchain openai")
        return

    # Check if OPENAI_API_KEY is set
    if "OPENAI_API_KEY" not in os.environ:
        print("Please set your OPENAI_API_KEY environment variable to run this example.")
        print("Example: export OPENAI_API_KEY='your-key-here'")
        return

    print("\n=== LangChain + AgentLens Example ===\n")

    # Simple LLM chain with recording
    @lens.record
    def run_llm_chain(query, temperature=0.7):
        """Run a simple LangChain chain with recording."""
        # This will be recorded by AgentLens
        llm = OpenAI(temperature=temperature)
        template = "Question: {question}\nAnswer:"
        prompt = PromptTemplate(template=template, input_variables=["question"])
        chain = LLMChain(prompt=prompt, llm=llm)
        
        return chain.run(query)

    # Execute the chain
    print("Running LLM chain...")
    result1 = run_llm_chain("What are three benefits of good documentation?")
    print(f"Result: {result1}\n")

    # Simple Agent with tools
    @lens.record
    def run_agent_with_tools(query):
        """Run a LangChain agent with tools."""
        llm = OpenAI(temperature=0)
        
        # Define a simple tool
        def get_word_length(word):
            """Returns the length of a word."""
            return len(word)
            
        tools = [
            Tool(
                name="WordLength",
                func=get_word_length,
                description="Useful for getting the length of a word"
            )
        ]
        
        # Initialize the agent
        agent = initialize_agent(
            tools, 
            llm, 
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True
        )
        
        return agent.run(query)

    # Execute the agent
    print("Running agent with tools...")
    try:
        result2 = run_agent_with_tools("What's the length of the word 'refrigerator'?")
        print(f"Result: {result2}\n")
    except Exception as e:
        print(f"Agent execution failed: {e}\n")

    # Now demonstrate the replay and analysis features
    print("\n=== Replaying LangChain Runs ===\n")
    lens.replay()  # Replay the most recent run
    
    print("\n=== Analyzing LangChain Runs ===\n")
    lens.analyze()  # Analyze the most recent run
    
    print("\n=== Cost Analysis for LangChain Runs ===\n")
    lens.costs(all_runs=True)  # Analyze costs for all runs

if __name__ == "__main__":
    # Create examples directory if it doesn't exist
    os.makedirs("examples", exist_ok=True)
    run_langchain_example() 