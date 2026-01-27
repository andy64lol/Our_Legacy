const GITHUB_API = "https://api.github.com";
const PROFANITY_WORDS_URL = "https://raw.githubusercontent.com/zautumnz/profane-words/refs/heads/master/words.json";

async function githubFetch(url, options) {
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

async function getFileSha(owner, repo, path, headers) {
  try {
    const data = await githubFetch(
      `${GITHUB_API}/repos/${owner}/${repo}/contents/${path}`,
      { headers }
    );
    return data.sha;
  } catch {
    return null;
  }
}

async function fetchProfanityWords() {
  try {
    const response = await fetch(PROFANITY_WORDS_URL);
    if (!response.ok) {
      throw new Error(`Failed to fetch profanity words: ${response.status}`);
    }
    const words = await response.json();
    return words;
  } catch (error) {
    console.error('Error fetching profanity words:', error);
    return [];
  }
}

function containsProfanity(text, profanityWords) {
  if (!text || typeof text !== 'string') return false;
  
  const lowerText = text.toLowerCase();
  for (const word of profanityWords) {
    if (typeof word === 'string' && word.trim()) {
      const escapedWord = word.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
      const regex = new RegExp(`\\b${escapedWord}\\b`, 'i');
      if (regex.test(text)) {
        return true;
      }
    }
  }
  return false;
}

function isJsonFile(filename) {
  if (!filename || typeof filename !== 'string') return false;
  return filename.toLowerCase().endsWith('.json');
}

function validateFileExtension(filename) {
  if (!isJsonFile(filename)) {
    return {
      valid: false,
      error: `File "${filename}" is not a JSON file. Only .json files are allowed.`
    };
  }
  return { valid: true };
}

export default async function handler(req, res) {
  if (req.method !== "POST") {
    return res.status(405).json({ error: "POST only" });
  }

  try {
    const { dir_name, files } = req.body;

    if (!dir_name || !files || typeof files !== "object") {
      return res.status(400).json({
        error: "dir_name and files object required"
      });
    }

    if (!files["mod.json"]) {
      return res.status(400).json({
        error: "Directory must contain mod.json"
      });
    }

    // 检查所有文件是否都是JSON文件
    for (const filename of Object.keys(files)) {
      const validation = validateFileExtension(filename);
      if (!validation.valid) {
        return res.status(400).json({
          error: validation.error
        });
      }
    }

    // 获取不雅词汇列表
    const profanityWords = await fetchProfanityWords();
    if (profanityWords.length === 0) {
      return res.status(500).json({
        error: "Failed to load profanity filter list"
      });
    }

    // 检查目录名是否包含不雅词汇
    if (containsProfanity(dir_name, profanityWords)) {
      return res.status(400).json({
        error: "Directory name contains prohibited content"
      });
    }

    // 检查文件名是否包含不雅词汇
    for (const filename of Object.keys(files)) {
      // 检查完整路径
      if (containsProfanity(filename, profanityWords)) {
        return res.status(400).json({
          error: `Filename "${filename}" contains prohibited content`
        });
      }
      
      // 检查路径的各个部分
      const pathParts = filename.split('/');
      for (const part of pathParts) {
        if (containsProfanity(part, profanityWords)) {
          return res.status(400).json({
            error: `Filename part "${part}" contains prohibited content`
          });
        }
      }
    }

    // 检查文件内容是否包含不雅词汇
    for (const [filename, content] of Object.entries(files)) {
      if (typeof content !== 'string') continue;
      
      // 如果不是base64编码的内容，直接检查
      if (!/^[A-Za-z0-9+/=]+$/.test(content)) {
        if (containsProfanity(content, profanityWords)) {
          return res.status(400).json({
            error: `File "${filename}" content contains prohibited content`
          });
        }
      } else {
        // 如果是base64编码的内容，先解码再检查
        try {
          const decodedContent = Buffer.from(content, 'base64').toString('utf-8');
          if (containsProfanity(decodedContent, profanityWords)) {
            return res.status(400).json({
              error: `File "${filename}" content contains prohibited content`
            });
          }
        } catch (decodeError) {
          // 如果解码失败，跳过内容检查
          console.error(`Failed to decode base64 content for file ${filename}:`, decodeError);
        }
      }
    }

    const token = process.env.GITHUB_REST_API;
    const owner = process.env.GITHUB_USERNAME;
    const repo = process.env.GITHUB_REPOSITORY;

    const headers = {
      Authorization: `Bearer ${token}`,
      Accept: "application/vnd.github+json",
      "X-GitHub-Api-Version": "2022-11-28"
    };

    const baseDir = `mods/${dir_name}`;

    // 🚫 如果目录已存在，拒绝请求
    if (await directoryExists(owner, repo, baseDir, headers)) {
      return res.status(409).json({
        error: "Mod directory already exists"
      });
    }

    const uploaded = [];

    for (const [relativePath, content] of Object.entries(files)) {
      const fullPath = `${baseDir}/${relativePath}`;

      const encoded =
        /^[A-Za-z0-9+/=]+$/.test(content)
          ? content
          : Buffer.from(content).toString("base64");

      const payload = {
        message: `Add mod ${dir_name}`,
        content: encoded
      };

      await githubFetch(
        `${GITHUB_API}/repos/${owner}/${repo}/contents/${fullPath}`,
        {
          method: "PUT",
          headers,
          body: JSON.stringify(payload)
        }
      );

      uploaded.push(fullPath);
    }

    return res.status(200).json({
      success: true,
      directory: baseDir,
      files: uploaded
    });

  } catch (err) {
    return res.status(err.status || 500).json({
      error: err.data?.message || err.message || "Internal server error"
    });
  }
}