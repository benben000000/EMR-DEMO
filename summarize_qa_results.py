import json

with open(r'qa_artifacts/detailed_qa_inspection_report.json', 'r', encoding='utf-8') as f:
    report = json.load(f)

print("=== G1 HEALTH EMR PLAYWRIGHT QA AUDIT METRICS ===")
print("Total Views Audited:", report['total_views_tested'])
print("Total Network Requests Recorded:", report['total_network_calls'])
print("Total Console Logs Captured:", report['total_console_logs'])
print("\n" + "="*80)
print(f"{'Module ID':24} | {'Module Name':32} | {'Rows':4} | {'Btns':4} | {'Notes'}")
print("="*80)

for vid, v in report['view_results'].items():
    notes_cnt = len(v.get('critique_notes', []))
    print(f"{v['view_id']:24} | {v['view_name'][:32]:32} | {v['table_rows_rendered']:4} | {v['buttons_found']:4} | {notes_cnt} critiques")
    if notes_cnt > 0:
        for n in v['critique_notes']:
            print(f"   -> [CRITIQUE] {n}")

print("="*80)
