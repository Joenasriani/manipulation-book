# Publication workflow

Status: prepared source. This branch is not a production release.

`publication.json` owns each publication's identity, price, product ID, website routes, Vercel mapping and buyer archive identity. The bookstore owns presentation and imports immutable, SHA256 checked snapshots through `catalogue/sources.lock.json`. Snapshots are build inputs, not competing publication records.

1. Finish the publication and its evidence audit before designing its landing page. Keep private buyer archives outside the public repository and deployment output. Preserve all earlier editions and their hashes.
2. Create one repository and one Vercel project. Record their verified IDs and stable URL in the publication manifest. Preserve the distinct art direction of each publication.
3. Record the buyer ZIP SHA256, file inventory and internal checksums. Run `python scripts/publish.py archive --file /private/path/to/edition.zip`. A missing archive blocks commercial release; never substitute another edition because its filename looks similar.
4. Run `python scripts/publish.py build`, `python scripts/publish.py validate` and `python scripts/test-publication.py`. Resolve identity, price, route and asset conflicts explicitly.
5. Commit the publication and record its exact Git commit and manifest SHA256. Prepare its catalogue template locally. Import its manifest only after stable URL verification in step 9. Never fetch an unpinned default branch during a production build.
6. Connect the repository to its recorded Vercel project with root directory `.`. Check the Vercel project ID, Git repository, branch, build command and output directory. No second canonical project may own this publication.
7. Deploy a preview. Run `python scripts/publish.py verify --base https://VERIFIED-PREVIEW-HOST --report verification/preview.json --source-repository OWNER/REPOSITORY --source-commit COMMIT_SHA`. Protected previews require an authenticated verifier; do not disable protection. Match served bytes, canonical tags, the served release manifest, assets and fixed checkout mapping. Evidence expires after 24 hours; retain older reports as historical evidence. Do not promote after a failed or incomplete check.
8. Confirm the original rollback refs still resolve. Save project configuration and deployment IDs. Check `python scripts/publish.py release-gate`. Promote the verified deployment, then independently repeat the checks at the stable public URL and record its deployment ID and source commit.
9. Update catalogue locks only after the publication's stable URL passes. Build, preview, verify and promote the store independently. Every generated schema offer and purchase link must match its publication manifest.
10. Retire a duplicate only after enumerating its routes, comparing content and hashes, preserving unique material, checking replacement routes and verifying redirects. Keep rollback branches and release evidence. Do not rewrite historical release documents to imply that old records describe the new deployment.
11. Keep payment acceptance, verified merchant transaction and actual buyer receipt as separate operational evidence. A checkout redirect or delivery page is not proof of payment. Do not mark the commercial release complete without them.

For future books, add a new canonical repository and manifest, validate its private package and preview, then add one immutable catalogue source entry and its publication-specific presentation. Do not add another numbered bookstore directory.
