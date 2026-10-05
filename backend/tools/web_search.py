import openai
from .schemas import WebSearchInput, WebSearchOutput
import os

# Set your OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

def web_search(args: WebSearchInput) -> WebSearchOutput:
    # Use OpenAI's API to generate search results
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",  # Use "gpt-4" or "gpt-3.5-turbo"
            messages=[
                {"role": "system", "content": "You are a helpful assistant that performs web searches."},
                {"role": "user", "content": f"Search the web for: {args.query}"}
            ],
            max_tokens=500,
            temperature=0.7,
        )

        # Extract the response content
        generated_text = response["choices"][0]["message"]["content"]

        # Parse the generated text into results and sources (you may need to customize this)
        results = generated_text.split("\n")[:3]  # Example: Take the first 3 lines as results
        sources = ["https://example.com/source1", "https://example.com/source2", "https://example.com/source3"]

        return WebSearchOutput(results=results, sources=sources)

    except Exception as e:
        print(f"Error during OpenAI API call: {e}")
        return WebSearchOutput(results=[], sources=[])

# def web_search(args: WebSearchInput) -> WebSearchOutput:
#     # Placeholder implementation for web search
#     # In a real implementation, you would call a web search API
#     results = ["Result 1", "Result 2", "Result 3"]
#     sources = ["https://example.com/result1", "https://example.com/result2", "https:example.com/result3"]
#     return WebSearchOutput(results=results, sources=sources)
