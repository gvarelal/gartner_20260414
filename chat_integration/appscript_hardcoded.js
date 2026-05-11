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
L_0002 - DTI: 24.6% - LTV: 50.8%
L_0003 - DTI: 49.8% - LTV: 92.1%
L_0004 - DTI: 42.5% - LTV: 86.8%
L_0005 - DTI: 26.0% - LTV: 70.4%
L_0006 - DTI: 26.1% - LTV: 78.6%
L_0007 - DTI: 27.1% - LTV: 65.5%
L_0008 - DTI: 28.0% - LTV: 74.4%
L_0009 - DTI: 54.2% - LTV: 93.3%
L_0010 - DTI: 38.1% - LTV: 83.0%`;
  }

  // 2. Process L_0001
  else if (lowerText.includes("l_0001")) {
    responseText = `Loan Application ID: L_0001

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
- Reach out to verify SSN.`;
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
- Download Excel Summary: https://storage.cloud.google.com/gartner_loan_processing_summary/generation_summary.xlsx
- View Full HTML Report: https://storage.cloud.google.com/gartner_loan_processing_summary/loan_processing_report.html`;
  }

  // 4. Slide deck
  else if (lowerText.includes("slide deck")) {
    responseText = `I have generated the slide deck for you. You can access it here: https://docs.google.com/presentation/d/1PuiV9BgsP3oFSyGNoQ4d_5GxIGjsAoUiJ737bJpYnVg/edit?slide=id.p1#slide=id.p1`;
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

