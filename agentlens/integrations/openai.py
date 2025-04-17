"""
OpenAI client integration for AgentLens.
"""

import functools
import inspect
import json
from typing import Any, Dict, Optional, Callable, List, Union

from ..core import AgentLens

class OpenAILens:
    """AgentLens integration for OpenAI client."""
    
    def __init__(self, lens: Optional[AgentLens] = None, log_file: str = "openai_runs.jsonl"):
        """
        Initialize OpenAI integration.
        
        Args:
            lens: Existing AgentLens instance, or a new one will be created
            log_file: Path to the log file (only used if lens is not provided)
        """
        self.lens = lens or AgentLens(log_file=log_file)
    
    def wrap_client(self, client):
        """
        Wrap an OpenAI client to record its completions and chat completions.
        
        Args:
            client: OpenAI client object
            
        Returns:
            Wrapped client
        """
        # Check if it's the new OpenAI client
        if hasattr(client, 'chat') and hasattr(client.chat, 'completions'):
            # Wrap chat completions
            self._wrap_new_chat_completions(client)
            # Wrap completions
            self._wrap_new_completions(client)
        # Fall back to legacy client
        elif hasattr(client, 'create'):
            self._wrap_legacy_client(client)
        
        return client
    
    def _wrap_new_chat_completions(self, client):
        """Wrap the chat.completions.create method in the new OpenAI client."""
        original_create = client.chat.completions.create
        
        @functools.wraps(original_create)
        def wrapped_create(*args, **kwargs):
            # Get the model from kwargs
            model = kwargs.get('model', 'unknown')
            messages = kwargs.get('messages', [])
            
            # Record the call
            with self.lens.context_record(model=model) as recording:
                try:
                    response = original_create(*args, **kwargs)
                    
                    # Extract token usage
                    token_usage = None
                    if hasattr(response, 'usage'):
                        token_usage = {
                            "prompt_tokens": response.usage.prompt_tokens,
                            "completion_tokens": response.usage.completion_tokens,
                            "total_tokens": response.usage.total_tokens
                        }
                    
                    # Extract tool calls if present
                    tool_calls = []
                    if hasattr(response, 'choices') and response.choices:
                        first_choice = response.choices[0]
                        if hasattr(first_choice, 'message') and hasattr(first_choice.message, 'tool_calls'):
                            for tc in first_choice.message.tool_calls:
                                tool_calls.append({
                                    "name": tc.function.name,
                                    "arguments": json.loads(tc.function.arguments),
                                    "id": tc.id
                                })
                    
                    # Convert response to a serializable format
                    serializable_response = self._make_serializable(response)
                    
                    # Record the chat completion
                    recording.log_run(
                        input_data={"messages": messages, **kwargs},
                        output_data=serializable_response,
                        token_usage=token_usage,
                        tool_calls=tool_calls
                    )
                    
                    return response
                except Exception as e:
                    # Record the error
                    recording.log_run(
                        input_data={"messages": messages, **kwargs},
                        output_data=None,
                        error=str(e)
                    )
                    raise
        
        # Replace the create method
        client.chat.completions.create = wrapped_create
    
    def _wrap_new_completions(self, client):
        """Wrap the completions.create method in the new OpenAI client."""
        original_create = client.completions.create
        
        @functools.wraps(original_create)
        def wrapped_create(*args, **kwargs):
            # Get the model and prompt from kwargs
            model = kwargs.get('model', 'unknown')
            prompt = kwargs.get('prompt', '')
            
            # Record the call
            with self.lens.context_record(model=model) as recording:
                try:
                    response = original_create(*args, **kwargs)
                    
                    # Extract token usage
                    token_usage = None
                    if hasattr(response, 'usage'):
                        token_usage = {
                            "prompt_tokens": response.usage.prompt_tokens,
                            "completion_tokens": response.usage.completion_tokens,
                            "total_tokens": response.usage.total_tokens
                        }
                    
                    # Convert response to a serializable format
                    serializable_response = self._make_serializable(response)
                    
                    # Record the completion
                    recording.log_run(
                        input_data={"prompt": prompt, **kwargs},
                        output_data=serializable_response,
                        token_usage=token_usage
                    )
                    
                    return response
                except Exception as e:
                    # Record the error
                    recording.log_run(
                        input_data={"prompt": prompt, **kwargs},
                        output_data=None,
                        error=str(e)
                    )
                    raise
        
        # Replace the create method
        client.completions.create = wrapped_create
    
    def _wrap_legacy_client(self, client):
        """Wrap the methods in the legacy OpenAI client."""
        # Check for chat completions
        if hasattr(client, 'ChatCompletion') and hasattr(client.ChatCompletion, 'create'):
            original_chat_create = client.ChatCompletion.create
            
            @functools.wraps(original_chat_create)
            def wrapped_chat_create(*args, **kwargs):
                # Get the model and messages from kwargs
                model = kwargs.get('model', 'unknown')
                messages = kwargs.get('messages', [])
                
                # Record the call
                with self.lens.context_record(model=model) as recording:
                    try:
                        response = original_chat_create(*args, **kwargs)
                        
                        # Extract token usage
                        token_usage = None
                        if 'usage' in response:
                            token_usage = response['usage']
                        
                        # Extract tool calls if present
                        tool_calls = []
                        if 'choices' in response and response['choices']:
                            choice = response['choices'][0]
                            if 'message' in choice and 'tool_calls' in choice['message']:
                                for tc in choice['message']['tool_calls']:
                                    tool_calls.append({
                                        "name": tc['function']['name'],
                                        "arguments": json.loads(tc['function']['arguments']),
                                        "id": tc['id']
                                    })
                        
                        # Record the chat completion
                        recording.log_run(
                            input_data={"messages": messages, **kwargs},
                            output_data=response,
                            token_usage=token_usage,
                            tool_calls=tool_calls
                        )
                        
                        return response
                    except Exception as e:
                        # Record the error
                        recording.log_run(
                            input_data={"messages": messages, **kwargs},
                            output_data=None,
                            error=str(e)
                        )
                        raise
            
            # Replace the create method
            client.ChatCompletion.create = wrapped_chat_create
        
        # Check for completions
        if hasattr(client, 'Completion') and hasattr(client.Completion, 'create'):
            original_completion_create = client.Completion.create
            
            @functools.wraps(original_completion_create)
            def wrapped_completion_create(*args, **kwargs):
                # Get the model and prompt from kwargs
                model = kwargs.get('model', 'unknown')
                prompt = kwargs.get('prompt', '')
                
                # Record the call
                with self.lens.context_record(model=model) as recording:
                    try:
                        response = original_completion_create(*args, **kwargs)
                        
                        # Extract token usage
                        token_usage = None
                        if 'usage' in response:
                            token_usage = response['usage']
                        
                        # Record the completion
                        recording.log_run(
                            input_data={"prompt": prompt, **kwargs},
                            output_data=response,
                            token_usage=token_usage
                        )
                        
                        return response
                    except Exception as e:
                        # Record the error
                        recording.log_run(
                            input_data={"prompt": prompt, **kwargs},
                            output_data=None,
                            error=str(e)
                        )
                        raise
            
            # Replace the create method
            client.Completion.create = wrapped_completion_create
    
    def _make_serializable(self, obj):
        """Convert an object to a JSON-serializable format."""
        if hasattr(obj, 'model_dump'):
            # For Pydantic v2 models
            return obj.model_dump()
        elif hasattr(obj, 'dict'):
            # For Pydantic v1 models
            return obj.dict()
        elif hasattr(obj, '__dict__'):
            # For general objects
            result = {}
            for key, value in obj.__dict__.items():
                if not key.startswith('_'):
                    if isinstance(value, (list, tuple)):
                        result[key] = [self._make_serializable(item) for item in value]
                    elif hasattr(value, '__dict__') or hasattr(value, 'dict') or hasattr(value, 'model_dump'):
                        result[key] = self._make_serializable(value)
                    else:
                        try:
                            json.dumps({key: value})
                            result[key] = value
                        except TypeError:
                            result[key] = str(value)
            return result
        else:
            # For primitive types
            return str(obj) 