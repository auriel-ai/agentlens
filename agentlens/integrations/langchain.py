"""
LangChain integration for AgentLens.
"""

import functools
import json
from typing import Any, Dict, Optional, Callable, List, Union

from ..core import AgentLens

class LangChainLens:
    """AgentLens integration for LangChain."""
    
    def __init__(self, lens: Optional[AgentLens] = None, log_file: str = "langchain_runs.jsonl"):
        """
        Initialize LangChain integration.
        
        Args:
            lens: Existing AgentLens instance, or a new one will be created
            log_file: Path to the log file (only used if lens is not provided)
        """
        self.lens = lens or AgentLens(log_file=log_file)
    
    def wrap_llm(self, llm):
        """
        Wrap a LangChain LLM to record its invocations.
        
        Args:
            llm: LangChain LLM object
            
        Returns:
            Wrapped LLM
        """
        original_call = llm._call
        
        @functools.wraps(original_call)
        def wrapped_call(prompt, stop=None, **kwargs):
            # Record the start of the call
            with self.lens.context_record(model=getattr(llm, 'model_name', 'langchain')) as recording:
                # Call the original method
                try:
                    result = original_call(prompt, stop=stop, **kwargs)
                    
                    # Extract token usage from llm
                    token_usage = None
                    if hasattr(llm, 'get_token_ids'):
                        try:
                            prompt_tokens = len(llm.get_token_ids(prompt))
                            completion_tokens = len(llm.get_token_ids(result))
                            token_usage = {
                                "prompt_tokens": prompt_tokens,
                                "completion_tokens": completion_tokens,
                                "total_tokens": prompt_tokens + completion_tokens
                            }
                        except Exception:
                            pass
                    
                    # Record the call
                    recording.log_run(
                        input_data=prompt,
                        output_data=result,
                        token_usage=token_usage
                    )
                    
                    return result
                except Exception as e:
                    # Record the error
                    recording.log_run(
                        input_data=prompt,
                        output_data=None,
                        error=str(e)
                    )
                    raise
        
        # Replace the _call method
        llm._call = wrapped_call
        return llm
    
    def wrap_chain(self, chain):
        """
        Wrap a LangChain Chain to record its invocations.
        
        Args:
            chain: LangChain Chain object
            
        Returns:
            Wrapped Chain
        """
        original_call = chain.__call__
        
        @functools.wraps(original_call)
        def wrapped_call(*args, **kwargs):
            # Determine input based on args and kwargs
            input_data = kwargs.copy()
            if args and len(args) > 0:
                input_data["args"] = args
            
            # Record the start of the call
            with self.lens.context_record(model=getattr(chain, '_llm_type', 'langchain_chain')) as recording:
                # Call the original method
                try:
                    result = original_call(*args, **kwargs)
                    
                    # Extract token usage if available
                    token_usage = None
                    tool_calls = []
                    
                    # If chain has memory with chat_memory, extract interactions
                    if hasattr(chain, 'memory') and hasattr(chain.memory, 'chat_memory'):
                        chat_history = []
                        for message in chain.memory.chat_memory.messages:
                            chat_history.append({
                                "role": message.type,
                                "content": message.content
                            })
                        input_data["chat_history"] = chat_history
                    
                    # If chain has llm_output, extract token usage
                    if hasattr(result, 'llm_output') and result.llm_output:
                        if 'token_usage' in result.llm_output:
                            token_usage = result.llm_output['token_usage']
                    
                    # Extract intermediate steps for agents
                    if hasattr(result, 'intermediate_steps') and result.intermediate_steps:
                        for action, output in result.intermediate_steps:
                            tool_name = action.tool if hasattr(action, 'tool') else "unknown"
                            tool_calls.append({
                                "name": tool_name,
                                "arguments": action.tool_input if hasattr(action, 'tool_input') else {},
                                "response": output
                            })
                    
                    # Convert result to serializable form
                    if hasattr(result, 'to_json'):
                        output_data = json.loads(result.to_json())
                    elif hasattr(result, 'dict'):
                        output_data = result.dict()
                    else:
                        # For simple string results or other return types
                        output_data = str(result)
                    
                    # Record the call
                    recording.log_run(
                        input_data=input_data,
                        output_data=output_data,
                        token_usage=token_usage,
                        tool_calls=tool_calls
                    )
                    
                    return result
                except Exception as e:
                    # Record the error
                    recording.log_run(
                        input_data=input_data,
                        output_data=None,
                        error=str(e)
                    )
                    raise
        
        # Replace the call method
        chain.__call__ = wrapped_call
        return chain
    
    def wrap_agent(self, agent):
        """
        Wrap a LangChain Agent to record its invocations.
        
        Args:
            agent: LangChain Agent object
            
        Returns:
            Wrapped Agent
        """
        # For most agents, wrapping the chain is sufficient
        if hasattr(agent, 'agent_chain'):
            return self.wrap_chain(agent.agent_chain)
        elif hasattr(agent, 'chain'):
            return self.wrap_chain(agent.chain)
        else:
            # Fallback for other types of agents
            original_call = agent.__call__
            
            @functools.wraps(original_call)
            def wrapped_call(*args, **kwargs):
                # Determine input based on args and kwargs
                input_data = kwargs.copy()
                if args and len(args) > 0:
                    input_data["args"] = args
                
                # Record the start of the call
                with self.lens.context_record(model=getattr(agent, '_llm_type', 'langchain_agent')) as recording:
                    # Call the original method
                    try:
                        result = original_call(*args, **kwargs)
                        
                        # Record the call (simplified for generic agents)
                        recording.log_run(
                            input_data=input_data,
                            output_data=str(result)
                        )
                        
                        return result
                    except Exception as e:
                        # Record the error
                        recording.log_run(
                            input_data=input_data,
                            output_data=None,
                            error=str(e)
                        )
                        raise
            
            # Replace the call method
            agent.__call__ = wrapped_call
            return agent 