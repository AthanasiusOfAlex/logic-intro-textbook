# TODO: Spanish Translation Review

## Items to check in previous translations

1. **Check for "entidad" usage**
   - Search for instances of "entidad" in Spanish translations
   - Replace with "ente" (plural: "entes") where appropriate
   - Files to check:
     - [md/sp/00-intro.md](md/sp/00-intro.md)
     - [md/sp/01-sciences-and-arts.md](md/sp/01-sciences-and-arts.md)

2. **Check em dash spacing**
   - Verify em dashes follow RAE rules with spaces
   - Format should be: `texto ---interrupción--- texto`
   - Space before first em dash, space after second em dash
   - Files to check:
     - [md/sp/00-intro.md](md/sp/00-intro.md)
     - [md/sp/01-sciences-and-arts.md](md/sp/01-sciences-and-arts.md)

## Search commands for review

```bash
# Search for "entidad" in Spanish files
grep -n "entidad" md/sp/*.md

# Search for em dashes to check spacing
grep -n "---" md/sp/*.md
```
