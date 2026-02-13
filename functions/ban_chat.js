// functions/ban_chat.js
// I hate having to adapt these things LOL

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

// Get file SHA for updates
async function getFileSha() {
  try {
    const data = await githubFetch(
      `${GITHUB_API}/repos/${REPO_OWNER}/${REPO_NAME}/contents/${USERS_FILE}`
    );
    return data.sha;
  } catch {
    return null;
  }
}

// Get file content from GitHub
async function getFileContent() {
  const data = await githubFetch(
    `${GITHUB_API}/repos/${REPO_OWNER}/${REPO_NAME}/contents/${USERS_FILE}?ref=${BRANCH}`
  );
  
  if (!data.content) {
    throw new Error('File content not found');
  }
  
  const decoded = Buffer.from(data.content, 'base64').toString('utf-8');
  return JSON.parse(decoded);
}

// Save users to repository
async function saveUsers(users, sha = null) {
  const content = JSON.stringify(users, null, 2);
  const encoded = Buffer.from(content).toString('base64');
  
  const payload = {
    message: `Update users: ban/unban operation`,
    content: encoded,
    branch: BRANCH
  };
  
  if (sha) {
    payload.sha = sha;
  }
  
  return await githubFetch(
    `${GITHUB_API}/repos/${REPO_OWNER}/${REPO_NAME}/contents/${USERS_FILE}`,
    {
      method: "PUT",
      body: JSON.stringify(payload)
    }
  );
}

// Get user permissions level
function getPermissionLevel(permissions) {
  const levels = {
    'user': 0,
    'admin': 1,
    'owner': 2
  };
  return levels[permissions] || 0;
}

// Netlify Functions handler
exports.handler = async function(event, context) {
  // CORS headers
  const headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'POST, OPTIONS',
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

  // Only allow POST requests
  if (event.httpMethod !== 'POST') {
    return {
      statusCode: 405,
      headers,
      body: JSON.stringify({
        error: "Method not allowed",
        allowed: ["POST"]
      })
    };
  }

  let body;
  try {
    body = JSON.parse(event.body);
  } catch (e) {
    return {
      statusCode: 400,
      headers,
      body: JSON.stringify({
        error: "Invalid JSON body"
      })
    };
  }

  const { action, target_alias, moderator_alias, reason } = body;

  // Validate required fields
  if (!action || !target_alias || !moderator_alias) {
    return {
      statusCode: 400,
      headers,
      body: JSON.stringify({
        error: "Missing required fields: action, target_alias, moderator_alias"
      })
    };
  }

  // Validate action
  const validActions = ['ban', 'unban', 'check'];
  if (!validActions.includes(action)) {
    return {
      statusCode: 400,
      headers,
      body: JSON.stringify({
        error: `Invalid action. Must be one of: ${validActions.join(', ')}`
      })
    };
  }

  try {
    // Fetch current users
    const users = await getFileContent();
    const sha = await getFileSha();

    // Find moderator
    const moderator = users.find(u => u.alias && u.alias.toLowerCase() === moderator_alias.toLowerCase());
    
    if (!moderator) {
      return {
        statusCode: 403,
        headers,
        body: JSON.stringify({
          error: "Moderator not found"
        })
      };
    }

    // Check moderator permissions
    const modPermissions = moderator.permissions || 'user';
    const modLevel = getPermissionLevel(modPermissions);

    if (modLevel < 1) { // Not admin or owner
      return {
        statusCode: 403,
        headers,
        body: JSON.stringify({
          error: "Insufficient permissions. Only admins and owners can perform this action."
        })
      };
    }

    // Find target user
    const targetIndex = users.findIndex(u => u.alias && u.alias.toLowerCase() === target_alias.toLowerCase());
    
    if (targetIndex === -1) {
      return {
        statusCode: 404,
        headers,
        body: JSON.stringify({
          error: "Target user not found"
        })
      };
    }

    const targetUser = users[targetIndex];
    const targetPermissions = targetUser.permissions || 'user';
    const targetLevel = getPermissionLevel(targetPermissions);

    // Permission checks
    if (action === 'ban') {
      // Admin cannot ban admin or owner
      if (modLevel === 1 && targetLevel >= 1) {
        return {
          statusCode: 403,
          headers,
          body: JSON.stringify({
            error: "Admins cannot ban other admins or owners"
          })
        };
      }

      // Owner can ban anyone except owner
      if (modLevel === 2 && targetLevel === 2) {
        return {
          statusCode: 403,
          headers,
          body: JSON.stringify({
            error: "Owners cannot ban other owners"
          })
        };
      }

      // Ban the user
      users[targetIndex].blacklisted = true;
      if (reason) {
        users[targetIndex].ban_reason = reason;
        users[targetIndex].banned_by = moderator_alias;
        users[targetIndex].banned_at = new Date().toISOString();
      }

    } else if (action === 'unban') {
      // Admin cannot unban if target is admin or owner (unless they banned them)
      if (modLevel === 1 && targetLevel >= 1) {
        // Check if this admin banned them
        if (targetUser.banned_by !== moderator_alias) {
          return {
            statusCode: 403,
            headers,
            body: JSON.stringify({
              error: "Admins cannot unban other admins or owners unless they banned them"
            })
          };
        }
      }

      // Owner can unban anyone except owner
      if (modLevel === 2 && targetLevel === 2) {
        return {
          statusCode: 403,
          headers,
          body: JSON.stringify({
            error: "Owners cannot unban other owners"
          })
        };
      }

      // Unban the user
      users[targetIndex].blacklisted = false;
      delete users[targetIndex].ban_reason;
      delete users[targetIndex].banned_by;
      delete users[targetIndex].banned_at;

    } else if (action === 'check') {
      // Just return status without modifying
      return {
        statusCode: 200,
        headers,
        body: JSON.stringify({
          success: true,
          action: 'check',
          target: {
            alias: targetUser.alias,
            permissions: targetPermissions,
            blacklisted: targetUser.blacklisted || false,
            ban_reason: targetUser.ban_reason || null,
            banned_by: targetUser.banned_by || null
          },
          moderator: {
            alias: moderator.alias,
            permissions: modPermissions
          }
        })
      };
    }

    // Save updated users
    await saveUsers(users, sha);

    return {
      statusCode: 200,
      headers,
      body: JSON.stringify({
        success: true,
        action: action,
        target_alias: target_alias,
        moderator_alias: moderator_alias,
        message: `User ${target_alias} has been ${action === 'ban' ? 'banned' : 'unbanned'} successfully`
      })
    };

  } catch (error) {
    console.error('Error in ban_chat:', error);
    
    return {
      statusCode: error.status || 500,
      headers,
      body: JSON.stringify({
        error: error.data?.message || error.message || "Failed to perform ban action"
      })
    };
  }
};
