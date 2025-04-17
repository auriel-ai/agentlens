"""
Basic tests for AgentLens core functionality.
"""

import os
import json
import tempfile
import unittest
from agentlens import AgentLens

class TestAgentLens(unittest.TestCase):
    """Test cases for the AgentLens core functionality."""
    
    def setUp(self):
        """Set up a temporary log file for testing."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.log_file = os.path.join(self.temp_dir.name, "test_runs.jsonl")
        self.lens = AgentLens(log_file=self.log_file)
    
    def tearDown(self):
        """Clean up temporary files."""
        self.temp_dir.cleanup()
    
    def test_record_decorator(self):
        """Test that the record decorator properly logs agent runs."""
        # Define a test agent function
        @self.lens.record
        def test_agent(query, model="test-model"):
            return f"Response to: {query}"
        
        # Run the agent
        result = test_agent("test query", model="test-model")
        
        # Verify the result
        self.assertEqual(result, "Response to: test query")
        
        # Verify the log file was created and contains the run
        self.assertTrue(os.path.exists(self.log_file))
        
        with open(self.log_file, "r") as f:
            logs = [json.loads(line) for line in f]
        
        self.assertEqual(len(logs), 1)
        self.assertEqual(logs[0]["id"], 1)
        self.assertEqual(logs[0]["model"], "test-model")
        self.assertEqual(logs[0]["output"], "Response to: test query")
    
    def test_context_manager(self):
        """Test that the context manager properly logs agent runs."""
        # Use the context manager
        with self.lens.context_record(model="test-model-2") as recording:
            input_data = "test query via context"
            output_data = "Response via context"
            token_usage = {"prompt_tokens": 5, "completion_tokens": 3, "total_tokens": 8}
            recording.log_run(
                input_data=input_data,
                output_data=output_data,
                token_usage=token_usage
            )
        
        # Verify the log file was created and contains the run
        with open(self.log_file, "r") as f:
            logs = [json.loads(line) for line in f]
        
        self.assertEqual(len(logs), 1)
        self.assertEqual(logs[0]["id"], 1)
        self.assertEqual(logs[0]["model"], "test-model-2")
        # Checking the serialized input contains our input text
        self.assertIn(input_data, str(logs[0]["input"]))
        self.assertEqual(logs[0]["output"], "Response via context")
        # The tokens value may be calculated differently based on implementation
        # Just verify that token information is present
        self.assertIn("tokens", logs[0])
        self.assertIn("token_details", logs[0])
    
    def test_error_handling(self):
        """Test that errors in agent runs are properly logged."""
        # Define a test agent function that raises an exception
        @self.lens.record
        def failing_agent(query):
            raise ValueError("Test error")
        
        # Run the agent and catch the error
        with self.assertRaises(ValueError):
            failing_agent("test query")
        
        # Verify the log file contains the error
        with open(self.log_file, "r") as f:
            logs = [json.loads(line) for line in f]
        
        self.assertEqual(len(logs), 1)
        self.assertEqual(logs[0]["status"], "error")
        self.assertEqual(logs[0]["error"], "Test error")
    
    def test_multiple_runs(self):
        """Test recording and retrieving multiple runs."""
        # Define a test agent function
        @self.lens.record
        def test_agent(query, model="test-model"):
            return f"Response to: {query}"
        
        # Run the agent multiple times
        test_agent("query 1", model="test-model")
        test_agent("query 2", model="test-model")
        test_agent("query 3", model="test-model")
        
        # Verify all runs were logged
        with open(self.log_file, "r") as f:
            logs = [json.loads(line) for line in f]
        
        self.assertEqual(len(logs), 3)
        self.assertEqual(logs[0]["id"], 1)
        self.assertEqual(logs[1]["id"], 2)
        self.assertEqual(logs[2]["id"], 3)
        
        # Test retrieving a specific run
        run = self.lens.replay(run_id=2, verbose=False)
        self.assertEqual(run["id"], 2)
        # Check that the input contains our query string somewhere
        self.assertIn("query 2", str(run["input"]))

if __name__ == "__main__":
    unittest.main()