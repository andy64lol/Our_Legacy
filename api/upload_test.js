// Check if all files are JSON files
for (const filename of Object.keys(files)) {
  const validation = validateFileExtension(filename);
  if (!validation.valid) {
    return res.status(400).json({
      error: validation.error
    });
  }
}

// Fetch the list of profanity words
const profanityWords = await fetchProfanityWords();
if (profanityWords.length === 0) {
  return res.status(500).json({
    error: "Failed to load profanity filter list"
  });
}

// Check if the directory name contains profanity
if (containsProfanity(dir_name, profanityWords)) {
  return res.status(400).json({
    error: "Directory name contains prohibited content"
  });
}

// Check if filenames contain profanity
for (const filename of Object.keys(files)) {
  // Check the full path
  if (containsProfanity(filename, profanityWords)) {
    return res.status(400).json({
      error: `Filename "${filename}" contains prohibited content`
    });
  }
  
  // Check each part of the path
  const pathParts = filename.split('/');
  for (const part of pathParts) {
    if (containsProfanity(part, profanityWords)) {
      return res.status(400).json({
        error: `Filename part "${part}" contains prohibited content`
      });
    }
  }
}

// Check if file content contains profanity
for (const [filename, content] of Object.entries(files)) {
  if (typeof content !== 'string') continue;
  
  // If the content is not base64 encoded, check directly
  if (!/^[A-Za-z0-9+/=]+$/.test(content)) {
    if (containsProfanity(content, profanityWords)) {
      return res.status(400).json({
        error: `File "${filename}" content contains prohibited content`
      });
    }
  } else {
    // If the content is base64 encoded, decode first then check
    try {
      const decodedContent = Buffer.from(content, 'base64').toString('utf-8');
      if (containsProfanity(decodedContent, profanityWords)) {
        return res.status(400).json({
          error: `File "${filename}" content contains prohibited content`
        });
      }
    } catch (decodeError) {
      // If decoding fails, skip content check
      console.error(`Failed to decode base64 content for file ${filename}:`, decodeError);
    }
  }
}

// If the directory already exists, reject the request
if (await directoryExists(owner, repo, baseDir, headers)) {
  return res.status(409).json({
    error: "Mod directory already exists"
  });
}
