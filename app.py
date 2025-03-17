import streamlit as st
import pandas as pd

st.set_page_config(page_title="Analyst Cross-Reference Tool", layout="wide")

st.title("Analyst Cross-Reference Tool")


try:
    # Load the Excel file
    df = pd.read_excel('data/coverage_analysts.xlsx')
    
    # Clean up data - standardize company names
    df['company'] = df['company'].str.strip()
    
    # Get unique companies for dropdowns
    companies = sorted(df['company'].unique())
    
    # Create two columns for the dropdowns
    col1, col2 = st.columns(2)
    
    with col1:
        # First company dropdown
        company1 = st.selectbox(
            "Select first company:",
            companies,
            key="company1"
        )
    
    with col2:
        # Second company dropdown
        company2 = st.selectbox(
            "Select second company:",
            companies,
            key="company2"
        )
    
    # Find analysts for each company
    company1_analysts = df[df['company'] == company1]
    company2_analysts = df[df['company'] == company2]
    
    # Extract just the analyst names and their firms
    company1_analysts_info = company1_analysts[['analyst', 'firm']].copy()
    company2_analysts_info = company2_analysts[['analyst', 'firm']].copy()
    
    # Find overlapping analysts by name
    company1_analyst_names = set(company1_analysts['analyst'])
    company2_analyst_names = set(company2_analysts['analyst'])
    
    overlapping_analyst_names = company1_analyst_names.intersection(company2_analyst_names)
    
    # Display results
    st.header("Results")
    
    if overlapping_analyst_names:
        st.success(f"Found {len(overlapping_analyst_names)} analyst(s) covering both companies")
        
        # Create a dataframe of the overlapping analysts with their firms for each company
        results = []
        
        for analyst in overlapping_analyst_names:
            # Get firm for first company
            firm1 = company1_analysts[company1_analysts['analyst'] == analyst]['firm'].iloc[0]
            
            # Get firm for second company
            firm2 = company2_analysts[company2_analysts['analyst'] == analyst]['firm'].iloc[0]
            
            results.append({
                'Analyst': analyst,
                f'Firm ({company1})': firm1,
                f'Firm ({company2})': firm2
            })
        
        # Create a dataframe from the results and display it
        results_df = pd.DataFrame(results)
        st.dataframe(results_df)
        
    else:
        st.warning(f"No common analysts found between {company1} and {company2}")
    
    # Optional: Show all analysts for each company
    with st.expander("View all analysts for each company"):
        st.subheader(f"Analysts covering {company1}")
        st.dataframe(company1_analysts_info.sort_values('firm'))
        
        st.subheader(f"Analysts covering {company2}")
        st.dataframe(company2_analysts_info.sort_values('firm'))
        
except Exception as e:
    st.error(f"Error processing file: {e}")
