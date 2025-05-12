import streamlit as st
from openai import OpenAI
import json

# Use the model name you have access to
# For this example, we'll use "gpt-4o-mini" as a placeholder for "gpt-4.1-mini"
# if "gpt-4.1-mini" is not yet available via API string.
# Update this to "gpt-4.1-mini" when you confirm the exact model identifier.
# If "gpt-4.1-mini" is the exact string, use that.
# For broad compatibility, "gpt-4o-mini" is a recent, capable model.
# The user specified "gpt-4.1-mini", so we'll assume it's a valid model string.
AI_MODEL = "gpt-4.1-mini" # Or "gpt-4o-mini" if "gpt-4.1-mini" is not the API identifier
SUMMARIZER_MODEL = "gpt-4.1-mini" # Can be a cheaper model if needed, but let's stick to user's model

@st.cache_resource
def get_openai_client():
    """Initializes and returns the OpenAI client."""
    try:
        client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
        return client
    except Exception as e:
        st.error(f"Failed to initialize OpenAI client: {e}")
        return None

@st.cache_data(show_spinner=False)
def summarize_text(_text_to_summarize: str, _client, max_chars: int = 2500) -> str | None:
    """Summarizes text using OpenAI API."""
    if not _text_to_summarize:
        return None
    if not _client:
        st.error("OpenAI client not available for summarization.")
        return None

    try:
        prompt = f"""
        Please summarize the following text, focusing on aspects relevant for marketing and advertising copy. 
        Identify the company's unique selling propositions, target audience (if discernible), products/services, 
        and overall brand voice/tone. The summary should be a maximum of {max_chars} characters.
        Ensure the summary is dense with information useful for creating ad copy.

        Text to summarize:
        ---
        {_text_to_summarize[:30000]} 
        ---
        Concise Summary (max {max_chars} chars):
        """
        # Truncate input text to avoid overly long prompts for summarization
        
        response = _client.chat.completions.create(
            model=SUMMARIZER_MODEL,
            messages=[
                {"role": "system", "content": "You are an expert marketing analyst skilled at extracting key information for ad copywriting."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=int(max_chars / 3), # Estimate tokens based on chars
            temperature=0.3,
        )
        summary = response.choices[0].message.content.strip()
        return summary[:max_chars] # Enforce max_chars strictly
    except Exception as e:
        st.error(f"Error during summarization: {e}")
        return None

def generate_json_content(client, prompt_text: str, content_description: str) -> dict | list | None:
    """
    Generates content from OpenAI as JSON.
    `content_description` is for error messages, e.g., "Email Ads".
    """
    if not client:
        st.error(f"OpenAI client not available for generating {content_description}.")
        return None
    try:
        response = client.chat.completions.create(
            model=AI_MODEL,
            messages=[
                {"role": "system", "content": "You are an expert marketing copywriter. Generate content in the specified JSON format."},
                {"role": "user", "content": prompt_text}
            ],
            response_format={"type": "json_object"}, # Request JSON mode
            temperature=0.7, # Creative but not too random
            # max_tokens can be adjusted based on expected output size
        )
        content_json_str = response.choices[0].message.content
        
        # The response content is a JSON string, parse it
        parsed_json = json.loads(content_json_str)
        return parsed_json
    except json.JSONDecodeError as e:
        st.error(f"Error decoding JSON from AI for {content_description}: {e}")
        st.error(f"Received string: {content_json_str}")
        return None
    except Exception as e:
        st.error(f"Error generating {content_description} content: {e}")
        return None