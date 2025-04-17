import json
import os
import datetime
from functools import wraps
from typing import Dict, List, Any, Optional, Union, Callable

# Import terminal helpers (with fallback if rich is not installed)
try:
    from .terminal import print_run, print_analysis, print_costs
    TERMINAL_HELPERS = True
except (ImportError, ModuleNotFoundError):
    TERMINAL_HELPERS = False

class AgentLens:
    def __init__(self, log_file: str = "runs.jsonl", pricing_config: Dict = None):
        """
        Initialize AgentLens.
        
        Args:
            log_file: Path to the log file
            pricing_config: Dictionary with pricing information (e.g., {"gpt-4": 0.06, "gpt-3.5-turbo": 0.002})
        """
        self.log_file = log_file
        self.pricing_config = pricing_config or {
            "gpt-4": 0.06/1000,  # $0.06 per 1000 tokens
            "gpt-3.5-turbo": 0.002/1000,  # $0.002 per 1000 tokens
            "default": 0.01/1000  # Default fallback price
        }
        
        # Create the directory for the log file if it doesn't exist
        os.makedirs(os.path.dirname(os.path.abspath(log_file)) if os.path.dirname(log_file) else '.', exist_ok=True)
        
        # Get the latest run ID from the log file if it exists
        self.run_id = 0
        if os.path.exists(self.log_file):
            try:
                with open(self.log_file, "r") as f:
                    for line in f:
                        try:
                            run = json.loads(line)
                            if "id" in run and run["id"] > self.run_id:
                                self.run_id = run["id"]
                        except json.JSONDecodeError:
                            continue
            except FileNotFoundError:
                pass

    def record(self, func):
        """
        Decorator to record agent runs.
        
        Args:
            func: The agent function to record
            
        Returns:
            Wrapped function that records inputs, outputs, and metadata
        """
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Get start time and increment run ID
            start_time = datetime.datetime.now()
            self.run_id += 1
            current_run_id = self.run_id
            
            # Get model name from kwargs if available
            model = kwargs.get("model", kwargs.get("model_name", "default"))
            
            # Run the function and capture the result
            try:
                result = func(*args, **kwargs)
                status = "success"
                error = None
            except Exception as e:
                result = None
                status = "error"
                error = str(e)
                raise  # Re-raise the exception
            finally:
                # Calculate duration
                end_time = datetime.datetime.now()
                duration = (end_time - start_time).total_seconds()
                
                # Extract token usage if available
                tokens = 0
                token_details = {}
                
                # If result is a dict with a usage field (like OpenAI responses)
                if isinstance(result, dict) and "usage" in result:
                    token_details = result["usage"]
                    tokens = result["usage"].get("total_tokens", 0)
                
                # If using LangChain's output structure
                elif hasattr(result, "llm_output") and result.llm_output and "token_usage" in result.llm_output:
                    token_details = result.llm_output["token_usage"]
                    tokens = sum(result.llm_output["token_usage"].values())
                
                # Create log entry
                log = {
                    "id": current_run_id,
                    "timestamp": start_time.isoformat(),
                    "duration": duration,
                    "model": model,
                    "status": status,
                    "input": self._serialize_input(args, kwargs),
                    "output": self._serialize_output(result),
                    "error": error,
                    "tokens": tokens,
                    "token_details": token_details,
                    "tools": self._extract_tool_calls(result),
                }
                
                # Write to log file
                with open(self.log_file, "a") as f:
                    f.write(json.dumps(log) + "\n")
            
            return result
        return wrapper
    
    def context_record(self, model: str = "default"):
        """
        Context manager for recording agent runs without using a decorator.
        
        Args:
            model: The name of the model being used
            
        Returns:
            Context manager for recording
        """
        class AgentLensContext:
            def __init__(self, outer, model):
                self.outer = outer
                self.model = model
                self.start_time = None
                self.run_id = None
            
            def __enter__(self):
                self.start_time = datetime.datetime.now()
                self.outer.run_id += 1
                self.run_id = self.outer.run_id
                return self
            
            def log_run(self, input_data, output_data, token_usage=None, tool_calls=None, error=None):
                end_time = datetime.datetime.now()
                duration = (end_time - self.start_time).total_seconds()
                
                tokens = 0
                token_details = {}
                
                if token_usage:
                    if isinstance(token_usage, dict):
                        token_details = token_usage
                        tokens = sum(token_usage.values()) if isinstance(token_usage, dict) else token_usage
                    else:
                        tokens = token_usage
                
                log = {
                    "id": self.run_id,
                    "timestamp": self.start_time.isoformat(),
                    "duration": duration,
                    "model": self.model,
                    "status": "error" if error else "success",
                    "input": self.outer._serialize_input(input_data),
                    "output": self.outer._serialize_output(output_data),
                    "error": error,
                    "tokens": tokens,
                    "token_details": token_details,
                    "tools": tool_calls or [],
                }
                
                with open(self.outer.log_file, "a") as f:
                    f.write(json.dumps(log) + "\n")
            
            def __exit__(self, exc_type, exc_val, exc_tb):
                # We don't automatically log here - the user must call log_run explicitly
                pass
        
        return AgentLensContext(self, model)

    def replay(self, run_id: Optional[int] = None, verbose: bool = True):
        """
        Replay a recorded agent run.
        
        Args:
            run_id: ID of the run to replay (defaults to the last run)
            verbose: Whether to print detailed information
            
        Returns:
            The run data
        """
        if not os.path.exists(self.log_file):
            print(f"No logs found at {self.log_file}")
            return None
            
        with open(self.log_file, "r") as f:
            runs = [json.loads(line) for line in f]
        
        if not runs:
            print("No runs recorded yet")
            return None
            
        # Get the run to replay
        if run_id:
            matching_runs = [r for r in runs if r["id"] == run_id]
            if not matching_runs:
                print(f"Run {run_id} not found")
                return None
            run = matching_runs[0]
        else:
            run = runs[-1]  # Default to last run
        
        if verbose:
            if TERMINAL_HELPERS:
                print_run(run, verbose)
            else:
                print(f"\n=== Run #{run['id']} - {run['timestamp']} ===")
                print(f"Model: {run.get('model', 'N/A')}")
                print(f"Status: {run.get('status', 'N/A')}")
                print(f"Duration: {run.get('duration', 'N/A'):.2f} seconds")
                print(f"Tokens: {run.get('tokens', 'N/A')}")
                
                print("\n--- Input ---")
                print(json.dumps(run["input"], indent=2))
                
                print("\n--- Output ---")
                print(json.dumps(run["output"], indent=2))
                
                if run.get("error"):
                    print("\n--- Error ---")
                    print(run["error"])
                
                if run.get("tools"):
                    print("\n--- Tool Calls ---")
                    for i, tool in enumerate(run["tools"]):
                        print(f"Tool {i+1}: {tool.get('name', 'unnamed')}")
                        print(f"  Arguments: {json.dumps(tool.get('arguments', {}), indent=2)}")
                        print(f"  Response: {json.dumps(tool.get('response', None), indent=2)}")
                
                if run.get('token_details'):
                    print("\n--- Token Details ---")
                    print(json.dumps(run["token_details"], indent=2))
                
        return run
    
    def analyze(self, run_id: Optional[int] = None):
        """
        Analyze a run for potential failures.
        
        Args:
            run_id: ID of the run to analyze (defaults to the last run)
            
        Returns:
            Dictionary with analysis results
        """
        run = self.replay(run_id, verbose=False)
        if not run:
            return None
            
        issues = []
        insights = []
        
        # Check for empty output
        if not run["output"] and run["status"] != "error":
            issues.append("Empty output detected")
        
        # Check for errors
        if run["status"] == "error":
            issues.append(f"Run failed with error: {run['error']}")
        
        # Check for timeout indicators
        if run.get("duration", 0) > 30:  # Assuming >30s might be a timeout concern
            issues.append(f"Potential timeout: Run took {run['duration']:.2f} seconds")
        
        # Check for potentially short/hallucinated outputs
        if isinstance(run["output"], str) and len(run["output"]) < 10:
            issues.append("Very short output detected - potential truncation or hallucination")
        
        # Analyze token usage
        token_count = run.get("tokens", 0)
        if token_count > 1000:
            insights.append(f"High token usage: {token_count} tokens")
        
        # Tool call analysis
        tools = run.get("tools", [])
        if tools:
            insights.append(f"Used {len(tools)} tool calls")
            for tool in tools:
                if tool.get("error"):
                    issues.append(f"Tool '{tool.get('name', 'unnamed')}' failed: {tool.get('error')}")
        
        # Create analysis result
        analysis = {
            "run_id": run["id"],
            "issues": issues,
            "insights": insights
        }
        
        # Print the analysis
        if TERMINAL_HELPERS:
            print_analysis(analysis)
        else:
            print(f"\n=== Analysis for Run #{run['id']} ===")
            
            if not issues and not insights:
                print("No issues detected!")
                
            if issues:
                print("\n⚠️ Potential Issues:")
                for issue in issues:
                    print(f"  • {issue}")
                    
            if insights:
                print("\n🔍 Insights:")
                for insight in insights:
                    print(f"  • {insight}")
        
        return analysis
    
    def costs(self, run_id: Optional[int] = None, all_runs: bool = False):
        """
        Calculate estimated costs for runs.
        
        Args:
            run_id: ID of the specific run to calculate costs for
            all_runs: Whether to calculate costs for all runs
            
        Returns:
            Dictionary with cost information
        """
        if not os.path.exists(self.log_file):
            print(f"No logs found at {self.log_file}")
            return None
            
        with open(self.log_file, "r") as f:
            runs = [json.loads(line) for line in f]
        
        if not runs:
            print("No runs recorded yet")
            return None
            
        if run_id and not all_runs:
            matching_runs = [r for r in runs if r["id"] == run_id]
            if not matching_runs:
                print(f"Run {run_id} not found")
                return None
            runs_to_analyze = matching_runs
        elif all_runs:
            runs_to_analyze = runs
        else:
            runs_to_analyze = [runs[-1]]  # Default to last run
        
        total_cost = 0
        total_tokens = 0
        costs_by_model = {}
        
        for run in runs_to_analyze:
            model = run.get("model", "default")
            tokens = run.get("tokens", 0)
            
            # Get price per token
            price_per_token = self.pricing_config.get(model, self.pricing_config["default"])
            
            # Calculate cost
            cost = tokens * price_per_token
            total_cost += cost
            total_tokens += tokens
            
            # Update model-specific stats
            if model not in costs_by_model:
                costs_by_model[model] = {"tokens": 0, "cost": 0, "runs": 0}
            costs_by_model[model]["tokens"] += tokens
            costs_by_model[model]["cost"] += cost
            costs_by_model[model]["runs"] += 1
        
        # Create cost analysis result
        cost_analysis = {
            "total_cost": total_cost,
            "total_tokens": total_tokens,
            "costs_by_model": costs_by_model,
            "runs_analyzed": len(runs_to_analyze)
        }
        
        # Print the cost analysis
        if TERMINAL_HELPERS:
            print_costs(cost_analysis)
        else:
            if all_runs:
                print(f"\n=== Cost Analysis for All {len(runs_to_analyze)} Runs ===")
            elif len(runs_to_analyze) == 1:
                print(f"\n=== Cost Analysis for Run #{runs_to_analyze[0]['id']} ===")
            else:
                print(f"\n=== Cost Analysis for {len(runs_to_analyze)} Runs ===")
            
            print(f"Total tokens: {total_tokens:,}")
            print(f"Estimated total cost: ${total_cost:.4f}")
            
            if len(costs_by_model) > 1:
                print("\nBreakdown by Model:")
                for model, stats in costs_by_model.items():
                    print(f"  • {model}: ${stats['cost']:.4f} ({stats['tokens']:,} tokens, {stats['runs']} runs)")
        
        return cost_analysis
    
    def _serialize_input(self, *args, **kwargs):
        """Helper method to serialize inputs into a JSON-serializable format"""
        try:
            # If only one argument and it's already a dictionary, use it directly
            if len(args) == 1 and len(kwargs) == 0 and isinstance(args[0], dict):
                return args[0]
            
            # Otherwise, combine args and kwargs
            input_data = {"args": list(args), "kwargs": kwargs} if kwargs else list(args)
            json.dumps(input_data)  # Test if serializable
            return input_data
        except TypeError:
            # If not serializable, create a string representation
            return str({"args": args, "kwargs": kwargs} if kwargs else args)
    
    def _serialize_output(self, output):
        """Helper method to serialize outputs into a JSON-serializable format"""
        try:
            # Test if directly serializable
            json.dumps(output)
            return output
        except TypeError:
            # If not serializable, create a string representation
            return str(output)
    
    def _extract_tool_calls(self, result):
        """Extract tool calls from the result if available"""
        tools = []
        
        # Check for OpenAI-style tool calls
        if isinstance(result, dict) and "tool_calls" in result:
            tools = result["tool_calls"]
        
        # Check for LangChain-style tool calls
        elif hasattr(result, "intermediate_steps"):
            for action, response in getattr(result, "intermediate_steps", []):
                tool = {
                    "name": getattr(action, "tool", action.tool_name if hasattr(action, "tool_name") else "unknown"),
                    "arguments": getattr(action, "tool_input", {}),
                    "response": response,
                }
                tools.append(tool)
        
        return tools

def cli():
    """Command line interface for AgentLens"""
    import argparse

    parser = argparse.ArgumentParser(description="AgentLens CLI")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Replay command
    replay_parser = subparsers.add_parser("replay", help="Replay a recorded run")
    replay_parser.add_argument("--id", type=int, help="ID of the run to replay")
    replay_parser.add_argument("--file", default="runs.jsonl", help="Path to the log file")

    # Analyze command
    analyze_parser = subparsers.add_parser("analyze", help="Analyze a recorded run")
    analyze_parser.add_argument("--id", type=int, help="ID of the run to analyze")
    analyze_parser.add_argument("--file", default="runs.jsonl", help="Path to the log file")

    # Costs command
    costs_parser = subparsers.add_parser("costs", help="Calculate costs for runs")
    costs_parser.add_argument("--id", type=int, help="ID of the run to calculate costs for")
    costs_parser.add_argument("--all", action="store_true", help="Calculate costs for all runs")
    costs_parser.add_argument("--file", default="runs.jsonl", help="Path to the log file")

    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return

    lens = AgentLens(log_file=args.file)
    
    if args.command == "replay":
        lens.replay(run_id=args.id)
    elif args.command == "analyze":
        lens.analyze(run_id=args.id)
    elif args.command == "costs":
        lens.costs(run_id=args.id, all_runs=args.all)