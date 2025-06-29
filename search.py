class MockSearchTool:
    """Mock search tool with predefined results."""
    def run(self, query: str) -> str:
        mock_results = {
            "who is the president of usa": "Joe Biden",
            "weather in kathmandu": "It’s sunny, 28°C",
        }
        return mock_results.get(query.lower(), "No result found.")