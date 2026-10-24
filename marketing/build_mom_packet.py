#!/usr/bin/env python3
"""Build the 'for Mom' explainer packet for the Busy Bees board + Bob of All Trades.
Plain language, money breakdown, all live links, flyer on the last page.
Output: mom-explainer-packet.pdf (same folder).
"""
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                TableStyle, Image, PageBreak, HRFlowable)
import os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "mom-explainer-packet.pdf")
FLYER = os.path.join(HERE, "coastal-dispatch-flyer.png")

NAVY = colors.HexColor("#0A2540")
TEAL = colors.HexColor("#0D9488")
GOLD = colors.HexColor("#D97706")
LIGHT = colors.HexColor("#F3EFE6")
GREY = colors.HexColor("#444444")

styles = {
    "title": ParagraphStyle("title", fontName="Helvetica-Bold", fontSize=24,
                            leading=29, textColor=NAVY, alignment=TA_CENTER),
    "subtitle": ParagraphStyle("subtitle", fontName="Helvetica", fontSize=12.5,
                               leading=17, textColor=GREY, alignment=TA_CENTER),
    "h1": ParagraphStyle("h1", fontName="Helvetica-Bold", fontSize=15.5,
                         leading=19, textColor=NAVY, spaceBefore=16, spaceAfter=6),
    "body": ParagraphStyle("body", fontName="Helvetica", fontSize=11.5,
                           leading=16.5, textColor=colors.black, spaceAfter=7),
    "step": ParagraphStyle("step", fontName="Helvetica", fontSize=11.5,
                           leading=16.5, textColor=colors.black, spaceAfter=5,
                           leftIndent=6),
    "link": ParagraphStyle("link", fontName="Helvetica", fontSize=11,
                           leading=15.5, textColor=colors.black, spaceAfter=6),
    "small": ParagraphStyle("small", fontName="Helvetica-Oblique", fontSize=10,
                            leading=14, textColor=GREY, spaceAfter=6),
    "cell": ParagraphStyle("cell", fontName="Helvetica", fontSize=11,
                           leading=14, textColor=colors.black),
    "cellb": ParagraphStyle("cellb", fontName="Helvetica-Bold", fontSize=11,
                            leading=14, textColor=colors.white),
}

def P(text, style="body"):
    return Paragraph(text, styles[style])

story = []

# ---------- Page 1 ----------
story.append(Spacer(1, 0.25 * inch))
story.append(P("What Bobby Is Building", "title"))
story.append(Spacer(1, 0.08 * inch))
story.append(P("Busy Bees &mdash; and Bob of All Trades, his own business", "subtitle"))
story.append(P("A plain-English guide, made for Mom.", "subtitle"))
story.append(Spacer(1, 0.15 * inch))
story.append(HRFlowable(width="100%", thickness=2, color=GOLD))
story.append(Spacer(1, 0.1 * inch))

story.append(P("The short version", "h1"))
story.append(P(
    "Bobby built a website that connects Cape Cod homeowners who need work done "
    "with local contractors who do that kind of work. Homeowners ask for help "
    "<b>for free</b>. The contractor who takes the job pays Bobby a small flat fee "
    "for sending them the customer. Bobby also has his own property-services "
    "business, <b>Bob of All Trades</b>, which takes jobs itself &mdash; so the website "
    "feeds his own business too."))

story.append(P("How it works", "h1"))
steps = [
    "<b>1.</b> A homeowner goes to the website and requests help &mdash; tree &amp; stump "
    "removal, storm debris cleanup, heavy hauling, power washing, or a fall cleanup. "
    "It is always free for them, and no credit card is ever asked for.",
    "<b>2.</b> The request is matched to a local contractor who covers that town and "
    "that kind of work.",
    "<b>3.</b> The contractor pays Bobby the flat fee for the job lead ($25&ndash;$35, "
    "depending on the kind of job) through Stripe &mdash; the same secure payment "
    "company big stores use. No subscription, no monthly bill &mdash; they only pay "
    "when they take a job.",
    "<b>4.</b> The contractor calls the customer, does the work, and keeps <b>100% of "
    "what the job pays</b>. Bobby never touches the job money &mdash; the homeowner "
    "pays the contractor directly, just like always.",
    "<b>5.</b> When a job fits Bobby&rsquo;s own business, Bob of All Trades takes it. "
    "Those carry <b>no fee at all</b> &mdash; and Bobby earns his normal rate doing "
    "the work himself.",
]
for s in steps:
    story.append(P(s, "step"))

story.append(P("The money &mdash; how Bobby gets paid", "h1"))
story.append(P(
    "Here is exactly what happens on every job another contractor takes. Stripe "
    "keeps a small standard cut (2.9% + 30&cent;) for processing the card, and the "
    "rest is Bobby&rsquo;s:"))

money = Table([
    [P("Kind of job", "cellb"), P("Contractor pays", "cellb"),
     P("Stripe keeps", "cellb"), P("Bobby keeps", "cellb")],
    [P("Tree &amp; Stump Removal"), P("$35.00"), P("$1.31"), P("$33.69")],
    [P("Storm Debris Cleanup"), P("$30.00"), P("$1.17"), P("$28.83")],
    [P("Heavy Hauling"), P("$25.00"), P("$1.03"), P("$23.97")],
    [P("Power Washing"), P("$25.00"), P("$1.03"), P("$23.97")],
    [P("Fall Cleanups"), P("$25.00"), P("$1.03"), P("$23.97")],
], colWidths=[2.3 * inch, 1.5 * inch, 1.3 * inch, 1.4 * inch])
money.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), NAVY),
    ("BACKGROUND", (0, 1), (-1, -1), LIGHT),
    ("BOX", (0, 0), (-1, -1), 1, NAVY),
    ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CCCCCC")),
    ("TOPPADDING", (0, 0), (-1, -1), 6),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ("LEFTPADDING", (0, 0), (-1, -1), 9),
]))
story.append(money)
story.append(Spacer(1, 0.1 * inch))
story.append(P(
    "<b>An example week:</b> if local contractors take 10 job requests in a week, "
    "that is roughly <b>$240 to $335 to Bobby</b> &mdash; on top of whatever he earns "
    "doing jobs himself with Bob of All Trades. Some weeks will be slower and some "
    "busier. It grows as more customers find the site and more contractors sign up."))
story.append(P(
    "The fee money lands in Bobby&rsquo;s Stripe account and then pays out to his "
    "bank, the same way any business gets paid by card."))

# ---------- Page 2 ----------
story.append(PageBreak())
story.append(P("Bob of All Trades &mdash; Bobby&rsquo;s own business", "h1"))
story.append(P(
    "Bob of All Trades is Bobby&rsquo;s property-services business for Yarmouth and "
    "the Cape: lawn care, fall cleanups, snow removal, pressure washing, junk "
    "removal, cleaning and carpet cleaning, painting, camera installs, small-engine "
    "repair, handyman work, and winter watch for second homes."))
story.append(P(
    "<b>Rates:</b> $75 an hour, $100 minimum per job, and <b>quotes are always "
    "free</b>. Customers can call or text him any time at <b>(413) 234-6351</b>."))
story.append(P(
    "On the Busy Bees website, Bob of All Trades is contractor #1 &mdash; it "
    "takes the smaller jobs itself, and the bigger jobs go to the other local "
    "companies on the roster."))

story.append(P("Everything in one place &mdash; the links", "h1"))
links = [
    ("<b>The customer website</b> (where homeowners request help):",
     "https://busybeesdispatch.com/"),
    ("<b>Mission Control</b> (Bobby&rsquo;s own dashboard for the business):",
     "https://busybeesdispatch.com/status.html"),
    ("<b>Contractor payment page &mdash; $25 jobs</b> (hauling, power washing, fall cleanups):",
     "https://buy.stripe.com/4gM3cueB3cgKgQD82M9AA00"),
    ("<b>Contractor payment page &mdash; $30 jobs</b> (storm debris):",
     "https://buy.stripe.com/28E7sK50t6Wq1VJ2Is9AA01"),
    ("<b>Contractor payment page &mdash; $35 jobs</b> (tree &amp; stump):",
     "https://buy.stripe.com/dRm14mcsVfsW9obbeY9AA02"),
]
for label, url in links:
    story.append(P(f'{label}<br/><link href="{url}" color="#0D9488">{url}</link>', "link"))
story.append(P(
    "<b>Towns covered:</b> Yarmouth, Hyannis / Barnstable, Dennis, Sandwich, "
    "Chatham, Harwich, Mashpee, and Brewster."))

story.append(P("Where it stands right now", "h1"))
story.append(P(
    "&bull; The website is <b>live</b> and taking requests today.<br/>"
    "&bull; Payments are <b>turned on</b> through Stripe.<br/>"
    "&bull; Bob of All Trades is signed up as the first contractor.<br/>"
    "&bull; <b>Next:</b> signing up more local contractors (the goal is 6&ndash;10), "
    "finishing the automatic text alerts, and one piece of Stripe paperwork &mdash; "
    "Bobby&rsquo;s ID and bank information, due by November 22 &mdash; so the money "
    "can pay out to his bank."))
story.append(Spacer(1, 0.15 * inch))
story.append(HRFlowable(width="100%", thickness=2, color=GOLD))
story.append(Spacer(1, 0.08 * inch))
story.append(P("Built by Bobby &mdash; October 2026. One call. Consider it done.", "subtitle"))

# ---------- Flyer page ----------
if os.path.exists(FLYER):
    story.append(PageBreak())
    story.append(P("The flyer Bobby had made for it:", "subtitle"))
    story.append(Spacer(1, 0.15 * inch))
    story.append(Image(FLYER, width=6.3 * inch, height=6.3 * inch))

doc = SimpleDocTemplate(OUT, pagesize=letter,
                        leftMargin=0.85 * inch, rightMargin=0.85 * inch,
                        topMargin=0.7 * inch, bottomMargin=0.7 * inch,
                        title="What Bobby Is Building - Busy Bees",
                        author="Bobby Bouchard")
doc.build(story)
print("Wrote", OUT, os.path.getsize(OUT), "bytes")
