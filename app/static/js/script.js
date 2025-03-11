// Check for SpeechRecognition API compatibility
const SpeechRecognition =
  window.SpeechRecognition || window.webkitSpeechRecognition;

if (SpeechRecognition) {
  const recognition = new SpeechRecognition();
  recognition.continuous = true; // To capture long speech
  recognition.interimResults = true; // To show real-time results
  recognition.lang = "id-ID"; // Bahasa Indonesia

  const convertText = document.getElementById("convert_text");
  const startButton = document.getElementById("click_to_convert");
  const stopButton = document.getElementById("click_to_stop");

  let finalTranscript = ""; // Variable to store the final transcribed text

  // Start voice recognition
  startButton.addEventListener("click", () => {
    recognition.start();
    startButton.disabled = true;
    stopButton.disabled = false;
    convertText.placeholder = "Listening...";
  });

  // Stop voice recognition and send result
  stopButton.addEventListener("click", () => {
    recognition.stop();
    startButton.disabled = false;
    stopButton.disabled = true;
    convertText.placeholder = "Voice recognition stopped.";

    // Send the transcribed text to the /evaluasi page
    submitAnswer(finalTranscript);
  });

  // On speech result
  recognition.addEventListener("result", (event) => {
    let transcript = "";
    for (let i = 0; i < event.results.length; i++) {
      transcript += event.results[i][0].transcript;
    }
    finalTranscript = transcript;
    convertText.value = finalTranscript;
  });

  // On recognition end
  recognition.addEventListener("end", () => {
    startButton.disabled = false;
    stopButton.disabled = true;
  });
} else {
  alert("SpeechRecognition API is not supported in this browser.");
}

fetch("/save_transcription", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
  },
  body: JSON.stringify({ student_answer: studentAnswer }),
})
  .then((response) => {
    if (response.ok) {
      return response.json();
    }
    throw new Error("Terjadi kesalahan saat menyimpan jawaban.");
  })
  .then((data) => {
    console.log("Response dari server:", data);

    // Contoh: Cek status atau pesan dalam respons
    if (data.status === "success") {
      alert("Jawaban berhasil disimpan! redirect ke -> / start simulation");

      // Lakukan permintaan GET ke /start_simulation
      return fetch("/start_simulation", {
        method: "GET",
      });
    } else {
      alert("Jawaban tidak valid, silakan coba lagi.");
      throw new Error("Invalid response status");
    }
  })
  .then((response) => {
    if (response.redirected) {
      // Jika server melakukan redirect, ikuti redirect tersebut
      window.location.href = response.url;
    } else {
      return response.text();
    }
  })
  .catch((error) => {
    console.error("Error:", error);
    alert("Gagal memproses simulasi. Silakan coba lagi.");
  });