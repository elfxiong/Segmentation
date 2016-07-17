from collections import defaultdict
from itertools import combinations, chain

from segmentation import get_unprocessed_data
from starter_code import MLCS_2


def powerset(iterable):
    """powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"""
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s) + 1))


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


def subtract(x, y):
    """x - y"""
    return [item for item in x if item not in y]


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
        lcs = MLCS_2(forms)
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
