import argparse
import os
import re
from email import policy
from email.parser import BytesParser
import PyPDF2

eml_txt = {} # dict of filename:message text

parser = argparse.ArgumentParser()
parser.add_argument('--dir', required=True, help='Path to the file listing of emails.')
args = parser.parse_args()

if not os.path.exists(args.dir):
    print("Directory not found")

for file in os.listdir(args.dir):
    if file.endswith(".eml"): #only testing eml files now
        with open(os.path.join(args.dir, file), 'rb') as m:
            msg = BytesParser(policy = policy.default).parse(m)
            txt = msg.get_body(preferencelist= 'plain').get_content()
            txt = re.sub("[^a-zA-z0-9]|\\n", "", txt)
            eml_txt[file] = txt
    elif file.endswith(".pdf"):
        with open(os.path.join(args.dir, file), mode = "rb") as m:
            reader = PyPDF2.PdfFileReader(m)
            n_pg = reader.getNumPages()
            for page in range(n_pg):
                msg = reader.getPage(page)
                txt = msg.extractText()
                if not isinstance(txt, str):
                    continue
                else:
                    txt = re.sub("[^a-zA-z0-9]|\\n", "", txt)
                    if n_pg > 1:
                        filename = os.path.splitext(file)[0] + "_pg" + str(page+1) + ".pdf"
                        eml_txt[filename] = txt
                    else:
                        eml_txt[file] = txt

fn_rm = [] # create list of filenames to be removed
for key in eml_txt:
    txt_to_compare = eml_txt[key]
    comparison = {k: v for k, v in eml_txt.items() if k != key}
    for nkey in comparison:
        if txt_to_compare in comparison[nkey]:
            if key in fn_rm: continue
            else: fn_rm.append(key)
        else: continue

# Remove eml files whose entire text can be found in another email file
# Check for and save attachment(s) before deleting
for file in os.listdir(args.dir):
    if file in fn_rm:
        with open(os.path.join(args.dir, file), 'rb') as f:
            f_msg = BytesParser(policy=policy.default).parse(f)
        for part in f_msg.iter_parts():
            if part.is_attachment():
                att_fname = os.path.join(args.dir, (os.path.splitext(file)[0] + "_" + part.get_filename()))
                content = part.get_content()
                with open(att_fname, 'wb') as w:
                    w.write(content)
        os.remove(os.path.join(args.dir, file))
