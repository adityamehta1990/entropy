'''helper to run matches for strings or dicts'''
from fuzzywuzzy import fuzz
from fuzzywuzzy import process

FUZZ_SCORE_CUTOFF = 95

def matchOneIdentifier(query, choices, scorer=fuzz.token_set_ratio, processor=None):
    matches = process.extractBests(query, choices, \
        score_cutoff=FUZZ_SCORE_CUTOFF, scorer=scorer, processor=processor)
    return matches[0][0] if len(matches) == 1 else ''

def matchAnyIdentifier(query, choices, scorer=fuzz.token_set_ratio, processor=None):
    matches = process.extract(query, choices, scorer=scorer, processor=processor)
    return len(matches) > 0

# this should find the dict from choices with max matching keys
# key-value match can be done by using fuzz
def matchDictBest(query, choices):
    pass