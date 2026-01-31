// Simple Netlify function to ensure Node.js environment
exports.handler = async function(event, context) {
  return {
    statusCode: 200,
    body: JSON.stringify({ message: "Hello from Netlify Function" })
  };
}