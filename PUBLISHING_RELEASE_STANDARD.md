# BOOKSTORE — Publishing Release Standard

Release control date: 2026-09-17

## Governing rule

A book is commercially releasable only when the public page, canonical publication files, buyer delivery, payment offer, fulfilment method and release manifest all describe the same edition.

`final`, `latest`, `(1)`, `v2`, `v3`, `ULTIMATE`, or a recent timestamp does not establish canonical status by itself.

The buyer product is not just a PDF. The canonical commercial object is:

**Book + Study Layer + Research Layer + Machine-Readable Knowledge + AI Reasoning Layer + Publication/Usage Metadata.**

Structural equivalence of rigor is required across titles, but artifact counts and taxonomies must be derived from each book rather than mechanically copied from another title.

## Professional delivery model

Do not force the buyer to open a ZIP before they can read the book.

A completed sale should expose:

1. **Main Book PDF** as a direct buyer file.
2. **EPUB** as a direct buyer file where produced.
3. **Complete Buyer Edition ZIP** containing the canonical book files plus all paid companion material.
4. **START HERE / Buyer Guide** explaining contents, reading routes, edition and support.

The ZIP is the complete archival bundle; PDF and EPUB are also surfaced individually for immediate reading and mobile/e-reader use.

## Canonical paid publication objects

1. **Main Book** — fixed-layout PDF.
2. **EPUB** — reflowable ebook where produced.
3. **Study Workbook** — separate practice companion where useful.
4. **Research Atlas** — underlying evidence/taxonomy or structured research substrate.
5. **Source Register** — provenance/source records.
6. **Structured Knowledge Register** — machine-readable CSV/JSON data where the book supports it.
7. **AI Reasoning Framework** — book-derived reasoning protocol for AI-assisted use.
8. **Application Materials** — only when intentionally included and clearly separated from validated products or market evidence.
9. **Buyer Guide / START HERE** — contents, edition, reading routes, support and usage notes.
10. **Digital Product Terms / Licence** — permitted use, delivery, refund, support and privacy terms as actually offered.
11. **Release Manifest** — exact shipped filenames, edition and hashes.
12. **SHA-256 Checksums** — generated from the exact shipped bytes after packaging.

## Public publication objects

The following support discovery, verification and purchase but are not counted as paid archive components:

- canonical landing page;
- methodology / source-standards page;
- public bibliography or selected source routes where appropriate;
- genuine Free Sample;
- seller/contact/terms/privacy/refund/delivery information;
- structured product metadata;
- search/crawler files such as sitemap and robots policy.

The Free Sample is a real publication artifact, but the full buyer edition supersedes it; it does not need to be duplicated inside the paid archive.

## Naming convention

Use:

`<Book_Slug>_<Object>_<Edition_YYYY-MM>.<ext>`

Buyer archive:

`<Book_Slug>_Buyer_Edition_<Edition_YYYY-MM>.zip`

Do not use `FINAL.zip`, `final2`, `latest`, `copy`, `(1)`, `ULTIMATE`, `NEW`, or `corrected-final` as canonical buyer-facing filenames.

## Buyer archive folder order

```text
00_START_HERE/
01_BOOK/
02_STUDY/
03_RESEARCH/
04_MACHINE_READABLE/
05_AI/
06_APPLICATIONS/
90_TERMS/
RELEASE_MANIFEST.json
SHA256SUMS.txt
```

Recommended contents:

```text
00_START_HERE/
  <Book>_Buyer_Guide_<YYYY-MM>.pdf or .md

01_BOOK/
  <Book>_Study_Edition_<YYYY-MM>.pdf
  <Book>_Study_Edition_<YYYY-MM>.epub

02_STUDY/
  <Book>_Study_Workbook_<YYYY-MM>.pdf

03_RESEARCH/
  <Book>_Research_Atlas_<YYYY-MM>.pdf
  <Book>_Source_Register_<YYYY-MM>.csv

04_MACHINE_READABLE/
  <Book>_Structured_Knowledge_Register_<YYYY-MM>.csv
  <Book>_Structured_Knowledge_Register_<YYYY-MM>.json

05_AI/
  <Book>_AI_Reasoning_Framework_<YYYY-MM>.md
  <Book>_AI_Reasoning_Framework_<YYYY-MM>.txt
  optional structured schema when genuinely implemented

06_APPLICATIONS/
  only audited book-specific application material intentionally sold

90_TERMS/
  <Book>_Licence_and_Usage_<YYYY-MM>.pdf or .txt
  <Book>_Edition_Notes_<YYYY-MM>.pdf or .txt
```

Omit an object when it does not exist. Never add a placeholder and advertise it as delivered content.

## Excluded from the paid buyer archive

Do not ship internal production material merely because it exists in the project workspace. Exclude:

- landing-page HTML/CSS/JS and deployment configuration;
- raw production notes and internal audit scratch files;
- obsolete pricing or sales copy;
- private credentials, environment configuration or customer data;
- duplicate/superseded drafts;
- publishing/marketing kits intended for the seller rather than the reader;
- the public Free Sample unless intentionally included for a specific reason.

A provenance or methodology document may be included only when it is deliberately authored as a buyer-facing publication object, not as raw working material.

## Public/private separation

**Public:** landing page, methodology, selected bibliography/source explanation, free sample, seller/contact/terms/privacy/refund/delivery information and product metadata.

**Private / buyer-only:** full book, full EPUB, paid workbook, paid research atlas, source/knowledge registers, paid AI framework, paid application materials and buyer archive.

## Release gate

All of the following must pass before a release is called current:

- Title, subtitle, author and edition are identical across PDF, EPUB, page, structured data and manifest.
- Price is identical across page, checkout and structured data.
- Every promised paid component physically exists.
- Direct PDF/EPUB buyer files and the complete ZIP are the same edition.
- The public sample resolves and contains only sample material.
- Paid files are not publicly enumerable.
- Delivery is tested from payment through receipt/access.
- PDF opens and page count matches the offer.
- EPUB navigation and metadata validate.
- Source/evidence labels are explained.
- AI assistance/provenance is disclosed where applicable.
- No obsolete price or superseded copy appears in the buyer archive.
- `RELEASE_MANIFEST.json` is generated from the exact shipped file inventory.
- SHA-256 hashes are generated after final packaging and include the archive hash.
- GitHub/source-of-truth and live production render the same public release.
- Public methodology/sample/terms routes return 200 before BOOK LOCK.

## Canonical terminology

Use **Research Atlas**, **Source Register**, **Structured Knowledge Register**, **Study Workbook**, **AI Reasoning Framework**, **Free Sample**, **Buyer Edition Package**, **Buyer Guide**, and **Release Manifest** consistently. Marketing language may explain benefits but must not rename publication objects or imply artifacts that do not physically exist.
