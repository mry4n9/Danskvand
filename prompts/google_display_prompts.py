def get_google_display_prompt(context_url_summary: str, additional_context_summary: str) -> str:
    context_section = f"""
    Context URL Summary:
    ---
    {context_url_summary}
    ---
    
    Additional Context Summary:
    ---
    {additional_context_summary}
    ---"""

    return f"""
    You are an expert Google Display Ads copywriter. Based on the provided context, generate components for Responsive Display Ads.

{context_section}

    Provide a single JSON object with two keys: "headlines" and "descriptions".
    - "headlines": A list of 5 unique headline strings. Each headline should be approximately 30 characters or less. (These are short headlines)
    - "descriptions": A list of 5 unique description strings. Each description should be approximately 90 characters or less. (These are long headlines or descriptions)

    Focus on visual appeal in text, benefits, and clear calls to action relevant to the context.
    Example JSON structure:
    {{
      "headlines": [
        "Short Headline 1 (Max 30)",
        "Catchy Phrase 2",
        ... (5 total)
      ],
      "descriptions": [
        "Longer Description 1: Elaborate on benefits. (Max 90 Chars)",
        "Description 2: Compelling offer or USP. Visit Us!",
        ... (5 total)
      ]
    }}
    """