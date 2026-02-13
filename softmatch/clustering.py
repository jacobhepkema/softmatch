def filter_hits(hits):
    """
    Deduplicate overlapping hits.
    Sort by errors (ascending), then by length (descending), then by start.
    Greedily pick non-overlapping hits.
    """
    if not hits:
        return []

    # Sort hits by quality: fewer errors first, then longer hits
    sorted_hits = sorted(hits, key=lambda x: (x['errors'], -x['len'], x['start']))

    picked = []

    for h in sorted_hits:
        overlap = False
        for p in picked:
            # Check for overlap: h starts before p ends AND h ends after p starts
            if h['start'] < p['end'] and h['end'] > p['start']:
                overlap = True
                break
        if not overlap:
            picked.append(h)

    # Sort by start for final output
    return sorted(picked, key=lambda x: x['start'])

def cluster_reads(reads_with_hits):
    """
    Groups reads by their adapter signature and sorts within clusters.
    Returns a dict: { signature: [read_info, ...] }
    """
    clusters = {}
    for read in reads_with_hits:
        hits = filter_hits(read['hits'])

        # Signature is a tuple of (adapter_name, strand)
        signature = tuple((h['name'], h['strand']) for h in hits)

        if signature not in clusters:
            clusters[signature] = []

        # Calculate distances between hits
        distances = []
        for i in range(len(hits) - 1):
            distances.append(hits[i+1]['start'] - hits[i]['end'])

        clusters[signature].append({
            'id': read.get('id', 'unknown'),
            'seq_len': len(read['seq']),
            'hits': hits,
            'distances': tuple(distances)
        })

    # Sort reads within each cluster by distances and then by sequence length
    for sig in clusters:
        clusters[sig].sort(key=lambda x: (x['distances'], x['seq_len']))

    return clusters
