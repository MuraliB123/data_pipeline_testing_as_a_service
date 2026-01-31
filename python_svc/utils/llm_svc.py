from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
# Set your OpenAI API key (recommended: use environment variable)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def call_openai_llm(prompt, model="gpt-3.5-turbo", max_tokens=256, temperature=0.7):
    """
    Calls the OpenAI LLM API with the given prompt.
    Returns the response text.
    """
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=max_tokens,
        temperature=temperature
    )
    return response.choices[0].message.content.strip()

if __name__ == "__main__":
    test_prompt = "Explain the theory of relativity in simple terms."
    response = call_openai_llm(test_prompt)
    print("Response from OpenAI LLM:")
    print(response)