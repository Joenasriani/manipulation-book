# BOOKSTORE PRE-MIGRATION ROLLBACK POINT

Created: 2026-09-23
Purpose: preserve the complete source and production map immediately before repository renaming, repository separation, internal path cleanup, Vercel Git reconnection, and terminology normalization.

## One-call rollback phrase

ROLLBACK BOOKSTORE TO PRE-MIGRATION

When this phrase is issued, restore the source repositories to the frozen rollback branches below, restore the canonical production mappings below, and redeploy those exact sources to the listed production projects. Do not delete the rollback branches.

## Frozen Git source state

### Combined bookstore + Manipulation repository
Repository at snapshot time: `Joenasriani/test-things`
Default branch at snapshot time: `main`
Frozen commit: `d1a2db194252ff45695b1c3ebf15929bb234da04`
Rollback branch: `rollback/bookstore-pre-migration-2026-09-23`

This snapshot contains:
- Manipulation public source at repository root.
- Reasoning Library source under `store-v3/`.
- ICF-AI public research/product source.
- release manifests, verification scripts, publication standards, and deployment workflow present at snapshot time.

### The Structure of Life repository
Repository at snapshot time: `Joenasriani/structure-of-life-book`
Default branch at snapshot time: `main`
Frozen commit: `df902f9c34108ac07c43730e5e049b4d3ee31ef0`
Rollback branch: `rollback/bookstore-pre-migration-2026-09-23`

## Frozen production map

### The Reasoning Library
Public URL: https://reasoning-library.vercel.app/
Vercel project: `reasoning-library`
Project ID: `prj_wOatJv2jARExk7008J15Jv7HbcNn`
Production deployment at snapshot: `dpl_F4iAS7TJnfBj38ev9tEXepCEshAr`

### Manipulation
Public URL: https://manipulation-book.vercel.app/
Vercel project: `manipulation-book`
Project ID: `prj_LM2IRHgaBTjJ397TBzNux308FuEw`
Production deployment at snapshot: `dpl_Fy9jATJrfXjQKqEAy4RN33xCLnqx`

### The Structure of Life
Public URL: https://the-structure-of-life.vercel.app/
Vercel project: `the-structure-of-life`
Project ID: `prj_tnA6mm9ivIayBSUAfLRxIiTxtYzb`
Production deployment at snapshot: `dpl_FSGUfFuFi2CwCkrqDqKssobn8pgF`

## Rollback rules

1. Never rewrite or delete either rollback branch.
2. Do not delete historical Vercel projects until the migration is fully verified and explicitly approved.
3. Repository renames must preserve Git history. Do not replace a canonical repository with a copied repository merely to change its name.
4. Public production URLs above remain the stable external addresses unless explicitly approved otherwise.
5. During rollback, source identity takes precedence over later naming cleanup.
6. After restoring Git refs, verify root, sample, methodology, terms, checkout, delivery, robots, sitemap, canonical metadata, and public assets before declaring rollback complete.
7. Payment acceptance and private buyer receipt remain separate operational checks.


## Preserved legacy Vercel state

Do not delete these during migration. They are not canonical production targets, but they existed at the rollback point and are part of the reversible state.

### RoboMarket team
Team ID: `team_aK7orsaNw316c1bdLjjKFVMy`

- `manipulation-the-fool-and-the-wise` — `prj_zaxPuXKECKueD8BcvBEqR7nbzpuF`
- `manipulation-the-fool-and-the-wise-v2` — `prj_enAbuUeWubH2zaeKIcb8komOlIZZ`

### The Testers 101 team
Team ID: `team_UgFTpDoLICV1eYAWYMLazes4`

- `manipulation-the-fool-and-the-wise` — `prj_qbJJt9RHtyfiLgxsrotDaNSododz`
- `manipulation-responsive-test` — `prj_pPfIqdweuhIh13o0e6f6Uo5izZMo`
- `manipulation-fix-test` — `prj_g4n1C4kZSSAkE9cdoE6Kf8eP0Ggp`

These legacy projects may be retired only after the canonical migration has passed final verification and the user explicitly approves retirement.
