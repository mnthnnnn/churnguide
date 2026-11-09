"""
Synthetic B2B SaaS Customer Churn Dataset Generator
Purpose: Provides a non-telecom business fixture to test cross-domain schema flexibility
and software plumbing.
Label: SYNTHETIC B2B SaaS Subscription Fixture (not real enterprise validation).
"""

import numpy as np
import pandas as pd
import os

def generate_saas_dataset(num_rows=1200, seed=42):
    np.random.seed(seed)
    
    account_ids = [f"ACC-{1000 + i}" for i in range(num_rows)]
    
    plan_tiers = np.random.choice(["Starter", "Professional", "Enterprise"], size=num_rows, p=[0.40, 0.42, 0.18])
    company_sizes = np.random.choice(["1-10", "11-50", "51-200", "201-1000", "1000+"], size=num_rows, p=[0.25, 0.35, 0.22, 0.12, 0.06])
    billing_cycles = np.random.choice(["Monthly", "Annual"], size=num_rows, p=[0.58, 0.42])
    payment_methods = np.random.choice(["Credit Card", "Direct Debit", "Invoice"], size=num_rows, p=[0.55, 0.25, 0.20])
    auto_renews = np.random.choice(["Yes", "No"], size=num_rows, p=[0.72, 0.28])
    
    contract_age_months = np.random.exponential(scale=14.0, size=num_rows).astype(int) + 1
    contract_age_months = np.clip(contract_age_months, 1, 60)
    
    # Licenses depend partially on tier
    base_licenses = {"Starter": 5, "Professional": 25, "Enterprise": 120}
    user_licenses = [int(np.random.normal(loc=base_licenses[t], scale=base_licenses[t] * 0.3)) for t in plan_tiers]
    user_licenses = [max(2, l) for l in user_licenses]
    
    # Monthly spend depends on plan tier and licenses
    tier_base_spend = {"Starter": 79.0, "Professional": 299.0, "Enterprise": 1299.0}
    monthly_spend = [round(tier_base_spend[t] + l * np.random.uniform(8.0, 15.0), 2) for t, l in zip(plan_tiers, user_licenses)]
    
    # Weekly active users as a fraction of licenses
    activity_ratio = np.random.beta(a=4, b=2, size=num_rows)
    weekly_active_users = [max(1, int(l * r)) for l, r in zip(user_licenses, activity_ratio)]
    
    # Feature adoption score (0-100)
    adoption_score = np.random.normal(loc=65.0, scale=18.0, size=num_rows)
    adoption_score = np.clip(np.round(adoption_score, 1), 5.0, 99.5)
    
    # Support tickets in last 90 days
    support_tickets = np.random.poisson(lam=3.5, size=num_rows)
    support_tickets = np.clip(support_tickets, 0, 25)
    
    # Calculate latent log-odds of churn
    # Risk factors: monthly billing, low contract age, low adoption, high tickets, no auto renew
    log_odds = -1.2
    for i in range(num_rows):
        lo = log_odds
        if billing_cycles[i] == "Monthly":
            lo += 0.85
        if auto_renews[i] == "No":
            lo += 0.65
        if contract_age_months[i] < 6:
            lo += 0.75
        elif contract_age_months[i] > 24:
            lo -= 0.80
        if adoption_score[i] < 45.0:
            lo += 0.90
        elif adoption_score[i] > 80.0:
            lo -= 0.70
        if support_tickets[i] > 6:
            lo += 0.80
        elif support_tickets[i] == 0:
            lo += 0.25 # disengaged users also churn
            
        prob = 1.0 / (1.0 + np.exp(-lo))
        # Random outcome based on probability
        is_churn = np.random.rand() < prob
        status = "Churned" if is_churn else "Active"
        yield_status = status
        
    # Re-generate cleanly as list
    statuses = []
    for i in range(num_rows):
        lo = log_odds
        if billing_cycles[i] == "Monthly":
            lo += 0.85
        if auto_renews[i] == "No":
            lo += 0.65
        if contract_age_months[i] < 6:
            lo += 0.75
        elif contract_age_months[i] > 24:
            lo -= 0.80
        if adoption_score[i] < 45.0:
            lo += 0.90
        elif adoption_score[i] > 80.0:
            lo -= 0.70
        if support_tickets[i] > 6:
            lo += 0.80
        elif support_tickets[i] == 0:
            lo += 0.25
            
        prob = 1.0 / (1.0 + np.exp(-lo))
        statuses.append("Churned" if np.random.rand() < prob else "Active")
        
    df = pd.DataFrame({
        "Account_ID": account_ids,
        "Plan_Tier": plan_tiers,
        "Company_Size": company_sizes,
        "Billing_Cycle": billing_cycles,
        "Payment_Method": payment_methods,
        "Auto_Renew": auto_renews,
        "Contract_Age_Months": contract_age_months,
        "User_Licenses": user_licenses,
        "Monthly_Spend": monthly_spend,
        "Weekly_Active_Users": weekly_active_users,
        "Support_Tickets_90d": support_tickets,
        "Feature_Adoption_Score": adoption_score,
        "Status": statuses
    })
    
    return df

if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    df = generate_saas_dataset(1200, seed=42)
    output_path = os.path.join("data", "saas_customer_churn.csv")
    df.to_csv(output_path, index=False)
    print(f"Generated {len(df)} rows in {output_path}")
    print("Class distribution:")
    print(df["Status"].value_counts(normalize=True))
    
    # Also generate unlabeled scoring sample (200 rows without Status column)
    scoring_df = df.drop(columns=["Status"]).sample(200, random_state=123).copy()
    scoring_path = os.path.join("data", "saas_scoring_unlabeled.csv")
    scoring_df.to_csv(scoring_path, index=False)
    print(f"Generated 200 unlabeled rows in {scoring_path}")

