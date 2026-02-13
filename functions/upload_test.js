// I was about to name this file upload_mod.js but realised that the another file is named upload_test.js because I forgot to rename this, btw im lazy to rename, i am always sleeping.

const GITHUB_API = "https://api.github.com";
const PROFANITY_WORDS_URL = "https://raw.githubusercontent.com/zautumnz/profane-words/refs/heads/master/words.json";

async function githubFetch(url, options = {}) {
  const r = await fetch(url, options);
  const data = await r.json();
  if (!r.ok) throw { status: r.status, data };
  return data;
}

async function directoryExists(owner, repo, dir, headers) {
  try {
    await githubFetch(
      `${GITHUB_API}/repos/${owner}/${repo}/contents/${dir}`,
      { headers }
    );
    return true;
  } catch {
    return false;
  }
}

async function fetchProfanityWords() {
  try {
    const response = await fetch(PROFANITY_WORDS_URL);
    if (!response.ok) throw new Error(`Failed to fetch profanity words: ${response.status}`);
    return await response.json();
  } catch (e) {
    console.error('Error fetching profanity words:', e);
    return [];
  }
}

function containsProfanity(text, profanityWords) {
  if (!text || typeof text !== 'string') return false;
  const lowerText = text.toLowerCase();
  for (const word of profanityWords) {
    if (typeof word === 'string' && word.trim()) {
      const escaped = word.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
      const regex = new RegExp(`\\b${escaped}\\b`, 'i');
      if (regex.test(lowerText)) return true;
    }
  }
  return false;
}

function isJsonFile(filename) {
  return typeof filename === 'string' && filename.toLowerCase().endsWith('.json');
}

function validateFileExtension(filename) {
  if (!isJsonFile(filename)) return { valid: false, error: `File "${filename}" is not a JSON file.` };
  return { valid: true };
}

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

  if (event.httpMethod !== "POST") {
    return { statusCode: 405, headers, body: JSON.stringify({ error: "POST only" }) };
  }

  let body;
  try { body = JSON.parse(event.body); } 
  catch { return { statusCode: 400, headers, body: JSON.stringify({ error: "Invalid JSON body" }) }; }

  const { dir_name, files } = body;
  if (!dir_name || !files || typeof files !== 'object') {
    return { statusCode: 400, headers, body: JSON.stringify({ error: "dir_name and files object required" }) };
  }

  if (!files["mod.json"]) {
    return { statusCode: 400, headers, body: JSON.stringify({ error: "Directory must contain mod.json" }) };
  }

  // Check JSON file extensions
  for (const filename of Object.keys(files)) {
    const validation = validateFileExtension(filename);
    if (!validation.valid) return { statusCode: 400, headers, body: JSON.stringify({ error: validation.error }) };
  }

  const profanityWords = await fetchProfanityWords();
  if (!profanityWords.length) return { statusCode: 500, headers, body: JSON.stringify({ error: "Failed to load profanity filter list" }) };

  // Directory name profanity check
  if (containsProfanity(dir_name, profanityWords)) return { statusCode: 400, headers, body: JSON.stringify({ error: "Directory name contains prohibited content" }) };

  // Filename profanity check
  for (const filename of Object.keys(files)) {
    if (containsProfanity(filename, profanityWords)) return { statusCode: 400, headers, body: JSON.stringify({ error: `Filename "${filename}" contains prohibited content` }) };
    for (const part of filename.split('/')) {
      if (containsProfanity(part, profanityWords)) return { statusCode: 400, headers, body: JSON.stringify({ error: `Filename part "${part}" contains prohibited content` }) };
    }
  }

  // File content profanity check
  for (const [filename, content] of Object.entries(files)) {
    if (typeof content !== 'string') continue;
    let decoded = content;
    if (/^[A-Za-z0-9+/=]+$/.test(content)) {
      try { decoded = Buffer.from(content, 'base64').toString('utf-8'); } catch (e) { console.error(e); }
    }
    if (containsProfanity(decoded, profanityWords)) return { statusCode: 400, headers, body: JSON.stringify({ error: `File "${filename}" content contains prohibited content` }) };
  }

  const token = process.env.GITHUB_REST_API;
  const owner = process.env.GITHUB_USERNAME;
  const repo = process.env.GITHUB_REPOSITORY;

  const githubHeaders = {
    Authorization: `Bearer ${token}`,
    Accept: "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28"
  };

  const baseDir = `mods/${dir_name}`;
  if (await directoryExists(owner, repo, baseDir, githubHeaders)) {
    return { statusCode: 409, headers, body: JSON.stringify({ error: "Mod directory already exists" }) };
  }

  const uploaded = [];
  for (const [relativePath, content] of Object.entries(files)) {
    const fullPath = `${baseDir}/${relativePath}`;
    const encoded = /^[A-Za-z0-9+/=]+$/.test(content) ? content : Buffer.from(content).toString("base64");
    const payload = { message: `Add mod ${dir_name}`, content: encoded };
    await githubFetch(`${GITHUB_API}/repos/${owner}/${repo}/contents/${fullPath}`, { method: "PUT", headers: githubHeaders, body: JSON.stringify(payload) });
    uploaded.push(fullPath);
  }

  return { statusCode: 200, headers, body: JSON.stringify({ success: true, directory: baseDir, files: uploaded }) };
};
