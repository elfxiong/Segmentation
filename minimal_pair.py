from collections import defaultdict
from itertools import combinations

from feature_combo import get_unprocessed_data


class Segmenter:
    def __init__(self):
        self.schema = None
        self.reverse_schema = None
        self.data = None

    def generate_minimal_pairs(self, lemma_fv_dict):
        # input:
        # lemma_fv_dict[lemma][fv] --> forms

        for lemma, fv_s in lemma_fv_dict:

            # for any pair of fv
            for fv_pair in combinations(fv_s, 2):
                fv1, fv2 = fv_pair

                # if fv1 and fv2 is a minimal pair
                if self.differ_by_one_dimension(fv1, fv2):
                    # TODO take the delta
                    pass

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

    def in_same_dimension(self, feature1, feature2):
        return feature1 == '' or feature2 == '' or self.reverse_schema[feature1] == self.reverse_schema[feature2]

    def differ_by_one_dimension(self, fv1, fv2):
        """
        differ by one dimension == is minimal pair

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

    print(segmenter.differ_by_one_dimension(('V', 'SG', 'PRS'), ('V', 'SG', 'PST')))
    # with open('data/tur_wik.csv') as file:
    #     segmenter.data = get_unprocessed_data(file)


if __name__ == '__main__':
    main()
