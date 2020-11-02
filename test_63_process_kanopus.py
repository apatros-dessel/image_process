from geodata import *

txt_in = r''

tmpt_id = '^[fr0-9_]*KV\d_.*[LNBF0-9]$'

tmpt_pan = '^[fr0-9_]*KV\d_.*_PSS1_.*_\d{5}'
tmpt_ms = '^[fr0-9_]*KV\d_.*_S_.*_\d{5}'
tmpt_pan = '^[fr0-9_]*KV\d_.*_PSS4_.*_\d{5}'

tmpt_rgb = '^[fr0-9_]*KV\d_.*.RGB'
tmpt_rgb = '^[fr0-9_]*KV\d_.*.QL'
tmpt_ref = '^[fr0-9_]*KV\d_.*.REF'

rsp_source_tmpt = r'.*RP.+PMS.L2[^\.]*$'
rsp_grn_tmpt = r'RP.+PMS.L2\..{0,3}\d{8}$'
rsp_rgb_tmpt = r'.*RP.+PMS.L2\..*\d*\.?RGB$'
rsp_ql_tmpt = r'.*RP.+PMS.L2\..*\.?QL$'
rsp_id_tmpt = r'RP.+PMS.L2'

files = open(txt_in).read().split('\n')
names = flist(files, lambda x: split3(x)[1])

result = {}

for file in files:
    f,n,e = split3(file)
    if re.search(tmpt_id,n):
        id = n.split('REF')[0].replace('PSS1','S').replace('PSS4','S')
        if id in result:
            get_date_from_string()
        else:
            result[id][type].append(file)
