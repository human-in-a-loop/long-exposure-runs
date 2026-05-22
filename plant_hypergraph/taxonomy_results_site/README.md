# PhytoGraph Taxonomy Results Review Site

Serve the folder locally:

```bash
python3 -m http.server 8765 --directory taxonomy_results_site
```

Then visit `http://127.0.0.1:8765/`.

The page loads local JSON evidence tables, so a small local web server is recommended instead of opening the HTML file directly.

The site is a public-facing teaching and expert-review layer over the closed PhytoGraph study. It summarizes the accepted-name substrate, six biological themes, validation limits, source-bias findings, and future evidence predicates. It does not reopen evidence collection or promote new biological claims.
