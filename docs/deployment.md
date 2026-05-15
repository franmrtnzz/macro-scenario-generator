# Deployment

The dashboard in `web/` is a static browser app. Anyone with the deployed URL can access it directly.

## Recommended Static Hosts

- GitHub Pages: publish the `web/` directory.
- Netlify: set publish directory to `web` and leave build command empty.
- Vercel: configure as a static project and use `web` as the output directory.
- Cloudflare Pages: leave build command empty and set output directory to `web`.

No backend, API key or database is required for the public platform.

## GitHub Pages Workflow

The repository includes `.github/workflows/pages.yml`, which publishes `web/` through GitHub Pages on every push to `main`.

In the repository settings, GitHub Pages must use `GitHub Actions` as the source. After the first successful run, GitHub will generate the public URL.

## Local Preview

```bash
python -m http.server 8000 -d web
```

Open `http://localhost:8000`.

## Launch Checklist

- Generate the final public platform URL.
- Test the link in an incognito/private browser window.
- Update the link in the LinkedIn publication.
- Update the link in the website article.
- Re-test both public entry points.
