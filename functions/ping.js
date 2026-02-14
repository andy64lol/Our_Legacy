// api/ping.js

exports.handler = async function(event, context) {
  // CORS headers
  const headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Content-Type': 'application/json'
  };
  
  // Handle OPTIONS request for CORS preflight
  if (event.httpMethod === 'OPTIONS') {
    return {
      statusCode: 200,
      headers: headers,
      body: ''
    };
  }
  
  return {
    statusCode: 200,
    headers: headers,
    body: JSON.stringify({
      ok: true,
      message: "Ping successful! Serverless is alive and responding.",
      method: event.httpMethod,
      timestamp: Date.now()
    })
  };
}
