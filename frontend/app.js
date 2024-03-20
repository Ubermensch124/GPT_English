// app.js
const startBtn = document.getElementById('startBtn');
const stopBtn = document.getElementById('stopBtn');
const resetBtn = document.getElementById('resetBtn');
const textOutput = document.getElementById('textOutput');
let mediaRecorder;
let chunks = [];

const userId = localStorage.getItem('userId') || generateUserId();
localStorage.setItem('userId', userId);

function generateUserId() {
    return Math.random().toString(36);
}

// Helper function to send the recorded audio to the FastAPI endpoint
async function sendAudioToServer(audioBlob) {
  const formData = new FormData();
  formData.append('audio', audioBlob, 'recording.mp3');

  try {
    const response = await fetch('http://localhost:8000/get_audio', {
      method: 'POST',
      body: formData,
      headers: {
        'userId': userId // Include user identifier in the request headers
          }
    //   credentials: 'include' // Send cookies with the request
    });

    if (!response.ok) {
      throw new Error('Error sending audio to server');
    }

    const data = await response.json();
    textOutput.value = data["response"];
      
    console.log('Audio sent successfully');
      
  } catch (error) {
    console.error('Error:', error);
  }
}

// Start recording
startBtn.addEventListener('click', async () => {
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
    });

    mediaRecorder.start();
    startBtn.disabled = true;
    stopBtn.disabled = false;
  } catch (error) {
    console.error('Error accessing microphone:', error);
  }
});

// Stop recording
stopBtn.addEventListener('click', () => {
  if (mediaRecorder && mediaRecorder.state !== 'inactive') {
    mediaRecorder.stop();
    startBtn.disabled = false;
    stopBtn.disabled = true;
  }
});

// Reset Conversation
resetBtn.addEventListener('click', async () => {
    try {
        const response = await fetch('http://localhost:8000/reset_conversation', {
          method: 'DELETE',
          headers: {
                'userId': userId // Include user identifier in the request headers
                  }
        });
    
        if (!response.ok) {
          throw new Error('Error resetting conversation');
        }
    
        console.log('Conversation reset successfully');
        textOutput.value = '';

      } catch (error) {
        console.error('Error:', error);
      }
  });