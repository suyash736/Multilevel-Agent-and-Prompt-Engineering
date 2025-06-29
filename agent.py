import re
import json
import os
from typing import Dict, Any, List
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate

from calculator import CalculatorTool
from search import MockSearchTool


class Configuration:
    """Configuration for the agent."""
    model = "gemini-1.5-flash"
    json_schema = {"type" : "object",
                   "properties": {
                       "steps": {
                           "type": "array",
                           "items": {"type": "string"}
                       }
                   },
                   "required": ["steps"]
    }

    prompt_template = """Break down the mathematical expression '{expression}' into steps.
    Provide a list of operations to perform, ensuring each step is a valid arithmetic operation.
    Example: For '2 * 3 + 4', return {{"steps": ["2 * 3", "6 + 4"]}}.
    Return the steps as a JSON object with a 'steps' key."""

class LLM:
    """Handles LLM interactions."""
    def __init__(self, model:str, json_schema: Dict[str,Any]):
        if not os.getenv("GOOGLE_API_KEY"):
            raise EnvironmentError("LLM API not found.")
        self.llm = ChatGoogleGenerativeAI(
            model=model,
            google_api_key = os.getenv("GOOGLE_API_KEY"),
            model_kwargs = {"respose_mime_type": "application/json", "response_schema":json_schema}
        )

    def invoke(self, prompt: str, expression:str) -> Any:
        """Invokes the LLM (gemini) with the given prompt and expression."""
        try:
            chain = PromptTemplate.from_template(prompt)|self.llm
            return chain.invoke({"expression": expression})
        except Exception as e:
            raise ValueError(f'LLM Invocation failed: {str(e)}')
        

class ResponseParser:
    """Parses LLM responses to extract structured data."""
    @staticmethod
    def parse(response: Any) -> List[str]:
        """Extracts steps from LLM response, handling various formats."""
        try:
            content = response.content if hasattr(response, 'content') else str(response)
            print(f"Raw LLM response: {content}")  # Debug: Log raw response
            try:
                parsed = json.loads(content)
                steps = parsed.get("steps", []) if isinstance(parsed, dict) else parsed
                if not isinstance(steps, list):
                    raise ValueError("Parsed response 'steps' is not a list")
                # Filter out non-arithmetic steps
                valid_steps = [step for step in steps if re.match(r'^[\d\s+*\/()-]+$', step)]
                return valid_steps
            except json.JSONDecodeError:
                # Fallback: extract arithmetic expressions only
                steps = re.findall(r'[\'"]([\d\s+*\/()-]+)[\'"]', content)
                if not steps:
                    steps = [s.strip().strip('"\'') for s in content.replace('[', '').replace(']', '').split(',') if s.strip()]
                    steps = [s for s in steps if re.match(r'^[\d\s+*\/()-]+$', s)]
                return steps
        except Exception as e:
            raise ValueError(f"Failed to parse response: {str(e)}")

class Orchestrator:
    """Handles breakdown, routing and execution of tasks"""
    def __init__(self):
        self.config = Configuration()
        self.llm_client = LLM(self.config.model, self.config.json_schema)
        self.parser = ResponseParser()
        self.calculator = CalculatorTool()
        self.search_tool = MockSearchTool()

    def run(self, task:str) -> str:
        """Routes and process input task"""
        try:
            if "calculate" in task.lower():
                return self.handle_calculation(task)
            elif "who is" in task.lower() or "weather" in task.lower():
                return self.search_tool.run(task)
            else:
                return "I cannot process this task."
        except Exception as e:
            return f'Error: {str(e)}'
    
    def handle_calculation(self, task:str) -> str:
        """Handles the calculation by parsing and executing the steps"""
        try:
            expression = task.lower().replace("calculate", "").strip().replace("×", "*")
            response = self.llm_client.invoke(self.config.prompt_template, expression)
            steps = self.parser.parse(response)
            print(steps)
            if not steps:
                return f'Error: No steps recieved.'
            result = 0
            for step in steps:
                step_result = self.calculator.run(step)
                if step_result.startswith("Error"):
                    return step_result
                result = float(step_result)
            return str(result)
        except Exception as e:
            return f'Calcualtion error: {str(e)}'

