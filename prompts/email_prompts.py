def get_email_prompt(context_summary: str, lead_objective: str, objective_link: str, content_count: int) -> str:
    return f"""
    You are an expert email marketing copywriter. Based on the provided context, generate {content_count} variations of a demand capture email.
    The lead objective is: {lead_objective}.
    The primary call to action link is: {objective_link}

    Context:
    ---
    {context_summary}
    ---

    For each email variation, provide a JSON object with the following keys: "headline", "subject_line", "body", "cta".
    - "headline": A compelling headline for the email (can be similar to subject or an internal title).
    - "subject_line": An engaging subject line for the email.
    - "body": Start with "Hi [First Name],". 2-3 paragraphs. Embed the link '{objective_link}' naturally within the body where appropriate for the call to action.
    - "cta": A condensed version of the call to action text from the body (e.g., "Book a Demo", "Schedule a Meeting").

    Output a single JSON object with a key "emails" containing a list of these {content_count} email variations.
    Wrap body with "\ n" at the beginning and end to simulate vertical padding.
    Example for one variation:
    {{
      "headline": "Unlock Growth with Our Solution",
      "subject_line": "Ready to achieve {lead_objective}?",
      "body": "Paragraph 1 introducing the problem and solution based on context... We help you achieve {lead_objective}. Learn more and book your session here: {objective_link}. Paragraph 2 with benefits... Paragraph 3 with final call to action.",
      "cta": "Book Your {lead_objective}"
    }}
    """