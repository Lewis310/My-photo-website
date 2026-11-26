# Photography portfolio

Static site (HTML, CSS, JS). No build step.

```
index.html     page layout and text (edit headings, intro, contact here)
css/style.css  styling
js/main.js     gallery, filters, lightbox
data.json      your photos and their background info
photos/        your image files
```

## Add or edit photos
1. Export photos at about 2000px on the long edge (JPEG, under ~500 KB each) and put them in `photos/`. Avoid spaces in file names.
2. Edit `data.json`. One entry per photo:
   ```json
   {"t":"Dawn Ridge","c":"landscape","img":"photos/dawn-ridge.jpg","r":"4/5",
    "alt":"Sunrise over a ridge","loc":"Blue Mountains, NSW","date":"June 2026",
    "cam":"Sony A7 IV","set":"f/8 · 1/250s · ISO 100","story":"Why I took it..."}
   ```
   - `t` title, `c` category (filter buttons are created automatically from these)
   - `img` file path. Leave `""` to show a coloured placeholder (uses `g`, two hex colours)
   - `r` width/height ratio such as `"3/2"` or `"4/5"`. Optional but avoids layout jumps
   - `loc`, `date`, `cam`, `set`, `story` are all optional; empty ones are hidden
   - `hero` at the top of the file is the big hero image path (optional)
3. Photo order in the file is the order on the page.

Tip: GitHub lets you edit `data.json` and upload images right in the browser (Add file > Upload files).

## Run locally
`data.json` is loaded with fetch, so open it through a server rather than double-clicking:
```
python3 -m http.server 8000
```
then visit http://localhost:8000

## Deploy on GitHub Pages
1. Create a new repo on GitHub, e.g. `photography-portfolio` (public).
2. Upload this folder's contents, or from this folder run:
   ```
   git init
   git add .
   git commit -m "Initial portfolio"
   git branch -M main
   git remote add origin https://github.com/Lewis310/photography-portfolio.git
   git push -u origin main
   ```
3. In the repo: Settings > Pages > Source: "Deploy from a branch", Branch: `main`, folder `/ (root)` > Save.
4. After a minute it is live at https://lewis310.github.io/photography-portfolio/

Every push to `main` redeploys automatically. For a custom domain, add it under Settings > Pages and point a DNS CNAME at `lewis310.github.io`.

## Notes
- The contact section is a `mailto:` link. Change the address in `index.html`. For a working form, a service like Formspree or Web3Forms can be added.
- Remove GPS/location data from photos before publishing (most export tools have an option).
