import csv
import regex

def parse_fastq(filepath):
    """
    Generator that streams FASTQ records to save memory.
    Yields (header, sequence, qual).
    """
    with open(filepath, 'r') as f:
        while True:
            header = f.readline().strip()
            if not header: break
            seq = f.readline().strip()
            f.readline() # Plus line
            qual = f.readline().strip()
            yield header, seq, qual

def parse_queries(filepath):
    """
    Parses CSV: Name,Sequence or just Sequence.
    Returns list of dicts: {'name': str, 'seq': str}
    """
    queries = []
    with open(filepath, 'r') as f:
        # Sniff format
        line = f.readline().strip()
        f.seek(0)

        # Check if CSV has header or simple list
        has_comma = ',' in line
        reader = csv.reader(f)

        idx = 1
        for row in reader:
            if not row: continue
            if len(row) >= 2:
                queries.append({'name': row[0].strip(), 'seq': row[1].strip().upper()})
            elif len(row) == 1:
                # Assign generic name if missing
                queries.append({'name': f"Adapter_{idx}", 'seq': row[0].strip().upper()})
                idx += 1
    return queries

_COMPLEMENT_TRANS = str.maketrans(
    "ATCGNRYKMSWBDHVatcgnrykmswbdhv",
    "TAGCNYRMKSWVHDBtagcnyrmkswvhdb"
)

def reverse_complement(seq):
    return seq.translate(_COMPLEMENT_TRANS)[::-1]

IUPAC_REGEX = {
    'R': '[AG]', 'Y': '[CT]', 'S': '[GC]', 'W': '[AT]',
    'K': '[GT]', 'M': '[AC]', 'B': '[CGT]', 'D': '[AGT]',
    'H': '[ACT]', 'V': '[ACG]', 'N': '[ACGTN]'
}

def expand_ambiguous(seq):
    """
    Expands IUPAC ambiguous bases into regex character classes.
    """
    pattern = ""
    for base in seq:
        pattern += IUPAC_REGEX.get(base, base)
    return pattern

def find_matches(read_seq, queries, max_errors):
    """
    Uses regex fuzzy matching to find adapters.
    Returns list of hits.
    """
    hits = []
    for q in queries:
        # Forward strand
        fwd_re = q.get('fwd_re')
        if fwd_re is None:
            expanded_seq = expand_ambiguous(q['seq'])
            fwd_pattern = f"({expanded_seq}){{e<={max_errors}}}"
            fwd_re = regex.compile(fwd_pattern, regex.BESTMATCH)

        matches = fwd_re.finditer(read_seq)
        for m in matches:
            start, end = m.span()
            errors = sum(m.fuzzy_counts)
            hits.append({
                'name': q['name'],
                'start': start,
                'end': end,
                'len': end - start,
                'errors': errors,
                'match_seq': m.group(),
                'strand': 1
            })

        # Reverse strand
        rev_re = q.get('rev_re')
        if rev_re is None:
            rev_seq = q.get('rev_seq') or reverse_complement(q['seq'])
            if rev_seq == q['seq']:
                continue # Avoid duplicate hits for palindromes

            expanded_rev = expand_ambiguous(rev_seq)
            rev_pattern = f"({expanded_rev}){{e<={max_errors}}}"
            rev_re = regex.compile(rev_pattern, regex.BESTMATCH)

        if rev_re:
            matches = rev_re.finditer(read_seq)
            for m in matches:
                start, end = m.span()
                errors = sum(m.fuzzy_counts)
                hits.append({
                    'name': q['name'],
                    'start': start,
                    'end': end,
                    'len': end - start,
                    'errors': errors,
                    'match_seq': m.group(),
                    'strand': -1
                })

    # Sort hits by start position
    hits.sort(key=lambda x: x['start'])
    return hits
