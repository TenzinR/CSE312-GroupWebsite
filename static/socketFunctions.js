var socket = io();

currentUser = document.getElementById("currentUser").innerText;

clickerBtn = document.getElementById("clickerBtn");
clickerBtn.addEventListener("click", () => {
  sendCountToServer(clickerBtn.innerText);
});

messageBoard = document.getElementById("messageBoard");

messageForm = document.getElementById("messageForm");
messageForm.addEventListener("submit", (e) => {
  sendMessage(e);
});

messageButton = document.getElementById("messageFormButton");
messageButton.addEventListener("click", () => {
  messageForm.removeAttribute("style");
  messageButton.setAttribute("style", "display: none;");
});

const sendMessage = (e) => {
  e.preventDefault();
  messageForm.setAttribute("style", "display:none;");
  messageButton.removeAttribute("style");
  let recipientUsername = messageForm.querySelector("#messageRecipient").value;
  let messageText = messageForm.querySelector("#messageText").value;
  let senderUsername = currentUser;
  messageForm.querySelector("#messageRecipient").value = "";
  messageForm.querySelector("#messageText").value = "";
  socket.emit("serverMessage", { senderUsername, recipientUsername, messageText });
};

const receiveMessage = (messageObj) => {
  let senderUsername = messageObj["senderUsername"];
  let recipientUsername = messageObj["recipientUsername"];
  let messageText = messageObj["messageText"];
  onlineUsers = getOnlineUsers();
  if (
    (currentUser == senderUsername && currentUser == recipientUsername) ||
    !(currentUser == senderUsername || currentUser == recipientUsername) ||
    onlineUsers.indexOf(senderUsername) == -1 ||
    onlineUsers.indexOf(recipientUsername) == -1
  ) {
    return;
  }
  conversation = document.createElement("ul");
  if (document.getElementsByClassName(senderUsername + recipientUsername).length != 0) {
    conversation = document.getElementsByClassName(senderUsername + recipientUsername)[0];
    console.log(senderUsername + recipientUsername);
    console.log("conversation: " + conversation);
  } else if (document.getElementsByClassName(recipientUsername + senderUsername).length != 0) {
    conversation = document.getElementsByClassName(recipientUsername + senderUsername)[0];
    console.log(recipientUsername + senderUsername);
    console.log("conversation: " + conversation);
  } else {
    console.log(senderUsername + recipientUsername);
    conversation.setAttribute("class", senderUsername + recipientUsername);
    messageBoard.appendChild(conversation);
  }
  console.log(conversation.innerHTML);

  li = document.createElement("li");
  li.innerText = `Message from ${senderUsername} to ${recipientUsername}: ${messageText}`;
  conversation.appendChild(li);
};

const getOnlineUsers = () => {
  userUl = document.getElementById("userList");
  arr = Array.from(userUl.children);
  onlineUsers = [];
  for (child of arr) {
    onlineUsers.push(child.innerText);
  }
  return onlineUsers;
};

const sendCountToServer = (count) => {
  if (count == "Click") {
    count = 0;
  }
  socket.emit("serverIncrement", count);
};

const addOnlineUsers = (onlyUsernames) => {
  // console.log(onlyUsernames);

  currentUsernames = getOnlineUsers();
  // console.log("current usernames: " + currentUsernames);
  // console.log("usernames to be added: " + onlyUsernames);
  if (currentUsernames.length > 0) {
    for (username of onlyUsernames) {
      li = document.createElement("li");
      li.innerText = username;

      if (!currentUsernames.includes(username)) {
        // console.log(username + " is new!");
        userUl.appendChild(li);
      }
    }
  } else {
    for (username of onlyUsernames) {
      li = document.createElement("li");
      li.innerText = username;
      userUl.appendChild(li);
    }
  }
};

socket.on("clientIncrement", (newCount) => {
  clickerBtn.innerText = newCount;
});

socket.on("clientMessage", (messageObj) => {
  receiveMessage(messageObj);
});
socket.on("addUserToList", (msg) => {
  addOnlineUsers(msg["onlyUsernames"]);
});

socket.on("removeUserFromList", (username) => {
  //console.log("username to remove: " + username);
  userUl = document.getElementById("userList");
  arr = Array.from(userUl.children);
  if (arr.length > 0) {
    indexToRemove = -1;
    for (listUser of arr) {
      // console.log("current user: " + listUser.innerText);
      if (listUser.innerText == username) {
        indexToRemove = arr.indexOf(listUser);
        // console.log("index to remove: " + indexToRemove);
      }
    }
    userUl.removeChild(arr[indexToRemove]);
  }
});
