# MAHA Business Growth Score — V1 Product Specification

## 1. Customer problem
Small businesses often know they need better digital visibility but do not know what to fix first. V1 gives them a simple, understandable scorecard with prioritized actions.

## 2. Core user journey
1. User opens the free tool.
2. User enters business name, website URL, category, and location.
3. Tool generates a scorecard from the information available in V1.
4. User receives a shareable public scorecard URL.
5. Public scorecard includes useful findings and a subtle `Powered by MAHA` attribution.
6. Visitor can click `Get your own score` and become a new user.
7. Original user receives an additional analysis credit when the referred visitor activates.
8. Pro unlock can later provide deeper automated analysis.

## 3. Anti-spam rule
The product never requires users to send unsolicited messages. Sharing is optional for the initial result; additional credits are unlocked only for legitimate referral activity or public publication of the scorecard.

## 4. Monetization hypothesis
Free:
- 1 scorecard
- basic recommendations
- public share page

Growth:
- additional scans unlocked through genuine referrals
- enhanced score history

Pro (test only after activation):
- deeper diagnostics
- monitoring/alerts
- downloadable branded report
- multiple businesses

Potential pricing test: Rp49k–Rp149k/month or a low-priced lifetime upgrade. Pricing is a hypothesis, not a forecast.

## 5. Viral loop metrics
Track:
- visitor → activation rate
- scorecards generated per user
- share/publication rate
- referred visits per active user
- referred activation rate
- K-factor = referred activations / active users
- paid conversion rate
- revenue per active user

## 6. V1 scoring model
Initial score categories:
- Business clarity
- Offer clarity
- Contact/action clarity
- Trust signals
- Mobile/readability basics
- Shareability

V1 must clearly label any score as an automated heuristic, not an official Google ranking or audit.

## 7. Technical constraints
- Static frontend first.
- No paid infrastructure required for prototype.
- Secrets never stored in frontend or Git.
- Supabase is the persistence target for production MVP.
- Cloudflare Worker is the target API runtime if compatible with the final dependency set.

## 8. First validation
Do not optimize for scale before evidence.

Minimum evidence before building expensive automation:
- 10 users complete a scorecard
- 5 publish/share it
- 3 referred visitors arrive
- at least 1 referred user completes a scorecard
- at least 1 user indicates willingness to pay

## 9. Product rule
The product must market itself because the **artifact is useful**, not because the user is manipulated into advertising MAHA.
