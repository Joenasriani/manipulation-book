# Canonical production map lock — 2026-09-23

This file is the release pointer for the BOOKSTORE project. Only the three production mappings below are canonical for future fixes, deployment checks and release decisions. Older Vercel projects, test projects, preview deployments and superseded package versions are not development targets unless a later confirmed change explicitly reactivates one.

| Product | Canonical GitHub source | Canonical source location | Canonical Vercel project | Canonical public URL |
|---|---|---|---|---|
| The Reasoning Library | `Joenasriani/test-things` | `main/store-v3/` | `reasoning-library` / `prj_wOatJv2jARExk7008J15Jv7HbcNn` | https://reasoning-library.vercel.app/ |
| Manipulation — The Fool and the Wise | `Joenasriani/test-things` | `main/` repository root | `manipulation-book` / `prj_LM2IRHgaBTjJ397TBzNux308FuEw` | https://manipulation-book.vercel.app/ |
| The Structure of Life | `Joenasriani/structure-of-life-book` | `main/` | `the-structure-of-life` / `prj_tnA6mm9ivIayBSUAfLRxIiTxtYzb` | https://the-structure-of-life.vercel.app/ |

Noncanonical Manipulation projects include `manipulation-the-fool-and-the-wise`, `manipulation-the-fool-and-the-wise-v2`, `manipulation-responsive-test` and `manipulation-fix-test`. They remain untouched in this lock step. Their later redirect, archive or deletion status requires separate confirmation.

# Canonical source and buyer files — 2026-09-19

The intended public sources are this repository for Manipulation and the store, and `Joenasriani/structure-of-life-book` for The Structure of Life. Source readiness, deployed behavior and successful buyer delivery are separate checks.

## Public addresses

| Property | Canonical URL | Source | Vercel project |
|---|---|---|---|
| The Reasoning Library | https://reasoning-library.vercel.app/ | `store-v3/` | `prj_wOatJv2jARExk7008J15Jv7HbcNn` |
| Manipulation — The Fool and the Wise | https://manipulation-book.vercel.app/ | repository root | `prj_LM2IRHgaBTjJ397TBzNux308FuEw` |
| The Structure of Life | https://the-structure-of-life.vercel.app/ | sibling repository | `prj_tnA6mm9ivIayBSUAfLRxIiTxtYzb` |

Use the store URL once. A second full URL appended to its path is malformed.

## September 19 repairs

The original 1,076,151-byte, 1512 × 2160 Manipulation cover replaces a corrupt 14,394-byte file. The correct Git blob is `56262bf0fdc93d3aade1a1967626f04fa4227e6f`. Browser image decoding passed on the live store and book page.

Both books' purchase links are mapped in source to their own `/api/buy` route, with product IDs `MANIPULATION-2026-09` and `STRUCTURE-2026-09`. Each fixed redirect uses the existing PayPal recipient and USD 23.33. A return visit to `/delivery` is not proof of payment.

Both complete Buyer Edition ZIPs have been assembled, with per-file manifests and checksums. See `MANIPULATION_RELEASE_MANIFEST.md` and `releases/2026-09/buyer-packages.json`. The source register retains every reference cited by the reading edition.

## Deployment status

**REMAINING SOURCE CHANGES REQUIRE DEPLOYMENT. PAYMENT AND BUYER RECEIPT ARE NOT VERIFIED.**

Last inspected READY deployments, from September 18:

- Store: `dpl_F4iAS7TJnfBj38ev9tEXepCEshAr`
- Manipulation: `dpl_Fy9jATJrfXjQKqEAy4RN33xCLnqx`
- Structure: `dpl_FSGUfFuFi2CwCkrqDqKssobn8pgF`

The original Manipulation hosted PayPal button produced an error. The replacement redirect is prepared in source; an authenticated checkout has not been completed. The existing Structure checkout encountered PayPal verification and was not proven functional or broken.

The manual production workflow requires repository/organization secret `VERCEL_TOKEN`; the inspected failed run reported it absent. The connected deployment tool also returned “Tool deploy_to_vercel not found.” After working deployment access is restored, run **Bookstore production sync** from this repository's Actions tab. Its final step checks deployed pages, product mapping and full cover bytes with `node scripts/verify-production.mjs`. Those checks do not prove payment acceptance or private delivery.

Earlier claims that all retired domains were redirect-only were incorrect. The legacy Manipulation site and test paths were still public during the September 19 audit. Retirement remains pending Vercel access.

## Buyer delivery and publication boundaries

Delivery is manual after payment verification. The seller must verify the completed transaction, product, amount/currency and recipient in the merchant account, then privately send the matching PDF, EPUB, complete ZIP and buyer guide to the verified transaction email. No automated payment notification or delivery system is implemented.

Paid files and customer records remain outside the public repository and web tree. Public hashes identify the edition without exposing its contents. EPUB container, resource and spine checks passed; full EPUBCheck was not run.

Keep the approved cover and dark editorial book design, ordinary HTML navigation, samples, methodology and terms. Technical repairs do not authorize a visual redesign.

See `PUBLISHING_RELEASE_STANDARD.md` for the complete release gate. Do not describe the commercial journey as fully verified until deployment, successful payment and actual buyer receipt have all passed.

## ICF-AI addition — 2026-09-22

ICF-AI — Integrative Causal Framework for AI Systems has been added to The Reasoning Library as a separate research-framework product without changing the existing two books or their prices.

- Canonical product page: https://reasoning-library.vercel.app/icf-ai
- Public research record: https://github.com/Joenasriani/test-things/tree/main/icf-ai
- Edition: Reference Edition v1.0
- Product ID: `ICF-AI-REF-1.0-2026-09`
- Price: USD 4.99
- Checkout source: `store-v3/api/icf-buy.js`
- Delivery remains private after verified payment; the paid Customer Pack is not committed to the public repository.
- SEO/AI discovery: the canonical page is indexable, included in `sitemap.xml`, described in `llms.txt`, and represented with Product/CreativeWork structured data.
- Search-oriented crawlers remain allowed under the existing robots policy. This addition does not change training-crawler policy.

The framework is described as provisional and versioned. No claim is made that it is a universal theory, industry standard, or validated causal model as a whole.
