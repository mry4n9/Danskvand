import streamlit as st
from modules import utils, data_extraction, ai_processing, excel_processing
from prompts import email_prompts, linkedin_prompts, facebook_prompts, google_search_prompts, google_display_prompts
import time

# --- Page Config ---
st.set_page_config(page_title="Branding & Marketing Ad Generator", layout="centered")

# --- Initialize Session State ---
if 'generated_excel_bytes' not in st.session_state:
    st.session_state.generated_excel_bytes = None
if 'company_name_for_file' not in st.session_state:
    st.session_state.company_name_for_file = "report"
if 'lead_objective_for_file' not in st.session_state:
    st.session_state.lead_objective_for_file = "general"

# --- UI Sections ---
st.title("M Funnel Generator")
st.markdown("Extract source material for tailored content generation.")

# --- API Key Check ---
openai_api_key = st.secrets.get("OPENAI_API_KEY")
if not openai_api_key or not openai_api_key.startswith("sk-"):
    st.error("OpenAI API key is not configured correctly in secrets.toml. Please add your key.")
    st.stop()

client = ai_processing.get_openai_client()
if not client:
    st.error("Failed to initialize OpenAI client. Check API key and network.")
    st.stop()

# --- Column Layout for Inputs ---
col1, col2 = st.columns(2)

with col1:
    st.header("1. Company Info")
    client_url_input = st.text_input("Client's Website URL")
    additional_context_file = st.file_uploader("Upload Additional Company Context (PDF or PPTX)", type=["pdf", "pptx"], key="additional_context")
    lead_magnet_file = st.file_uploader("Upload Lead Magnet (PDF)", type=["pdf"], key="lead_magnet")

with col2:
    st.header("2. Campaign Options")
    lead_objective_options = ["Demo Booking", "Sales Meeting"]
    lead_objective_input = st.selectbox("Lead Objective", lead_objective_options, key="lead_obj")

    learn_more_link_input = st.text_input("Link to 'Learn More' Page", key="learn_more")
    lead_magnet_download_link_input = st.text_input("Link to Lead Magnet Download", key="lead_magnet_dl")

    if lead_objective_input == "Demo Booking":
        objective_link_label = "Link to Demo Booking Page"
    else: # Sales Meeting
        objective_link_label = "Link to Sales Meeting Booking Page"
    objective_specific_link_input = st.text_input(objective_link_label, key="obj_link")

    content_count_input = st.slider("Ad Variations per Channel x Funnel Stage", 1, 20, 10, key="content_count")

# --- Generate Button & Progress ---
st.header("3. Generate Content")

if st.button("✨ Generate Ad Content", type="primary"):
    # Reset previous generation ( use_container_width=True)
    st.session_state.generated_excel_bytes = None

    # --- Input Validation ---
    valid_inputs = True
    if not client_url_input:
        st.warning("Client's Website URL is required.")
        valid_inputs = False

    client_url = utils.validate_and_format_url(client_url_input)
    if not client_url:
        st.error("Invalid Client Website URL format.")
        valid_inputs = False

    learn_more_link = utils.validate_and_format_url(learn_more_link_input)
    if not learn_more_link:
        st.warning("Learn More link is recommended.") # Not strictly required

    lead_magnet_download_link = utils.validate_and_format_url(lead_magnet_download_link_input)
    if not lead_magnet_download_link:
        st.warning("Lead Magnet Download link is recommended for Demand Gen ads.")

    objective_specific_link = utils.validate_and_format_url(objective_specific_link_input)
    if not objective_specific_link:
        st.warning(f"{objective_link_label} is recommended for Demand Capture ads.")

    if not valid_inputs:
        st.stop()

    st.session_state.company_name_for_file = utils.extract_company_name_from_url(client_url)
    st.session_state.lead_objective_for_file = utils.sanitize_for_filename(lead_objective_input)

    progress_bar = st.progress(0, text="Initializing...")

    # --- 1. Context Extraction & Summarization ---
    summaries = []
    with st.spinner("Extracting and summarizing website content..."):
        progress_bar.progress(5, text="Extracting website content...")
        website_text = data_extraction.extract_text_from_url(client_url)
        if website_text:
            progress_bar.progress(10, text="Summarizing website content...")
            website_summary = ai_processing.summarize_text(website_text, client)
            if website_summary:
                summaries.append(f"Website Summary:\n{website_summary}")
            st.success("Website content processed.")
        else:
            st.warning("Could not extract text from website URL.")

    if additional_context_file:
        with st.spinner("Extracting and summarizing additional context file..."):
            progress_bar.progress(15, text="Extracting additional context...")
            additional_text = data_extraction.extract_text_from_file(additional_context_file)
            if additional_text:
                progress_bar.progress(20, text="Summarizing additional context...")
                additional_summary = ai_processing.summarize_text(additional_text, client)
                if additional_summary:
                    summaries.append(f"Additional Context Summary:\n{additional_summary}")
                st.success("Additional context file processed.")
            else:
                st.warning("Could not extract text from additional context file.")

    if lead_magnet_file:
        with st.spinner("Extracting and summarizing lead magnet file..."):
            progress_bar.progress(25, text="Extracting lead magnet content...")
            lead_magnet_text = data_extraction.extract_text_from_file(lead_magnet_file)
            if lead_magnet_text:
                progress_bar.progress(30, text="Summarizing lead magnet content...")
                lead_magnet_summary = ai_processing.summarize_text(lead_magnet_text, client)
                if lead_magnet_summary:
                    summaries.append(f"Lead Magnet Summary:\n{lead_magnet_summary}")
                st.success("Lead magnet file processed.")
            else:
                st.warning("Could not extract text from lead magnet file.")

    if not summaries:
        st.error("No context could be extracted or summarized. Please provide at least a website URL.")
        st.stop()

    combined_summary = "\n\n---\n\n".join(summaries)
    # st.subheader("Combined Summary for AI Prompts:")
    # st.text_area("", combined_summary, height=200) # For debugging

    # --- 2. Generate Ad Content ---
    all_ad_content_json = {}
    total_tasks = 8 # Email, 3x LinkedIn, 3x Facebook, Google Search, Google Display
    completed_tasks = 0 # <<< CORRECTION: Define completed_tasks BEFORE the function that uses it nonlocally

    def update_progress(task_name):
        # nonlocal completed_tasks # <<< REMOVE THIS LINE
        # Directly access and modify completed_tasks from the enclosing scope
        global completed_tasks # <<< USE GLOBAL INSTEAD
        completed_tasks += 1
        progress_value = 30 + int((completed_tasks / total_tasks) * 65) # 30% for context, 65% for generation
        # Ensure progress doesn't exceed 100 if total_tasks is slightly off or rounding occurs
        progress_value = min(progress_value, 95) # Cap generation progress before final step
        progress_bar.progress(progress_value, text=f"Generating {task_name}...")

    with st.spinner("Generating Email Content..."):
        email_prompt = email_prompts.get_email_prompt(combined_summary, lead_objective_input, objective_specific_link or client_url, content_count_input)
        all_ad_content_json["Email"] = ai_processing.generate_json_content(client, email_prompt, "Email Ads")
        update_progress("Email Ads")

    # LinkedIn Ads
    linkedin_stages = {
        "BA": ("Brand Awareness", learn_more_link or client_url, "Learn More"),
        "DG": ("Demand Gen", lead_magnet_download_link or client_url, "Download"),
        "DC": ("Demand Capture", objective_specific_link or client_url, "Register, Request Demo")
    }
    for key, (stage_name, link, cta) in linkedin_stages.items():
        with st.spinner(f"Generating LinkedIn {stage_name} Ads..."):
            prompt = linkedin_prompts.get_linkedin_prompt(combined_summary, stage_name, link, cta, content_count_input, lead_objective_input)
            all_ad_content_json[f"LinkedIn_{key}"] = ai_processing.generate_json_content(client, prompt, f"LinkedIn {stage_name} Ads")
            update_progress(f"LinkedIn {stage_name} Ads")
            time.sleep(0.5) # Small delay if API rate limits are a concern

    # Facebook Ads
    facebook_stages = {
        "BA": ("Brand Awareness", learn_more_link or client_url, "Learn More"),
        "DG": ("Demand Gen", lead_magnet_download_link or client_url, "Download"),
        "DC": ("Demand Capture", objective_specific_link or client_url, "Book Now")
    }
    for key, (stage_name, link, cta) in facebook_stages.items():
        with st.spinner(f"Generating Facebook {stage_name} Ads..."):
            prompt = facebook_prompts.get_facebook_prompt(combined_summary, stage_name, link, cta, content_count_input, lead_objective_input)
            all_ad_content_json[f"Facebook_{key}"] = ai_processing.generate_json_content(client, prompt, f"Facebook {stage_name} Ads")
            update_progress(f"Facebook {stage_name} Ads")
            time.sleep(0.5)

    with st.spinner("Generating Google Search Ad Components..."):
        gsearch_prompt = google_search_prompts.get_google_search_prompt(combined_summary)
        all_ad_content_json["GoogleSearch"] = ai_processing.generate_json_content(client, gsearch_prompt, "Google Search Ads")
        update_progress("Google Search Ads")
        time.sleep(0.5)

    with st.spinner("Generating Google Display Ad Components..."):
        gdisplay_prompt = google_display_prompts.get_google_display_prompt(combined_summary)
        all_ad_content_json["GoogleDisplay"] = ai_processing.generate_json_content(client, gdisplay_prompt, "Google Display Ads")
        update_progress("Google Display Ads")

    # --- 3. Create Excel Report ---
    # Update progress before starting Excel formatting
    progress_bar.progress(95, text="Formatting Excel report...")
    with st.spinner("Creating Excel report..."):
        # Filter out None values from all_ad_content_json before passing
        valid_ad_content = {k: v for k, v in all_ad_content_json.items() if v is not None}
        if not valid_ad_content:
            st.error("No ad content was successfully generated. Cannot create Excel report.")
            # Ensure progress bar completes even on error
            progress_bar.progress(100, text="Generation failed. No content.")
            st.stop()

        excel_bytes = excel_processing.create_excel_report(
            valid_ad_content,
            st.session_state.company_name_for_file,
            lead_objective_input
        )
        st.session_state.generated_excel_bytes = excel_bytes

    progress_bar.progress(100, text="Content generation complete!")
    st.success("🎉 Ad content generated and Excel report is ready for download!")

# --- Download Button ---
if st.session_state.generated_excel_bytes:
    file_name = f"{st.session_state.company_name_for_file}_funnel.xlsx"
    st.download_button(
        label="📥 Download Funnel",
        data=st.session_state.generated_excel_bytes,
        file_name=file_name,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )

st.markdown("---")
st.markdown("Made by M. Version 0.9")