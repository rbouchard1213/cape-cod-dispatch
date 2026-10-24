# Busy Bees

A mobile-first, single-file web app (`index.html` — HTML + Tailwind CDN + vanilla JS, no build step) for text-only lead generation and dispatch across Cape Cod, MA.

**Live app:** GitHub Pages — `https://rbouchard1213.github.io/cape-cod-dispatch/`

## What it does

**Customer portal**
- Coastal Cape Cod design (sandy linen `#FDFBF7`, nautical navy `#0A2540`, seafoam teal `#0D9488`, dune gold `#D97706`)
- Interactive service grid with lead values: Tree & Stump Removal **$35** · Emergency Storm Debris **$30** · Heavy Equipment Haul **$25** · Power Washing & Salt Prep **$25**
- Clickable town grid: Yarmouth, Hyannis/Barnstable, Dennis, Sandwich, Chatham, Harwich, Mashpee, Brewster
- Intake form (name, text-enabled phone, urgency, job notes) with validation; generates a JSON lead payload and fires a webhook
- Trust layer: SSL-encrypted form, payments secured by Stripe (PCI-compliant, card data never stored on the site), submitting a request is always free

**Dispatcher portal** (top-nav toggle)
- Live metrics: total leads, total value, pending routing, billed leads
- Lead queue with status flow `New → Dispatched → Accepted → Invoiced`
- **Dispatch via Text (Webhook)** and **Clear via Stripe** actions, payload log, CSV export
- Leads persist in the browser via `localStorage`

## Going live

Everything runs as an on-device simulation until a webhook URL is saved in the Dispatcher portal's **Automation Settings**. See **GO-LIVE.md** for the full Make/Zapier + Twilio + Stripe wiring. Stripe secret keys never go in this app — charges are created server-side by the automation.
