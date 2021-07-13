import os
import re
import argparse
from email import policy
from email.parser import BytesParser

eml_txt = {} # dict of filename:message text

parser = argparse.ArgumentParser()
parser.add_argument('--dir', required=True, help='Path to the file listing of emails.')
args = parser.parse_args()

if not os.path.exists(args.dir):
    print("Directory not found")

for file in os.listdir(args.dir):
    if file.endswith(".eml"): #only testing eml files now
        m = open(os.path.join(args.dir, file), 'rb')
        msg = BytesParser(policy = policy.default).parse(m)
        txt = msg.get_body(preferencelist= 'plain').get_content()
        txt = re.sub("[^a-zA-z0-9]|\\n", "", txt)
        eml_txt[file] = txt
        m.close()

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
        f = open(os.path.join(args.dir, file), 'rb')
        f_msg = BytesParser(policy=policy.default).parse(f)
        for part in f_msg.iter_parts():
            if part.is_attachment():
                att_fname = os.path.join(args.dir, (os.path.splitext(file)[0] + "_" + part.get_filename()))
                content = part.get_content()
                with open(att_fname, 'wb') as w:
                    w.write(content)
                    w.close()
        f.close()
        os.remove(os.path.join(args.dir, file))
