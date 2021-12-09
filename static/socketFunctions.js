var socket = io();

clickerBtn = document.getElementById("clickerBtn");
clickerBtn.addEventListener("click", () => {
  sendCountToServer(clickerBtn.innerText);
});

const sendCountToServer = (count) => {
  if (count == "Click") {
    count = 0;
  }
  socket.emit("serverIncrement", count);
};

const addOnlineUsers = (onlyUsernames) => {
  // console.log(onlyUsernames);

  userUl = document.getElementById("userList");
  arr = Array.from(userUl.children);
  currentUsernames = [];
  for (child of arr) {
    currentUsernames.push(child.innerText);
  }
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
      console.log("current user: " + listUser.innerText);
      if (listUser.innerText == username) {
        indexToRemove = arr.indexOf(listUser);
        console.log("index to remove: " + indexToRemove);
      }
    }
    userUl.removeChild(arr[indexToRemove]);
  }
});
