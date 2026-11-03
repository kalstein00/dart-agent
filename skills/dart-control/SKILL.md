---
name: dart-control
description: Connect Linux Cline to a running Windows DART application, inspect its status, and start or reuse an explicit single-window control session with the official DART 2.1.0 CLI.
---

# DART control

Use this skill for DART 앱 connection, status, and control requests. Read `references/connection.md` before connecting. The installed official executable is `bin/dart` relative to this skill directory; resolve the absolute skill directory from this loaded file. Run that executable directly, never a guessed PATH command. Do not start or discover a Windows app from Linux.

The supported application, CLI and command contract are **2.1.0, protocol 2**. Compare the executing CLI and connected Main independently against `references/dart-agent-distribution.json`; a failed or missing response is not compatibility proof. Do not run business commands on a mismatch.

Connection bundles and official profiles are private. Use a bundle file via stdin and an explicitly chosen profile; never print its contents or put credentials in command arguments, transcripts, repository files or evidence. Keep personal profiles outside this skill. Never auto-forget or replace trust after an error.

For each task, retain the explicit profile, appId, windowId and sessionId returned by DART. Inspect the app and session again before reusing them. A restart or target change invalidates the binding; never substitute GUI focus. A single available window may be selected; multiple windows require an explicit user target. Return the public status, exact binding and any missing prerequisite.

For later work, use `command list`, `command inspect --json '{"command":"..."}'` and the installed reference/catalog to find commands, then inspect current inputs before executing. This ticket supplies connection and single-window session support; data workflows are expanded separately. Windows file paths stay on Windows; Linux sources stay on Linux.
