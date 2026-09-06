// A per-browser session id, kept in localStorage so refreshing the page
// keeps the same conversation history (the backend keeps history per id).
function getSessionId() {
  let id = localStorage.getItem("kisan_dost_session_id");
  if (!id) {
    id = crypto.randomUUID();
    localStorage.setItem("kisan_dost_session_id", id);
  }
  return id;
}

const sessionId = getSessionId();

const chatEl = document.getElementById("chat");
const composerEl = document.getElementById("composer");
const inputEl = document.getElementById("messageInput");

function addMessage(text, kind) {
  // kind: "bot" | "user" | "blocked"
  const div = document.createElement("div");
  div.className = `msg msg--${kind}`;
  const p = document.createElement("p");
  p.textContent = text;
  div.appendChild(p);
  chatEl.appendChild(div);
  chatEl.scrollTop = chatEl.scrollHeight;
  return div;
}

function addTypingIndicator() {
  const div = document.createElement("div");
  div.className = "msg msg--typing";
  div.innerHTML = "<span></span><span></span><span></span>";
  chatEl.appendChild(div);
  chatEl.scrollTop = chatEl.scrollHeight;
  return div;
}

composerEl.addEventListener("submit", async (e) => {
  e.preventDefault();
  const text = inputEl.value.trim();
  if (!text) return;

  addMessage(text, "user");
  inputEl.value = "";
  inputEl.focus();

  const typingEl = addTypingIndicator();

  try {
    const res = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ session_id: sessionId, message: text }),
    });

    if (!res.ok) {
      throw new Error(`Server error: ${res.status}`);
    }

    const data = await res.json();
    typingEl.remove();
    addMessage(data.reply, data.blocked ? "blocked" : "bot");
  } catch (err) {
    typingEl.remove();
    addMessage(
      "Maazrat, server se rabta nahi ho saka. Dobara koshish karein.",
      "blocked"
    );
    console.error(err);
  }
});

// ---------- Profile panel ----------

const profileToggle = document.getElementById("profileToggle");
const profilePanel = document.getElementById("profilePanel");
const profileClose = document.getElementById("profileClose");
const overlay = document.getElementById("overlay");
const profileForm = document.getElementById("profileForm");

function openProfilePanel() {
  profilePanel.classList.add("is-open");
  overlay.classList.add("is-open");
  loadProfile();
}

function closeProfilePanel() {
  profilePanel.classList.remove("is-open");
  overlay.classList.remove("is-open");
}

profileToggle.addEventListener("click", openProfilePanel);
profileClose.addEventListener("click", closeProfilePanel);
overlay.addEventListener("click", closeProfilePanel);

async function loadProfile() {
  try {
    const res = await fetch(`/api/profile?session_id=${encodeURIComponent(sessionId)}`);
    const data = await res.json();
    for (const [key, value] of Object.entries(data)) {
      const field = profileForm.elements.namedItem(key);
      if (field && value !== null && value !== undefined) {
        field.value = value;
      }
    }
  } catch (err) {
    console.error("Profile load failed", err);
  }
}

profileForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const formData = new FormData(profileForm);
  const payload = { session_id: sessionId };

  for (const [key, value] of formData.entries()) {
    if (value === "") continue;
    payload[key] = key === "land_size_acres" ? parseFloat(value) : value;
  }

  try {
    await fetch("/api/profile", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    closeProfilePanel();
  } catch (err) {
    console.error("Profile save failed", err);
  }
});