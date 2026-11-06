"""Build the price list workbook from the products on the website.

Every product in index.html, with its code, grouped by what it "shows under"
(Scrunchies, Claw Clips, Coasters...), plus a Price Groups sheet where one
price is set per group, and the checklist for the cart and Razorpay.

    pip install openpyxl
    python bot/price_list.py index.html Mayuriz-Price-List.xlsx

The filled-in workbook holds costs and profit, so keep it out of this public
repository. Only selling prices belong on the site.
"""
import re, sys
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.comments import Comment
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.formatting.rule import FormulaRule

SRC, OUT = sys.argv[1], sys.argv[2]
html = open(SRC, encoding="utf-8").read()
blk = html[html.index("/* PRODUCTS:START */"):html.index("/* PRODUCTS:END */")]
def unjs(v): return v.replace("\\'", "'").replace("\\\\", "\\")
S = r"'((?:[^'\\]|\\.)*)'"
products = []
for m in re.finditer(r"\{\s*id: %s,\s*sku: %s,\s*name: %s,\s*cat: %s, tag: %s(?:, badge: %s)?(?:, fresh: true)?,\s*desc: %s,\s*image: %s" % ((S,)*8), blk):
    pid, sku, name, cat, tag, badge, desc, image = [unjs(x) if x else "" for x in m.groups()]
    products.append(dict(id=pid, sku=sku, name=name, cat=cat, tag=tag, badge=badge, desc=desc, image=image))
assert len(products) == len(re.findall(r"sku: 'MZ-", blk)), "parse missed products"

GROUPS = [  # code, shows under, website category, suggested HSN
    ("SCR", "Scrunchies", "Scrunchies", "6117"),
    ("BOW", "Bows", "Bows", "6117"),
    ("HBD", "Hair Bands", "Claw Clips", "6117"),
    ("CLW", "Claw Clips", "Claw Clips", "9615"),
    ("HCL", "Hair Clips", "Claw Clips", "9615"),
    ("HPN", "Hair Pins", "Claw Clips", "9615"),
    ("ROS", "Roses", "Flowers & Roses", "6702"),
    ("FLW", "Flowers", "Flowers & Roses", "6702"),
    ("GAR", "Garlands", "Garlands", "6702"),
    ("KEY", "Keychains", "Keychains", "6307"),
    ("CHM", "Charms", "Keychains", "6307"),
    ("HRT", "Hearts", "Hearts", "6307"),
    ("BMK", "Bookmarks", "Bookmarks", "6307"),
    ("CST", "Coasters", "Coasters", "6304"),
    ("BNG", "Bangles", "Bangles", "7117"),
    ("BAG", "Bags", "Bags", "4202"),
]
CODE = {g[1]: g[0] for g in GROUPS}
ORDER = {g[0]: i for i, g in enumerate(GROUPS)}
for p in products:
    p["group"] = p["sku"].split("-")[1]
    assert p["group"] in ORDER, p
products.sort(key=lambda p: (ORDER[p["group"]], int(p["sku"].split("-")[2])))

def set_size(p):
    t = (p["badge"] + " " + p["name"]).lower()
    m = re.search(r"set of (\d+)", t)
    if m: return int(m.group(1))
    for w, n in (("trio", 3), ("pair", 2), ("duo", 2)):
        if w in t: return n
    return 1

SECOND_PHOTO = {
    "sunflower-clips-detail": "sunflower-clips-pair",
    "sunflower-keychain-tagged": "sunflower-keychain",
    "scallop-bow": "classic-bow",
}
by_id = {p["id"]: p for p in products}

# ---------- styles ----------
F = "Arial"
base = Font(name=F, size=10)
bold = Font(name=F, size=10, bold=True)
head = Font(name=F, size=10, bold=True, color="FFFFFF")
title = Font(name=F, size=16, bold=True, color="7A2E2E")
sub = Font(name=F, size=10, italic=True, color="666666")
inp = Font(name=F, size=10, color="0000FF")
link = Font(name=F, size=10, color="008000")
HEAD = PatternFill("solid", fgColor="7A2E2E")
YELLOW = PatternFill("solid", fgColor="FFF2B3")
GROUPF = PatternFill("solid", fgColor="F3E3D3")
GREY = PatternFill("solid", fgColor="F2F2F2")
thin = Side(style="thin", color="D9D9D9")
box = Border(left=thin, right=thin, top=thin, bottom=thin)
wrap = Alignment(wrap_text=True, vertical="top")
center = Alignment(horizontal="center", vertical="center", wrap_text=True)
RUPEE = '"₹"#,##0;("₹"#,##0);"-"'
PCT = '0.0%;(0.0%);"-"'

wb = Workbook()

# ================= How to Use =================
ws = wb.active; ws.title = "How to Use"
ws.sheet_view.showGridLines = False
ws.column_dimensions["A"].width = 3
ws.column_dimensions["B"].width = 26
for c in "CDEFG": ws.column_dimensions[c].width = 16
ws["B2"] = "Mayuri'z — Price List & Product Codes"; ws["B2"].font = title
ws["B3"] = f"{len(products)} products in {len(GROUPS)} price groups, taken from the live website. Fill in the yellow cells; everything else works itself out."
ws["B3"].font = sub
r = 5
ws.cell(r, 2, "Colour key").font = bold; r += 1
for fill, font, text in [
    (YELLOW, inp, "Yellow cell, blue text — you type here"),
    (None, base, "Black text — a formula, leave it alone"),
    (None, link, "Green text — pulled from the Price Groups sheet"),
    (GROUPF, bold, "Beige row — a product group heading"),
]:
    c = ws.cell(r, 2, "Sample"); c.font = font; c.border = box
    if fill: c.fill = fill
    ws.cell(r, 3, text).font = base; r += 1
r += 1
ws.cell(r, 2, "Steps").font = bold; r += 1
for i, t in enumerate([
    "Price Groups sheet: set one Selling Price (and MRP if you want a 'was' price) for each kind of product. Every product in that group takes this price.",
    "Products sheet: a piece that should cost more or less than its group (a set of 3, a big bouquet) gets its own price in 'Own Price'. Leave it empty to use the group price.",
    "Fill Making Cost, Making Time and Weight per group — these feed profit, delivery dates and shipping charges.",
    "Stock Qty: 0 means made to order. Put a number if you keep ready pieces.",
    "Send the filled sheet back and the prices go onto the website, ready for the cart and Razorpay.",
], 1):
    ws.cell(r, 2, f"{i}.").font = bold
    ws.cell(r, 2).alignment = Alignment(horizontal="right", vertical="top")
    c = ws.cell(r, 3, t); c.font = base; c.alignment = wrap
    ws.merge_cells(start_row=r, start_column=3, end_row=r, end_column=7)
    ws.row_dimensions[r].height = 30; r += 1
r += 1
ws.cell(r, 2, "Example of a filled group (made-up numbers, for format only)").font = bold; r += 1
ex_h = ["Shows Under", "Selling Price ₹", "MRP ₹", "Making Cost ₹", "Making Time (days)", "Weight (g)"]
for j, h in enumerate(ex_h):
    c = ws.cell(r, 2 + j, h); c.font = head; c.fill = HEAD; c.alignment = center; c.border = box
r += 1
for j, v in enumerate(["Scrunchies", 149, 199, 60, 2, 40]):
    c = ws.cell(r, 2 + j, v); c.font = Font(name=F, size=10, italic=True, color="888888"); c.fill = GREY; c.border = box
    if j in (1, 2, 3): c.number_format = RUPEE
r += 2
ws.cell(r, 2, "Product code format").font = bold; r += 1
ws.cell(r, 2, "MZ-SCR-007").font = Font(name=F, size=11, bold=True, color="7A2E2E")
ws.cell(r, 3, "MZ = Mayuri'z · SCR = the product group · 007 = the 7th scrunchie. Codes never change and are never reused, so orders and payments can always be traced to the right piece. The code is printed on every card on the website.").font = base
ws.cell(r, 3).alignment = wrap
ws.merge_cells(start_row=r, start_column=3, end_row=r, end_column=7); ws.row_dimensions[r].height = 42
r += 2
ws.cell(r, 2, "Keep this file private").font = Font(name=F, size=10, bold=True, color="C00000"); r += 1
c = ws.cell(r, 2, "The website's code is public on GitHub, so this sheet (with your costs and profit) is not stored there. Only the selling prices will go onto the site.")
c.font = base; c.alignment = wrap
ws.merge_cells(start_row=r, start_column=2, end_row=r, end_column=7); ws.row_dimensions[r].height = 28

# ================= Tax & GST =================
tx = wb.create_sheet("Tax & GST")
tx.sheet_view.showGridLines = False
tx.column_dimensions["A"].width = 3; tx.column_dimensions["B"].width = 30; tx.column_dimensions["C"].width = 95
tx["B2"] = "Tax & GST — plain-language notes for Mayuri'z"; tx["B2"].font = title
tx["B3"] = "Written by Claude from Indian GST and income-tax rules as of late 2025. Not advice from a licensed CA: rules and rates change, so check anything marked 'confirm' before relying on it."
tx["B3"].font = sub; tx["B3"].alignment = wrap; tx.merge_cells("B3:C3"); tx.row_dimensions[3].height = 28
r = 5
for h in ("Topic", "What applies to you"):
    c = tx.cell(r, 2 if h == "Topic" else 3, h); c.font = head; c.fill = HEAD; c.border = box
r += 1
notes = [
    ("Do I charge GST?", "No, not while Mayuri'z is unregistered. An unregistered seller must not add GST to prices or show a GSTIN. Your website price is the full price the customer pays (plus shipping). GST % stays 0 on the Price Groups sheet."),
    ("When must I register?", "Selling within your own state: once total sales in a financial year cross ₹40 lakh for goods (₹20 lakh in a few states — confirm for yours)."),
    ("Selling to other states (confirm)", "The GST law normally requires registration for any seller of goods to another state, whatever the sales. There is an exemption for notified handicraft goods made by hand below the ₹40 lakh limit. Whether hand-made crochet accessories count is the one question to settle. Call the free GST helpline 1800-103-4786 and ask: 'I make crochet hair accessories, coasters and keychains by hand and sell them online from my own website to buyers in other states, with yearly sales under ₹40 lakh. Do I need GST registration, or does the handicraft exemption apply?' Note the answer and the date here."),
    ("If registration is needed", "Register on gst.gov.in (free, with PAN, Aadhaar, bank account and address proof). Choose the regular scheme: the composition scheme does not allow selling to other states. Then fill GST % per group, add GST to invoices and file returns (GSTR-1 and GSTR-3B). Most crochet textile articles priced up to ₹2,500 fall in the 5% slab — check each HSN code in the rate finder on cbic-gst.gov.in."),
    ("Income tax", "Shop profit is the maker's income and goes on their own income tax return (ITR-4 Sugam). Under section 44AD you can declare 6% of sales received online (8% of cash sales) as profit instead of keeping full accounts. In the new tax regime, total income up to ₹12 lakh pays no tax for FY 2025-26, but file the return anyway once you have shop sales."),
    ("Records to keep", "Every order (product code, price, shipping, date, buyer's state), Razorpay settlement reports, and receipts for yarn, clips and packing. Razorpay's reports cover most of this; keep them for 6 years."),
    ("Razorpay", "Razorpay accepts unregistered individuals: sign up with PAN, Aadhaar and a bank account in the same name. GSTIN is optional. Razorpay charges about 2% per payment plus 18% GST on that fee; that fee is a cost, not something you charge the buyer."),
    ("Bank account", "Use one account only for the shop (a savings account in the maker's name is fine to start). It keeps sales and expenses easy to show if anyone asks."),
]
for t, v in notes:
    a = tx.cell(r, 2, t); a.font = bold; a.alignment = wrap; a.border = box
    b = tx.cell(r, 3, v); b.font = base; b.alignment = wrap; b.border = box
    tx.row_dimensions[r].height = max(30, 15 * (len(v) // 95 + 1))
    r += 1
r += 1
tx.cell(r, 2, "Helpline answer").font = bold
c = tx.cell(r, 3, ""); c.fill = YELLOW; c.font = inp; c.border = box
tx.cell(r + 1, 2, "Date asked").font = bold
c = tx.cell(r + 1, 3, ""); c.fill = YELLOW; c.font = inp; c.border = box

# ================= Price Groups =================
pg = wb.create_sheet("Price Groups")
cols = [("Group Code", 11), ("Shows Under", 15), ("Website Filter", 16), ("No. of Products", 11),
        ("Selling Price ₹", 13), ("MRP ₹", 11), ("Discount %", 10), ("Making Cost ₹", 13),
        ("Profit per Piece ₹", 13), ("Profit %", 10), ("Making Time (days)", 12),
        ("Weight with Packing (g)", 13), ("HSN Code (for later)", 13), ("GST % (0 = not registered)", 12), ("Notes", 36)]
pg.sheet_view.showGridLines = False
pg["A1"] = "Price Groups — one price for each kind of product"; pg["A1"].font = title
pg["A2"] = "Yellow cells are yours. 'No. of Products' counts the Products sheet. GST is 0% while Mayuri'z is not GST registered — see the Tax & GST sheet."
pg["A2"].font = sub
HR = 4
for j, (h, w) in enumerate(cols, 1):
    c = pg.cell(HR, j, h); c.font = head; c.fill = HEAD; c.alignment = center; c.border = box
    pg.column_dimensions[c.column_letter].width = w
pg.row_dimensions[HR].height = 32
first = HR + 1
for i, (code, shows, web, hsn) in enumerate(GROUPS):
    r = first + i
    vals = {1: code, 2: shows, 3: web,
            4: f"=COUNTIF(Products!$D:$D,A{r})",
            7: f"=IF(AND(E{r}>0,F{r}>E{r}),(F{r}-E{r})/F{r},0)",
            9: f"=IF(E{r}>0,E{r}-H{r},0)",
            10: f"=IF(E{r}>0,(E{r}-H{r})/E{r},0)",
            13: hsn, 14: 0}
    for j in range(1, len(cols) + 1):
        c = pg.cell(r, j, vals.get(j)); c.font = base; c.border = box
        if j in (5, 6, 8, 11, 12, 14, 15):
            c.fill = YELLOW; c.font = inp
        if j in (5, 6, 8, 9): c.number_format = RUPEE
        if j in (7, 10): c.number_format = PCT
        if j == 14: c.number_format = '0%;;"-"'
        if j in (4, 7, 9, 10, 11, 12, 13, 14): c.alignment = Alignment(horizontal="center")
    pg.cell(r, 1).font = bold
last = first + len(GROUPS) - 1
tr = last + 1
pg.cell(tr, 2, "Total").font = bold
pg.cell(tr, 4, f"=SUM(D{first}:D{last})").font = bold
pg.cell(tr, 4).alignment = Alignment(horizontal="center")
for j in range(1, len(cols) + 1): pg.cell(tr, j).border = Border(top=Side(style="medium", color="7A2E2E"))
pg.cell(tr + 2, 1, "Check: products counted here").font = sub
pg.cell(tr + 2, 4, f'=IF(D{tr}=COUNTA(Products!$A:$A)-1-{len(GROUPS)},"OK — all counted","Some products have an unknown group")').font = sub
pg["E4"].comment = Comment("What the customer pays for one piece of this kind. Each product can override it on the Products sheet.", "Claude")
pg["F4"].comment = Comment("Optional 'was' price shown crossed out. Leave empty for no discount.", "Claude")
pg["H4"].comment = Comment("Yarn + clip/pin/hardware + packing for one piece.", "Claude")
pg["L4"].comment = Comment("Weight of one packed piece. Razorpay shipping partners (Shiprocket etc.) charge by weight.", "Claude")
pg["M4"].comment = Comment("Only needed once Mayuri'z is GST registered (it goes on tax invoices). Picked by what the product is made of and used for: 6117 crocheted clothing accessories, 9615 hair clips/pins, 6702 artificial flowers, 6307 other made-up textile articles, 6304 crocheted furnishings, 7117 imitation jewellery, 4202 bags. Check each against the rate finder on cbic-gst.gov.in when you register.", "Claude")
pg.freeze_panes = pg.cell(first, 3)
gst = DataValidation(type="decimal", operator="between", formula1="0", formula2="0.28", allow_blank=True,
                     error="Type GST as a percent, e.g. 0% or 5%.", errorTitle="GST %")
pg.add_data_validation(gst); gst.add(f"N{first}:N{last}")
pos = DataValidation(type="decimal", operator="greaterThanOrEqual", formula1="0", allow_blank=True)
pg.add_data_validation(pos); pos.add(f"E{first}:F{last}"); pos.add(f"H{first}:H{last}"); pos.add(f"K{first}:L{last}")
pg.conditional_formatting.add(f"F{first}:F{last}", FormulaRule(formula=[f"AND(F{first}>0,F{first}<E{first})"], font=Font(color="C00000", bold=True)))
pg.conditional_formatting.add(f"I{first}:I{last}", FormulaRule(formula=[f"AND(E{first}>0,I{first}<0)"], font=Font(color="C00000", bold=True)))
GR = f"'Price Groups'!$A${first}:$A${last}"
def gcol(letter): return f"'Price Groups'!${letter}${first}:${letter}${last}"

# ================= Products =================
pr = wb.create_sheet("Products")
pcols = [("Product Code", 13), ("Product Name", 32), ("Shows Under", 13), ("Group Code", 9),
         ("Website Filter", 14), ("Pieces in Set", 9), ("Group Price ₹", 11), ("Own Price ₹", 11),
         ("Selling Price ₹", 12), ("MRP ₹", 10), ("Stock Qty", 9), ("Made to Order", 10),
         ("Making Time (days)", 10), ("Colours Available", 18), ("Show on Website", 10),
         ("Badge", 10), ("Notes", 34), ("Website ID", 26), ("Photo Link", 44), ("Description", 70)]
for j, (h, w) in enumerate(pcols, 1):
    c = pr.cell(1, j, h); c.font = head; c.fill = HEAD; c.alignment = center; c.border = box
    pr.column_dimensions[c.column_letter].width = w
pr.row_dimensions[1].height = 32
pr.freeze_panes = "C2"
yn = DataValidation(type="list", formula1='"Yes,No"', allow_blank=False); pr.add_data_validation(yn)
nonneg = DataValidation(type="decimal", operator="greaterThanOrEqual", formula1="0", allow_blank=True); pr.add_data_validation(nonneg)
r = 2
gname = {g[0]: g[1] for g in GROUPS}
for code, *_ in GROUPS:
    items = [p for p in products if p["group"] == code]
    if not items: continue
    c = pr.cell(r, 1, f"{gname[code]}  ·  {code}  ·  {len(items)} product{'s' if len(items) > 1 else ''}")
    for j in range(1, len(pcols) + 1):
        pr.cell(r, j).fill = GROUPF; pr.cell(r, j).border = box
    c.font = Font(name=F, size=11, bold=True, color="7A2E2E")
    r += 1
    for p in items:
        note = ""
        if p["id"] in SECOND_PHOTO:
            note = f"Second photo of {by_id[SECOND_PHOTO[p['id']]]['sku']} ({by_id[SECOND_PHOTO[p['id']]]['name']}) — merge before the cart goes live"
        n = set_size(p)
        row = {
            1: p["sku"], 2: p["name"], 3: p["tag"], 4: code,
            5: f"=IFERROR(INDEX({gcol('C')},MATCH(D{r},{GR},0)),\"\")",
            6: n,
            7: f"=IFERROR(INDEX({gcol('E')},MATCH(D{r},{GR},0)),0)",
            8: None,
            9: f"=IF(H{r}>0,H{r},G{r})",
            10: f"=IF(H{r}>0,0,IFERROR(INDEX({gcol('F')},MATCH(D{r},{GR},0)),0))",
            11: 0, 12: "Yes",
            13: f"=IFERROR(INDEX({gcol('K')},MATCH(D{r},{GR},0)),0)",
            14: "Any colour", 15: "Yes", 16: p["badge"], 17: note or None,
            18: p["id"], 19: f"https://mayurisyarntales.online/{p['image']}", 20: p["desc"],
        }
        for j in range(1, len(pcols) + 1):
            c = pr.cell(r, j, row.get(j)); c.font = base; c.border = box
            if j in (6, 8, 11, 12, 14, 15, 17): c.fill = YELLOW; c.font = inp
            if j in (5, 7, 10, 13): c.font = link
            if j in (7, 8, 9, 10): c.number_format = RUPEE
            if j in (6, 11, 12, 13, 15, 16): c.alignment = Alignment(horizontal="center")
            if j == 20: c.alignment = Alignment(wrap_text=False)
        pr.cell(r, 1).font = bold; pr.cell(r, 9).font = bold
        if note: pr.cell(r, 17).font = Font(name=F, size=10, color="C00000")
        pr.row_dimensions[r].outlineLevel = 1
        r += 1
lastp = r - 1
yn.add(f"L2:L{lastp}"); yn.add(f"O2:O{lastp}")
nonneg.add(f"F2:F{lastp}"); nonneg.add(f"H2:H{lastp}"); nonneg.add(f"K2:K{lastp}")
pr.sheet_properties.outlinePr.summaryBelow = False
pr["H1"].comment = Comment("Leave empty to use the group price. Type a price only when this piece should differ, e.g. a set of 3.", "Claude")
pr["F1"].comment = Comment("How many pieces the customer gets for the price. Filled in from names like 'Pair', 'Trio', 'Set of 4' — check them.", "Claude")
pr["J1"].comment = Comment("Comes from the group. Shows '-' when this product has its own price; then no 'was' price is shown.", "Claude")
pr["K1"].comment = Comment("Ready-made pieces in hand. 0 with 'Made to Order = Yes' means it's made after the order.", "Claude")

# ================= Launch Checklist =================
cl = wb.create_sheet("Before Razorpay")
cl.sheet_view.showGridLines = False
cl["A1"] = "Before the cart and Razorpay go live"; cl["A1"].font = title
cl["A2"] = "What a marketplace website needs, and where Mayuri'z stands today."; cl["A2"].font = sub
ch = [("#", 4), ("Step", 30), ("Why it matters", 62), ("Who", 12), ("Status", 14)]
for j, (h, w) in enumerate(ch, 1):
    c = cl.cell(4, j, h); c.font = head; c.fill = HEAD; c.alignment = center; c.border = box
    cl.column_dimensions[c.column_letter].width = w
steps = [
    ("Product codes on every piece", "Every order, payment and refund needs one fixed code per product. Done: on the website and in this sheet; the Telegram bot gives new uploads their code too.", "Claude", "Done"),
    ("Prices", "Fill the Price Groups sheet (and Own Price for sets). Razorpay can't charge without a price.", "You", "To do"),
    ("Merge the 3 second photos", "Three listings are a second photo of another piece (marked red in Products → Notes). In a cart they'd be bought as separate items.", "You decide", "To do"),
    ("Colour choice", "Pieces are 'any colour you like'. Decide: fixed colour as shown, or a colour choice at checkout (adds a variant per colour).", "You decide", "To do"),
    ("Shipping charges & delivery time", "Flat fee, free above an amount, or by weight? Which areas you ship to, and how many days. Fill Weight and Making Time per group.", "You", "To do"),
    ("Policy pages", "Razorpay checks the website for: Contact Us (with address), Terms & Conditions, Privacy Policy, Refund & Cancellation, Shipping & Delivery. Without them the account is not approved.", "Claude writes, you approve", "To do"),
    ("Settle GST registration", "Selling to other states can need GST registration even below ₹40 lakh, unless crochet pieces count as exempt handicrafts. Ask the free GST helpline 1800-103-4786 the exact question on the Tax & GST sheet, then mark this done.", "You", "To do"),
    ("Razorpay account & KYC", "Sign up as an individual / unregistered business: PAN, bank account in the same name, Aadhaar, and the website. No GSTIN is needed for this. See the Tax & GST sheet for the one GST question to settle first.", "You", "To do"),
    ("Payment backend", "The website is static (GitHub Pages). Razorpay needs a small server to create each order and verify the payment with the secret key — the existing Cloudflare Worker can do it. The secret key must never go into the website.", "Claude", "To do"),
    ("Cart & checkout", "Add to cart, quantity, address form, order summary, Razorpay checkout, thank-you page.", "Claude", "To do"),
    ("Order records & emails", "Each paid order saved (Google Sheet or database) and a confirmation email to the customer and to you. EmailJS is already set up for enquiries.", "Claude", "To do"),
    ("Test payments", "Run full orders in Razorpay test mode before switching to live keys.", "Both", "To do"),
]
for i, (s1, s2, who, st) in enumerate(steps, 1):
    r = 4 + i
    for j, v in enumerate([i, s1, s2, who, st], 1):
        c = cl.cell(r, j, v); c.font = base; c.border = box; c.alignment = wrap
    cl.cell(r, 2).font = bold
    cl.cell(r, 5).font = inp; cl.cell(r, 5).fill = YELLOW; cl.cell(r, 5).alignment = center
    cl.row_dimensions[r].height = 44
stv = DataValidation(type="list", formula1='"To do,In progress,Done"'); cl.add_data_validation(stv); stv.add(f"E5:E{4+len(steps)}")
cl.conditional_formatting.add(f"E5:E{4+len(steps)}", FormulaRule(formula=['E5="Done"'], fill=PatternFill("solid", fgColor="D9EAD3"), font=Font(color="006100", bold=True)))

for sh in wb.worksheets:
    sh.sheet_view.zoomScale = 100
wb.active = 0
wb.save(OUT)
print(len(products), "products,", lastp, "rows")
