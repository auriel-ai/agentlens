from agentlens.core import AgentLens

def test_record():
    lens = AgentLens()
    @lens.record
    def test_agent(x):
        return x
    test_agent("test")
    assert True  # Placeholder, expand later