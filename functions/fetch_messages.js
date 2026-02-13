// Fetch Messages API for Our Legacy
// NETLIFY CRAZINESS EDITION

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
  const blocks = text.split('[[messages]]').slice(1); 
  
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
  
  // Decode base64 content... GitHub API returns file content in base64 encoding, ALWAYS.
  const decoded = Buffer.from(data.content, 'base64').toString('utf-8');
  return decoded;
}

exports.handler = async function(event, context) {
  // CORS headers
  const headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Content-Type': 'application/json'
  };

  // Handle OPTIONS request for CORS preflight
  if (event.httpMethod === 'OPTIONS') {
    return {
      statusCode: 200,
      headers,
      body: ''
    };
  }

  // Only allow GET requests
  if (event.httpMethod !== 'GET') {
    return {
      statusCode: 405,
      headers,
      body: JSON.stringify({
        error: "Method not allowed",
        allowed: ["GET"]
      })
    };
  }

  try {
    const tomlContent = await getFileContent();
    const messages = parseTOML(tomlContent);
    const queryParams = event.queryStringParameters || {};
    const limit = queryParams.limit ? parseInt(queryParams.limit) : 50;
    const offset = queryParams.offset ? parseInt(queryParams.offset) : 0;
    const limitNum = isNaN(limit) ? 50 : Math.max(1, limit);
    const offsetNum = isNaN(offset) ? 0 : Math.max(0, offset);
    const start = Math.min(offsetNum, messages.length);
    const end = Math.min(start + limitNum, messages.length);
    const paginatedMessages = messages.slice(start, end);
    
    return {
      statusCode: 200,
      headers,
      body: JSON.stringify({
        success: true,
        data: {
          messages: paginatedMessages,
          total: messages.length,
          limit: limitNum,
          offset: offsetNum,
          hasMore: end < messages.length
        }
      })
    };
    
  } catch (error) {
    console.error('Error fetching messages:', error);
    
    // Handle specific error cases
    if (error.status === 404) {
      return {
        statusCode: 404,
        headers,
        body: JSON.stringify({
          error: "Messages file not found",
          data: {
            messages: [],
            total: 0,
            limit: 50,
            offset: 0,
            hasMore: false
          }
        })
      };
    }
    
    return {
      statusCode: error.status || 500,
      headers,
      body: JSON.stringify({
        error: error.data?.message || error.message || "Failed to fetch messages"
      })
    };
  }
};
