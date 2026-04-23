# Territory Share Portal

A simple Flask app that turns the "Google Map" link field in your app into a smart territory page.

## What it does

When a publisher taps your custom link, they get a simple page with:

- **Open Map**
- **Download PDF**
- **Share Territory**

The PDF includes the territory details and a QR code back to the page.

## Why this fits your use case

You said most publishers are not tech-savvy and the real goal is **sharing the territory with others**.
This approach keeps everything simple:

1. Put your custom link in the app instead of the raw Google Maps link.
2. User taps it.
3. Your page opens.
4. They tap **Share Territory** or **Download PDF**.

No app install, no scripting, no Android permissions, no screenshots.

## Setup

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Mac/Linux
source .venv/bin/activate

pip install -r requirements.txt
python app.py
```

Open:
- `http://127.0.0.1:5000/`
- Territory example: `http://127.0.0.1:5000/t/LO-541`

## Replace the app link

Instead of storing the raw Google Maps link in the app, store your territory page link:

```text
https://yourdomain.com/t/LO-541
```

Inside `territories.json`, still keep the real `google_map_url`, so the **Open Map** button works.

## Editing territory data

Edit `territories.json`. Add one object per territory.

Example fields:

- `id`
- `type`
- `area`
- `assigned_to`
- `date_due`
- `google_map_url`
- `map_embed_url`
- `custom` (list)
- `working_notes`

## Deploying

Easy options:
- Render
- Railway
- Fly.io
- PythonAnywhere
- Your own VPS

## Notes

- `map_embed_url` is optional. If you do not have an embeddable map URL, leave it blank.
- The **Share Territory** button uses the phone's normal share sheet when supported.
- The PDF is generated on demand.

## Next good upgrade

If you want, the next step would be:
- password or token protection
- "assigned to" hidden from public viewers
- one-click WhatsApp share text
- printable card layout
- CSV import/export for all territories
