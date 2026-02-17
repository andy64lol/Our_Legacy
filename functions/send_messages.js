const GITHUB_API = "https://api.github.com";
const REPO_OWNER = "andy64lol";
const REPO_NAME = "globalchat";
const BRANCH = "main";
const FILE_PATH = "global_chat.toml";
const OLD_MESSAGES_DIR = "old_messages";
const MAX_MESSAGES = 1000;
const MESSAGES_TO_KEEP = 20;
const PROFANITY_WORDS_URL = "https://raw.githubusercontent.com/zautumnz/profane-words/refs/heads/master/words.json";

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

async function fetchProfanityWords() {
  try {
    const response = await fetch(PROFANITY_WORDS_URL);
    if (!response.ok) throw new Error(`Failed: ${response.status}`);
    return await response.json();
  } catch {
    return [];
  }
}

function containsProfanity(text, profanityWords) {
  if (!text || typeof text !== "string") return false;

  for (const word of profanityWords) {
    if (typeof word === "string" && word.trim()) {
      const escaped = word.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
      const regex = new RegExp(`\\b${escaped}\\b`, "i");
      if (regex.test(text)) return true;
    }
  }

  return false;
}

function parseTOML(text) {
  const messages = [];
  const blocks = text.split("[[messages]]").slice(1);

  for (const block of blocks) {
    const message = {};
    const lines = block.trim().split("\n");

    for (const line of lines) {
      const trimmed = line.trim();
      if (!trimmed || trimmed.startsWith("#")) continue;

      const match = trimmed.match(/^(\w+)\s*=\s*"([^"]*)"/);
      if (match) message[match[1]] = match[2];
    }

    if (message.content && message.author) messages.push(message);
  }

  return messages;
}

function serializeTOML(messages) {
  if (!messages.length) return "";

  const lines = [];

  for (const msg of messages) {
    lines.push("[[messages]]");
    lines.push(`content = "${msg.content.replace(/"/g, '\\"')}"`);
    lines.push(`author = "${msg.author.replace(/"/g, '\\"')}"`);
    lines.push(`timestamp = "${msg.timestamp}"`);
    lines.push(`id = "${msg.id}"`);
    lines.push("");
  }

  return lines.join("\n");
}

async function readMessages() {
  const rawUrl = `https://raw.githubusercontent.com/${REPO_OWNER}/${REPO_NAME}/refs/heads/${BRANCH}/${FILE_PATH}`;

  const response = await fetch(rawUrl, { cache: "no-store" });

  if (!response.ok) {
    if (response.status === 404) return [];
    throw new Error(`Failed: ${response.status}`);
  }

  const text = await response.text();
  return parseTOML(text);
}

async function saveMessages(messages, sha = null) {
  const content = serializeTOML(messages);
  const encoded = Buffer.from(content).toString("base64");

  const payload = {
    message: messages.length
      ? `Update chat: ${messages.length} messages`
      : "Initialize chat",
    content: encoded,
    branch: BRANCH
  };

  if (sha) payload.sha = sha;

  return await githubFetch(
    `${GITHUB_API}/repos/${REPO_OWNER}/${REPO_NAME}/contents/${FILE_PATH}`,
    {
      method: "PUT",
      body: JSON.stringify(payload)
    }
  );
}

async function archiveMessages(messages) {
  const timestamp = messages.length
    ? messages[messages.length - 1].timestamp
    : Date.now();

  const archiveFilename = `${OLD_MESSAGES_DIR}/${timestamp}_chat.toml`;
  const content = serializeTOML(messages);
  const encoded = Buffer.from(content).toString("base64");

  await githubFetch(
    `${GITHUB_API}/repos/${REPO_OWNER}/${REPO_NAME}/contents/${archiveFilename}`,
    {
      method: "PUT",
      body: JSON.stringify({
        message: `Archive ${messages.length} old messages`,
        content: encoded,
        branch: BRANCH
      })
    }
  );
}

exports.handler = async function (event) {
  // CORS headers
  const headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
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

  const method = event.httpMethod;

  if (method === "GET") {
    const { limit = 50, offset = 0 } = event.queryStringParameters || {};

    try {
      const messages = await readMessages();
      const start = Math.min(parseInt(offset), messages.length);
      const end = Math.min(start + parseInt(limit), messages.length);

      return {
        statusCode: 200,
        headers,
        body: JSON.stringify({
          success: true,
          data: {
            messages: messages.slice(start, end),
            total: messages.length,
            limit: parseInt(limit),
            offset: parseInt(offset),
            hasMore: end < messages.length
          }
        })
      };
    } catch (error) {
      return {
        statusCode: 500,
        headers,
        body: JSON.stringify({ error: error.message })
      };
    }
  }

  if (method === "POST") {
    const body = JSON.parse(event.body || "{}");
    const { message, author } = body;

    if (!message || !author) {
      return {
        statusCode: 400,
        headers,
        body: JSON.stringify({ error: "Message and author required" })
      };
    }

    if (message.length > 300 || author.length > 50) {
      return {
        statusCode: 400,
        headers,
        body: JSON.stringify({ error: "Input too long" })
      };
    }

    const profanityWords = await fetchProfanityWords();

    if (
      containsProfanity(message, profanityWords) ||
      containsProfanity(author, profanityWords)
    ) {
      return {
        statusCode: 400,
        headers,
        body: JSON.stringify({ error: "Prohibited content", filtered: true })
      };
    }

    try {
      let messages = await readMessages();
      const sha = await getFileSha();

      const newMessage = {
        content: message.trim(),
        author: author.trim(),
        timestamp: Date.now().toString(),
        id: `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
      };

      messages.push(newMessage);
      await saveMessages(messages, sha);

      if (messages.length >= MAX_MESSAGES) {
        await archiveMessages(messages);
        messages = messages.slice(-MESSAGES_TO_KEEP);
      }

      return {
        statusCode: 200,
        headers,
        body: JSON.stringify({
          success: true,
          data: {
            id: newMessage.id,
            timestamp: newMessage.timestamp,
            position: messages.length
          }
        })
      };
    } catch (error) {
      return {
        statusCode: error.status || 500,
        headers,
        body: JSON.stringify({
          error: error.data?.message || error.message
        })
      };
    }
  }

  return {
    statusCode: 405,
    headers,
    body: JSON.stringify({
      error: "Method not allowed",
      allowed: ["GET", "POST"]
    })
  };
};
