const messagesDiv = document.getElementById("messages");
const messageInput = document.getElementById("message-input");
const statusDiv = document.getElementById("status");
const loginScreen = document.getElementById("login-screen");
const chatContainer = document.getElementById("chat-container");
const usernameInput = document.getElementById("username-input");
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

  ws.onmessage = function (event) {
    const message = JSON.parse(event.data);
    const messageElement = document.createElement("div");

    if (message.type === "system") {
      messageElement.className = "message-system";
      messageElement.textContent = message.text;
    } else {
      const userSpan = document.createElement("span");
      userSpan.className = "message-user";
      userSpan.textContent = message.username + ": ";

      messageElement.appendChild(userSpan);
      messageElement.appendChild(document.createTextNode(message.text));
    }

    messagesDiv.appendChild(messageElement);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
  };
}

function sendMessage() {
  const text = messageInput.value.trim();
  if (text && ws.readyState === WebSocket.OPEN) {
    ws.send(
      JSON.stringify({
        type: "message",
        text: text,
        username: username,
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
