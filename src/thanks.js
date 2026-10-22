// Shared handler for the paid-kit thank-you pages (/<kit>/thanks).
//
// The download links live only in templates/ (never in public/), and this
// function hands them out only when the URL carries a Stripe Checkout
// session ID that Stripe confirms as paid. Stripe adds the ID itself:
// each Payment Link redirects to
//   https://money-stories.ch/<kit>/thanks?session_id={CHECKOUT_SESSION_ID}
//
// Needs one secret in Netlify (Site configuration → Environment variables):
//   STRIPE_KEY  a restricted key (rk_live_…) with read access to Checkout Sessions.
// Optional, to make sure a payment for one kit doesn't unlock the other:
//   PLINK_FIRST_YEAR_INVESTING  the plink_… ID of that kit's Payment Link.

const SESSION_RE = /^cs_(live|test)_[A-Za-z0-9]{10,200}$/;

const HEADERS = {
  "content-type": "text/html; charset=utf-8",
  "cache-control": "private, no-store",
  "x-robots-tag": "noindex, nofollow",
  "referrer-policy": "no-referrer",
};

export async function verifySession(sessionId, env, expectedPlink, fetchImpl = fetch) {
  if (!sessionId || !SESSION_RE.test(sessionId)) return { ok: false, reason: "missing" };
  if (!env.STRIPE_KEY) return { ok: false, reason: "config" };

  let res;
  try {
    res = await fetchImpl(
      `https://api.stripe.com/v1/checkout/sessions/${encodeURIComponent(sessionId)}`,
      { headers: { authorization: `Bearer ${env.STRIPE_KEY}` } },
    );
  } catch {
    return { ok: false, reason: "stripe" };
  }
  if (res.status === 404) return { ok: false, reason: "unknown" };
  if (!res.ok) return { ok: false, reason: "stripe" };

  const s = await res.json();
  const paid = s.status === "complete" && (s.payment_status === "paid" || s.payment_status === "no_payment_required");
  if (!paid) return { ok: false, reason: "unpaid" };
  if (expectedPlink && s.payment_link && s.payment_link !== expectedPlink) return { ok: false, reason: "other-kit" };
  return { ok: true };
}

function lockedPage(template, kitPath, reason) {
  const temporary = reason === "stripe" || reason === "config";
  const body = temporary
    ? `<span class="pill">One moment</span>
  <h1>We couldn't <span class="mark">check your purchase</span></h1>
  <p class="lead">It's a temporary problem on our side, not yours. Reload the page in a minute.</p>`
    : `<span class="pill">Download link</span>
  <h1>This page is for <span class="mark">people who bought the kit</span></h1>
  <p class="lead">If you bought it, open the link that brought you here after paying (it's also in your Stripe receipt). Can't find it? Write to us and we'll resend it.</p>
  <p style="margin-top:24px"><a class="btn" href="/${kitPath}/">See the kit</a></p>`;

  const main = `<main id="content" class="thanks">
<div class="wrap narrow">
  ${body}
  <p class="tip muted">Paid but can't get in? Write to <a class="link" href="mailto:kikotajada@gmail.com">kikotajada@gmail.com</a> with the email you used to pay and we'll fix it right away.</p>
</div>
</main>`;
  return template.replace(/<main[\s\S]*?<\/main>/, main);
}

export async function handleThanks(context, { template, kitPath, expectedPlinkVar }) {
  const url = new URL(context.request.url);
  const sessionId = url.searchParams.get("session_id");
  const result = await verifySession(sessionId, context.env, context.env[expectedPlinkVar]);

  if (result.ok) return new Response(template, { headers: HEADERS });
  const status = result.reason === "stripe" || result.reason === "config" ? 503 : 403;
  return new Response(lockedPage(template, kitPath, result.reason), { status, headers: HEADERS });
}
