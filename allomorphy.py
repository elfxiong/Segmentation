"""
"Brute force" way of finding potential allomorphs.

For each feature, gather all the forms that have this feature, do:
for any possible two letters combination, assume there is a allomorphic variation between the two
and try to find the MLCS of the forms.

For example, if a morpheme alternatives between lar/ler, then neither 'lar' nor 'ler' can be found using simple MLCS,
since neither is common among all forms. However, when assuming a/e are the same, l{a/e}r can be found using MLCS.

The brute force part is: each combinations of 2 letters are attempted when trying to find the variation.
Increasing this number to 3 or more is wanted (since variations at a single position is not limited 2 letters)
but painful since the number of combinations of letters increases exponentially if not 'factorially'
(I don't know which is the correct description).
"""
import argparse
from itertools import combinations
from feature_combo import get_unprocessed_data, get_feature_combi_dict


class Model:
    """This class is just used as a container in order to avoid using global variable"""

    def __init__(self):
        self.all_letters = set()
        self.letter_combinations = None
        self.feature_form_dict = None
        self.MLCS = None

    def get_all_letters(self, data, separate=False):
        # get every letter in the data and put it into a set
        for form, lemma, fv in data:
            # convert to lower case
            self.all_letters.update(form.lower())
        print('{} letters: {}'.format(len(self.all_letters), ','.join(self.all_letters)))

        # combinations of letters
        # currently limited to 2 letter combinations TODO increase to 3?
        if separate:  # generate combinations for vowels and consonants separately
            vowels = ['î', 'ü', 'ö', 'a', 'i', 'e', 'û', 'u', 'o', 'ı', 'â']
            consonants = [s for s in self.all_letters if s not in vowels]
            vowels.append('y')
            self.letter_combinations = list(combinations(vowels, 2)) + list(combinations(consonants, 2))
        else:
            self.letter_combinations = list(combinations(self.all_letters, 2))
        print('{} combinations: {}'.format(len(self.letter_combinations), self.letter_combinations))

    def find_allomorph(self, forms):
        """ Find MLCS of the forms.
        For example, if 'n' is the longest substring/sequence that occurs in all forms, then 'n' would be in the output.
        If either 'a' or 'e' occurs in any forms, then {a/e} would be in the output. """
        lcs_list = set()
        for a, b in self.letter_combinations:
        forms = [form.lower() for form in forms]
            # a and b are two letters that we assume is the variation
            # so I pretend they are the same letter
            # (by replace each of them with a char that is not present in the alphabet)
            # and then find MLCS, and then replace them back with {a/b}
            archi = '{{{}/{}}}'.format(a, b)
            forms_copy = [form.replace(a, 'Q').replace(b, 'Q') for form in forms]
            # print(forms_copy)
            lcs = self.MLCS(forms_copy)
            if lcs:
                lcs_list.add(lcs.replace('Q', archi))
        # TODO cleanup the lcs_list because for example, whenever 'n' is in the list, {n/*} is also in the list
        return lcs_list


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--contiguous', '-ct', action='store_true',
                        help='use longest_common_substring instead of longest_common_subsequence')
    parser.add_argument('--combo_size', '-cs', help='the size of combination', default=2, type=int)
    parser.add_argument('--separate', '-sp', action='store_true',
                        help='separate vowels from consonants when considering possible variations')

    return parser.parse_args()


def main():
    args = parse_arguments()
    print('contiguous: {}\ncombo size: {}\nseparate: {}'.format(args.contiguous, args.combo_size, args.separate))

    with open('wik_tur.csv') as file:
        data = get_unprocessed_data(file)

    combi_forms_dict = {}
    for i in range(1, args.combo_size + 1):
        combi_forms_dict.update(get_feature_combi_dict(data, i))
    key_list = [tuple(sorted(tuple(key))) for key in combi_forms_dict.keys()]
    key_list.sort(key=lambda x: (len(x), x))
    print('{} combinations of features: {}'.format(len(key_list), key_list))

    m = Model()
    m.get_all_letters(data, separate=args.separate)

    if args.contiguous:
        from helper import m_longest_common_substring as MLCS
    else:
        from helper import m_longest_common_subsequence_3 as MLCS
    m.MLCS = MLCS

    # combi_lcs_list_dict = {}
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
