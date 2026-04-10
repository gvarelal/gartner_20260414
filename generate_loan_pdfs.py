import asyncio
import os
import json
import random
import argparse
from playwright.async_api import async_playwright
from faker import Faker
from google.cloud import storage

# Setup Directories
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(CURRENT_DIR, "generated_loan_docs")
os.makedirs(OUTPUT_DIR, exist_ok=True)

fake = Faker()
Faker.seed(42)
random.seed(42)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700;800&display=swap');
        
        @page {{
            size: A4 portrait;
            margin: 15mm;
        }}

        body {{
            margin: 0;
            padding: 0;
            font-family: 'Inter', sans-serif;
            color: #1e293b;
            background-color: #fff;
            font-size: 12px;
            line-height: 1.5;
        }}

        .container {{
            max-width: 800px;
            margin: 0 auto;
        }}

        .header {{
            text-align: center;
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 3px solid #0f172a;
        }}

        .header h1 {{
            color: #0f172a;
            margin: 0;
            font-size: 22px;
            font-weight: 800;
            letter-spacing: 0.05em;
        }}

        .header p {{
            margin: 5px 0 0 0;
            color: #64748b;
            font-size: 12px;
            font-weight: 500;
        }}

        .metadata-grid {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 10px;
            margin-bottom: 20px;
            padding: 10px;
            background-color: #f8fafc;
            border-radius: 6px;
            border: 1px solid #e2e8f0;
        }}

        .metadata-item {{
            font-size: 11px;
        }}

        .metadata-label {{
            color: #64748b;
            font-weight: 600;
            text-transform: uppercase;
            font-size: 10px;
        }}

        .metadata-value {{
            color: #0f172a;
            font-weight: 700;
            font-family: monospace;
        }}

        .section-title {{
            font-size: 14px;
            font-weight: 700;
            color: #0f172a;
            margin: 20px 0 10px 0;
            padding-bottom: 5px;
            border-bottom: 1px solid #e2e8f0;
            text-transform: uppercase;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 15px;
        }}

        th, td {{
            border: 1px solid #e2e8f0;
            padding: 10px 12px;
            text-align: left;
        }}

        th {{
            background-color: #f8fafc;
            font-weight: 600;
            color: #475569;
            width: 30%;
        }}

        .value-col {{
            width: 35%;
            font-weight: 500;
        }}

        .evidence-col {{
            width: 35%;
            color: #64748b;
            font-size: 11px;
            font-style: italic;
        }}

        .disposition-box {{
            display: inline-block;
            padding: 6px 12px;
            border-radius: 4px;
            font-weight: 700;
            font-size: 12px;
            text-transform: uppercase;
        }}

        .decision-approved {{
            background-color: #dcfce7;
            color: #15803d;
            border: 1px solid #bbf7d0;
        }}

        .decision-rejected {{
            background-color: #fee2e2;
            color: #b91c1c;
            border: 1px solid #fecaca;
        }}

        .decision-review {{
            background-color: #fef9c3;
            color: #a16207;
            border: 1px solid #fef08a;
        }}

        .flag-section {{
            background-color: #f8fafc;
            padding: 12px;
            border-radius: 6px;
            border: 1px solid #e2e8f0;
            margin-bottom: 15px;
        }}

        .flag-title {{
            font-weight: 700;
            font-size: 11px;
            text-transform: uppercase;
            margin-bottom: 5px;
        }}

        .flag-title.integrity {{
            color: #b91c1c;
        }}

        .flag-title.policy {{
            color: #a16207;
        }}

        .footer {{
            margin-top: 30px;
            text-align: center;
            font-size: 10px;
            color: #94a3b8;
            padding-top: 10px;
            border-top: 1px solid #e2e8f0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>CREDIT MEMORANDUM & UNDERWRITING WORKSHEET</h1>
            <p>Automated Underwriting System (AUS) - Risk Assessment Trail</p>
        </div>

        <div class="metadata-grid">
            <div class="metadata-item">
                <div class="metadata-label">Processing Timestamp</div>
                <div class="metadata-value">{timestamp}</div>
            </div>
            <div class="metadata-item">
                <div class="metadata-label">Model Version</div>
                <div class="metadata-value">{model_version}</div>
            </div>
            <div class="metadata-item">
                <div class="metadata-label">Bureau Reference ID</div>
                <div class="metadata-value">{bureau_ref}</div>
            </div>
        </div>

        <div class="section-title">File Identification</div>
        <table>
            <tr>
                <th>Loan Application ID</th>
                <td class="value-col">{loan_id}</td>
                <td class="evidence-col">System Generated</td>
            </tr>
            <tr>
                <th>Applicant Name</th>
                <td class="value-col">{name}</td>
                <td class="evidence-col">Extracted from Application.pdf</td>
            </tr>
            <tr>
                <th>Contact Email</th>
                <td class="value-col">{email}</td>
                <td class="evidence-col">Extracted from Application.pdf</td>
            </tr>
            <tr>
                <th>SSN (Masked)</th>
                <td class="value-col">{ssn}</td>
                <td class="evidence-col">OCR Confidence: {ocr_confidence}</td>
            </tr>
        </table>

        <div class="section-title">Financial Analysis & Ratios</div>
        <table>
            <tr>
                <th>Verified Annual Gross</th>
                <td class="value-col">{income}</td>
                <td class="evidence-col">Extracted from Pay_Stub.png ({ocr_confidence})</td>
            </tr>
            <tr>
                <th>Loan Amount Requested</th>
                <td class="value-col">{loan_amount}</td>
                <td class="evidence-col">Extracted from Application.pdf</td>
            </tr>
            <tr>
                <th>Appraised Property Value</th>
                <td class="value-col">{property_value}</td>
                <td class="evidence-col">Simulated Valuation Engine</td>
            </tr>
            <tr>
                <th>Debt-to-Income (DTI)</th>
                <td class="value-col">{dti}</td>
                <td class="evidence-col">Formula: Total Debt / Gross Income</td>
            </tr>
            <tr>
                <th>Loan-to-Value (LTV)</th>
                <td class="value-col">{ltv}</td>
                <td class="evidence-col">Formula: Loan Amount / Appraised Value</td>
            </tr>
            <tr>
                <th>Credit Score</th>
                <td class="value-col">{credit_score}</td>
                <td class="evidence-col">Direct Bureau Pull</td>
            </tr>
        </table>

        <div class="section-title">Risk Assessment & Disposition</div>
        <table>
            <tr>
                <th>Pricing Grade / Risk Tier</th>
                <td class="value-col">{risk_tier}</td>
                <td class="evidence-col">Based on Credit, DTI, and LTV</td>
            </tr>
            <tr>
                <th>Status / Disposition</th>
                <td class="value-col"><span class="disposition-box {decision_class}">{disposition}</span></td>
                <td class="evidence-col">Final Automated Decision</td>
            </tr>
        </table>

        <div class="section-title">Automated Risk Flags</div>
        
        <div class="flag-section">
            <div class="flag-title integrity">Data Integrity Flags</div>
            <div>{data_integrity_flags}</div>
        </div>

        <div class="flag-section">
            <div class="flag-title policy">Credit & Policy Flags</div>
            <div>{credit_policy_flags}</div>
        </div>

        <div class="section-title">Recommended Next Steps</div>
        <table>
            <tr>
                <td style="width: 100%; background-color: #f8fafc;">{next_steps}</td>
            </tr>
        </table>

        <div class="footer">
            <span>STRICTLY CONFIDENTIAL // FOR INTERNAL UNDERWRITING USE ONLY</span>
        </div>
    </div>
</body>
</html>
"""

def generate_record(counter):
    import datetime
    
    loan_id = f"L_{counter:04d}"
    name = fake.name()
    
    # Fraud simulation: 5% chance of mismatch
    is_fraud = random.random() < 0.05
    email_domains = ['gmail.com', 'yahoo.com', 'outlook.com']
    
    if is_fraud:
        email = f"{fake.first_name().lower()}.{fake.last_name().lower()}@{random.choice(email_domains)}"
    else:
        email = f"{name.replace(' ', '.').lower()}@{random.choice(email_domains)}"
        
    phone = fake.phone_number()
    ssn = fake.ssn()
    
    # Financial Data Generation
    property_value = random.randint(150000, 800000)
    
    # Rule overrides for IDs 1-10
    if counter in [2, 5, 7, 8]:
        credit_score = random.randint(760, 850)
        dti_percentage = random.uniform(0.15, 0.34)
        ltv_percentage = random.uniform(0.50, 0.79)
    elif counter in [3, 9]:
        credit_score = random.randint(500, 590)
        dti_percentage = random.uniform(0.46, 0.55)
        ltv_percentage = random.uniform(0.91, 0.95)
    elif counter in [1, 4, 10]:
        credit_score = random.randint(610, 740)
        dti_percentage = random.uniform(0.36, 0.44)
        ltv_percentage = random.uniform(0.81, 0.89)
    else:
        credit_score = random.randint(500, 850)
        dti_percentage = random.uniform(0.15, 0.55)
        ltv_percentage = random.uniform(0.5, 0.95)

    loan_amount_val = int(property_value * ltv_percentage)
    
    income_val = random.randint(50000, 250000)
    monthly_income = income_val / 12
    monthly_debt = int(monthly_income * dti_percentage)
    
    # Calculations for display
    dti = dti_percentage * 100
    ltv = ltv_percentage * 100
    
    # Multi-dimensional Risk Logic
    risk_factors = 0
    if credit_score < 640: risk_factors += 3
    if dti > 43: risk_factors += 3
    if ltv > 90: risk_factors += 2
    if is_fraud: risk_factors += 4
    
    if risk_factors >= 6:
        risk_tier = "Tier 3 (High Risk)"
        disposition = "REJECTED"
        decision_class = "decision-rejected"
    elif risk_factors >= 3:
        risk_tier = "Tier 2 (Medium Risk)"
        disposition = "NEEDS HUMAN REVIEW"
        decision_class = "decision-review"
    else:
        risk_tier = "Tier 1 (Low Risk)"
        disposition = "APPROVED"
        decision_class = "decision-approved"
        
    # Hardcoded overrides for demo IDs 1-10
    if counter in [2, 5, 7, 8]:
        disposition = "APPROVED"
        risk_tier = "Tier 1 (Low Risk)"
        decision_class = "decision-approved"
    elif counter in [3, 9]:
        disposition = "REJECTED"
        risk_tier = "Tier 3 (High Risk)"
        decision_class = "decision-rejected"
    elif counter in [1, 4, 10]:
        disposition = "NEEDS HUMAN REVIEW"
        risk_tier = "Tier 2 (Medium Risk)"
        decision_class = "decision-review"
        
    # Categorize Warnings
    data_integrity_flags = []
    credit_policy_flags = []
    
    if is_fraud:
        data_integrity_flags.append("Applicant name does not match email domain owner identity.")
    
    if credit_score < 640:
        credit_policy_flags.append(f"Credit score ({credit_score}) below minimum threshold of 640.")
    if dti > 43:
        credit_policy_flags.append(f"Debt-to-Income ratio ({dti:.1f}%) exceeds standard limit of 43%.")
    if ltv > 90:
        credit_policy_flags.append(f"Loan-to-Value ratio ({ltv:.1f}%) exceeds 90%.")
        
    data_flags_str = "<br>".join([f"- {f}" for f in data_integrity_flags]) if data_integrity_flags else "- None"
    credit_flags_str = "<br>".join([f"- {f}" for f in credit_policy_flags]) if credit_policy_flags else "- None"
    
    # Next Steps
    if disposition == "REJECTED":
        next_steps = "- Send adverse action notice.<br>- File retainment for compliance auditing."
    elif disposition == "NEEDS HUMAN REVIEW":
        next_steps = "- Verify address with applicant.<br>- Request tax returns for income verification."
        if is_fraud:
            next_steps += "<br>- Compare Utility Bill (Extracted) vs. Application Address; flag discrepancies in LexisNexis."
    else:
        next_steps = "- Proceed to closing."
        
    # Confidence Scores
    ocr_confidence = f"{random.randint(95, 99)}%"
    
    # Metadata
    timestamp = datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    bureau_ref = f"EXP-{random.randint(100000, 999999)}-X"
    
    return {
        "loan_id": loan_id,
        "name": name,
        "email": email,
        "phone": phone,
        "ssn": ssn,
        "income": f"${income_val:,}",
        "loan_amount": f"${loan_amount_val:,}",
        "property_value": f"${property_value:,}",
        "credit_score": str(credit_score),
        "risk_tier": risk_tier,
        "disposition": disposition,
        "decision_class": decision_class,
        "data_integrity_flags": data_flags_str,
        "credit_policy_flags": credit_flags_str,
        "next_steps": next_steps,
        "dti": f"{dti:.1f}%",
        "ltv": f"{ltv:.1f}%",
        "ocr_confidence": ocr_confidence,
        "timestamp": timestamp,
        "bureau_ref": bureau_ref,
        "model_version": "Underwriting_Engine_v4.2.1"
    }


async def generate_pdf(record, page):
    html_content = HTML_TEMPLATE.format(**record)
    await page.set_content(html_content)
    await asyncio.sleep(0.5)
    
    output_path = os.path.join(OUTPUT_DIR, f"{record['loan_id']}_processed.pdf")
    await page.pdf(path=output_path, print_background=True, width="210mm", height="297mm")
    print(f"Generated PDF: {output_path}")
    

    
    return output_path

def upload_to_gcs(file_path, bucket_name):
    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob_name = os.path.basename(file_path)
        blob = bucket.blob(blob_name)
        
        blob.upload_from_filename(file_path)
        print(f"Uploaded {blob_name} to gs://{bucket_name}/")
        return True
    except Exception as e:
        print(f"Failed to upload {file_path} to GCS: {e}")
        return False

async def main():
    parser = argparse.ArgumentParser(description="Generate synthetic loan PDFs and upload to GCS.")
    parser.add_argument("--count", type=int, default=5, help="Number of records to generate")
    parser.add_argument("--bucket", type=str, default="gartner_loan_processing", help="GCS bucket name")
    parser.add_argument("--start", type=int, default=None, help="Starting counter for IDs")
    args = parser.parse_args()
    
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        
        log_path = os.path.join(CURRENT_DIR, "generation_log.md")
        
        # Check if we need to write headers
        write_headers = not os.path.exists(log_path) or os.path.getsize(log_path) == 0
        
        with open(log_path, "a") as log_file:
            if write_headers:
                log_file.write("| Loan ID | Name | Email | Disposition | Risk Tier | DTI | LTV |\n")
                log_file.write("| --- | --- | --- | --- | --- | --- | --- |\n")
                
            # Find the highest existing loan ID to make it evergrowing
            import glob
            import re
            existing_files = glob.glob(os.path.join(OUTPUT_DIR, "L_*_processed.pdf"))
            start_counter = 1
            if args.start is not None:
                start_counter = args.start
            elif existing_files:
                try:
                    ids = [int(m.group(1)) for f in existing_files if (m := re.search(r"L_(\d+)_processed", os.path.basename(f)))]
                    if ids:
                        start_counter = max(ids) + 1
                except Exception:
                    pass
            
            for i in range(start_counter, start_counter + args.count):
                record = generate_record(i)
                pdf_path = await generate_pdf(record, page)
                
                # Log to markdown table
                log_file.write(f"| {record['loan_id']} | {record['name']} | {record['email']} | {record['disposition']} | {record['risk_tier']} | {record['dti']} | {record['ltv']} |\n")
                
                # Upload to GCS
                upload_to_gcs(pdf_path, args.bucket)
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
