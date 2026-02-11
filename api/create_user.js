// User Management API for Our Legacy
// Repository: andy64lol/globalchat
// File: users.json on main branch

const GITHUB_API = "https://api.github.com";
const REPO_OWNER = "andy64lol";
const REPO_NAME = "globalchat";
const BRANCH = "main";
const FILE_PATH = "users.json";

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

// Read users from the repository
async function readUsers() {
  const rawUrl = `https://raw.githubusercontent.com/${REPO_OWNER}/${REPO_NAME}/${BRANCH}/${FILE_PATH}`;
  
  try {
    const response = await fetch(rawUrl);
    if (!response.ok) {
      if (response.status === 404) {
        return [];
      }
      throw new Error(`Failed to fetch users: ${response.status}`);
    }
    const content = await response.text();
    // GitHub API returns base64 encoded content, but raw URL returns plain text
    try {
      // Try parsing as JSON first (raw URL returns JSON)
      return JSON.parse(content);
    } catch {
      // If that fails, try base64 decoding
      const decoded = Buffer.from(content, 'base64').toString('utf-8');
      return JSON.parse(decoded);
    }
  } catch (error) {
    console.error('Error reading users:', error);
    return [];
  }
}

// Save users to repository
async function saveUsers(users, sha = null) {
  const content = JSON.stringify(users, null, 2);
  const encoded = Buffer.from(content).toString('base64');
  
  const payload = {
    message: `Add new user: ${users.length} total users`,
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

// Check if alias exists (case-insensitive)
function aliasExists(users, alias) {
  const lowerAlias = alias.toLowerCase();
  return users.some(user => 
    user && typeof user === 'object' && 
    user.alias && user.alias.toLowerCase() === lowerAlias
  );
}

// Validate alias format
function validateAlias(alias) {
  if (!alias || typeof alias !== 'string') {
    return { valid: false, error: "Alias is required and must be a string" };
  }
  
  const trimmed = alias.trim();
  
  if (!trimmed) {
    return { valid: false, error: "Alias cannot be empty" };
  }
  
  if (trimmed.length > 20) {
    return { valid: false, error: "Alias too long (max 20 characters)" };
  }
  
  // Allow letters, numbers, spaces, underscores, and hyphens
  const validPattern = /^[a-zA-Z0-9_\- ]+$/;
  if (!validPattern.test(trimmed)) {
    return { valid: false, error: "Only letters, numbers, spaces, underscores, and hyphens allowed" };
  }
  
  return { valid: true, alias: trimmed };
}

// Handle creating a new user
async function handleCreateUser(req, res) {
  const { alias, metadata = {} } = req.body;
  
  // Validate alias format
  const validation = validateAlias(alias);
  if (!validation.valid) {
    return res.status(400).json({ 
      error: validation.error,
      field: "alias"
    });
  }
  
  const validatedAlias = validation.alias;
  
  try {
    // Read current users
    const users = await readUsers();
    const sha = await getFileSha();
    
    // Check if alias already exists
    if (aliasExists(users, validatedAlias)) {
      return res.status(409).json({ 
        error: "Username already taken",
        alias: validatedAlias,
        available: false
      });
    }
    
    // Create new user with standard structure
    const newUser = {
      alias: validatedAlias,
      permissions: metadata.permissions || "user",
      blacklisted: false
    };
    
    // Add to users list
    users.push(newUser);
    
    // Save updated users
    await saveUsers(users, sha);
    
    return res.status(201).json({
      success: true,
      message: "User created successfully",
      data: {
        alias: newUser.alias,
        permissions: newUser.permissions,
        available: true
      }
    });
    
  } catch (error) {
    console.error('Error creating user:', error);
    return res.status(error.status || 500).json({
      error: error.data?.message || error.message || "Failed to create user"
    });
  }
}

// Handle checking if alias exists
async function handleCheckAlias(req, res) {
  const { alias } = req.query;
  
  if (!alias) {
    return res.status(400).json({
      error: "Alias parameter is required"
    });
  }
  
  // Validate format
  const validation = validateAlias(alias);
  if (!validation.valid) {
    return res.status(400).json({
      error: validation.error,
      available: false
    });
  }
  
  try {
    const users = await readUsers();
    const exists = aliasExists(users, validation.alias);
    
    return res.status(200).json({
      alias: validation.alias,
      available: !exists,
      exists: exists
    });
    
  } catch (error) {
    console.error('Error checking alias:', error);
    return res.status(error.status || 500).json({
      error: error.data?.message || error.message || "Failed to check alias"
    });
  }
}

// Handle getting all users (admin/debug)
async function handleGetUsers(req, res) {
  try {
    const users = await readUsers();
    
    // Return sanitized list (no sensitive data)
    const sanitizedUsers = users.map(user => ({
      alias: user.alias,
      permissions: user.permissions || "user",
      blacklisted: user.blacklisted || false
    }));
    
    return res.status(200).json({
      success: true,
      count: sanitizedUsers.length,
      users: sanitizedUsers
    });
    
  } catch (error) {
    console.error('Error getting users:', error);
    return res.status(error.status || 500).json({
      error: error.data?.message || error.message || "Failed to get users"
    });
  }
}

// Main handler
export default async function handler(req, res) {
  const { method, query } = req;
  
  // Enable CORS
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  
  if (method === 'OPTIONS') {
    return res.status(200).end();
  }
  
  switch (method) {
    case "GET":
      // If alias query param provided, check existence
      if (query.alias) {
        return handleCheckAlias(req, res);
      }
      // Otherwise return all users
      return handleGetUsers(req, res);
    case "POST":
      return handleCreateUser(req, res);
    default:
      return res.status(405).json({ 
        error: "Method not allowed",
        allowed: ["GET", "POST", "OPTIONS"]
      });
  }
}
