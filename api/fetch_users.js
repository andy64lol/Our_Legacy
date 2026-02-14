// Fetch Users API for Our Legacy
// Uses GitHub REST API to read users from globalchat repository
// Repository: andy64lol/globalchat
// File: users.json on main branch

const GITHUB_API = "https://api.github.com";
const REPO_OWNER = "andy64lol";
const REPO_NAME = "globalchat";
const BRANCH = "main";
const USERS_FILE = "users.json";

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

// Get file content from GitHub
async function getFileContent() {
  const data = await githubFetch(
    `${GITHUB_API}/repos/${REPO_OWNER}/${REPO_NAME}/contents/${USERS_FILE}?ref=${BRANCH}`
  );
  
  if (!data.content) {
    throw new Error('File content not found');
  }
  
  // Decode base64 content
  const decoded = Buffer.from(data.content, 'base64').toString('utf-8');
  return JSON.parse(decoded);
}

// Main handler
export default async function handler(req, res) {
  // Enable CORS
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  
  // Handle OPTIONS request for CORS preflight
  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }
  
  // Only allow GET requests
  if (req.method !== 'GET') {
    return res.status(405).json({
      error: "Method not allowed",
      allowed: ["GET"]
    });
  }

  try {
    // Fetch users from GitHub
    const users = await getFileContent();
    
    // Get query parameters for filtering
    const { alias, check_banned } = req.query;
    
    // If alias provided, return specific user info
    if (alias) {
      const user = users.find(u => u.alias && u.alias.toLowerCase() === alias.toLowerCase());
      
      if (!user) {
        return res.status(404).json({
          error: "User not found",
          exists: false
        });
      }
      
      return res.status(200).json({
        success: true,
        exists: true,
        user: {
          alias: user.alias,
          permissions: user.permissions || 'user',
          blacklisted: user.blacklisted || false,
          metadata: user.metadata || {}
        }
      });
    }
    
    // If check_banned is requested, return only banned users
    if (check_banned === 'true') {
      const bannedUsers = users.filter(u => u.blacklisted === true);
      return res.status(200).json({
        success: true,
        data: {
          users: bannedUsers,
          total: bannedUsers.length
        }
      });
    }
    
    // Return all users (with limited info for privacy)
    const sanitizedUsers = users.map(u => ({
      alias: u.alias,
      permissions: u.permissions || 'user',
      blacklisted: u.blacklisted || false
    }));
    
    return res.status(200).json({
      success: true,
      data: {
        users: sanitizedUsers,
        total: sanitizedUsers.length
      }
    });
    
  } catch (error) {
    console.error('Error fetching users:', error);
    
    if (error.status === 404) {
      return res.status(404).json({
        error: "Users file not found",
        data: {
          users: [],
          total: 0
        }
      });
    }
    
    return res.status(error.status || 500).json({
      error: error.data?.message || error.message || "Failed to fetch users"
    });
  }
}
