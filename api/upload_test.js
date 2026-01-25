const GITHUB_API = "https://api.github.com";

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

    const token = process.env.GITHUB_REST_API;
    const owner = process.env.GITHUB_USERNAME;
    const repo = process.env.GITHUB_REPOSITORY;

    const headers = {
      Authorization: `Bearer ${token}`,
      Accept: "application/vnd.github+json",
      "X-GitHub-Api-Version": "2022-11-28"
    };

    const baseDir = `mods/${dir_name}`;

    // 🚫 reject if directory exists
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
      error: err.data || err.message
    });
  }
}