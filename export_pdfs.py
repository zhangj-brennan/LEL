"""Export the letter-size Figure PDFs with print-specific CSS.

Usage (run from this folder):
    python3 export_pdfs.py 0.87 0.83 . figure1 figure2 figure3

Args: <figure2 zoom> <figure1 zoom> <output dir> <figure names...>
Writes <output dir>/<name>_letter.pdf and prints the page count for each.
The HTML pages are not modified; print CSS is injected into a temp copy.
"""
import os, re, subprocess, sys, tempfile
C = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
S = tempfile.mkdtemp(prefix="figpdf_")
pub = os.getcwd()
Z2 = float(sys.argv[1])            # figure 2 zoom sets the header size for all
cfg = {  # name: (zoom, margin, extra css)
  "figure1": (float(sys.argv[2]), "0.25in 0.25in 0.15in", ".phase{margin-top:10px!important} .step{padding:7px 0!important} .footnote{line-height:1.15!important} .footnote p{margin:0 0 2px!important} body{padding:0!important} #container,.grants-section,.footnote,.figure-label,#title,.lifecycle{max-width:none!important}"),
  "figure2": (Z2, "0.25in 0.25in 0.15in", ".node.ojp .offices > li .office-header,.office-name{line-height:1.2!important} .office-name{display:block!important;margin-top:2px} .tree{padding-bottom:4px!important} .grants-title{text-transform:none!important;margin-bottom:5px!important} .grants-section{margin-top:20px!important} .footnote{line-height:1.15!important} .footnote p{margin:0 0 2px!important} body{padding:0!important} #container,.grants-section,.footnote,.figure-label,#title,.lifecycle{max-width:none!important}"),
  "figure3": (1.0, "0.3in", ".op-appropriations{margin-top:16px!important;margin-bottom:16px!important} .op-journey{margin-top:0!important;margin-bottom:12px!important} .op-timeline{margin-top:0!important} .op-intro-row{margin-top:4px!important} .op-challenges-row{margin-top:14px!important} .op-timeline{margin-left:30px!important;margin-right:30px!important} .op-step{border-top-width:1.66px!important;padding-left:10px!important;padding-right:10px!important} body{padding-bottom:0!important} .op-approp-list{max-width:300px!important} .op-step-header > div:not(.op-step-number){display:flex!important;align-items:baseline;gap:10px} .op-duration{display:inline!important;margin:0!important} .footnote{line-height:1.15!important;margin-top:16px!important} .footnote p{margin:0 0 2px!important} .op-step-number{width:19.92px!important;height:19.92px!important;font-size:9.96px!important} #container h2{text-transform:none!important} .op-step,.op-intro-row,.op-challenges-row,li{break-inside:avoid} .op-challenges ul,.op-changes ul{line-height:1.4!important}"),
}
# fixed print sizes in pt, per figure
PT = {"figure1": {".phase-title": 10, ".step-content h3": 10, ".step-content p": 8},
      "figure2": {".node.top .dept": 16, ".node.top .grantmaking": 12, ".node-header strong": 12,
                  ".node .name": 10, ".office-header": 10, ".office-name": 8, ".node p": 10,
                  ".node .placeholder-list li": 10, ".grant-card h3": 10, ".grant-card p": 10, ".footnote": 12*0.83*0.75},
      "figure3": {".op-intro p": 8, ".op-appropriations p": 8, ".op-approp-list": 8, ".op-duration": 8, ".op-step-header h3": 10, ".op-step > p:not(.op-friction)": 8, ".op-friction": 8, ".op-reports li": 8, ".footnote": 12*0.83*0.75}}
def glue(m):
    # avoid a last line of one word, or of two short words: join the tail with nbsp
    words = m.group(3).split(" ")
    if len(words) >= 4:
        n = 3 if len(words) >= 6 and len(words[-1]) + len(words[-2]) < 14 and len(" ".join(words[-3:])) <= 20 else 2
        words = words[:-n] + ["&nbsp;".join(words[-n:])]
    return m.group(1) + " ".join(words) + m.group(4)
out_dir = sys.argv[3]
for name in sys.argv[4:]:
    z, m, extra = cfg[name]
    k = Z2 / z
    css = (f"@page{{size:letter;margin:{m}}} html{{zoom:{z}}} {extra} "
           f".figure-label{{font-size:{(10/0.75-1)/z:.3f}px!important}} h1{{font-size:{14/0.75/z:.3f}px!important}} #title{{border-top-width:{3/z:.3f}px!important}} .deck{{font-size:{10/0.75/z:.3f}px!important}}")
    css += "".join(f" {sel}{{font-size:{pt/0.75/z:.3f}px!important}}" for sel, pt in PT.get(name, {}).items())
    if name == "figure2":
        css += f" .node.top .grantmaking{{display:block!important;margin-top:{-5/z:.3f}px!important}} .node-header strong{{padding-top:{4+4/z:.3f}px!important}}"
    if name == "figure1":
        css += f" .lifecycle{{margin-left:{45/z:.3f}px!important;margin-right:{45/z:.3f}px!important}} .footnote{{margin-top:{28+10/z:.3f}px!important}} .deck{{margin-bottom:{8+10/z:.3f}px!important}} .step-content p{{margin-right:{30/z:.3f}px!important}}"
    css += " h2,h3{text-wrap:balance}"
    h = open(f"{name}.html").read().replace("<head>", f'<head><base href="file://{pub}/"><style>{css}</style>', 1)
    # keep the last three words of each paragraph/list item together (no 1-2 word last lines)
    h = re.sub(r'(<(p|li)\b[^>]*>)([^<]*)(</\2>)', glue, h)
    h = h.replace("Help Applicants Like Officer P", "Help Applicants<br>Like Officer P")
    tmp = f"{S}/{name}_tmp.html"; open(tmp, "w").write(h)
    pdf = f"{out_dir}/{name}_letter.pdf"
    subprocess.run([C, "--headless", "--disable-gpu", "--no-pdf-header-footer", f"--print-to-pdf={pdf}", f"file://{tmp}"], capture_output=True)
    n = len(re.findall(rb"/Type\s*/Page[^s]", open(pdf, "rb").read()))
    print(name, z, "pages:", n)
