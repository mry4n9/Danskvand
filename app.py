import streamlit as st
from modules import utils, data_extraction, ai_processing, excel_processing, document_processing # Added document_processing
from prompts import email_prompts, linkedin_prompts, facebook_prompts, google_search_prompts, google_display_prompts
import time

# --- Page Config ---
st.set_page_config(page_title="Branding & Marketing Ad Generator", layout="wide")

# --- Initialize Session State ---
if 'generated_excel_bytes' not in st.session_state:
    st.session_state.generated_excel_bytes = None
if 'generated_transparency_doc_bytes' not in st.session_state: # New state for Word doc
    st.session_state.generated_transparency_doc_bytes = None
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
    st.header("1. Company Context")
    client_url_input = st.text_input("Client's Website URL", placeholder="https://www.example.com")
    additional_context_file = st.file_uploader("Upload Additional Company Context (PDF or PPTX)", type=["pdf", "pptx"], key="additional_context")
    lead_magnet_file = st.file_uploader("Upload Lead Magnet (PDF)", type=["pdf"], key="lead_magnet")

with col2:
    st.header("2. Campaign Options")
    lead_objective_options = ["Demo Booking", "Sales Meeting"]
    lead_objective_input = st.selectbox("Lead Objective", lead_objective_options, key="lead_obj")

    learn_more_link_input = st.text_input("Link to 'Learn More' Page", placeholder="https://www.example.com/about-us", key="learn_more")
    lead_magnet_download_link_input = st.text_input("Link to Lead Magnet Download", placeholder="https://www.example.com/download/ebook.pdf", key="lead_magnet_dl")

    if lead_objective_input == "Demo Booking":
        objective_link_label = "Link to Demo Booking Page"
        objective_link_placeholder = "https://www.example.com/book-demo"
    else: # Sales Meeting
        objective_link_label = "Link to Sales Meeting Booking Page"
        objective_link_placeholder = "https://www.example.com/schedule-meeting"
    objective_specific_link_input = st.text_input(objective_link_label, placeholder=objective_link_placeholder, key="obj_link")

    content_count_input = st.slider("Ad Variations per Type/Funnel Stage", 1, 10, 3, key="content_count")

# --- Generate Button & Progress ---
st.header("3. Generate Content")

if st.button("✨ Generate Ad Content & Reports", type="primary", use_container_width=True):
    # Reset previous generation
    st.session_state.generated_excel_bytes = None
    st.session_state.generated_transparency_doc_bytes = None

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
    # Not strictly required, so no valid_inputs = False
    
    lead_magnet_download_link = utils.validate_and_format_url(lead_magnet_download_link_input)
    # Not strictly required

    objective_specific_link = utils.validate_and_format_url(objective_specific_link_input)
    # Not strictly required

    if not valid_inputs:
        st.stop()

    st.session_state.company_name_for_file = utils.extract_company_name_from_url(client_url)
    st.session_state.lead_objective_for_file = utils.sanitize_for_filename(lead_objective_input)

    progress_bar = st.progress(0, text="Initializing...")

    # --- 1. Context Extraction & Summarization (Individual) ---
    website_text, website_summary = None, None
    additional_text, additional_summary = None, None
    lead_magnet_text, lead_magnet_summary = None, None
    
    extraction_progress_step = 5 # Progress per extraction/summarization pair

    with st.spinner("Extracting and summarizing website content..."):
        progress_bar.progress(extraction_progress_step * 0, text="Extracting website content...")
        website_text = data_extraction.extract_text_from_url(client_url)
        if website_text:
            progress_bar.progress(extraction_progress_step * 1, text="Summarizing website content...")
            website_summary = ai_processing.summarize_text(website_text, client)
            st.success("Website content processed.")
        else:
            st.warning("Could not extract text from website URL.")
    
    if additional_context_file:
        with st.spinner("Extracting and summarizing additional context file..."):
            progress_bar.progress(extraction_progress_step * 2, text="Extracting additional context...")
            additional_text = data_extraction.extract_text_from_file(additional_context_file)
            if additional_text:
                progress_bar.progress(extraction_progress_step * 3, text="Summarizing additional context...")
                additional_summary = ai_processing.summarize_text(additional_text, client)
                st.success("Additional context file processed.")
            else:
                st.warning("Could not extract text from additional context file.")

    if lead_magnet_file:
        with st.spinner("Extracting and summarizing lead magnet file..."):
            progress_bar.progress(extraction_progress_step * 4, text="Extracting lead magnet content...")
            lead_magnet_text = data_extraction.extract_text_from_file(lead_magnet_file)
            if lead_magnet_text:
                progress_bar.progress(extraction_progress_step * 5, text="Summarizing lead magnet content...")
                lead_magnet_summary = ai_processing.summarize_text(lead_magnet_text, client)
                st.success("Lead magnet file processed.")
            else:
                st.warning("Could not extract text from lead magnet file.")

    if not (website_summary or additional_summary or lead_magnet_summary):
        st.error("No context could be summarized. Please provide valid inputs.")
        progress_bar.progress(100, text="Failed: No context.")
        st.stop()

    # --- Create Transparency Document ---
    current_progress = extraction_progress_step * 6
    progress_bar.progress(current_progress, text="Generating transparency document...")
    with st.spinner("Generating transparency Word document..."):
        st.session_state.generated_transparency_doc_bytes = document_processing.create_transparency_document(
            client_url,
            website_text, website_summary,
            additional_text, additional_summary,
            lead_magnet_text, lead_magnet_summary
        )
        st.info("Transparency document generated.")
    
    # --- Define Context Strings for AI Prompts ---
    # General context (URL + Additional)
    general_context_parts = []
    if website_summary:
        general_context_parts.append(f"Company Website Summary:\n{website_summary}")
    if additional_summary:
        general_context_parts.append(f"Additional Company Context Summary:\n{additional_summary}")
    
    context_for_general_ads = "\n\n---\n\n".join(general_context_parts) if general_context_parts else "No general company context available."

    # Demand Gen context (URL + Additional + Lead Magnet)
    demand_gen_context_parts = []
    if website_summary:
        demand_gen_context_parts.append(f"Company Website Summary:\n{website_summary}")
    if additional_summary:
        demand_gen_context_parts.append(f"Additional Company Context Summary:\n{additional_summary}")
    if lead_magnet_summary:
        demand_gen_context_parts.append(f"Lead Magnet Summary (Primary Focus for this Ad):\n{lead_magnet_summary}")
    else: # If no lead magnet summary, DG ads might not be effective, but we can try with general context
        demand_gen_context_parts.append("NOTE: Lead magnet summary is missing. Ad copy will be based on general company context.")

    context_for_demand_gen_ads = "\n\n---\n\n".join(demand_gen_context_parts) if demand_gen_context_parts else "No context available for Demand Gen ads."


    # --- 2. Generate Ad Content ---
    all_ad_content_json = {}
    # total_tasks for generation part (excluding context extraction and doc gen)
    generation_tasks_total = 8 # Email, 3x LinkedIn, 3x Facebook, Google Search, Google Display
    generation_tasks_completed = 0 # <<< Defined here
    
    # Base progress after context extraction and doc gen (e.g., 35%)
    base_progress_for_generation = current_progress 
    # Remaining progress for generation (e.g., 60%)
    remaining_progress_total = 95 - base_progress_for_generation 


    def update_generation_progress(task_name):
        # nonlocal generation_tasks_completed # <<< REMOVE THIS LINE
        global generation_tasks_completed # <<< USE THIS INSTEAD
        generation_tasks_completed += 1
        progress_value = base_progress_for_generation + int((generation_tasks_completed / generation_tasks_total) * remaining_progress_total)
        progress_value = min(progress_value, 95) # Cap before final Excel step
        progress_bar.progress(progress_value, text=f"Generating {task_name}...")

    with st.spinner("Generating Email Content..."):
        email_prompt = email_prompts.get_email_prompt(
            context_for_general_ads, 
            lead_objective_input, 
            objective_specific_link or client_url, 
            content_count_input
        )
        all_ad_content_json["Email"] = ai_processing.generate_json_content(client, email_prompt, "Email Ads")
        update_generation_progress("Email Ads")

    # LinkedIn Ads
    linkedin_stages = {
        "BA": ("Brand Awareness", learn_more_link or client_url, "Learn More", context_for_general_ads),
        "DG": ("Demand Gen", lead_magnet_download_link or client_url, "Download", context_for_demand_gen_ads),
        "DC": ("Demand Capture", objective_specific_link or client_url, "Register, Request Demo", context_for_general_ads)
    }
    for key, (stage_name, link, cta, stage_context) in linkedin_stages.items():
        with st.spinner(f"Generating LinkedIn {stage_name} Ads..."):
            if not link and (key == "DG" or key == "DC"): # Ensure critical links are present
                st.warning(f"Skipping LinkedIn {stage_name} as required link is missing.")
                update_generation_progress(f"LinkedIn {stage_name} Ads (Skipped)")
                time.sleep(0.1)
                continue
            prompt = linkedin_prompts.get_linkedin_prompt(stage_context, stage_name, link, cta, content_count_input, lead_objective_input)
            all_ad_content_json[f"LinkedIn_{key}"] = ai_processing.generate_json_content(client, prompt, f"LinkedIn {stage_name} Ads")
            update_generation_progress(f"LinkedIn {stage_name} Ads")
            time.sleep(0.5) 

    # Facebook Ads
    facebook_stages = {
        "BA": ("Brand Awareness", learn_more_link or client_url, "Learn More", context_for_general_ads),
        "DG": ("Demand Gen", lead_magnet_download_link or client_url, "Download", context_for_demand_gen_ads),
        "DC": ("Demand Capture", objective_specific_link or client_url, "Book Now", context_for_general_ads)
    }
    for key, (stage_name, link, cta, stage_context) in facebook_stages.items():
        with st.spinner(f"Generating Facebook {stage_name} Ads..."):
            if not link and (key == "DG" or key == "DC"):
                st.warning(f"Skipping Facebook {stage_name} as required link is missing.")
                update_generation_progress(f"Facebook {stage_name} Ads (Skipped)")
                time.sleep(0.1)
                continue
            prompt = facebook_prompts.get_facebook_prompt(stage_context, stage_name, link, cta, content_count_input, lead_objective_input)
            all_ad_content_json[f"Facebook_{key}"] = ai_processing.generate_json_content(client, prompt, f"Facebook {stage_name} Ads")
            update_generation_progress(f"Facebook {stage_name} Ads")
            time.sleep(0.5)

    with st.spinner("Generating Google Search Ad Components..."):
        gsearch_prompt = google_search_prompts.get_google_search_prompt(context_for_general_ads)
        all_ad_content_json["GoogleSearch"] = ai_processing.generate_json_content(client, gsearch_prompt, "Google Search Ads")
        update_generation_progress("Google Search Ads")
        time.sleep(0.5)

    with st.spinner("Generating Google Display Ad Components..."):
        gdisplay_prompt = google_display_prompts.get_google_display_prompt(context_for_general_ads)
        all_ad_content_json["GoogleDisplay"] = ai_processing.generate_json_content(client, gdisplay_prompt, "Google Display Ads")
        update_generation_progress("Google Display Ads")
    
    # --- 3. Create Excel Report ---
    progress_bar.progress(95, text="Formatting Excel report...")
    with st.spinner("Creating Excel report..."):
        valid_ad_content = {k: v for k, v in all_ad_content_json.items() if v is not None}
        if not valid_ad_content:
            st.error("No ad content was successfully generated. Cannot create Excel report.")
            progress_bar.progress(100, text="Failed: No ad content for Excel.")
            st.stop()
            
        excel_bytes = excel_processing.create_excel_report(
            valid_ad_content, 
            st.session_state.company_name_for_file, 
            lead_objective_input
        )
        st.session_state.generated_excel_bytes = excel_bytes
    
    progress_bar.progress(100, text="All reports generated!")
    st.success("🎉 Ad content & transparency reports generated and ready for download!")

# --- Download Buttons ---
if st.session_state.generated_transparency_doc_bytes:
    doc_file_name = f"{st.session_state.company_name_for_file}_context_transparency_report.docx"
    st.download_button(
        label="📄 Download Transparency Report (DOCX)",
        data=st.session_state.generated_transparency_doc_bytes,
        file_name=doc_file_name,
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        use_container_width=True,
        key="download_docx"
    )

if st.session_state.generated_excel_bytes:
    excel_file_name = f"{st.session_state.company_name_for_file}_{st.session_state.lead_objective_for_file}_ads.xlsx"
    st.download_button(
        label="📊 Download Ad Content (XLSX)",
        data=st.session_state.generated_excel_bytes,
        file_name=excel_file_name,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
        key="download_xlsx"
    )

st.markdown("---")
st.markdown("Made by M. Version 0.9")