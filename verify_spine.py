import zipfile, re, glob, os
for p in sorted(glob.glob(r"D:\empty\KDP-POLISHED\EPUB\*.epub")):
    z = zipfile.ZipFile(p)
    opf = z.read("OEBPS/content.opf").decode()
    spine_ids = re.findall(r'idref="([^"]+)"', opf.split("<spine")[1].split("</spine>")[0])
    manifest_ids = re.findall(r'<item id="([^"]+)"', opf)
    ok = all(s in manifest_ids for s in spine_ids)
    print(os.path.basename(p)[:48].ljust(50), "spine ok:", ok, f"({len(spine_ids)} refs)")
