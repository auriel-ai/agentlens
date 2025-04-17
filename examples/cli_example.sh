#!/bin/bash
# This script demonstrates how to use the AgentLens CLI

# First, generate some example runs by running the basic example
echo "Generating example runs..."
python examples/basic_example.py

echo ""
echo "================================================================="
echo "AgentLens CLI Examples"
echo "================================================================="

# Show help
echo ""
echo "Showing help:"
python -m agentlens --help

# Replay a run
echo ""
echo "Replaying the last run:"
python -m agentlens replay --file example_runs.jsonl

# Replay a specific run
echo ""
echo "Replaying a specific run (run #1):"
python -m agentlens replay --id 1 --file example_runs.jsonl

# Analyze a run
echo ""
echo "Analyzing the last run:"
python -m agentlens analyze --file example_runs.jsonl

# Analyze a specific run (the one with an error)
echo ""
echo "Analyzing a specific run (the one with an error, run #3):"
python -m agentlens analyze --id 3 --file example_runs.jsonl

# Calculate costs for a specific run
echo ""
echo "Calculating costs for a specific run:"
python -m agentlens costs --id 1 --file example_runs.jsonl

# Calculate costs for all runs
echo ""
echo "Calculating costs for all runs:"
python -m agentlens costs --all --file example_runs.jsonl 