import zipfile, re, glob, os, xml.etree.ElementTree as ET

ok = True
for ep in sorted(glob.glob(r"D:\empty\KDP-POLISHED\EPUB\*.epub")):
    z = zipfile.ZipFile(ep)
    names = set(z.namelist())
    errs = []
    # mimetype must be first, stored
    if z.namelist()[0] != "mimetype" or z.read("mimetype") != b"application/epub+zip":
        errs.append("mimetype")
    # parse OPF
    opf = z.read("OEBPS/content.opf").decode("utf-8")
    # every manifest href exists
    for m in re.finditer(r'href="([^"]+)"', opf):
        href = m.group(1)
        if href.startswith("http"): continue
        if "OEBPS/" + href not in names:
            errs.append("opf missing: " + href)
    # every spine idref exists in manifest
    opf_root = ET.fromstring(opf)
    NS = {"opf": "http://www.idpf.org/2007/opf"}
    man_ids = {it.get("id") for it in opf_root.iter("{http://www.idpf.org/2007/opf}item")}
    for ir in opf_root.iter("{http://www.idpf.org/2007/opf}itemref"):
        if ir.get("idref") not in man_ids:
            errs.append("spine idref missing: " + ir.get("idref"))
    # every xhtml parses + internal anchors exist
    anchors = {}
    for name in names:
        if name.endswith(".xhtml"):
            xmlt = z.read(name).decode("utf-8")
            try:
                ET.fromstring(xmlt)
            except ET.ParseError as e:
                errs.append(f"XML {name}: {e}")
            ids = set(re.findall(r'id="([^"]+)"', xmlt))
            anchors[name] = ids
    # every internal link in xhtml resolves
    for name in names:
        if name.endswith(".xhtml"):
            xmlt = z.read(name).decode("utf-8")
            base = name.split("/")[-1]
            for href in re.findall(r'<a href="([^"]+)"', xmlt):
                if href.startswith("http"): continue
                tgt, _, frag = href.partition("#")
                tgtfile = "OEBPS/" + tgt if tgt else name
                if tgtfile not in names:
                    errs.append(f"link missing file: {href} in {base}")
                elif frag and frag not in anchors.get(tgtfile, set()):
                    errs.append(f"link missing anchor: {href} in {base}")
    # nav + ncx present
    if "OEBPS/nav.xhtml" not in names: errs.append("no nav.xhtml")
    if "OEBPS/toc.ncx" not in names: errs.append("no toc.ncx")
    # nav parses
    try:
        ET.fromstring(z.read("OEBPS/nav.xhtml"))
        ET.fromstring(z.read("OEBPS/toc.ncx"))
    except ET.ParseError as e:
        errs.append(f"nav/ncx XML: {e}")
    status = "OK" if not errs else "FAIL"
    if errs: ok = False
    print(os.path.basename(ep)[:50].ljust(52), status)
    for e in errs[:5]: print("   -", e)
print("\nALL EPUBS VALID" if ok else "\nERRORS FOUND")
