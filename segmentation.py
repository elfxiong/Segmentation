from collections import defaultdict
from starter_code import LCS, MLCS


def read_csv(filename):
    feature_to_word = defaultdict(list)
    all_forms = []
    with open(filename) as file:
        for line in file:
            inflected_form, lemma, fv = line.split(',')

            # ignore any inflection that contains spaces
            if ' ' in inflected_form:
                continue

            for feature in fv.strip().split(';'):
                feature_to_word[feature].append(inflected_form)
                all_forms.append(inflected_form)

    print(all_forms)

    # first guess of the stem
    stem = MLCS(all_forms)
    print('lemma: {}\n'.format(stem))

    for feature, forms in feature_to_word.items():
        print("{}: {}\n{}\n".format(feature, MLCS(forms), ','.join(forms)))


def print_dict(d):
    print(d.keys())
    for key, value in d.items():
        print("{}: {}".format(key, ', '.join(value)))


def main():
    read_csv('test_tur.csv')


if __name__ == '__main__':
    main()
