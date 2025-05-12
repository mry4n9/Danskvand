import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl.utils import get_column_letter
import io

def apply_header_style(cell):
    cell.font = Font(color="FFFFFF", bold=True)
    cell.fill = PatternFill(start_color="000000", end_color="000000", fill_type="solid")
    cell.alignment = Alignment(horizontal="center", vertical="center")
    cell.border = Border(left=Side(style='thin'), right=Side(style='thin'), top=Side(style='thin'), bottom=Side(style='thin'))

def apply_content_style(cell):
    cell.alignment = Alignment(vertical="center", wrap_text=True) # Changed to top for better readability with wrapped text
    cell.border = Border(left=Side(style='thin'), right=Side(style='thin'), top=Side(style='thin'), bottom=Side(style='thin'))

def adjust_column_width(worksheet):
    for col in worksheet.columns:
        max_length = 0
        column = col[0].column_letter # Get the column name
        for cell in col:
            try: # Necessary to avoid error on empty cells
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        adjusted_width = (max_length + 2) * 1.2
        worksheet.column_dimensions[column].width = min(adjusted_width, 50) # Max width 50

def create_excel_report(ad_data: dict, company_name: str, lead_objective: str) -> bytes:
    """
    Creates an XLSX report from the generated ad_data.
    ad_data is a dictionary where keys are like "Email", "LinkedIn_BA", "GoogleSearch"
    and values are lists of ad dicts or a single dict for Google Ads.
    """
    wb = Workbook()
    wb.remove(wb.active) # Remove default sheet

    # --- Email Sheet ---
    if "Email" in ad_data and ad_data["Email"]:
        ws_email = wb.create_sheet("Email")
        email_headers = ["Ad Name", "Funnel Stage", "Headline", "Subject Line", "Body", "CTA"]
        ws_email.append(email_headers)
        for cell in ws_email[1]: apply_header_style(cell)

        for i, ad in enumerate(ad_data["Email"].get("emails", [])):
            ad_name = f"Email_Demand Capture_Ver. {i+1}"
            row = [ad_name, "Demand Capture", ad.get("headline"), ad.get("subject_line"), ad.get("body"), ad.get("cta")]
            ws_email.append(row)
        
        for row_idx in range(2, ws_email.max_row + 1):
            for col_idx in range(1, ws_email.max_column + 1):
                apply_content_style(ws_email.cell(row=row_idx, column=col_idx))
        adjust_column_width(ws_email)

    # --- LinkedIn Sheet ---
    if any(k.startswith("LinkedIn") for k in ad_data):
        ws_linkedin = wb.create_sheet("LinkedIn")
        linkedin_headers = ["Ad Name", "Funnel Stage", "Introductory Text", "Image Copy", "Headline", "Destination", "CTA Button"]
        ws_linkedin.append(linkedin_headers)
        for cell in ws_linkedin[1]: apply_header_style(cell)
        
        row_num = 2
        for funnel_key, funnel_stage_name, ads_list_key in [
            ("LinkedIn_BA", "Brand Awareness", "linkedin_brand_awareness_ads"),
            ("LinkedIn_DG", "Demand Gen", "linkedin_demand_gen_ads"),
            ("LinkedIn_DC", "Demand Capture", "linkedin_demand_capture_ads")
        ]:
            if funnel_key in ad_data and ad_data[funnel_key]:
                for i, ad in enumerate(ad_data[funnel_key].get(ads_list_key, [])):
                    ad_name = f"LinkedIn_{funnel_stage_name.replace(' ', '')}_Ver. {i+1}"
                    row = [ad_name, funnel_stage_name, ad.get("introductory_text"), ad.get("image_copy"), 
                           ad.get("headline"), ad.get("destination_url"), ad.get("cta_button")]
                    ws_linkedin.append(row)
                    row_num +=1

        for row_idx in range(2, ws_linkedin.max_row + 1):
            for col_idx in range(1, ws_linkedin.max_column + 1):
                apply_content_style(ws_linkedin.cell(row=row_idx, column=col_idx))
        adjust_column_width(ws_linkedin)

    # --- Facebook Sheet ---
    if any(k.startswith("Facebook") for k in ad_data):
        ws_facebook = wb.create_sheet("FaceBook") # Note: 'FaceBook' as per spec
        facebook_headers = ["Ad Name", "Funnel Stage", "Primary Text", "Image Copy", "Headline", "Link Description", "Destination", "CTA Button"]
        ws_facebook.append(facebook_headers)
        for cell in ws_facebook[1]: apply_header_style(cell)

        row_num = 2
        for funnel_key, funnel_stage_name, ads_list_key in [
            ("Facebook_BA", "Brand Awareness", "facebook_brand_awareness_ads"),
            ("Facebook_DG", "Demand Gen", "facebook_demand_gen_ads"),
            ("Facebook_DC", "Demand Capture", "facebook_demand_capture_ads")
        ]:
            if funnel_key in ad_data and ad_data[funnel_key]:
                for i, ad in enumerate(ad_data[funnel_key].get(ads_list_key, [])):
                    ad_name = f"Facebook_{funnel_stage_name.replace(' ', '')}_Ver. {i+1}"
                    row = [ad_name, funnel_stage_name, ad.get("primary_text"), ad.get("image_copy"), 
                           ad.get("headline"), ad.get("link_description"), ad.get("destination_url"), ad.get("cta_button")]
                    ws_facebook.append(row)
                    row_num +=1
        
        for row_idx in range(2, ws_facebook.max_row + 1):
            for col_idx in range(1, ws_facebook.max_column + 1):
                apply_content_style(ws_facebook.cell(row=row_idx, column=col_idx))
        adjust_column_width(ws_facebook)

    # --- Google Search Sheet ---
    if "GoogleSearch" in ad_data and ad_data["GoogleSearch"]:
        ws_gsearch = wb.create_sheet("Google Search")
        gsearch_headers = ["Headline", "Description"]
        ws_gsearch.append(gsearch_headers)
        for cell in ws_gsearch[1]: apply_header_style(cell)

        headlines = ad_data["GoogleSearch"].get("headlines", [])
        descriptions = ad_data["GoogleSearch"].get("descriptions", [])
        max_rows = max(len(headlines), len(descriptions))

        for i in range(max_rows):
            headline = headlines[i] if i < len(headlines) else ""
            description = descriptions[i] if i < len(descriptions) else ""
            ws_gsearch.append([headline, description])

        for row_idx in range(2, ws_gsearch.max_row + 1):
            for col_idx in range(1, ws_gsearch.max_column + 1):
                apply_content_style(ws_gsearch.cell(row=row_idx, column=col_idx))
        adjust_column_width(ws_gsearch)

    # --- Google Display Sheet ---
    if "GoogleDisplay" in ad_data and ad_data["GoogleDisplay"]:
        ws_gdisplay = wb.create_sheet("Google Display")
        gdisplay_headers = ["Headline", "Description"]
        ws_gdisplay.append(gdisplay_headers)
        for cell in ws_gdisplay[1]: apply_header_style(cell)

        headlines = ad_data["GoogleDisplay"].get("headlines", [])
        descriptions = ad_data["GoogleDisplay"].get("descriptions", [])
        max_rows = max(len(headlines), len(descriptions))

        for i in range(max_rows):
            headline = headlines[i] if i < len(headlines) else ""
            description = descriptions[i] if i < len(descriptions) else ""
            ws_gdisplay.append([headline, description])

        for row_idx in range(2, ws_gdisplay.max_row + 1):
            for col_idx in range(1, ws_gdisplay.max_column + 1):
                apply_content_style(ws_gdisplay.cell(row=row_idx, column=col_idx))
        adjust_column_width(ws_gdisplay)

    # Save to a BytesIO object
    excel_bytes = io.BytesIO()
    wb.save(excel_bytes)
    excel_bytes.seek(0)
    return excel_bytes.getvalue()