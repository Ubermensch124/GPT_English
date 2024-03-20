const startBtn = document.getElementById("startBtn");
const stopBtn = document.getElementById("stopBtn");
const resetBtn = document.getElementById("resetBtn");
const UserOutput = document.getElementById("UserOutput");
const GPTOutput = document.getElementById("GPTOutput");

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
      let user_answer = arr[arr.length - 2]["content"];
      let gpt_answer = arr[arr.length - 1]["content"];
      UserOutput.value = user_answer;
      GPTOutput.value = gpt_answer;
      resetBtn.disabled = false;
    }
  } catch (error) {
    console.error("Error:", error);
  }
}

checkChat();

async function sendAudioToServer(audioBlob) {
  const formData = new FormData();
  formData.append("audio", audioBlob, "recording.mp3");

  try {
    const response = await fetch("http://localhost:8000/get_audio", {
      method: "POST",
      body: formData,
      headers: { userId: userId },
    });

    if (!response.ok) {
      throw new Error("Error sending audio to server");
    }

    const data = await response.json();
    UserOutput.value = data["UserPrompt"];
    GPTOutput.value = data["GPTResponse"];

    console.log("Audio sent successfully");
  } catch (error) {
    console.error("Error:", error);
  }
}

// Start recording
startBtn.addEventListener("click", async () => {
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
    });

    mediaRecorder.start();
    startBtn.disabled = true;
    stopBtn.disabled = false;
  } catch (error) {
    console.error("Error accessing microphone:", error);
  }
});

// Stop recording
stopBtn.addEventListener("click", () => {
  if (mediaRecorder && mediaRecorder.state !== "inactive") {
    mediaRecorder.stop();
    startBtn.disabled = false;
    stopBtn.disabled = true;
    resetBtn.disabled = false;
  }
});

// Reset Conversation
resetBtn.addEventListener("click", async () => {
  try {
    const response = await fetch("http://localhost:8000/reset_conversation", {
      method: "DELETE",
      headers: { userId: userId },
    });

    if (!response.ok) {
      throw new Error("Error resetting conversation");
    }

    GPTOutput.value = "";
    UserOutput.value = "";
    resetBtn.disabled = true;
  } catch (error) {
    console.error("Error:", error);
  }
});
