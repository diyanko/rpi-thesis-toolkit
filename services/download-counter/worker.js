// Aggregate-only endpoint. Deploy with a D1 binding named COUNTS and request logs off.
// No request headers, IP addresses, visitor IDs, referrers, or raw events are stored.
const ORIGIN = "https://diyanko.github.io";
const ASSETS = ["starter", "overleaf", "class", "cheatsheet"];

function reply(body, status = 200, cache = "no-store") {
  return new Response(body, {status, headers: {
    "Content-Type": "application/json", "Cache-Control": cache,
    "Access-Control-Allow-Origin": ORIGIN, "Vary": "Origin",
    "Access-Control-Allow-Methods": "POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
    "X-Content-Type-Options": "nosniff"
  }});
}

async function smallBody(request) {
  if (!request.body) return null;
  const reader = request.body.getReader();
  const chunks = [];
  let size = 0;
  while (true) {
    const {value, done} = await reader.read();
    if (done) break;
    size += value.byteLength;
    if (size > 64) { await reader.cancel(); return null; }
    chunks.push(...value);
  }
  return new TextDecoder("utf-8", {fatal: true}).decode(new Uint8Array(chunks));
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (url.search) return reply(null, 404);
    try {
      if (url.pathname === "/counts" && request.method === "GET") {
        const {results} = await env.COUNTS.prepare(
          "SELECT day, asset, total FROM daily_downloads ORDER BY day DESC, asset LIMIT 1464"
        ).all();
        return reply(JSON.stringify({metric: "first download action per browser tab session", days: results}), 200, "public, max-age=300");
      }
      if (url.pathname !== "/event") return reply(null, 404);
      if (request.headers.get("Origin") !== ORIGIN) return reply(null, 403);
      if (request.method === "OPTIONS") return reply(null, 204);
      if (request.method !== "POST") return reply(null, 405);
      if ((request.headers.get("Content-Type") || "").split(";")[0].trim() !== "application/json") return reply(null, 415);
      let data;
      try { data = JSON.parse(await smallBody(request)); } catch (_) { return reply(null, 400); }
      if (!data || Array.isArray(data) || Object.keys(data).length !== 1 || !ASSETS.includes(data.asset)) return reply(null, 400);
      const day = new Date().toISOString().slice(0, 10);
      await env.COUNTS.prepare(
        "INSERT INTO daily_downloads(day, asset, total) VALUES (?1, ?2, 1) ON CONFLICT(day, asset) DO UPDATE SET total = total + 1"
      ).bind(day, data.asset).run();
      return reply(null, 204);
    } catch (_) {
      // Measurement failure never affects the original download. Do not log payloads.
      return reply(null, 503);
    }
  }
};
