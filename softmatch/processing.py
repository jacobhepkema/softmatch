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

def reverse_complement(seq):
    complement = {'A': 'T', 'C': 'G', 'G': 'C', 'T': 'A', 'N': 'N',
                  'a': 't', 'c': 'g', 'g': 'c', 't': 'a', 'n': 'n'}
    return "".join(complement.get(base, base) for base in reversed(seq))

def find_matches(read_seq, queries, max_errors):
    """
    Uses regex fuzzy matching to find adapters.
    Returns list of hits.
    """
    hits = []
    for q in queries:
        # Forward strand
        fwd_pattern = f"({q['seq']}){{e<={max_errors}}}"
        matches = regex.finditer(fwd_pattern, read_seq, regex.BESTMATCH)
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
        rev_seq = reverse_complement(q['seq'])
        if rev_seq == q['seq']:
            continue # Avoid duplicate hits for palindromes

        rev_pattern = f"({rev_seq}){{e<={max_errors}}}"
        matches = regex.finditer(rev_pattern, read_seq, regex.BESTMATCH)
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
