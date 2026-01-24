// api/upload.js
// Vercel Serverless API for uploading mods to GitHub repository
// Upload mods to: https://github.com/andy64lol/Our_Legacy_Mods/tree/main

import { Octokit } from "octokit";

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({
      ok: false,
      error: "Method not allowed. Use POST request."
    });
  }

  const { modName, fileName, fileContent, commitMessage } = req.body;

  // Validate required fields
  if (!modName || !fileName || !fileContent) {
    return res.status(400).json({
      ok: false,
      error: "Missing required fields: modName, fileName, and fileContent are required."
    });
  }

  // Get GitHub token from environment variables
  const GITHUB_TOKEN = process.env.GITHUB_TOKEN;
  const REPO_OWNER = process.env.GITHUB_REPO_OWNER || "andy64lol";
  const REPO_NAME = process.env.GITHUB_REPO_NAME || "Our_Legacy_Mods";
  const BRANCH = process.env.GITHUB_BRANCH || "main";

  if (!GITHUB_TOKEN) {
    return res.status(500).json({
      ok: false,
      error: "GitHub token not configured. Set GITHUB_TOKEN environment variable."
    });
  }

  try {
    // Initialize Octokit with authentication
    const octokit = new Octokit({
      auth: GITHUB_TOKEN
    });

    // File path in the repository
    const filePath = `mods/${modName}/${fileName}`;
    
    // Commit message
    const message = commitMessage || `Upload ${fileName} to ${modName}`;
    
    // Get the current file SHA if it exists (for updates)
    let sha = null;
    try {
      const { data: existingFile } = await octokit.rest.repos.getContent({
        owner: REPO_OWNER,
        repo: REPO_NAME,
        path: filePath,
        ref: BRANCH
      });
      
      if (existingFile && existingFile.sha) {
        sha = existingFile.sha;
      }
    } catch (error) {
      // File doesn't exist yet, which is fine for new uploads
      if (error.status !== 404) {
        throw error;
      }
    }

    // Encode content to base64
    const encodedContent = Buffer.from(fileContent).toString('base64');

    // Upload/update the file
    const response = await octokit.rest.repos.createOrUpdateFileContents({
      owner: REPO_OWNER,
      repo: REPO_NAME,
      path: filePath,
      message: message,
      content: encodedContent,
      branch: BRANCH,
      sha: sha // Include SHA for updates, omit for new files
    });

    console.log(`[Upload API] Successfully uploaded: ${filePath}`);

    return res.status(200).json({
      ok: true,
      message: `Successfully uploaded ${fileName} to ${modName}`,
      data: {
        modName,
        fileName,
        path: filePath,
        sha: response.data.content.sha,
        url: response.data.content.html_url,
        commit: {
          sha: response.data.commit.sha,
          message: response.data.commit.message
        }
      }
    });

  } catch (error) {
    console.error("[Upload API] Error:", error.message);
    
    // Handle specific GitHub API errors
    if (error.status === 401) {
      return res.status(401).json({
        ok: false,
        error: "Authentication failed. Invalid GitHub token."
      });
    }
    
    if (error.status === 403) {
      return res.status(403).json({
        ok: false,
        error: "Permission denied. Check repository access permissions."
      });
    }
    
    if (error.status === 404) {
      return res.status(404).json({
        ok: false,
        error: "Repository or path not found."
      });
    }

    return res.status(500).json({
      ok: false,
      error: error.message || "Failed to upload file to GitHub"
    });
  }
}

// Export config for Vercel
export const config = {
  api: {
    bodyParser: {
      sizeLimit: '10mb' // Allow up to 10MB file uploads
    }
  }
};

