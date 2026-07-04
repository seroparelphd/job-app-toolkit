# Google Docs Sync

If you use Google Docs as a collaborative review surface, the markdown source file is always the source of truth.

## Sync order (always)

MD -> PDF -> GDoc -> Drive PDF

After ANY markdown edit: rebuild the PDF, sync the text into the GDoc, upload the PDF to Drive.

## Overwriting a GDoc

When replacing GDoc content programmatically, you need to:

1. Read the document to find the current end index
2. Delete all existing content (from index 1 to end-1)
3. Insert the new content at index 1
4. Read the document back and verify the old content is gone

**Critical bug to watch for:** If you search for `endIndex` naively (taking the first match), you'll get the section break's endIndex (which is 1), and your delete operation becomes a no-op. Content stacks instead of replacing. Always take the **maximum** endIndex across the entire document structure.

```python
def find_max_end(node):
    """Recursively find the maximum endIndex in a GDoc JSON response."""
    m = 0
    if isinstance(node, dict):
        if 'endIndex' in node:
            m = max(m, node['endIndex'])
        for v in node.values():
            m = max(m, find_max_end(v))
    elif isinstance(node, list):
        for x in node:
            m = max(m, find_max_end(x))
    return m
```

## Review workflow

Before declaring all review comments addressed:
- Check BOTH inline comments AND suggestion-mode edits
- Comments API and suggestions API are separate -- check both
- GDoc sync wipes comment anchors (the highlighted text they point to), but the comments themselves remain

## After sync

- Sync strips markdown formatting -- the GDoc becomes raw text. This is acceptable; pandoc handles PDF styling.
- Re-apply any hyperlinks that were in the markdown (DOI links, etc.) after each sync
- Upload the final PDF to your cloud storage after the GDoc is confirmed clean
