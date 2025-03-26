import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Analyst Cross-Reference Tool", layout="wide")

st.title("Analyst Cross-Reference Tool")

try:
    # Load the Excel file
    df = pd.read_excel('coverage_analysts.xlsx')
    
    # Clean up data - standardize company names and column names
    df.columns = [col.strip().lower() for col in df.columns]
    
    # Handle NaN values in key columns
    df['company'] = df['company'].fillna('Unknown Company')
    df['company'] = df['company'].str.strip()
    df['status'] = df['status'].fillna('Unknown Status')
    df['status'] = df['status'].str.strip()
    
    # Check if 'industry' column exists (after normalization)
    if 'industry' in df.columns:
        industry_column = 'industry'
    else:
        # Try to find a column that might match 'industry'
        potential_industry_cols = [col for col in df.columns if 'industr' in col.lower()]
        
        if potential_industry_cols:
            industry_column = potential_industry_cols[0]
            st.info(f"Using '{industry_column}' as the industry column.")
        else:
            # Add the column if it doesn't exist
            df['industry'] = 'Unknown'
            industry_column = 'industry'
            st.warning("No industry column found in the data. Adding a default 'Unknown' industry.")
    
    # Handle NaN values in industry column
    df[industry_column] = df[industry_column].fillna('Unknown')
    
    # Get unique companies and industries for dropdowns
    companies = sorted(df['company'].unique())
    industries = sorted(df[industry_column].unique())
    
    # Create tabs for different analysis modes
    tab1, tab2, tab3 = st.tabs(["Compare Two Companies", "Find All Shared Analysts", "Active Customer Analysis"])
    
    with tab1:
        st.header("Compare Two Companies")
        
        # Add industry filter
        industry_filter = st.selectbox(
            "Filter by industry (optional):",
            ["All Industries"] + list(industries),
            key="industry_filter1"
        )
        
        # Filter companies by selected industry if needed
        filtered_companies = companies
        if industry_filter != "All Industries":
            industry_companies = df[df[industry_column] == industry_filter]['company'].unique()
            filtered_companies = sorted(industry_companies)
        
        # Create two columns for the dropdowns
        col1, col2 = st.columns(2)
        
        with col1:
            # First company dropdown with industry info and status
            company1 = st.selectbox(
                "Select first company:",
                filtered_companies,
                key="company1",
                format_func=lambda x: f"{x} ({df[df['company'] == x][industry_column].iloc[0]}) [{df[df['company'] == x]['status'].iloc[0]}]"
            )
        
        with col2:
            # Second company dropdown with industry info and status
            company2 = st.selectbox(
                "Select second company:",
                filtered_companies,
                key="company2",
                format_func=lambda x: f"{x} ({df[df['company'] == x][industry_column].iloc[0]}) [{df[df['company'] == x]['status'].iloc[0]}]"
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
        st.subheader("Results")
        
        if overlapping_analyst_names:
            # Display industry information for context
            industry1 = company1_analysts[industry_column].iloc[0]
            industry2 = company2_analysts[industry_column].iloc[0]
            
            st.info(f"{company1} Industry: {industry1} | {company2} Industry: {industry2}")
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
    
    with tab2:
        st.header("Find All Companies Sharing Analysts")
        
        # Add industry filter for the second tab
        industry_filter2 = st.selectbox(
            "Filter by industry (optional):",
            ["All Industries"] + list(industries),
            key="industry_filter2"
        )
        
        # Filter companies by selected industry if needed
        filtered_companies2 = companies
        if industry_filter2 != "All Industries":
            industry_companies2 = df[df[industry_column] == industry_filter2]['company'].unique()
            filtered_companies2 = sorted(industry_companies2)
        
        # Company selection for finding shared analysts
        selected_company = st.selectbox(
            "Select a company:",
            filtered_companies2,
            key="shared_company",
            format_func=lambda x: f"{x} ({df[df['company'] == x][industry_column].iloc[0]}) [{df[df['company'] == x]['status'].iloc[0]}]"
        )
        
        # Get analysts for the selected company
        selected_company_analysts = df[df['company'] == selected_company]['analyst'].unique()
        
        # Find all companies that share at least one analyst with the selected company
        companies_with_shared_analysts = []
        
        for company in companies:
            if company == selected_company:
                continue
                
            company_analysts = df[df['company'] == company]['analyst'].unique()
            shared_analysts = set(selected_company_analysts).intersection(set(company_analysts))
            
            if shared_analysts:
                industry = df[df['company'] == company][industry_column].iloc[0]
                status = df[df['company'] == company]['status'].iloc[0]
                companies_with_shared_analysts.append({
                    'Company': company,
                    'Industry': industry,
                    'Status': status,
                    'Shared Analysts': len(shared_analysts),
                    'Analyst List': ', '.join(sorted(shared_analysts))
                })
        
        if companies_with_shared_analysts:
            # Convert to DataFrame and sort by number of shared analysts
            shared_df = pd.DataFrame(companies_with_shared_analysts)
            shared_df = shared_df.sort_values('Shared Analysts', ascending=False)
            
            st.success(f"Found {len(shared_df)} companies sharing analysts with {selected_company}")
            st.dataframe(shared_df)
            
            # Add a download button for the results
            csv = shared_df.to_csv(index=False)
            st.download_button(
                label="Download results as CSV",
                data=csv,
                file_name=f"shared_analysts_{selected_company}.csv",
                mime="text/csv"
            )
        else:
            st.warning(f"No companies found sharing analysts with {selected_company}")
    
    with tab3:
        st.header("Active Customer Analysis")
        
        # Get list of Active Customers
        active_customers = sorted(df[df['status'].str.lower() == 'active customer']['company'].unique())
        
        if not active_customers:
            st.warning("No Active Customers found in the data.")
        else:
            # Select an Active Customer
            selected_ac = st.selectbox(
                "Select an Active Customer:",
                active_customers,
                key="ac_company",
                format_func=lambda x: f"{x} ({df[df['company'] == x][industry_column].iloc[0]})"
            )
            
            # Get analysts for the selected AC
            ac_analysts = df[df['company'] == selected_ac]['analyst'].unique()
            
            # Find all prospects that share analysts with the selected AC
            prospects_with_shared_analysts = []
            
            for company in companies:
                if company == selected_ac or df[df['company'] == company]['status'].str.lower().iloc[0] == 'active customer':
                    continue
                    
                company_analysts = df[df['company'] == company]['analyst'].unique()
                shared_analysts = set(ac_analysts).intersection(set(company_analysts))
                
                if shared_analysts:
                    industry = df[df['company'] == company][industry_column].iloc[0]
                    status = df[df['company'] == company]['status'].iloc[0]
                    prospects_with_shared_analysts.append({
                        'Prospect Company': company,
                        'Industry': industry,
                        'Status': status,
                        'Shared Analysts': len(shared_analysts),
                        'Analyst List': ', '.join(sorted(shared_analysts))
                    })
            
            if prospects_with_shared_analysts:
                # Convert to DataFrame and sort by number of shared analysts
                prospects_df = pd.DataFrame(prospects_with_shared_analysts)
                prospects_df = prospects_df.sort_values('Shared Analysts', ascending=False)
                
                st.success(f"Found {len(prospects_df)} prospects sharing analysts with {selected_ac}")
                st.dataframe(prospects_df)
                
                # Add a download button for the results
                csv = prospects_df.to_csv(index=False)
                st.download_button(
                    label="Download prospects as CSV",
                    data=csv,
                    file_name=f"prospects_for_{selected_ac}.csv",
                    mime="text/csv"
                )
            else:
                st.warning(f"No prospects found sharing analysts with {selected_ac}")
    
except Exception as e:
    st.error(f"Error processing file: {e}")
    # Add more detailed error information
    import traceback
    st.error(traceback.format_exc())
