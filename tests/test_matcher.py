from softmatch.processing import reverse_complement, find_matches

def test_reverse_complement():
    assert reverse_complement("ATCG") == "CGAT"
    assert reverse_complement("atcg") == "cgat"
    assert reverse_complement("GATTACA") == "TGTAATC"
    assert reverse_complement("N") == "N"
    print("test_reverse_complement passed")

def test_find_matches():
    queries = [{'name': 'Adapter1', 'seq': 'ATCG'}]
    read = "NNNNATCGNNNNCGATNNNN"
    hits = find_matches(read, queries, 0)
    assert len(hits) == 2
    assert hits[0]['strand'] == 1
    assert hits[0]['start'] == 4
    assert hits[1]['strand'] == -1
    assert hits[1]['start'] == 12
    print("test_find_matches passed")

if __name__ == "__main__":
    test_reverse_complement()
    test_find_matches()
