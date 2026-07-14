---
name: definition-discovery
description: "Exhaustive system knowledge discovery before creating new definitions. Multi-method search to avoid missing existing entries."
version: 1.0.0
---

# Definition Discovery

Before declaring something undefined or creating new routing rules, use multiple discovery methods. A single search tool can produce false negatives.

## Workflow

For any request to define or check definitions:

1. Broad pattern search (regex)
2. Plain-text substring search on key files
3. Full-text read of relevant sections
4. Past conversation search
5. Only create new definition if all four methods confirm absence

## Why

Regex can miss entries due to character encoding, mixed-language content, and format differences. The raw file is ground truth.
