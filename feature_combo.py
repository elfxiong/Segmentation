"""
Look at multiple features at a time instead of one at a time,
in order to discover LCS that is not present when only treating one feature at a time.

Motivation: sometimes multiple features together determine a single morpheme.
e.g. '3;SG' in English has 's' while neither '3' nor 'SG' entails the 's'.
"""

from collections import defaultdict
from itertools import combinations
from helper import m_longest_common_subsequence_3 as MLCS
from helper import powerset, subtract


def get_unprocessed_data(file):
    """ Read the csv file without doing any processing of the data
    Input: csv file formatted as [inflected form],[lemma],[feature1;feature2;...]
    Output: A list of tuples. The tuple is formatted as (inflected_form, lemma, feature_vector)
    """
    lst = []
    for line in file:
        inflected_form, lemma, fv = line.split(',')
        # ignore any inflection that contains spaces
        if ' ' in inflected_form or ' ' in lemma or '{' in inflected_form or '?' in inflected_form or '-' in inflected_form:
            continue

        inflected_form = inflected_form.replace('*', '')

        if '(' in inflected_form or '/' in inflected_form:
            continue

        lst.append((inflected_form, lemma, fv))
    return lst


def get_feature_combi_dict(tup_list, n):
    """Return a dictionary where each key value pair is defined as:
    key: a set of feature (the size of the set is n)
    value: a list of forms that has the same set of feature

    For example, if a form has features {a,b,c,d} and n is 3, then this form is appended to four lists - the list with {a,b,c} as the key, the list with {a,b,d} as the key etc..
    """
    feature_pair_count = defaultdict(list)
    for inflected_form, lemma, fv in tup_list:
        fvs = fv.strip().split(';')
        # print(len(list(combinations(fvs, r=2))))
        for pair in combinations(fvs, r=n):
            feature_pair_count[frozenset(pair)].append(inflected_form)

    return feature_pair_count


def main():
    with open('wik_tur.csv') as file:
        data = get_unprocessed_data(file)

    combi_forms_dict = {}
    # from 1 to 4
    for i in range(1, 5):
        combi_forms_dict.update(get_feature_combi_dict(data, i))

    print('computing lcs')
    combi_lcs_dict = {}
    combi_count_dict = {}
    for features, forms in combi_forms_dict.items():
        lcs = MLCS(forms)
        count = len(forms)
        if lcs:
            combi_lcs_dict[features] = lcs
            combi_count_dict[features] = count
    del combi_forms_dict

    print('refining lcs')
    results = []
    for features, lcs in combi_lcs_dict.items():
        # remove parts that is already been accounted for in any subset of the features
        # for example, if features {a;b;c} has lcs 'abc',
        # and features {a;b} has lcs 'ab', and each of other subsets of {a;b;c} do not have a lcs
        # then the 'ab' is subtracted from 'abc' so that 'c' is what {a;b;c} contribute as a whole means
        for feature_subset in powerset(features):
            feature_subset = frozenset(feature_subset)
            if feature_subset != features and feature_subset in combi_lcs_dict.keys():
                lcs = subtract(lcs, combi_lcs_dict[feature_subset])
        if lcs:
            results.append((features, ''.join(lcs), combi_count_dict[features]))

    for_print = sorted(results, key=lambda x: (len(x[0]), sorted(list(x[0])), - x[2]))
    with open('combi.csv', 'w+') as file:
        for features, lcs, count in for_print:
            print(';'.join(sorted(features)), lcs, str(count), file=file, sep=',')


if __name__ == '__main__':
    main()
