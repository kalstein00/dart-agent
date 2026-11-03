---
name: dart-control
description: Connect Linux Cline to a running Windows DART application, select the intended window, and retain its explicit control session with the official DART 2.1.0 CLI.
---

# DART control

Use this skill for DART 앱 connection, status, and control requests. Read `references/connection.md` before connecting. The installed official executable is `bin/dart` relative to this skill directory; resolve the absolute skill directory from this loaded file. Run that executable directly, never a guessed PATH command. Do not start or discover a Windows app from Linux.

The supported application, CLI and command contract are **2.1.0, protocol 2**. Compare the executing CLI and connected Main independently against `references/dart-agent-distribution.json`; a failed or missing response is not compatibility proof. Do not run business commands on a mismatch.

Connection bundles and official profiles are private. Use a bundle file via stdin and an explicitly chosen profile; never print its contents or put credentials in command arguments, transcripts, repository files or evidence. Keep personal profiles outside this skill. Never auto-forget or replace trust after an error.

For each task, retain the explicit profile, appId, windowId and sessionId returned by DART. The current request's explicit target takes priority over a previous selection; otherwise reuse a valid previous selection, or select the sole available window only when there was no previous selection. Without a current explicit target, if a previous target disappeared, ask before selecting a replacement. Ask when multiple candidates remain ambiguous, without executing business commands. Reinspect the app, window and session before reuse. A restart, target change or invalid session requires rechecking and reselection while preserving the user's intent; never substitute GUI focus. Return the public status, exact binding and any missing prerequisite.

For Dataset import and DM/Tag log queries, read `references/dataset.md` and inspect only the relevant public command contracts. Windows file paths stay on Windows; Linux sources stay on Linux.
