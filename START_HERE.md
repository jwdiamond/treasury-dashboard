# START HERE — Treasury & Credit Market Dashboard

This folder is the public dashboard. It is separate from the Baker Institute landing page.

## What is in the folder

- `index.html` — the webpage
- `styles.css` — how the page looks
- `dashboard.js` — charts and formatting
- `data/dashboard_data.js` — the numbers shown on the webpage
- `export_dashboard_data.py` — converts your Treasury program's CSV outputs into website data

## First goal: open the dashboard on your computer

1. Copy this entire folder into:

   `C:\Users\jdiamond\Box\Center for Tax and Budget Policy\Code\Treasurydebt\dashboard`

2. Double-click `index.html`.

It should open in Chrome/Edge immediately. The included data are seeded from the latest run you showed ChatGPT so you can see the design before doing anything else.

## Then connect it to your live data

Recommended folder structure:

    Treasurydebt\
        treasury_market_credit_v3.py
        treasury_output\
        dashboard\
            index.html
            styles.css
            dashboard.js
            export_dashboard_data.py
            data\
                dashboard_data.js

Important: run your Treasury script from the `Treasurydebt` directory so `treasury_output` is created there.

PowerShell:

    cd "C:\Users\jdiamond\Box\Center for Tax and Budget Policy\Code\Treasurydebt"
    python treasury_market_credit_v3.py

Then:

    cd dashboard
    python export_dashboard_data.py

Then refresh `index.html` in your browser.

## If your current `treasury_output` folder is under `...\Code\treasury_output`

Either move that folder into `Treasurydebt`, or edit this line in `export_dashboard_data.py`:

    OUTPUT_DIR = HERE.parent / "treasury_output"

and point it to the correct folder.

## What Version 1 shows

1. 10-year Treasury yield
2. 10-year real Treasury yield
3. Investment-grade OAS
4. BBB OAS
5. High-yield OAS
6. Five-day rates/credit regime
7. Historical corporate credit spread chart
8. Double-tightening chart
9. Total marketable debt
10. Weighted-average maturity
11. Estimated modified duration
12. Maturity buckets
13. Security composition
14. Debt maturing by year
15. Estimated annual interest-cost reset
16. Refinancing detail table

## What is intentionally NOT in Version 1

- AI bond basket / TRACE
- News feeds
- Forecasts
- Anything requiring a paid data license

## Next step after local review

Once you like the layout, put the `dashboard` folder in a GitHub repository and enable GitHub Pages. That produces a public URL Baker can link to.

Do not worry about GitHub yet. First get the local page looking exactly the way you want.
