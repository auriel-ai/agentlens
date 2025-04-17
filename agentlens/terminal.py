"""
Terminal output helpers for AgentLens.
"""
import json
from typing import Any, Dict, List, Optional, Union

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.syntax import Syntax
    from rich.text import Text
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

console = Console() if RICH_AVAILABLE else None

def print_run(run: Dict[str, Any], verbose: bool = True) -> None:
    """
    Print a run to the terminal with enhanced formatting if rich is available.
    
    Args:
        run: The run data to print
        verbose: Whether to print detailed information
    """
    if not RICH_AVAILABLE:
        # Fallback to simple printing if rich is not available
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
        return

    # Rich formatting
    title = f"Run #{run['id']} - {run['timestamp']}"
    
    # Create the header
    table = Table(show_header=False, box=None)
    table.add_column("Property", style="bold cyan")
    table.add_column("Value")
    
    table.add_row("Model", run.get('model', 'N/A'))
    
    # Add status with color
    status = run.get('status', 'N/A')
    status_style = "green" if status == "success" else "red"
    table.add_row("Status", Text(status, style=status_style))
    
    table.add_row("Duration", f"{run.get('duration', 'N/A'):.2f} seconds")
    table.add_row("Tokens", f"{run.get('tokens', 0):,}")
    
    console.print(Panel(table, title=title, border_style="blue"))
    
    # Print input
    if isinstance(run["input"], dict):
        input_json = json.dumps(run["input"], indent=2)
        console.print(Panel(Syntax(input_json, "json", theme="monokai"), 
                           title="Input", border_style="green"))
    else:
        console.print(Panel(str(run["input"]), title="Input", border_style="green"))
    
    # Print output
    if run.get("error"):
        console.print(Panel(run["error"], title="Error", border_style="red"))
    
    if isinstance(run["output"], dict):
        output_json = json.dumps(run["output"], indent=2)
        console.print(Panel(Syntax(output_json, "json", theme="monokai"), 
                           title="Output", border_style="yellow"))
    else:
        console.print(Panel(str(run["output"]), title="Output", border_style="yellow"))
    
    # Print tool calls
    if run.get("tools") and verbose:
        tools_table = Table(title="Tool Calls", show_header=True)
        tools_table.add_column("Tool", style="cyan")
        tools_table.add_column("Arguments")
        tools_table.add_column("Response")
        
        for tool in run["tools"]:
            name = tool.get('name', 'unnamed')
            args = json.dumps(tool.get('arguments', {}), indent=2)
            response = json.dumps(tool.get('response', None), indent=2)
            tools_table.add_row(name, args, response)
        
        console.print(tools_table)
    
    # Print token details
    if run.get('token_details') and verbose:
        token_table = Table(title="Token Details", show_header=True)
        token_table.add_column("Type", style="cyan")
        token_table.add_column("Count", style="green")
        
        for token_type, count in run.get('token_details', {}).items():
            token_table.add_row(token_type, str(count))
        
        console.print(token_table)

def print_analysis(analysis: Dict[str, Any]) -> None:
    """
    Print analysis results with enhanced formatting if rich is available.
    
    Args:
        analysis: The analysis data to print
    """
    if not analysis:
        return
        
    if not RICH_AVAILABLE:
        # Fallback to simple printing
        print(f"\n=== Analysis for Run #{analysis['run_id']} ===")
        
        if not analysis.get('issues') and not analysis.get('insights'):
            print("No issues detected!")
            
        if analysis.get('issues'):
            print("\n⚠️ Potential Issues:")
            for issue in analysis['issues']:
                print(f"  • {issue}")
                
        if analysis.get('insights'):
            print("\n🔍 Insights:")
            for insight in analysis['insights']:
                print(f"  • {insight}")
        return
    
    # Rich formatting
    title = f"Analysis for Run #{analysis['run_id']}"
    
    if not analysis.get('issues') and not analysis.get('insights'):
        console.print(Panel("[bold green]No issues detected!", title=title, border_style="blue"))
        return
    
    # Create panel content
    content = ""
    
    if analysis.get('issues'):
        content += "[bold red]⚠️ Potential Issues:[/bold red]\n"
        for issue in analysis['issues']:
            content += f"  • {issue}\n"
            
    if content and analysis.get('insights'):
        content += "\n"  # Add separator
        
    if analysis.get('insights'):
        content += "[bold blue]🔍 Insights:[/bold blue]\n"
        for insight in analysis['insights']:
            content += f"  • {insight}\n"
    
    console.print(Panel(content, title=title, border_style="blue"))

def print_costs(costs: Dict[str, Any]) -> None:
    """
    Print cost analysis results with enhanced formatting if rich is available.
    
    Args:
        costs: The cost data to print
    """
    if not costs:
        return
        
    if not RICH_AVAILABLE:
        # Fallback to simple printing
        runs_count = costs.get('runs_analyzed', 0)
        
        if runs_count == 1:
            print(f"\n=== Cost Analysis for Run #{list(costs.get('runs_analyzed', {}).keys())[0]} ===")
        else:
            print(f"\n=== Cost Analysis for {runs_count} Runs ===")
        
        print(f"Total tokens: {costs.get('total_tokens', 0):,}")
        print(f"Estimated total cost: ${costs.get('total_cost', 0):.4f}")
        
        if len(costs.get('costs_by_model', {})) > 1:
            print("\nBreakdown by Model:")
            for model, stats in costs.get('costs_by_model', {}).items():
                print(f"  • {model}: ${stats['cost']:.4f} ({stats['tokens']:,} tokens, {stats['runs']} runs)")
        return
    
    # Rich formatting
    runs_count = costs.get('runs_analyzed', 0)
    
    if runs_count == 1:
        title = "Cost Analysis"
    else:
        title = f"Cost Analysis for {runs_count} Runs"
    
    # Create cost table
    table = Table(title=title)
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")
    
    table.add_row("Total Tokens", f"{costs.get('total_tokens', 0):,}")
    table.add_row("Estimated Cost", f"${costs.get('total_cost', 0):.4f}")
    
    console.print(table)
    
    # If multiple models, show breakdown
    if len(costs.get('costs_by_model', {})) > 1:
        model_table = Table(title="Model Breakdown")
        model_table.add_column("Model", style="cyan")
        model_table.add_column("Cost", style="green")
        model_table.add_column("Tokens", style="blue")
        model_table.add_column("Runs", style="magenta")
        
        for model, stats in costs.get('costs_by_model', {}).items():
            model_table.add_row(
                model,
                f"${stats['cost']:.4f}",
                f"{stats['tokens']:,}",
                str(stats['runs'])
            )
            
        console.print(model_table) 