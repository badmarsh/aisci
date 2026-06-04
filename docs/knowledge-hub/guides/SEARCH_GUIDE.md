# Search and Discovery Guide

How to find information effectively in the Multica Knowledge Hub.

## Using the CLI

Search for keywords:
```bash
multica issue search "blast-wave"
```

Filter by label:
```bash
multica issue list --label research
```

Combine filters:
```bash
multica issue list --label physics --label decision
```

## Advanced Search with JSON
If you need structured results for further processing:
```bash
multica issue list --output json | jq '.[] | select(.labels[] == "research")'
```

## Search Strategies
- **Search by Domain**: Start with a broad domain label (`physics`) if you're not sure about keywords.
- **Search by Type**: Look at all `decision` issues to understand the project's evolution.
- **Check Related Work**: Use the links in issue descriptions to navigate the knowledge graph.
