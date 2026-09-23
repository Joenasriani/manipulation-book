# Manipulation: The Fool and the Wise

Prepared canonical repository source. Production migration is pending.

See `PUBLISHING_WORKFLOW.md` for the validated publishing process and `MIGRATION_STATUS.json` for unresolved gates. Historical release records remain unchanged and refer to their recorded dates.

## Checkout repair candidate

Use `preview/consolidation` for the current candidate. The checkout route and delivery page must be deployed and independently verified before switching catalogue links. A confirmed product-specific public PayPal link can be stored in `publication.json` under `checkout.hosted_url`; null preserves the existing fixed-parameter redirect. Historical release and rollback documents retain their original contents. See the bookstore repository's `VERCEL_HANDOFF.md` for deployment and payment settings.
