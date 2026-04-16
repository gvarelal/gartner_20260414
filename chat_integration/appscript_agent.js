function queryReasoningEngine(queryText) {
  const PROJECT_ID = "demo4events10";
  const LOCATION = "us-central1";
  const REASONING_ENGINE_ID = "5328541761214087168";
  
  var url = "https://" + LOCATION + "-aiplatform.googleapis.com/v1/projects/" + PROJECT_ID + "/locations/" + LOCATION + "/reasoningEngines/" + REASONING_ENGINE_ID + ":query";
  
  var payload = {
    "input": {
      "input": queryText
    }
  };
  
  var options = {
    "method": "post",
    "contentType": "application/json",
    "payload": JSON.stringify(payload),
    "headers": {
      "Authorization": "Bearer " + ScriptApp.getOAuthToken()
    },
    "muteHttpExceptions": true
  };
  
  var response = UrlFetchApp.fetch(url, options);
  var responseText = response.getContentText();
  console.log("Agent response status: " + response.getResponseCode());
  console.log("Agent response text: " + responseText);
  
  if (response.getResponseCode() == 200) {
    var result = JSON.parse(responseText);
    // Adjust this path based on the actual output structure of your agent
    return result.output || responseText; 
  } else {
    return "Error calling agent: " + responseText;
  }
}

function onMessage(event) {
  const version = "AGENT_V1 (Real Agent Call)";
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
  
  // Call the agent instead of hardcoded branches
  console.log("Querying agent...");
  var responseText = queryReasoningEngine(text);
  
  // Real agent thinking, no need to simulate delay
  
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
