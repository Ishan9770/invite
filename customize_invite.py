#!/usr/bin/env python3
"""
customize_invite.py  -  edit the wedding invitation from ONE place.

HOW TO USE
  1. Put this file inside the site folder (next to index.html).
  2. Edit the settings in the "EDIT HERE" section below.
  3. Run:        python customize_invite.py
     Run + open: python customize_invite.py --serve
  4. Re-run it any time you change something. It always starts again from the
     untouched originals saved in the  _original/  folder (created on first run),
     so you can never "break" the site by running it twice.
  5. To go back to the very first version:  python customize_invite.py --reset

Images need Pillow once:   pip install pillow
"""

import argparse
import html as htmllib
import os
import re
import shutil
import sys

# =============================================================================
#                               EDIT HERE
# =============================================================================

# ---- 1. Bride & groom ------------------------------------------------------
GROOM = "Analjeet"
BRIDE = "Kriti"
FAMILY_NAME = "Thakur"          # used in: "the Pathak Family invites you ..."

# ---- 2. "With The Heavenly Blessings From" (one line per entry, add/remove freely)
HEAVENLY_BLESSINGS = [
    "Late Shri. Himmat Singh Thakur",
]

# ---- 3. Parents ------------------------------------------------------------
GROOM_PARENTS = "S/o. Kamal Thakur & Smt. Prerna Thakur"   # one paragraph under the groom
BRIDE_PARENTS = [                                                   # one line per entry under the bride
    "D/o. Shri. Sunil Vyas & Smt. Santosh Vyas",
    
]

# ---- 4. Venue / map --------------------------------------------------------
VENUE = {
    "name":    "Daga Palace",
    "address": "Daga Palace, Karoli Nagar, Dewas, Madhya Pradesh",   # shown in the panel next to the map
    "label":   "Dewas, Madhya Pradesh",                              # small tag on top-right of the map
    "coords":  "22.9562702, 76.0359719",                             # map pin (lat, long)
    "link":    "https://maps.app.goo.gl/FiZptQ3Lu5K459Lq5",          # "Open in Google Maps" button
    "zoom":    15,
    "eyebrow": "The Venue",               # small heading above the venue name ("" to hide)
    "show_schedule": True,                # list every function (from CARDS) inside the venue panel
    "directions_text": "Get Directions",  # text on the button under the address ("" to hide)
}

# ---- 5. RSVP (WhatsApp) ----------------------------------------------------
RSVP = {
    "whatsapp_number": "919770684291",               # country code + number, digits only (no + or spaces)
    "event_options":   ["You have to attend all"],   # choices in the "Select Event" dropdown (add more lines if needed)
}

# ---- 6. Itinerary cards (the site has exactly 6 cards: keys 1..6) ----------
# On the card the date line is shown as  CARD_DATE_FORMAT  (see below).
# "note" is only used if you set SHOW_NOTE_IN_VENUE_SCHEDULE = True.
CARDS = {
    1: {"title": "Haldi",        "day": "Wednesday", "date": "10 Feb 2027", "place": "Dewas, Madhya Pradesh", "time": "9 Am Onwards",    "note": "More details below"},
    2: {"title": "Mandap",       "day": "Wednesday", "date": "10 Feb 2027", "place": "Dewas, Madhya Pradesh", "time": "11 Am Onwards",   "note": "More details below"},
    3: {"title": "Sagai",        "day": "Wednesday", "date": "10 Feb 2027", "place": "Dewas, Madhya Pradesh", "time": "2 Pm Onwards",    "note": "More details below"},
    4: {"title": "Sangeet",      "day": "Wednesday", "date": "10 Feb 2027", "place": "Dewas, Madhya Pradesh", "time": "7:30 Pm Onwards", "note": "More details below"},
    5: {"title": "Phere",        "day": "Thursday",  "date": "11 Feb 2027", "place": "Dewas, Madhya Pradesh", "time": "9 Am Onwards",    "note": "More details below"},
    6: {"title": "Preeti Bhoj",  "day": "Thursday",  "date": "11 Feb 2027", "place": "Dewas, Madhya Pradesh", "time": "12 Pm Onwards",   "note": "More details below"},
}
CARD_DATE_FORMAT = "{date}, {day}"        # -> "10 Feb 2027, Wednesday"   (try "{day}, {date}")
SHOW_NOTE_IN_VENUE_SCHEDULE = False

# ---- 7. Other small things -------------------------------------------------
# Countdown timer target (ISO format, with timezone).  +05:30 = India time.
COUNTDOWN_TARGET = "2027-02-11T09:00:00+05:30"
PAGE_TITLE = f"{GROOM} weds {BRIDE}"   # browser-tab title

# ---- 8. IMAGES -------------------------------------------------------------
# Put your photos anywhere (e.g. in a folder called  my_photos/ ) and write the path.
# Leave a slot as None to keep the current image.  jpg / png / webp all work.
# Your photo is automatically cropped to fill the same shape as the old one and
# re-saved in all the sizes the site needs - you do NOT need to resize anything.
#
# NOTE: the two COVER images have the text ("Akash weds Drashti / date / Tap to Enter")
# baked into the picture, so make that cover artwork yourself and give it here.
#   cover_desktop : landscape 16:9   (current size 1600x900)
#   cover_mobile  : portrait  9:16   (current size 900x1600)
IMAGES = {
    # ---- your photos --------------------------------------------------------
    "cover_desktop":  None,   # e.g. "my_photos/cover_wide.jpg"
    "cover_mobile":   None,   # e.g. "my_photos/cover_tall.jpg"
    "featured_photo": None,   # big landscape couple photo        (862x575)
    "photo_strip_1":  None,   # scrolling photo strip, portrait   (462x662)
    "photo_strip_2":  None,   #                                   (323x462)
    "photo_strip_3":  None,   #                                   (333x475)
    "photo_strip_4":  None,   #                                   (382x546)
    "photo_strip_5":  None,   #                                   (424x606)

    # ---- decorative artwork (only change if you have matching artwork) ------
    "ganesha_icon":        None,   # orange Ganesha at the top           (94x130)
    "hero_garden_gazebos": None,   # garden path with two gazebos        (1201x1310)
    "hero_elephant_pond":  None,   # elephant & lotus pond               (1440x1783)
    "hero_mountains":      None,   # mountains / valley                  (1259x1247)
    "hero_sky":            None,   # sky gradient                        (1200x968)
    "hero_sun":            None,   # sun glow                            (400x339)
    "hero_clouds":         None,   # clouds                              (1200x968)
    "hero_tall_mandap":    None,   # tall mandap background              (1440x5394)
    "hero_tall_temple":    None,   # tall temple background              (1440x5187)
    "hero_tall_ground":    None,   # tall ground strip                   (868x4326)
    "bell_left":           None,   # hanging bell (left)                 (248x1774)
    "bell_right":          None,   # hanging bell (right)                (248x1774)
    "flag_pole":           None,   # flag pole                           (116x607)
    "border_top":          None,   # thin top border                     (684x112)
    "border_ellipse":      None,   # ellipse divider                     (1440x140)
    "divider_line":        None,   # thin ornament divider               (428x24)
    "divider_lotus":       None,   # pink lotus divider                  (330x130)
    "floral_top_1":        None,   # floral top border                   (1515x478)
    "floral_top_2":        None,   # floral arch top                     (1600x838)
    "event_card_frame":    None,   # background frame of itinerary cards (1515x2342, png)
    "frame_rect":          None,   # rectangular frame                   (864x592, png)
    "frame_ornate":        None,   # ornate oval frame                   (674x830)
    "ornament_diamond":    None,   # diamond ornament                    (280x280)
    "sunburst_1":          None,   # (142x205)
    "sunburst_2":          None,   # (140x202)
    "sunburst_3":          None,   # (143x206)
}

# =============================================================================
#                       END OF SETTINGS - do not edit below
# =============================================================================

HERE = os.path.dirname(os.path.abspath(__file__))
SITE_JS_DIR = None
for _d in os.listdir(os.path.join(HERE, "sites")) if os.path.isdir(os.path.join(HERE, "sites")) else []:
    if os.path.exists(os.path.join(HERE, "sites", _d, "shared-lib.BPw4mLPm.mjs")):
        SITE_JS_DIR = os.path.join("sites", _d)
JS_REL = os.path.join(SITE_JS_DIR, "shared-lib.BPw4mLPm.mjs") if SITE_JS_DIR else None
HTML_REL = "index.html"
BACKUP = os.path.join(HERE, "_original")

# image slot -> original file(s) in images/  (variants -1/-2 are found automatically)
IMAGE_FILES = {
    "cover_desktop": "1WwE8dzVbfyyznXeI0zdv36r0.webp",
    "cover_mobile": "tcOGEtIW1cwCny8iA30UyIl2m0.webp",
    "featured_photo": "cuJqbfW35i2RRVw2Q3Vaix9WO8I.webp",
    "photo_strip_1": "Bqgd6mCInGuKi2DkoylipkjZttQ.webp",
    "photo_strip_2": "X2k4WiGTIyjwCt0kYjvNFw6Ew.webp",
    "photo_strip_3": "sjHDfRZ61KmVp6cmbH6fTVWk8wQ.webp",
    "photo_strip_4": "vMtYMMpb3RXorGzKKQ7HrjYVc.webp",
    "photo_strip_5": "xx4y0hmowXnxGqMdaJGre6xiLNM.webp",
    "ganesha_icon": "5FVM3OmFePuLZFoKyYpESSXgaE.webp",
    "hero_garden_gazebos": "6TXoawcenoOWcnQlzINrKDWObE.webp",
    "hero_elephant_pond": "A8wZo3T1skxgl2PmEFeRcc5ujY.webp",
    "hero_mountains": "HqjJi7nGgVS7OCvQQhSxu4ZHtp8.webp",
    "hero_sky": "ELVgHUKqtqAl9gf1nwbYhSeTg.webp",
    "hero_sun": "CAJYZSTyHrLw4D8Gxv3UGjFaMg.webp",
    "hero_clouds": "qTlCAkdnbuZVEx4RAWSlgsGHX0.webp",
    "hero_tall_mandap": "CXndWLPXOgg6uXLmUF900AC6VA.webp",
    "hero_tall_temple": "VAPiNRpZS70jx7TG6S1mnc6YM.webp",
    "hero_tall_ground": "RERsf0FzAyHP3XzTjLuKTTrvtU8.webp",
    "bell_left": "9mGbdQrz7F3caMjWkMSJDVKxYg.webp",
    "bell_right": "IbytQqqRrapGMzTHP2x8mqvSDgA.webp",
    "flag_pole": "plRMuObVZgXFVWzrOuY2xNVRHHs.webp",
    "border_top": "7Jr9KCHDFL5pwPFZFeisN44Yzi4.webp",
    "border_ellipse": "RNlpugn7P3pGC6PCD02o3SRlvMk.webp",
    "divider_line": "T7c0PLf2sfUhiq0SlGf4frlVQMA.webp",
    "divider_lotus": "pyLtbhSLIRf4NHAy72amY2aW58.webp",
    "floral_top_1": "XEME29GdiyV3RDHfslzLVTpFP1g.webp",
    "floral_top_2": "Y6Fdke7ERBoQcnHXW1RLN1E.webp",
    "event_card_frame": "TUkRvFIUDwblbb4eewkBlJzZwJw.png",
    "frame_rect": "are7oBx1tbG76Oy5UqSq8sFoJ4.png",
    "frame_ornate": "nGPy0RPGbGwAd8w8op4XKveKWM.webp",
    "ornament_diamond": "ciPCtoLf1PEnCNBnsx6boOBPU.webp",
    "sunburst_1": "dU6QWYOyKfqMfHH3mCT84Z3dAJE.webp",
    "sunburst_2": "gt4WrIeOxcZz1kQLQ9ovWBkpc.webp",
    "sunburst_3": "lsI4FJ0BeiT9e8FhL5WYmPRlnyY.webp",
}

# ORIGINAL texts inside the site (what we search for)
O_GROOM, O_BRIDE, O_FAMILY = "Akash", "Drashti", "Pathak"
O_HEAVENLY = ["Late Shri. Rajmani Pathak & Smt. Ambika Pathak ", "S/o. Shri. Rajmani Pathak & Smt. Ambika Pathak "]
O_GROOM_PARENTS = "G/S/o. Shri. Rajmani Pathak & Smt. Ambika Pathak S/o. Shri. Rajmani Pathak & Smt. Ambika Pathak "
O_BRIDE_PARENTS = ["G/S/o. Shri. Rajmani Pathak & Smt. Ambika Pathak", "S/o. Shri. Rajmani Pathak & Smt. Ambika Pathak"]
O_TITLES = ["Ring Ceremony", "Haldi & Mehendi", " Mayra", "Sangeet Night", "Wedding", "Reception"]
O_DATE, O_PLACE, O_TIME = "29th Aug 2026, Friday", "Pune, Maharashtra", "6 Pm Onwards"
O_COUNTDOWN = "2026-11-28T16:04:00.000Z"
O_TITLE = "My Framer Site"


# ----------------------------------------------------------------- helpers ---
def js(s):
    """escape text for a JS template literal (`...`)"""
    return s.replace("\\", "\\\\").replace("`", "\\`").replace("${", "\\${")


def hx(s):
    return htmllib.escape(s, quote=False)


def must_replace(text, old, new, label, count=None):
    n = text.count(old)
    if n == 0:
        print(f"  ! WARNING: could not find {label}")
        return text
    if count is not None and n != count:
        print(f"  ! note: {label}: expected {count} place(s), found {n}")
    return text.replace(old, new)


def replace_nth_groups(text, old, new_list, label, group_name):
    """old text appears (6*k) times, grouped by event in order -> replace by event index."""
    pos = [m.start() for m in re.finditer(re.escape(old), text)]
    if not pos:
        print(f"  ! WARNING: could not find {label}")
        return text
    if len(pos) % 6:
        print(f"  ! WARNING: {label}: {len(pos)} matches is not a multiple of 6 - skipped")
        return text
    per = len(pos) // 6
    out, last = [], 0
    for i, p in enumerate(pos):
        out.append(text[last:p])
        out.append(new_list[i // per])
        last = p + len(old)
    out.append(text[last:])
    return "".join(out)


def rebuild_p_runs(text, olds, new_lines, mode, label):
    """Find consecutive <p> elements holding `olds` and rebuild them with `new_lines`."""
    if mode == "js":
        one = r"(/\*#__PURE__\*/ h\(`p`,\{(?:(?!/\*#__PURE__\*/).)*?children:`)%s(`\}\))"
        pat = ",".join(one % re.escape(o) for o in olds)

        def sub(m):
            g = m.groups()
            pre, post = g[0], g[1]
            return ",".join(f"{pre}{js(l)}{post}" for l in new_lines)
    else:
        one = r"(<p [^>]*>)%s(</p>)"
        pat = "".join(one % re.escape(hx(o)) for o in olds)

        def sub(m):
            g = m.groups()
            return "".join(f"{g[0]}{hx(l)}{g[1]}" for l in new_lines)

    new, n = re.subn(pat, sub, text, flags=re.S)
    if n == 0:
        print(f"  ! WARNING: could not find {label}")
    return new


# ------------------------------------------------------------- main patching --
def card_fields():
    cards = []
    for k in range(1, 7):
        c = CARDS.get(k)
        if not c:
            sys.exit(f"CARDS needs entries 1..6 (missing {k}); the layout has exactly 6 cards.")
        date_line = CARD_DATE_FORMAT.format(date=c["date"], day=c["day"])
        cards.append((c["title"], date_line, c["place"], c["time"]))
    extra = [k for k in CARDS if k not in range(1, 7)]
    if extra:
        print(f"  ! note: cards {extra} ignored - the design only has 6 cards")
    return cards


def schedule_lines():
    lines = []
    for k in range(1, 7):
        c = CARDS[k]
        line = f"{c['title']} \u2014 {c['date']}, {c['time']}"
        if SHOW_NOTE_IN_VENUE_SCHEDULE and c.get("note"):
            line += f" ({c['note']})"
        lines.append(line)
    return lines


def patch_js(s):
    # names
    s = must_replace(s, f"children:`{O_GROOM}`", f"children:`{js(GROOM)}`", "groom name (js)")
    s = must_replace(s, f"children:`{O_BRIDE}`", f"children:`{js(BRIDE)}`", "bride name (js)")
    s = must_replace(s, f"the {O_FAMILY} Family invites", f"the {js(FAMILY_NAME)} Family invites", "family name (js)")

    # heavenly blessings / parents
    s = rebuild_p_runs(s, O_HEAVENLY, HEAVENLY_BLESSINGS, "js", "heavenly blessings (js)")
    s = rebuild_p_runs(s, O_BRIDE_PARENTS, BRIDE_PARENTS, "js", "bride parents (js)")
    s = must_replace(s, f"children:`{O_GROOM_PARENTS}`", f"children:`{js(GROOM_PARENTS)}`", "groom parents (js)")

    # cards
    cards = card_fields()
    for old, (title, *_r) in zip(O_TITLES, cards):
        s = must_replace(s, f"children:`{old}`", f"children:`{js(title)}`", f"card title '{old}' (js)")
    s = replace_nth_groups(s, f"children:`{O_DATE}`", [f"children:`{js(c[1])}`" for c in cards], "card dates (js)", "date") \
        if False else _nth(s, f"children:`{O_DATE}`", [f"children:`{js(c[1])}`" for c in cards], "card dates (js)")
    s = _nth(s, f"children:`{O_PLACE}`", [f"children:`{js(c[2])}`" for c in cards], "card places (js)")
    s = _nth(s, f"children:`{O_TIME}`", [f"children:`{js(c[3])}`" for c in cards], "card times (js)")

    # RSVP
    s = must_replace(s, "whatsappNumber:`919819200906`", f"whatsappNumber:`{re.sub(r'[^0-9]', '', RSVP['whatsapp_number'])}`", "whatsapp number")
    opts = ",".join(f"`{js(o)}`" for o in RSVP["event_options"])
    s = must_replace(s, "eventOptions:[`Mehendi`,`Sangeet`,`Wedding Ceremony`,`Reception`],eventPlaceholder",
                     f"eventOptions:[{opts}],eventPlaceholder", "RSVP event options")
    if len(RSVP["event_options"]) <= 1:   # one choice -> single select (tap & done)
        s = must_replace(s, "h(Xv,{allowMultipleEvents:!0,borderRadius:20", "h(Xv,{allowMultipleEvents:!1,borderRadius:20", "RSVP single select")

    # countdown
    s = must_replace(s, f"targetDate:`{O_COUNTDOWN}`", f"targetDate:`{js(COUNTDOWN_TARGET)}`", "countdown date")

    # venue / map -----------------------------------------------------------
    V = VENUE
    sched = schedule_lines() if V.get("show_schedule") else []
    loc = (f"locations:[{{addressHeader:`{js(V['name'])}`,addressSubtext:`{js(V['address'])}`,"
           f"buttonLabel:`{js(V['name'])}`,coordinates:`{js(V['coords'])}`,id:`kB9sQ_Os7`,"
           f"overlayLabel:`{js(V['label'])}`,zoom:{int(V['zoom'])},link:`{js(V['link'])}`,"
           f"eyebrow:`{js(V.get('eyebrow', ''))}`,directionsText:`{js(V.get('directions_text', ''))}`,"
           f"schedule:[{','.join('`' + js(x) + '`' for x in sched)}]}}],mapHeight:320,name:`Map Details`")
    s, n = re.subn(r"locations:\[\{addressHeader:`Venue Name`,addressSubtext:`M10.*?\}\],mapHeight:320,name:`Map Details`",
                   lambda m: loc, s, flags=re.S)
    if n != 1:
        print(f"  ! WARNING: map locations block matched {n} times")

    # teach the map component about: custom link, eyebrow, schedule, directions button
    a = "let ue=L?`https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(L.coordinates||``)}`:`#`;"
    b = "let ue=L?(L.link||`https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(L.coordinates||``)}`):`#`;"
    s = must_replace(s, a, b, "map link hook", 1)

    a = "me=L&&/*#__PURE__*/ m(d,{children:[/*#__PURE__*/ h(`div`,{style:{fontSize:18,fontWeight:700,...S,marginBottom:6},children:L.addressHeader}),"
    b = ("me=L&&/*#__PURE__*/ m(d,{children:[L.eyebrow?/*#__PURE__*/ h(`div`,{style:{fontSize:12,letterSpacing:`0.16em`,textTransform:`uppercase`,"
         "opacity:.7,marginBottom:6,fontWeight:600},children:L.eyebrow}):null,"
         "/*#__PURE__*/ h(`div`,{style:{fontSize:18,fontWeight:700,...S,marginBottom:6},children:L.addressHeader}),")
    b = b.replace("textTransform:`uppercase`", "textTransform:`uppercase`")
    s = must_replace(s, a, b, "map eyebrow hook", 1)

    a = "children:L.addressSubtext}),/*#__PURE__*/ h(`button`,{onClick:z,"
    b = ("children:L.addressSubtext}),"
         "L.schedule&&L.schedule.length>0?/*#__PURE__*/ h(`div`,{style:{marginTop:14,display:`flex`,flexDirection:`column`,gap:4,fontSize:13,lineHeight:1.35},"
         "children:L.schedule.map((t,i)=>/*#__PURE__*/ h(`div`,{style:{opacity:.9},children:t},i))}):null,"
         "L.directionsText?/*#__PURE__*/ h(`a`,{href:ue,target:`_blank`,rel:`noopener noreferrer`,style:{display:`inline-block`,marginTop:16,"
         "padding:`10px 18px`,borderRadius:8,border:`1px solid ${p}`,color:p,textDecoration:`none`,fontSize:14,fontWeight:600},"
         "children:L.directionsText}):null,"
         "/*#__PURE__*/ h(`button`,{onClick:z,")
    s = must_replace(s, a, b, "map schedule/directions hook", 1)
    return s


def _nth(text, old, new_list, label):
    return replace_nth_groups(text, old, new_list, label, "")


def patch_html(h):
    cards = card_fields()
    # names
    h = must_replace(h, f">{O_GROOM}</p>", f">{hx(GROOM)}</p>", "groom name (html)")
    h = must_replace(h, f">{O_BRIDE}</p>", f">{hx(BRIDE)}</p>", "bride name (html)")
    h = must_replace(h, f"the {O_FAMILY} Family invites", f"the {hx(FAMILY_NAME)} Family invites", "family name (html)")
    h = rebuild_p_runs(h, O_HEAVENLY, HEAVENLY_BLESSINGS, "html", "heavenly blessings (html)")
    h = rebuild_p_runs(h, O_BRIDE_PARENTS, BRIDE_PARENTS, "html", "bride parents (html)")
    h = must_replace(h, f">{hx(O_GROOM_PARENTS)}</p>", f">{hx(GROOM_PARENTS)}</p>", "groom parents (html)")

    # cards
    for old, (title, *_r) in zip(O_TITLES, cards):
        h = must_replace(h, f">{hx(old)}<", f">{hx(title)}<", f"card title '{old}' (html)")
    h = _nth(h, f">{O_DATE}<", [f">{hx(c[1])}<" for c in cards], "card dates (html)")
    h = _nth(h, f">{O_PLACE}<", [f">{hx(c[2])}<" for c in cards], "card places (html)")
    h = _nth(h, f">{O_TIME}<", [f">{hx(c[3])}<" for c in cards], "card times (html)")

    # map (server-rendered placeholder - the live version is built from the JS)
    V = VENUE
    h = h.replace("https://www.google.com/maps/search/?api=1&amp;query=19.2183%2C%2072.9781", htmllib.escape(V["link"]))
    h = h.replace("https://www.google.com/maps/search/?api=1&query=19.2183%2C%2072.9781", htmllib.escape(V["link"]))
    h = h.replace(">Nearby Location<", f">{hx(V['label'])}<")
    h = h.replace(">Venue Name<", f">{hx(V['name'])}<")
    h = re.sub(r">M10\ngeomatrix.*?9819200906<", f">{hx(V['address'])}<", h, flags=re.S)
    h = h.replace("Map showing Location 1", f"Map showing {hx(V['name'])}")
    # drop the placeholder "Location 1 / Location 2 ..." selector buttons
    h = re.sub(r'<div style="[^"]*"><button style="[^"]*">Location 1</button>.*?</div>', "", h, count=1, flags=re.S)

    # tab title
    h = must_replace(h, f"<title>{O_TITLE}</title>", f"<title>{hx(PAGE_TITLE)}</title>", "page title")
    h = h.replace(f'content="{O_TITLE}"', f'content="{htmllib.escape(PAGE_TITLE)}"')
    return h


# ------------------------------------------------------------------- images ---
def process_images():
    todo = {k: v for k, v in IMAGES.items() if v}
    if not todo:
        return
    try:
        from PIL import Image, ImageOps
    except ImportError:
        sys.exit("Images need Pillow:  pip install pillow")
    img_dir, bak_img = os.path.join(HERE, "images"), os.path.join(BACKUP, "images")
    os.makedirs(bak_img, exist_ok=True)
    for slot, src in todo.items():
        if slot not in IMAGE_FILES:
            print(f"  ! unknown image slot '{slot}'")
            continue
        src_path = src if os.path.isabs(src) else os.path.join(HERE, src)
        if not os.path.exists(src_path):
            print(f"  ! image for '{slot}' not found: {src}")
            continue
        base, ext = os.path.splitext(IMAGE_FILES[slot])
        targets = [IMAGE_FILES[slot]] + [f"{base}-{i}{ext}" for i in (1, 2) if os.path.exists(os.path.join(img_dir, f"{base}-{i}{ext}"))]
        im = ImageOps.exif_transpose(Image.open(src_path))
        for t in targets:
            orig = os.path.join(bak_img, t)
            cur = os.path.join(img_dir, t)
            if not os.path.exists(orig):
                shutil.copy2(cur, orig)               # keep the original forever
            w, h_ = Image.open(orig).size
            fitted = ImageOps.fit(im.convert("RGBA"), (w, h_), Image.LANCZOS, centering=(0.5, 0.4))
            if t.lower().endswith(".png"):
                fitted.save(cur, "PNG", optimize=True)
            else:
                fitted.save(cur, "WEBP", quality=88, method=4)
        print(f"  image  {slot:<20} <- {src}")


def restore_images():
    bak_img = os.path.join(BACKUP, "images")
    if os.path.isdir(bak_img):
        for f in os.listdir(bak_img):
            shutil.copy2(os.path.join(bak_img, f), os.path.join(HERE, "images", f))


# --------------------------------------------------------------------- main ---
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--serve", action="store_true", help="start the local server after building")
    ap.add_argument("--reset", action="store_true", help="restore the original site and exit")
    args = ap.parse_args()

    if not JS_REL:
        sys.exit("Run this script from inside the site folder (next to index.html and sites/).")
    os.makedirs(BACKUP, exist_ok=True)
    for rel in (HTML_REL, JS_REL):
        bak = os.path.join(BACKUP, os.path.basename(rel))
        if not os.path.exists(bak):
            shutil.copy2(os.path.join(HERE, rel), bak)

    orig_html = open(os.path.join(BACKUP, os.path.basename(HTML_REL)), encoding="utf-8").read()
    orig_js = open(os.path.join(BACKUP, os.path.basename(JS_REL)), encoding="utf-8").read()

    if args.reset:
        open(os.path.join(HERE, HTML_REL), "w", encoding="utf-8").write(orig_html)
        open(os.path.join(HERE, JS_REL), "w", encoding="utf-8").write(orig_js)
        restore_images()
        print("Restored the original site.")
        return

    print("Patching text ...")
    new_js = patch_js(orig_js)
    print("Patching page ...")
    new_html = patch_html(orig_html)
    open(os.path.join(HERE, JS_REL), "w", encoding="utf-8").write(new_js)
    open(os.path.join(HERE, HTML_REL), "w", encoding="utf-8").write(new_html)

    print("Images ...")
    restore_images()          # start from originals so removed slots go back to normal
    process_images()

    print("\nDone.  Run  python serve.py  (or re-run this with --serve) and open http://localhost:8000")
    print("Hard-refresh the browser (Ctrl+Shift+R) if you still see old content.")
    if args.serve:
        os.chdir(HERE)
        os.execv(sys.executable, [sys.executable, "serve.py"])


if __name__ == "__main__":
    main()
