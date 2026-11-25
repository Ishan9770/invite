Akash weds Drashti – wedding invitation (Framer site, rebuilt locally)

HOW TO RUN
  python serve.py      -> opens http://localhost:8000
  (or: npx serve .  /  VS Code "Live Server").  Do not double-click index.html:
  browsers block ES modules from file://, which is what runs the animations.

WHAT'S IN HERE
  index.html                  working site: loc1 markup + Framer runtime, wired to local assets
  sites/<id>/*.mjs            Framer runtime + page code (from loc1.zip); gsap / ScrollTrigger
                              rebuilt from npm (gsap 3.12.5) because loc1 didn't include them
  images/, assets/, s/        images, fonts, music (asset-029.mp3 = main background track)
  index.static-snapshot.html  the original Sitepeel static snapshot (no animations), kept for reference
  styles.css, assets.json, snapshot.json   original snapshot files

ANIMATIONS NOW WORKING
  tap-to-enter cover + music, hero appear (names, temple, mountains, clouds, sun, bells, flag),
  scroll-linked hero parallax, swinging bells, birds, WebGL waving flag, scroll-fill text,
  marquee photo strip, countdown, RSVP/map blocks.

NEEDS INTERNET (not included in either zip)
  - flag texture  images/ea6WAeUsN6PJaauIQhAYB0hyDQ.webp  (loaded from framerusercontent.com)
  - bell chime sounds (h45eKdEQgEZsNQLY8z9lrI3tuY.mp3)
  - map tiles / Leaflet (unpkg + OpenStreetMap), Inter font from Google Fonts
