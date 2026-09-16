const SITE_HOST = "gundoganvize.com";
const SITE_ORIGIN = `https://${SITE_HOST}`;

function cleanPath(pathname) {
  let path = pathname || "/";
  path = path.replace(/\/index\.html$/i, "/");
  path = path.replace(/\/{2,}/g, "/");
  if (!path.startsWith("/")) path = `/${path}`;

  // This site uses directory URLs as canonicals. Keep real files unchanged.
  const last = path.split("/").pop() || "";
  const looksLikeFile = last.includes(".");
  if (path !== "/" && !looksLikeFile && !path.endsWith("/")) path += "/";
  return path || "/";
}

function canonicalUrl(url) {
  return `${SITE_ORIGIN}${cleanPath(url.pathname)}`;
}

function replaceCanonical(html, canonical) {
  const tag = `<link rel="canonical" href="${canonical}">`;
  if (/<link\s+[^>]*rel=["']canonical["'][^>]*>/i.test(html)) {
    return html.replace(/<link\s+[^>]*rel=["']canonical["'][^>]*>/i, tag);
  }
  return html.replace(/<head([^>]*)>/i, `<head$1>${tag}`);
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const isCustomDomain = url.hostname === SITE_HOST || url.hostname === `www.${SITE_HOST}`;
    const path = cleanPath(url.pathname);

    if (
      isCustomDomain &&
      (url.protocol !== "https:" || url.hostname !== SITE_HOST || path !== url.pathname)
    ) {
      const target = new URL(`${SITE_ORIGIN}${path}`);
      target.search = url.search;
      return new Response(null, {
        status: 301,
        headers: {
          Location: target.toString(),
          "Cache-Control": "public, max-age=3600, s-maxage=3600",
          "X-GundoganVize-Canonical-Redirect": "2026-09-17",
        },
      });
    }

    const response = await env.ASSETS.fetch(request);
    const headers = new Headers(response.headers);
    if (url.hostname.endsWith(".pages.dev")) headers.set("X-Robots-Tag", "noindex, nofollow");

    const type = headers.get("content-type") || "";
    if (!type.includes("text/html")) {
      return new Response(response.body, { status: response.status, statusText: response.statusText, headers });
    }

    const canonical = canonicalUrl(url);
    const body = replaceCanonical(await response.text(), canonical);
    headers.delete("content-length");
    headers.set("Link", `<${canonical}>; rel="canonical"`);
    return new Response(body, { status: response.status, statusText: response.statusText, headers });
  },
};
