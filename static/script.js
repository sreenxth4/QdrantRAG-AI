/* RAG Chatbot Frontend Logic with Role-Based Access */

const chatArea = document.getElementById('chatArea');
const userInput = document.getElementById('userInput');
const btnSend = document.getElementById('btnSend');
const btnReindex = document.getElementById('btnReindex');
const welcomeMsg = document.getElementById('welcomeMsg');
const roleSelect = document.getElementById('roleSelect');
const roleDocInfo = document.getElementById('roleDocInfo');

let rolesData = [];

// === Load Roles on Page Load ===
async function loadRoles() {
    try {
        const res = await fetch('/api/roles');
        rolesData = await res.json();
        rolesData.forEach(role => {
            const opt = document.createElement('option');
            opt.value = role.id;
            opt.textContent = `${role.title} — ${role.description.split('—')[1]?.trim() || ''}`;
            roleSelect.appendChild(opt);
        });
    } catch (e) {
        console.error('Failed to load roles:', e);
    }
}

// === Update role doc info ===
roleSelect.addEventListener('change', () => {
    const val = roleSelect.value;
    if (val === 'all') {
        roleDocInfo.textContent = 'Access: All 100 documents';
        roleDocInfo.style.color = '';
    } else {
        const role = rolesData.find(r => r.id === val);
        if (role) {
            roleDocInfo.textContent = `Access: ${role.doc_count} documents for ${role.title}`;
            roleDocInfo.style.color = '#9b85ff';
        }
    }
});

// === Load Stats on Page Load ===
async function loadStats() {
    try {
        const res = await fetch('/api/stats');
        const data = await res.json();
        document.getElementById('docCount').textContent = data.documents_in_folder ?? '—';
        document.getElementById('vecCount').textContent = data.vectors_count ?? '—';
        document.getElementById('roleCount').textContent = data.roles_count ?? '—';
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

loadRoles();
loadStats();

// === Send Message ===
async function sendMessage() {
    const question = userInput.value.trim();
    if (!question) return;

    if (welcomeMsg) welcomeMsg.remove();

    const role = roleSelect.value;
    const roleLabel = role === 'all' ? '' : ` [${roleSelect.options[roleSelect.selectedIndex].textContent.split('—')[0].trim()}]`;
    addMessage(question + roleLabel, 'user');
    userInput.value = '';
    autoResize();
    btnSend.disabled = true;

    const typingEl = addTypingIndicator();

    try {
        const res = await fetch('/api/query', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ question, role }),
        });
        const data = await res.json();
        typingEl.remove();

        if (data.error) {
            addMessage('Error: ' + data.error, 'ai');
        } else {
            addMessage(data.answer, 'ai', data.sources, data.chunks_used, data.role);
        }
    } catch (err) {
        typingEl.remove();
        addMessage('Connection error. Is the server running?', 'ai');
    }

    btnSend.disabled = false;
    userInput.focus();
}

// === Add Message to Chat ===
function addMessage(text, msgRole, sources = [], chunksUsed = 0, accessRole = '') {
    const msg = document.createElement('div');
    msg.className = `message ${msgRole}`;

    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.textContent = msgRole === 'user' ? 'U' : 'AI';

    const content = document.createElement('div');
    content.className = 'message-content';

    const textEl = document.createElement('div');
    textEl.className = 'message-text';
    textEl.textContent = text;
    content.appendChild(textEl);

    if (msgRole === 'ai' && sources.length > 0) {
        const srcDiv = document.createElement('div');
        srcDiv.className = 'sources-list';

        // Show role badge
        if (accessRole && accessRole !== 'all') {
            const roleBadge = document.createElement('div');
            roleBadge.className = 'role-badge-inline';
            roleBadge.textContent = `🔒 Role: ${accessRole.toUpperCase().replace('_', ' ')}`;
            srcDiv.appendChild(roleBadge);
        }

        srcDiv.innerHTML += `<div class="sources-title">📄 Source Documents</div>`;
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

    const overlay = document.createElement('div');
    overlay.className = 'reindex-overlay';
    overlay.innerHTML = `
        <div class="reindex-modal">
            <h3>🔄 Reindexing Documents</h3>
            <p>Loading, chunking, embedding with role metadata, and storing in Qdrant Cloud...</p>
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

userInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

btnSend.addEventListener('click', sendMessage);

function askSample(btn) {
    userInput.value = btn.textContent;
    autoResize();
    sendMessage();
}
