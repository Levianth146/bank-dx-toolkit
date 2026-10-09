"""Tải tài liệu theo config/sources.csv (điền URL thủ công). Chỉ tải dòng có URL.
Cách dùng: python 01_download.py [--force] [--no-robots] [--bank tcb,mb] [--year 2024] [--type bctn,bctc]
Biến môi trường CONTACT: email liên hệ ghi trong User-Agent (nên đặt)."""
import csv, hashlib, os, sys, time, urllib.robotparser, urllib.parse, requests
from common import *

DELAY = 3.0
UA = f"Mozilla/5.0 (academic research; contact: {os.environ.get('CONTACT', 'n/a')})"
force = "--force" in sys.argv
robots_on = "--no-robots" not in sys.argv
_rp = {}

def allowed(url):
    if not robots_on: return True
    host = "{0.scheme}://{0.netloc}".format(urllib.parse.urlparse(url))
    if host not in _rp:
        rp = urllib.robotparser.RobotFileParser(host + "/robots.txt")
        try: rp.read()
        except Exception: rp = None
        _rp[host] = rp
    rp = _rp[host]
    return True if rp is None else rp.can_fetch(UA, url)

man_path = DATA / "raw" / "manifest.csv"
rows = list(csv.DictReader(open(CONF / "sources.csv", encoding="utf8")))
new = not man_path.exists()
mf = open(man_path, "a", newline="", encoding="utf8"); mw = csv.writer(mf)
if new: mw.writerow(["bank", "year", "doc_type", "url", "file", "sha256", "bytes", "accessed_at", "status"])
pending, pending_opt = [], []
s = requests.Session(); s.headers["User-Agent"] = UA
for r in rows:
    if not keep(r["bank"], r["year"], r["doc_type"]): continue
    url = (r["url"] or "").strip()
    if not url:
        if not (r.get("notes") or "").strip() and r["doc_type"] != "bcptbv": pending.append((r["bank"], r["year"], r["doc_type"]))
        elif not (r.get("notes") or "").strip(): pending_opt.append((r["bank"], r["year"]))
        continue
    dest = DATA / "raw" / r["bank"] / f"{r['year']}_{r['doc_type']}.pdf"
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() and not force:
        print("đã có", dest.name); continue
    if not allowed(url):
        print("robots.txt không cho phép:", url); mw.writerow([*[r[k] for k in ("bank","year","doc_type","url")], "", "", "", today(), "robots_blocked"]); continue
    status = "ok"
    for attempt in range(3):
        try:
            resp = s.get(url, timeout=60)
            resp.raise_for_status()
            if not resp.content.startswith(b"%PDF"):
                status = "not_pdf (kiểm tra link: có thể là trang HTML, hãy mở thủ công lấy link trực tiếp)"
            else:
                dest.write_bytes(resp.content)
            break
        except Exception as e:
            status = f"error: {e}"; time.sleep(2 * (attempt + 1))
    sha = hashlib.sha256(dest.read_bytes()).hexdigest() if dest.exists() else ""
    mw.writerow([r["bank"], r["year"], r["doc_type"], url, str(dest.relative_to(ROOT)), sha, dest.stat().st_size if dest.exists() else 0, today(), status])
    print(r["bank"], r["year"], r["doc_type"], "->", status); time.sleep(DELAY)
mf.close()
if pending:
    print(f"\nCHƯA ĐIỀN: {len(pending)} dòng BCTN/BCTC thiếu cả url lẫn notes (bắt buộc phải có link, hoặc ghi 'không công bố'/'chưa tìm thấy'):")
    for b, y, t in pending[:20]: print("  ", b, y, t)
    if len(pending) > 20: print("   ...")
if pending_opt:
    print(f"\nGợi ý: {len(pending_opt)} dòng BCPTBV chưa có link và chưa có ghi chú. Nếu ESG nằm trong BCTN thì ghi 'tích hợp trong BCTN' vào notes.")
