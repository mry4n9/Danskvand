def get_linkedin_prompt(context_summary: str, funnel_stage: str, destination_link: str, cta_button_options: str, content_count: int, lead_objective: str = None) -> str:
    
    intro_text_guidance = "300-400 characters. Hook in the first 150 characters. Embed relevant emojis. Split into paragraphs for readability."
    headline_chars = "~70 characters."
    
    specific_instructions = ""
    if funnel_stage == "Brand Awareness":
        specific_instructions = f"Focus on education, problem/solution awareness. Destination link is for learning more. CTA button should be '{cta_button_options}' or left empty if appropriate."
    elif funnel_stage == "Demand Gen":
        specific_instructions = f"Focus on a lead magnet or valuable resource. Destination link is for download. CTA button should be '{cta_button_options}'."
    elif funnel_stage == "Demand Capture":
        specific_instructions = f"Focus on direct action like booking a demo or sales meeting ({lead_objective}). Destination link is for this action. CTA button should be one of '{cta_button_options}'."

    return f"""
    You are an expert LinkedIn advertising copywriter. Based on the provided context, generate {content_count} variations of a LinkedIn ad for the {funnel_stage} funnel stage.
    {specific_instructions}
    The destination URL for this ad is: {destination_link}

    Context:
    ---
    {context_summary}
    ---

    For each ad variation, provide a JSON object with the following keys: "introductory_text", "image_copy", "headline", "destination_url", "cta_button".
    - "introductory_text": {intro_text_guidance}
    - "image_copy": Compelling text for the accompanying ad image (5-10 words).
    - "headline": {headline_chars}
    - "destination_url": Use this exact URL: {destination_link}
    - "cta_button": Choose an appropriate CTA button text from the options: {cta_button_options}. If options allow empty for Brand Awareness, you can return an empty string.

    Output a single JSON object with a key "linkedin_{funnel_stage.lower().replace(' ', '_')}_ads" containing a list of these {content_count} ad variations.
    Wrap introductory_text with "\ n" at the beginning and end to simulate vertical padding.
    Example for one variation:
    {{
      "introductory_text": "🚀 Discover how [Company Benefit] can transform your business! Learn more about our innovative solutions.",
      "image_copy": "Transform Your Business Today",
      "headline": "Innovative Solutions for Growth by [Company Name]",
      "destination_url": "{destination_link}",
      "cta_button": "{cta_button_options.split(',')[0].strip() if cta_button_options else 'Learn More'}"
    }}
    """