const startBtn = document.getElementById("startBtn");
const stopBtn = document.getElementById("stopBtn");
const resetBtn = document.getElementById("resetBtn");
const chatMessages = document.getElementById("chatMessages");
const initialMessage = document.getElementById("initialMessage");
const textInput = document.getElementById("textInput");
const sendTextBtn = document.getElementById("sendTextBtn");
const newBtn = document.getElementById("newBtn");

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

async function sendTextEvent(text) {
  try {
    // const text = textInput.value.trim();

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

    const data = await response.json();

    const gptMessage = document.createElement("div");
    gptMessage.classList.add("gpt-message");
    gptMessage.textContent = data["GPTResponse"].trim();
    chatMessages.appendChild(gptMessage);

    chatMessages.scrollTop = chatMessages.scrollHeight;

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


newBtn.addEventListener('click', async () => {
  if (!mediaRecorder) {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorder = new MediaRecorder(stream);

      mediaRecorder.addEventListener('dataavailable', (event) => {
        chunks.push(event.data);
      });

      mediaRecorder.addEventListener('stop', () => {
        const audioBlob = new Blob(chunks, { type: 'audio/mp3' });
        chunks = [];
        sendAudioToServer(audioBlob);
        mediaRecorder = null;
        newBtn.style.backgroundImage = 'url("static/mic.png")';
        newBtn.classList.remove('Rec');
        newBtn.title = "Start recording";
      });

      mediaRecorder.start();
      newBtn.style.backgroundImage = 'url("static/mic_red.png")';
      newBtn.classList.add('Rec');
      newBtn.title = "Stop recording";
    } catch (error) {
      console.error('Error accessing microphone:', error);
    }
  } else {
    if (mediaRecorder && mediaRecorder.state !== 'inactive') {
      mediaRecorder.stop();
    }
  }
});


document.addEventListener('keydown', (event) => {
  if (event.code === 'Space') {
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
    textInput.value = textInput.value + '\n';
  }
  else if (event.key === "Enter") {
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
