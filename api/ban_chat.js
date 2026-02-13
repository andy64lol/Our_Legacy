// Ban Chat API for Our Legacy
// Admin/Owner exclusive commands for banning/unbanning users
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

// Main handler
export default async function handler(req, res) {
  // Only allow POST requests
  if (req.method !== 'POST') {
    return res.status(405).json({
      error: "Method not allowed",
      allowed: ["POST"]
    });
  }

  const { action, target_alias, moderator_alias, reason } = req.body;

  // Validate required fields
  if (!action || !target_alias || !moderator_alias) {
    return res.status(400).json({
      error: "Missing required fields: action, target_alias, moderator_alias"
    });
  }

  // Validate action
  const validActions = ['ban', 'unban', 'check'];
  if (!validActions.includes(action)) {
    return res.status(400).json({
      error: `Invalid action. Must be one of: ${validActions.join(', ')}`
    });
  }

  try {
    // Fetch current users
    const users = await getFileContent();
    const sha = await getFileSha();

    // Find moderator
    const moderator = users.find(u => u.alias && u.alias.toLowerCase() === moderator_alias.toLowerCase());
    
    if (!moderator) {
      return res.status(403).json({
        error: "Moderator not found"
      });
    }

    // Check moderator permissions
    const modPermissions = moderator.permissions || 'user';
    const modLevel = getPermissionLevel(modPermissions);

    if (modLevel < 1) { // Not admin or owner
      return res.status(403).json({
        error: "Insufficient permissions. Only admins and owners can perform this action."
      });
    }

    // Find target user
    const targetIndex = users.findIndex(u => u.alias && u.alias.toLowerCase() === target_alias.toLowerCase());
    
    if (targetIndex === -1) {
      return res.status(404).json({
        error: "Target user not found"
      });
    }

    const targetUser = users[targetIndex];
    const targetPermissions = targetUser.permissions || 'user';
    const targetLevel = getPermissionLevel(targetPermissions);

    // Permission checks
    if (action === 'ban') {
      // Admin cannot ban admin or owner
      if (modLevel === 1 && targetLevel >= 1) {
        return res.status(403).json({
          error: "Admins cannot ban other admins or owners"
        });
      }

      // Owner can ban anyone except owner
      if (modLevel === 2 && targetLevel === 2) {
        return res.status(403).json({
          error: "Owners cannot ban other owners"
        });
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
          return res.status(403).json({
            error: "Admins cannot unban other admins or owners unless they banned them"
          });
        }
      }

      // Owner can unban anyone except owner
      if (modLevel === 2 && targetLevel === 2) {
        return res.status(403).json({
          error: "Owners cannot unban other owners"
        });
      }

      // Unban the user
      users[targetIndex].blacklisted = false;
      delete users[targetIndex].ban_reason;
      delete users[targetIndex].banned_by;
      delete users[targetIndex].banned_at;

    } else if (action === 'check') {
      // Just return status without modifying
      return res.status(200).json({
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
      });
    }

    // Save updated users
    await saveUsers(users, sha);

    return res.status(200).json({
      success: true,
      action: action,
      target_alias: target_alias,
      moderator_alias: moderator_alias,
      message: `User ${target_alias} has been ${action === 'ban' ? 'banned' : 'unbanned'} successfully`
    });

  } catch (error) {
    console.error('Error in ban_chat:', error);
    
    return res.status(error.status || 500).json({
      error: error.data?.message || error.message || "Failed to perform ban action"
    });
  }
}
