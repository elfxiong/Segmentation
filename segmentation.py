from collections import defaultdict
from starter_code import LCS, MLCS


def read_csv(filename):
    feature_to_word = defaultdict(list)
    all_forms = []
    with open(filename) as file:
        for line in file:
            inflection, fv = line.split(',')

            # ignore any inflection that contains spaces
            if ' ' in inflection:
                continue

            for feature in fv.strip().split(';'):
                feature_to_word[feature].append(inflection)
                all_forms.append(inflection)

    print(all_forms)
    print('lemma: {}\n'.format(MLCS(all_forms)))

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
