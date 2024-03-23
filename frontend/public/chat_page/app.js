const startBtn = document.getElementById("startBtn");
const stopBtn = document.getElementById("stopBtn");
const resetBtn = document.getElementById("resetBtn");
const chatMessages = document.getElementById("chatMessages");
const initialMessage = document.getElementById("initialMessage");
const textInput = document.getElementById("textInput");
const sendTextBtn = document.getElementById("sendTextBtn");
const newBtn = document.getElementById("newBtn");
const outerBtn = document.getElementById("outerBtn");

let mediaRecorder;
let chunks = [];

const userId = localStorage.getItem("userId") || generateUserId();
localStorage.setItem("userId", userId);

function generateUserId() {
  return Math.random().toString(36);
}

async function checkChat() {
  try {
    const response = await fetch("http://localhost:8000/get_conversation", {
      method: "GET",
      headers: { userId: userId },
    });

    if (!response.ok) {
      throw new Error("Error sending audio to server");
    }

    const data = await response.json();
    if (data["chat_history"]) {
      let arr = data["chat_history"];
      chatMessages.innerHTML = "";

      for (let i = 1; i < arr.length; i += 1) {
        const message = document.createElement("div");
        if (i % 2 === 1) {
          message.classList.add("user-message");
        } else {
          message.classList.add("gpt-message");
        }
        message.textContent = arr[i]["content"].trim();
        chatMessages.appendChild(message);
      }

      chatMessages.scrollTop = chatMessages.scrollHeight; // Scroll to the bottom
      resetBtn.disabled = false;
    }
  } catch (error) {
    console.error("Error:", error);
  }
}

checkChat();

async function getAudioFromServer(prompt) {
  try {
    const response = await fetch("http://localhost:8000/get_audio", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: prompt }),
    });

    if (response.ok) {
      const audioBlob = await response.blob();
      const audioUrl = URL.createObjectURL(audioBlob);

      const gptMessage = document.createElement("div");
      gptMessage.classList.add("audio-message");

      const audioElement = document.createElement("audio");
      audioElement.src = audioUrl;
      audioElement.controls = true;

      gptMessage.appendChild(audioElement);
      chatMessages.appendChild(gptMessage);
    } else {
      console.error("Error fetching audio:", response.status);
    }
  } catch (error) {
    console.error("Error:", error);
  }
}

async function sendTextEvent(text) {
  try {
    const userMessage = document.createElement("div");
    userMessage.classList.add("user-message");
    userMessage.textContent = text;
    chatMessages.appendChild(userMessage);

    const response = await fetch("http://localhost:8000/text_prompt", {
      method: "POST",
      headers: { userId: userId, "Content-Type": "application/json" },
      body: JSON.stringify({ text: text }),
    });

    if (!response.ok) {
      throw new Error("Error sending text prompt");
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let receivedData = "";

    const gptMessage = document.createElement("div");
    gptMessage.classList.add("gpt-message");
    chatMessages.appendChild(gptMessage);

    while (true) {
      const { value, done } = await reader.read();

      if (done) {
        break;
      }

      let isFirstChunk = true;

      const chunk = decoder.decode(value, { stream: true });
      if (isFirstChunk) {
        receivedData += chunk;
        isFirstChunk = false;
      } else {
        receivedData += chunk;
      }
      console.log(chunk);
      gptMessage.textContent = receivedData;
      chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    console.log(receivedData);
    getAudioFromServer(receivedData);

    console.log("Text sent successfully");
  } catch (error) {
    console.error("Error:", error);
  }
}

async function sendAudioToServer(audioBlob) {
  const formData = new FormData();
  formData.append("audio", audioBlob, "recording.mp3");

  try {
    const response = await fetch("http://localhost:8000/audio_prompt", {
      method: "POST",
      body: formData,
      headers: { userId: userId },
    });

    if (!response.ok) {
      throw new Error("Error sending audio to server");
    }

    const data = await response.json();
    const txt = data["text"];
    sendTextEvent(txt);

    console.log("Audio sent successfully");
  } catch (error) {
    console.error("Error:", error);
  }
}

newBtn.addEventListener("click", async () => {
  if (!mediaRecorder) {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorder = new MediaRecorder(stream);

      mediaRecorder.addEventListener("dataavailable", (event) => {
        chunks.push(event.data);
      });

      mediaRecorder.addEventListener("stop", () => {
        const audioBlob = new Blob(chunks, { type: "audio/mp3" });
        chunks = [];
        sendAudioToServer(audioBlob);
        mediaRecorder = null;
        newBtn.style.backgroundImage = 'url("chat_page/static/mic.png")';
        newBtn.classList.remove("Rec");
        outerBtn.classList.remove("Rec-outer");
        newBtn.title = "Start recording";
        outerBtn.title = "Start recording";
      });

      mediaRecorder.start();
      newBtn.style.backgroundImage = 'url("chat_page/static/mic_red.png")';
      newBtn.classList.add("Rec");
      outerBtn.classList.add("Rec-outer");
      newBtn.title = "Stop recording";
      outerBtn.title = "Stop recording";
    } catch (error) {
      console.error("Error accessing microphone:", error);
    }
  } else {
    if (mediaRecorder && mediaRecorder.state !== "inactive") {
      mediaRecorder.stop();
    }
  }
});

document.addEventListener("keydown", (event) => {
  if (event.code === "Space" && document.activeElement !== textInput) {
    newBtn.click();
  }
});

async function resetEvent() {
  try {
    const response = await fetch("http://localhost:8000/reset_conversation", {
      method: "DELETE",
      headers: { userId: userId },
    });

    if (!response.ok) {
      throw new Error("Error resetting conversation");
    }

    chatMessages.innerHTML = "";
    resetBtn.disabled = true;
  } catch (error) {
    console.error("Error:", error);
  }
}

let sendTextBtnFlag = false;

resetBtn.addEventListener("click", async () => {
  resetEvent();
  sendTextBtn.style.transform = "rotate(0deg)";
  sendTextBtnFlag = false;
  textInput.value = "";
});

textInput.addEventListener("input", () => {
  if (textInput.value.trim()) {
    if (!sendTextBtnFlag) {
      sendTextBtn.style.transform =
        "rotate(-90deg) translateY(3px) translateX(-5px)";
      sendTextBtnFlag = true;
    }
  }
  if (!textInput.value.trim()) {
    if (sendTextBtnFlag) {
      sendTextBtn.style.transform = "rotate(0deg)";
      sendTextBtnFlag = false;
    }
  }
});

textInput.addEventListener("keydown", (event) => {
  if (event.shiftKey && event.key === "Enter") {
    event.preventDefault();
    textInput.value = textInput.value + "\n";
  } else if (event.key === "Enter") {
    event.preventDefault();
    sendTextBtn.click();
  }
});

sendTextBtn.addEventListener("click", async () => {
  if (textInput.value.trim()) {
    const txt = textInput.value.trim();
    sendTextEvent(txt);
    textInput.value = "";
    sendTextBtn.style.transform = "rotate(0deg)";
    sendTextBtnFlag = false;
    resetBtn.disabled = false;
  }
});

outerBtn.addEventListener("click", async () => {
  newBtn.click();
});

document.addEventListener("keydown", handleKeyDown);

function handleKeyDown(event) {
  if (event.ctrlKey && event.key === "q") {
    const audioMessages = document.querySelectorAll(".audio-message");
    const lastAudioMessage = audioMessages[audioMessages.length - 1];
    const audioElement = lastAudioMessage.querySelector("audio");
    if (audioElement) {
      audioElement.currentTime = 0;
      audioElement.play();
    }
  }
}
