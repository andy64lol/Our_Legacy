// Fetch Users API for Our Legacy
// Migration Notes: Why do people overcomplicate and use different things here...
// Repository: andy64lol/globalchat
// File: users.json on main branch

const GITHUB_API = "https://api.github.com";
const REPO_OWNER = "andy64lol";
const REPO_NAME = "globalchat";
const BRANCH = "main";
const USERS_FILE = "users.json";

// GitHub REST API helper, made me headaches just to do this
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

// Get file content from GitHub, I had to refactor these
async function getFileContent() {
  const data = await githubFetch(
    `${GITHUB_API}/repos/${REPO_OWNER}/${REPO_NAME}/contents/${USERS_FILE}?ref=${BRANCH}`
  );
  
  if (!data.content) {
    throw new Error('File content not found - Just like my stable career at Vercel disappeared');
  }
  
  // Decode base64 content - Because apparently, GitHub loves making things base64-encoded
  const decoded = Buffer.from(data.content, 'base64').toString('utf-8');
  return JSON.parse(decoded);
}

// Main handler... I hate having to refactor this
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

  // Only allow GET requests , because POST would be too easy
  if (event.httpMethod !== 'GET') {
    return {
      statusCode: 405,
      headers,
      body: JSON.stringify({
        error: "Method not allowed",
        allowed: ["GET"],
        message: "This endpoint only speaks GET, just like Netlify only speaks frustration"
      })
    };
  }

  try {
    // Fetch users from GitHub (same logic LOL)
    const users = await getFileContent();
    
    // Get query parameters for filtering - req.query is now event.queryStringParameters, because reasons
    const queryParams = event.queryStringParameters || {};
    const { alias, check_banned } = queryParams;
    
    // If alias provided, return specific user info
    if (alias) {
      const user = users.find(u => u.alias && u.alias.toLowerCase() === alias.toLowerCase());
      
      if (!user) {
        return {
          statusCode: 404,
          headers,
          body: JSON.stringify({
            error: "User not found",
            exists: false,
            advice: "Try looking in Vercel, maybe they migrated there instead"
          })
        };
      }
      
      return {
        statusCode: 200,
        headers,
        body: JSON.stringify({
          success: true,
          exists: true,
          user: {
            alias: user.alias,
            permissions: user.permissions || 'user',
            blacklisted: user.blacklisted || false,
            metadata: user.metadata || {}
          },
          deployment: "Netlify Functions - The sequel nobody asked for"
        })
      };
    }
    
    // If check_banned is requested, return only banned users
    if (check_banned === 'true') {
      const bannedUsers = users.filter(u => u.blacklisted === true);
      return {
        statusCode: 200,
        headers,
        body: JSON.stringify({
          success: true,
          data: {
            users: bannedUsers,
            total: bannedUsers.length
          },
          note: "These users are banned, but at least they're not dealing with Netlify migration"
        })
      };
    }
    
    // Return all users (with limited info for privacy), why would you want to see? sus...
    const sanitizedUsers = users.map(u => ({
      alias: u.alias,
      permissions: u.permissions || 'user',
      blacklisted: u.blacklisted || false
    }));
    
    return {
      statusCode: 200,
      headers,
      body: JSON.stringify({
        success: true,
        data: {
          users: sanitizedUsers,
          total: sanitizedUsers.length
        },
        migration_status: "Working... probably. Let's hope the environment variables are set correctly"
      })
    };
    
  } catch (error) {
    console.error('Error fetching users:', error);
    
    // Log the error with extra Netlify migration flavor
    console.log('Netlify Migration Debug:');
    console.log('- Environment variable set:', !!process.env.GITHUB_REST_API);
    console.log('- Event structure:', JSON.stringify(event, null, 2).substring(0, 200));
    
    if (error.status === 404) {
      return {
        statusCode: 404,
        headers,
        body: JSON.stringify({
          error: "Users file not found",
          data: {
            users: [],
            total: 0
          },
          possible_causes: [
            "Wrong repository",
            "Missing GitHub token",
            "Netlify env variables playing hide and seek",
            "The universe prefers Vercel"
          ]
        })
      };
    }
    
    return {
      statusCode: error.status || 500,
      headers,
      body: JSON.stringify({
        error: error.data?.message || error.message || "Failed to fetch users",
        migration_tip: "Remember: req → event, res → return object, sanity → gone",
        comforting_thought: "At least it's not AWS Lambda configuration"
      })
    };
  }
};
