---
id: fort-collins-genesis
owner: architect
type: feature
created: 2026-08-19
size: L
lane: genesis
after: [hardcoded-path-defect-portfolio]
retriage: 2026-10-02
classification: BLOCKED
---
**Classification reasoning (2026-09-02, corrected 2026-09-03):** BLOCKED on the Director's go-ahead to start the fourth-property genesis — not on the domain. The 2026-09-02 reasoning said the domain "does not exist yet"; it does (registered 2026-08-05, DNS live, A record already on the portfolio VPS — see "Premise corrected" below). What is missing is a Director decision to begin, an undated event with nothing for Architect to rule on until it arrives.

# Fort Collins — the fourth property: domain registered and DNS live, genesis not yet started

`fortcollinscoloradoinsulation.com` is registered (IONOS, 2026-08-05) and its
A record already points at the portfolio VPS; nothing is built behind it — no
nginx vhost, no TLS certificate, no site content (verified 2026-09-03, below).

`METHODS/PROPERTY_GENESIS.md` now carries 10 Zarr-derived genesis steps
across its phases plus two standing rulings, in addition to the pre-existing
checklist. Register Search Console/Bing the day the domain resolves (the
single highest-value step — data before verification cannot be recovered),
check domain history before authoring, author `COPY_VOICE.md` in Phase 1
rather than four waves later, and derive output paths from the script's own
location from day one rather than inheriting the 36-file hardcoded-path
defect. Recommend the hardcoded-path defect (see that card) lands on the
three existing properties before this genesis starts, so Fort Collins has a
clean parent to clone from.

---

## Deferred — 2026-08-19 (HOLD — new property)

Held. Not started. `METHODS/PROPERTY_GENESIS.md` is the procedure and already
carries the cwd-relative-path requirement (Phase 4, item 9) that the existing
three properties had to be retrofitted for — so a Fort Collins genesis would
start compliant rather than needing the same 36-file remediation.

**Card stays open. State above is verified, not assumed.**

---

## Premise corrected — 2026-09-03

The 2026-08-19 and 2026-09-02 text said the domain did not exist. It does.
Every fact below was re-verified by the board-drain lane on 2026-09-03 with
the command shown; nothing is carried from an earlier session's memory.

| Fact | Value | Command |
|---|---|---|
| Registrar | IONOS SE (`Registrar URL: http://www.ionos.com`) | `whois fortcollinscoloradoinsulation.com` |
| Registered | `Creation Date: 2026-08-05T21:06:35Z` | same |
| Expires | `Registry Expiry Date: 2027-08-05T21:06:35Z` | same |
| Status | `clientTransferProhibited` | same |
| Name servers | `ns1033.ui-dns.com`, `ns1045.ui-dns.de`, `ns1096.ui-dns.biz`, `ns1108.ui-dns.org` (IONOS DNS) | `dig +short NS fortcollinscoloradoinsulation.com` |
| A record | `74.208.181.10` — the portfolio VPS, same host as DCI/LGM/GCI | `dig +short fortcollinscoloradoinsulation.com A` |
| nginx vhost | **none** — `grep -rl fortcollins /etc/nginx/` is empty; `sites-enabled/` lists the three insulation properties and the other tenants, nothing for Fort Collins | `ssh root@74.208.181.10 'ls /etc/nginx/sites-enabled/; grep -rl fortcollins /etc/nginx/'` |
| TLS certificate | **none** — `/etc/letsencrypt/live/` has no `fortcollinscoloradoinsulation.com` entry | `ssh root@74.208.181.10 'ls /etc/letsencrypt/live/'` |
| `http://` answers | `HTTP/1.1 200 OK`, `Server: nginx/1.24.0 (Ubuntu)`, body `<title>Apache2 Ubuntu Default Page: It works</title>` (10,671 bytes) — nginx's fall-through default page, not site content | `curl -sI http://fortcollinscoloradoinsulation.com/` |
| `https://` answers | TLS handshakes but with **another tenant's certificate** (`CN=stund.calibrateddesignapp.com`, Let's Encrypt, expires 2026-10-08) and serves that tenant's Express app (`HTTP/2 200`, `x-powered-by: Express`, `<title>STUND</title>`) — SNI fall-through to the first TLS server block, since no block matches this name | `curl -sIk https://fortcollinscoloradoinsulation.com/` |

**Corrected premise:** domain registered and DNS live, already resolving to
the VPS; no site content, no vhost, no TLS certificate. Because the A record
is live, the host currently answers this name with a default page over HTTP
and a mismatched certificate over HTTPS — harmless while nobody links to it,
but it means "register Search Console/Bing the day the domain resolves" (the
opening paragraph's single highest-value step) is already past due in the
sense that the domain resolves today; nothing to register against until a
vhost exists. **Blocked on:** the Director's go-ahead to start the genesis.
Not blocked on the domain.

`retriage: 2026-10-02` kept. Classification kept: BLOCKED (reasoning updated
at the top of this card). Column kept: `later/`.
