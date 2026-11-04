(function () {
  if (window.__shopAssistantLoaded) return;
  window.__shopAssistantLoaded = true;

  const API = window.SHOP_ASSISTANT_API || "";
  const TITLE = window.SHOP_ASSISTANT_TITLE || "Ассистент магазина";

  // --- ключ истории в localStorage ---
  const STORAGE_KEY = "shop_assistant_history_v1";
  const MAX_MESSAGES = 100; // чтобы не раздувать хранилище

  function loadHistory() {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (!raw) return [];
      const arr = JSON.parse(raw);
      return Array.isArray(arr) ? arr : [];
    } catch (e) {
      return [];
    }
  }

  function saveHistory(messages) {
    try {
      const trimmed = messages.slice(-MAX_MESSAGES);
      localStorage.setItem(STORAGE_KEY, JSON.stringify(trimmed));
    } catch (e) {
      // localStorage может быть недоступен (приватный режим, переполнение)
    }
  }

  let history = loadHistory();

  // --- стили ---
  const style = document.createElement("style");
style.textContent = `
  #sa-fab{position:fixed;right:20px;bottom:20px;width:72px;height:72px;border-radius:50%;
    background:#2563eb;color:#fff;border:none;cursor:pointer;font-size:32px;z-index:99999;
    box-shadow:0 6px 18px rgba(0,0,0,.25);display:flex;align-items:center;
    justify-content:center;line-height:1;transition:transform .15s ease, box-shadow .15s ease;}
  #sa-fab:hover{transform:scale(1.06);box-shadow:0 8px 22px rgba(0,0,0,.3);}
  #sa-win{position:fixed;right:20px;bottom:104px;width:340px;max-width:calc(100vw - 40px);
    height:460px;max-height:calc(100vh - 140px);background:#fff;border-radius:12px;
    box-shadow:0 8px 30px rgba(0,0,0,.25);display:none;flex-direction:column;
    z-index:99999;font-family:system-ui,Segoe UI,Roboto,sans-serif;overflow:hidden;}
  #sa-win.open{display:flex;}
  #sa-head{background:#2563eb;color:#fff;padding:12px 14px;font-weight:600;
    display:flex;justify-content:space-between;align-items:center;}
  #sa-clear{background:transparent;border:none;color:#dbeafe;cursor:pointer;font-size:12px;}
  #sa-clear:hover{color:#fff;}
  #sa-body{flex:1;overflow-y:auto;padding:12px;background:#f8fafc;}
  .sa-msg{margin:8px 0;padding:8px 12px;border-radius:10px;font-size:14px;line-height:1.4;
    max-width:85%;word-wrap:break-word;}
  .sa-user{background:#2563eb;color:#fff;margin-left:auto;}
  .sa-bot{background:#e5e7eb;color:#111;}
  #sa-form{display:flex;border-top:1px solid #e5e7eb;}
  #sa-input{flex:1;border:none;padding:12px;font-size:14px;outline:none;}
  #sa-send{border:none;background:#2563eb;color:#fff;padding:0 16px;cursor:pointer;}
`;
document.head.appendChild(style);

  // --- DOM ---
  const fab = document.createElement("button");
  fab.id = "sa-fab";
  fab.textContent = "💬";
  fab.setAttribute("aria-label", "Открыть чат");

  const win = document.createElement("div");
  win.id = "sa-win";
  win.innerHTML = `
    <div id="sa-head">
      <span>${TITLE}</span>
      <button id="sa-clear" title="Очистить историю">Очистить</button>
    </div>
    <div id="sa-body"></div>
    <form id="sa-form">
      <input id="sa-input" placeholder="Напишите вопрос…" autocomplete="off">
      <button id="sa-send" type="submit">➤</button>
    </form>
  `;

  document.body.appendChild(fab);
  document.body.appendChild(win);

  const body = win.querySelector("#sa-body");
  const input = win.querySelector("#sa-input");
  const form = win.querySelector("#sa-form");
  const clearBtn = win.querySelector("#sa-clear");

  function renderMsg(text, who) {
    const div = document.createElement("div");
    div.className = "sa-msg " + (who === "user" ? "sa-user" : "sa-bot");
    div.textContent = text;
    body.appendChild(div);
    body.scrollTop = body.scrollHeight;
  }

  function addMsg(text, who, persist = true) {
    renderMsg(text, who);
    if (persist) {
      history.push({ who, text, ts: Date.now() });
      saveHistory(history);
    }
  }

  // --- восстановление истории ---
  if (history.length > 0) {
    history.forEach((m) => renderMsg(m.text, m.who));
  } else {
    addMsg("Здравствуйте! Спросите про товар, доставку или возврат.", "bot", false);
  }

  // --- события ---
  fab.addEventListener("click", () => {
    win.classList.toggle("open");
    if (win.classList.contains("open")) input.focus();
  });

  clearBtn.addEventListener("click", () => {
    history = [];
    saveHistory(history);
    body.innerHTML = "";
    addMsg("История очищена. Чем могу помочь?", "bot", false);
  });

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const text = input.value.trim();
    if (!text) return;

    addMsg(text, "user");
    input.value = "";
    input.disabled = true;

    try {
      const res = await fetch(API + "/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: text }),
      });
      if (!res.ok) throw new Error("HTTP " + res.status);
      const data = await res.json();
      addMsg(data.answer, "bot");
    } catch (err) {
      addMsg("Извините, не удалось получить ответ. Попробуйте позже.", "bot");
    } finally {
      input.disabled = false;
      input.focus();
    }
  });
})();