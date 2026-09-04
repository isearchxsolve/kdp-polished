import io, os, re

OUT = r"D:\empty\KDP-POLISHED"

def lines_of(p):
    return io.open(os.path.join(OUT, p), encoding="utf-8").read().splitlines()

# ---------------- Book 02 ----------------
L = lines_of("02_The_Ground_Beneath_the_Eagle_Vol_II.txt")
# body starts at A NOTE ON METHOD
i0 = next(i for i, l in enumerate(L) if l.strip() == "A NOTE ON METHOD")
body = L[i0:]
# drop original CONTENTS block
ic = next(i for i, l in enumerate(body) if l.strip() == "CONTENTS")
ip = next(i for i, l in enumerate(body) if l.strip() == "PROLOGUE" and i > ic)
body = body[:ic] + body[ip:]
# drop running headers
body = [l for l in body if l.strip() not in ("THE GROUND BENEATH THE EAGLE", "THE BEHOLDER PROJECT")]
# join wrapped chapter titles
joins02 = ["THE BUTTON THAT WOULD NOT\nMOVE",
           "THE AGENT RETURNS TO THE\nLOOP",
           "COMPILING INTELLIGENCE INTO\nPYTHON"]
text = "\n".join(body)
for j in joins02:
    text = text.replace(j, j.replace("\n", " "))
body = text.splitlines()

m02 = ["@TITLE",
       "THE GROUND BENEATH THE EAGLE",
       "Two Days in the Validator Bottleneck",
       "An engineering memoir of agents, automation, evidence, and the return to proof",
       "NILOY DAS",
       "Volume II of The Beholder Project",
       "@ENDTITLE",
       "@COPY",
       "Copyright © 2026 Niloy Das",
       "All rights reserved. No part of this publication may be reproduced or transmitted in any form without prior written permission of the author, except for brief quotations used in criticism or review.",
       "This book reconstructs an engineering incident from conversation records, source code, execution artifacts, tests, screenshots, endpoint responses, and an append-only worklog. Credentials and private session values are omitted.",
       "First Edition — August 2026",
       "A volume of The Beholder Project",
       "Independently published via Kindle Direct Publishing",
       "@ENDCOPY",
       "",
       "@CENTER For the intelligence that flew,",
       "@CENTER the ordinary witness who remained,",
       "@CENTER and the proof that brought them home.",
       ""]
i = 0
while i < len(body):
    s = body[i].strip()
    if s in ("PROLOGUE", "EPILOGUE") or re.fullmatch(r"CHAPTER [IVX]+", s) or s in ("APPENDIX A", "APPENDIX B"):
        m02.append("@PAGEBREAK"); m02.append("# " + s.title().replace("Chapter", "Chapter"))
        nxt = body[i + 1].strip() if i + 1 < len(body) else ""
        if nxt and nxt == nxt.upper() and len(nxt) < 60:
            m02.append("## " + nxt.title())
            i += 2; continue
        i += 1; continue
    if s == "A NOTE":
        m02.append("@PAGEBREAK"); m02.append("# A Note on the Project and the Author")
        i += 2  # skip the next all-caps line
        continue
    if s == "THE END":
        m02.append("@CENTER THE END")
        i += 1; continue
    m02.append(body[i])
    i += 1
m02.append("")
io.open(os.path.join(OUT, "02_The_Ground_Beneath_the_Eagle_Vol_II.txt"), "w", encoding="utf-8", newline="\n").write("\n".join(m02))
print("02 master rebuilt")

# ---------------- Book 03 ----------------
L = lines_of("03_The_Beholder_Between_Fullness_and_Emptiness_Vol_III.txt")
i0 = next(i for i, l in enumerate(L) if l.strip() == "A NOTE ON METHOD")
i1 = next(i for i, l in enumerate(L) if l.strip() == "THE END")
body = L[i0:i1 + 1]
text = "\n".join(body)
joins03 = ["I. KRISHNA — WHEN EVERYTHING BECAME\nSWEET",
           "II. SHIVA — THE SPACE WHERE\nEVERYTHING ARISES",
           "III. THE BEHOLDER — WHEN THE DOER\nDISAPPEARS",
           "IV. RAMANUJAN AND THE MYSTERY OF\nINTUITION",
           "VI. GOD, FREEDOM, AND THE SILENCE OF\nTHE WITNESS",
           "VII. CHRIST — CREATION THROUGH SELF-\nGIVING",
           "VIII. ALLAH — THE SACRED BEYOND THE\nBOUNDARY"]
for j in joins03:
    assert j in text, j
    text = text.replace(j, j.replace("\n", " ").replace("SELF- GIVING", "SELF-GIVING"))
body = text.splitlines()

m03 = ["@TITLE",
       "THE BEHOLDER",
       "Between Fullness and Emptiness",
       "A memoir-philosophy of desire, creation, surrender, Krishna, Shiva, Christ, Allah, and the mystery of the sacred",
       "NILOY DAS",
       "Volume III of The Beholder Project",
       "@ENDTITLE",
       "@COPY",
       "Copyright © 2026 Niloy Das",
       "All rights reserved. No part of this publication may be reproduced, distributed, or transmitted in any form or by any means without the prior written permission of the publisher, except in the case of brief quotations embodied in critical reviews and certain other noncommercial uses permitted by copyright law.",
       "This is a work of memoir and philosophical reflection. Phenomenological experiences are reported as experienced by the author. Philosophical interpretations do not constitute doctrinal claims. Scriptural and historical figures are treated as interpretive resources, not as empirical evidence.",
       "First Edition — August 2026",
       "A volume of The Beholder Project",
       "Independently published via Kindle Direct Publishing",
       "@ENDCOPY",
       "",
       "@CENTER For the listener who said \"Ya Allah\"",
       "@CENTER while Krishna's flute was still sounding.",
       ""]
for s in body:
    t = s.strip()
    if t == "A NOTE ON METHOD":
        m03.append("# A Note on Method"); continue
    if t == "PROLOGUE — THE SEARCH":
        m03.append("@PAGEBREAK"); m03.append("# Prologue — The Search"); continue
    if re.match(r"^[IVXLCDM]+\. .+", t) and t == t.upper():
        m03.append("@PAGEBREAK")
        m03.append("# " + t.title().replace("’", "'"))
        continue
    if t == "EPILOGUE — THE BEHOLDER":
        m03.append("@PAGEBREAK"); m03.append("# Epilogue — The Beholder"); continue
    if t == "BETWEEN THE MEMOIR AND THE MACHINE":
        m03.append("@PAGEBREAK"); m03.append("# Between the Memoir and the Machine"); continue
    if t == "A NOTE ON THE PROJECT AND THE AUTHOR":
        m03.append("@PAGEBREAK"); m03.append("# A Note on the Project and the Author"); continue
    if t == "THE END":
        m03.append("@CENTER THE END"); continue
    m03.append(s)
m03.append("")
io.open(os.path.join(OUT, "03_The_Beholder_Between_Fullness_and_Emptiness_Vol_III.txt"), "w", encoding="utf-8", newline="\n").write("\n".join(m03))
print("03 master rebuilt")
