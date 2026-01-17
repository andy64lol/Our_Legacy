// api/ping.js

export default function handler(req, res) {
  res.status(200).json({
    ok: true,
    message: "Ping successful! Serverless is alive and responding.",
    method: req.method,
    timestamp: Date.now()
  });
}