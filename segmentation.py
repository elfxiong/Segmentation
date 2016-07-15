from collections import defaultdict
from starter_code import LCS, MLCS, compare_str_lcs
import codecs

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

    #print(lemma_lcs_dict)

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
    final_freq_dict = {}
    fout = codecs.open("Tag_endings_freq.csv",'wb',encoding='utf-8')
    fout.write("Feature_Tag,Ending,Frequency"+"\n")
    with open(filename, encoding='utf-8') as file:
        feature_lemma_forms_dict, lemma_forms_dict = produce_dicts(file)
    #print(feature_lemma_forms_dict['N'])
    for feature, lemmas in feature_lemma_forms_dict.items():
        # all the features are the N, V and a list so on.
        # lemmas are a list with lemmas and endings
        all_forms = set()  # all words with this feature
        for lemma, forms in lemmas.items():
            for x in range(len(forms)):
                # take every word here in the set which has an inflection
                affixes = []
                #print(type(forms[x]))
                characters_in_word = list(forms[x])
                characters_in_lemma = list(lemma)
                lemma_length = len(characters_in_lemma)
                for i in range(lemma_length,len(characters_in_word)):
                    affixes.append(characters_in_word[i])
                affix = ''.join(affixes)
                # TAG -> ending -> frequency
                # feature -> affix -> frequency yet to cal.
                if affix+","+feature in final_freq_dict:
                    count = final_freq_dict.get(affix+","+feature)
                    #print(type(count))
                    count = count+1
                    final_freq_dict[affix+","+feature] = count
                else:
                    final_freq_dict[affix+","+feature] = 1

                #fout.write(feature+","+affix+"\n")
    lst = []
    for feature, count in final_freq_dict.items():
        temp = feature.split(",")

        # fout.write(temp[1]+","+temp[0]+","+str(count)+"\n")
        tup = (temp[1], temp[0], str(count))
        lst.append(tup)
    lst = sorted(lst, key=lambda x: x[1])
    lst = sorted(lst, key=lambda x: x[0])
    lst = [','.join(tup) for tup in lst]
    fout.write('\n'.join(lst))

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
    read_csv('test_tur.csv')


if __name__ == '__main__':
    main()
