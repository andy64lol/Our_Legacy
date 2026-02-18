const GITHUB_API = "https://api.github.com";
const REPO_OWNER = "andy64lol";
const REPO_NAME = "globalchat";
const BRANCH = "main";
const FILE_PATH = "global_chat.toml";

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
      data,
      message:
        data?.message ||
        `GitHub API request failed with status ${response.status}`
    };
  }

  return data;
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

async function getFileContent() {
  const data = await githubFetch(
    `${GITHUB_API}/repos/${REPO_OWNER}/${REPO_NAME}/contents/${FILE_PATH}?ref=${BRANCH}`
  );

  if (!data.content) {
    throw new Error("File content not found in API response");
  }

  return Buffer.from(data.content, "base64").toString("utf-8");
}

export default async function handler(req, res) {
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Methods", "GET, OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type");

  if (req.method === "OPTIONS") {
    return res.status(200).end();
  }

  if (req.method !== "GET") {
    return res.status(405).json({
      error: "Method not allowed",
      allowed: ["GET"]
    });
  }

  try {
    const tomlContent = await getFileContent();
    const messages = parseTOML(tomlContent);

    const { limit = 50, offset = 0 } = req.query;

    const limitNum = isNaN(parseInt(limit))
      ? 50
      : Math.max(1, Math.min(parseInt(limit), 100));

    const offsetNum = isNaN(parseInt(offset))
      ? 0
      : Math.max(0, parseInt(offset));

    const start = Math.min(offsetNum, messages.length);
    const end = Math.min(start + limitNum, messages.length);

    return res.status(200).json({
      success: true,
      data: {
        messages: messages.slice(start, end),
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
    });
  } catch (error) {
    console.error("Legacy messages API error:", error);

    if (error.status === 404) {
      return res.status(404).json({
        error: "Messages file not found",
        data: {
          messages: [],
          total: 0,
          limit: 50,
          offset: 0,
          hasMore: false
        }
      });
    }

    if (error.status === 401 || error.status === 403) {
      return res.status(500).json({
        error: "Authentication failed",
        message: "Check your GitHub token."
      });
    }

    return res.status(error.status || 500).json({
      error: "Failed to fetch messages",
      message: error.data?.message || error.message
    });
  }
}