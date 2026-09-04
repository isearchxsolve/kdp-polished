import zipfile, re, glob, os
ok = True
for p in sorted(glob.glob(r"D:\empty\KDP-POLISHED\*.docx")):
    z = zipfile.ZipFile(p)
    xml = z.read("word/document.xml").decode("utf-8")
    settings = z.read("word/settings.xml").decode("utf-8")
    has_field = 'fldCharType="begin"' in xml and re.search(r"<w:instrText[^>]*>[^<]*TOC", xml)
    has_dirty = 'w:dirty="true"' in xml
    has_update = "updateFields" in settings
    links = len(re.findall(r'<w:hyperlink [^>]*w:anchor="toc_', xml))
    status = "OK" if (has_field and has_dirty and has_update and links > 0) else "FAIL"
    if status == "FAIL": ok = False
    print(os.path.basename(p)[:50].ljust(52), status, "| field:", bool(has_field),
          "| dirty:", has_dirty, "| updateFields:", has_update, "| links:", links)
print("\nALL SEVEN PASS" if ok else "\nSOMETHING FAILED")
