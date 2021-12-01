import argparse
import os
import re
from email import policy
from email.parser import BytesParser, HeaderParser
from email.utils import getaddresses

eml_txt = {}  # dict of filename:message text

parser = argparse.ArgumentParser()
parser.add_argument('--dir', required=True, help='Path to the file listing of emails.')
args = parser.parse_args()

if not os.path.exists(args.dir):
    print("Directory not found")

for file in os.listdir(args.dir):
    if file.endswith(".eml"):
        with open(os.path.join(args.dir, file), 'rb') as m:
            msg = BytesParser(policy=policy.default).parse(m)
            txt = msg.get_body(preferencelist='plain').get_content()
            txt = re.sub("[^a-zA-z0-9]|_|\\n", "", txt)
            eml_txt[file] = txt

fn_rm = []  # create list of filenames to be removed
for key in eml_txt:
    txt_to_compare = eml_txt[key]
    comparison = {k: v for k, v in eml_txt.items() if k != key}
    for nkey in comparison:
        if txt_to_compare in comparison[nkey]:
            if key in fn_rm:
                continue
            else:
                # Compare people involved in thread. If new people added, keep as unique email
                name_list = []
                comp_names = []
                with open(os.path.join(args.dir, key), 'r') as h:
                    headers = HeaderParser().parse(h)
                    cc = headers.get_all('cc', [])
                    bcc = headers.get_all('bcc', [])
                    to = headers.get_all('to', [])
                    froms = headers.get_all('from', [])
                    addresses = getaddresses(cc + bcc + to + froms)
                    for tup in addresses:
                        name = tup[0]
                        name_list.append(name)
                with open(os.path.join(args.dir, nkey), 'r') as comp:
                    comp_head = HeaderParser().parse(comp)
                    comp_cc = comp_head.get_all('cc', [])
                    comp_bcc = comp_head.get_all('bcc', [])
                    comp_to = comp_head.get_all('to', [])
                    comp_from = comp_head.get_all('from', [])
                    c_addresses = getaddresses(comp_cc + comp_bcc + comp_to + comp_from)
                    for tup in c_addresses:
                        cname = tup[0]
                        comp_names.append(cname)
                for person in name_list:
                    if person not in comp_names:
                        continue  # If there is a new name, keep the email
                    else:  # compare subject
                        subj = re.sub("^RE:\\s|^FW:\\s", "", headers['Subject'], flags=re.IGNORECASE)
                        comp_subj = re.sub("^RE:\\s|^FW:\\s", "", comp_head['Subject'], flags=re.IGNORECASE)
                        if subj != comp_subj:
                            continue
                        elif key not in fn_rm:  # Only delete if no new persons and no new subject
                            fn_rm.append(key)

# Remove files indicated
# Check for and save attachment(s) before deleting
for file in os.listdir(args.dir):
    if file in fn_rm:
        with open(os.path.join(args.dir, file), 'rb') as f:
            f_msg = BytesParser(policy=policy.default).parse(f)
        for part in f_msg.iter_parts():
            if part.is_attachment():
                newfolder = os.path.join(args.dir, "Attachments")
                if not os.path.exists(newfolder):
                    os.makedirs(newfolder)
                afn = re.sub("[^a-zA-z0-9]|_|\\n", "", part.get_filename())
                att_fname = os.path.join(newfolder, (os.path.splitext(file)[0] + "_" + afn))
                content = part.get_content()
                if part.get_content_type().startswith("text"):
                    with open(att_fname, 'w', encoding='utf-8') as w:
                        w.write(content)
                elif part.get_content_type.startswith("message"):
                    em_att = content.as_bytes()
                    with open(att_fname+".eml", 'wb') as w:
                        w.write(em_att)
                else:
                    with open(att_fname, 'wb') as w:
                        w.write(content)
        os.remove(os.path.join(args.dir, file))
