# Paper 1: Domain Research
## Drop-off in Digital KYC Onboarding Funnels: Background, Business Impact, and How This Analysis Fits

> **Author note:** written for the "Customer Onboarding Funnel Drop-off Analysis (Digital KYC)" project.
> **Scope honesty:** the dataset in this project is **simulated**. Real KYC data is private (personal identity
> documents, biometrics) and is not publicly available. Statements about industry practice below are general
> background, checked and cited against the sources listed at the end of this paper. Nothing here is presented
> as a measured result from real company data.

---

### 1. Introduction
Know Your Customer (KYC) is the process by which a regulated business verifies who a customer is before
opening an account. Banks, fintech apps, wallets, brokerages and lending platforms are legally required to do
this to limit fraud, money laundering and terrorist financing. In India, digital KYC is shaped by regulators
such as the RBI and SEBI, and by identity infrastructure such as Aadhaar and PAN.

Historically KYC was in-branch and paper-based. Modern products run it inside a mobile app as a **funnel**:

`Registration -> Phone OTP -> Document upload -> Liveness / selfie check -> Consent / e-sign -> Approval`

Every step is a place where a user can leave. Funnel analysis asks *where* users leave, *why*, and *what it costs*.

### 2. Why this problem matters : three business pain points

**2.1 Customer Acquisition Cost (CAC) bleed.** A company pays to bring a user to the app (ads, referrals,
promotions). If that user quits during KYC, the spend produced no customer. Multiplied across thousands of
users, even a few percentage points of avoidable drop-off is real money. *Illustration (hypothetical):* 50,000
installs at a CAC of $50 is $2.5M of acquisition spend; each avoidable 1% of drop-off at that scale is $25,000.

**2.2 Vendor cost bleed.** Many companies buy identity verification from third-party vendors that charge per
verification attempt, often whether or not it succeeds. A step with a high failure rate on a specific device
class therefore costs twice: the user is lost *and* fees are paid for failed attempts. In this project's
simulation, 20.2% of simulated vendor fees ($7,080 of $35,101) were spent on failed attempts, and
Budget-Android devices, only 19.4% of users, accounted for 41.3% of that waste. *(Simulated fee levels are
assumptions, not real vendor prices.)*

**2.3 Compliance versus growth gridlock.** Compliance and Legal want thorough verification; Product and Growth
want a short, low-friction flow. Both are legitimate. Without data, the argument is opinion versus opinion.
A funnel analysis provides a neutral referee: it can show which step costs the most users and whether the
cost is technical (fixable without weakening controls) or structural (a genuine trade-off).

### 3. Existing approaches in the domain
This section summarises common practice, drawing on the sources cited at the end of this paper.

- **Funnel analysis** is a standard product-analytics technique: count users reaching each step, compute step
  conversion and drop-off, and locate the largest leak.
- **Friction measurement** goes beyond counts: retries, error codes, and time-on-step indicate *effort*, not just outcome.
- **Segmentation / cohort analysis** compares groups (device, region, document type, channel) to find where a
  problem concentrates. Device capability is widely recognised as an important factor for camera-based
  verification (image quality, autofocus, low light).
- **Vendor-side optimisation** includes capture guidance, auto-capture, glare/blur detection and
  passive liveness, all aimed at reducing failed attempts.
- **Predictive approaches** score sessions for abandonment risk so an intervention (help prompt, video-KYC
  fallback, save-and-resume) can be triggered. This project documents this as future work, not as a built feature.

### 4. How this project fits
| Question | This project's method |
|---|---|
| Where are users lost? | Volume Velocity: step conversion and drop-off % (SQL + Pandas) |
| How hard is each step? | Friction Density: retries and errors per session |
| Do they lack intent or hit a blocker? | Time Dwell: **Time-to-Abandon** cohorts (<5 s vs 5-60 s vs 60 s+) |
| Which errors hurt most? | Error-Impact Mapping: abandonment rate by error code |
| Who is hit hardest? | Device Tier cohorts: iOS, mid-tier Android, budget Android |
| What does it cost? | Vendor-cost analysis and estimated recovery |
| What should be done? | Prioritised Product Optimization Blueprint |

**Central framework: the Step-Metrics Matrix.** Each funnel step is scored on three dimensions: Volume Velocity,
Friction Density, Time Dwell. Combining them separates *"users left because they did not care"* from
*"users left because something broke"*, which need different fixes and different owners.

### 5. Findings on the simulated dataset (illustrative, not real-world claims)
The generator was designed with a documented rule: Budget-Android devices fail more on camera steps. The
analysis therefore *recovers a pattern that was built in*, and that is a **test of the pipeline**, not a discovery
about real users.

- Overall abandonment: **26.35%** (10,000 sessions).
- Largest drop-off step: **liveness check (8.49%)**, then document upload (7.42%).
- Early steps: most quitters left in under 5 seconds (registration 94%, consent 87%), consistent with low intent.
- Camera steps: 24% of document-upload quitters and 16% of liveness quitters spent over a minute trying, consistent with a technical blocker.
- Device tier: abandonment **40.1%** (Budget Android) vs **26.6%** (Mid Android) vs **19.6%** (iOS).
- Errors: sessions that hit an error abandoned at 35-42% vs 20.3% for error-free sessions.
- If Budget-Android abandonment matched Mid-Tier, an estimated **263 sessions (2.6% of all; 10% of all abandonment)** would be recovered.

Region and document type showed no meaningful differences, because the generator did not build any in. No
insight is claimed from them.

### 6. Limitations
1. **Simulated data.** Patterns are partly assumptions. Real data could show different, messier relationships.
2. **Independence assumptions.** Simulated attempts are independent; real retries are correlated (a bad camera stays bad).
3. **Observational, not causal.** Even on real data, association between device and abandonment does not prove the device caused it.
4. **Simplified outcomes.** The simulation has no fraud-rejection, manual-review, or later-day return visits.
5. **No cost validation.** Vendor fees are assumed values.

### 7. How this would extend in industry (not built)
- Replace simulated data with real event logs (with privacy controls); reuse the same SQL/Pandas pipeline.
- Predictive abandonment model on the same session table (Logistic Regression first, then gradient boosting, with explainability).
- Real-time nudges or fallback routing when predicted risk crosses a threshold.
- Continuous monitoring for step-level anomalies, e.g. a vendor outage.

### 8. Conclusion
Funnel drop-off in digital KYC is measurable, segmentable and costly. A step-by-step framework combining volume,
friction and time separates low-intent quitting from technical failure, and points to fixes with clear owners. The
methods transfer directly to real data; the specific numbers in this project do not, because the data is simulated.

### References
1. Reserve Bank of India. *Master Direction – Know Your Customer (KYC) Direction, 2016* (updated as on August 14, 2025). https://www.rbi.org.in/commonman/english/scripts/notification.aspx?id=2607 — regulatory basis for digital KYC/CDD in India.
2. Entrust (Onfido). *Liveness Verification* developer documentation. https://documentation.identity.entrust.com/guide/liveness-verification/ — official vendor documentation on liveness/biometric checks during onboarding, cited for Section 2.2 (vendor cost bleed) and Section 3 (existing approaches).
3. Amplitude. *Funnel Analysis* documentation — "Get the most out of Amplitude's Funnel Analysis chart" and "How Amplitude computes funnels". https://amplitude.com/docs/analytics/charts/funnel-analysis and https://amplitude.com/docs/analytics/charts/funnel-analysis/funnel-analysis-how-amplitude-computes — standard industry reference for funnel-analysis methodology (step ordering, conversion, drop-off), cited for Section 3.
