// Legacy Messages Fetch API using GitHub REST API
// This API provides read-only access to the global chat messages

// GitHub API configuration
const GITHUB_API = "https://api.github.com";
const REPO_OWNER = "andy64lol";
const REPO_NAME = "globalchat";
const BRANCH = "main";
const FILE_PATH = "global_chat.toml";

// Helper function for GitHub REST API calls
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
    throw { 
      status: response.status, 
      data: data,
      message: data?.message || `GitHub API request failed with status ${response.status}`
    };
  }
  
  return data;
}

// Parse TOML content and convert it to messages array
function parseTOML(text) {
  const messages = [];
  
  // Split by message blocks
  const blocks = text.split('[[messages]]').slice(1);
  
  for (const block of blocks) {
    const message = {};
    const lines = block.trim().split('\n');
    
    // Parse each line of the message block
    for (const line of lines) {
      const trimmed = line.trim();
      
      // Skip empty lines and comments
      if (!trimmed || trimmed.startsWith('#')) continue;
      
      // Match key-value pairs (e.g., content = "Hello")
      const match = trimmed.match(/^(\w+)\s*=\s*"([^"]*)"/);
      if (match) {
        message[match[1]] = match[2];
      }
    }
    
    // Only add messages that have both content and author
    if (message.content && message.author) {
      messages.push(message);
    }
  }
  
  return messages;
}

// Fetch file content from GitHub repository
async function getFileContent() {
  try {
    // Make API request to get file content
    const data = await githubFetch(
      `${GITHUB_API}/repos/${REPO_OWNER}/${REPO_NAME}/contents/${FILE_PATH}?ref=${BRANCH}`
    );
    
    // Validate that content exists
    if (!data.content) {
      throw new Error('File content not found in API response');
    }
    
    // GitHub API always returns file content in base64 encoding
    // Decode base64 to UTF-8 string
    const decoded = Buffer.from(data.content, 'base64').toString('utf-8');
    return decoded;
    
  } catch (error) {
    // Enhance error information for better debugging
    console.error('Failed to fetch file content:', {
      url: `${GITHUB_API}/repos/${REPO_OWNER}/${REPO_NAME}/contents/${FILE_PATH}?ref=${BRANCH}`,
      error: error.message || error,
      status: error.status
    });
    
    // Re-throw the error for higher level handling
    throw error;
  }
}

// Main handler function for the API
exports.handler = async function(event, context) {
  // CORS headers for cross-origin requests
  const headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Content-Type': 'application/json'
  };

  // Handle CORS preflight OPTIONS request
  if (event.httpMethod === 'OPTIONS') {
    return {
      statusCode: 200,
      headers,
      body: ''
    };
  }

  // Only allow GET requests for this legacy API
  if (event.httpMethod !== 'GET') {
    return {
      statusCode: 405,
      headers,
      body: JSON.stringify({
        error: "Method not allowed",
        allowed: ["GET"],
        message: "This API only supports GET requests"
      })
    };
  }

  try {
    // Fetch and parse TOML content
    const tomlContent = await getFileContent();
    const messages = parseTOML(tomlContent);
    
    // Parse query parameters for pagination
    const queryParams = event.queryStringParameters || {};
    const limit = queryParams.limit ? parseInt(queryParams.limit) : 50;
    const offset = queryParams.offset ? parseInt(queryParams.offset) : 0;
    
    // Validate and sanitize parameters
    const limitNum = isNaN(limit) ? 50 : Math.max(1, Math.min(limit, 100)); // Max 100 messages per request
    const offsetNum = isNaN(offset) ? 0 : Math.max(0, offset);
    
    // Calculate pagination boundaries
    const start = Math.min(offsetNum, messages.length);
    const end = Math.min(start + limitNum, messages.length);
    
    // Extract paginated messages
    const paginatedMessages = messages.slice(start, end);
    
    // Return success response
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
        },
        meta: {
          source: "GitHub REST API",
          file: FILE_PATH,
          branch: BRANCH
        }
      })
    };
    
  } catch (error) {
    console.error('Error in legacy messages API:', error);
    
    // Handle specific HTTP error cases
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
          },
          message: "The chat file does not exist in the repository"
        })
      };
    }
    
    if (error.status === 401 || error.status === 403) {
      return {
        statusCode: 500,
        headers,
        body: JSON.stringify({
          error: "Authentication failed",
          message: "Unable to authenticate with GitHub API. Please check your token."
        })
      };
    }
    
    // Return generic error response
    return {
      statusCode: error.status || 500,
      headers,
      body: JSON.stringify({
        error: "Failed to fetch messages",
        message: error.data?.message || error.message || "Internal server error",
        details: process.env.NODE_ENV === 'development' ? error.stack : undefined
      })
    };
  }
};