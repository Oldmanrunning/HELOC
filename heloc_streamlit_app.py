import streamlit as st

def fmt_usd(x: float) -> str:
    return f"${x:,.2f}"

def amortize(principal: float, apr: float, years: int):
    n = int(years * 12)
    if n <= 0:
        return 0.0, 0.0, 0.0
    if apr == 0:
        monthly = principal / n
        total_paid = monthly * n
        return monthly, total_paid, total_paid - principal
    r = apr / 12.0
    factor = (1 + r) ** n
    monthly = principal * (r * factor) / (factor - 1)
    total_paid = monthly * n
    return monthly, total_paid, total_paid - principal

st.sidebar.header("Inputs")
APR_pct = st.sidebar.number_input("HELOC APR (%)", min_value=0.0, value=8.5, step=0.01)
Borrowed = st.sidebar.number_input("Borrowed (USD)", min_value=0.0, value=50000.0, step=100.0, format="%.2f")
Application_fee = st.sidebar.number_input("Application Fee (USD)", min_value=0.0, value=0.0, step=10.0, format="%.2f")
Annual_fee = st.sidebar.number_input("Annual Fee (USD)", min_value=0.0, value=0.0, step=10.0, format="%.2f")
Closing_costs = st.sidebar.number_input("Closing Costs (USD)", min_value=0.0, value=0.0, step=10.0, format="%.2f")
Appraisal_fee = st.sidebar.number_input("Appraisal Fee (USD)", min_value=0.0, value=0.0, step=10.0, format="%.2f")
Origination_fee = st.sidebar.number_input("Origination Fee (USD)", min_value=0.0, value=0.0, step=10.0, format="%.2f")
Home_value = st.sidebar.number_input("Home Value (USD)", min_value=0.0, value=400000.0, step=1000.0, format="%.2f")
Existing_loan = st.sidebar.number_input("Existing Loan (USD)", min_value=0.0, value=200000.0, step=1000.0, format="%.2f")
Period_years = st.sidebar.number_input("Payment Period (years)", min_value=1, value=10, step=1)
APR_alt_pct = st.sidebar.number_input("Alternative APR (%)", min_value=0.0, value=28.0, step=0.1)

APR = APR_pct / 100.0
APR_alt = APR_alt_pct / 100.0
Estimated_loan = Borrowed + Existing_loan
LTV = (Estimated_loan / Home_value) if Home_value else 0.0
m, tot, intr = amortize(Borrowed, APR, Period_years)
m_alt, tot_alt, intr_alt = amortize(Borrowed, APR_alt, Period_years)

md = f"""
---
#### *Estimated annual percentage rate of the HELOC*
- **APR**: {APR:.2%}  

#### *Amount of HELOC funds you plan to borrow*
- **Borrowed**: {fmt_usd(Borrowed)}  

#### *Upfront fee for submitting your HELOC application*
- **Application Fee**: {fmt_usd(Application_fee)}  

#### *Yearly fee charged for maintaining the HELOC.*  
- **Annual Fee**: {fmt_usd(Annual_fee)}  

#### *Total costs due at closing (e.g., attorney, title, etc.).*
- **Closing Costs**: {fmt_usd(Closing_costs)}  

#### *Cost for the home valuation appraisal.*
- **Appraisal Fee**: {fmt_usd(Appraisal_fee)}  

#### *Fee charged by lender to process the loan.*
- **Origination Fee**: {fmt_usd(Origination_fee)}  

#### *Estimated current market value of your home.*
- **Home Value**: {fmt_usd(Home_value)}  

#### *Outstanding loan balance before taking the HELOC.*
- **Existing Loan**: {fmt_usd(Existing_loan)}  

#### *Number of years over which you plan to repay the combined loan.*
- **Payment Period**: {Period_years} years

---
## Calculations

#### *Sum of borrowed HELOC funds and existing loan balance.*
- **Estimated Loan Amount**: {fmt_usd(Estimated_loan)}  

#### *(Estimated Loan / Home Value) to assess borrowing relative to collateral.*
- **Loan-to-Value Ratio (LTV)**: {LTV:.2%}  

---
## Amortization of Borrowed Amount
- **Monthly Payment**: {fmt_usd(m)} per month over {Period_years} years

#### *Total of all payments (principal + interest).*
- **Total Paid**: {fmt_usd(tot)}  

####  *Total interest cost over the life of the loan.*
- **Total Interest**: {fmt_usd(intr)}  

---
## Alternative APR:  {APR_alt_pct:g}

## Amortization at Alternative APR
- **Alternative APR**: {APR_alt:.1%}


- **Monthly Payment ({APR_alt:.1%} APR)**: {fmt_usd(m_alt)}    *per month for {Period_years} years*


- **Total Paid ({APR_alt:.1%} APR)**: {fmt_usd(tot_alt)}
 
- **Total Interest ({APR_alt:.1%} APR)**: {fmt_usd(intr_alt)}
"""

st.title("HELOC Calculator")
st.caption("Simple HELOC amortization with alternative APR comparison")
st.markdown(md)


