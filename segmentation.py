from collections import defaultdict
from starter_code import LCS, MLCS, compare_str_lcs


def produce_dicts(file):
    # feature_dict[feature][lemma] = [form1, form2, ...]
    feature_dict = defaultdict(lambda: defaultdict(list))

    # lemma_dict[lemma] = [form1, form2, ...]
    lemma_dict = defaultdict(list)
    for line in file:
        inflected_form, lemma, fv = line.split(',')

        # ignore any inflection that contains spaces
        if ' ' in inflected_form or ' ' in lemma:
            continue

        for feature in fv.strip().split(';'):
            feature_dict[feature][lemma].append(inflected_form)
            lemma_dict[lemma].append(inflected_form)
    return feature_dict, lemma_dict


def read_csv(filename):
    with open(filename) as file:
        feature_lemma_forms_dict, lemma_forms_dict = produce_dicts(file)

    for feature, lemmas in feature_lemma_forms_dict.items():
        all_forms = set()  # all words with this feature
        for lemma, forms in lemmas.items():
            all_forms.update(forms)
        # lcs = MLCS(all_forms)
        # print('{}: {}'.format(feature, lcs))


def main():
    read_csv('test_tur.csv')


if __name__ == '__main__':
    main()
