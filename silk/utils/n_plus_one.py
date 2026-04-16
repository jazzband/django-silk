import re

# Only replace single-quoted string *literals* (values).
# Double-quoted identifiers like "table"."column" are kept intact
# so the fingerprint remains human-readable for grouping.
_RE_STRINGS = re.compile(r"'[^']*'")
_RE_NUMBERS = re.compile(r'\b\d+\b')
_RE_WHITESPACE = re.compile(r'\s+')


def fingerprint_query(sql: str) -> str:
    s = _RE_STRINGS.sub('?', sql)
    s = _RE_NUMBERS.sub('?', s)
    return _RE_WHITESPACE.sub(' ', s).strip().lower()


class NPlusOneGroup:
    __slots__ = ('fingerprint', 'queries', 'count', 'representative', 'total_time_taken')

    def __init__(self, fingerprint, queries):
        self.fingerprint = fingerprint
        self.queries = queries
        self.count = len(queries)
        self.representative = queries[0]
        self.total_time_taken = sum(q.time_taken for q in queries)


class NPlusOneResult:
    __slots__ = ('groups', 'flagged_query_ids', 'has_n_plus_one')

    def __init__(self, groups):
        self.groups = groups
        self.flagged_query_ids = {q.pk for g in groups for q in g.queries}
        self.has_n_plus_one = bool(groups)


def detect_n_plus_one(queries, threshold=3) -> NPlusOneResult:
    buckets = {}
    for q in queries:
        buckets.setdefault(fingerprint_query(q.query), []).append(q)
    flagged = [NPlusOneGroup(fp, qs) for fp, qs in buckets.items() if len(qs) >= threshold]
    flagged.sort(key=lambda g: g.count, reverse=True)
    return NPlusOneResult(flagged)
