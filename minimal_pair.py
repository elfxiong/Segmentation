# cython: language_level=3
from collections import defaultdict
from difflib import ndiff
from itertools import combinations

from feature_combo import get_unprocessed_data


def defaultdict_of_int():
    return defaultdict(int)


class Segmenter:
    def __init__(self):

        # category/dimension --> list of features
        self.schema = None

        # feature --> category/dimension
        self.reverse_schema = None

        # lemma --> fv -->form
        self.lemma_fv_form_dict = None

        # feature --> morph --> count
        self.feature_morph_count = None

    def produce_possible_morphs_from_minimal_pair(self):
        """Generate a list of possible morphs for each feature by comparing minimal pairs
            input: a dictionary: lemma --> fv --> form
            1. find fv minimal pairs
            2. compute the diff of the forms and append it to the list of possible forms

            For example, V;SG;1 and V;PL;1 is a minimal pair.
            If for a lemma, V;SG;1 is 'blahsg', and V;PL;1 is 'blahpl',
            then 'sg' is added to the list for feature SG, and 'pl' is added to the list for feature PL.
        """

        # feature --> morph --> count
        feature_morph_dict = defaultdict(defaultdict_of_int)

        for lemma, fv_s in self.lemma_fv_form_dict.items():

            # for any pair of fv
            for fv_pair in combinations(fv_s, 2):
                fv1, fv2 = fv_pair
                fv1, fv2 = frozenset(fv1), frozenset(fv2)
                # if fv1 and fv2 is a minimal pair
                if self.differ_by_one_dimension(fv1, fv2):
                    form1 = fv_s[fv1]
                    form2 = fv_s[fv2]

                    delta = list(ndiff(form1, form2))
                    chars_only_in_form2 = ''.join([x[2:] for x in delta if x.startswith('+')])
                    chars_only_in_form1 = ''.join([x[2:] for x in delta if x.startswith('-')])
                    feature1 = fv1 - fv2
                    feature2 = fv2 - fv1
                    # print('{}:{} \t {}: {}'.format(''.join(feature1), chars_only_in_form1, ''.join(feature2),
                    #                                chars_only_in_form2))

                    # count ++
                    if feature1:
                        feature_morph_dict[feature1][chars_only_in_form1] += 1
                    if feature2:
                        feature_morph_dict[feature2][chars_only_in_form2] += 1

        self.feature_morph_count = feature_morph_dict

    def read_unimorph_schema(self, file):
        import csv
        reader = csv.reader(file)

        # a map from dimension to a list of features
        self.schema = defaultdict(list)

        # a map from feature to the dimension the feature belongs to
        self.reverse_schema = {}
        for dimension, gloss, feature in reader:
            # dimension, gloss, feature = line.strip().split(',')
            # for dimension, feature in file:
            self.schema[dimension].append(feature)
            self.reverse_schema[feature] = dimension

        # hardcoded TODO: do it dynamically
        self.reverse_schema['{IPFV/PROG}'] = self.schema['IPFV']
        self.reverse_schema['{IPFV/PFV}'] = self.schema['IPFV']
        self.reverse_schema['{IPFV/PFR}'] = self.schema['IPFV']

    def in_same_dimension(self, feature1, feature2):
        return feature1 == '' or feature2 == '' or self.reverse_schema[feature1] == self.reverse_schema[feature2]

    def differ_by_one_dimension(self, fv1, fv2):
        """
        differ by one dimension == is minimal pair

        V;1;SG and V;2;PL --> False
        V;1;SG;PRS and V;1;SG --> True
        V;1;SG;PRS and V;1;SG;PST --> True
        V;1;SG;PRS and V;1;SG;PRS --> False
        """

        # the features that is in either fv1 or fv2 but NOT both.
        diff = fv1 ^ fv2
        if len(diff) == 1:
            return True
        elif len(diff) == 2:
            feature1, feature2 = list(diff)
            return self.in_same_dimension(feature1, feature2)
        else:
            return False

    def print_feature_morph_prob(self):
        tuple_list = []
        for feature, morph_count_dict in self.feature_morph_count.items():
            tuple_list.extend((''.join(feature), morph, count) for morph, count in morph_count_dict.items())

        # print(tuple_list)
        # import json
        # json.dump(self.feature_morph_count, fp=open('minimal_pair.json', 'w+'))
        # sort by feature and then by freq
        tuple_list.sort(key=lambda tup: (tup[0], -tup[2]))
        tuple_list = ['{},{},{}'.format(feature_set, morph, count) for feature_set, morph, count in tuple_list]
        print('\n'.join(tuple_list))

    def generate_correlation(self):
        # TODO
        pass

    def pickle_feature_morph_prob(self):
        import pickle
        pickle.dump(self.feature_morph_count, file=open('minimal_pair.pickle', 'wb+'))

    def unpickle_feature_morph_prob(self):
        import pickle
        self.feature_morph_count = pickle.load(file=open('minimal_pair.pickle'))


def main():
    segmenter = Segmenter()

    with open('data/universal_features.csv') as file:
        segmenter.read_unimorph_schema(file)

    # print(segmenter.differ_by_one_dimension(('V', 'SG', 'PRS'), ('V', 'SG', 'PST')))

    with open('data/wik_tur.csv') as file:
        data = get_unprocessed_data(file)

    # lemma --> fv -->form
    lemma_fv_form_dict = defaultdict(dict)

    for form, lemma, fv in data:
        feature_frozenset = frozenset(fv.split(';'))
        lemma_fv_form_dict[lemma][feature_frozenset] = form

    segmenter.lemma_fv_form_dict = lemma_fv_form_dict

    segmenter.produce_possible_morphs_from_minimal_pair()

    segmenter.print_feature_morph_prob()

    segmenter.pickle_feature_morph_prob()

    segmenter.generate_correlation()


if __name__ == '__main__':
    main()
