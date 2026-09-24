---
name: gamebox-aab-publish
description: Use when user invokes /gamebox-aab-publish or asks to version, sign, build release AAB, generate privacy policy and SEO listing, and write the Play Console publish guide.
---
> **Public version:** no hardcoded developer identity ships in this copy. Ask the user for organization name, contact email, and country code at the start of each run - never assume values.


# 🎮 GAMEBOX-AAB-PUBLISH — Signed AAB, Privacy, SEO & Detailed Publish Guide
**GameBox V2.0 | Skill 4 of 6**
**Scope:** One project (the same one just verified in GAMEBOX-TEST-APK).
**Output:**
- `./Reports/[GameName]/[GameName]_Report.md` (appended — signing + privacy summary)
- `./Reports/[GameName]/[GameName]_Publish_Guide.md` (**separate file** — the
  full, explained, step-by-step Play Console walkthrough)
- `./APK_AAB/[GameName]/[GameName]-release.aab` (signed — this is what gets uploaded)
- `./APK_AAB/[GameName]/[GameName].keystore`
- `./APK_AAB/[GameName]/[GameName]_keystore_info.txt`
**Next:** None — this is the final skill. The user does the actual Play
Console submission by hand, using the Publish Guide.

> **No release `.apk` is produced anywhere in this pipeline.** Only the
> unsigned test APK (from GAMEBOX-TEST-APK) and the signed release **AAB**
> exist. Google Play requires the AAB for submission — a signed release
> APK isn't part of the deliverable set here.

---

## PURPOSE

Bump the version, generate a release signing keystore, build the signed
release AAB, generate and host a privacy policy, produce SEO store-listing
content — then package all of it into ONE detailed Publish Guide that
doesn't just hand over pre-filled values, but **explains what each Play
Console decision means and why**, so the user can actually choose
confidently instead of guessing.

---

# ═══════════════════════════════════════════
# PHASE 1 — VERSION MANAGEMENT
# ═══════════════════════════════════════════

## STEP 1 — DETECT CURRENT VERSION

Read `app/build.gradle`:
- Current `versionCode` (integer)
- Current `versionName` (string, e.g., "1.0")

> `Current version: [versionName] (code: [versionCode])`

## STEP 2 — PROPOSE, DON'T AUTO-INCREMENT

Never silently bump the version. Show both the current value and a
suggested next value, and let the user confirm or override — this matters
because the local project's version number may not match what's actually
live in Play Console (e.g. if a previous export was uploaded manually, or a
build was made but never published).

> `Current local version: [versionName] (code: [versionCode])`
> `Suggested next version: [versionName+0.1 or +1] (code: [versionCode+1])`
> `Does this match what's currently live on Google Play for this app? If
> you're not sure, check the Play Console → your app → Release → Production
> before confirming. What version should this build be?`

If the user provides:
- Just a name (e.g., "2.0") → `versionName = "2.0"`, `versionCode = [current+1]`
- Both values → use exactly what they provide
- "keep"/"same" → don't change version

Show the exact diff and apply after explicit approval.

---

# ═══════════════════════════════════════════
# PHASE 2 — KEYSTORE & SIGNED AAB BUILD
# ═══════════════════════════════════════════

## STEP 0 — VERIFY FOLDER

```bash
mkdir -p ./APK_AAB/[GameName]
```

## INPUT REQUIRED

| Field | Source |
|-------|--------|
| Game Name | `_internal/SCAN_data.txt` or ask |
| Package Name | `_internal/SCAN_data.txt` or ask |
| Organization name | Ask the user |
| Country code | Ask the user |
| Keystore password | Generate strong random OR user-provided |
| Key password | Generate strong random OR user-provided (recommended: different) |

Show all values. Ask for confirmation before proceeding.

## PRE-BUILD CHECK

Re-verify before building release artifacts:
- [ ] `targetSdk` / `compileSdk` 36+
- [ ] `com.android.billingclient:billing` 8.0.0+ (if IAP present)
- [ ] `ndkVersion` 27+ and `useLegacyPackaging = false`
- [ ] `_internal/STATE.json` shows `"test_apk": "PASS"` and the real-device
      test in GAMEBOX-TEST-APK actually passed — **do not sign and build a
      release from a project that hasn't been verified on a real device.**
      If it wasn't tested, stop and send the user back to GAMEBOX-TEST-APK.

## STEP 3 — GENERATE KEYSTORE

```bash
keytool -genkey -v \
  -keystore "./APK_AAB/[GameName]/[GameName].keystore" \
  -alias [GameName]_release \
  -keyalg RSA \
  -keysize 2048 \
  -validity 10000 \
  -storepass [keystorePassword] \
  -keypass [keyPassword] \
  -dname "CN=[GameName], O=[Organization - ask], C=[Country - ask]"
```

Verify:
```bash
keytool -list -v \
  -keystore "./APK_AAB/[GameName]/[GameName].keystore" \
  -storepass [keystorePassword]
```

If `.keystore` already exists → warn user, ask: **replace / keep / abort**.
Never overwrite without explicit YES — this file is irreplaceable; losing it
means losing the ability to ever update this app on Google Play again.

## STEP 4 — CREATE CREDENTIAL FILE

Create `./APK_AAB/[GameName]/[GameName]_keystore_info.txt`:

```
════════════════════════════════════════════
GAMEBOX KEYSTORE CREDENTIALS
Game:    [GameName]
Created: [date time]
════════════════════════════════════════════

Keystore File:      [GameName].keystore
Keystore Path:      ./APK_AAB/[GameName]/[GameName].keystore
Keystore Password:  [keystorePassword]

Key Alias:          [GameName]_release
Key Password:       [keyPassword]
Key Algorithm:      RSA 2048
Key Validity:       10000 days

Certificate Info:
  CN: [GameName]
  O:  GameBox
  C:  EG

Package Name:       [packageName]

────────────────────────────────────────────
⚠️  SECURITY WARNING
- This file and the .keystore sit inside ./APK_AAB/[GameName]/ alongside
  your build outputs for convenience — but that also means: DO NOT sync
  this folder to a public cloud drive, DO NOT commit it to any repository,
  and DO NOT share it outside a secure channel.
- If this keystore is lost, you CANNOT update your app on Google Play.
- Back up the .keystore file AND this credentials file to at least 2
  separate secure locations (encrypted drive, password manager attachment,
  offline backup) right after this step.
────────────────────────────────────────────

Google Play Notes:
Upload [GameName].keystore as your upload key during first Play Console
submission. If using Play App Signing, this becomes your upload key.

════════════════════════════════════════════
```

Display the path in chat and repeat the backup warning verbally.

## STEP 5 — CONFIGURE SIGNING IN BUILD.GRADLE

Show exact diff. Wait for confirmation.

```gradle
signingConfigs {
    release {
        storeFile file("[relative path to]/APK_AAB/[GameName]/[GameName].keystore")
        storePassword "[keystorePassword]"
        keyAlias "[GameName]_release"
        keyPassword "[keyPassword]"
    }
}

buildTypes {
    release {
        signingConfig signingConfigs.release
        minifyEnabled true
        shrinkResources true
        proguardFiles getDefaultProguardFile('proguard-android-optimize.txt'), 'proguard-rules.pro'
    }
    debug {
        signingConfig signingConfigs.debug
    }
}
```

## STEP 6 — BUILD THE SIGNED RELEASE AAB (no release APK)

```bash
./gradlew bundleRelease
```
Output: `app/build/outputs/bundle/release/app-release.aab`

Verify the AAB is actually signed — `.aab` bundles use JAR signing, not the
APK v1/v2/v3 schemes, so `apksigner` is not the right tool here:
```bash
jarsigner -verify -verbose -certs app/build/outputs/bundle/release/app-release.aab
```
Confirm output includes `jar verified.`

Re-run the 16 KB alignment check against the AAB's base module libraries
(release minification can repackage `.so` files differently than the debug
test build did):
```bash
unzip -o app/build/outputs/bundle/release/app-release.aab -d /tmp/aab_check "base/lib/*"
for f in $(find /tmp/aab_check/base/lib -name "*.so"); do
  objdump -p "$f" | grep LOAD
done
```
All `LOAD` segments must show `align 2**14` or higher.

## STEP 7 — COPY TO APK_AAB FOLDER

```bash
cp app/build/outputs/bundle/release/app-release.aab ./APK_AAB/[GameName]/[GameName]-release.aab
ls -lh ./APK_AAB/[GameName]/
```

---

# ═══════════════════════════════════════════
# PHASE 3 — PRIVACY POLICY
# ═══════════════════════════════════════════

## INPUT REQUIRED

| Field | Source |
|-------|--------|
| Game Name / Package Name | From Phase 2 |
| Developer / Organization | Ask the user (no default) |
| Developer contact email | Default: **[ask the user - developer contact email]** |
| Does the game show ads? | From scan data or ask |
| Does the game have in-app purchases? | From scan data or ask |
| Does the game collect location data? | Ask |
| Does the game require account creation? | Ask |
| Google account email (for Firebase) | Default: **[ask the user - developer contact email]** |

## GENERATE PRIVACY POLICY HTML

Generate a complete, self-contained privacy policy HTML at
`./Reports/[GameName]/privacy-policy.html` (temp location before deploy —
Firebase hosting will serve the deployed copy, this local file is the
source). Must be:
- Fully self-contained (no external CSS/JS)
- Clean, professional design
- Google Play policy compliant, GDPR-aware
- Accurate to the game's actual data practices

### Required sections
1. **Introduction** — app name, developer, effective date
2. **Information We Collect** — only what applies:

| Condition | Add this section |
|-----------|-----------------|
| Shows ads | Device identifiers (Advertising ID), ad SDK usage data |
| Has IAP | Purchase history, payment processing (via Google Play) |
| Collects location | Location data |
| Requires account | Email, username, profile data |
| Always | App usage data, crash reports, device information |

3. **How We Use Your Information**
4. **Third-Party Services** — AdMob (if ads), Play Billing (if IAP),
   Firebase Analytics/Crashlytics (always, Buildbox default), Google Play Services
5. **Data Retention**
6. **Children's Privacy** — COPPA statement or "not directed at under-13"
7. **Your Rights** — access/correct/delete, contact, GDPR if applicable
8. **Changes to This Policy**
9. **Contact Us**

## HOST ON FIREBASE

```bash
firebase login   # if not already logged in
cd ./Reports/[GameName]
firebase init hosting
```
| Prompt | Answer |
|--------|--------|
| Which Firebase project? | Create new: `[gamename]-privacy` (or reuse if exists) |
| Public directory? | `.` |
| Single-page app? | `N` |
| Automatic GitHub builds? | `N` |
| Overwrite index.html? | `N` |

```bash
mv privacy-policy.html index.html
firebase deploy --only hosting
```
Record the Hosting URL (`https://[project-id].web.app`). Test it loads in
a browser.

---

# ═══════════════════════════════════════════
# PHASE 4 — SEO STORE LISTING CONTENT
# ═══════════════════════════════════════════

## INPUT REQUIRED

Ask the user for:
1. Genre (endless runner, puzzle, platformer, idle, arcade...)
2. Core gameplay loop (1–2 sentences)
3. Main character or theme
4. Key features (up to 5 bullets)
5. Competitor games it's similar to
6. Target audience: kids / casual / everyone / teens

## COMPETITOR RESEARCH (live web search, not memory)

Web-search for 3–5 similar games currently on Google Play. Extract their
titles, short descriptions, and visible tags/keywords. This keeps the SEO
content grounded in what's actually ranking right now instead of stale
knowledge.

## GENERATE ALL ASSETS

- **App Title** (max 30 chars) — 3 variations, one recommended with reason
- **Short Description** (max 80 chars) — 3 variations
- **Full Description** (max 4000 chars) — Hook (keyword in first 167
  chars) → Gameplay Overview → Key Features (5–8 bullets, `🎮 Name — desc.`)
  → Why Play This → Technical Info → Call to Action
- **Keyword Strategy** — 5 primary (with placement), 10 secondary
  long-tail, keywords to avoid
- **Tags** (max 5, from Play Store taxonomy)
- **Feature Graphic Copy** — headline (≤6 words), subheadline (≤10 words),
  suggested visuals
- **What's New** (first release): `Initial release. Download and start playing now!`
- **Content Rating Guidance** — recommended answers per category with reasoning

All content must be Google Play policy compliant (no misleading claims, no
keyword stuffing).

---

# ═══════════════════════════════════════════
# PHASE 5 — ASSEMBLE OUTPUTS
# ═══════════════════════════════════════════

## OUTPUT 1 — append to `./Reports/[GameName]/[GameName]_Report.md`

```markdown
## 🔐 Signing & Release Build
**Completed:** [date time]

| Field | Before | After |
|-------|--------|-------|
| versionName | 1.0 | 2.0 |
| versionCode | 1 | 2 |

| Field | Value |
|-------|-------|
| Keystore | `./APK_AAB/[GameName]/[GameName].keystore` |
| Credential File | `./APK_AAB/[GameName]/[GameName]_keystore_info.txt` |
| Release AAB | `./APK_AAB/[GameName]/[GameName]-release.aab` (xx MB) |
| AAB Signature Verified | ✅ jarsigner: jar verified |
| 16 KB Alignment (AAB base/lib) | ✅ All libs aligned |
| Target API Level | ✅ 36+ |
| Billing Library | ✅ 8.0.0+ (if IAP) |

⚠️ Keystore backed up to 2+ secure locations — confirm this before moving on.

## 🌐 Privacy Policy
| Field | Value |
|-------|-------|
| Live URL | https://[project-id].web.app |
| Covers Ads / IAP / Location / Account | Yes/No each |
| COPPA / GDPR | Yes/No each |
```

Update `_internal/STATE.json`: `"aab_publish": "PASS"`.

## OUTPUT 2 — `./Reports/[GameName]/[GameName]_Publish_Guide.md` (separate file)

This is the file the user actually works from inside Play Console. Every
field has the ready-to-paste value **and** a short plain-language
explanation of what the choice means and what it affects — never assume
the user already knows Play Console conventions. Use this template:

```markdown
# 🎮 [GameName] — Google Play Publish Guide
**Package:** [packageName]
**Generated:** [date time]

> Every field below has the value ready to copy, plus a short explanation
> of what it means and why it matters — so you're not just filling boxes
> blind.

---

## 📋 Before You Start

- [ ] Signed AAB ready: `./APK_AAB/[GameName]/[GameName]-release.aab`
- [ ] Keystore backed up to 2+ places
- [ ] Privacy policy live: `[privacyPolicyURL]`
- [ ] App icon: 512×512 PNG, no alpha channel — **you provide this file**
- [ ] Feature graphic: 1024×500 JPEG/PNG — **you provide this file**
- [ ] Phone screenshots: 2–8, JPEG/24-bit PNG — **you provide these**
- [ ] Target API 36+, Billing Library 8.0.0+ (if IAP), 16 KB alignment —
      all already confirmed in the Master Report above

---

## 🖥️ SCREEN 1 — Create Application

`https://play.google.com/console` → **Create app**

| Field | Value | Why it matters |
|-------|-------|-----------------|
| App name | `[GameName]` | This is the exact name shown on the store listing — you can adjust wording later, but the package name (below) is permanent. If the Phase 0 check flagged an exact-name collision with apps already on Play, use the differentiated SEO title here (e.g. `[GameName]: [suffix]`), not the bare game name. |
| Default language | Fill the language the console created for this app (observed: `English (United Kingdom)` / en-GB — do NOT assume en-US) | The fallback language shown if a user's device locale isn't otherwise translated. Complete the listing in exactly this language; add further translations only via "Add translation". |
| App or Game | `Game` | Affects which category options and store templates you get later — must match the actual content type. |
| Free or Paid | `[Free/Paid]` | **This cannot be changed from Paid to Free later without unpublishing and republishing as a new app** — free apps can add IAP later without this restriction. |

---

## 🖥️ SCREEN 2 — Main Store Listing

**Path:** Grow → Store presence → Main store listing

### App details
| Field | Value |
|-------|-------|
| App name (30 char limit) | `[title]` |
| Short description (80 char limit) | `[from SEO]` |
| Full description (4000 char limit) | `[from SEO — full text pasted here]` |

*Short description shows right under the title in search results — it's
often the deciding factor for whether someone taps into your listing at
all, so keep it benefit-focused, not just descriptive.*

### Graphics — you provide these files
| Asset | Size | What it's for |
|-------|------|----------------|
| App icon | 512×512, no alpha | Shown everywhere the app is listed — home screen, search, store |
| Feature graphic | 1024×500 | The banner Play may show at the top of your listing or in promotional placements |
| Phone screenshots | 2–8 | The single biggest factor in convert-to-install after your icon/title — lead with your best gameplay moment |

### Categorization
| Field | Value | Why it matters |
|-------|-------|-----------------|
| App category | `Games` | Determines which charts/browse sections you can appear in |
| Subcategory | `[Arcade/Casual/Action]` | Narrows discoverability further — pick the closest match to actual gameplay, not the most popular one, or Google may reclassify it later |

### Contact details
| Field | Value |
|-------|-------|
| Email | `[ask the user - developer contact email]` |
| Website | `[supportURL or privacy URL]` |
| Privacy policy | `[privacyPolicyURL]` |

---

## 🖥️ SCREEN 3 — App Content

**Path:** Policy → App content

Follow the console's own section order (dashboard checklist): Privacy
policy → Sign-in details → Ads → Content rating → Target audience →
Data safety → Government apps → Financial features → Health.

### Privacy policy
Paste: `[privacyPolicyURL]` → Save.

### Sign-in details (App access)
| Question | Answer | Why it matters |
|----------|--------|-----------------|
| All or some functionality restricted? | `All functionality is accessible` | Only change this if login is required to play — Google's reviewer needs to be able to test the whole app, so if anything is gated, you must provide test credentials here. |

### Ads
| Question | Answer | Why it matters |
|----------|--------|-----------------|
| Does your app contain ads? | `[Yes/No]` | If Yes, you must also correctly declare this in Data Safety below — a mismatch between this answer and your actual ad SDK behavior is a common rejection reason. |

If Yes: select every ad format actually used (banner/interstitial/rewarded)
— check which ones were detected in the scan (`[list from scan data]`).

### Content ratings
Step 1 — Category: select **Game**, enter the developer contact email,
agree to the IARC Terms of Use → Next.

Step 2 — Questionnaire. This determines the age rating badges shown in
every region's store (ESRB, PEGI, etc.) — **answer honestly based on
actual content**, not what you think will sell better; a mismatch found
later can get the app removed. For a typical Buildbox casual game with
ads + IAP and no mature content:

| Questionnaire item | Answer | Why |
|----------|--------|-----|
| Violence, blood or gory images | `No` | Abstract shapes/obstacles only — no characters, weapons, or combat |
| Fear (scary/horrifying/disturbing) | `No` | No horror content |
| Sexuality, suggestiveness or dating | `No` | Casual game, no such content |
| Gambling themes / simulated / real gambling | `No` — unless the game has loot boxes, slots, or chance-based paid rewards | Direct IAP purchases (remove-ads, packs) are NOT gambling; chance-based mechanics ARE — verify against the actual shop |
| Language (offensive) | `No` | No dialogue/text of concern |
| Controlled Substance | `No` | Not applicable |
| Crude Humour | `No` | Not applicable |
| Digital purchases, cash rewards or NFTs | **`Yes` if the game has IAP, `No` only if it truly has none** | ⚠️ This must match the binary: shipping Google Play Billing while answering No is a review mismatch and a rejection trigger |
| Miscellaneous (user interaction, precise location sharing, extremist content, etc.) | `No` to all | No chat/UGC, no location sharing, no such content |

Step 3 — Summary: review, then **Save** → back to dashboard.

Click **Save questionnaire** → **Calculate rating**.

### Target audience and content
Step 1 — Target age: tick `13–15`, `16–17`, `18 and over`; leave all
under-13 boxes unchecked (unless the game is genuinely aimed at children
— see warning below).
| Question | Suggested Answer | Why it matters |
|----------|-------------------|-----------------|
| Target age groups | `13–15, 16–17, 18+` | Selecting an under-13 age group triggers **Families Policy** requirements — stricter ad content rules, no behavioral ad targeting to that audience, and additional data safety declarations. Only select it if the game is genuinely aimed at children. |
| Does your app appeal to children? | `[Yes/No]` | This is a separate signal from the target age group — Google can flag "appeals to children" even for an "Everyone" rated app based on art style/theme, and that also triggers extra ad restrictions. Answer based on genuine visual style/theme, not marketing intent. |

Complete the remaining Target-audience steps (App details → Ads → Store
presence → Summary) with the values from this guide, then Save.

### Data safety
**Path:** Policy → Data safety

Steps 1–2 — Overview → Data collection and security:

This section tells users exactly what data is collected and why — before
you fill it in, understand: **anything your ad SDK or Firebase Analytics
collects counts as "collected by your app,"** even though you didn't write
that code yourself. Buildbox exports almost always collect at minimum:
Advertising ID, app interactions, and crash logs.

> ⚠️ **A mismatch between what you declare here and what your app actually
> does is itself a suspension trigger** — separate from whether the app
> crashes or not. If in doubt, under-declaring is worse than
> over-declaring: declare every SDK actually bundled in the AAB (check the
> ad SDK list from the scan report), not just the ones you remember adding.

| Question | Answer | Why |
|----------|--------|-----|
| Does your app collect or share user data? | `Yes` | True for any ad-supported or analytics-enabled app |
| Is all data encrypted in transit? | `Yes` | Standard for Google/AdMob/Vungle/Firebase SDKs (HTTPS/TLS) — answer No only if the app itself sends data over plain HTTP |
| Account creation methods | Tick `My app does not allow users to create an account` (if true) + `Can users log in…?` → `No` | Must match the Sign-in details answer above |
| User data deletion request available? | `Yes` — via the contact email in the privacy policy | Say No only if no request channel exists; the generated privacy policy provides the email channel, so Yes is correct |
| Independent security review | `No` | Unless the app was actually reviewed against a standard (e.g. MASA) |
| UPI payments verified | Skip | Only for finance apps operating in India |

Step 3 — Data types. Tick exactly these (leave everything else unchecked):

**Data types to declare:**
| Data type | Collected | Shared | Purpose |
|-----------|-----------|--------|---------|
| Device or other IDs (Advertising ID) | Yes | Yes | Advertising |
| App activity → App interactions | Yes | Yes | Analytics / Advertising |
| App info and performance → Crash logs | Yes | Yes | App functionality |
| Financial info → Purchase history | Yes (only if IAP) | No | App functionality |

Location, Personal info, Health and fitness, Messages, Photos and videos,
Audio files, Files and docs, Calendar, Contacts, Web browsing → all
unchecked (unless the scan proves otherwise).

Steps 4–5 — Data usage and handling → Preview: confirm the store-listing
preview matches the table above, then Save.

### Data safety via CSV export/import (recommended over clicking)
The Data safety page has **Export to CSV** / **Import from CSV** (top
right). Use this workflow — it is faster and produces a versioned file —
but follow these rules learned from real imports:

1. **Export first, never start from Google's sample CSV.** The sample
   template is incomplete: it lacks the account-creation rows
   (`PSL_SUPPORTED_ACCOUNT_CREATION_METHODS` / `PSL_ACM_*`), the deletion
   URL row (`PSL_ACCOUNT_DELETION_URL`), and the conditional outside-login
   row (`PSL_HAS_OUTSIDE_APP_ACCOUNTS`). Only an export from the app's own
   console contains every exact Question ID + Response ID. Save it to
   `./Reports/[GameName]/[GameName]-data-safety-export.csv`.
2. **Import overwrites everything** already entered in the form — that is
   the point, but re-verify steps 2–5 visually after importing.
3. **Fill every conditional row or the import fails.** The importer reports
   missing responses one batch at a time (`Response missing for <ID>`).
   Known rows that must be answered explicitly:
   | Row | Value | When |
   |-----|-------|------|
   | `PSL_SUPPORTED_ACCOUNT_CREATION_METHODS` / `PSL_ACM_NONE` = TRUE | No in-app accounts | Always answer the account block, even for "no accounts" |
   | `PSL_HAS_OUTSIDE_APP_ACCOUNTS` = FALSE (response ID empty) | No in-app accounts | This question only exists when ACM is none — it is in neither the sample nor the export; add the row manually |
   | `PSL_ACCOUNT_DELETION_URL` = `[privacyPolicyURL]` | Deletion answer is Yes | Required as soon as deletion=Yes; the privacy page is the correct link since it names the request channel |
   | `PSL_SUPPORT_DATA_DELETION_BY_USER` / `DATA_DELETION_YES` = TRUE | Deletion via contact email | Note: the export uses this ID, not the sample's `PSL_DATA_COLLECTION_USER_REQUEST_DELETE` |
   | `…:PSL_DATA_USAGE_EPHEMERAL` = FALSE per selected data type | Always | Blank ephemeral cells are rejected — none of the ad/analytics/IAP data is memory-only |
4. Keep Response values uppercase (`TRUE`/`FALSE`), keep every label cell
   byte-identical, leave all non-applicable rows blank (not FALSE, except
   the ephemeral rows above).
5. Save the filled file as
   `./Reports/[GameName]/[GameName]-data-safety-import.csv`, import it,
   and if the console reports another `Response missing for <ID>`, patch
   that row the same way and re-import.

### Government apps
| Question | Answer | Why it matters |
|----------|--------|-----------------|
| Is this app developed for or on behalf of a government? | `No` | Only government-built or government-commissioned apps answer Yes — answering Yes triggers extra verification you cannot pass. |

### Financial features
| Question | Answer | Why it matters |
|----------|--------|-----------------|
| Does the app provide banking, payment, crypto, or other financial features? | `No` | In-app purchases through Google Play Billing are NOT financial features — this section is about banking/finance apps. Answer Yes only for genuine finance functionality. |

### Health
| Question | Answer | Why it matters |
|----------|--------|-----------------|
| Does the app include health, fitness, or medical features? | `No` | Answer Yes only for genuine health/fitness functionality (workouts, medical advice, health-data sync) — a casual game is always No. |

### Advertising ID declaration
**Path:** Policy → App content → Advertising ID declaration. You cannot
roll out releases targeting Android 13+ until this is completed.

| Question | Answer | Why it matters |
|----------|--------|-----------------|
| Does your app use an advertising ID? | `Yes` if the game shows ads (AdMob/Vungle/etc.), `No` only for a truly ad-free build with no ad SDKs | This includes ad SDKs — if any bundled SDK uses the advertising ID, you must declare Yes. |

If Yes, the console then asks "Why does your app need to use an advertising
ID?" — tick all that apply:

| Purpose | Tick when | Typical Buildbox game |
|---------|-----------|----------------------|
| Advertising or marketing | Ads are displayed or measured (AdMob/Vungle/etc.) | ✅ tick |
| Analytics | An ad/analytics SDK uses it for aggregated measurement | ✅ tick if ad SDKs present |
| App functionality | The ID enables features or authenticates users | ❌ skip for games |
| Developer communications | Push notifications about the app | ❌ skip |
| Fraud prevention, security and compliance | Login-abuse monitoring etc. | ❌ skip |
| Personalisation | Recommendations based on user data | ❌ skip |
| Account management | User accounts across services | ❌ skip (no accounts) |

These must stay consistent with the Data Safety purposes declared for
Device or other IDs — a purpose ticked here but missing there (or vice
versa) is a mismatch flag.

If Yes, the release artifact **must** contain the
`com.google.android.gms.permission.AD_ID` permission or Play blocks the
release. Verify before answering:
- Source manifest declares it explicitly (`app/src/main/AndroidManifest.xml`), and/or
- The release merged manifest
  (`app/build/intermediates/merged_manifests/release/processReleaseManifest/AndroidManifest.xml`)
  contains `<uses-permission android:name="com.google.android.gms.permission.AD_ID" />`,
  and/or `aapt dump badging` on the built APK lists it.
If the permission is missing, add `<uses-permission android:name="com.google.android.gms.permission.AD_ID" />` to the source manifest and rebuild — do not answer No just to skip the declaration when ads are present (that zeroes out the ad identifier and breaks ad SDK attribution).

---

## ⚠️ Before You Submit: Repetitive Content / Account Pattern Reminder

If the Policy & Differentiation Risk Check in GAMEBOX-SCAN-FIX (Phase 0)
flagged this game as similar to other apps in this developer account,
**that risk has not been resolved by anything in this guide.** Code fixes,
signing, and SEO copy do not address Repetitive Content or Spam &
Minimum Functionality policy risk — only genuine content differentiation
does. Re-read that check's recorded answer in the master report before
submitting. If it was 🟠 or 🔴 and nothing changed since, submitting this
app as-is carries real suspension risk regardless of how clean the build is.

---

## 🖥️ SCREEN 4 — Store Settings

**Path:** Grow → Store presence → Store settings

| Field | Value |
|-------|-------|
| App category | `Games` |
| Tags | `[from SEO — up to 5]` |
| Contact email | `[ask the user - developer contact email]` |

---

## 🖥️ SCREEN 5 — Production Release

**Path:** Release → Production → **Create new release**

1. Click **Upload** → select `./APK_AAB/[GameName]/[GameName]-release.aab`
2. Wait for processing (1–5 min) — confirm package name and version match
3. **Play App Signing**: choose **Use Google-managed key** (recommended —
   Google re-signs your AAB with an app signing key it manages, and your
   uploaded keystore becomes just the "upload key" used to verify it's
   really you submitting updates). This is safer than managing the signing
   key yourself and is what Google recommends for all new apps.
4. Release notes (English US): `Initial release.`
5. Click **Save** → **Review release** — every item must show a green
   checkmark before you can proceed
6. Click **Start rollout to production** → **Rollout**

> This pipeline does **not** click this button for you — production
> rollout is a one-way action you should trigger yourself once you've
> reviewed everything above.

---

## 🖥️ SCREEN 6 — In-App Products *(only appears if this game has IAP)*

> ⚠️ You must upload the AAB to at least **Internal Testing** first before
> creating in-app products. If you haven't, go to Release → Testing →
> Internal testing → Create new release, upload there first.

**Path:** Monetize → Products → In-app products

For each product detected in scan / provided by you:

| # | Product ID | Name | Description | Type | Price |
|---|-----------|------|--------------|------|-------|
| 1 | *(you set this — cannot be changed after creation)* | [name] | [desc] | Consumable/One-time | [price] |

> **Important:** Product IDs are permanent once created. Products must be
> **Activated** to actually work in the running game. You need a **Google
> Payments merchant account** (Setup → Payments profile) to receive payouts
> — set this up before activating products if you haven't already.

---

## 🖥️ SCREEN 7 — Pricing & Distribution

**Path:** Monetize → Pricing & distribution

| Field | Value | Why it matters |
|-------|-------|-----------------|
| App price | `Free/[price]` | See the Free/Paid warning in Screen 1 |
| Countries | `All countries` or `[list]` | Restricting countries limits install volume but can be useful if payment/legal setup only covers certain regions |
| Contains ads | `[Yes/No]` | Must match what you declared in Screen 3 |

---

## ⏱️ What Happens Next

| Stage | Typical Duration |
|-------|-------------------|
| First submission review | 3–7 days |
| Update review | 1–3 days |

### If it gets rejected — what each reason actually means

| Reason | What it means | Fix |
|--------|----------------|-----|
| Privacy policy not accessible | The URL either 404s or isn't reachable by Google's crawler | Re-check the Firebase URL loads in an incognito browser |
| Missing content rating | The questionnaire wasn't completed/saved | Go back to Screen 3 |
| Misleading metadata | Screenshots/description don't match actual gameplay | Revise description or screenshots to be accurate |
| Target SDK too low | AAB was built against an older API level than required | Return to GAMEBOX-SCAN-FIX |
| **App crashes on launch / "opens but keeps crashing"** | Almost always R8/ProGuard stripping a class an ad SDK or billing library needs in the release build — this is exactly what GAMEBOX-TEST-APK's real-device test is meant to catch beforehand. Note: Google files repeated crash issues under **Spam & Minimum Functionality** policy, not a separate "bug" bucket — repeated occurrences across an account read as a pattern | If this happens despite testing, check whether the *exact* AAB uploaded matches the one built here (not an older cached build), then return to GAMEBOX-SCAN-FIX to verify ProGuard rules again |
| **"App suspended, including all previous versions"** | This specific phrasing means Google considers the issue present since the *first* upload, not a recent regression — almost always a content-level policy (Spam/Repetitive Content/IP), not a code bug. Re-fixing the build will not resolve this. | Open the suspension email for the exact policy name. If Repetitive Content: the app needs genuine content differentiation, not a resubmission. If IP: resolve licensing/naming before any resubmission. Consider the Appeal only if you have a genuine factual disagreement with the classification. |
| Repetitive Content | Google considers this app functionally/visually near-identical to other apps from the same developer account | Not fixable by this pipeline — requires genuinely original art, mechanics, or content per game, not just a new name/icon |
| Policy violation in ads | An ad format/placement violates Play policy (e.g. accidental clicks, ads over system UI) | Review ad SDK mediation settings — see the Ads policy compliance checklist from GAMEBOX-TEST-APK |
| Billing Library version rejected | Below 8.0.0 | Return to GAMEBOX-SCAN-FIX |
| 16 KB page size non-compliance | A native `.so` isn't aligned | Return to GAMEBOX-SCAN-FIX / re-check NDK version |

---

## ✅ Final Checklist

- [ ] AAB uploaded and processed
- [ ] All store listing fields completed
- [ ] Screenshots/icon/feature graphic uploaded
- [ ] Content rating questionnaire completed
- [ ] Data safety form completed
- [ ] Privacy policy URL live and entered
- [ ] In-app products created and activated (if applicable)
- [ ] Release notes added
- [ ] Rollout started (by you, deliberately)

---

## 🎉 GameBox V2.0 Pipeline Complete

| Skill | File |
|-------|------|
| 1. GAMEBOX-ENV | `Reports/_ENV/ENV_report.md` |
| 2. GAMEBOX-SCAN-FIX | `Reports/[GameName]/[GameName]_Report.md` |
| 3. GAMEBOX-TEST-APK | `Reports/[GameName]/[GameName]_Report.md` (appended) |
| 4. GAMEBOX-AAB-PUBLISH | `Reports/[GameName]/[GameName]_Report.md` (appended) + this guide |

Your game is fully prepared. Submission itself is in your hands from here. 🚀
```

---

## AFTER WRITING BOTH OUTPUTS

Tell the user:

> `✅ Version, signing, AAB, privacy policy, and SEO content all done for [GameName].`
> `⚠️ BACK UP YOUR KEYSTORE NOW: ./APK_AAB/[GameName]/[GameName].keystore`
> `Master report updated: ./Reports/[GameName]/[GameName]_Report.md`
> `Full Publish Guide (with explanations for every decision): ./Reports/[GameName]/[GameName]_Publish_Guide.md`
> `🎉 GameBox V2.0 pipeline complete for [GameName].`

---

## Next - If store graphics are missing or undersized run /gamebox-listing-assets, then upload PlayFinal contents per Screens 1-2. Otherwise pipeline complete.



