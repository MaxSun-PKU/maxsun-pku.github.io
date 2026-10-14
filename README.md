# Shengxiu Sun

Source for the academic homepage at `https://maxsun-pku.github.io/`.

The site contains a biography, publication list, research summaries, CV, teaching and conference presentations, and two supplied personal photographs. The publication list distinguishes published articles, submitted preprints, and manuscripts in preparation. Recommendation letters and job-search documents are excluded.

## Edit

`content.json` contains profile details, publication metadata, and the site URL. `build_site.py` contains the page text and builds the static pages. Styles and browser interactions are in `dist/assets/`.

```sh
python3 build_site.py
python3 -m http.server 4174 --directory dist
```

## Publish

The GitHub repository must be named `maxsun-pku.github.io` under the `MaxSun-PKU` account. In Settings → Pages, select GitHub Actions as the publishing source. The included workflow builds and publishes the site on pushes to `main`.

The publishing workflow uploads only `dist/`. The biography is at `/`, and the other pages are at `/publications/`, `/research/`, `/cv/`, and `/more/`. The generator also creates `robots.txt`, `sitemap.xml`, and canonical URLs for this domain.

Google Search Console requires a separate ownership verification. Once verified, submit `https://maxsun-pku.github.io/sitemap.xml` and inspect the homepage URL. Publishing the site does not guarantee search indexing.
