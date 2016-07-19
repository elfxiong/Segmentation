from collections import defaultdict

from feature_combo import get_unprocessed_data
from helper import powerset


class Segmenter():
    """This class is used as a container of variables and methods, in order to avoid using global var"""

    def __init__(self):
        self.feature_morpheme_dict = None

    def attempt_segment(self, form, features):
        recognized_morph = set()
        for feature_set in powerset(features):
            feature_set = frozenset(feature_set)
            if feature_set in self.feature_morpheme_dict:
                recognized_morph.update(self.feature_morpheme_dict[feature_set])

        # sort and prioritize long morphs
        recognized_morph = list(recognized_morph)
        recognized_morph.sort(key=lambda x: len(x), reverse=True)
        for morph in recognized_morph:
            form = form.replace(morph, '{{{}}}'.format(morph))
        return form


def main():
    with open('data/wik_tur_N_only.csv') as file:
        data = get_unprocessed_data(file)

    segmenter = Segmenter()

    d = defaultdict(list)
    with open('data/tur_N_affix_list.csv') as file:
        for line in file:
            print(line)
            features, segment = line.strip().split(',')
            if segment:
                d[frozenset(features.split(';'))].append(segment)
    segmenter.feature_morpheme_dict = d

    for inflected_form, lemma, features in data:
        features = features.split(';')
        segmented_form = segmenter.attempt_segment(inflected_form, features)
        print(inflected_form, segmented_form, lemma, features, sep=',')


if __name__ == '__main__':
    main()
