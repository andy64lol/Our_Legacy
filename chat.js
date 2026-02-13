/**
 * Our Legacy Chat - Web Client
 * JavaScript implementation of the chat client with fallback support
 */

// Configuration - Primary URLs (Vercel)
const CONFIG = {
    PING_URL: "https://our-legacy.vercel.app/api/ping",
    SEND_MESSAGE_URL: "https://our-legacy.vercel.app/api/send_message",
    CREATE_USER_URL: "https://our-legacy.vercel.app/api/create_user",
    FETCH_MESSAGES_URL: "https://our-legacy.vercel.app/api/fetch_messages",
    FETCH_USERS_URL: "https://our-legacy.vercel.app/api/fetch_users",
    BAN_CHAT_URL: "https://our-legacy.vercel.app/api/ban_chat",
    USERS_URL: "https://raw.githubusercontent.com/andy64lol/globalchat/refs/heads/main/users.json",
    
    // Fallback URLs (Netlify)
    PING_URL_FALLBACK: "https://our-legacy.netlify.app/functions/ping",
    SEND_MESSAGE_URL_FALLBACK: "https://our-legacy.netlify.app/functions/send_messages",
    CREATE_USER_URL_FALLBACK: "https://our-legacy.netlify.app/functions/create_user",
    FETCH_MESSAGES_URL_FALLBACK: "https://our-legacy.netlify.app/functions/fetch_messages",
    FETCH_USERS_URL_FALLBACK: "https://our-legacy.netlify.app/functions/fetch_users",
    BAN_CHAT_URL_FALLBACK: "https://our-legacy.netlify.app/functions/ban_chat",
    
    // Settings
    COOLDOWN_SECONDS: 20,
    AUTO_REFRESH_SECONDS: 10,
    BAN_CHECK_SECONDS: 90,
    MAX_MESSAGE_LENGTH: 300,
    MESSAGES_PER_PAGE: 10,
    MAX_FETCH_MESSAGES: 10
};

// Chat Client Class
class ChatClient {
    constructor() {
        this.alias = null;
        this.lastMessageTime = 0;
        this.messages = [];
        this.currentPage = 0;
        this.autoRefresh = true;
        this.connectionOk = false;
        this.lastRefreshTime = 0;
        this.isExiting = false;
        this.lastMessageCount = 0;
        this.usersList = [];
        this.isBanned = false;
        this.lastBanCheck = 0;
        this.lastFetchTime = 0;
        this.userPermissions = 'user';
        this.autoRefreshInterval = null;
        this.banCheckInterval = null;
        
        this.init();
    }
    
    init() {
        this.loadAlias();
        this.setupEventListeners();
    }
    
    // Utility: Try multiple URLs with fallback
    async tryUrls(urls, options = {}) {
        const { method = 'GET', body = null, headers = {}, timeout = 10000 } = options;
        
        let lastError = null;
        
        for (const url of urls) {
            try {
                const controller = new AbortController();
                const timeoutId = setTimeout(() => controller.abort(), timeout);
                
                const fetchOptions = {
                    method,
                    headers: {
                        'Content-Type': 'application/json',
                        ...headers
                    },
                    signal: controller.signal
                };
                
                if (body && (method === 'POST' || method === 'PUT')) {
                    fetchOptions.body = JSON.stringify(body);
                }
                
                const response = await fetch(url, fetchOptions);
                clearTimeout(timeoutId);
                
                if (response.ok) {
                    return response;
                }
            } catch (error) {
                lastError = error;
                console.warn(`Failed to connect to ${url}:`, error.message);
                continue;
            }
        }
        
        throw lastError || new Error('All URLs failed');
    }
    
    // Check connection with fallback
    async checkConnection() {
        try {
            const response = await this.tryUrls(
                [CONFIG.PING_URL, CONFIG.PING_URL_FALLBACK],
                { method: 'GET', timeout: 5000 }
            );
            this.connectionOk = response.status === 200;
            this.updateConnectionStatus();
            return this.connectionOk;
        } catch (error) {
            this.connectionOk = false;
            this.updateConnectionStatus();
            return false;
        }
    }
    
    updateConnectionStatus() {
        const statusDot = document.getElementById('connection-status');
        if (statusDot) {
            statusDot.className = `status-dot ${this.connectionOk ? 'connected' : 'disconnected'}`;
            statusDot.title = this.connectionOk ? 'Connected' : 'Disconnected';
        }
    }
    
    // Fetch users from repository
    async fetchUsers() {
        try {
            const response = await fetch(CONFIG.USERS_URL, { timeout: 10000 });
            if (response.ok) {
                const data = await response.json();
                if (Array.isArray(data)) {
                    this.usersList = data;
                    return data;
                }
            }
        } catch (error) {
            console.error('Error fetching users:', error);
        }
        return [];
    }
    
    // Check if alias exists with fallback
    async checkAliasExists(alias) {
        try {
            const encodedAlias = encodeURIComponent(alias);
            const response = await this.tryUrls([
                `${CONFIG.CREATE_USER_URL}?alias=${encodedAlias}`,
                `${CONFIG.CREATE_USER_URL_FALLBACK}?alias=${encodedAlias}`
            ], { method: 'GET', timeout: 10000 });
            
            if (response.ok) {
                const data = await response.json();
                return data.exists || false;
            }
        } catch (error) {
            console.warn('Could not check alias online, falling back to local check');
        }
        
        // Fallback to local check
        const users = await this.fetchUsers();
        return users.some(user => 
            user && user.alias && user.alias.toLowerCase() === alias.toLowerCase()
        );
    }
    
    // Check if user is banned
    async isUserBanned(alias) {
        const users = await this.fetchUsers();
        const user = users.find(u => 
            u && u.alias && u.alias.toLowerCase() === alias.toLowerCase()
        );
        return user ? user.blacklisted || false : false;
    }
    
    // Get user permissions with fallback
    async getUserPermissions(alias) {
        try {
            const encodedAlias = encodeURIComponent(alias);
            const response = await this.tryUrls([
                `${CONFIG.FETCH_USERS_URL}?alias=${encodedAlias}`,
                `${CONFIG.FETCH_USERS_URL_FALLBACK}?alias=${encodedAlias}`
            ], { method: 'GET', timeout: 10000 });
            
            if (response.ok) {
                const data = await response.json();
                if (data.success && data.user) {
                    return data.user.permissions || 'user';
                }
            }
        } catch (error) {
            console.error('Error fetching user permissions:', error);
        }
        return 'user';
    }
    
    getPermissionLevel(permissions) {
        const levels = { user: 0, admin: 1, owner: 2 };
        return levels[permissions] || 0;
    }
    
    // Ban user with fallback
    async banUser(targetAlias, reason = null) {
        try {
            const payload = {
                action: 'ban',
                target_alias: targetAlias,
                moderator_alias: this.alias,
                reason: reason
            };
            
            const response = await this.tryUrls([
                CONFIG.BAN_CHAT_URL,
                CONFIG.BAN_CHAT_URL_FALLBACK
            ], { method: 'POST', body: payload, timeout: 10000 });
            
            if (response.ok) {
                const data = await response.json();
                this.showToast(data.message || 'User banned successfully', 'success');
                return true;
            } else {
                const errorData = await response.json().catch(() => ({}));
                this.showToast(errorData.error || `Failed to ban (HTTP ${response.status})`, 'error');
                return false;
            }
        } catch (error) {
            this.showToast(`Error banning user: ${error.message}`, 'error');
            return false;
        }
    }
    
    // Unban user with fallback
    async unbanUser(targetAlias) {
        try {
            const payload = {
                action: 'unban',
                target_alias: targetAlias,
                moderator_alias: this.alias
            };
            
            const response = await this.tryUrls([
                CONFIG.BAN_CHAT_URL,
                CONFIG.BAN_CHAT_URL_FALLBACK
            ], { method: 'POST', body: payload, timeout: 10000 });
            
            if (response.ok) {
                const data = await response.json();
                this.showToast(data.message || 'User unbanned successfully', 'success');
                return true;
            } else {
                const errorData = await response.json().catch(() => ({}));
                this.showToast(errorData.error || `Failed to unban (HTTP ${response.status})`, 'error');
                return false;
            }
        } catch (error) {
            this.showToast(`Error unbanning user: ${error.message}`, 'error');
            return false;
        }
    }
    
    // Check user status with fallback
    async checkUserStatus(targetAlias) {
        try {
            const payload = {
                action: 'check',
                target_alias: targetAlias,
                moderator_alias: this.alias
            };
            
            const response = await this.tryUrls([
                CONFIG.BAN_CHAT_URL,
                CONFIG.BAN_CHAT_URL_FALLBACK
            ], { method: 'POST', body: payload, timeout: 10000 });
            
            if (response.ok) {
                const data = await response.json();
                if (data.success && data.target) {
                    this.showStatusModal(targetAlias, data.target);
                    return true;
                }
            } else {
                const errorData = await response.json().catch(() => ({}));
                this.showToast(errorData.error || `Failed to check status (HTTP ${response.status})`, 'error');
                return false;
            }
        } catch (error) {
            this.showToast(`Error checking user status: ${error.message}`, 'error');
            return false;
        }
        return false;
    }
    
    showStatusModal(alias, target) {
        const modal = document.getElementById('status-modal');
        const content = document.getElementById('status-content');
        
        content.innerHTML = `
            <div class="status-row">
                <span class="status-label">User:</span>
                <span class="status-value">${alias}</span>
            </div>
            <div class="status-row">
                <span class="status-label">Permissions:</span>
                <span class="status-value">${target.permissions || 'user'}</span>
            </div>
            <div class="status-row">
                <span class="status-label">Blacklisted:</span>
                <span class="status-value">${target.blacklisted ? 'Yes' : 'No'}</span>
            </div>
            ${target.ban_reason ? `
            <div class="status-row">
                <span class="status-label">Ban Reason:</span>
                <span class="status-value">${target.ban_reason}</span>
            </div>
            ` : ''}
            ${target.banned_by ? `
            <div class="status-row">
                <span class="status-label">Banned By:</span>
                <span class="status-value">${target.banned_by}</span>
            </div>
            ` : ''}
        `;
        
        modal.classList.remove('hidden');
    }
    
    // Load or create alias
    async loadAlias() {
        const savedAlias = localStorage.getItem('chat_alias');
        
        if (savedAlias) {
            this.alias = savedAlias;
            const banned = await this.isUserBanned(this.alias);
            
            if (banned) {
                alert('You are banned from the chat.');
                localStorage.removeItem('chat_alias');
                this.showSetupScreen();
                return;
            }
            
            this.userPermissions = await this.getUserPermissions(this.alias);
            this.showChatScreen();
            this.startChat();
        } else {
            this.showSetupScreen();
        }
    }
    
    showSetupScreen() {
        document.getElementById('setup-screen').classList.remove('hidden');
        document.getElementById('chat-screen').classList.add('hidden');
    }
    
    showChatScreen() {
        document.getElementById('setup-screen').classList.add('hidden');
        document.getElementById('chat-screen').classList.remove('hidden');
        document.getElementById('current-alias').textContent = this.alias;
    }
    
    // Register user online with fallback
    async registerUserOnline(alias) {
        const maxRetries = 3;
        
        for (let attempt = 0; attempt < maxRetries; attempt++) {
            try {
                const payload = {
                    alias: alias,
                    metadata: { permissions: 'user' }
                };
                
                const response = await this.tryUrls([
                    CONFIG.CREATE_USER_URL,
                    CONFIG.CREATE_USER_URL_FALLBACK
                ], { method: 'POST', body: payload, timeout: 15000 });
                
                if (response.status === 201) {
                    return true;
                } else if (response.status === 409) {
                    console.log('Username already registered online');
                    return true;
                } else {
                    const errorData = await response.json().catch(() => ({}));
                    console.warn(`Registration attempt ${attempt + 1} failed:`, errorData.error || `HTTP ${response.status}`);
                }
            } catch (error) {
                console.warn(`Registration attempt ${attempt + 1} error:`, error.message);
            }
            
            if (attempt < maxRetries - 1) {
                await this.delay(1000);
            }
        }
        
        return false;
    }
    
    // Save alias
    async saveAlias(alias) {
        const onlineSuccess = await this.registerUserOnline(alias);
        
        if (!onlineSuccess) {
            console.warn('Failed to register username online, continuing in local mode');
        }
        
        localStorage.setItem('chat_alias', alias);
        this.alias = alias;
        this.userPermissions = await this.getUserPermissions(alias);
    }
    
    // Fetch messages with fallback
    async fetchMessages(force = false) {
        const currentTime = Date.now();
        const timeSinceLast = (currentTime - this.lastFetchTime) / 1000;
        
        if (!force && timeSinceLast < 20) {
            const cooldown = Math.ceil(20 - timeSinceLast);
            this.showToast(`Please wait ${cooldown}s before refreshing`, 'warning');
            return false;
        }
        
        try {
            const response = await this.tryUrls([
                CONFIG.FETCH_MESSAGES_URL,
                CONFIG.FETCH_MESSAGES_URL_FALLBACK
            ], { method: 'GET', timeout: 10000 });
            
            if (response.ok) {
                const data = await response.json();
                
                if (data.success && data.data) {
                    let allMessages = data.data.messages || [];
                    
                    // Only take last N messages for performance
                    if (allMessages.length > CONFIG.MAX_FETCH_MESSAGES) {
                        allMessages = allMessages.slice(-CONFIG.MAX_FETCH_MESSAGES);
                    }
                    
                    // Normalize messages
                    const normalized = allMessages.map(msg => {
                        if (typeof msg === 'object' && msg !== null) {
                            return msg;
                        } else if (typeof msg === 'string') {
                            try {
                                const parsed = JSON.parse(msg);
                                if (typeof parsed === 'object') {
                                    return parsed;
                                }
                            } catch (e) {
                                // Not valid JSON
                            }
                            return {
                                author: 'System',
                                content: msg,
                                timestamp: Date.now()
                            };
                        }
                        return {
                            author: 'Unknown',
                            content: String(msg),
                            timestamp: Date.now()
                        };
                    });
                    
                    const hasChanges = JSON.stringify(normalized) !== JSON.stringify(this.messages);
                    
                    if (hasChanges) {
                        this.messages = normalized;
                        this.lastRefreshTime = currentTime;
                        this.lastFetchTime = currentTime;
                        this.displayMessages();
                    }
                    
                    return hasChanges;
                }
            }
            
            return false;
        } catch (error) {
            console.error('Error fetching messages:', error);
            return false;
        }
    }
    
    // Display messages
    displayMessages() {
        const container = document.getElementById('messages-list');
        
        if (this.messages.length === 0) {
            container.innerHTML = '<div class="empty-state">No messages yet. Be the first to say something!</div>';
            return;
        }
        
        const totalMessages = this.messages.length;
        const totalPages = Math.max(Math.ceil(totalMessages / CONFIG.MESSAGES_PER_PAGE), 1);
        this.currentPage = Math.min(this.currentPage, totalPages - 1);
        this.currentPage = Math.max(0, this.currentPage);
        
        const startIdx = this.currentPage * CONFIG.MESSAGES_PER_PAGE;
        const endIdx = Math.min(startIdx + CONFIG.MESSAGES_PER_PAGE, totalMessages);
        
        const messagesToShow = this.messages.slice(startIdx, endIdx);
        
        container.innerHTML = messagesToShow.map((msg, index) => {
            const author = msg.author || 'Unknown';
            const content = msg.content || '';
            const timestamp = msg.timestamp || Date.now();
            
            const timeStr = this.formatTimestamp(timestamp);
            
            let authorClass = 'other';
            let authorPrefix = '';
            
            if (author === this.alias) {
                authorClass = 'self';
            } else if (author === 'System' || author === 'Unknown') {
                authorClass = 'system';
                authorPrefix = '*** ';
            }
            
            const isLast = index === messagesToShow.length - 1;
            
            return `
                <div class="message">
                    <div class="message-header">
                        <span class="message-timestamp">[${timeStr}]</span>
                        <span class="message-author ${authorClass}">${authorPrefix}${author}</span>
                    </div>
                    <div class="message-content">${this.escapeHtml(content)}</div>
                    ${!isLast ? '<div class="message-divider"></div>' : ''}
                </div>
            `;
        }).join('');
        
        // Scroll to bottom
        const messagesContainer = document.getElementById('messages-container');
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
        
        this.lastMessageCount = totalMessages;
    }
    
    formatTimestamp(timestamp) {
        try {
            const date = new Date(timestamp);
            const now = new Date();
            
            const isToday = date.toDateString() === now.toDateString();
            const isYesterday = new Date(now - 86400000).toDateString() === date.toDateString();
            
            if (isToday) {
                return date.toLocaleTimeString('en-US', { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' });
            } else if (isYesterday) {
                return `Yesterday ${date.toLocaleTimeString('en-US', { hour12: false, hour: '2-digit', minute: '2-digit' })}`;
            } else {
                return `${(date.getMonth() + 1).toString().padStart(2, '0')}/${date.getDate().toString().padStart(2, '0')} ${date.toLocaleTimeString('en-US', { hour12: false, hour: '2-digit', minute: '2-digit' })}`;
            }
        } catch (e) {
            return '??:??';
        }
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    // Send message with fallback
    async sendMessage(content) {
        const cooldown = this.getCooldownStatus();
        
        if (cooldown > 0) {
            this.showToast(`Please wait ${cooldown} seconds before sending another message`, 'warning');
            return false;
        }
        
        if (content.length > CONFIG.MAX_MESSAGE_LENGTH) {
            this.showToast(`Message too long (max ${CONFIG.MAX_MESSAGE_LENGTH} characters)`, 'error');
            return false;
        }
        
        if (!content.trim()) {
            this.showToast('Message cannot be empty', 'warning');
            return false;
        }
        
        try {
            const payload = {
                message: content,
                author: this.alias
            };
            
            const response = await this.tryUrls([
                CONFIG.SEND_MESSAGE_URL,
                CONFIG.SEND_MESSAGE_URL_FALLBACK
            ], { method: 'POST', body: payload, timeout: 10000 });
            
            if (response.ok) {
                this.lastMessageTime = Date.now();
                this.updateCooldownDisplay();
                return true;
            } else {
                const errorData = await response.json().catch(() => ({}));
                this.showToast(errorData.error || `Failed to send (HTTP ${response.status})`, 'error');
                return false;
            }
        } catch (error) {
            this.showToast(`Error: ${error.message}`, 'error');
            return false;
        }
    }
    
    getCooldownStatus() {
        const currentTime = Date.now();
        const timeSinceLast = (currentTime - this.lastMessageTime) / 1000;
        
        if (timeSinceLast < CONFIG.COOLDOWN_SECONDS) {
            return CONFIG.COOLDOWN_SECONDS - Math.floor(timeSinceLast);
        }
        return 0;
    }
    
    updateCooldownDisplay() {
        const cooldown = this.getCooldownStatus();
        const indicator = document.getElementById('cooldown-indicator');
        const timeSpan = document.getElementById('cooldown-time');
        const input = document.getElementById('message-input');
        const sendBtn = document.getElementById('send-btn');
        
        if (cooldown > 0) {
            indicator.classList.remove('hidden');
            timeSpan.textContent = cooldown;
            input.disabled = true;
            sendBtn.disabled = true;
            
            setTimeout(() => this.updateCooldownDisplay(), 1000);
        } else {
            indicator.classList.add('hidden');
            input.disabled = false;
            sendBtn.disabled = false;
            input.focus();
        }
    }
    
    // Handle commands
    async handleCommand(input) {
        const cmd = input.toLowerCase().trim();
        const parts = input.split(' ');
        const baseCmd = parts[0].toLowerCase();
        
        switch (baseCmd) {
            case '/r':
            case '/refresh':
                this.showToast('Refreshing messages...', 'success');
                await this.fetchMessages(true);
                break;
                
            case '/next':
            case '/n':
                const totalPages = Math.max(Math.ceil(this.messages.length / CONFIG.MESSAGES_PER_PAGE), 1);
                if (this.currentPage < totalPages - 1) {
                    this.currentPage++;
                    this.displayMessages();
                } else {
                    this.showToast('Already at last page', 'warning');
                }
                break;
                
            case '/prev':
            case '/p':
                if (this.currentPage > 0) {
                    this.currentPage--;
                    this.displayMessages();
                } else {
                    this.showToast('Already at first page', 'warning');
                }
                break;
                
            case '/auto':
                this.autoRefresh = !this.autoRefresh;
                this.showToast(`Auto-refresh: ${this.autoRefresh ? 'ON' : 'OFF'}`, this.autoRefresh ? 'success' : 'warning');
                break;
                
            case '/clear':
            case '/c':
                this.messages = [];
                this.displayMessages();
                this.showToast('Screen cleared', 'success');
                break;
                
            case '/status':
            case '/s':
                const connected = await this.checkConnection();
                this.showToast(connected ? '✓ Connected to server' : '✗ Cannot connect to server', connected ? 'success' : 'error');
                break;
                
            case '/exit':
            case '/quit':
            case '/q':
                if (confirm('Are you sure you want to exit?')) {
                    localStorage.removeItem('chat_alias');
                    location.reload();
                }
                break;
                
            case '/help':
            case '/h':
                this.showHelp();
                break;
                
            case '/whoami':
                this.showToast(`Alias: ${this.alias}, Permissions: ${this.userPermissions}`, 'success');
                break;
                
            case '/ban':
                if (this.getPermissionLevel(this.userPermissions) < 1) {
                    this.showToast('Unknown command: ' + input, 'error');
                    return;
                }
                if (parts.length < 2) {
                    this.showToast('Usage: /ban <username> [reason]', 'warning');
                    return;
                }
                const banTarget = parts[1];
                const banReason = parts.slice(2).join(' ') || null;
                await this.banUser(banTarget, banReason);
                break;
                
            case '/unban':
                if (this.getPermissionLevel(this.userPermissions) < 1) {
                    this.showToast('Unknown command: ' + input, 'error');
                    return;
                }
                if (parts.length < 2) {
                    this.showToast('Usage: /unban <username>', 'warning');
                    return;
                }
                await this.unbanUser(parts[1]);
                break;
                
            case '/check':
                if (this.getPermissionLevel(this.userPermissions) < 1) {
                    this.showToast('Unknown command: ' + input, 'error');
                    return;
                }
                if (parts.length < 2) {
                    this.showToast('Usage: /check <username>', 'warning');
                    return;
                }
                await this.checkUserStatus(parts[1]);
                break;
                
            default:
                this.showToast('Unknown command: ' + input, 'error');
                this.showToast('Type /help for available commands', 'warning');
        }
    }
    
    showHelp() {
        const modal = document.getElementById('help-modal');
        const adminCommands = document.getElementById('admin-commands');
        
        if (this.getPermissionLevel(this.userPermissions) >= 1) {
            adminCommands.classList.remove('hidden');
        } else {
            adminCommands.classList.add('hidden');
        }
        
        modal.classList.remove('hidden');
    }
    
    // Event Listeners
    setupEventListeners() {
        // Alias setup
        const aliasInput = document.getElementById('alias-input');
        const aliasSubmit = document.getElementById('alias-submit');
        const aliasError = document.getElementById('alias-error');
        const aliasPreview = document.getElementById('alias-preview');
        const confirmYes = document.getElementById('confirm-yes');
        const confirmNo = document.getElementById('confirm-no');
        const previewAlias = document.getElementById('preview-alias');
        
        aliasSubmit.addEventListener('click', async () => {
            const alias = aliasInput.value.trim();
            
            if (!alias) {
                aliasError.textContent = 'Alias cannot be empty';
                return;
            }
            
            if (alias.length > 20) {
                aliasError.textContent = 'Alias too long (max 20 characters)';
                return;
            }
            
            if (!/^[a-zA-Z0-9_\- ]+$/.test(alias)) {
                aliasError.textContent = 'Only letters, numbers, spaces, underscores, and hyphens allowed';
                return;
            }
            
            const exists = await this.checkAliasExists(alias);
            if (exists) {
                aliasError.textContent = `Username '${alias}' is already taken. Please choose another.`;
                return;
            }
            
            aliasError.textContent = '';
            previewAlias.textContent = alias;
            aliasPreview.classList.remove('hidden');
            aliasSubmit.classList.add('hidden');
        });
        
        confirmYes.addEventListener('click', async () => {
            const alias = aliasInput.value.trim();
            await this.saveAlias(alias);
            this.showChatScreen();
            this.startChat();
        });
        
        confirmNo.addEventListener('click', () => {
            aliasPreview.classList.add('hidden');
            aliasSubmit.classList.remove('hidden');
            aliasInput.value = '';
            aliasInput.focus();
        });
        
        aliasInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                aliasSubmit.click();
            }
        });
        
        // Chat input
        const messageInput = document.getElementById('message-input');
        const sendBtn = document.getElementById('send-btn');
        
        sendBtn.addEventListener('click', async () => {
            const content = messageInput.value.trim();
            
            if (content.startsWith('/')) {
                messageInput.value = '';
                await this.handleCommand(content);
            } else {
                const success = await this.sendMessage(content);
                if (success) {
                    messageInput.value = '';
                    await this.delay(500);
                    await this.fetchMessages();
                }
            }
        });
        
        messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                sendBtn.click();
            }
        });
        
        messageInput.addEventListener('input', () => {
            const count = messageInput.value.length;
            const charCount = document.getElementById('char-count');
            charCount.textContent = `${count}/${CONFIG.MAX_MESSAGE_LENGTH}`;
            
            if (count > CONFIG.MAX_MESSAGE_LENGTH * 0.9) {
                charCount.className = 'char-count error';
            } else if (count > CONFIG.MAX_MESSAGE_LENGTH * 0.8) {
                charCount.className = 'char-count warning';
            } else {
                charCount.className = 'char-count dim';
            }
        });
        
        // Help modal
        document.getElementById('close-help').addEventListener('click', () => {
            document.getElementById('help-modal').classList.add('hidden');
        });
        
        // Status modal
        document.getElementById('close-status').addEventListener('click', () => {
            document.getElementById('status-modal').classList.add('hidden');
        });
        
        // Close modals on outside click
        document.querySelectorAll('.modal').forEach(modal => {
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    modal.classList.add('hidden');
                }
            });
        });
    }
    
    // Start chat
    async startChat() {
        await this.checkConnection();
        await this.fetchMessages();
        
        // Start auto-refresh
        this.autoRefreshInterval = setInterval(async () => {
            if (this.autoRefresh) {
                await this.fetchMessages();
            }
        }, CONFIG.AUTO_REFRESH_SECONDS * 1000);
        
        // Start ban check
        this.banCheckInterval = setInterval(async () => {
            if (this.alias) {
                const banned = await this.isUserBanned(this.alias);
                if (banned) {
                    this.showToast('You have been banned from the chat. Exiting...', 'error');
                    setTimeout(() => {
                        localStorage.removeItem('chat_alias');
                        location.reload();
                    }, 2000);
                }
            }
        }, CONFIG.BAN_CHECK_SECONDS * 1000);
        
        // Focus input
        document.getElementById('message-input').focus();
    }
    
    // Utility: Delay
    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
    
    // Utility: Show toast notification
    showToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.textContent = message;
        document.body.appendChild(toast);
        
        setTimeout(() => {
            toast.remove();
        }, 3000);
    }
}

// Initialize chat when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.chatClient = new ChatClient();
});
