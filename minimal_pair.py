from collections import defaultdict
from difflib import ndiff
from itertools import combinations

from feature_combo import get_unprocessed_data


class Segmenter:
    def __init__(self):

        # category/dimension --> list of features
        self.schema = None

        # feature --> category/dimension
        self.reverse_schema = None

        # lemma --> fv -->form
        self.lemma_fv_form_dict = None

    def generate_minimal_pairs(self):
        # input:
        # lemma_fv_dict[lemma][fv] --> forms

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
                    print('{}:{} \t {}: {}'.format(''.join(feature1), chars_only_in_form1, ''.join(feature2),
                                                   chars_only_in_form2))
                    # print('{},{} --> {}, {}'.format(form1, form2, chars_only_in_form1, chars_only_in_form2))
                    # TODO: store in a dict

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
        diff = frozenset(fv1) ^ frozenset(fv2)
        if len(diff) == 1:
            return True
        elif len(diff) == 2:
            feature1, feature2 = list(diff)
            return self.in_same_dimension(feature1, feature2)
        else:
            return False


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

    segmenter.generate_minimal_pairs()


if __name__ == '__main__':
    main()
