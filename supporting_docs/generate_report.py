import csv
import os
import asyncio

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(CURRENT_DIR, "generation_summary.csv")
MD_PATH = os.path.join(CURRENT_DIR, "loan_processing_report.md")
HTML_PATH = os.path.join(CURRENT_DIR, "loan_processing_report.html")

def read_data():
    stats = {
        "total": 0,
        "approved": 0,
        "rejected": 0,
        "review": 0,
        "tier1": 0,
        "tier2": 0,
        "tier3": 0,
        "total_dti": 0.0,
        "total_ltv": 0.0,
        "count_dti": 0,
        "count_ltv": 0
    }
    
    if not os.path.exists(CSV_PATH):
        raise FileNotFoundError(f"Could not find {CSV_PATH}")
        
    with open(CSV_PATH, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            stats["total"] += 1
            
            disp = row["Disposition"].upper()
            if "APPROVED" in disp:
                stats["approved"] += 1
            elif "REJECTED" in disp:
                stats["rejected"] += 1
            elif "REVIEW" in disp:
                stats["review"] += 1
                
            tier = row["Risk Tier"]
            if "Tier 1" in tier:
                stats["tier1"] += 1
            elif "Tier 2" in tier:
                stats["tier2"] += 1
            elif "Tier 3" in tier:
                stats["tier3"] += 1
                
            try:
                dti = float(row["DTI"].replace('%', ''))
                stats["total_dti"] += dti
                stats["count_dti"] += 1
            except ValueError:
                pass
                
            try:
                ltv = float(row["LTV"].replace('%', ''))
                stats["total_ltv"] += ltv
                stats["count_ltv"] += 1
            except ValueError:
                pass
                
    stats["avg_dti"] = stats["total_dti"] / stats["count_dti"] if stats["count_dti"] > 0 else 0
    stats["avg_ltv"] = stats["total_ltv"] / stats["count_ltv"] if stats["count_ltv"] > 0 else 0
    
    return stats

def generate_markdown(stats):
    p_app = (stats["approved"] / stats["total"]) * 100 if stats["total"] > 0 else 0
    p_rev = (stats["review"] / stats["total"]) * 100 if stats["total"] > 0 else 0
    p_rej = (stats["rejected"] / stats["total"]) * 100 if stats["total"] > 0 else 0
    
    p_t1 = (stats["tier1"] / stats["total"]) * 100 if stats["total"] > 0 else 0
    p_t2 = (stats["tier2"] / stats["total"]) * 100 if stats["total"] > 0 else 0
    p_t3 = (stats["tier3"] / stats["total"]) * 100 if stats["total"] > 0 else 0

    def make_bar(pct):
        filled = int(pct / 5)
        return "▓" * filled + "░" * (20 - filled)

    md = f"""# Comprehensive Loan Underwriting & Risk Operations Report
**Date:** April 10, 2026  
**To:** Senior Leadership, Risk Management, and Operations  
**From:** Automated Underwriting System (AUS) Division  

## 1. Executive Summary
This report presents a detailed analysis of the loan processing operations for the current period. A total of **{stats["total"]}** loan applications were processed through our advanced automated underwriting system. 

The system utilizes a multi-dimensional risk scoring model to evaluate applicants based on Credit Score, Debt-to-Income (DTI) ratio, and Loan-to-Value (LTV) ratio. The primary objective is to optimize approval rates while maintaining strict risk controls to protect the institution's portfolio.

### 1.1 Key Takeaways
*   **Healthy Approval Rate**: {p_app:.1f}% of applications were approved automatically, indicating a strong pipeline of qualified applicants.
*   **Significant Review Volume**: {p_rev:.1f}% of applications were flagged for human review. This highlights a need for potential rule calibration or increased staffing in the underwriting department.
*   **Controlled Risk**: Only {p_rej:.1f}% of applications were outright rejected, suggesting that the top-of-funnel marketing is attracting reasonably qualified leads.

## 2. Operational Metrics

### 2.1 Volume & Disposition

| Metric | Value | Percentage | Visual Representation |
| --- | --- | --- | --- |
| **Total Applications** | {stats["total"]} | 100% | |
| **Approved** | {stats["approved"]} | {p_app:.1f}% | `{make_bar(p_app)}` |
| **Needs Human Review** | {stats["review"]} | {p_rev:.1f}% | `{make_bar(p_rev)}` |
| **Rejected** | {stats["rejected"]} | {p_rej:.1f}% | `{make_bar(p_rej)}` |

### 2.2 Portfolio Averages
*   **Average Debt-to-Income (DTI)**: {stats["avg_dti"]:.1f}% (Target: < 43%)
*   **Average Loan-to-Value (LTV)**: {stats["avg_ltv"]:.1f}% (Target: < 80%)

## 3. Risk Distribution

### 3.1 Disposition Breakdown
```mermaid
pie title Loan Disposition Distribution
    "Approved" : {stats["approved"]}
    "Needs Human Review" : {stats["review"]}
    "Rejected" : {stats["rejected"]}
```

### 3.2 Risk Tier Breakdown
*   **Tier 1 (Low Risk)**: {stats["tier1"]} applications ({p_t1:.1f}%)
*   **Tier 2 (Medium Risk)**: {stats["tier2"]} applications ({p_t2:.1f}%)
*   **Tier 3 (High Risk)**: {stats["tier3"]} applications ({p_t3:.1f}%)

## 4. Methodology & Risk Scoring
The system calculates a risk score based on the following criteria:
*   **Credit Score**: Scores below 640 add significant risk points.
*   **DTI Ratio**: Ratios exceeding 43% add points.
*   **LTV Ratio**: Ratios exceeding 90% add points.
*   **Identity Verification**: Mismatches between applicant data add fraud risk points.

Applications accumulating 6 or more points are automatically **Rejected**. Applications with 3-5 points are routed for **Human Review**. Applications with fewer than 3 points proceed to **Automatic Approval**.

## 5. Strategic Recommendations
Based on the analysis of the current portfolio, we recommend the following strategic actions:
1.  **Rule Calibration & Queue Management**: With over {p_rev:.1f}% of loans requiring review, we recommend auditing the Tier 2 criteria to see if certain low-risk profiles can be safely auto-approved.
2.  **Credit Policy Review**: The average DTI of {stats["avg_dti"]:.1f}% is well within safety limits. There may be room to expand credit availability for applicants with slightly higher DTI if they possess strong credit scores.
3.  **Automation Enhancement**: Investigate common reasons for review routing to identify opportunities for further automated verification (e.g., automated income verification).
4.  **Fraud Detection**: Continue monitoring identity verification flags to prevent fraudulent applications from bypassing the manual review stage.

---
*STRICTLY CONFIDENTIAL // FOR INTERNAL USE ONLY*
"""
    with open(MD_PATH, 'w', encoding='utf-8') as f:
        f.write(md)
    print(f"Generated MD: {MD_PATH}")

def generate_html(stats):
    p_app = (stats["approved"] / stats["total"]) * 100 if stats["total"] > 0 else 0
    p_rev = (stats["review"] / stats["total"]) * 100 if stats["total"] > 0 else 0
    p_rej = (stats["rejected"] / stats["total"]) * 100 if stats["total"] > 0 else 0
    
    p_t1 = (stats["tier1"] / stats["total"]) * 100 if stats["total"] > 0 else 0
    p_t2 = (stats["tier2"] / stats["total"]) * 100 if stats["total"] > 0 else 0
    p_t3 = (stats["tier3"] / stats["total"]) * 100 if stats["total"] > 0 else 0

    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Comprehensive Loan Underwriting Report</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
        body {{
            font-family: 'Inter', sans-serif;
            color: #1e293b;
            line-height: 1.6;
            margin: 40px;
            background-color: #fff;
        }}
        .container {{
            max-width: 850px;
            margin: 0 auto;
            padding: 20px;
        }}
        .header {{
            text-align: center;
            border-bottom: 4px solid #1e3a8a;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }}
        h1 {{
            color: #1e3a8a;
            font-weight: 800;
            font-size: 32px;
            margin-bottom: 5px;
            letter-spacing: -0.05em;
        }}
        .subtitle {{
            color: #64748b;
            font-size: 14px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.1em;
        }}
        h2 {{
            color: #1e3a8a;
            font-size: 20px;
            border-bottom: 2px solid #e2e8f0;
            padding-bottom: 8px;
            margin-top: 35px;
            font-weight: 700;
        }}
        h3 {{
            color: #0f172a;
            font-size: 16px;
            font-weight: 700;
            margin-top: 20px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 25px;
            font-size: 14px;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border: 1px solid #e2e8f0;
        }}
        th {{
            background-color: #f8fafc;
            font-weight: 600;
            color: #1e3a8a;
        }}
        .chart-container {{
            margin-bottom: 30px;
            background-color: #f8fafc;
            padding: 25px;
            border-radius: 10px;
            border: 1px solid #e2e8f0;
        }}
        .bar-wrapper {{
            display: flex;
            align-items: center;
            margin-bottom: 15px;
        }}
        .bar-wrapper:last-child {{
            margin-bottom: 0;
        }}
        .bar-label {{
            width: 180px;
            font-weight: 600;
            font-size: 13px;
            color: #475569;
        }}
        .bar-bg {{
            flex-grow: 1;
            background-color: #e2e8f0;
            height: 18px;
            border-radius: 9px;
            overflow: hidden;
            margin: 0 20px;
        }}
        .bar-fill {{
            height: 100%;
            background-color: #1e3a8a;
            border-radius: 9px;
        }}
        .bar-value {{
            width: 60px;
            font-size: 13px;
            font-weight: 700;
            text-align: right;
            color: #1e3a8a;
        }}
        .fill-approved {{ background-color: #10b981; }}
        .fill-review {{ background-color: #f59e0b; }}
        .fill-rejected {{ background-color: #ef4444; }}
        
        .footer {{
            margin-top: 60px;
            text-align: center;
            font-size: 10px;
            color: #94a3b8;
            border-top: 1px solid #e2e8f0;
            padding-top: 20px;
            font-weight: 600;
            letter-spacing: 0.05em;
        }}
        .kpi-grid {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 15px;
            margin-bottom: 30px;
        }}
        .kpi-card {{
            background-color: #f8fafc;
            padding: 20px;
            border-radius: 10px;
            border: 1px solid #e2e8f0;
            text-align: center;
        }}
        .kpi-title {{
            font-size: 11px;
            color: #64748b;
            font-weight: 600;
            text-transform: uppercase;
            margin-bottom: 8px;
            letter-spacing: 0.05em;
        }}
        .kpi-value {{
            font-size: 28px;
            font-weight: 800;
            color: #1e3a8a;
        }}
        .recommendation-list {{
            background-color: #f0f9ff;
            padding: 20px 40px;
            border-radius: 10px;
            border: 1px solid #bae6fd;
            margin-bottom: 30px;
        }}
        .recommendation-list li {{
            margin-bottom: 10px;
            font-size: 14px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>LOAN PROCESSING OPERATIONS</h1>
            <div class="subtitle">Senior Leadership Report</div>
        </div>
        
        <div style="display: flex; justify-content: space-between; font-size: 12px; color: #64748b; margin-bottom: 25px;">
            <div><strong>Date:</strong> April 10, 2026</div>
            <div><strong>Classification:</strong> STRICTLY CONFIDENTIAL</div>
        </div>
        
        <h2>1. Executive Summary</h2>
        <p style="font-size: 14px;">This report presents a detailed analysis of the loan processing operations for the current period. A total of <strong>{stats["total"]}</strong> loan applications were processed through our advanced automated underwriting system. The primary objective is to optimize approval rates while maintaining strict risk controls to protect the institution's portfolio.</p>
        
        <div class="kpi-grid">
            <div class="kpi-card">
                <div class="kpi-title">Total Volume</div>
                <div class="kpi-value">{stats["total"]}</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">Approval Rate</div>
                <div class="kpi-value">{p_app:.1f}%</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">Avg DTI</div>
                <div class="kpi-value">{stats["avg_dti"]:.1f}%</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">Avg LTV</div>
                <div class="kpi-value">{stats["avg_ltv"]:.1f}%</div>
            </div>
        </div>
        
        <h3>1.1 Key Takeaways</h3>
        <ul style="font-size: 14px;">
            <li><strong>Healthy Approval Rate</strong>: {p_app:.1f}% of applications were approved automatically, indicating a strong pipeline of qualified applicants.</li>
            <li><strong>Significant Review Volume</strong>: {p_rev:.1f}% of applications were flagged for human review. This highlights a need for potential rule calibration or increased staffing in the underwriting department.</li>
            <li><strong>Controlled Risk</strong>: Only {p_rej:.1f}% of applications were outright rejected, suggesting that the top-of-funnel marketing is attracting reasonably qualified leads.</li>
        </ul>
        
        <h2>2. Disposition Breakdown</h2>
        <div class="chart-container">
            <div class="bar-wrapper">
                <div class="bar-label">Approved</div>
                <div class="bar-bg"><div class="bar-fill fill-approved" style="width: {p_app}%"></div></div>
                <div class="bar-value">{p_app:.1f}%</div>
            </div>
            <div class="bar-wrapper">
                <div class="bar-label">Needs Human Review</div>
                <div class="bar-bg"><div class="bar-fill fill-review" style="width: {p_rev}%"></div></div>
                <div class="bar-value">{p_rev:.1f}%</div>
            </div>
            <div class="bar-wrapper">
                <div class="bar-label">Rejected</div>
                <div class="bar-bg"><div class="bar-fill fill-rejected" style="width: {p_rej}%"></div></div>
                <div class="bar-value">{p_rej:.1f}%</div>
            </div>
        </div>
        
        <h2>3. Risk Tier Analysis</h2>
        <div class="chart-container">
            <div class="bar-wrapper">
                <div class="bar-label">Tier 1 (Low Risk)</div>
                <div class="bar-bg"><div class="bar-fill" style="width: {p_t1}%"></div></div>
                <div class="bar-value">{p_t1:.1f}%</div>
            </div>
            <div class="bar-wrapper">
                <div class="bar-label">Tier 2 (Medium Risk)</div>
                <div class="bar-bg"><div class="bar-fill" style="width: {p_t2}%"></div></div>
                <div class="bar-value">{p_t2:.1f}%</div>
            </div>
            <div class="bar-wrapper">
                <div class="bar-label">Tier 3 (High Risk)</div>
                <div class="bar-bg"><div class="bar-fill" style="width: {p_t3}%"></div></div>
                <div class="bar-value">{p_t3:.1f}%</div>
            </div>
        </div>
        
        <h2>4. Methodology & Risk Scoring</h2>
        <p style="font-size: 14px;">The system calculates a risk score based on the following criteria:</p>
        <ul style="font-size: 14px;">
            <li><strong>Credit Score</strong>: Scores below 640 add significant risk points.</li>
            <li><strong>DTI Ratio</strong>: Ratios exceeding 43% add points.</li>
            <li><strong>LTV Ratio</strong>: Ratios exceeding 90% add points.</li>
            <li><strong>Identity Verification</strong>: Mismatches between applicant data add fraud risk points.</li>
        </ul>
        <p style="font-size: 14px;">Applications accumulating 6 or more points are automatically <strong>Rejected</strong>. Applications with 3-5 points are routed for <strong>Human Review</strong>. Applications with fewer than 3 points proceed to <strong>Automatic Approval</strong>.</p>
        
        <h2>5. Strategic Recommendations</h2>
        <div class="recommendation-list">
            <ul>
                <li><strong>Rule Calibration & Queue Management</strong>: With over {p_rev:.1f}% of loans requiring review, we recommend auditing the Tier 2 criteria to see if certain low-risk profiles can be safely auto-approved.</li>
                <li><strong>Credit Policy Review</strong>: The average DTI of {stats["avg_dti"]:.1f}% is well within safety limits. There may be room to expand credit availability for applicants with slightly higher DTI if they possess strong credit scores.</li>
                <li><strong>Automation Enhancement</strong>: Investigate common reasons for review routing to identify opportunities for further automated verification (e.g., automated income verification).</li>
                <li><strong>Fraud Detection</strong>: Continue monitoring identity verification flags to prevent fraudulent applications from bypassing the manual review stage.</li>
            </ul>
        </div>
        
        <div class="footer">
            STRICTLY CONFIDENTIAL // FOR INTERNAL USE ONLY // GENERATED BY AUS V4.2.1
        </div>
    </div>
</body>
</html>
"""
    with open(HTML_PATH, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"Generated HTML: {HTML_PATH}")

if __name__ == "__main__":
    try:
        stats = read_data()
        generate_markdown(stats)
        generate_html(stats)
    except Exception as e:
        print(f"Error generating report: {e}")
