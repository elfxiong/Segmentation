from collections import defaultdict

import re

from starter_code import LCS, MLCS, compare_str_lcs
import codecs


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


def produce_dicts(file):
    tup_list = get_unprocessed_data(file)

    # dict[lemma] == [form1, form2, ...]
    lemma_forms_dict = defaultdict(list)
    for inflected_form, lemma, fv in tup_list:
        lemma_forms_dict[lemma].append(inflected_form)

    # dict[lemma] == lcs_of_all_its_forms
    lemma_lcs_dict = {}
    for word, forms in lemma_forms_dict.items():
        lemma_lcs_dict[word] = MLCS(forms)

    # dict[feature][stem] == [form1, form2, ...]
    feature_dict = defaultdict(lambda: defaultdict(list))

    for inflected_form, lemma, fv in tup_list:
        stem = lemma_lcs_dict[lemma]
        for feature in fv.strip().split(';'):
            feature_dict[feature][stem].append(inflected_form)
    return feature_dict, lemma_forms_dict


def convert_to_archiphonemic(form):
    # language specific
    form = re.sub('[ae]', 'E', form)
    form = re.sub('[iɪüu]', 'I', form)
    form = re.sub('[dt]', 'D', form)
    form = re.sub('[cç]', 'C', form)
    form = re.sub('[kgǧ]', 'K', form)
    return form


def read_csv(filename):
    final_freq_dict = defaultdict(int)
    fout = codecs.open("Tag_endings_freq.csv", 'wb', encoding='utf-8')
    fout.write("Feature_Tag,Ending,Frequency" + "\n")
    with open(filename, encoding='utf-8') as file:
        feature_lemma_forms_dict, lemma_forms_dict = produce_dicts(file)
    # print(feature_lemma_forms_dict['N'])
    for feature, lemmas in feature_lemma_forms_dict.items():
        # all the features are the N, V and a list so on.
        # lemmas are a list with lemmas and endings
        all_forms = set()  # all words with this feature
        for lemma, forms in lemmas.items():
            for form in forms:
                # take every word here in the set which has an inflection
                suffix = form[len(lemma):]

                # TAG -> ending -> frequency
                # feature -> affix -> frequency yet to cal.
                final_freq_dict[(suffix, feature)] += 1
                # fout.write(feature+","+affix+"\n")
    lst = []

    lcs_dict = {}
    # this dict is used as a bag to store the feature and the lcs over the affixes associated with the feature.

    for (suffix, feature), count in final_freq_dict.items():
        if feature in lcs_dict:
            lcs_dict[feature].append(suffix)
        else:
            lcs_dict[feature] = [suffix]
        # fout.write(feature+","+suffix+","+str(count)+"\n")
        tup = (feature, suffix, str(count))
        lst.append(tup)
    lst = sorted(lst, key=lambda x: int(x[2]), reverse=True)
    lst = sorted(lst, key=lambda x: x[0])
    lst = [','.join(tup) for tup in lst]
    fout.write('\n'.join(lst))

    for features, affix in lcs_dict.items():
        lcs_temp = MLCS(affix)
        print(features+" "+lcs_temp)



            #fout.write(feature+","+)
            # lemma is the key word
            #all_forms.update(forms)
            # lcs = MLCS(all_forms)
            # chop lemma from all the forms.
            # store this as an entire file like this.
            # TAG -> ending -> frequency

            #print(forms)
            #print('{}'.format(feature))


def main():
    read_csv('wik_tur.csv')


if __name__ == '__main__':
    main()
