const messagesDiv = document.getElementById("messages");
const messageInput = document.getElementById("message-input");
const statusDiv = document.getElementById("status");
const loginScreen = document.getElementById("login-screen");
const chatContainer = document.getElementById("chat-container");
const usernameInput = document.getElementById("username-input");
const pinnedMessagesContainer = document.getElementById("pinned-messages");
let ws;
let username = "";

function setUsername() {
  const newUsername = usernameInput.value.trim();
  if (newUsername) {
    username = newUsername;
    loginScreen.classList.add("hidden");
    chatContainer.classList.remove("hidden");
    connect();
  }
}

usernameInput.addEventListener("keypress", function (e) {
  if (e.key === "Enter") {
    setUsername();
  }
});

function connect() {
  ws = new WebSocket("ws://" + location.host + "/ws");

  ws.onopen = function () {
    statusDiv.textContent = "Connected";
    statusDiv.style.color = "green";
    // Send username to server
    ws.send(
      JSON.stringify({
        type: "join",
        username: username,
      })
    );
  };

  ws.onclose = function () {
    statusDiv.textContent = "Disconnected - Reconnecting...";
    statusDiv.style.color = "red";
    setTimeout(connect, 1000);
  };

  function updateUserList(users) {
    const userListElement = document.getElementById("user-list");
    userListElement.innerHTML = "";

    for (let i = 0; i < users.length; i++) {
      const user = users[i];
      const userElement = document.createElement("li");
      userElement.textContent = user;
      userListElement.appendChild(userElement);
    }
  }

  ws.onmessage = function (event) {
    const message = JSON.parse(event.data);
    const messageElement = document.createElement("div");
    const currentTime = new Date().toLocaleTimeString();

    if (message.type === "system") {
      messageElement.className = "message-system";
      messageElement.textContent = `[${currentTime}] ${message.text}`;
    } else if (message.type === "message") {
      const userSpan = document.createElement("span");
      userSpan.className = "message-user";
      userSpan.textContent = message.username + ": ";

      const timestamp = document.createElement("span");
      timestamp.className = "message-time";
      timestamp.textContent = `[${currentTime}]`;

      //Format of Chat Message
      //[10:56:03 PM] A: Some Text
      messageElement.appendChild(timestamp);
      messageElement.appendChild(document.createTextNode(" "));
      messageElement.appendChild(userSpan);
      messageElement.appendChild(document.createTextNode(message.text));
      messageElement.classList.add("chat-message");

      //right clicking pins message
      messageElement.addEventListener("contextmenu", function (e) {
        e.preventDefault();
        pinMessage(message.username, message.text);
      });
    } else if (message.type === "user_list") {
      updateUserList(message.users);
      return;
    } else if (message.type === "pinned_message") {
      const pinnedElement = document.createElement("div");
      pinnedElement.classList.add("pinned-message");
      pinnedElement.textContent = message.username + ": " + message.text;

      pinnedMessagesContainer.appendChild(pinnedElement);
      return;
    } else if (message.type === "unpin_message") {
      const pinnedMessages = document.querySelectorAll(".pinned-message");
      for (let i = 0; i < pinnedMessages.length; i++) {
        const pinnedMessage = pinnedMessages[i];

        if (pinnedMessage.textContent === message.text) {
          pinnedMessagesContainer.removeChild(pinnedMessage);
        }
      }
      return;
    }

    messagesDiv.appendChild(messageElement);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
  };
}
//right clicking pinned message, unpins them
pinnedMessagesContainer.addEventListener("contextmenu", function (e) {
  e.preventDefault();
  const targetMessage = e.target;

  if (targetMessage && targetMessage.classList.contains("pinned-message")) {
    unpinMessage(targetMessage.textContent);
  }
});

function sendMessage() {
  const text = messageInput.value.trim();
  if (text && ws.readyState === WebSocket.OPEN) {
    const currentTime = new Date().toLocaleTimeString();
    ws.send(
      JSON.stringify({
        type: "message",
        text: text,
        username: username,
        timestamp: currentTime,
      })
    );
    messageInput.value = "";
  }
}

messageInput.addEventListener("keypress", function (e) {
  if (e.key === "Enter") {
    sendMessage();
  }
});

function pinMessage(username, text) {
  const pinnedMessage = {
    type: "pin_message",
    username: username,
    text: text,
  };

  ws.send(JSON.stringify(pinnedMessage));
}

function unpinMessage(text) {
  const unpinMessage = {
    type: "unpin_message",
    text: text,
  };

  ws.send(JSON.stringify(unpinMessage));
}
