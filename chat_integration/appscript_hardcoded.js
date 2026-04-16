function onMessage(event) {
  const version = "MOCK_V21 (Suggestive Fallback)";
  console.log("Running version: " + version);
  console.log("Received event:", JSON.stringify(event));

  var text = "";
  var spaceName = "";

  // Extract text and space name safely
  if (event && event.chat && event.chat.messagePayload) {
    text = event.chat.messagePayload.message.text;
    spaceName = event.chat.messagePayload.space.name;
  } else if (event.message) {
    text = event.message.text;
    spaceName = event.space.name;
  }

  console.log("User message: " + text);
  console.log("Space name: " + spaceName);

  if (!text || text.trim() === "") {
    return { "text": "Please provide a command." };
  }

  var lowerText = text.toLowerCase();

  // Updated to be more suggestive and highlight keywords using Chat markdown (*)
  var responseText = "I didn't quite catch that. Try asking me to show the *latest 10 unprocessed* applications, *process L_0001*, *summarize loan applications*, or generate a *slide deck*. How can I help?";

  // 0. Greeting
  if (lowerText.includes("hi") || lowerText.includes("hello")) {
    console.log("Flow: GREETING | Version: " + version + " | Message: " + text);
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
    console.log("Flow: UNPROCESSED | Version: " + version + " | Message: " + text);
    responseText = `Here are 10 unprocessed mortgage loan applications:

L_0001 - DTI: 37.8% - LTV: 86.9%
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
    console.log("Flow: PROCESS L_0001 | Version: " + version + " | Message: " + text);
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
    console.log("Flow: SUMMARIZE | Version: " + version + " | Message: " + text);
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
    console.log("Flow: SLIDE DECK | Version: " + version + " | Message: " + text);
    responseText = `I have generated the slide deck for you. You can access it here: https://docs.google.com/presentation/d/1PuiV9BgsP3oFSyGNoQ4d_5GxIGjsAoUiJ737bJpYnVg/edit?slide=id.p1#slide=id.p1`;
  }

  // 3-second sleep to simulate thinking
  console.log("Sleeping for 3 seconds to simulate thinking...");
  Utilities.sleep(3000);

  // PUSH THE MESSAGE DIRECTLY VIA CHAT API
  if (spaceName) {
    try {
      console.log("Attempting to push message to space...");
      Chat.Spaces.Messages.create({
        "text": responseText
      }, spaceName);
      console.log("Message pushed successfully!");
    } catch (e) {
      console.error("Error pushing message: " + e.toString());
    }
  }

  // Return a dummy response to satisfy the execution
  return { 
    "actionResponse": { "type": "NEW_MESSAGE" },
    "text": "I am processing your request..." 
  };
}
