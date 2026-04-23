
from flask import Flask, abort, make_response, render_template_string, request, url_for
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
)
from reportlab.lib.units import inch
import qrcode
import io
import json
from pathlib import Path

app = Flask(__name__)

DATA_FILE = Path(__file__).with_name("territories.json")

PAGE_TEMPLATE = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>{{ t.id }} Territory</title>
  <style>
    body { font-family: Arial, sans-serif; margin:0; background:#f5f7fb; color:#111; }
    .wrap { max-width: 860px; margin: 0 auto; padding: 18px; }
    .card {
      background:white; border-radius:16px; padding:20px; margin-bottom:16px;
      box-shadow: 0 2px 10px rgba(0,0,0,.08);
    }
    h1,h2,h3 { margin:0 0 10px; }
    .sub { color:#555; margin-top:4px; }
    .grid {
      display:grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap:12px;
      margin-top:14px;
    }
    .meta { background:#f7f7f7; padding:14px; border-radius:12px; }
    .meta .label { font-size:13px; color:#666; margin-bottom:6px; }
    .meta .value { font-size:20px; font-weight:700; }
    .btns { display:grid; gap:12px; margin-top:16px; }
    .btn {
      display:block; text-align:center; text-decoration:none; font-weight:700;
      padding:16px 14px; border-radius:14px; font-size:20px;
    }
    .primary { background:#e91e63; color:white; }
    .secondary { background:#1f6feb; color:white; }
    .neutral { background:#1f2937; color:white; }
    ul { margin:10px 0 0 22px; padding:0; }
    li { margin:8px 0; font-size:20px; }
    .small { color:#666; font-size:14px; }
    .mapbox { margin-top:16px; }
    iframe { width:100%; min-height:380px; border:0; border-radius:14px; }
    .pill {
      display:inline-block; padding:6px 10px; border-radius:999px;
      background:#fff0f5; color:#c2185b; font-weight:700; margin-top:6px;
    }
    .share-note { margin-top:10px; color:#444; }
  </style>
</head>
<body>
  <div class="wrap">
    <div class="card">
      <h1>{{ t.id }}</h1>
      <div class="sub">{{ t.type }}</div>
      {% if t.status %}<div class="pill">{{ t.status }}</div>{% endif %}

      <div class="grid">
        <div class="meta">
          <div class="label">Area</div>
          <div class="value">{{ t.area }}</div>
        </div>
        <div class="meta">
          <div class="label">Assigned to</div>
          <div class="value">{{ t.assigned_to }}</div>
        </div>
        <div class="meta">
          <div class="label">Date due</div>
          <div class="value">{{ t.date_due }}</div>
        </div>
      </div>

      <div class="btns">
        <a class="btn primary" href="{{ t.google_map_url }}" target="_blank" rel="noopener">Open Map</a>
        <a class="btn secondary" href="{{ url_for('territory_pdf', territory_id=t.id) }}">Download PDF</a>
        <a class="btn neutral" href="#" onclick="shareTerritory(); return false;">Share Territory</a>
      </div>
      <div class="share-note small">On most phones, “Share Territory” opens the share sheet. If that is not supported, it copies the link.</div>
    </div>

    <div class="card">
      <h2>Custom</h2>
      <ul>
        {% for item in t.custom %}
          <li>{{ item }}</li>
        {% endfor %}
      </ul>
    </div>

    {% if t.working_notes %}
    <div class="card">
      <h2>Working Notes</h2>
      <p style="font-size:20px; line-height:1.5">{{ t.working_notes }}</p>
    </div>
    {% endif %}

    {% if t.map_embed_url %}
    <div class="card mapbox">
      <h2>Map Preview</h2>
      <iframe src="{{ t.map_embed_url }}" loading="lazy"></iframe>
      <div class="small" style="margin-top:10px;">If the preview does not load on your phone, use the “Open Map” button above.</div>
    </div>
    {% endif %}
  </div>

<script>
async function shareTerritory() {
  const shareUrl = window.location.href;
  const shareData = {
    title: "{{ t.id }} Territory",
    text: "{{ t.id }} - {{ t.area }}",
    url: shareUrl
  };

  if (navigator.share) {
    try {
      await navigator.share(shareData);
      return;
    } catch (e) {}
  }

  try {
    await navigator.clipboard.writeText(shareUrl);
    alert("Link copied.");
  } catch (e) {
    prompt("Copy this link:", shareUrl);
  }
}
</script>
</body>
</html>
"""

def load_data():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        items = json.load(f)
    by_id = {item["id"]: item for item in items}
    return by_id

def get_territory(territory_id):
    data = load_data()
    territory = data.get(territory_id.upper())
    if not territory:
        abort(404, description="Territory not found")
    return territory

def make_qr_code_image(data: str):
    qr = qrcode.QRCode(box_size=6, border=1)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf

@app.get("/")
def index():
    data = load_data()
    rows = []
    for territory_id, t in sorted(data.items()):
        rows.append(f'<li><a href="/t/{territory_id}">{territory_id}</a> - {t["area"]}</li>')
    return f"<h1>Territories</h1><ul>{''.join(rows)}</ul>"

@app.get("/t/<territory_id>")
def territory_page(territory_id):
    t = get_territory(territory_id)
    return render_template_string(PAGE_TEMPLATE, t=t)

@app.get("/t/<territory_id>.pdf")
def territory_pdf(territory_id):
    t = get_territory(territory_id)
    buf = io.BytesIO()

    doc = SimpleDocTemplate(
        buf,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36,
        title=f"{t['id']} Territory",
    )

    styles = getSampleStyleSheet()
    title_style = styles["Title"]
    h2 = styles["Heading2"]
    body = styles["BodyText"]
    body.leading = 16
    body.spaceAfter = 6

    small = ParagraphStyle(
        "small",
        parent=styles["BodyText"],
        fontSize=9,
        leading=11,
        textColor=colors.HexColor("#555555")
    )

    story = []
    story.append(Paragraph(f"{t['id']} - {t['type']}", title_style))
    story.append(Spacer(1, 10))

    meta_data = [
        ["Area", t["area"]],
        ["Assigned to", t["assigned_to"]],
        ["Date due", t["date_due"]],
    ]
    table = Table(meta_data, colWidths=[1.4 * inch, 4.6 * inch])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), colors.HexColor("#f4f4f4")),
        ("BOX", (0,0), (-1,-1), 0.5, colors.HexColor("#cccccc")),
        ("INNERGRID", (0,0), (-1,-1), 0.5, colors.HexColor("#cccccc")),
        ("FONTNAME", (0,0), (0,-1), "Helvetica-Bold"),
        ("PADDING", (0,0), (-1,-1), 8),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
    ]))
    story.append(table)
    story.append(Spacer(1, 16))

    story.append(Paragraph("Custom", h2))
    for item in t.get("custom", []):
        story.append(Paragraph(f"• {item}", body))
    story.append(Spacer(1, 10))

    if t.get("working_notes"):
        story.append(Paragraph("Working Notes", h2))
        story.append(Paragraph(t["working_notes"], body))
        story.append(Spacer(1, 10))

    story.append(Paragraph("Map", h2))
    story.append(Paragraph(
        f'<link href="{t["google_map_url"]}">{t["google_map_url"]}</link>',
        body
    ))
    story.append(Spacer(1, 12))

    public_url = request.url_root.rstrip("/") + url_for("territory_page", territory_id=t["id"])
    qr_buf = make_qr_code_image(public_url)
    qr_img = Image(qr_buf, width=1.4*inch, height=1.4*inch)
    story.append(Paragraph("Scan to open this territory page", small))
    story.append(Spacer(1, 6))
    story.append(qr_img)

    doc.build(story)
    pdf = buf.getvalue()
    buf.close()

    response = make_response(pdf)
    response.headers["Content-Type"] = "application/pdf"
    response.headers["Content-Disposition"] = f'inline; filename="{t["id"]}.pdf"'
    return response

import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
