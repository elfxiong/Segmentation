import argparse
from itertools import combinations

from feature_combo import get_feature_combi_dict


def get_unprocessed_data(file):
    lst = []
    for line in file:
        inflected_form, lemma, fv = line.split(',')
        # ignore any inflection that contains spaces
        if ' ' in inflected_form or ' ' in lemma or '{' in inflected_form or '?' in inflected_form or '-' in inflected_form:
            continue

        inflected_form = inflected_form.replace('*', '')

        if '(' in inflected_form or '/' in inflected_form:
            continue

        lst.append((inflected_form, lemma, fv))
    return lst


class Model:
    def __init__(self):
        self.all_letters = set()
        self.letter_combinations = None
        self.feature_form_dict = None
        self.MLCS = None

    def get_all_letters(self, data, separate=False):
        for form, lemma, fv in data:
            # convert to lower case
            self.all_letters.update(form.lower())
        # form combinations
        if separate:
            vowels = ['î', 'ü', 'ö', 'a', 'i', 'e', 'û', 'u', 'o', 'ı', 'â']
            consonants = [s for s in self.all_letters if s not in vowels]
            vowels.append('y')
            self.letter_combinations = list(combinations(vowels, 2)) + list(combinations(consonants, 2))
        else:
            self.letter_combinations = list(combinations(self.all_letters, 2))

        print(self.letter_combinations)
        print(len(self.letter_combinations))

    def find_allomorph(self, forms):
        lcs_list = set()
        for a, b in self.letter_combinations:
            # print(a, b)
            archi = '{{{}/{}}}'.format(a, b)
            # a and b are two letters that we assume is the variation
            forms_copy = [form.replace(a, 'Q').replace(b, 'Q') for form in forms]
            # print(forms_copy)
            lcs = self.MLCS(forms_copy)
            if lcs:
                lcs_list.add(lcs.replace('Q', archi))
        return lcs_list


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--contiguous', '-ct', action='store_true',
                        help='use longest_common_substring instead of longest_common_subsequence')
    parser.add_argument('--combo_size', '-cs', help='the size of combination', default=2, type=int)
    parser.add_argument('--separate', '-sp', action='store_true',
                        help='separate vowels from consonants when considering possible variations')

    args = parser.parse_args()
    print('contiguous: {}\ncombo size: {}\nseparate: {}'.format(args.contiguous, args.combo_size, args.separate))

    with open('wik_tur.csv') as file:
        data = get_unprocessed_data(file)

    combi_forms_dict = {}
    for i in range(1, args.combo_size + 1):
        combi_forms_dict.update(get_feature_combi_dict(data, i))
    key_list = [tuple(sorted(tuple(key))) for key in combi_forms_dict.keys()]
    key_list.sort(key=lambda x: (len(x), x))
    print(key_list)
    print(len(key_list))

    m = Model()
    m.get_all_letters(data, separate=args.separate)
    if args.contiguous:
        from helper import m_longest_common_substring as MLCS
    else:
        from helper import m_longest_common_subsequence_3 as MLCS
    m.MLCS = MLCS

    # combi_lcs_list_dict = {}
    # c = 0
    for feature in key_list:
        forms = combi_forms_dict[frozenset(feature)]
        lcs_list = m.find_allomorph(forms)
        # combi_lcs_list_dict[feature] = lcs_list
        # lcs_list = MLCS_2(forms)
        if lcs_list:
            print('{}:\n{}'.format(feature, ','.join(lcs_list)))
            # print(combi_lcs_list_dict)


if __name__ == '__main__':
    main()
