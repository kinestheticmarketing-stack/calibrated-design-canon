# Restore drill — 2026-10-11 (Kickoff 33, D1)

Restore drill of the three insulation databases into scratch `drill_<site>_20261011`
databases on the VPS docker cluster (`porter-db-1`, postgres 16). Each scratch
database was created, restored, compared to live, and dropped before the next
site started. No live database, service or credential was written, stopped or
rotated.

## Runbook

Path: `ops/db_backup.sh`, header section `RESTORE RUNBOOK` (lines 116-149).
Docker-cluster steps, as followed (with `<db>_restore_test` replaced by
`drill_<site>_20261011`):

```
cd /root/porter
docker compose exec -T db psql -U porter -d postgres -c 'CREATE DATABASE <db>_restore_test;'
docker compose cp <dump> db:/tmp/r.dump
docker compose exec -T db pg_restore -U porter -d <db>_restore_test --no-owner /tmp/r.dump
docker compose exec -T db rm -f /tmp/r.dump
```

Then per-table row counts source vs restored, then `DROP` the scratch database.

Steps SKIPPED: none of the docker-cluster steps writes to, drops, renames or
replaces a live database, stops a service, or rotates a credential, so none was
skipped on that ground. Not used because they do not apply: the host-cluster
steps (`sudo -u postgres psql -c 'CREATE DATABASE <db>_restore_test;'`,
`sudo -u postgres pg_restore -d <db>_restore_test --no-owner <dump>`; the three
insulation databases are on the docker cluster) and the B2 retrieval steps
(`rclone --b2-versions lsf ...`, `rclone copyto ...`; the newest dump was local).

Site to database, from a presence test (`grep -qw`) of each service's own env
file, no value printed: denver → `insulation`, longmont → `longmont_insulation`,
greeley → `greeley_insulation`.

Method per site: dump header and `pg_restore -l` (count of `DATABASE` entries);
`df` of the filesystem holding `/var/lib/docker`; `pg_restore` with `-d
drill_<site>_20261011 --no-owner --exit-on-error`, never `-C`/`--create`/`--clean`;
live opened with `PGOPTIONS='-c default_transaction_read_only=on'` (confirmed
`on`), SELECT and `\d` only; exact `count(*)` per table; drop by literal name.

Backup timestamp is the dump file's mtime on the host (`-0600`). The archive
header's own `Archive created at` line reads `10:30:05 MDT`, one hour off the
host mtime; the cause was not investigated, and the host mtime is used.

## Denver — `insulation`

| Item | Value |
|---|---|
| Dump | `/root/backups/db/insulation/insulation-2026-10-11.dump` |
| Format | CUSTOM (`PGDMP` header, `Format: CUSTOM`); `pg_restore -l` 24 entries, 0 `DATABASE` objects; filtered-line count n/a (not plain text) |
| Size vs free space | 29,669 B dump; 209,896,386,560 B free |
| Backup timestamp | 2026-10-11 03:30:05 -0600 |
| Restore | `pg_restore` exit 0 |
| Tables scratch | `lead_submissions_log`, `leads`, `pageviews` |
| Tables live | `lead_submissions_log`, `leads`, `pageviews` |
| Set difference | empty both ways |
| `lead_submissions_log` | scratch 105 / live 105 |
| `leads` | scratch 104 / live 104 |
| `pageviews` | scratch 311 / live 313; live rows with `viewed_at` after the backup: 2 (the whole gap) |
| Newest `leads.created_at` | scratch 2026-10-10 15:00:00.481784+00 / live the same; live leads after the backup: 0 |
| Scratch dropped | `DROP DATABASE drill_denver_20261011` exit 0; `drill%` count after: 0 |
| **Verdict** | **RESTORES** |

## Longmont — `longmont_insulation`

| Item | Value |
|---|---|
| Dump | `/root/backups/db/longmont_insulation/longmont_insulation-2026-10-11.dump` |
| Format | CUSTOM (`PGDMP` header, `Format: CUSTOM`); `pg_restore -l` 23 entries, 0 `DATABASE` objects; filtered-line count n/a (not plain text) |
| Size vs free space | 21,090 B dump; 209,896,308,736 B free |
| Backup timestamp | 2026-10-11 03:30:05 -0600 |
| Restore | `pg_restore` exit 0 |
| Tables scratch | `lead_submissions_log`, `leads`, `pageviews` |
| Tables live | `lead_submissions_log`, `leads`, `pageviews` |
| Set difference | empty both ways |
| `lead_submissions_log` | scratch 83 / live 83 |
| `leads` | scratch 82 / live 82 |
| `pageviews` | scratch 70 / live 70 |
| Newest `leads.created_at` | scratch 2026-10-10 15:00:01.042049+00 / live the same; live rows after the backup: 0 in all three tables |
| Scratch dropped | `DROP DATABASE drill_longmont_20261011` exit 0; `drill%` count after: 0 |
| **Verdict** | **RESTORES** |

## Greeley — `greeley_insulation`

| Item | Value |
|---|---|
| Dump | `/root/backups/db/greeley_insulation/greeley_insulation-2026-10-11.dump` |
| Format | CUSTOM (`PGDMP` header, `Format: CUSTOM`); `pg_restore -l` 23 entries, 0 `DATABASE` objects; filtered-line count n/a (not plain text) |
| Size vs free space | 22,340 B dump; 209,896,304,640 B free |
| Backup timestamp | 2026-10-11 03:30:05 -0600 |
| Restore | `pg_restore` exit 0 |
| Tables scratch | `lead_submissions_log`, `leads`, `pageviews` |
| Tables live | `lead_submissions_log`, `leads`, `pageviews` |
| Set difference | empty both ways |
| `lead_submissions_log` | scratch 92 / live 92 |
| `leads` | scratch 91 / live 91 |
| `pageviews` | scratch 56 / live 56 |
| Newest `leads.created_at` | scratch 2026-10-10 15:00:00.789606+00 / live the same; live rows after the backup: 0 in all three tables |
| Scratch dropped | `DROP DATABASE drill_greeley_20261011` exit 0; `drill%` count after: 0 (docker and host) |
| **Verdict** | **RESTORES** |

## After all sites

`select count(*) from pg_database where datname like 'drill%'`: docker cluster 0,
host cluster 0. The three insulation services were `active` with homepage 200
from the server, host `postgresql@16-main` `active` and `porter-db-1` `healthy`,
at start and before each site.

Not drilled here: the host-cluster databases (`totefinders`,
`kinestheticmarketing_com`) and the host-cluster role-password reset.

Verify: `ls /root/backups/db/{insulation,longmont_insulation,greeley_insulation}/ | tail`
for the dumps used; `docker compose exec -T db psql -U porter -d postgres -XAtc "select count(*) from pg_database where datname like 'drill%'"`
(from `/root/porter`) returns 0.
