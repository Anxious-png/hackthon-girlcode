from django.db import migrations

ARTICLES = [
    {
        "title": "Start Your Savings Journey Today",
        "category": "Savings",
        "icon": "fa-piggy-bank",
        "summary": "Every shilling you save brings you closer to your dreams. Start small — even 1,000 UGX daily grows to 365,000 UGX yearly. The best time to start saving is now.",
        "content": """<h5>Why Start Saving Now?</h5>
<p>Many people delay saving because they feel they don't earn enough. But the truth is, saving is a habit — not a function of income. The earlier you start, the more time your money has to grow.</p>

<h5>The Power of Small Amounts</h5>
<p>Consider this: saving just <strong>UGX 1,000 per day</strong> adds up to <strong>UGX 365,000 per year</strong>. That's enough for school fees, a small emergency fund, or a business startup.</p>

<h5>Practical Steps to Start</h5>
<ul>
  <li>Open a dedicated savings account — keep it separate from your spending account</li>
  <li>Set up an automatic transfer on payday so you save before you spend</li>
  <li>Start with any amount — even UGX 500 a day builds the habit</li>
  <li>Track your savings weekly to stay motivated</li>
  <li>Celebrate small milestones — reaching 10,000, 50,000, 100,000 UGX</li>
</ul>

<h5>Common Excuses — And Why They're Wrong</h5>
<p><strong>"I'll start when I earn more."</strong> — People who earn more often spend more. The habit must come first.</p>
<p><strong>"I have bills to pay."</strong> — Pay yourself first. Even 5% of your income saved consistently beats saving nothing.</p>

<h5>Key Takeaway</h5>
<p>The best savings account is the one you actually use. Start today, start small, and stay consistent.</p>""",
    },
    {
        "title": "Set Clear Savings Goals",
        "category": "Savings",
        "icon": "fa-bullseye",
        "summary": "Define what you're saving for: school fees, emergency fund, business capital, or a new home. Write down your goal amount and deadline to stay motivated.",
        "content": """<h5>Why Goals Matter</h5>
<p>Saving without a goal is like travelling without a destination. You might move, but you won't know when you've arrived. Clear goals give your savings purpose and keep you disciplined.</p>

<h5>The SMART Goal Framework</h5>
<ul>
  <li><strong>Specific</strong> — "Save for school fees" not just "save money"</li>
  <li><strong>Measurable</strong> — "UGX 500,000" not "a lot"</li>
  <li><strong>Achievable</strong> — Realistic given your income</li>
  <li><strong>Relevant</strong> — Tied to something that matters to you</li>
  <li><strong>Time-bound</strong> — "By December 2026"</li>
</ul>

<h5>Types of Savings Goals</h5>
<p><strong>Short-term (0–6 months):</strong> Emergency fund, phone, school supplies</p>
<p><strong>Medium-term (6 months–2 years):</strong> School fees, business capital, travel</p>
<p><strong>Long-term (2+ years):</strong> Land, house, retirement</p>

<h5>How to Use SilentGuard for Goals</h5>
<p>Use the <strong>Savings Goal Tracker</strong> to set your target amount and track your progress. The app shows you a progress bar and gives you smart feedback as you save.</p>

<h5>Key Takeaway</h5>
<p>Write your goal down. People who write their goals are 42% more likely to achieve them.</p>""",
    },
    {
        "title": "The 50-30-20 Savings Rule",
        "category": "Financial Planning",
        "icon": "fa-chart-pie",
        "summary": "Allocate your income wisely: 50% for needs, 30% for wants, and 20% for savings. Adjust as needed — but always save something.",
        "content": """<h5>What Is the 50-30-20 Rule?</h5>
<p>The 50-30-20 rule is a simple budgeting framework that helps you manage your money without complicated spreadsheets.</p>

<h5>How It Works</h5>
<ul>
  <li><strong>50% — Needs:</strong> Rent, food, transport, utilities, school fees</li>
  <li><strong>30% — Wants:</strong> Entertainment, eating out, new clothes, subscriptions</li>
  <li><strong>20% — Savings & Debt:</strong> Emergency fund, savings goals, loan repayments</li>
</ul>

<h5>Example: UGX 500,000 Monthly Income</h5>
<table style="width:100%;border-collapse:collapse;margin:15px 0;">
  <tr style="background:#f8f9fa;"><th style="padding:8px;text-align:left;border:1px solid #ddd;">Category</th><th style="padding:8px;text-align:right;border:1px solid #ddd;">Amount</th></tr>
  <tr><td style="padding:8px;border:1px solid #ddd;">Needs (50%)</td><td style="padding:8px;text-align:right;border:1px solid #ddd;">UGX 250,000</td></tr>
  <tr><td style="padding:8px;border:1px solid #ddd;">Wants (30%)</td><td style="padding:8px;text-align:right;border:1px solid #ddd;">UGX 150,000</td></tr>
  <tr style="background:#d4edda;"><td style="padding:8px;border:1px solid #ddd;font-weight:700;">Savings (20%)</td><td style="padding:8px;text-align:right;border:1px solid #ddd;font-weight:700;">UGX 100,000</td></tr>
</table>

<h5>Adjusting for Your Situation</h5>
<p>If your needs exceed 50%, reduce wants first — not savings. Savings should be the last thing you cut.</p>

<h5>Key Takeaway</h5>
<p>You don't need a perfect budget. You need a consistent one. The 50-30-20 rule is simple enough to stick to.</p>""",
    },
    {
        "title": "Build an Emergency Fund First",
        "category": "Financial Planning",
        "icon": "fa-first-aid",
        "summary": "Save at least 3–6 months of expenses for emergencies. Keep it separate from daily spending to protect your long-term goals.",
        "content": """<h5>What Is an Emergency Fund?</h5>
<p>An emergency fund is money set aside specifically for unexpected events — job loss, medical bills, urgent repairs, or family emergencies. It is not for planned expenses.</p>

<h5>How Much Should You Save?</h5>
<p>Financial experts recommend <strong>3 to 6 months of living expenses</strong>. If your monthly expenses are UGX 300,000, your emergency fund target is UGX 900,000 – 1,800,000.</p>

<h5>Why Keep It Separate?</h5>
<p>If your emergency fund is in the same account as your daily spending, you will spend it. Keep it in a separate account — ideally one that's slightly harder to access so you're not tempted.</p>

<h5>Building It Step by Step</h5>
<ol>
  <li>Start with a mini-goal: UGX 100,000 (one month of basic expenses)</li>
  <li>Save a fixed amount every month until you reach 3 months</li>
  <li>Only use it for genuine emergencies</li>
  <li>Replenish it immediately after using it</li>
</ol>

<h5>What Counts as an Emergency?</h5>
<p>✅ Medical bills, job loss, urgent home repair, family crisis</p>
<p>❌ Sales, holidays, new phone, entertainment</p>

<h5>Key Takeaway</h5>
<p>An emergency fund is not a luxury — it's the foundation of financial security. Build it before anything else.</p>""",
    },
    {
        "title": "Beware of Get-Rich-Quick Schemes",
        "category": "Fraud Prevention",
        "icon": "fa-exclamation-triangle",
        "summary": "Avoid anyone promising unrealistic profits or asking for upfront payments. True investments take time and transparency.",
        "content": """<h5>What Are Get-Rich-Quick Schemes?</h5>
<p>These are fraudulent investment opportunities that promise unusually high returns in a very short time, often with little or no risk. They are designed to steal your money.</p>

<h5>Common Types in Uganda</h5>
<ul>
  <li><strong>Pyramid schemes:</strong> You earn by recruiting others, not from real business</li>
  <li><strong>Fake forex trading:</strong> "Invest UGX 100,000, get UGX 500,000 in a week"</li>
  <li><strong>Fake crypto platforms:</strong> Unregulated apps promising daily returns</li>
  <li><strong>Ponzi schemes:</strong> Early investors are paid using money from new investors</li>
  <li><strong>Fake SACCOs:</strong> Unregistered groups collecting savings and disappearing</li>
</ul>

<h5>Warning Signs</h5>
<ul>
  <li>Promises of returns above 20% per month</li>
  <li>Pressure to recruit friends and family</li>
  <li>No clear explanation of how money is made</li>
  <li>Requests for upfront fees to "unlock" your earnings</li>
  <li>No registration with Bank of Uganda or UMRA</li>
</ul>

<h5>What To Do If You Suspect a Scam</h5>
<p>Do not invest. Report it to the <strong>Bank of Uganda</strong> or use SilentGuard's fraud reporting feature to warn others.</p>

<h5>Key Takeaway</h5>
<p>If it sounds too good to be true, it is. Real wealth is built slowly, consistently, and transparently.</p>""",
    },
    {
        "title": "Protect Your Savings from Fraud",
        "category": "Fraud Prevention",
        "icon": "fa-shield-alt",
        "summary": "Never share your mobile money PIN or banking details. Fraudsters may impersonate officials — always verify before sending money.",
        "content": """<h5>How Fraudsters Target Your Savings</h5>
<p>Scammers use many tactics to steal money from mobile money users and bank account holders in Uganda. Understanding their methods is your first line of defence.</p>

<h5>Common Fraud Tactics</h5>
<ul>
  <li><strong>SIM swap fraud:</strong> Scammer convinces your telecom to transfer your number to their SIM</li>
  <li><strong>Phishing SMS:</strong> Fake messages pretending to be from MTN, Airtel, or your bank</li>
  <li><strong>Impersonation:</strong> Caller pretends to be a bank official asking for your PIN</li>
  <li><strong>Fake prizes:</strong> "You've won! Send UGX 5,000 to claim your prize"</li>
  <li><strong>Overpayment scam:</strong> Someone "accidentally" sends you money and asks for it back</li>
</ul>

<h5>Golden Rules</h5>
<ul>
  <li>🔒 <strong>Never share your PIN</strong> — not with family, not with "bank officials"</li>
  <li>📵 <strong>Hang up on suspicious callers</strong> — call back on the official number</li>
  <li>🔍 <strong>Verify before sending</strong> — use SilentGuard's transaction check feature</li>
  <li>📱 <strong>Scan suspicious messages</strong> — use SilentGuard's SMS scanner</li>
  <li>🚨 <strong>Report fraud immediately</strong> — use SilentGuard's report feature</li>
</ul>

<h5>Key Takeaway</h5>
<p>Your PIN is yours alone. No legitimate organisation will ever ask for it.</p>""",
    },
    {
        "title": "Avoid Impulsive Spending",
        "category": "Financial Planning",
        "icon": "fa-shopping-cart",
        "summary": "Before buying, wait 24 hours and ask: 'Do I really need this?' Pausing helps control spending and boosts your savings.",
        "content": """<h5>What Is Impulsive Spending?</h5>
<p>Impulsive spending is buying something without planning to — driven by emotion, advertising, or peer pressure rather than genuine need.</p>

<h5>Why It Hurts Your Savings</h5>
<p>Small impulsive purchases add up fast. Buying an unplanned UGX 5,000 item every day costs you <strong>UGX 1,825,000 per year</strong> — money that could have been saved or invested.</p>

<h5>The 24-Hour Rule</h5>
<p>Before any unplanned purchase, wait 24 hours. Ask yourself:</p>
<ul>
  <li>Do I need this or just want it?</li>
  <li>Can I afford it without touching my savings?</li>
  <li>Will I still want it tomorrow?</li>
</ul>
<p>Most impulse urges disappear within 24 hours.</p>

<h5>Practical Tips</h5>
<ul>
  <li>Shop with a list — and stick to it</li>
  <li>Unsubscribe from promotional emails and SMS</li>
  <li>Avoid shopping when hungry, bored, or emotional</li>
  <li>Use cash instead of mobile money for daily spending — it feels more real</li>
  <li>Track every purchase for one week — you'll be surprised</li>
</ul>

<h5>Key Takeaway</h5>
<p>Every shilling you don't spend impulsively is a shilling you can save. Small discipline creates big results.</p>""",
    },
    {
        "title": "Diversify Your Savings",
        "category": "Savings",
        "icon": "fa-layer-group",
        "summary": "Keep your savings in multiple safe places — mobile wallets, banks, and SACCOs — to balance access, growth, and safety.",
        "content": """<h5>What Does Diversification Mean?</h5>
<p>Diversification means spreading your savings across different types of accounts or instruments so that if one fails, you don't lose everything.</p>

<h5>Where Ugandans Can Save</h5>
<table style="width:100%;border-collapse:collapse;margin:15px 0;">
  <tr style="background:#8B0000;color:white;"><th style="padding:8px;text-align:left;">Option</th><th style="padding:8px;text-align:left;">Best For</th><th style="padding:8px;text-align:left;">Risk</th></tr>
  <tr><td style="padding:8px;border:1px solid #ddd;">Mobile Money (MTN/Airtel)</td><td style="padding:8px;border:1px solid #ddd;">Daily access</td><td style="padding:8px;border:1px solid #ddd;">Low</td></tr>
  <tr><td style="padding:8px;border:1px solid #ddd;">Bank Savings Account</td><td style="padding:8px;border:1px solid #ddd;">Medium-term goals</td><td style="padding:8px;border:1px solid #ddd;">Very Low</td></tr>
  <tr><td style="padding:8px;border:1px solid #ddd;">SACCO</td><td style="padding:8px;border:1px solid #ddd;">Group savings + loans</td><td style="padding:8px;border:1px solid #ddd;">Low-Medium</td></tr>
  <tr><td style="padding:8px;border:1px solid #ddd;">Fixed Deposit</td><td style="padding:8px;border:1px solid #ddd;">Long-term growth</td><td style="padding:8px;border:1px solid #ddd;">Very Low</td></tr>
  <tr><td style="padding:8px;border:1px solid #ddd;">Unit Trusts</td><td style="padding:8px;border:1px solid #ddd;">Investment growth</td><td style="padding:8px;border:1px solid #ddd;">Medium</td></tr>
</table>

<h5>A Simple Diversification Strategy</h5>
<ul>
  <li>Keep 1 month of expenses in mobile money for emergencies</li>
  <li>Keep 3–6 months in a bank savings account</li>
  <li>Invest any surplus in a SACCO or fixed deposit</li>
</ul>

<h5>Key Takeaway</h5>
<p>Don't put all your eggs in one basket. Spread your savings to protect yourself and grow your wealth.</p>""",
    },
    {
        "title": "Recognize Pyramid Schemes",
        "category": "Fraud Prevention",
        "icon": "fa-user-slash",
        "summary": "If you must recruit others to earn, it's a scam. Always verify any savings or investment group with authorities.",
        "content": """<h5>What Is a Pyramid Scheme?</h5>
<p>A pyramid scheme is a fraudulent business model where participants earn money primarily by recruiting new members, not by selling real products or services. It always collapses — and most participants lose their money.</p>

<h5>How They Work</h5>
<p>Person A recruits 5 people. Each pays UGX 100,000. Person A gets UGX 500,000. Each of those 5 must recruit 5 more. The scheme requires exponential growth — which is mathematically impossible to sustain.</p>

<h5>How to Identify One</h5>
<ul>
  <li>You earn mainly by recruiting, not from a real product or service</li>
  <li>There's pressure to recruit friends and family quickly</li>
  <li>The "product" is vague or overpriced</li>
  <li>Promises of passive income just for joining</li>
  <li>No registration with UMRA or Bank of Uganda</li>
</ul>

<h5>Famous Examples in Uganda</h5>
<p>Several pyramid schemes have operated in Uganda under names like "investment clubs" or "blessing circles." They always end the same way — the founders disappear with the money.</p>

<h5>What To Do</h5>
<ul>
  <li>Verify any investment group at <strong>Bank of Uganda</strong> or <strong>UMRA</strong></li>
  <li>Ask for audited financial statements</li>
  <li>Report suspicious schemes using SilentGuard's fraud report feature</li>
</ul>

<h5>Key Takeaway</h5>
<p>Legitimate investments don't require you to recruit. If recruitment is the main income source, walk away.</p>""",
    },
]


def seed_content(apps, schema_editor):
    EducationalContent = apps.get_model('home', 'EducationalContent')
    # Clear existing and reseed
    EducationalContent.objects.all().delete()
    for article in ARTICLES:
        EducationalContent.objects.create(**article)


def unseed_content(apps, schema_editor):
    EducationalContent = apps.get_model('home', 'EducationalContent')
    EducationalContent.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0014_educational_content_upgrade'),
    ]

    operations = [
        migrations.RunPython(seed_content, unseed_content),
    ]
