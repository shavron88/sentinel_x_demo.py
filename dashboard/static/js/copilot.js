async function sendQuestion() {
    const input = document.getElementById("userQuestion");
    const chat = document.getElementById("chatWindow");
    const empty = document.getElementById("emptyState");
    
    if (!input || !chat) return;
    
    const question = input.value.trim();
    if (!question) return;
    
    if (empty) empty.style.display = "none";
    
    const userMsg = document.createElement("div");
    userMsg.className = "user-message";
    userMsg.textContent = question;
    chat.appendChild(userMsg);
    
    const loadingMsg = document.createElement("div");
    loadingMsg.className = "ai-message loading";
    loadingMsg.textContent = "Thinking...";
    chat.appendChild(loadingMsg);
    
    chat.scrollTop = chat.scrollHeight;
    input.value = "";
    
    try {
        const response = await fetch("/api/copilot", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ question: question })
        });
        
        const data = await response.json();
        
        loadingMsg.textContent = data.response || "No response available.";
        
    } catch (err) {
        console.error("Copilot error:", err);
        loadingMsg.textContent = "Backend integration pending. AI chat is not yet connected.";
        loadingMsg.className = "ai-message error";
    }
    
    chat.scrollTop = chat.scrollHeight;
}

document.getElementById("userQuestion")?.addEventListener("keypress", function(e) {
    if (e.key === "Enter") {
        sendQuestion();
    }
});