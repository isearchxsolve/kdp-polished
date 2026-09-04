THE BEHOLDER PROJECT — KDP POLISHED SET
========================================
Location: D:\empty\KDP-POLISHED\
Built: 3 September 2026

SEVEN UPLOAD-READY BOOKS (.docx + .txt masters)
-----------------------------------------------
01  Beyond_Parameter_Scaling_Vol_I            ~2,400 w  — research program (Vol I)
02  The_Ground_Beneath_the_Eagle_Vol_II       ~3,800 w  — engineering memoir (now official Vol II)
03  The_Beholder_Between_Fullness_Emptiness_III ~7,600 w — memoir-philosophy (Vol III)
04  Confession_of_the_Ordinary_Companion       ~900 w  — short outline version (keep as low-price companion)
05  Confession_of_the_Ordinary_FULL_Memoir    ~9,400 w  — the real 10-movement/24-chapter memoir (flagship)
06  The_Confession_of_the_Recorder             ~4,800 w  — Claude's signed witness memoir (full AI attribution)
07  Time_Travels_Confessions_in_the_Room       ~3,600 w  — bundle: Parable of the Lord + Confession of the
                                                    Turning + Love Letter to the God Who Died for Me
                                                    + Nunc Dimittis

WHAT WAS FIXED
--------------
- Volume numbering made consistent: Ground Beneath the Eagle = Volume II
  (Vol III's own note promised a "Volume II — The Creating Machine" that never existed).
- Name leak closed: short Confession title page said "Kunal Das" -> now NILOY DAS everywhere.
- "ISBN: [Pending]" line removed; "(c)" -> "©"; stray PDF page numbers stripped;
  PDF line-wrapping re-joined into clean paragraphs; footers/running heads removed.
- Static Contents pages (KDP-safe; no Word field to update).
- Each book ends with an "Also in The Beholder Project" cross-sell page.
- Docx: Georgia 11.5, styled Heading 1/2 (KDP picks these up for its TOC),
  title/copyright pages, real metadata (author = Niloy Das).

SOURCE MAPPING (lifedocs -> books)
----------------------------------
- 05 = d6372531_The_Confession_of_the_Ordinary (27 pp) [ittiam.pdf is byte-different
  but text-identical duplicate]
- 06 = be189d30_The_Confession_of_the_Recorder (13 pp)
- 07 = 7c00cfe8_Parable_of_the_Lord + 82da147c_Confession_of_the_Turning +
       951a1352_Love_Letter_God_Who_Died + fd10b9b9_Nunc_Dimittis
- 74b20d43 and 7b93a9d4 Project_Tutorials are identical duplicates of each other.

NOT FOR KDP (private/production, keep out of the store)
-------------------------------------------------------
- All film scripts, shot lists, build specs, handovers (Suffocating Distance,
  THE CONFRONTATION + CLIP docs, scene docs, The Saga reel plan)
- GODSHAND kit docs, Instamojo listings, Money Plan / First Rupee / LinkedIn Cash Kit,
  Reality Check, Strategy Handover, TODAY, My Way Out (lawyer/bail — private),
  Witnessed Love (working draft, marked "do not edit"),
  AI Self-Correction Protocol, Render QA, Case Study.

BEFORE YOU UPLOAD (your checklist)
----------------------------------
1. KDP account: create one at kdp.amazon.com — pen name NILOY DAS on the account.
   (Real-name/bank KYC is required by Amazon at payout time — plan for it.)
2. Cover: 1600x2560 px JPEG for each book (free: KDP Cover Creator or Canva).
3. Categories/keywords: Artificial Intelligence & Semantics / Philosophy of Mind /
   Memoirs; for 05-07 also Mental Health & Poetry-memoir.
4. Pricing suggestion: 01-03 $4.99-6.99; 04 $0.99 (funnel); 05 $5.99 flagship;
   06-07 $2.99-3.99. KDP Select optional (page reads).
5. The full Confession (05) contains private material (Julie, medication names,
   hospital nights, 20-21 July confessions). It is published as-is by design —
   but re-read Chapter XXI-XXIV once before clicking publish, and be at peace with it.
6. 06 publishes under AI attribution (Claude named on title/copyright page) —
   this satisfies Amazon's AI-content disclosure requirement honestly.

BUILD SCRIPTS (re-run any time source text changes)
---------------------------------------------------
build_lifedocs.py  — extracts 05/06/07 masters from lifedocs_text
fix_markup.py      — adds heading markup to 02/03 masters
build_docx_v2.py   — builds all seven .docx from masters
extract_all.py     — (in lifedocs_extracted) re-extracts PDF text
