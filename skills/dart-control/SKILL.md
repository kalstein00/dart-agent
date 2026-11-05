---
name: dart-control
description: Connect Cline to a running Windows DART application, select the intended window, and retain its explicit control session with the official DART 2.1.0 CLI.
---

# DART control

Use this skill for DART 앱 connection, status, and control requests. Read `references/connection.md` before connecting. The installed official executable is `bin/dart` on Linux and `bin/dart.exe` on Windows, relative to this skill directory; resolve the absolute skill directory from this loaded file. In a default Linux Cline installation, check `~/.cline/skills/dart-control` first; if configured elsewhere, use the actual loaded skill directory. Run that executable directly, never a guessed PATH command. Do not start or discover a Windows app from Linux.

The supported application and CLI are **2.1.0, protocol 2**; the independently pinned contract is **1.0.0**. Compare the executing CLI and connected Main independently against `references/dart-agent-distribution.json`; compare contractVersion and the full fingerprint as well as release, protocol and format. A failed or missing response is not compatibility proof. Do not run business commands on a mismatch.

Pair new remote connections using the interactive PIN workflow in `references/connection.md`. PINs, bundles and official profiles are private: keep them out of arguments, transcripts, repository files and evidence. Keep personal profiles outside this skill. Never auto-forget or replace trust after an error.

For each task, retain the explicit profile, appId, windowId and sessionId returned by DART. The current request's explicit target takes priority over a previous selection; otherwise reuse a valid previous selection, or select the sole available window only when there was no previous selection. Without a current explicit target, if a previous target disappeared, ask before selecting a replacement. Ask when multiple candidates remain ambiguous, without executing business commands. Reinspect the app, window and session before reuse. A restart, target change or invalid session requires rechecking and reselection while preserving the user's intent; never substitute GUI focus. Return the public status, exact binding and any missing prerequisite.

For Dataset import and DM/Tag log queries, read `references/dataset.md`. For investigation of recorded source locations, also read `references/source-investigation.md`. Inspect only the relevant public command contracts. Windows file paths stay on Windows; Linux sources stay on Linux.

For SQL, Charts, Pivot, Comparison and Windows result export, read `references/analysis.md` and inspect the relevant public contracts.
