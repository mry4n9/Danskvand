def get_google_search_prompt(context_summary: str) -> str:
    return f"""
    You are an expert Google Search Ads copywriter. Based on the provided context, generate components for Responsive Search Ads (RSAs).

    Context:
    ---
    {context_summary}
    ---

    Provide a single JSON object with two keys: "headlines" and "descriptions".
    - "headlines": A list of 15 unique headline strings. Each headline should be approximately 30 characters or less.
    - "descriptions": A list of 4 unique description strings. Each description should be approximately 90 characters or less.

    Focus on keywords, benefits, and calls to action relevant to the context.
    Example JSON structure:
    {{
      "headlines": [
        "Headline 1 (Max 30 Chars)",
        "Headline 2 (Benefit)",
        ... (15 total)
      ],
      "descriptions": [
        "Description 1: Feature + Benefit. Call to Action (Max 90 Chars)",
        "Description 2: Unique Selling Proposition. Learn More Here.",
        ... (4 total)
      ]
    }}
    """