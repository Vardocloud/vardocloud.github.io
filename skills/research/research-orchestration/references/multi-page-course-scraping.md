# Multi-Page Course/Documentation Scraping Pattern

When scraping a structured multi-page course or documentation site (MOOC, university course, docs site with numbered sections), avoid guessing URLs. Use the discover-then-batch pattern:

## Pattern

1. **Extract first page** via `web_extract` to confirm content and structure
2. **Navigate with browser** to the first section: `browser_navigate(url=first_section_url)`
3. **Query all section links** via browser console:
   ```js
   [...document.querySelectorAll('article a[href*="chapter"]')].map(a => a.href + ' | ' + a.textContent.trim()).join('\n')
   ```
4. **Batch extract all sections** via `web_extract(urls=[...])` with all discovered URLs
5. Repeat steps 2-4 for each chapter

## Why This Works

- MOOC/course sites use consistent URL patterns but section slugs vary (underscores, hyphens, descriptive names)
- Guessing URLs wastes time and produces 404s
- Browser console JS extracts exact links from the rendered sidebar/ToC
- Batch `web_extract` (up to 5 URLs per call) is efficient

## Example: Helsinki Ethics of AI Course

- 7 chapters, 25 total sections
- Chapter sidebar has `<a href>` links with `chapter` in the path
- First attempt (guessing URLs): 5 web_extract calls, 3 were 404s
- Browser discovery approach: 7 navigate calls + 7 console queries + 5 batch extracts = all 25 sections in ~12 calls

## Pitfall

Do NOT iterate through guessed URL patterns (`chapter-2/3-rights-and-duties`, `chapter-2/3-kantian-ethics`). Course section slugs are descriptive and unpredictable. Always query the rendered sidebar via browser console.
