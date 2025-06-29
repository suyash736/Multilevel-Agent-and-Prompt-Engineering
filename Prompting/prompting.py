import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
import json


if not os.getenv("GOOGLE_API_KEY"):
     raise EnvironmentError("LLM API not found.")

model_name = "gemini-2.5-flash"

model = ChatGoogleGenerativeAI(
     model = model_name,
     google_api_key = os.getenv("GOOGLE_API_KEY")
)


prompt_template = """
You are a riddle-solving expert.
You are given fused animal words that are created by using the first three letters of both animals, concatenating them together and reversing the result.
For example, "barlow" comes from "rabbit" (rab) + "wolf" (wol) → "rabwol" → reversed to "lowbar" (barlow), representing "wolf + rabbit".

For each of the given fused words: {fused_word}, perform these steps:
1. Lowercase and Reverse the fused word.
2. Split the fused words into two equal parts.
3. Identify the names of the animals that start from those parted letters.
4. Return the JSON Object as an output where:
    Each key is a fused word and the value for each key contains the list of string which are the names of the two animals .

Strictly stick instructions for solving the riddle.

Output only the JSON object, ensuring it is valid and concise. Strictly adhere to the given example strcture of output. Example:
{{
  "barlow": "wolf + rabbit",
  "all_animals": ["rabbit", "wolf"]
}}
"""

prompt = PromptTemplate.from_template(prompt_template)
chain = prompt | model

fused_word = ["Aebrib", "Oilnid", "Somoro"]

response = chain.invoke({"fused_word": json.dumps(fused_word)})

try:
    result = json.loads(response.content)
    print(json.dumps(result, indent=2))
except json.JSONDecodeError:
    print("Error: LLM output is not valid JSON")
    print("Raw output:", response.content)