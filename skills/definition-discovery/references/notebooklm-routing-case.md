# NotebookLM Routing — 14 Jul 2026

Concrete case where search_files returned zero hits but the definition existed at line 386 of the system rules file.

The existing definition was:
- pro account = Studio operations (audio, video, slide deck)
- legacy account = backup and normal notebook operations

Search query patterns that failed:
- Regex with Turkish content
- Format mismatch (pro=value vs pro: value vs pro = value)

Lesson: plain-text substring grep followed by section read is the reliable method.
