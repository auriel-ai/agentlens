"""
Advanced example demonstrating the LangChain integration for AgentLens.

Note: You will need to install langchain and openai to run this example:
pip install langchain openai
"""

import os
from agentlens import AgentLens
from agentlens.integrations.langchain import LangChainLens

def run_langchain_integration_example():
    """Run a more advanced LangChain integration example."""
    try:
        from langchain.llms import OpenAI
        from langchain.agents import initialize_agent, Tool, AgentType
        from langchain.chains import LLMChain
        from langchain.memory import ConversationBufferMemory
        from langchain.prompts import PromptTemplate
    except ImportError:
        print("This example requires langchain and openai. Install with: pip install langchain openai")
        return

    # Check if OPENAI_API_KEY is set
    if "OPENAI_API_KEY" not in os.environ:
        print("Please set your OPENAI_API_KEY environment variable to run this example.")
        print("Example: export OPENAI_API_KEY='your-key-here'")
        return

    print("\n=== LangChain Integration Example ===\n")

    # Initialize AgentLens and LangChainLens
    lens = AgentLens(log_file="langchain_integration_runs.jsonl")
    lc_lens = LangChainLens(lens=lens)

    # 1. Example with a simple LLM
    print("1. Simple LLM Example")
    print("--------------------")
    
    llm = OpenAI(temperature=0.7)
    
    # Wrap the LLM with LangChainLens
    wrapped_llm = lc_lens.wrap_llm(llm)
    
    # Use the wrapped LLM
    print("Running wrapped LLM...")
    llm_response = wrapped_llm("What are three best practices for writing clean code?")
    print(f"Response: {llm_response}\n")

    # 2. Example with a chain
    print("2. Chain with Memory Example")
    print("--------------------------")
    
    # Create a chain with memory
    template = """
    You are a helpful assistant that provides information about programming languages.
    
    Current conversation:
    {chat_history}
    
    Human: {question}
    AI Assistant:"""
    
    prompt = PromptTemplate(
        input_variables=["chat_history", "question"], 
        template=template
    )
    
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    chain = LLMChain(
        llm=OpenAI(temperature=0),
        prompt=prompt,
        memory=memory,
        verbose=True
    )
    
    # Wrap the chain with LangChainLens
    wrapped_chain = lc_lens.wrap_chain(chain)
    
    # Use the wrapped chain in a conversation
    print("Running wrapped chain with memory...")
    response1 = wrapped_chain.run(question="What are the key features of Python?")
    print(f"Response 1: {response1}\n")
    
    response2 = wrapped_chain.run(question="How does it compare to JavaScript?")
    print(f"Response 2: {response2}\n")

    # 3. Example with an agent using tools
    print("3. Agent with Tools Example")
    print("-------------------------")
    
    # Define tools
    def get_word_length(word):
        """Returns the length of a word."""
        return len(word)
    
    def get_word_first_letter(word):
        """Returns the first letter of a word."""
        return word[0] if word else ""
    
    tools = [
        Tool(
            name="WordLength",
            func=get_word_length,
            description="Returns the length of a word. Input should be a single word."
        ),
        Tool(
            name="FirstLetter",
            func=get_word_first_letter,
            description="Returns the first letter of a word. Input should be a single word."
        )
    ]
    
    # Initialize an agent
    agent = initialize_agent(
        tools, 
        OpenAI(temperature=0), 
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True
    )
    
    # Wrap the agent with LangChainLens
    wrapped_agent = lc_lens.wrap_agent(agent)
    
    # Use the wrapped agent
    print("Running wrapped agent with tools...")
    try:
        agent_response = wrapped_agent.run(
            "What's the length of the word 'Python' and what's its first letter?"
        )
        print(f"Agent response: {agent_response}\n")
    except Exception as e:
        print(f"Agent execution failed: {e}\n")

    # Now demonstrate the replay and analysis features
    print("\n=== Replay, Analysis and Cost Tracking ===\n")
    
    # Replay the agent run (usually the most interesting)
    print("Replaying the agent run:")
    lens.replay(run_id=3)
    
    # Analyze the agent run
    print("\nAnalyzing the agent run:")
    lens.analyze(run_id=3)
    
    # Show cost analysis for all runs
    print("\nCalculating costs for all runs:")
    lens.costs(all_runs=True)

if __name__ == "__main__":
    # Create examples directory if it doesn't exist
    os.makedirs("examples", exist_ok=True)
    run_langchain_integration_example() 