/**
 * Login Fetch API - Dedicated endpoint for handling login requests
 * This file provides a simplified interface for CLI-based login operations
 */

import { createClient } from '@supabase/supabase-js';
import crypto from 'crypto';

// Initialize Supabase client with service role key
const supabaseUrl = process.env.SUPABASE_URL;
const supabaseServiceKey = process.env.SUPABASE_SERVICE_ROLE_KEY;

const supabase = createClient(supabaseUrl, supabaseServiceKey);

/**
 * Verify password against hash
 */
function verifyPassword(password, hashedPassword) {
  const [salt, hash] = hashedPassword.split(':');
  const verifyHash = crypto.pbkdf2Sync(password, salt, 10000, 64, 'sha512').toString('hex');
  return hash === verifyHash;
}

/**
 * Find account by username
 */
async function findByUsername(username) {
  const { data, error } = await supabase
    .from('accounts')
    .select('*')
    .ilike('username', username)
    .single();
  
  if (error && error.code !== 'PGRST116') {
    console.error('Error finding by username:', error);
  }
  return data;
}

/**
 * Update last login timestamp
 */
async function updateLastLogin(accountId) {
  try {
    const now = new Date().toISOString();
    await supabase
      .from('accounts')
      .update({ last_login: now })
      .eq('account_id', accountId);
  } catch (error) {
    console.error('Error updating last login:', error);
  }
}

/**
 * Main handler for login requests
 */
export default async function handler(req, res) {
  // Set CORS headers for CLI access
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  // Only allow POST requests
  if (req.method !== 'POST') {
    return res.status(405).json({
      ok: false,
      error: 'Method not allowed',
      message: 'Only POST requests are supported for login'
    });
  }

  try {
    const { username, password } = req.body;

    // Validate input
    if (!username || !password) {
      return res.status(400).json({
        ok: false,
        error: 'Missing credentials',
        message: 'Username and password are required'
      });
    }

    const account = await findByUsername(username);

    // Account not found
    if (!account) {
      return res.status(401).json({
        ok: false,
        error: 'Invalid credentials',
        message: 'Username or password is incorrect'
      });
    }

    // Verify password
    if (!verifyPassword(password, account.password_hash)) {
      return res.status(401).json({
        ok: false,
        error: 'Invalid credentials',
        message: 'Username or password is incorrect'
      });
    }

    // Update last login (async, don't wait)
    updateLastLogin(account.account_id);

    // Return success with account info
    return res.status(200).json({
      ok: true,
      message: 'Login successful',
      account: {
        account_id: account.account_id,
        username: account.username,
        email: account.email,
        created_at: account.created_at,
        last_login: new Date().toISOString()
      },
      timestamp: Date.now()
    });

  } catch (error) {
    console.error('Login fetch error:', error);
    return res.status(500).json({
      ok: false,
      error: 'Internal server error',
      message: error.message
    });
  }
}
