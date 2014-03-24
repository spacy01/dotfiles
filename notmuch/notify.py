#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from gi.repository import Notify
import notmuch
import sys

markup_cnt  = '[<span foreground="#93e0e3">{0}</span>]'
markup_from = '<span foreground="#ffeece">{0}</span>'
markup_subj = '<b>{0}</b>'
markup_tags = '<i>(<span foreground="#9fc59f">{0}</span>)</i>'

MAX_FROM_LEN = 35
MAX_SUBJ_LEN = 70

db = notmuch.Database(mode=notmuch.Database.MODE.READ_ONLY)
q = notmuch.Query(db, "(tag:unread or tag:todo) and not tag:spam")
q.set_sort(notmuch.Query.SORT.OLDEST_FIRST)

# Read data about the new messages
tab = []
msgs, threads_total = 0, 0
mlc, mlf, mls = 0, 0, 0
for thr in q.search_threads():
    from_ = thr.get_authors()
    subj_ = thr.get_subject() or "(no subject)"
    tags = list(thr.get_tags())
    threads_total += 1
    if "unread" not in tags:
        continue

    from_ = from_.split(u"|", 1)[0]

    lf = len(from_)
    if lf > MAX_FROM_LEN:
        from_ = from_[:MAX_FROM_LEN] + u"…"
        lf = len(from_)
    if lf > mlf:
        mlf = lf

    ls = len(subj_)
    if ls > MAX_SUBJ_LEN:
        subj_ = subj_[:MAX_SUBJ_LEN] + u"…"
        ls = len(subj_)
    if ls > mls:
        mls = ls

    from_ = from_.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    subj_ = subj_.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    tags = [tag.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;') for tag in tags]
    tags = ["<b>"+tag+"</b>" if tag in ("unread", "todo") else tag for tag in tags]
    tags = " ".join(tags)

    count = thr.get_matched_messages()
    msgs += count
    count = markup_cnt.format(count)
    lc = len(count)
    if lc > mlc:
        mlc = lc

    from_ = markup_from.format(from_)
    subj_ = markup_subj.format(subj_)
    tags = markup_tags.format(tags)
    tab.append((count, from_, subj_, tags, lc, lf, ls))

if len(tab) == 0 and threads_total == 0:
    sys.exit(0)

# Format a table
txt = []
for c, f, s, t, lc, lf, ls in tab:
    c += " " * (mlc-lc)
    f += " " * (mlf-lf)
    s += " " * (mls-ls)
    line = "{0} {1}  {2}  {3}".format(c, f, s, t)
    txt.append(line)
txt = '<span font_desc="DejaVu Sans Mono 7.5">' + "\n".join(txt) + '</span>'

# Display a notification
Notify.init("notmuch notify")
summary = "{0} threads, including {1} unread threads ({2} messages)".format(threads_total, len(tab), msgs)
n = Notify.Notification.new(summary, txt, "/usr/share/emacs/site-lisp/notmuch-logo.png")
n.set_timeout(10000)
n.set_category("email.arrived")
n.show()
