// Sh*t here we go againnnnnnnnnnn

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
    try {
      return JSON.parse(content);
    } catch {
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
  
  const validPattern = /^[a-zA-Z0-9_\- ]+$/;
  if (!validPattern.test(trimmed)) {
    return { valid: false, error: "Only letters, numbers, spaces, underscores, and hyphens allowed" };
  }
  
  return { valid: true, alias: trimmed };
}

// Handle creating a new user
async function handleCreateUser(body) {
  const { alias, metadata = {} } = body;
  
  const validation = validateAlias(alias);
  if (!validation.valid) {
    return {
      statusCode: 400,
      body: JSON.stringify({ 
        error: validation.error,
        field: "alias"
      })
    };
  }
  
  const validatedAlias = validation.alias;
  
  try {
    const users = await readUsers();
    const sha = await getFileSha();
    
    if (aliasExists(users, validatedAlias)) {
      return {
        statusCode: 409,
        body: JSON.stringify({ 
          error: "Username already taken",
          alias: validatedAlias,
          available: false
        })
      };
    }
    
    const newUser = {
      alias: validatedAlias,
      permissions: metadata.permissions || "user",
      blacklisted: false
    };
    
    users.push(newUser);
    
    await saveUsers(users, sha);
    
    return {
      statusCode: 201,
      body: JSON.stringify({
        success: true,
        message: "User created successfully",
        data: {
          alias: newUser.alias,
          permissions: newUser.permissions,
          available: true
        }
      })
    };
    
  } catch (error) {
    console.error('Error creating user:', error);
    return {
      statusCode: error.status || 500,
      body: JSON.stringify({
        error: error.data?.message || error.message || "Failed to create user"
      })
    };
  }
}

// Handle checking if alias exists
async function handleCheckAlias(query) {
  const { alias } = query;
  
  if (!alias) {
    return {
      statusCode: 400,
      body: JSON.stringify({
        error: "Alias parameter is required"
      })
    };
  }
  
  const validation = validateAlias(alias);
  if (!validation.valid) {
    return {
      statusCode: 400,
      body: JSON.stringify({
        error: validation.error,
        available: false
      })
    };
  }
  
  try {
    const users = await readUsers();
    const exists = aliasExists(users, validation.alias);
    
    return {
      statusCode: 200,
      body: JSON.stringify({
        alias: validation.alias,
        available: !exists,
        exists: exists
      })
    };
    
  } catch (error) {
    console.error('Error checking alias:', error);
    return {
      statusCode: error.status || 500,
      body: JSON.stringify({
        error: error.data?.message || error.message || "Failed to check alias"
      })
    };
  }
}

// Handle getting all users (admin/debug)
async function handleGetUsers() {
  try {
    const users = await readUsers();
    
    const sanitizedUsers = users.map(user => ({
      alias: user.alias,
      permissions: user.permissions || "user",
      blacklisted: user.blacklisted || false
    }));
    
    return {
      statusCode: 200,
      body: JSON.stringify({
        success: true,
        count: sanitizedUsers.length,
        users: sanitizedUsers
      })
    };
    
  } catch (error) {
    console.error('Error getting users:', error);
    return {
      statusCode: error.status || 500,
      body: JSON.stringify({
        error: error.data?.message || error.message || "Failed to get users"
      })
    };
  }
}

// Main Netlify Functions handler
exports.handler = async function(event, context) {
  const { httpMethod, queryStringParameters, body } = event;
  
  // Enable CORS
  const headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Content-Type': 'application/json'
  };
  
  if (httpMethod === 'OPTIONS') {
    return {
      statusCode: 200,
      headers,
      body: ''
    };
  }
  
  switch (httpMethod) {
    case "GET":
      // If alias query param provided, check existence
      if (queryStringParameters.alias) {
        const result = await handleCheckAlias(queryStringParameters);
        return { ...result, headers };
      }
      // Otherwise return all users
      const result = await handleGetUsers();
      return { ...result, headers };
      
    case "POST":
      let parsedBody;
      try {
        parsedBody = JSON.parse(body);
      } catch (e) {
        return {
          statusCode: 400,
          headers,
          body: JSON.stringify({ error: "Invalid JSON body" })
        };
      }
      
      const postResult = await handleCreateUser(parsedBody);
      return { ...postResult, headers };
      
    default:
      return {
        statusCode: 405,
        headers,
        body: JSON.stringify({ 
          error: "Method not allowed",
          allowed: ["GET", "POST", "OPTIONS"]
        })
      };
  }
};