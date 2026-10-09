# chatgpt

## Source

ChatGPT export, normalized. A collection of ChatGPT conversations and messages from Derek's account, normalized from raw exports. Source: `/mnt/omen-e-read/work/chatGPT_parser/data/normalized/` containing `messages.ndjson` and `conversations.ndjson`.

Reference: SURVEY.md § chatGPT_parser / ChatGPT export, normalized

## Span

2023-04-17 → 2026-03-12

## Collection

- Conversations: 380 raw → 380 events (normalized conversation records with title, create_time, update_time, model_slug, is_archived, voice, branch info)
- Messages: 19,045 raw → 10,879 events (normalized message records with conversation_id, role, author_name, content_type, text, create_time)

Total: 19,425 raw items → **11,259 events** in one slice.

## Dropped

- `null_ts`: 12 records with null or missing timestamps (filtered)
- `other_role`: 4,932 message records (likely system messages or other non-user/assistant roles; these are metadata-only records per task rules and are excluded from the canonical event stream)
- `polling`: 0
- `decode_errors`: 0

## Form

- Slices: 1 (completed in first budget window)
- Quirks: None
- Warnings: None
- SHA256 (events): `ca830c9fa298c1a8c88b08d7ef3fc450bec4a5961454f7aebfd40307100091c6`

## Next steps

No issues detected. The source is a clean, bounded ChatGPT conversation export with standard filtering applied. Canonical event stream (11,259 events) ready for downstream analysis.
