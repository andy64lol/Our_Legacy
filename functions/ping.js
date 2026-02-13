// api/ping.js

exports.handler = async function(event, context) {
  return {
    statusCode: 200,
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      ok: true,
      message: "Ping successful! Serverless is alive and responding.",
      method: event.httpMethod,
      timestamp: Date.now()
    })
  };
}
