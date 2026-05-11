const version = "MOCK_V33 (Workspace Add-on with Chat Push and Native Card Return)";

function doPost(e) {
  try {
    console.log("Received POST request in Web App Bridge. Version: " + version);
    var event = JSON.parse(e.postData.contents);
    console.log("Received event:", JSON.stringify(event));
    
    // Extract text
    var text = "";
    if (event && event.chat && event.chat.messagePayload && event.chat.messagePayload.message) {
      text = event.chat.messagePayload.message.text;
    } else if (event && event.message && event.message.text) {
      text = event.message.text;
    }
    
    console.log("Extracted text: " + text);
    
    var responseText = getResponseForText(text);
    var responsePayload = buildChatResponseJSON(responseText);
    
    return ContentService.createTextOutput(JSON.stringify(responsePayload))
                         .setMimeType(ContentService.MimeType.JSON);
  } catch (err) {
    console.error("Web App Bridge Crash: " + err.toString());
    var errPayload = {
      "text": "🚨 *Web App Bridge Crash Error:*\n" + err.toString()
    };
    return ContentService.createTextOutput(JSON.stringify(errPayload))
                         .setMimeType(ContentService.MimeType.JSON);
  }
}

function onMessage(event) {
  try {
    console.log("Received direct onMessage invocation. Version: " + version);
    console.log("Received event:", JSON.stringify(event));
    
    var text = "";
    var spaceName = "";
    if (event && event.chat && event.chat.messagePayload) {
      text = event.chat.messagePayload.message.text;
      spaceName = event.chat.messagePayload.space.name;
    } else if (event && event.message) {
      text = event.message.text;
      spaceName = event.space.name;
    }
    
    console.log("Extracted text: " + text + ", spaceName: " + spaceName);
    
    var responseText = getResponseForText(text);
    
    if (spaceName) {
      try {
        console.log("Pushing text message via Chat Advanced Service to space: " + spaceName);
        Chat.Spaces.Messages.create({ "text": responseText }, spaceName);
        console.log("Message pushed successfully!");
      } catch (e) {
        console.error("Error pushing message via Chat Advanced Service: " + e.toString());
      }
    }
    
    return buildPlaceholderCard();
  } catch (e) {
    console.error("Direct onMessage Crash Error: " + e.toString());
    return CardService.newCardBuilder()
      .setHeader(CardService.newCardHeader().setTitle("Loan Supervisor Error"))
      .addSection(CardService.newCardSection().addWidget(CardService.newTextParagraph().setText("Error: " + e.toString())))
      .build();
  }
}

// Centralized text response logic
const mockLoanResponses = {
  "l_0001": `Loan Application ID: L_0001

Name: Andrew Jason
Email: andrew.jason@example.com
Phone: +1-555-010-9988
Decision: NEEDS HUMAN REVIEW

Warnings:
- Missing preferred documents: Bank Statement, Tax Statements.
- Name mismatch: Andrew Jason vs Andrew Jason Sample.
- SSN is a placeholder and requires secondary verification.
- Income discrepancy: $125,000 vs $140,200 YTD.

Recommended Next Step:
- Send this application for deep review.
- Reach out to verify SSN.

Underwriting Worksheet: <https://storage.cloud.google.com/gartner_loan_processing/L_0001_processed.pdf|L_0001_processed.pdf>`,

  "l_0002": `Loan Application ID: L_0002

Name: Cristian Santos
Email: amy.robinson@gmail.com
Income: $150,000
Loan Amount: $50,000
Credit Score: 780
Risk Score: 2
Decision: APPROVED

Warnings:
- None.
- [System Check]: PII data matches 100% across all submitted documents.
- [System Check]: Income verified via payroll API ($150,000 vs $149,800 reported).
- [System Check]: FICO score 780 meets prime tier criteria.

Recommended Next Step:
- Push to automated closing queue.
- Generate closing disclosure (CD) and send to applicant.
- Wire funds to escrow account upon e-signature confirmation.

Underwriting Worksheet: <https://storage.cloud.google.com/gartner_loan_processing/L_0002_processed.pdf|L_0002_processed.pdf>`,

  "l_0003": `Loan Application ID: L_0003

Name: Gregory Baker
Email: gregory.baker@gmail.com
Income: $45,000
Loan Amount: $120,000
Credit Score: 540
Risk Score: 10
Decision: REJECTED

Warnings:
- Credit score 540 is below the minimum required 620 for this product.
- Calculated DTI is 49.8%, exceeding the maximum allowed 45%.
- Active tax lien found in public records search.

Recommended Next Step:
- Generate FCRA-compliant Adverse Action notice.
- Provide applicant with credit score disclosure and factors.
- Close file in system and retain for mandatory compliance period.

Underwriting Worksheet: <https://storage.cloud.google.com/gartner_loan_processing/L_0003_processed.pdf|L_0003_processed.pdf>`,

  "l_0004": `Loan Application ID: L_0004

Name: Patricia Galloway
Email: patricia.galloway@yahoo.com
Income: $85,000
Loan Amount: $90,000
Credit Score: 650
Risk Score: 6
Decision: NEEDS HUMAN REVIEW

Warnings:
- Income reported as self-employed; requires manual verification of 1040 Schedule C.
- Debt-to-Income ratio is at 42.5%, approaching the system threshold.
- Credit report shows a recent dispute on a primary credit card account.

Recommended Next Step:
- Assign to Senior Underwriter specializing in self-employment.
- Request last 24 months of business bank statements for cash flow analysis.
- Verify business registration status via Secretary of State portal.

Underwriting Worksheet: <https://storage.cloud.google.com/gartner_loan_processing/L_0004_processed.pdf|L_0004_processed.pdf>`,

  "l_0005": `Loan Application ID: L_0005

Name: Carolyn Daniel
Email: carolyn.daniel@outlook.com
Income: $160,000
Loan Amount: $40,000
Credit Score: 790
Risk Score: 1
Decision: APPROVED

Warnings:
- None.
- [System Check]: 10+ years of clean credit history verified with zero delinquencies.
- [System Check]: Employment confirmed directly with employer HR via automated API.

Recommended Next Step:
- Fast-track to document generation module.
- Send digital welcome package and loan terms to applicant.

Underwriting Worksheet: <https://storage.cloud.google.com/gartner_loan_processing/L_0005_processed.pdf|L_0005_processed.pdf>`,

  "l_0006": `Loan Application ID: L_0006

Name: Tommy Walter
Email: tommy.walter@gmail.com
Income: $85,000
Loan Amount: $90,000
Credit Score: 650
Risk Score: 6
Decision: NEEDS HUMAN REVIEW

Warnings:
- Unclassified application profile requiring standard manual triage.
- Address verification returned a partial match.
- Income documentation provided is in a non-standard format.

Recommended Next Step:
- Triage to manual review queue for general underwriting.
- Perform secondary address verification via postal database.
- Request standard W-2 or Tax Return forms.

Underwriting Worksheet: <https://storage.cloud.google.com/gartner_loan_processing/L_0006_processed.pdf|L_0006_processed.pdf>`,

  "l_0007": `Loan Application ID: L_0007

Name: Peter Callahan Jr.
Email: peter.callahan.jr.@outlook.com
Income: $145,000
Loan Amount: $55,000
Credit Score: 760
Risk Score: 2
Decision: APPROVED

Warnings:
- None.
- [System Check]: Liquid reserves exceed minimum requirements by 150%.
- [System Check]: Low LTV ratio (35%) provides strong collateral position.

Recommended Next Step:
- Approve loan application and queue for closing.
- Notify assigned loan officer of green-light status.
- Generate automated closing document package.

Underwriting Worksheet: <https://storage.cloud.google.com/gartner_loan_processing/L_0007_processed.pdf|L_0007_processed.pdf>`,

  "l_0008": `Loan Application ID: L_0008

Name: Kimberly Adams
Email: kimberly.adams@outlook.com
Income: $155,000
Loan Amount: $45,000
Credit Score: 770
Risk Score: 2
Decision: APPROVED

Warnings:
- None.
- [System Check]: Digital signatures on all documents are cryptographically valid.
- [System Check]: Income source matches historical tax transcripts.

Recommended Next Step:
- Execute automated approval workflow.
- Send e-sign link for final documents to applicant.
- Log green-light status in audit trail.

Underwriting Worksheet: <https://storage.cloud.google.com/gartner_loan_processing/L_0008_processed.pdf|L_0008_processed.pdf>`,

  "l_0009": `Loan Application ID: L_0009

Name: Paula Moreno
Email: paula.moreno@yahoo.com
Income: $40,000
Loan Amount: $130,000
Credit Score: 520
Risk Score: 10
Decision: REJECTED

Warnings:
- Unable to verify income (scans provided are illegible).
- Applicant has insufficient credit history (thin file).
- Requested loan amount exceeds maximum permitted for calculated income.
- Uploaded bank statements contain blurred and illegible pages.

Recommended Next Step:
- Send notice of incomplete application / adverse action.
- Provide instructions on how to appeal with valid documents.

Underwriting Worksheet: <https://storage.cloud.google.com/gartner_loan_processing/L_0009_processed.pdf|L_0009_processed.pdf>`,

  "l_0010": `Loan Application ID: L_0010

Name: Rose Spence
Email: rose.spence@outlook.com
Income: $80,000
Loan Amount: $95,000
Credit Score: 660
Risk Score: 6
Decision: NEEDS HUMAN REVIEW

Warnings:
- Employment gap of 6 months in the last 2 years requires explanation.
- Unexplained large deposit of $50,000 in recent bank statement.
- Property appraisal value is borderline for requested loan amount.

Recommended Next Step:
- Request letter of explanation for employment gap from applicant.
- Request documentation for source of large deposit.
- Order desk review of property appraisal.

Underwriting Worksheet: <https://storage.cloud.google.com/gartner_loan_processing/L_0010_processed.pdf|L_0010_processed.pdf>`
};

function getResponseForText(text) {
  if (!text || text.trim() === "") {
    return "Please provide a command.";
  }
  
  var lowerText = text.toLowerCase();
  
  // Default fallback response
  var responseText = "I didn't quite catch that. Try asking me to show the *latest 10 unprocessed* applications, *process L_0001*, *summarize loan applications*, or generate a *slide deck*. How can I help?";
  
  // 0. Greeting
  if (lowerText.includes("hi") || lowerText.includes("hello")) {
    responseText = `Hello! I am the Loan Supervisor Agent.

I can help you with the following tasks:
- List the latest 10 unprocessed mortgage loan applications.
- Process a specific application (e.g., "Process application L_0001").
- Summarize the loan applications processed in the last batch.
- Generate a slide deck with the summary report.

How can I assist you today?`;
  }
  
  // 1. Latest 10 unprocessed
  else if (lowerText.includes("latest 10 unprocessed")) {
    responseText = `Here are 10 unprocessed mortgage loan applications:

L_0001 - Andrew Jason - DTI: 37.8% - LTV: 86.9%
L_0002 - Cristian Santos - DTI: 24.6% - LTV: 50.8%
L_0003 - Gregory Baker - DTI: 49.8% - LTV: 92.1%
L_0004 - Patricia Galloway - DTI: 42.5% - LTV: 86.8%
L_0005 - Carolyn Daniel - DTI: 26.0% - LTV: 70.4%
L_0006 - Tommy Walter - DTI: 26.1% - LTV: 78.6%
L_0007 - Peter Callahan Jr. - DTI: 27.1% - LTV: 65.5%
L_0008 - Kimberly Adams - DTI: 28.0% - LTV: 74.4%
L_0009 - Paula Moreno - DTI: 54.2% - LTV: 93.3%
L_0010 - Rose Spence - DTI: 38.1% - LTV: 83.0%`;
  }
  
  // 2. Match L_0001 to L_0010 dynamically
  else {
    var match = lowerText.match(/(l_00\d{2})/);
    if (match) {
      var loanId = match[1];
      if (mockLoanResponses[loanId]) {
        responseText = mockLoanResponses[loanId];
      }
    }
    // 3. Summarize
    else if (lowerText.includes("summarize") && lowerText.includes("loan applications")) {
      responseText = `Summary of 1,108 mortgage applications:

Executive Summary:
The automated loan processing agent has completed its review. 40.8% automatically approved, 15.3% automatically rejected, and 43.9% flagged for manual human review.

Status Breakdown:
- Approved: 452 (40.8%)
- Needs Human Review: 486 (43.9%)
- Rejected: 170 (15.3%)
- Total: 1,108 (100%)

Download Full Reports:
- <https://storage.cloud.google.com/gartner_loan_processing_summary/generation_summary.xlsx|Download Excel Summary>
- <https://storage.cloud.google.com/gartner_loan_processing_summary/loan_processing_report.html|View Full HTML Report>`;
    }
    // 4. Slide deck
    else if (lowerText.includes("slide deck")) {
      responseText = `I have generated the slide deck for you. You can access it here: <https://docs.google.com/presentation/d/1PuiV9BgsP3oFSyGNoQ4d_5GxIGjsAoUiJ737bJpYnVg/edit?slide=id.p1#slide=id.p1|Slide Deck>`;
    }
  }

  return responseText;
}

// Helper to construct standard Google Chat JSON message with Card
function buildChatResponseJSON(text) {
  return {
    "cardsV2": [
      {
        "cardId": "mainCard",
        "card": {
          "header": {
            "title": "Loan Supervisor Agent",
            "subtitle": "Mortgage Processing Assistant"
          },
          "sections": [
            {
              "widgets": [
                {
                  "textParagraph": {
                    "text": text
                  }
                }
              ]
            }
          ]
        }
      }
    ]
  };
}

function buildPlaceholderCard() {
  return CardService.newCardBuilder()
    .setHeader(CardService.newCardHeader()
      .setTitle("Loan Supervisor")
      .setSubtitle("Mortgage Assistant"))
    .addSection(CardService.newCardSection()
      .addWidget(CardService.newTextParagraph()
        .setText("Processing request...")))
    .build();
}



