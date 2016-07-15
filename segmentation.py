from collections import defaultdict
from starter_code import LCS, MLCS, compare_str_lcs


def produce_dicts(file):
    # dict[lemma] == [form1, form2, ...]
    lemma_forms_dict = defaultdict(list)
    for line in file:
        inflected_form, lemma, fv = line.split(',')
        if ' ' in inflected_form or ' ' in lemma:
            continue
        lemma_forms_dict[lemma].append(inflected_form)

    # dict[lemma] == lcs_of_all_its_forms
    lemma_lcs_dict = {}
    for word, forms in lemma_forms_dict.items():
        lemma_lcs_dict[word] = MLCS(forms)

    print(lemma_lcs_dict)

    # dict[feature][stem] == [form1, form2, ...]
    feature_dict = defaultdict(lambda: defaultdict(list))
    file.seek(0)
    for line in file:
        inflected_form, lemma, fv = line.split(',')

        # ignore any inflection that contains spaces
        if ' ' in inflected_form or ' ' in lemma:
            continue
        stem = lemma_lcs_dict[lemma]
        for feature in fv.strip().split(';'):
            feature_dict[feature][stem].append(inflected_form)
    return feature_dict, lemma_forms_dict


def read_csv(filename):
    with open(filename) as file:
        feature_lemma_forms_dict, lemma_forms_dict = produce_dicts(file)

    print(feature_lemma_forms_dict)
    # for feature, lemmas in feature_lemma_forms_dict.items():
    #     all_forms = set()  # all words with this feature
    #     for lemma, forms in lemmas.items():
    #         all_forms.update(forms)
    #         # lcs = MLCS(all_forms)
    #     print('{}'.format(feature))


def main():
    read_csv('test_tur.csv')


if __name__ == '__main__':
    main()
