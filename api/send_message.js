// Global Chat API for Our Legacy
// Message structure: [{ content, author, timestamp }]
// Repository: andy64lol/globalchat
// File: global_chat.json on main branch

const GITHUB_API = "https://api.github.com";
const REPO_OWNER = "andy64lol";
const REPO_NAME = "globalchat";
const BRANCH = "main";
const FILE_PATH = "global_chat.json";
const OLD_MESSAGES_DIR = "old_messages";
const MAX_MESSAGES = 100;
const MESSAGES_TO_KEEP = 5;
const PROFANITY_WORDS_URL = "https://raw.githubusercontent.com/zautumnz/profane-words/refs/heads/master/words.json";

// GitHub REST API helper
async function githubFetch(url, options = {}) {
  const token = process.env.GITHUB_REST_API;
  const headers = {
    Authorization: `Bearer ${token}`,
    Accept: "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
    "Content-Type": "application/json",
    ...options.headers
  };

  const response = await fetch(url, { ...options, headers });
  const data = await response.json();
  
  if (!response.ok) {
    throw { status: response.status, data };
  }
  
  return data;
}

// Get file SHA for updates
async function getFileSha() {
  try {
    const data = await githubFetch(
      `${GITHUB_API}/repos/${REPO_OWNER}/${REPO_NAME}/contents/${FILE_PATH}`
    );
    return data.sha;
  } catch {
    return null;
  }
}

// Fetch profanity words for filtering
async function fetchProfanityWords() {
  try {
    const response = await fetch(PROFANITY_WORDS_URL);
    if (!response.ok) {
      throw new Error(`Failed to fetch profanity words: ${response.status}`);
    }
    const words = await response.json();
    return words;
  } catch (error) {
    console.error('Error fetching profanity words:', error);
    return [];
  }
}

// Check if text contains profanity
function containsProfanity(text, profanityWords) {
  if (!text || typeof text !== 'string') return false;
  
  const lowerText = text.toLowerCase();
  for (const word of profanityWords) {
    if (typeof word === 'string' && word.trim()) {
      const escapedWord = word.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
      const regex = new RegExp(`\\b${escapedWord}\\b`, 'i');
      if (regex.test(text)) {
        return true;
      }
    }
  }
  return false;
}

// Read messages from the repository
async function readMessages() {
  const rawUrl = `https://raw.githubusercontent.com/${REPO_OWNER}/${REPO_NAME}/${BRANCH}/${FILE_PATH}`;
  
  try {
    const response = await fetch(rawUrl, { cache: 'no-store' });
    if (!response.ok) {
      if (response.status === 404) {
        return [];
      }
      throw new Error(`Failed to fetch messages: ${response.status}`);
    }
    const content = await response.json();
    return Array.isArray(content) ? content : [];
  } catch (error) {
    console.error('Error reading messages:', error);
    throw error;
  }
}

// Save messages to repository
async function saveMessages(messages, sha = null) {
  const content = JSON.stringify(messages, null, 2);
  const encoded = Buffer.from(content).toString('base64');
  
  const payload = {
    message: messages.length > 0 
      ? `Update chat: ${messages.length} messages` 
      : "Initialize chat",
    content: encoded,
    branch: BRANCH
  };
  
  if (sha) {
    payload.sha = sha;
  }
  
  return await githubFetch(
    `${GITHUB_API}/repos/${REPO_OWNER}/${REPO_NAME}/contents/${FILE_PATH}`,
    {
      method: "PUT",
      body: JSON.stringify(payload)
    }
  );
}

// Archive old messages
async function archiveMessages(messages) {
  // Create archive filename with timestamp
  const timestamp = messages.length > 0 
    ? messages[messages.length - 1].timestamp 
    : Date.now();
  const archiveFilename = `${OLD_MESSAGES_DIR}/${timestamp}_chat.json`;
  
  // Save archived messages - GitHub creates the directory automatically if it doesn't exist
  const content = JSON.stringify(messages, null, 2);
  const encoded = Buffer.from(content).toString('base64');
  
  const archivePayload = {
    message: `Archive ${messages.length} old messages`,
    content: encoded,
    branch: BRANCH
  };
  
  await githubFetch(
    `${GITHUB_API}/repos/${REPO_OWNER}/${REPO_NAME}/contents/${archiveFilename}`,
    {
      method: "PUT",
      body: JSON.stringify(archivePayload)
    }
  );
}

// Get latest commit SHA
async function getLatestCommitSha() {
  const data = await githubFetch(
    `${GITHUB_API}/repos/${REPO_OWNER}/${REPO_NAME}/commits/${BRANCH}`
  );
  return data.sha;
}

// Handle incoming messages
async function handleMessage(req, res) {
  const { message, author } = req.body;
  
  // Validate input
  if (!message || !author) {
    return res.status(400).json({ 
      error: "Message and author are required" 
    });
  }
  
  if (typeof message !== 'string' || typeof author !== 'string') {
    return res.status(400).json({ 
      error: "Message and author must be strings" 
    });
  }
  
  if (message.length > 300) {
    return res.status(400).json({ 
      error: "Message too long (max 300 characters)" 
    });
  }
  
  if (author.length > 50) {
    return res.status(400).json({ 
      error: "Author name too long (max 50 characters)" 
    });
  }
  
  // Check for profanity
  const profanityWords = await fetchProfanityWords();
  
  if (containsProfanity(message, profanityWords)) {
    return res.status(400).json({ 
      error: "Message contains prohibited content",
      filtered: true
    });
  }
  
  if (containsProfanity(author, profanityWords)) {
    return res.status(400).json({ 
      error: "Author name contains prohibited content",
      filtered: true
    });
  }
  
  // Read current messages first
  let messages;
  try {
    messages = await readMessages();
  } catch (error) {
    console.error('Failed to read existing messages:', error);
    return res.status(500).json({
      error: "Failed to read existing messages. Please try again."
    });
  }
  
  try {
    const sha = await getFileSha();
    
    // Create new message
    const newMessage = {
      content: message.trim(),
      author: author.trim(),
      timestamp: Date.now().toString(),
      id: `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
    };
    
    // Check if we need to archive messages
    if (messages.length >= MAX_MESSAGES) {
      // Archive current messages before trimming
      await archiveMessages(messages);
      messages = messages.slice(-MESSAGES_TO_KEEP);
    }
    
    // Add new message
    messages.push(newMessage);
    
    // Save updated messages
    await saveMessages(messages, sha);
    
    return res.status(200).json({
      success: true,
      message: "Message sent successfully",
      data: {
        id: newMessage.id,
        timestamp: newMessage.timestamp,
        position: messages.length
      }
    });
    
  } catch (error) {
    console.error('Error sending message:', error);
    return res.status(error.status || 500).json({
      error: error.data?.message || error.message || "Failed to send message"
    });
  }
}

// Handle reading messages
async function handleRead(req, res) {
  const { limit = 50, offset = 0 } = req.query;
  
  try {
    const messages = await readMessages();
    
    // Pagination
    const start = Math.min(offset, messages.length);
    const end = Math.min(start + parseInt(limit), messages.length);
    const paginatedMessages = messages.slice(start, end);
    
    return res.status(200).json({
      success: true,
      data: {
        messages: paginatedMessages,
        total: messages.length,
        limit: parseInt(limit),
        offset: parseInt(offset),
        hasMore: end < messages.length
      }
    });
    
  } catch (error) {
    console.error('Error reading messages:', error);
    return res.status(error.status || 500).json({
      error: error.data?.message || error.message || "Failed to read messages"
    });
  }
}

// Main handler
export default async function handler(req, res) {
  const { method, query } = req;
  
  switch (method) {
    case "GET":
      return handleRead(req, res);
    case "POST":
      return handleMessage(req, res);
    default:
      return res.status(405).json({ 
        error: "Method not allowed",
        allowed: ["GET", "POST"]
      });
  }
}
