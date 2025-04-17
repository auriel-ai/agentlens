"""
Tests for AgentLens integrations.
These tests just verify that the integration modules can be imported.
"""

import unittest
import importlib

class TestIntegrations(unittest.TestCase):
    """Test cases for AgentLens integrations."""
    
    def test_langchain_integration_import(self):
        """Test that the LangChain integration can be imported."""
        try:
            langchain_lens = importlib.import_module("agentlens.integrations.langchain")
            self.assertTrue(hasattr(langchain_lens, "LangChainLens"))
        except ImportError:
            self.skipTest("LangChain integration not available.")
    
    def test_openai_integration_import(self):
        """Test that the OpenAI integration can be imported."""
        try:
            openai_lens = importlib.import_module("agentlens.integrations.openai")
            self.assertTrue(hasattr(openai_lens, "OpenAILens"))
        except ImportError:
            self.skipTest("OpenAI integration not available.")

if __name__ == "__main__":
    unittest.main() 