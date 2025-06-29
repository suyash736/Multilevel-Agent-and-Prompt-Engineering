class CalculatorTool:
    """Evaluates mathematical expressions."""
    def run(self, query: str) -> str:
        try:
            result = eval(query, {"__builtins__": {}}, {"sum": sum})
            return str(result)
        except Exception as e:
            return f"Error: {e}"