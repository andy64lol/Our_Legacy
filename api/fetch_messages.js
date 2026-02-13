// Fetch Messages API for Our Legacy
// Uses GitHub REST API to read messages from globalchat repository
// Repository: andy64lol/globalchat
// File: global_chat.toml on main branch

const GITHUB_API = "https://api.github.com";
const REPO_OWNER = "andy64lol";
const REPO_NAME = "globalchat";
const BRANCH = "main";
const FILE_PATH = "global_chat.toml";

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

// Parse TOML content to messages array
function parseTOML(text) {
  const messages = [];
  const blocks = text.split('[[messages]]').slice(1); // Skip empty first element
  
  for (const block of blocks) {
    const message = {};
    const lines = block.trim().split('\n');
    
    for (const line of lines) {
      const trimmed = line.trim();
      if (!trimmed || trimmed.startsWith('#')) continue;
      
      const match = trimmed.match(/^(\w+)\s*=\s*"([^"]*)"/);
      if (match) {
        message[match[1]] = match[2];
      }
    }
    
    if (message.content && message.author) {
      messages.push(message);
    }
  }
  
  return messages;
}

// Get file content from GitHub
async function getFileContent() {
  const data = await githubFetch(
    `${GITHUB_API}/repos/${REPO_OWNER}/${REPO_NAME}/contents/${FILE_PATH}?ref=${BRANCH}`
  );
  
  if (!data.content) {
    throw new Error('File content not found');
  }
  
  // Decode base64 content
  const decoded = Buffer.from(data.content, 'base64').toString('utf-8');
  return decoded;
}

// Main handler
export default async function handler(req, res) {
  // Only allow GET requests
  if (req.method !== 'GET') {
    return res.status(405).json({
      error: "Method not allowed",
      allowed: ["GET"]
    });
  }

  try {
    // Fetch file content from GitHub
    const tomlContent = await getFileContent();
    
    // Parse TOML to messages array
    const messages = parseTOML(tomlContent);
    
    // Get pagination parameters
    const { limit = 50, offset = 0 } = req.query;
    const limitNum = parseInt(limit);
    const offsetNum = parseInt(offset);
    
    // Paginate results
    const start = Math.min(offsetNum, messages.length);
    const end = Math.min(start + limitNum, messages.length);
    const paginatedMessages = messages.slice(start, end);
    
    return res.status(200).json({
      success: true,
      data: {
        messages: paginatedMessages,
        total: messages.length,
        limit: limitNum,
        offset: offsetNum,
        hasMore: end < messages.length
      }
    });
    
  } catch (error) {
    console.error('Error fetching messages:', error);
    
    // Handle specific error cases
    if (error.status === 404) {
      return res.status(404).json({
        error: "Messages file not found",
        data: {
          messages: [],
          total: 0,
          limit: 50,
          offset: 0,
          hasMore: false
        }
      });
    }
    
    return res.status(error.status || 500).json({
      error: error.data?.message || error.message || "Failed to fetch messages"
    });
  }
}
