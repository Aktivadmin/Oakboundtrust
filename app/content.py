"""Editorial content for the public pages (blog, careers, help, pricing).

SAMPLE COPY: written as placeholder content for the Oakbound Trust Bank launch.
Replace the figures, roles and policy wording with approved text before going live.
"""

BLOG_POSTS = [
    {
        "slug": "build-an-emergency-fund",
        "title": "Build an emergency fund that actually sticks",
        "tag": "Saving", "date": "March 4, 2026", "read": "4 min read",
        "accent": "#2f6b3f", "doodle": "d-coin",
        "excerpt": "Start small, automate it, and give it a job. A practical way to build a cushion without feeling the pinch.",
        "body": [
            ("p", "An emergency fund is the money you set aside for the things you cannot plan for: a car repair, a gap between jobs, an unexpected bill. The goal is not a perfect number on day one. The goal is a habit you can keep."),
            ("h2", "Start with one month of essentials"),
            ("p", "Add up what you must pay each month: housing, food, transport, utilities, minimum debt payments. Aim for that single month first. It is a goal you can reach in a few months, and it already covers most small shocks."),
            ("h2", "Automate, then forget"),
            ("p", "Set a recurring transfer for the day after payday. Money you never see in your spending account is money you do not miss. Even a small amount, repeated, becomes a real cushion."),
            ("quote", "Give every pot a name and a job. A fund with a purpose is much harder to raid."),
            ("h2", "Keep it separate and reachable"),
            ("p", "Hold the fund in its own account so it does not blur into everyday spending, but keep it somewhere you can reach within a day or two. When you use it, rebuild it before you increase other saving goals."),
        ],
    },
    {
        "slug": "spot-a-payment-scam",
        "title": "How to spot a payment scam before it costs you",
        "tag": "Security", "date": "February 18, 2026", "read": "5 min read",
        "accent": "#4a3020", "doodle": "d-spark",
        "excerpt": "Scammers rely on urgency and trust. Here are the signals that should make you stop and check.",
        "body": [
            ("p", "Most payment scams follow the same script: someone creates a sense of urgency, asks you to move money quickly, and makes it feel awkward to question them. Knowing the script is half the defence."),
            ("h2", "Warning signs"),
            ("p", "Be wary of unexpected calls, texts or emails asking you to confirm details or move money to a 'safe account'. A real bank will never ask for your full PIN or password, and will never ask you to transfer funds to protect them."),
            ("h2", "What to do instead"),
            ("p", "Hang up and call the number on your card or on our website. Take your time: a genuine request will still be there in ten minutes. Never share one-time codes, even with someone who says they work for the bank."),
            ("quote", "If it feels urgent, that is the moment to slow down."),
            ("p", "If you think you have already sent money to the wrong person, contact us straight away. The sooner we know, the more we can do."),
        ],
    },
    {
        "slug": "international-transfers-checklist",
        "title": "International transfers: what to check before you send",
        "tag": "Payments", "date": "January 29, 2026", "read": "4 min read",
        "accent": "#5a9a68", "doodle": "d-arrow",
        "excerpt": "Details, deadlines and double checks that keep a cross-border payment from going astray.",
        "body": [
            ("p", "Sending money abroad has more moving parts than a local payment. A few minutes of checking up front saves days of chasing later."),
            ("h2", "Confirm the beneficiary details"),
            ("p", "Check the name, account number and bank identifier with the person you are paying, using a channel you trust. A single wrong digit can delay or misdirect a payment."),
            ("h2", "Understand the cost and timing"),
            ("p", "Look at the exchange rate, any fees, and the expected arrival window before you confirm. Public holidays in either country can add time."),
            ("h2", "Keep a record"),
            ("p", "Save the confirmation and reference number. If something goes wrong, those details help us trace the payment quickly."),
        ],
    },
    {
        "slug": "credit-scores-plain-english",
        "title": "A plain-English guide to credit scores",
        "tag": "Credit", "date": "January 12, 2026", "read": "6 min read",
        "accent": "#c9a24a", "doodle": "d-star",
        "excerpt": "What goes into a score, what does not, and the small habits that move it in the right direction.",
        "body": [
            ("p", "A credit score is a summary of how reliably you have repaid borrowing in the past. Lenders use it as one input when deciding whether to offer credit and on what terms."),
            ("h2", "What usually matters"),
            ("p", "Paying on time is the biggest factor. How much of your available credit you are using, how long you have held credit, and how often you apply for new credit also play a part."),
            ("h2", "Habits that help"),
            ("p", "Set up reminders or automatic payments so nothing is ever late. Keep balances comfortably below your limits. Apply only for credit you need, and check your report regularly for mistakes."),
            ("quote", "Small, boring habits beat clever tricks every time."),
        ],
    },
    {
        "slug": "saving-for-a-home",
        "title": "Saving for a home: the first twelve months",
        "tag": "Mortgage", "date": "December 15, 2025", "read": "5 min read",
        "accent": "#6b4630", "doodle": "d-acorn",
        "excerpt": "Turn a distant goal into a monthly number, and know what to line up before you apply.",
        "body": [
            ("p", "A home purchase is a long project. The first year is about building a plan and a habit, not hitting the finish line."),
            ("h2", "Work backwards from the goal"),
            ("p", "Estimate the price range you are aiming for, the deposit you will need, and the costs on top: fees, taxes, moving and furnishing. Divide the total by the months you have, and you have a monthly target."),
            ("h2", "Get your paperwork in order"),
            ("p", "Lenders look at income, spending, existing debts and savings history. Keep statements tidy and avoid taking on new borrowing in the months before you apply."),
            ("h2", "Talk to us early"),
            ("p", "A short conversation can tell you what you might be able to borrow and what to work on, long before you start viewing homes."),
        ],
    },
    {
        "slug": "small-business-banking",
        "title": "Running a small business account without the admin",
        "tag": "Business", "date": "November 27, 2025", "read": "4 min read",
        "accent": "#1f4a2c", "doodle": "d-leaf",
        "excerpt": "Separate the money, track it simply, and keep tax time from becoming a scramble.",
        "body": [
            ("p", "Mixing personal and business money is the fastest way to make bookkeeping painful. A dedicated business account fixes most of it on day one."),
            ("h2", "Keep everything in one place"),
            ("p", "Receive payments, pay suppliers and set money aside for tax from the same account, so your statements tell the whole story."),
            ("h2", "Make reconciling a weekly habit"),
            ("p", "Ten minutes each week matching payments to invoices is far easier than a whole month at once."),
            ("h2", "Plan for the quiet months"),
            ("p", "Hold a buffer that covers a few weeks of costs. It turns a slow month into an inconvenience, not a crisis."),
        ],
    },
]

JOBS = [
    {"slug": "senior-backend-engineer", "title": "Senior Backend Engineer", "team": "Engineering", "where": "Remote", "type": "Full-time",
     "about": "Own core banking services written in Python and Django, from data model to deployment.",
     "do": ["Design and ship reliable payment and account features", "Improve test coverage, observability and performance", "Review code and mentor teammates"],
     "need": ["Strong Python and relational database skills", "Experience building secure, high-availability services", "Clear written communication"]},
    {"slug": "product-designer", "title": "Product Designer", "team": "Design", "where": "Hybrid", "type": "Full-time",
     "about": "Shape how money feels to use: accessible, calm and quick.",
     "do": ["Design flows from sketch to polished prototype", "Maintain our design system and brand", "Run research sessions with customers"],
     "need": ["A portfolio of shipped product work", "Fluency in Figma and prototyping", "A strong eye for typography and detail"]},
    {"slug": "customer-support-specialist", "title": "Customer Support Specialist", "team": "Support", "where": "Remote", "type": "Full-time",
     "about": "Be the calm, knowledgeable voice customers meet when they need help.",
     "do": ["Resolve account and payment questions", "Spot patterns and feed them back to product", "Keep help articles accurate"],
     "need": ["Empathy and clear writing", "Comfort learning financial products", "Reliability under pressure"]},
    {"slug": "compliance-analyst", "title": "Compliance Analyst", "team": "Risk & Compliance", "where": "On-site", "type": "Full-time",
     "about": "Help us keep customers and the bank safe by monitoring, reviewing and improving controls.",
     "do": ["Review account and transaction alerts", "Maintain policies and training", "Prepare reports for regulators and auditors"],
     "need": ["Experience in financial compliance or risk", "Attention to detail", "Sound judgement"]},
]

FAQS = [
    ("Accounts", "How do I open an account?", "Choose Open account and follow the steps. You will be asked for personal details, employment information, a photo ID and a selfie, security questions, and a transaction PIN."),
    ("Accounts", "How do I log in and reset my password?", "Use Log in at the top of any page. If you have forgotten your password, choose Forgot password and we will email you a secure reset link."),
    ("Accounts", "Why can I not access some features?", "Some features need your identity and profile to be fully verified. If your account has been restricted, contact us and we will explain what is needed."),
    ("Cards", "How do I apply for a card?", "Sign in to your account, open Cards, pick the card that suits you and submit the short application. We will email you about the outcome."),
    ("Cards", "What should I do if my card is lost or stolen?", "Contact us immediately so the card can be blocked. Do not wait: the sooner we know, the sooner we can protect your money."),
    ("Transfers", "How do I send money?", "From your dashboard choose Transfer, then pick local or international, add the beneficiary and confirm with your PIN."),
    ("Transfers", "How long do transfers take?", "Timing depends on the destination, the amount and any checks we need to complete. You can follow every payment in your transaction history."),
    ("Transfers", "Why was my transfer paused or declined?", "We sometimes review payments to protect you and meet legal requirements. If we need more information we will tell you how to provide it."),
    ("Loans", "How do I apply for a loan or mortgage?", "Open the Loans or Mortgage page, check the options and start an application. You can save your progress and come back."),
    ("Loans", "What do you look at when I apply?", "Typically your income, existing commitments, credit history and the purpose and size of the loan."),
    ("Security", "How do you protect my account?", "Security questions, a transaction PIN, identity verification and monitoring for unusual activity all work together to keep your account safe."),
    ("Security", "Will you ever ask for my full PIN or password?", "Never. If someone asks for it, even if they say they are from the bank, do not share it and contact us."),
    ("Support", "How can I contact you?", "Use the Contact page to send us a message. For anything urgent about a card or a payment, say so in the subject line."),
]

PLANS = [
    {"name": "Everyday", "price": "$0", "per": "/month", "blurb": "A simple account for day-to-day money.", "feat": False,
     "items": ["Online account and dashboard", "Local and international transfers", "Transaction history and alerts", "Card application"]},
    {"name": "Plus", "price": "$9", "per": "/month", "blurb": "More room for people who bank often.", "feat": True,
     "items": ["Everything in Everyday", "Priority support", "Higher transfer allowances", "Preferred rates on selected loans"]},
    {"name": "Business", "price": "$19", "per": "/month", "blurb": "For small businesses and sole traders.", "feat": False,
     "items": ["Everything in Plus", "Separate business account", "Invoice-friendly payment references", "Dedicated onboarding"]},
]

SERVICES = [
    ("Accounts", "Open a personal account and manage everything from one dashboard.", "d-coin", "signup"),
    ("Cards", "Apply for a card and follow your spending.", "d-star", "cards"),
    ("Transfers", "Move money locally or abroad with clear confirmations.", "d-arrow", "international-transfer"),
    ("Loans", "Borrow for what matters, with a clear application.", "d-leaf", "loans"),
    ("Mortgage", "Plan, apply and track your journey to a home.", "d-acorn", "mortgage"),
    ("Small business", "Banking tools built around how small firms work.", "d-loop", "small-businesses"),
    ("Invest & wealth", "Grow your money with guidance you can trust.", "d-spark", "investment"),
    ("Security", "Layers of protection around every account.", "d-spark", "security"),
]


def post_by_slug(slug):
    return next((p for p in BLOG_POSTS if p["slug"] == slug), None)


def job_by_slug(slug):
    return next((j for j in JOBS if j["slug"] == slug), None)
