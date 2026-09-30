const form = document.getElementById("eduForm");
const inputText = document.getElementById("inputText");
const inputLabel = document.getElementById("inputLabel");
const optionsGroup = document.getElementById("optionsGroup");
const level = document.getElementById("level");
const timeframe = document.getElementById("timeframe");
const quizCountWrap = document.getElementById("quizCountWrap");
const quizCount = document.getElementById("quizCount");
const summaryStyleWrap = document.getElementById("summaryStyleWrap");
const summaryStyle = document.getElementById("summaryStyle");
const result = document.getElementById("result");
const errorBox = document.getElementById("error");
const loading = document.getElementById("loading");
const submitButton = document.getElementById("submitButton");
const copyButton = document.getElementById("copyButton");
const statusPill = document.getElementById("statusPill");
const taskCards = document.querySelectorAll(".task-card");

let currentTask = "qa";
let chatHistory = [];

const config = {
  qa: {
    label: "Your question",
    placeholder: "Example: Explain Newton's third law with a simple example.",
    button: "Ask Gemini Flash"
  },
  explain: {
    label: "Topic to explain",
    placeholder: "Example: Photosynthesis",
    button: "Explain with Gemini"
  },
  quiz: {
    label: "Study passage",
    placeholder: "Paste your textbook passage, notes, or study material here.",
    button: "Generate Quiz"
  },
  summarize: {
    label: "Text to summarize",
    placeholder: "Paste a chapter, article section, or study notes.",
    button: "Create Summary"
  },
  learn: {
    label: "Topic to learn",
    placeholder: "Example: Python, Data Structures, Machine Learning, SQL",
    button: "Build Roadmap"
  },
  chat: {
    label: "Message",
    placeholder: "Ask a follow-up question or continue your learning session.",
    button: "Send Message"
  }
};

function escapeHtml(value) {
  return String(value).replace(/[&<>"']/g, ch => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#039;"
  }[ch]));
}

function renderMarkdownLite(value) {
  return escapeHtml(value)
    .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
    .replace(/`([^`]+)`/g, "<code>$1</code>")
    .replace(/\n/g, "<br>");
}

function setTask(task) {
  currentTask = task;

  taskCards.forEach(card => {
    card.classList.toggle("active", card.dataset.task === task);
  });

  const c = config[task];
  inputLabel.textContent = c.label;
  inputText.placeholder = c.placeholder;
  submitButton.textContent = c.button;

  const needsOptions = ["quiz", "summarize", "learn"].includes(task);
  optionsGroup.classList.toggle("hidden", !needsOptions);
  quizCountWrap.classList.toggle("hidden", task !== "quiz");
  summaryStyleWrap.classList.toggle("hidden", task !== "summarize");

  if (task === "learn") {
    optionsGroup.classList.remove("hidden");
  }
}

function renderText(text) {
  result.innerHTML = `<div class="answer">${renderMarkdownLite(text)}</div>`;
}

function renderQuiz(data) {
  result.innerHTML = data.questions.map((q, i) => `
    <div class="quiz-question">
      <div class="question-number">QUESTION ${i + 1}</div>
      <h3>${escapeHtml(q.question)}</h3>
      <div class="options">
        ${q.options.map((option, index) => `
          <div class="quiz-option">
            <span>${String.fromCharCode(65 + index)}</span>
            ${escapeHtml(option)}
          </div>
        `).join("")}
      </div>
      <div class="answer-box">
        <strong>Correct answer:</strong> ${escapeHtml(q.correct_answer)}
        <p>${escapeHtml(q.explanation)}</p>
      </div>
    </div>
  `).join("");
}

function renderLearningPath(data) {
  const steps = data.steps.map((step, i) => `
    <div class="path-step">
      <div class="step-number">${i + 1}</div>
      <div>
        <h3>${escapeHtml(step.stage)}</h3>
        <p><strong>Topics:</strong> ${step.topics.map(escapeHtml).join(", ")}</p>
        <p><strong>Time:</strong> ${escapeHtml(step.suggested_time)}</p>
        <p><strong>Resources:</strong> ${step.resources.map(escapeHtml).join(", ")}</p>
      </div>
    </div>
  `).join("");

  result.innerHTML = `
    <div class="roadmap-header">
      <span>${escapeHtml(data.level)} • ${escapeHtml(data.timeframe)}</span>
      <h3>${escapeHtml(data.topic)} Roadmap</h3>
      <p>${escapeHtml(data.overview)}</p>
    </div>
    ${steps}
    <div class="tips">
      <h3>Study tips</h3>
      <ul>${data.tips.map(t => `<li>${escapeHtml(t)}</li>`).join("")}</ul>
    </div>
  `;
}

async function callApi() {
  const value = inputText.value.trim();
  if (!value) throw new Error("Please enter some content first.");

  let endpoint;
  let payload;

  if (currentTask === "qa") {
    endpoint = "/qa";
    payload = { question: value };
  } else if (currentTask === "explain") {
    endpoint = "/explain";
    payload = { topic: value };
  } else if (currentTask === "quiz") {
    endpoint = "/quiz";
    payload = { text: value, count: Number(quizCount.value) };
  } else if (currentTask === "summarize") {
    endpoint = "/summarize";
    payload = { text: value, style: summaryStyle.value };
  } else if (currentTask === "learn") {
    endpoint = "/learn/recommendations";
    payload = {
      topic: value,
      level: level.value,
      timeframe: timeframe.value.trim()
    };
  } else {
    endpoint = "/chat";
    payload = { message: value, history: chatHistory };
  }

  const response = await fetch(endpoint, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });

  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    throw new Error(data.detail || `Request failed with HTTP ${response.status}.`);
  }

  return data;
}

taskCards.forEach(card => {
  card.addEventListener("click", () => setTask(card.dataset.task));
});

form.addEventListener("submit", async event => {
  event.preventDefault();
  errorBox.classList.add("hidden");
  loading.classList.remove("hidden");
  submitButton.disabled = true;
  copyButton.disabled = true;

  try {
    const data = await callApi();

    if (currentTask === "quiz") {
      renderQuiz(data);
    } else if (currentTask === "learn") {
      renderLearningPath(data);
    } else {
      renderText(data.result);

      if (currentTask === "chat") {
        chatHistory.push({ role: "user", content: inputText.value.trim() });
        chatHistory.push({ role: "assistant", content: data.result });
      }
    }

    copyButton.disabled = false;
    inputText.value = "";
  } catch (error) {
    errorBox.textContent = error.message;
    errorBox.classList.remove("hidden");
  } finally {
    loading.classList.add("hidden");
    submitButton.disabled = false;
  }
});

copyButton.addEventListener("click", async () => {
  await navigator.clipboard.writeText(result.innerText);
  const original = copyButton.textContent;
  copyButton.textContent = "Copied ✓";
  setTimeout(() => { copyButton.textContent = original; }, 1200);
});

async function checkHealth() {
  try {
    const response = await fetch("/health");
    const data = await response.json();

    statusPill.textContent = data.gemini_configured
      ? `● ${data.model} ready`
      : "● Gemini API key missing";

    statusPill.classList.toggle("ready", Boolean(data.gemini_configured));
  } catch {
    statusPill.textContent = "● Server unavailable";
  }
}

setTask("qa");
checkHealth();
