# SEO and checkout hardening, 23 September 2026

Changes are based on `preview/consolidation`. This is a source update, not evidence of production rollout.

## Applied

- Canonical URLs are present on generated publication routes, including delivery guidance.
- Product offers point to the canonical publication page rather than an unindexable checkout redirect.
- Book edition and keywords are derived from the manifest; existing additional structured metadata survives the build.
- Store and publication product identifiers use the same book/product fragments and the same author identity.
- Publication checkout requires an explicitly configured, validated hosted PayPal link. Missing configuration fails closed.
- Structure of Life and ICF-AI include baseline browser security headers. Structure of Life no longer emits an explicit index header that can conflict with preview protection.
- Regression checks cover canonical uniqueness, public indexing, delivery exclusion, sitemap boundaries, metadata and invalid checkout configuration.

Changes listed above span the four-repository batch; each repository contains its applicable subset. Existing HTML samples, crawler policy, assets, paid-file boundaries and public GitHub distribution decisions are preserved.

## Validation

All four repositories passed deterministic builds, local validation and publication regression checks. The store proxy suite passed. Public production pages for the store and both books returned HTTP 200 on 23 September; the store ICF-AI route returned HTTP 404. Those responses predate this change and do not prove deployment of it.

## Outstanding

The Vercel deployment connector reports `Tool deploy_to_vercel not found`. No production rollout is claimed. Existing release gates remain in place. Canonical cutover and legacy-domain redirects require a verified deployment. ICF-AI routing/project verification remains open. Search Console submission and URL inspection have not been performed.

Fulfilment remains manual. A delivery-page visit does not confirm payment or expose paid files. Hosted PayPal settings, payment acceptance, the exact private buyer archives and receipt of the product have not been verified in this change. No payment was made and no customer message was sent.
