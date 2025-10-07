import streamlit as st
import json
import pandas as pd
import altair as alt

# Import additional components
from tax_engine import compute_total_tax_liability
from smart_tips import get_smart_tips, display_tips, get_tax_payment_guidance, get_document_checklist, get_upcoming_deadlines
from visualization import display_visualizations, offer_pdf_download
from indian_formatter import format_indian_currency, format_indian_number

# Helper function to format values for display
def format_value_display(value):
    if value > 0:
        return f"{format_indian_currency(value)}"
    return "Not entered"

# Improved layout
st.set_page_config(
    page_title="Tax Assistant",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS styles for background and marquee
st.markdown("""
<style>
.main {
    background-color: #BAE2BE;
}

@keyframes marquee {
    0% { transform: translateX(-100%); }
    100% { transform: translateX(100%); }
}
.marquee {
    display: inline-block;
    white-space: nowrap;
    overflow: hidden;
    font-size: 2.5em;
    font-weight: bold;
    color: #1E90FF;  /* Blue color */
    animation: marquee 10s linear infinite;
    text-align: center;
    width: 100%;
}
</style>
<div class="marquee">Tax Assistant 💵</div>
""", unsafe_allow_html=True)

# Initialize session state for form data
if 'form_submitted' not in st.session_state:
    st.session_state.form_submitted = False

# Form for personal information
with st.form(key='personal_info'):
    st.header("1. Personal Information")
    age_group = st.selectbox("Select Age Group", options=["Below 60", "60 and above", "80 and above"])
    residential_status = st.radio("Residential Status", options=["Resident", "Non-Resident"], help="Are you living in India?")
    fy_ay = st.selectbox("Financial Year / Assessment Year", options=["FY 2025-26 / AY 2026-27"], index=0, help="Choose the applicable financial year")
    employment_type = st.selectbox("Employment Type", options=["Salaried", "Freelancer", "Business", "Rental", "Investor", "Mixed"], help="Select your source of income")
    
    submit_info = st.form_submit_button(label='Submit Profile')
    
    if submit_info:
        st.session_state.form_submitted = True
        st.session_state.age_group = age_group
        st.session_state.residential_status = residential_status
        st.session_state.fy_ay = fy_ay
        st.session_state.employment_type = employment_type

# Added navigation
if st.session_state.form_submitted:
    tab_profile, tab_income, tab_taxation, tab_reports, tab_guidance = st.tabs(["Profile", "Income Details", "Tax Calculation", "Reports & Visualization", "Guidance"])

    with tab_profile:
        st.success("Profile information saved!")
        st.write(f"**Age Group:** {st.session_state.age_group}")
        st.write(f"**Residential Status:** {st.session_state.residential_status}")
        st.write(f"**Financial Year:** {st.session_state.fy_ay}")
        st.write(f"**Employment Type:** {st.session_state.employment_type}")

    with tab_income:
        # Income input handling (same as your original code)
        # ... (keep all your income input code here) ...

    with tab_taxation:
        if 'income_details' in st.session_state:
            if st.button("Calculate Tax", type="primary"):
                with st.spinner("Calculating tax..."):
                    try:
                        tax_result = compute_total_tax_liability(
                            st.session_state.income_details, 
                            st.session_state.fy_ay, 
                            st.session_state.employment_type
                        )
                        tips = get_smart_tips(
                            st.session_state.income_details, 
                            tax_result, 
                            st.session_state.fy_ay, 
                            st.session_state.employment_type
                        )
                        
                        st.session_state.tax_result = tax_result
                        st.session_state.tips = tips
                        
                        st.success("Tax calculation complete!")
                        
                        # Display results
                        display_visualizations(
                            st.session_state.income_details, 
                            tax_result, 
                            st.session_state.employment_type, 
                            st.session_state.fy_ay
                        )
                        display_tips(tips)
                        
                    except Exception as e:
                        st.error(f"Error in tax calculation: {str(e)}")
        else:
            st.info("Please enter your income details first.")

    with tab_reports:
        if 'tax_result' in st.session_state and 'tips' in st.session_state:
            offer_pdf_download(
                st.session_state.income_details, 
                st.session_state.tax_result, 
                st.session_state.tips, 
                st.session_state.employment_type, 
                st.session_state.fy_ay
            )
        else:
            st.info("Please calculate tax first to generate reports.")
            
    with tab_guidance:
        st.header("Tax Payment & Filing Guidance")
        get_tax_payment_guidance()
        
        st.header("Document Checklist")
        if 'employment_type' in st.session_state:
            get_document_checklist(st.session_state.employment_type)
        
        st.header("Important Deadlines")
        get_upcoming_deadlines()
        
else:
    st.info("Please submit your profile information to continue.")
