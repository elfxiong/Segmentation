from collections import defaultdict
from itertools import combinations

from segmentation import get_unprocessed_data
from starter_code import MLCS_2


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

    combi_dict = get_feature_combi_dict(data, 3)
    for pair, forms in combi_dict.items():
        print(';'.join(sorted(pair)), MLCS_2(forms), sep=',')


if __name__ == '__main__':
    main()
