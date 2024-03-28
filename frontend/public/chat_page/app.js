const newChatBtn = document.getElementById("newChatBtn");
const chatMessages = document.getElementById("chatMessages");
const textInput = document.getElementById("textInput");
const sendTextBtn = document.getElementById("sendTextBtn");
const smallMicBtn = document.getElementById("smallMicBtn");
const bigMicBtn = document.getElementById("bigMicBtn");

const settingsBtn = document.getElementById("settingsBtn");
const dropdownMenu = document.getElementById("dropdownMenu");
const closeSettingsBtn = document.getElementById("closeSettingsBtn");
const overlay = document.getElementById("overlay");

const assistan_voice_selector = document.getElementById("assistantVoiceSelect");
const llm_selector = document.getElementById("llmSelect");
const mother_lang_selector = document.getElementById("nativeLangSelect");
const foreign_lang_selector = document.getElementById("foreignLangSelect");

let mediaRecorder;
let chunks = [];

const userId = localStorage.getItem("userId") || Math.random().toString(36);
localStorage.setItem("userId", userId);

restoreChat();

// function playAudio(audioUrl) {
//   const audio = new Audio(audioUrl);
//   audio.play().catch((error) => {
//     console.error("Failed to play audio:", error);
//   });
// }


async function restoreChat() {
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
      let chat = data["chat_history"];
      chatMessages.innerHTML = "";

      for (let i = 1; i < chat.length; i += 1) {
        const message = document.createElement("div");
        if (i % 2 === 1) {
          message.classList.add("user-message");
        } else {
          message.classList.add("gpt-message");
        }
        // message.textContent = chat[i]["content"].trim();
        message.innerHTML = marked.parse(chat[i]["content"].trim());

        const paragraphs = message.querySelectorAll("p");
        const firstParagraph = paragraphs[0];
        const lastParagraph = paragraphs[paragraphs.length - 1];
        firstParagraph.style.marginBlockStart = "0em";
        lastParagraph.style.marginBlockEnd = "0em";

        // const audioButton = document.createElement("button");
        // audioButton.classList.add("audio-button");
        // audioButton.textContent = "🔊";
        // audioButton.addEventListener("click", () =>
        //   playAudio("C://Users//Mark//Desktop//GPT English//sample-9s.mp3")
        // );
        // message.appendChild(audioButton);

        chatMessages.appendChild(message);
      }

      chatMessages.scrollIntoView({
        behavior: "smooth",
        block: "end",
        inline: "start",
      });
      newChatBtn.disabled = false;
    }
  } catch (error) {
    console.error("Error:", error);
  }
}


/**
 * Receive text of GPT response and add audio to chat.
 * @param {string} prompt - Text response of GPT
 */
async function getAudioFromServer(prompt) {
  try {
    console.log(assistan_voice_selector.value);
    const response = await fetch("http://localhost:8000/get_audio", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        text: prompt,
        voice: assistan_voice_selector.selectedOptions[0].text,
      }),
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
      chatMessages.scrollIntoView({
        behavior: "smooth",
        block: "end",
        inline: "start",
      });
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
    // userMessage.textContent = text;
    userMessage.innerHTML = marked.parse(text.trim());
    const firstParagraph = userMessage.querySelector("p");
    firstParagraph.style.marginBlockStart = "0em";
    const paragraphs = userMessage.querySelectorAll("p");
    const lastParagraph = paragraphs[paragraphs.length - 1];
    lastParagraph.style.marginBlockEnd = "0em";
    chatMessages.appendChild(userMessage);
    chatMessages.scrollIntoView({
      behavior: "smooth",
      block: "end",
      inline: "start",
    });

    const response = await fetch("http://localhost:8000/text_prompt", {
      method: "POST",
      headers: { userId: userId, "Content-Type": "application/json" },
      body: JSON.stringify({
        text: text,
        llm: llm_selector.selectedOptions[0].text,
        native_lang: mother_lang_selector.selectedOptions[0].text,
        foreign_lang: foreign_lang_selector.selectedOptions[0].text,
      }),
    });

    if (!response.ok) {
      console.log(llm_selector.selectedOptions[0].text);
      console.log(mother_lang_selector.selectedOptions[0].text);
      console.log(foreign_lang_selector.selectedOptions[0].text);
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
      // gptMessage.textContent = receivedData;
      gptMessage.innerHTML = marked.parse(receivedData);
      const firstParagraph = gptMessage.querySelector("p");
      firstParagraph.style.marginBlockStart = "0em";
      const paragraphs = gptMessage.querySelectorAll("p");
      const lastParagraph = paragraphs[paragraphs.length - 1];
      lastParagraph.style.marginBlockEnd = "0em";
      chatMessages.scrollIntoView({
        behavior: "smooth",
        block: "end",
        inline: "start",
      });
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
    const response = await fetch("http://localhost:8000/audio_prompt_to_text", {
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

smallMicBtn.addEventListener("click", async () => {
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
        smallMicBtn.style.backgroundImage = 'url("chat_page/static/mic.png")';
        smallMicBtn.classList.remove("Rec");
        bigMicBtn.classList.remove("Rec-outer");
        smallMicBtn.title = "Start recording";
        bigMicBtn.title = "Start recording";
      });

      mediaRecorder.start();
      smallMicBtn.style.backgroundImage = 'url("chat_page/static/mic_red.png")';
      smallMicBtn.classList.add("Rec");
      bigMicBtn.classList.add("Rec-outer");
      smallMicBtn.title = "Stop recording";
      bigMicBtn.title = "Stop recording";
    } catch (error) {
      console.error("Error accessing microphone:", error);
    }
  } else {
    if (mediaRecorder && mediaRecorder.state !== "inactive") {
      mediaRecorder.stop();
    }
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
    newChatBtn.disabled = true;
  } catch (error) {
    console.error("Error:", error);
  }
}

let sendTextBtnFlag = false;

newChatBtn.addEventListener("click", async () => {
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
  } else if (event.key === "Escape") {
    event.target.blur();
  }
});

sendTextBtn.addEventListener("click", async () => {
  if (textInput.value.trim()) {
    const txt = textInput.value.trim();
    sendTextEvent(txt);
    textInput.value = "";
    sendTextBtn.style.transform = "rotate(0deg)";
    sendTextBtnFlag = false;
    newChatBtn.disabled = false;
  }
});

bigMicBtn.addEventListener("click", async () => {
  smallMicBtn.click();
});

document.addEventListener("keydown", handleKeyDown);

function handleKeyDown(event) {
  if (event.code === "Space" && document.activeElement !== textInput) {
    smallMicBtn.click();
  } else if (event.key === "/") {
    if (document.activeElement !== textInput) {
      event.preventDefault();
      textInput.focus();
    }
  } else if (event.ctrlKey && event.key === "q") {
    const audioMessages = document.querySelectorAll(".audio-message");
    const lastAudioMessage = audioMessages[audioMessages.length - 1];
    const audioElement = lastAudioMessage.querySelector("audio");
    if (audioElement) {
      audioElement.currentTime = 0;
      audioElement.play();
    }
  } else if (event.ctrlKey && event.key === "Tab") {
    const audioMessages = document.querySelectorAll(".audio-message");
    const lastAudioMessage = audioMessages[audioMessages.length - 1];
    const audioElement = lastAudioMessage.querySelector("audio");
    if (audioElement) {
      if (audioElement.paused) {
        audioElement.play();
      } else {
        audioElement.pause();
      }
    }
  }
}

settingsBtn.addEventListener("click", function () {
  dropdownMenu.style.display = "none" ? "block" : "none";
  overlay.style.display = "none" ? "block" : "none";
});

closeSettingsBtn.addEventListener("click", function () {
  dropdownMenu.style.display = "none";
  overlay.style.display = "none";
});

document.addEventListener("click", function (event) {
  const isClickInside = dropdownMenu.contains(event.target);
  const isClickOnSettingsBtn = event.target === settingsBtn;

  if (!isClickInside && !isClickOnSettingsBtn) {
    closeSettingsBtn.click();
  }
});
