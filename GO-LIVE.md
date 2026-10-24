# GO-LIVE Guide — Busy Bees

The app is simulation-only until you connect the three pieces below. Nothing here
requires code changes — the app reads its targets from **Dispatcher Portal →
Automation Settings** (stored in the browser).

## How it flows when live

1. Customer submits the form → app POSTs a `lead.created` JSON payload to your webhook.
2. **Dispatch via Text** → app POSTs `lead.dispatch_sms` → automation texts the contractor (Twilio).
3. **Clear via Stripe** → app POSTs `lead_fee.charge_requested` → automation creates a
   Stripe payment link/invoice and texts it to the contractor. Stripe hosts the secure
   checkout; card data never touches the app.

## Already set up — Stripe sandbox (test mode, 2026-10-23)

Created in the connected Stripe sandbox account ("Cape connect sandbox", test mode —
**no real money moves**; pay with test card `4242 4242 4242 4242`):

- Product: **Busy Bees Lead Fee** — `prod_VUZTsBv33sZjbD`
- Prices: $25 `price_1UTaKmR2bpKCKmn6ifN9du9L` · $30 `price_1UTaKrR2bpKCKmn6sbjNLRJh` · $35 `price_1UTaKvR2bpKCKmn664r3LG60`
- Payment links (text one of these to a contractor to collect that fee):
  - $25 — https://buy.stripe.com/test_cNi14p1IqbFo2zY5N7eUU00
  - $30 — https://buy.stripe.com/test_9B67sNcn4dNw7UigrLeUU01
  - $35 — https://buy.stripe.com/test_eVq5kFevc8tccaygrLeUU02

## LIVE — Stripe live account (activated 2026-10-23)

Live account `acct_1UTaBvBxk2BeDiA8`, payments ACTIVE. Rebrand status
(2026-10-23): product below renamed to "Busy Bees Lead Fee" by Muse via the
Stripe connector (now connected to this LIVE account). Still Bobby's in the
dashboard (Stripe exposes no API for an account's own name): business public
name is still "Cape Cod Coastal Dispatch" (Settings → Public details → Name
→ Busy Bees) and the card statement descriptor is still "CAPE DISPATCH"
(Settings → Payments → Statement descriptor → BUSY BEES). Sandbox data was
NOT copied over ("Don't copy anything") — the live catalog was built fresh:

- Product: **Busy Bees Lead Fee** — `prod_VUa66fiWZJl5XJ`
- Prices: $25 `price_1UTavzBxk2BeDiA8ZngXaCnI` (Haul / Power Washing / Fall Cleanup) ·
  $30 `price_1UTavzBxk2BeDiA8AhIO6Ba2` (Storm Debris) ·
  $35 `price_1UTavzBxk2BeDiA8usnyuo6x` (Tree & Stump)
- **LIVE payment links** (text one to a contractor to collect that fee — real money):
  - $25 — https://buy.stripe.com/4gM3cueB3cgKgQD82M9AA00
  - $30 — https://buy.stripe.com/28E7sK50t6Wq1VJ2Is9AA01
  - $35 — https://buy.stripe.com/dRm14mcsVfsW9obbeY9AA02
  Links: quantity fixed at 1, phone number collected, confirmation message set.

**Still open on the live account (Bobby only):**
- Identity review in progress; task "Provide an ID number for an account representative"
  must be completed by **Nov 22, 2026** (or $600 volume) or payouts pause.
- Bank routing + account numbers must be added in payout settings before payouts can land.

## Step 1 — Stripe (payments)

- Create/activate a Stripe account (dashboard.stripe.com). Stripe will ask for business
  details, an ID, and a bank account for payouts — payouts are documented income for the
  account holder, so use the name/account you want this business's money under.
- Card fees are Stripe's standard 2.9% + $0.30 per charge (on a $25 lead fee you net ~$23.97).
- Start in **Test mode** and run the checklist below before switching to live keys.
- Your secret key goes ONLY into Make/Zapier's Stripe connection — never into `index.html`.

## Step 2 — Make (recommended) or Zapier (alternative)

**Make scenario (one scenario handles all three events):**
1. Trigger: **Webhooks → Custom webhook**. Copy its URL into the app's Automation Settings
   (Webhook URL; the Billing Webhook field can stay blank to reuse it).
2. Router by `event`:
   - `lead.created` → Twilio **Send an SMS** to the contractor number: service, town,
     customer name/phone, notes. Optionally a second Twilio SMS to the customer:
     "Request received — a local contractor will text you shortly."
   - `lead.dispatch_sms` → Twilio **Send an SMS** with the payload's `message` field.
   - `lead_fee.charge_requested` → Stripe **Create a Payment Link** (or invoice) for
     `amount_usd` → Twilio **Send an SMS** to the contractor with the payment link.
3. Turn the scenario ON.

**Zapier alternative:** Catch Hook trigger → filter by `event` → Twilio + Stripe actions
the same way. (Zapier's Twilio/Stripe steps need a paid Zapier plan for multi-step Zaps.)

## Step 3 — Twilio (texting)

- Create a Twilio account, buy a local (508) number.
- **US rule that trips everyone up:** before carriers will deliver business texts from a
  10-digit number, you must complete **A2P 10DLC registration** (brand + campaign) inside
  Twilio. Budget ~30 minutes and a few dollars; unregistered numbers get filtered/blocked.
- Connect Twilio inside Make/Zapier with your Account SID + Auth Token (keep them there only).

## Test checklist (do this in Stripe Test mode first)

- [ ] Submit a test lead from the Customer portal — check it lands in the Dispatcher queue.
- [ ] Webhook log (Make/Zapier run history) shows the `lead.created` payload.
- [ ] Dispatch via Text → contractor phone receives the SMS.
- [ ] Mark Accepted → Clear via Stripe → payment link arrives; pay with Stripe's test card
      `4242 4242 4242 4242`, any future date/CVC.
- [ ] Confirm the test payment shows in the Stripe dashboard, then switch Stripe + the
      automation to live keys and repeat with a real $25 run.

## Security rules (already built into the design)

- No Stripe secret keys, Twilio tokens, or passwords in `index.html` — ever.
- Card entry happens only on Stripe-hosted pages (PCI-compliant).
- Customer phone numbers go only to the matched contractor — stated on the form itself.
