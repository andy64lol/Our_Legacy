const GITHUB_API = "https://api.github.com";

async function getFileSha(owner, repo, path, headers) {
  const res = await fetch(
    `${GITHUB_API}/repos/${owner}/${repo}/contents/${path}`,
    { headers }
  );

  if (res.status === 200) {
    const data = await res.json();
    return data.sha;
  }
  return null;
}

export default async function handler(req, res) {
  if (req.method !== "POST") {
    return res.status(405).json({ error: "POST only" });
  }

  try {
    const { content, remote_path, message } = req.body;

    if (!content || !remote_path) {
      return res.status(400).json({
        error: "content and remote_path required"
      });
    }

    const token = process.env.GITHUB_REST_API;
    const username = process.env.GITHUB_USERNAME;
    const repo = process.env.GITHUB_REPOSITORY;

    if (!token || !username || !repo) {
      return res.status(500).json({
        error: "Missing GitHub env vars"
      });
    }

    const headers = {
      Authorization: `Bearer ${token}`,
      Accept: "application/vnd.github+json",
      "X-GitHub-Api-Version": "2022-11-28"
    };

    // If not base64, encode
    const encoded =
      /^[A-Za-z0-9+/=]+$/.test(content)
        ? content
        : Buffer.from(content).toString("base64");

    const sha = await getFileSha(username, repo, remote_path, headers);

    const payload = {
      message: message || `Upload ${remote_path}`,
      content: encoded,
      ...(sha && { sha })
    };

    const r = await fetch(
      `${GITHUB_API}/repos/${username}/${repo}/contents/${remote_path}`,
      {
        method: "PUT",
        headers,
        body: JSON.stringify(payload)
      }
    );

    const data = await r.json();

    if (!r.ok) {
      return res.status(r.status).json({ error: data });
    }

    return res.status(200).json({
      success: true,
      url: data.content.html_url
    });

  } catch (err) {
    return res.status(500).json({ error: err.message });
  }
}