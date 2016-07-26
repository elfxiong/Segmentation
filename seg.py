import re
from collections import defaultdict

from feature_combo import get_unprocessed_data
from helper import powerset

BRACES = re.compile(r'[{}]')


class Segmenter():
    """This class is used as a container of variables and methods, in order to avoid using global var"""

    def __init__(self):
        self.feature_morpheme_dict = None

    def attempt_segment(self, form, feature_vector):
        # print(type(features))
        recognized_morph = set()

        for feature_set in powerset(feature_vector):
            feature_set = frozenset(feature_set)
            if feature_set in self.feature_morpheme_dict:
                # recognized_morph.update(self.feature_morpheme_dict[feature_set])
                tup_list = [(feature_set, morph) for morph in self.feature_morpheme_dict[feature_set]]
                recognized_morph.update(tup_list)

        feature_vector = set(feature_vector)

        # sort and prioritize long morphs
        recognized_morph = list(recognized_morph)
        recognized_morph.sort(key=lambda x: len(x[1]), reverse=True)
        for feature_set, morph in recognized_morph:

            segments = BRACES.split(form)
            for index, seg in enumerate(segments):
                if index % 2 == 0:  # outside braces
                    segments[index] = seg.replace(morph, '{{{}}}'.format(morph))
                else:  # inside braces
                    segments[index] = "{{{}}}".format(seg)

            # remove found features from the feature vector
            feature_vector -= feature_set
            form = ''.join(segments)

        return form, feature_vector


def main():
    with open('data/wik_tur_N_only.csv', encoding='utf8') as file:
        data = get_unprocessed_data(file)

    segmenter = Segmenter()

    d = defaultdict(list)
    with open('data/tur_N_affix_list.csv', encoding='utf8') as file:
        for line in file:
            # print(line)
            features, segment = line.strip().split(',')
            if segment:
                d[frozenset(features.split(';'))].append(segment)
    segmenter.feature_morpheme_dict = d

    for inflected_form, lemma, features in data:
        features = features.split(';')
        inflection = inflected_form.replace(lemma, "")

        segmented_form, new_feature_set = segmenter.attempt_segment(inflection, features)
        print(inflected_form, segmented_form, lemma, new_feature_set, sep=',')


if __name__ == '__main__':
    main()
