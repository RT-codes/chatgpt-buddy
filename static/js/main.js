// when the page is fully loaded
$(window).on("load", function() {
  // showResponseMessage();

  // add event listener to the "#chat-input-form" form and prevent default behavior and make it start a function on submit
  $("#chat-input-form").on("submit", chatSubmitHandler);

  // go to the right conversation when clicking on a conversation in the conversation list
  $(".go-to-conv").on("click", function() {
    var conversationId = $(this).data("conv-id");

    // sent a POST request to the server
    $.ajax({
      url: "/conversation/" + conversationId,
      method: "POST",
      success: function(response) {
        // reload the page
        // location.reload();
        // goto the url of "/conversation/" + conversationId
        window.location.href = "/conversation/" + conversationId;
      },
    });
  });

  const conversationContainer = $("#conversation-container");

  if (conversationContainer != undefined) {
    // check if there is a conversation history in the conversation container by checking all if the children of the conversation container have the class "conv-block"
    if (conversationContainer.children(".conv-block").length < 1) {
      // if there is no conversation history in the conversation container, call the checkForHistory function and pass in the conversation id
      checkForHistory(conversationContainer.data("conv-id"));
      setActiveResponse();
      scrollToBottom(conversationContainer);
    }
  }

  // conversation functions

  $("#start-new-conversation").on("click", function() {
    const selectedFormula = document.querySelector("#selectedOption").innerHTML;

    if (selectedFormula == undefined) {
      console.log("cannot find selected formula");
      return;
    }

    const data = {
      formula: selectedFormula,
    };

    $.ajax({
      url: "/new-conversation",
      method: "POST",
      data: data,
      success: function(response) {
        //reload the page
        // location.reload();
        // goto the url of "/"
        window.location.href = "/";

        // wait for 2 seconds and then call the checkForHistory function
        checkForHistory();
      },
    });

    console.log("new conversation started");
  });
});

function checkForHistory() {
  // checks if there is a conversation history in the conversation container
  // if there is a history in the conversation that is currently open, it will be added to the conversation container
  console.log("checking for history");
  // clear the conversation-container of all conversation blocks
  var conversationContainerBlock = [];
  var conversationContainer = $("#conversation-container");
  conversationContainer.children(".conv-block").each(function() {
    conversationContainerBlock.push($(this));
  });
  conversationContainerBlock.forEach(function(block) {
    block.remove();
  });
  var convId = $("#conversation-container").data("conv-id");
  if (convId == undefined) {
    return;
  }
  // convert convId to string
  convId = convId.toString();
  console.log(convId);
  $.ajax({
    url: "/gethistory",
    method: "POST",
    data: {
      conversationId: convId,
    },
    success: function(response) {
      console.log("history retrieved");
      console.log(response);
      // take the response object and give it to the buildHistory function
      buildHistory(response);
    },
  });
  if (conversationContainer != undefined) {
    setActiveResponse();
  }
}

function toggleBouncerWithHiddenClass() {
  console.log("toggling bouncer");
  // toggles the bouncer with the .bouncer-hidden class
  var bouncer = $("#bouncer");
  console.log(bouncer);
  // if the bouncer has the .bouncer-hidden class, remove it
  if (bouncer.hasClass("bouncer-hidden")) {
    bouncer.removeClass("bouncer-hidden");
    // if the bouncer doesn't have the .bouncer-hidden class, add it
  } else {
    bouncer.addClass("bouncer-hidden");
  }
}

function chatSubmitHandler(event) {
  // no page reload
  event.preventDefault();

  // grab the user message from the input field
  const userMessage = $("#message-input").val();
  const conversationId = $("#conversation-container").data("conv-id");
  sendDefaultMessage(userMessage, conversationId);
  toggleBouncerWithHiddenClass();
}

function sendDefaultMessage(userMessage, conversationId = None) {
  // sends a default message to the server with an AJAX POST request
  // get the element with the .bouncer class and add the .bouncer-active class to it
  var waitingForResponse = true;

  $.ajax({
    url: "/send_message",
    method: "POST",
    data: {
      message: userMessage,
      conversationId: conversationId,
    },
    success: function(response) {
      toggleBouncerWithHiddenClass();
      waitingForResponse = false;
      // convert the response json string to a javascript object
      checkForHistory(conversationId);
      var responseObj = JSON.parse(response);
      console.log(response);
      console.log(responseObj);
    },
  });

  // wait for 4 seconds and then call the slowServer function

  setTimeout(function() {
    // this function will be called after 4 seconds
    if (waitingForResponse) {
      console.log("Server is slow or overloaded");
    }
  }, 4000);
}

function buildNewConversation() {
  //adds a new empty conversation to the conversation container
}

function buildHistory(responseObj) {
  //adds the conversation history to the conversation container with passed in data
  //loops through the responseObj.history list and calls the addNewUserMessage and addNewResponse functions

  for (var i = 0; i < responseObj.history.length; i++) {
    var conversationContainer = $("#conversation-container");
    var message = responseObj.history[i]["message"];
    var response = responseObj.history[i]["response"];
    if (!message.startsWith("[formula]")) {
      var messageBlock = addNewUserMessage(message);
      var responseBlock = addNewResponse(response);
      // if message doesnt start with "[formula]" then

      conversationContainer.append(messageBlock);
      conversationContainer.append(responseBlock);
    }
  }
  if (conversationContainer != undefined || conversationContainer != null) {
    setActiveResponse();
  }
  scrollToBottom(conversationContainer);
}

function messageAddCodeBlock(messageIn) {
  //go trough each line of the message and add a code block if the line contains a '```'
  //split the message into an array of lines
  var messageInArray = messageIn.split("\n");
  var messageOut = "";
  //loop through the array of lines
  for (var i = 0; i < messageInArray.length; i++) {
    //check if the line contains a '```'
    //then add a <code> tag to the line instead of the '```'
    // but if there was already a <code> tag in one of the previous lines, close the <code> tag with a </code> tag this time
    if (messageInArray[i].includes("```")) {
      if (messageInArray[i].includes("<code>")) {
        messageInArray[i] = messageInArray[i].replace("```", "</code>");
      } else {
        messageInArray[i] = messageInArray[i].replace("```", "<code>");
      }
    }
    //add a new line to the message
    messageOut += messageInArray[i] + "\n";
  }
  //return the message
  return messageOut;
}

function formatCodeBlocks(message) {
  const lines = message.split("\n");
  let codeBlockOpen = false;
  let formattedMessage = "";

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];

    if (line.trim() === "```") {
      codeBlockOpen = !codeBlockOpen;
      if (codeBlockOpen) {
        formattedMessage += "<code>";
      } else {
        formattedMessage += "</code>";
      }
    } else {
      if (codeBlockOpen) {
        formattedMessage += line;
      } else {
        formattedMessage += `<p>${line}</p>`;
      }
    }
  }

  // If the last line was part of a code block, make sure to close the block.
  if (codeBlockOpen) {
    formattedMessage += "</code>";
  }

  return formattedMessage;
}

function addNewUserMessage(message) {
  // message = formatCodeBlocks(message);

  message = marked.parse(message);
  //adds a new user message to the conversation container
  var messageEl = document.createElement("div");
  messageEl.classList.add("conv-block");
  messageEl.classList.add("not-show");
  // responseEl.classList.add("not-show");
  var messageTextEl = document.createElement("div");
  messageTextEl.classList.add("user-msg");
  messageTextEl.innerHTML = "<p>" + formatString(message) + "</p>";
  messageEl.appendChild(messageTextEl);
  var userIconEl = document.createElement("div");
  userIconEl.classList.add("icon-user");
  messageEl.appendChild(userIconEl);
  return messageEl;
}

function addNewResponse(message) {
  // message = formatCodeBlocks(message);
  message = marked.parse(message);
  //adds a new response to the conversation container
  var responseEl = document.createElement("div");
  responseEl.classList.add("conv-block");
  responseEl.classList.add("not-show");
  // responseEl.classList.add("not-show");
  var responseTextEl = document.createElement("div");
  responseTextEl.classList.add("bot-msg");
  responseTextEl.innerHTML = "<p>" + formatString(message) + "</p>";
  responseEl.appendChild(responseTextEl);
  var botIconEl = document.createElement("div");
  botIconEl.classList.add("icon-bot");
  responseEl.appendChild(botIconEl);
  return responseEl;
}

// utility functions

function formatString(string) {
  var formattedString = "";
  for (var i = 0; i < string.length; i++) {
    if (string[i] == " ") {
      formattedString += "&nbsp;";
    } else {
      formattedString += string[i];
    }
  }
  return formattedString;
}

// when window is ready
$(window).ready(function() {
  const parentContainer = document.querySelector(".bg-image-container");
  const scrollingImage = document.querySelector(".conversation-container-background");

  if (parentContainer && scrollingImage) {
    parentContainer.addEventListener("scroll", () => {
      const scrollTop = parentContainer.scrollTop;
      const containerHeight = parentContainer.clientHeight;
      const imageHeight = scrollingImage.clientHeight;
      const speed = 0.3;

      const maxScrollTop = imageHeight - containerHeight;
      const scrollFraction = scrollTop / maxScrollTop;

      const scalingSpeed = 0.33 + 0.67 * scrollFraction * speed; /* calculate the scaling factor based on the scroll position */
      // scrollingImage.style.transform = `scale(${scalingFactor})`;

      // the max scroll distance is the height of the image minus the height of the container
      var maxScrollDistance = imageHeight - containerHeight;

      scrollingImage.style.transform = `translateY(-${(scrollTop * scalingSpeed) / 12 + 400}px)`;
    });
  }

  // wait for half a second
  var convBlocks = document.querySelectorAll(".conv-block");
  console.log(convBlocks);
  convBlocks.forEach((el) => observer.observe(el));

  // observer for elements with .conv-block class
  var observer = new IntersectionObserver(function(entries) {
    entries.forEach(function(entry) {
      if (entry.isIntersecting) {
        entry.target.classList.add("show");
      } else {
        entry.target.classList.remove("show");
      }
    });
  });

  //get the formulas from the server
  getFormulas();

  // check if there is any history
  // check if there is a conversation container
  var conversationContainer = document.getElementById("conversation-container");
  if (conversationContainer != undefined || conversationContainer != null) {
    // check if there is any history
    checkForHistory();

    // scroll to the bottom of the conversation container
    // wait 1 second to scroll to the bottom
    setTimeout(function() {
      scrollToBottom();
    }, 300);

    setTimeout(function() {
      setActiveResponse();
    }, 200);
  }
});

function setActiveResponse() {
  const conversationContainer = document.getElementById("conversation-container");
  if (conversationContainer == undefined || conversationContainer == null) {
    return;
  }
  if (conversationContainer.children.length == 0) {
    return;
  }

  // get the latest child with the class bot-msg
  // const conversationContainer = conversationContainer;

  // remove the active-response class from all the children
  for (var j = 0; j < conversationContainer.children.length; j++) {
    // check if the child has the class active-response
    if (conversationContainer.children[j].classList.contains("active-response")) {
      conversationContainer.children[j].classList.remove("active-response");
    }
  }

  // get the latest child of the conversation container with class conv-block
  var latestResponse = conversationContainer.lastElementChild;
  console.log(latestResponse);
  // now we add the active-response class to the latest response
  latestResponse.classList.add("active-response");
}

function scrollToBottom(scollElement) {
  const element = scollElement;
  if (element == undefined || element == null) {
    return;
  }
  element.scrollTop = element.scrollHeight;
}

function getFormulas() {
  console.log("getting formulas");
  // sends a ajax request to the server to get the formulas
  $.ajax({
    url: "/formulas/getformulas",
    method: "POST",
    success: function(response) {
      // convert the response json string to a javascript object
      // var responseObj = JSON.parse(response);
      console.log(response);
    },
  });
}
// def add_formula(self, id: int, title: str, description: str, timestamp: str, json_object: dict)
// generate a timestamp
function generateFormula(title = "", description = "") {
  var timestamp = new Date().getTime();
  formula = {
    title: title,
    description: description,
    timestamp: timestamp,
  };
}

function addFormula(formula) {
  // adds a formula to the formula container
  var formulaContainer = document.querySelector(".formula-container");
  var formulaEl = document.createElement("div");
  formulaEl.classList.add("formula");
  formulaEl.innerHTML = formula;
  formulaContainer.appendChild(formulaEl);
}
