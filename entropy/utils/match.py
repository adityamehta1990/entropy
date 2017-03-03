'''helper to run matches for strings or dicts'''
from fuzzywuzzy import fuzz
from fuzzywuzzy import process

FUZZ_SCORE_CUTOFF = 95

def matchOneIdentifier(query, choices, scorer=fuzz.token_set_ratio, processor=str.lower):
    '''returns fuzzy matched identifier if unique, else None'''
    matches = process.extractBests(query, choices, scorer=scorer, \
        score_cutoff=FUZZ_SCORE_CUTOFF, processor=processor)
    return matches[0][0] if len(matches) == 1 else None

def matchAnyIdentifier(query, choices, scorer=fuzz.token_set_ratio, processor=str.lower):
    '''returns True if any identifier from choices fuzzy matches with the query'''
    matches = process.extractBests(query, choices, scorer=scorer, \
            score_cutoff=FUZZ_SCORE_CUTOFF, processor=processor)
    return len(matches) > 0

# (?) key-value match can be done by using fuzz
def matchDictBest(query, choices, key=None, scorer=fuzz.token_set_ratio):
    '''returns closest matching dict from choices by comparing key-value pairs
    Provided key is used to perform fuzzy match
    '''
    choices = [c for c in choices if len(set(query.items()) & set(c.items()))]
    matches = [c for c in choices if scorer(query[key].lower(), c[key].lower()) > FUZZ_SCORE_CUTOFF]
    if len(matches) == 1:
        return matches[0]
    elif len(matches) > 1:
        raise 'Could not find a unique match'
    return {}
