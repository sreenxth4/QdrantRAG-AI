/* RAG Chatbot Frontend Logic */

const chatArea = document.getElementById('chatArea');
const userInput = document.getElementById('userInput');
const btnSend = document.getElementById('btnSend');
const btnReindex = document.getElementById('btnReindex');
const welcomeMsg = document.getElementById('welcomeMsg');

// === Load Stats on Page Load ===
async function loadStats() {
    try {
        const res = await fetch('/api/stats');
        const data = await res.json();
        document.getElementById('docCount').textContent = data.documents_in_folder ?? '—';
        document.getElementById('vecCount').textContent = data.vectors_count ?? '—';
        const status = document.getElementById('dbStatus');
        if (data.error) {
            status.textContent = 'offline';
            status.className = 'stat-value status-badge offline';
        } else {
            status.textContent = 'online';
            status.className = 'stat-value status-badge online';
        }
    } catch {
        document.getElementById('dbStatus').textContent = 'error';
        document.getElementById('dbStatus').className = 'stat-value status-badge offline';
    }
}

loadStats();

// === Send Message ===
async function sendMessage() {
    const question = userInput.value.trim();
    if (!question) return;

    // Hide welcome
    if (welcomeMsg) welcomeMsg.remove();

    // Add user message
    addMessage(question, 'user');
    userInput.value = '';
    autoResize();
    btnSend.disabled = true;

    // Add typing indicator
    const typingEl = addTypingIndicator();

    try {
        const res = await fetch('/api/query', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ question }),
        });
        const data = await res.json();

        typingEl.remove();

        if (data.error) {
            addMessage('Error: ' + data.error, 'ai');
        } else {
            addMessage(data.answer, 'ai', data.sources, data.chunks_used);
        }
    } catch (err) {
        typingEl.remove();
        addMessage('Connection error. Is the server running?', 'ai');
    }

    btnSend.disabled = false;
    userInput.focus();
}

// === Add Message to Chat ===
function addMessage(text, role, sources = [], chunksUsed = 0) {
    const msg = document.createElement('div');
    msg.className = `message ${role}`;

    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.textContent = role === 'user' ? 'U' : 'AI';

    const content = document.createElement('div');
    content.className = 'message-content';

    const textEl = document.createElement('div');
    textEl.className = 'message-text';
    textEl.textContent = text;
    content.appendChild(textEl);

    // Add sources for AI messages
    if (role === 'ai' && sources.length > 0) {
        const srcDiv = document.createElement('div');
        srcDiv.className = 'sources-list';
        srcDiv.innerHTML = `<div class="sources-title">📄 Source Documents</div>`;
        sources.forEach(src => {
            const tag = document.createElement('span');
            tag.className = 'source-tag';
            tag.textContent = src;
            srcDiv.appendChild(tag);
        });
        if (chunksUsed > 0) {
            const info = document.createElement('div');
            info.className = 'chunks-info';
            info.textContent = `Retrieved ${chunksUsed} relevant chunks`;
            srcDiv.appendChild(info);
        }
        content.appendChild(srcDiv);
    }

    msg.appendChild(avatar);
    msg.appendChild(content);
    chatArea.appendChild(msg);
    chatArea.scrollTop = chatArea.scrollHeight;
}

// === Typing Indicator ===
function addTypingIndicator() {
    const msg = document.createElement('div');
    msg.className = 'message ai';
    msg.id = 'typingMsg';

    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.textContent = 'AI';

    const content = document.createElement('div');
    content.className = 'message-content';
    content.innerHTML = '<div class="typing-indicator"><span></span><span></span><span></span></div>';

    msg.appendChild(avatar);
    msg.appendChild(content);
    chatArea.appendChild(msg);
    chatArea.scrollTop = chatArea.scrollHeight;
    return msg;
}

// === Reindex ===
btnReindex.addEventListener('click', async () => {
    btnReindex.disabled = true;
    btnReindex.classList.add('loading');

    // Show overlay
    const overlay = document.createElement('div');
    overlay.className = 'reindex-overlay';
    overlay.innerHTML = `
        <div class="reindex-modal">
            <h3>🔄 Reindexing Documents</h3>
            <p>Loading, chunking, embedding, and storing all documents in Qdrant Cloud...</p>
            <div class="reindex-progress"><div class="reindex-progress-bar"></div></div>
        </div>
    `;
    document.body.appendChild(overlay);

    try {
        const res = await fetch('/api/ingest', { method: 'POST' });
        const data = await res.json();
        overlay.remove();

        if (data.error) {
            alert('Reindex failed: ' + data.error);
        } else {
            alert(`✅ Reindex complete!\n\nDocuments: ${data.documents_loaded}\nChunks: ${data.chunks_created}\nVectors: ${data.vectors_stored}`);
        }
        loadStats();
    } catch (err) {
        overlay.remove();
        alert('Reindex failed: ' + err.message);
    }

    btnReindex.disabled = false;
    btnReindex.classList.remove('loading');
});

// === Auto-resize Textarea ===
function autoResize() {
    userInput.style.height = 'auto';
    userInput.style.height = Math.min(userInput.scrollHeight, 120) + 'px';
}

userInput.addEventListener('input', autoResize);

// === Key Events ===
userInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

btnSend.addEventListener('click', sendMessage);

// === Sample Questions ===
function askSample(btn) {
    userInput.value = btn.textContent;
    autoResize();
    sendMessage();
}
