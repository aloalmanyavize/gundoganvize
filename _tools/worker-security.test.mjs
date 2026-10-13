// node --test _tools/worker-security.test.mjs
// No network access or production credentials needed.
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";

const source = readFileSync(new URL("../_worker.js", import.meta.url), "utf8");
const moduleUrl = "data:text/javascript;base64," + Buffer.from(source).toString("base64");
const { default: worker } = await import(moduleUrl);

function mockEnv() {
  const requests = [];
  return {
    requests,
    ASSETS: {
      async fetch(request) {
        requests.push({ url: request.url, method: request.method });
        const path = new URL(request.url).pathname;
        const isDocument = path === "/" || path.endsWith("/");
        const type = isDocument ? "text/html; charset=utf-8" : path.endsWith(".pdf") ? "application/pdf" : "text/plain; charset=utf-8";
        const body = isDocument ? '<!doctype html><html><head><title>Gündoğan Vize</title></head><body><h1>Test</h1></body></html>' : "static resource";
        return new Response(body, { status: 200, headers: { "Content-Type": type } });
      }
    }
  };
}

test("normal page has security headers and keeps a crawlable canonical", async () => {
  const env = mockEnv();
  const response = await worker.fetch(new Request("https://gundoganvize.com/"), env);
  assert.equal(response.status, 200);
  assert.equal(env.requests.length, 1);
  assert.equal(response.headers.get("x-frame-options"), "DENY");
  assert.equal(response.headers.get("x-content-type-options"), "nosniff");
  assert.equal(response.headers.get("strict-transport-security"), "max-age=15552000");
  assert.match(response.headers.get("content-security-policy"), /frame-ancestors 'none'/);
  assert.match(await response.text(), /<link rel="canonical" href="https:\/\/gundoganvize\.com\/">/);
  assert.doesNotMatch(response.headers.get("x-robots-tag") || "", /noindex/);
});

test("legacy and insecure URLs redirect without losing query strings", async () => {
  const env = mockEnv();
  const res = await worker.fetch(new Request("http://www.gundoganvize.com/almanya-vizesi?ref=organic"), env);
  assert.equal(res.status, 301);
  assert.equal(res.headers.get("location"), "https://gundoganvize.com/almanya-vizesi/?ref=organic");
  assert.equal(res.headers.get("x-frame-options"), "DENY");
  assert.equal(env.requests.length, 0);
});

test("source, config and private paths cannot be served", async () => {
  for (const path of ["/.git/config", "/.github/workflows/site-health.yml", "/.agents/test", "/_tools/check_sitemap.py", "/.env", "/.env.production", "/AGENTS.md", "/README.md", "/_worker.js", "/_headers", "/wrangler.toml", "/.assetsignore"]) {
    const env = mockEnv();
    const response = await worker.fetch(new Request("https://gundoganvize.com" + path), env);
    assert.equal(response.status, 404, path);
    assert.equal(response.headers.get("cache-control"), "no-store", path);
    assert.equal(env.requests.length, 0, path);
  }
});

test("unexpected write methods are not passed through to static assets", async () => {
  const env = mockEnv();
  const response = await worker.fetch(new Request("https://gundoganvize.com/randevu-talebi/", { method: "POST", body: "test" }), env);
  assert.equal(response.status, 405);
  assert.equal(response.headers.get("allow"), "GET, HEAD");
  assert.equal(env.requests.length, 0);
});

test("SEO resources, appointment paths, and PDFs remain accessible", async () => {
  for (const path of ["/robots.txt", "/sitemap.xml", "/randevu-talebi/", "/gerekli-evraklar/", "/gerekli-evraklar/test.pdf"]) {
    const env = mockEnv();
    const response = await worker.fetch(new Request("https://gundoganvize.com" + path), env);
    assert.equal(response.status, 200, path);
    assert.equal(env.requests.length, 1, path);
    assert.equal(response.headers.get("x-content-type-options"), "nosniff", path);
  }
});

test("pages.dev preview remains noindex and does not receive custom-domain HSTS", async () => {
  const env = mockEnv();
  const response = await worker.fetch(new Request("https://example.pages.dev/"), env);
  assert.equal(response.status, 200);
  assert.equal(response.headers.get("x-robots-tag"), "noindex, nofollow");
  assert.equal(response.headers.get("strict-transport-security"), null);
});
