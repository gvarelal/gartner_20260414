const version = "AGENT_V5 (Workspace Add-on with Chat Push and Native Card Return)";

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
    
    var responseText = getAgentResponse(text);
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
    
    var responseText = getAgentResponse(text);
    
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

// Shared Agent Query Logic
function getAgentResponse(text) {
  if (!text || text.trim() === "") {
    return "Please provide a command.";
  }
  
  console.log("Checking session...");
  var userProperties = PropertiesService.getUserProperties();
  var sessionId = userProperties.getProperty('sessionId_v3');
  
  if (!sessionId) {
    console.log("No session found, creating new session...");
    sessionId = createSession();
    if (sessionId) {
      userProperties.setProperty('sessionId_v3', sessionId);
      console.log("New session saved: " + sessionId);
    }
  } else {
    console.log("Using existing session: " + sessionId);
  }
  
  console.log("Querying agent...");
  var responseText = queryReasoningEngine(text, sessionId);
  return responseText;
}

function queryReasoningEngine(queryText, sessionId) {
  const PROJECT_ID = "demo4events10";
  const LOCATION = "us-east1";
  const REASONING_ENGINE_ID = "9021624847297413120";
  
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
    if (thinkingResponse && thinkingResponse.trim() !== "") {
      combinedResponse += "*Thinking:*\n" + thinkingResponse + "\n";
      if (formattedFinalResponse) {
        combinedResponse += "*Final response:*\n" + formattedFinalResponse;
      }
    } else {
      if (formattedFinalResponse) {
        combinedResponse += formattedFinalResponse;
      }
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
  const LOCATION = "us-east1";
  const REASONING_ENGINE_ID = "9021624847297413120";
  
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

