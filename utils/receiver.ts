import { appendFile } from "node:fs/promises";

// server.ts
const server = Bun.serve({
  port: 3000,
  async fetch(req) {
    // Handle CORS preflight requests
    if (req.method === "OPTIONS") {
      return new Response(null, {
        headers: {
          "Access-Control-Allow-Origin": "https://www.google.com",
          "Access-Control-Allow-Methods": "POST, OPTIONS",
          "Access-Control-Allow-Headers": "Content-Type",
        },
      });
    }

    // Handle POST requests
    if (req.method === "POST") {
      const body = await req.text();
      await appendFile("output.txt", body);
    //   await Bun.write("output.txt", body, { append: true });
      return new Response("Data saved!", {
        status: 200,
        headers: {
          "Access-Control-Allow-Origin": "https://www.google.com",
        },
      });
    }

    // Handle other requests
    return new Response("Send a POST request with your data.", {
      status: 400,
      headers: {
        "Access-Control-Allow-Origin": "https://www.google.com",
      },
    });
  },
});

console.log(`Server running on http://${server.hostname}:${server.port}`);
