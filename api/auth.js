import { createClient } from '@supabase/supabase-js';
import crypto from 'crypto';

// Initialize Supabase client with service role key for server-side operations
const supabaseUrl = process.env.SUPABASE_URL;
const supabaseServiceKey = process.env.SUPABASE_SERVICE_ROLE_KEY;

const supabase = createClient(supabaseUrl, supabaseServiceKey);

/**
 * Hash password using PBKDF2
 */
function hashPassword(password) {
  const salt = crypto.randomBytes(16).toString('hex');
  const hash = crypto.pbkdf2Sync(password, salt, 10000, 64, 'sha512').toString('hex');
  return `${salt}:${hash}`;
}

/**
 * Verify password against hash
 */
function verifyPassword(password, hashedPassword) {
  const [salt, hash] = hashedPassword.split(':');
  const verifyHash = crypto.pbkdf2Sync(password, salt, 10000, 64, 'sha512').toString('hex');
  return hash === verifyHash;
}

/**
 * Generate secure random token
 */
function generateToken() {
  return crypto.randomBytes(32).toString('hex');
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
 * Find account by email
 */
async function findByEmail(email) {
  const { data, error } = await supabase
    .from('accounts')
    .select('*')
    .ilike('email', email)
    .single();
  
  if (error && error.code !== 'PGRST116') {
    console.error('Error finding by email:', error);
  }
  return data;
}

/**
 * Find account by ID
 */
async function findById(accountId) {
  const { data, error } = await supabase
    .from('accounts')
    .select('*')
    .eq('account_id', accountId)
    .single();
  
  if (error && error.code !== 'PGRST116') {
    console.error('Error finding by ID:', error);
  }
  return data;
}

/**
 * Validate email format
 */
function isValidEmail(email) {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
}

/**
 * Validate username format (alphanumeric, 3-20 chars)
 */
function isValidUsername(username) {
  const usernameRegex = /^[a-zA-Z0-9_]{3,20}$/;
  return usernameRegex.test(username);
}

/**
 * Validate password strength
 */
function isValidPassword(password) {
  return password.length >= 8;
}

/**
 * Register new account
 */
async function register(req, res) {
  const { username, email, password } = req.body;

  // Validation
  if (!username || !email || !password) {
    return res.status(400).json({
      ok: false,
      error: 'Missing required fields',
      message: 'Username, email, and password are required'
    });
  }

  if (!isValidUsername(username)) {
    return res.status(400).json({
      ok: false,
      error: 'Invalid username',
      message: 'Username must be 3-20 characters, alphanumeric and underscores only'
    });
  }

  if (!isValidEmail(email)) {
    return res.status(400).json({
      ok: false,
      error: 'Invalid email',
      message: 'Please provide a valid email address'
    });
  }

  if (!isValidPassword(password)) {
    return res.status(400).json({
      ok: false,
      error: 'Weak password',
      message: 'Password must be at least 8 characters long'
    });
  }

  // Check for existing username
  const existingUsername = await findByUsername(username);
  if (existingUsername) {
    return res.status(409).json({
      ok: false,
      error: 'Username taken',
      message: 'This username is already registered'
    });
  }

  // Check for existing email
  const existingEmail = await findByEmail(email);
  if (existingEmail) {
    return res.status(409).json({
      ok: false,
      error: 'Email taken',
      message: 'This email is already registered'
    });
  }

  // Create account
  const accountId = crypto.randomUUID();
  const hashedPassword = hashPassword(password);
  const now = new Date().toISOString();

  const newAccount = {
    account_id: accountId,
    username: username.toLowerCase(),
    email: email.toLowerCase(),
    password_hash: hashedPassword,
    created_at: now,
    last_login: null,
    verification_token: null,
    verification_expires: null,
    verification_used: true
  };

  const { error } = await supabase
    .from('accounts')
    .insert([newAccount]);

  if (error) {
    console.error('Error creating account:', error);
    return res.status(500).json({
      ok: false,
      error: 'Server error',
      message: 'Failed to create account'
    });
  }

  return res.status(201).json({
    ok: true,
    message: 'Account created successfully',
    account: {
      account_id: accountId,
      username: newAccount.username,
      email: newAccount.email,
      created_at: now
    }
  });
}

/**
 * Login to account
 */
async function login(req, res) {
  const { username, password } = req.body;

  if (!username || !password) {
    return res.status(400).json({
      ok: false,
      error: 'Missing credentials',
      message: 'Username and password are required'
    });
  }

  const account = await findByUsername(username);

  if (!account) {
    return res.status(401).json({
      ok: false,
      error: 'Invalid credentials',
      message: 'Username or password is incorrect'
    });
  }

  if (!verifyPassword(password, account.password_hash)) {
    return res.status(401).json({
      ok: false,
      error: 'Invalid credentials',
      message: 'Username or password is incorrect'
    });
  }

  // Update last login
  const now = new Date().toISOString();
  await supabase
    .from('accounts')
    .update({ last_login: now })
    .eq('account_id', account.account_id);

  return res.status(200).json({
    ok: true,
    message: 'Login successful',
    account: {
      account_id: account.account_id,
      username: account.username,
      email: account.email,
      last_login: now
    }
  });
}

/**
 * Request account recovery (send verification link)
 */
async function recover(req, res) {
  const { email } = req.body;

  if (!email) {
    return res.status(400).json({
      ok: false,
      error: 'Missing email',
      message: 'Email address is required'
    });
  }

  const account = await findByEmail(email);

  if (!account) {
    // Don't reveal if email exists
    return res.status(200).json({
      ok: true,
      message: 'If an account exists with this email, a recovery link will be sent'
    });
  }

  // Generate recovery token
  const token = generateToken();
  const expires = new Date();
  expires.setHours(expires.getHours() + 24); // 24 hour expiration

  const { error } = await supabase
    .from('accounts')
    .update({
      verification_token: token,
      verification_expires: expires.toISOString(),
      verification_used: false
    })
    .eq('account_id', account.account_id);

  if (error) {
    console.error('Error updating verification:', error);
    return res.status(500).json({
      ok: false,
      error: 'Server error',
      message: 'Failed to process recovery request'
    });
  }

  // In a real implementation, you would send an email here
  // For now, we return the token (in production, this would be emailed)
  return res.status(200).json({
    ok: true,
    message: 'Recovery token generated',
    // In production, remove this and send via email
    recovery_token: token,
    expires: expires.toISOString(),
    note: 'In production, this token would be sent to your email'
  });
}

/**
 * Verify recovery token
 */
async function verifyToken(req, res) {
  const { token, email } = req.body;

  if (!token || !email) {
    return res.status(400).json({
      ok: false,
      error: 'Missing parameters',
      message: 'Token and email are required'
    });
  }

  const account = await findByEmail(email);

  if (!account) {
    return res.status(404).json({
      ok: false,
      error: 'Account not found',
      message: 'No account found with this email'
    });
  }

  if (!account.verification_token || account.verification_token !== token) {
    return res.status(400).json({
      ok: false,
      error: 'Invalid token',
      message: 'The recovery token is invalid'
    });
  }

  if (account.verification_used) {
    return res.status(400).json({
      ok: false,
      error: 'Token used',
      message: 'This recovery token has already been used'
    });
  }

  if (new Date() > new Date(account.verification_expires)) {
    return res.status(400).json({
      ok: false,
      error: 'Token expired',
      message: 'This recovery token has expired'
    });
  }

  return res.status(200).json({
    ok: true,
    message: 'Token verified',
    account_id: account.account_id
  });
}

/**
 * Reset password with verified token
 */
async function resetPassword(req, res) {
  const { token, email, new_password } = req.body;

  if (!token || !email || !new_password) {
    return res.status(400).json({
      ok: false,
      error: 'Missing parameters',
      message: 'Token, email, and new password are required'
    });
  }

  if (!isValidPassword(new_password)) {
    return res.status(400).json({
      ok: false,
      error: 'Weak password',
      message: 'Password must be at least 8 characters long'
    });
  }

  const account = await findByEmail(email);

  if (!account) {
    return res.status(404).json({
      ok: false,
      error: 'Account not found',
      message: 'No account found with this email'
    });
  }

  if (!account.verification_token || account.verification_token !== token) {
    return res.status(400).json({
      ok: false,
      error: 'Invalid token',
      message: 'The recovery token is invalid'
    });
  }

  if (account.verification_used) {
    return res.status(400).json({
      ok: false,
      error: 'Token used',
      message: 'This recovery token has already been used'
    });
  }

  if (new Date() > new Date(account.verification_expires)) {
    return res.status(400).json({
      ok: false,
      error: 'Token expired',
      message: 'This recovery token has expired'
    });
  }

  // Update password and mark token as used
  const hashedPassword = hashPassword(new_password);
  const now = new Date().toISOString();

  const { error } = await supabase
    .from('accounts')
    .update({
      password_hash: hashedPassword,
      verification_used: true,
      last_login: now
    })
    .eq('account_id', account.account_id);

  if (error) {
    console.error('Error resetting password:', error);
    return res.status(500).json({
      ok: false,
      error: 'Server error',
      message: 'Failed to reset password'
    });
  }

  return res.status(200).json({
    ok: true,
    message: 'Password reset successful'
  });
}

/**
 * Get account info by ID
 */
async function getAccount(req, res) {
  const { account_id } = req.query;

  if (!account_id) {
    return res.status(400).json({
      ok: false,
      error: 'Missing account ID',
      message: 'Account ID is required'
    });
  }

  const account = await findById(account_id);

  if (!account) {
    return res.status(404).json({
      ok: false,
      error: 'Account not found',
      message: 'No account found with this ID'
    });
  }

  return res.status(200).json({
    ok: true,
    account: {
      account_id: account.account_id,
      username: account.username,
      email: account.email,
      created_at: account.created_at,
      last_login: account.last_login
    }
  });
}

/**
 * Main handler
 */
export default async function handler(req, res) {
  // Set CORS headers
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  const { action } = req.query;

  try {
    switch (action) {
      case 'register':
        if (req.method !== 'POST') {
          return res.status(405).json({ ok: false, error: 'Method not allowed' });
        }
        return await register(req, res);
      
      case 'login':
        if (req.method !== 'POST') {
          return res.status(405).json({ ok: false, error: 'Method not allowed' });
        }
        return await login(req, res);
      
      case 'recover':
        if (req.method !== 'POST') {
          return res.status(405).json({ ok: false, error: 'Method not allowed' });
        }
        return await recover(req, res);
      
      case 'verify':
        if (req.method !== 'POST') {
          return res.status(405).json({ ok: false, error: 'Method not allowed' });
        }
        return await verifyToken(req, res);
      
      case 'reset':
        if (req.method !== 'POST') {
          return res.status(405).json({ ok: false, error: 'Method not allowed' });
        }
        return await resetPassword(req, res);
      
      case 'info':
        if (req.method !== 'GET') {
          return res.status(405).json({ ok: false, error: 'Method not allowed' });
        }
        return await getAccount(req, res);
      
      default:
        return res.status(400).json({
          ok: false,
          error: 'Invalid action',
          message: 'Valid actions: register, login, recover, verify, reset, info'
        });
    }
  } catch (error) {
    console.error('Auth handler error:', error);
    return res.status(500).json({
      ok: false,
      error: 'Internal server error',
      message: error.message
    });
  }
}
