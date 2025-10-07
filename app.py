import streamlit as st
import json
import pandas as pd
import altair as alt

from voice_assistant import voice_assistant_ui
from tax_engine import compute_total_tax_liability
from smart_tips import (
    get_smart_tips, display_tips,
    get_tax_payment_guidance, get_document_checklist,
    get_upcoming_deadlines
)
from visualization import display_visualizations, offer_pdf_download
from indian_formatter import format_indian_currency, format_indian_number


# ---------------- Helper Function ---------------- #
def format_value_display(value):
    if value > 0:
        return f"{format_indian_currency(value)}"
    return "Not entered"


# ---------------- Page Configuration ---------------- #
st.set_page_config(
    page_title="Income Tax Assistant",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------- Custom CSS ---------------- #
st.markdown("""
<style>
.main {
    background-color: #f5f5f5;
}
.elegant-title h2 {
    font-size: 2.5em;
    color: #2c3e50;
    font-family: 'Georgia', serif;
    text-align: center;
    margin-bottom: 0.5em;
    letter-spacing: 1px;
}
.personal-header h2, .voice-header h2 {
    font-family: 'Georgia', serif;
    color: #2c3e50;
    font-size: 1.8em;
    letter-spacing: 0.5px;
}
.stSidebar {
    background: rgba(255, 255, 255, 0.25);
    backdrop-filter: blur(15px);
    border: 1px solid rgba(255, 255, 255, 0.18);
    box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
}
</style>
""", unsafe_allow_html=True)


# ---------------- Page Header ---------------- #
st.markdown("""
<div class="elegant-title">
    <h2>Income Tax Assistant</h2>
</div>
""", unsafe_allow_html=True)


# ---------------- Sidebar Voice Assistant ---------------- #
with st.sidebar:
    st.markdown("""
    <div style="
        background: rgba(255, 255, 255, 0.25);
        backdrop-filter: blur(15px);
        border-radius: 15px;
        border: 1px solid rgba(255, 255, 255, 0.18);
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
        padding: 20px;
        margin-bottom: 20px;
        ">
        <h2 style="
            font-family: 'Georgia', serif;
            color: #2c3e50;
            text-align: center;
            letter-spacing: 0.5px;
            ">🎙 Voice Assistant</h2>
    </div>
    """, unsafe_allow_html=True)

    # Render voice assistant
    voice_assistant_ui()


# ---------------- Session State ---------------- #
if 'form_submitted' not in st.session_state:
    st.session_state.form_submitted = False


# ---------------- Personal Info Form ---------------- #
with st.form(key='personal_info'):
    st.markdown("""
    <div class="personal-header">
        <h2>Personal Information</h2>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1])
    with col1:
        age_group = st.selectbox("Select Age Group", ["Below 60", "60 and above", "80 and above"])
        residential_status = st.radio(
            "Residential Status", ["Resident", "Non-Resident"],
            horizontal=True, help="Are you living in India?"
        )
    with col2:
        fy_ay = st.selectbox(
            "Financial Year / Assessment Year",
            ["FY 2025-26 / AY 2026-27"], index=0,
            help="Choose the applicable financial year"
        )
        employment_type = st.selectbox(
            "Employment Type",
            ["Salaried", "Freelancer", "Business", "Rental", "Investor", "Mixed"],
            help="Select your source of income"
        )

    col1, col2 = st.columns([2, 1])
    with col1:
        submit_info = st.form_submit_button(label='Submit Profile', use_container_width=True)

    if submit_info:
        st.session_state.form_submitted = True
        st.session_state.age_group = age_group
        st.session_state.residential_status = residential_status
        st.session_state.fy_ay = fy_ay
        st.session_state.employment_type = employment_type


# ---------------- Main Tabs ---------------- #
if st.session_state.form_submitted:
    tab_profile, tab_income, tab_taxation, tab_reports, tab_guidance = st.tabs(
        ["Profile", "Income Details", "Tax Calculation", "Reports & Visualization", "Guidance"]
    )

    # ----- Profile Tab ----- #
    with tab_profile:
        st.success("Profile information saved!")
        st.write(f"**Age Group:** {st.session_state.age_group}")
        st.write(f"**Residential Status:** {st.session_state.residential_status}")
        st.write(f"**Financial Year:** {st.session_state.fy_ay}")
        st.write(f"**Employment Type:** {st.session_state.employment_type}")

    # ----- Income Details Tab ----- #
    with tab_income:
        # Initialize defaults
        basic_salary = hra = pf = bonus = rent_paid = employer_nps = 0
        property_details = ""
        rent_received = municipal_tax = interest_paid = 0
        net_profit = expenses = 0
        presumptive_eligibility = False
        stcg = ltcg = dividends = interest_income = 0
        tds_paid = advance_tax_paid = 0

        etype = st.session_state.employment_type

        if etype == "Salaried":
            st.subheader("Income Details: Salaried")
            col1, col2 = st.columns(2)
            with col1:
                basic_salary = st.number_input("Basic Salary", min_value=0, value=0)
                pf = st.number_input("Provident Fund Contribution", min_value=0, value=0)
                bonus = st.number_input("Bonus", min_value=0, value=0)
            with col2:
                hra = st.number_input("HRA", min_value=0, value=0)
                rent_paid = st.number_input("Rent Paid", min_value=0, value=0)
                employer_nps = st.number_input("Employer NPS Contribution", min_value=0, value=0)

        elif etype == "Rental":
            st.subheader("Income Details: Rental")
            col1, col2 = st.columns(2)
            with col1:
                property_details = st.text_input("Property Details")
                rent_received = st.number_input("Rent Received", min_value=0, value=0)
            with col2:
                municipal_tax = st.number_input("Municipal Tax Paid", min_value=0, value=0)
                interest_paid = st.number_input("Interest Paid on Home Loan", min_value=0, value=0)

        elif etype in ["Freelancer", "Business"]:
            st.subheader("Income Details: Freelance / Business")
            net_profit = st.number_input("Net Profit", min_value=0, value=0)
            expenses = st.number_input("Expenses", min_value=0, value=0)
            presumptive_eligibility = st.checkbox("Eligible for Presumptive Taxation Scheme")

        elif etype == "Investor":
            st.subheader("Income Details: Investor")
            col1, col2 = st.columns(2)
            with col1:
                stcg = st.number_input("Short Term Capital Gains (STCG)", min_value=0, value=0)
                ltcg = st.number_input("Long Term Capital Gains (LTCG)", min_value=0, value=0)
            with col2:
                dividends = st.number_input("Dividends", min_value=0, value=0)
                interest_income = st.number_input("Interest Income", min_value=0, value=0)

        with st.expander("Optional Fields"):
            tds_paid = st.number_input("TDS Paid", min_value=0, value=0)
            advance_tax_paid = st.number_input("Advance Tax Paid", min_value=0, value=0)

        st.session_state.income_details = {
            "basic_salary": basic_salary,
            "hra": hra,
            "pf": pf,
            "bonus": bonus,
            "rent_paid": rent_paid,
            "employer_nps": employer_nps,
            "rent_received": rent_received,
            "municipal_tax": municipal_tax,
            "interest_paid": interest_paid,
            "net_profit": net_profit,
            "expenses": expenses,
            "stcg": stcg,
            "ltcg": ltcg,
            "dividends": dividends,
            "interest_income": interest_income,
            "tds_paid": tds_paid,
            "advance_tax_paid": advance_tax_paid
        }

    # ----- Taxation Tab ----- #
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

    # ----- Reports Tab ----- #
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

    # ----- Guidance Tab ----- #
    with tab_guidance:
        st.header("Guidance")
        get_tax_payment_guidance()

        st.header("Checklist")
        if 'employment_type' in st.session_state:
            get_document_checklist(st.session_state.employment_type)

        st.header("Important Deadlines")
        get_upcoming_deadlines()
else:
    st.info("Please submit your profile information to continue.")
