function queryReasoningEngine(queryText, sessionId) {
  const PROJECT_ID = "demo4events10";
  const LOCATION = "us-central1";
  const REASONING_ENGINE_ID = "5328541761214087168";
  
  // ADK agents require the streamQuery endpoint
  var url = "https://" + LOCATION + "-aiplatform.googleapis.com/v1/projects/" + PROJECT_ID + "/locations/" + LOCATION + "/reasoningEngines/" + REASONING_ENGINE_ID + ":streamQuery?alt=sse";
  
  var payload = {
    "class_method": "async_stream_query",
    "input": {
      "message": queryText,
      "user_id": "gartner_demo_user" // Mandatory for ADK agents
    }
  };
  
  if (sessionId) {
    payload.input.session_id = sessionId;
  }
  
  console.log("Sending payload to ADK agent:", JSON.stringify(payload));
  
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
  console.log("Raw response text: " + responseText);
  
  if (response.getResponseCode() == 200) {
    var lines = responseText.split("\n");
    var thinkingResponse = "";
    var finalResponse = "";
    
    for (var i = 0; i < lines.length; i++) {
      var line = lines[i].trim();
      if (!line) continue;
      
      try {
        var dataObj = JSON.parse(line);
        if (dataObj.content && dataObj.content.parts && dataObj.content.parts[0] && dataObj.content.parts[0].text) {
          var text = dataObj.content.parts[0].text;
          
          if (dataObj.content.parts[0].thought === true) {
            thinkingResponse += "* " + text.trim() + "\n";
          } else {
            finalResponse += text;
          }
        }
      } catch (e) {
        // Line might not be valid JSON, ignore
      }
    }
    
    var formattedFinalResponse = convertTableToText(finalResponse);
    
    var combinedResponse = "";
    if (thinkingResponse) {
      combinedResponse += "*Thinking:*\n" + thinkingResponse + "\n";
    }
    if (formattedFinalResponse) {
      combinedResponse += "*Final response:*\n" + formattedFinalResponse;
    }
    
    // Convert markdown links [Text](URL) to Google Chat format <URL|Text>
    combinedResponse = combinedResponse.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<$2|$1>');
    
    console.log("Full parsed response from stream: " + combinedResponse);
    return combinedResponse || "No text content returned from stream.";
  } else {
    return "Error calling agent: " + responseText;
  }
}

function createSession() {
  const PROJECT_ID = "demo4events10";
  const LOCATION = "us-central1";
  const REASONING_ENGINE_ID = "5328541761214087168";
  
  var url = "https://" + LOCATION + "-aiplatform.googleapis.com/v1/projects/" + PROJECT_ID + "/locations/" + LOCATION + "/reasoningEngines/" + REASONING_ENGINE_ID + ":query";
  
  var payload = {
    "class_method": "create_session",
    "input": {
      "user_id": "gartner_demo_user"
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
  console.log("Create session status: " + response.getResponseCode());
  console.log("Create session text: " + response.getContentText());
  
  if (response.getResponseCode() == 200) {
    var result = JSON.parse(response.getContentText());
    if (result.output && result.output.id) {
      return result.output.id;
    }
    return result.session_id || null;
  }
  return null;
}

function convertTableToText(text) {
  var lines = text.split("\n");
  var result = "";
  var headers = [];
  var inTable = false;
  
  for (var i = 0; i < lines.length; i++) {
    var line = lines[i].trim();
    if (line.startsWith("|")) {
      if (line.includes("---|")) continue; // Skip separator
      
      var parts = line.split("|").map(p => p.trim()).filter(p => p !== "");
      
      if (parts.length === 2) {
        // Handle vertical key-value table (2 columns)
        var label = parts[0].replace(/\*\*/g, ""); // Remove bold markdown
        var value = parts[1];
        result += "*" + label + ":* " + value + "\n";
      } else {
        // Handle horizontal multi-column table
        if (!inTable) {
          headers = parts;
          inTable = true;
          result += "*Applications Table:*\n";
        } else {
          var rowText = "";
          for (var j = 0; j < parts.length; j++) {
            var header = headers[j] || "Col " + (j+1);
            header = header.replace(/\*\*/g, "");
            rowText += "*" + header + ":* " + parts[j] + " | ";
          }
          if (rowText.endsWith(" | ")) {
            rowText = rowText.substring(0, rowText.length - 3);
          }
          result += rowText + "\n";
        }
      }
    } else {
      if (inTable) {
        result += "\n"; // Add newline after table
        inTable = false;
        headers = [];
      }
      result += lines[i] + "\n";
    }
  }
  return result;
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
  console.log("Checking session...");
  var userProperties = PropertiesService.getUserProperties();
  var sessionId = userProperties.getProperty('sessionId_v2');
  
  if (!sessionId) {
    console.log("No session found, creating new session...");
    sessionId = createSession();
    if (sessionId) {
      userProperties.setProperty('sessionId_v2', sessionId);
      console.log("New session saved: " + sessionId);
    }
  } else {
    console.log("Using existing session: " + sessionId);
  }
  
  console.log("Querying agent...");
  var responseText = queryReasoningEngine(text, sessionId);
  
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
