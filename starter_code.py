# coding: utf-8
# author: John Sylak-Glassman (johnsylakglassman@gmail.com)

"""
This file contains code to use functions based on longest common subsequence (LCS) to find affixes.
Based on these affixes and average word length, a scaling co-efficient for use with
a position-weighted Levenshtein distance algorithm is calculated.
"""


def LCS(X, Y):
    """
    First finds a table (matrix) such that L[j][k] is length of longest common subsequence for X[0:j] and Y[0:k].
    Then, uses tracebacks through this table to print the actual LCS.
    This only works for two strings, and is the most straightforward dynamic programming solution,
    but it likely isn't the fastest.
    """
    n, m = len(X), len(Y)
    L = [[0] * (m + 1) for k in range(n + 1)]  # Creates matrix of values to fill
    for j in range(n):  # Loop through indices of 1st string
        for k in range(m):  # Loop through indices of 2nd str each time you're on an index of first
            if X[j] == Y[k]:  # If the characters match,
                L[j + 1][k + 1] = L[j][k] + 1  # fill in coordinates of table with value of upper left cell + 1.
            else:  # Otherwise,
                L[j + 1][k + 1] = max(L[j][k + 1], L[j + 1][k])  # choose max value from left cell or above cell
    solution = []  # Initialize a list for storing the solution
    j, k = len(X), len(Y)  # Now, do a traceback through L, starting with the highest valued cell.
    while L[j][k] > 0:
        if X[j - 1] == Y[k - 1]:
            solution.append(X[j - 1])
            j -= 1
            k -= 1
        elif L[j - 1][k] > L[j][k - 1]:  # This and the next elif pick the highest value in a cell to
            j -= 1  # the left or above in L.
        elif L[j - 1][k] < L[j][k - 1]:
            k -= 1
        elif L[j - 1][k] == L[j][k - 1]:  # Original algorithm didn't adequately deal with case in which
            # cell to the left or above were equally good.
            if X[j - 2] == Y[k - 1] and X[j - 2] not in {"a", "e", "i", "o", "u"}:  # Bias toward consonants in stem.
                j -= 1  # Eventually, need to not hardcode the vowels!!
            elif X[j - 1] == Y[k - 2] and Y[k - 2] not in {"a", "e", "i", "o", "u"}:  # Bias toward consonants in stem.
                k -= 1  # Eventually, need to not hardcode the vowels!!
            else:  # Default directionality: Leftward in chart.
                k -= 1
        else:  # Default directionality: Leftward in chart.
            k -= 1
    return ''.join(reversed(solution))


def MLCS(s):
    """
    s is a set of strings, e.g. set(["höfn","höfn","höfn","hafnar","hafnir","hafnir","höfnum","hafna"])
    from Fig. 1 of AFH 2015

    First sort the list of strings, then loop over them two by two, applying LCS. Store the results for each pair.
    Eliminate duplicates in that list, then recursively do the same thing you did before, and on and on until you get 
    down to one unique string (or no unique string!). This is a naive, possibly very slow method, but it's a first 
    step that will work with modest data (e.g. not full Turkic or Archi verb paradigms!).

    This function works well, but doesn't significantly alter the results of calculating the MLCS. The function 
    LCS(X,Y) is much more important to determining the longest common subsequence that results than this function is.
    """
    if len(s) == 1:
        return ""
    s_sorted = sorted(list(s))  # Converts a set to a list and sorts it.
    lcs_set = set()  # This stores candidates for the LCS, eliminating duplicates.
    for i, item in enumerate(s_sorted[:-1]):  # Go through every word in the input set, except the very last
        lcs_set.add(LCS(s_sorted[i], s_sorted[i + 1]))  # Add the LCS of the word you're on as well as the next - this
        # incorporates the last word.
    if len(lcs_set) > 1:  # Until we arrive at only a single LCS,
        return MLCS(lcs_set)  # keep feeding the candidates back in like any other set, and
        # find LCS
    else:  # When you finally arrive at just one, return it as the MLCS
        return lcs_set.pop()


def compare_str_lcs(string, lcs):
    """
    Takes a string and the LCS of it with another unicode string to be compared, and which is supplied by a previous 
    call to LCS(). Finds the set of prefixal, infixal, and suffixal changes between the unicode string form and the
    LCS. Outputs a 3-tuple of the prefix, any infixal changes, and the suffix change. Empty strings that result from
    there being no change between the LCS and the string for, e.g. a prefix, need to be filtered out after this function.
    """
    prev_ind = 0
    prefix = ""
    infixes = set()
    suffix = ""
    infix_counter = 1
    for i, ch in enumerate(lcs):
        if prev_ind == 0 and i == 0:
            if string.startswith(ch):
                prefix = ""
                continue
            else:
                prev_ind = string.find(ch, prev_ind)
                prefix = string[0:prev_ind]
        else:
            inf_ind = string.find(ch, prev_ind + 1)
            if string[prev_ind + 1:inf_ind] != "":
                infix = (string[prev_ind + 1:inf_ind], infix_counter)
                # in previous line, add i to the tuple to get position within the LCS, which is important for Arabic.
                # in Beta, would be useful to add functionality to tell software what to pay attention to.
                # E.g. keep track of LCS position in templatic systems, otherwise just linear order using 
                # infix_counter in systems like Spanish or German where there either is a stem change or isn't, and
                # it's not as important precisely which segment it is after, since the position is prosodic or
                # morphological, like first syllable of stem, for example.
                infixes.add(infix)
                infix_counter += 1
            prev_ind = inf_ind
    if string[prev_ind + 1:] != "":
        suffix = string[prev_ind + 1:]
    else:
        suffix = ""
    return (prefix, frozenset(infixes), suffix)


def segment_lcs(lcs):
    """
    The purpose of this function is to generate all the possible splittings of the LCS, so that find_lcs_seg can 
    figure out how the LCS is split up in a given word. Also, to deal with duplicated material in an LCS, 
    e.g. "barbar" for ["barbarian", "barbarous","barbaric"], the original indices of material in the LCS is saved in 
    lcs_seg_ind.
    """
    n = len(lcs)  #
    lcs_segs = []  # Working list of segmentations of the LCS
    lcs_seg_ind = dict()  # Initalize dict to keep track of segmentations' indices
    for i in range(len(lcs)):  # Loop through the indices of the LCS
        lcs_segs.append(
            lcs[i:len(lcs)])  # This appends segmentations that peel from the left, e.g. barbar, arbar, rbar, etc.
        if lcs[i:len(lcs)] in lcs_seg_ind:  # If the segment is already in the lcs_seg_ind,
            lcs_seg_ind[lcs[i:len(lcs)]].append((i, len(lcs)))  # append its indices to the list of index pairs
        else:  # Otherwise, record the segment's start and end index
            lcs_seg_ind[lcs[i:len(lcs)]] = [(i, len(lcs))]  # in a tuple embedded in a list
        for j in range(1, len(lcs)):  # Now, loop through the indices of the LCS, but appending
            lcs_segs.append(lcs[i:-j])  # segmentations that peel from the right, e.g. barbar, barba, barb, etc.
            if lcs[i:-j] in lcs_seg_ind:  # Like above, record the segment start and ending indices.
                lcs_seg_ind[lcs[i:-j]].append((i, len(lcs) - (j)))
            else:
                lcs_seg_ind[lcs[i:-j]] = [(i, len(lcs) - (j))]
    lcs_segments = []  # Initialize final list of LCS segments which should be returned.
    if "" in lcs_seg_ind:  # Remove an empty string, since it's useless here.
        lcs_seg_ind.pop("")
    for k in lcs_segs:  # Remove an empty string, putting meaningful contents in a new list.
        if k != "":  # This is probably unnecessarily memory-intensive...
            lcs_segments.append(k)
    return lcs_segments, lcs_seg_ind  # Return both the list of segmentations, and a record of their original indices in the LCS.


def find_lcs_seg(word, word_pos, lcs_segments, lcs_seg_pos):
    """
    This function takes a single word, the current search position in the word (default = 0), a list of segmentations 
    of the LCS of that word's cluster (therefore including that word), and an initialized list, lcs_seg_pos, which is 
    initialized outside the function, and can then be passed in on subsequent rounds of recursion. The goal of the
    function is to produce a dictionary of which LCS segments are in the word at which positions. This output is
    actually lcs_seg_pos, which is only initialized outside the function to allow recursion.
    Likely need to add in something to keep track of which lcs_segments you've searched for and not found... 
    There should theoretically not be any!
    """
    for seg in lcs_segments:  # Loop through the possible segmentations of the LCS.
        if word.find(seg, word_pos) != -1:  # If you find an LCS segment in the word (since find()
            # returns -1 if there is no match) anywhere after word_pos,
            last_word_ind = word.index(seg, word_pos) + len(
                seg)  # Update a variable that records your position in the word.
            lcs_seg_pos.append((seg, word.index(seg, word_pos), last_word_ind))
            # Add a list element to lcs_seg_pos that is a tuple containing the segment of the LCS, where it starts in the 
            # word, and where it ends in the word
            lcs = lcs_segments[0]
            # Need to keep track of where we are in the LCS itself, so we do this all to find out whether we're done.
            # The LCS itself is always the first segment in the lcs_segments list, so grab it.
            lcs = lcs[
                  lcs.find(seg) + len(seg):]  # Redefine the LCS as being from the portion you just found to the end.
            # This reduces the subsequent search space for LCS segments and prevents
            # rediscovery of already found segments. It also prevents infinite recursion.
            if lcs == "":  # If the LCS is now an empty string, you've gone through it all, and you're done.
                return lcs_seg_pos  # Return the list of segmentations of the LCS with their positions in this word.
            else:  # Otherwise, use recursion to keep finding segments in the word.
                lcs_segments, lcs_seg_ind = segment_lcs(lcs)  # lcs_seg_ind never gets used.
                return find_lcs_seg(word, last_word_ind, lcs_segments,
                                    lcs_seg_pos)  # Calls the function again for recursion.


def find_infl(word, lcs_seg_pos):
    """
    This finds material in a word that is not the LCS. The name of the function reflects a view in which the LCS is 
    the stem or template, while everything outside of it is potentially inflectional. This view is from the point 
    of view of Arabic triconsonantal roots and data that include full paradigms. 
    """
    infl_pos = dict()
    for i, seg in enumerate(lcs_seg_pos[0:-1]):  # For every segment of the LCS in a word,
        if i == 0 and lcs_seg_pos[i][1] > 0:  # If it's the very first segment of the LCS and there's material before it
            infl_start = 0  # record the start and end of that INFL material, and what the
            infl_end = lcs_seg_pos[i][1]  # material itself is. Use the start of the INFL material as the
            infl = word[infl_start:infl_end]  # key to facilitate lookup in building the template.
            infl_pos[infl_start] = (infl, infl_end)
            infl_start = lcs_seg_pos[i][2]  # Then, grab the INFL material after the very first segment of the
            infl_end = lcs_seg_pos[i + 1][1]  # LCS, and similarly record it in infl_pos
            infl = word[infl_start:infl_end]
            infl_pos[infl_start] = (infl, infl_end)
        else:
            infl_start = lcs_seg_pos[i][2]  # Then, for each subsequent LCS segment, grab the INFL material
            infl_end = lcs_seg_pos[i + 1][1]  # after it, and record it just like as above in infl_pos.
            infl = word[infl_start:infl_end]
            infl_pos[infl_start] = (infl, infl_end)
    infl_after_lcs = word[lcs_seg_pos[-1][2]:len(word)]  # Finally, grab all the INFL material after the LCS.
    if infl_after_lcs != "":
        infl_start = lcs_seg_pos[-1][2]
        infl_end = len(word)
        infl_pos[infl_start] = (infl_after_lcs, infl_end)
    return infl_pos


def templ_aug(lcs, lcs_seg_ind, lcs_seg_pos, infl_pos):
    """
    The goal of this block is to generalize from finding the LCS and INFL material in a specific word to finding a template for
    a cluster of words that breaks up the LCS as much as it can be broken up and comes up with all the material in between each 
    segmentation of the LCS. Working with multiple words is done in the function cand_gen. This function builds up a single
    template for one word.
    """
    templ_dict = dict()  # Initialize a dictionary
    for i in range(len(
            lcs) + 1):  # For every character index in the LCS, i, plus one more, initialize a dict entry such that
        # for an LCS of "ktbktb", the indices capture the following material: <-0k1-> t2-> b3-> k4-> t5-> b6-> 
        # Entry 0 will store material before LCS, all other indices store material after them, with the final index storing 
        # material after the LCS. Only need to initialize all this once.
        templ_dict[i] = set()
    lcs_ind = 0  # Keep track of position within the LCS
    word_ind = 0  # Keep track of position within the word
    for i, seg_i in enumerate(lcs_seg_pos):
        if i == 0 and lcs_seg_pos[0][
            1] > 0:  # For templ_dict[0], which is material in the word before the first part of the LCS
            # POTENTIAL PROBLEM: We don't break up the LCS segment here. Am I accidentally indexing a dict with lcs_seg_pos[0]?
            templ_dict[0].add(infl_pos[0][0])  # for the zeroeth index, add the infl material that appears before it
            lcs_ind = lcs_seg_pos[0][2] - lcs_seg_pos[0][1]  # update the within-LCS index
            word_ind = lcs_seg_pos[0][2]  # update the within-word position index
            templ_dict[lcs_ind].add(infl_pos[word_ind][0])  # Add infl material after the very first LCS segment
            word_ind = infl_pos[word_ind][1]  # update the within-word position index again
        else:  # For all subsequent material, where it can be understood as being after the LCS index, which is the key
            # in templ_dict, add material that occurs after each LCS segment.
            if len(lcs_seg_ind[lcs_seg_pos[i][0]]) > 1:  # If the LCS segment is larger than one character,
                for j, ind_j in enumerate(lcs_seg_ind[lcs_seg_pos[i][0]]):  # Then for each character in the segment,
                    if ind_j[0] == lcs_ind:  # if the segment starts at where you are in the LCS
                        lcs_ind = lcs_seg_ind[lcs_seg_pos[i][0]][j][1]  # update the LCS
                        word_ind = lcs_seg_pos[i][2]  # update the within-word index
                        if word_ind in infl_pos:  # If there's infl material at the that word position,
                            templ_dict[lcs_ind].add(infl_pos[word_ind][0])  # add it to the template.
            else:  # If the LCS segment is just one character,
                lcs_ind = lcs_seg_ind[lcs_seg_pos[i][0]][0][1]  # update the LCS and word indices,
                word_ind = lcs_seg_pos[i][2]
                if word_ind in infl_pos:  # and add the following INFL material to the template
                    templ_dict[lcs_ind].add(infl_pos[word_ind][0])
    for k in templ_dict:  # If there are entries in the template dictionary for which there is no material,
        if templ_dict[k] == set():
            templ_dict[k].add("")  # Add an empty string as a possible value.
    return templ_dict


# MAIN FUNCTION
def template_gen(s, template_dict_by_fv=0):
    """
    s may be a list or a set of words, such as those in an automatically-discovered cluster.
    This function loops over words in a set, and uses all the above functions for finding a template over that set.
    """
    from collections import defaultdict
    s_words = set([x for (x, y) in s])  # Turn s into a set already if it isn't one in order to remove duplicates.
    template = dict()  # TODO: Check if this can be removed.
    lcs = MLCS(s_words)  # First, find the LCS. TODO HERE: Make sure that input to MLCS is just words, not tuples.
    lcs_segments, lcs_seg_ind = segment_lcs(lcs)
    if template_dict_by_fv == 0:
        template_dict_by_fv = defaultdict(list)  # Store all templates in here, in the form of (feat_vec, template)
    template_list = list()  # Keep two templates in here: An aggregate template and the previous template
    for (word, feat_vec) in s:  # Loop through the words in the input list/set
        # TODO HERE: Check if s is what you need it to be...
        if len(template_list) == 2:  # If there are two templates in the template list already, then
            temporary_template = dict()  # Create a temporary_template with the same keys as the templates in the list,
            for i in template_list[0]:  # and store the union of material in every key in the two templates in the list
                temporary_template[i] = template_list[0][i] | template_list[1][i]
            template_list = [
                temporary_template]  # Then, replace the whole list with the temporary template as the only item
        word_pos = 0  # Keep track of where we are in the word.
        lcs_seg_pos = find_lcs_seg(word, word_pos, lcs_segments, [])  # Find where the LCS occurs in the word.
        infl_pos = find_infl(word, lcs_seg_pos)  # Use that to find where the INFL material occurs.
        template = templ_aug(lcs, lcs_seg_ind, lcs_seg_pos, infl_pos)  # Then, build a template using that information.
        # WORK HERE - Need to get every set([]) inside a template to be a frozenset([]) so that we can remove duplicate templates.
        template_froz = set()
        for j in template:
            template_froz.add(tuple((j, frozenset(template[j]))))
        if template_froz not in template_dict_by_fv[feat_vec]:
            template_dict_by_fv[feat_vec].append(
                template_froz)  # Want to be able to add additional templates for each feat_vec
        template_list.append(template)  # Add that template to the template_list.
        # merge templates for each word at each step!
    for i in template_list[0]:  # Do one last merge of the final template into
        temporary_template[i] = template_list[0][i] | template_list[1][
            i]  # the aggregate template, then store that as usual.
    template_list = [temporary_template]
    template_list = template_list[
        0]  # Turn template_list from a list to a dictionary. Should probably change the variable name.
    final_template = dict()
    for i in template_list:  # For every key in the final template, which represents an index of the LCS,
        final_template[i] = []  # initialize a list as the value, then
        for j in template_list[i]:  # for every element in the value of each key,
            final_template[i].append(j)  # add that element to the newly initialized list
        final_template[i] = sorted(final_template[i])  # and then finally, do a sort
    # TODO HERE: Process template_list_by_fv to remove duplicate templates. Note that inner sets of templates must be frozensets.
    return final_template, template_dict_by_fv, lcs


def cand_gen_paradigm(final_template, lcs):
    """
    This is the first version of candidate generation that I did. However, it's not clear how useful it is. It takes
    a template generated from a full paradigm and builds all the possible 
    """
    from itertools import product  # Any way to avoid calling this for every function execution?
    command = ""  # This is one aspect of my code that is probably bad. I basically build a complex
    for i in range(len(lcs)):  # command using string replacement, then throw that string through eval. Is there
        command = command + "final_template[" + str(i) + "],lcs[" + str(
            i) + "],"  # a better way? eval() is very dangerous
    command = "product(" + command + "final_template[" + str(len(lcs)) + "])"  # and open to exploitation, potentially.
    concat_cand_material = eval(command)  # The line above is where I do the Cartesian product of the template material!
    candidate_set = set()  # Finally, we're ready to build the candidate set. Initialize it as a set.
    for i in concat_cand_material:  # The output of itertools.product() are tuples, which need to have their internal
        candidate_set.add("".join(j for j in i))  # material joined in this line, then added to the set.
    candidate_list = list(candidate_set)  # For easy reading, I turn the set into a list and sort it, then return it.
    candidate_list = sorted(candidate_list)
    return candidate_list


def get_morph_data(data_file):
    """
    Takes in CSV data with rows of the form: inflected_form, lemma, feature_vector
    (where feature_vector is a set of features separated by ";"). Produces a 
    dictionary data structure to use to access morphological data.
    """
    ft_vec_set = set()
    data = dd(dict)
    with open(data_file, "rb") as mdata_file:
        mdata = ucsv.reader(mdata_file, encoding='utf-8')
        for line in mdata:
            ft_vec_set.add(line[2])
            data[line[1]][line[2]] = line[0]
            # = data[lemma][ft_vec] = infl
    return data


def get_morph_data_no_spaces(data_file):
    """
    Takes in CSV data with rows of the form: inflected_form, lemma, feature_vector
    (where feature_vector is a set of features separated by ";"). Filters out any
    inflected_forms or lemmas with spaces in them. Produces a 
    dictionary data structure to use to access morphological data.
    """
    ft_vec_set = set()
    data = dd(dict)
    with open(data_file, "rb") as mdata_file:
        mdata = ucsv.reader(mdata_file, encoding='utf-8')
        for line in mdata:
            if " " not in line[0] and " " not in line[1]:
                ft_vec_set.add(line[2])
                data[line[1]][line[2]] = line[0]
                # = data[lemma][ft_vec] = infl
    return data


def compile_paradigm_list(data):
    """
    This function is the heart of the process of finding affixes based on training data.
    For a given lemma, it finds the LCS among all possible forms, then creates a dict of
    affixes used for each feature vector in each lemma, based on differences from the LCS.
    It stores all these dicts in a paradigm_list, and keeps track of which lemmas belong to
    which paradigms (although that information isn't currently used). It also keeps track
    of what the LCS for each lemma's paradigm is (although this also isn't currently used.)
    This function produces the data structure used to gather prefixes, infixes, and suffixes
    to calculate the weighting coefficients for the position-weighted Levenshtein distance
    algorithm.
    """
    import time
    start = time.clock()
    print("Starting time:", start)
    current_paradigm_list_index = 0
    paradigm_list = list()
    #    lemma_to_paradigm = dd(set)
    #    lemma_to_mlcs = dict()
    for i, lemma in enumerate(sorted(data)):
        # Just to give you something to look at while it runs...
        if i % 300 == 0:
            print("Index in data:", i, "\tLemma:", lemma, "\tTime at processing:", time.clock())
            print("\tCurrent number of separate paradigms:", len(paradigm_list))
        # Need to calculate the LCS for the entire lemma's paradigm. Watch out for it returning as 0.
        infl_group = set()
        for ft_vec in data[lemma]:
            infl_group.add(data[lemma][ft_vec])
        mlcs = MLCS(infl_group)
        #        lemma_to_mlcs[lemma] = mlcs
        if len(mlcs) == 0:
            continue
        # Need a dict that, for each lemma, keeps an (infl, ftvec) tuple as key, then keeps dicts with "target" ftvec as 
        # key and set_of_changes to reach it as values. 
        # e.g. dd[(u"abacoro", u"IND;V;PRS;1;SG;IPFV/PFV")][u"IND;V;PRS;2;SG;IPFV/PFV"] = frozenset(["o","as"])
        chg_set = dd(dict)
        for ft_vec in data[lemma].keys():  # originally used it.permutations - I think we
            # can use combinations instead because the number of changes from one infl form to another is the same
            # regardless of direction, and the changes themselves are also the same, except for the artificial designation
            # of infixes as infixes to the source or target.
            changes = compare_str_lcs(data[lemma][ft_vec], mlcs)
            chg_set[ft_vec] = changes
            # e.g. chg_set[u'V.PTCP;PST;FEM;SG'] = 
            #               (('p', ''),
            #                frozenset(('i', u'ue')), 
            #                ('s', u'da'),
            #               )
        # NO INDICATION OF FREQUENCY... TRY TO REDO THINGS TO MAKE THIS WHOLE PROCESS FASTER AND KEEP FREQUENCY!
        if chg_set not in paradigm_list:
            paradigm_list.append(chg_set)
        #        if chg_set in paradigm_list:
        #            lemma_to_paradigm[paradigm_list.index(chg_set)].add(lemma)
        #        else:
        #            paradigm_list.append(chg_set)
        #            lemma_to_paradigm[paradigm_list.index(chg_set)].add(lemma)
    print("Final number of separate paradigms:", len(paradigm_list))
    end = time.clock()
    print("This whole thing took", end - start, "seconds")
    return paradigm_list  # , lemma_to_paradigm, lemma_to_mlcs


def pickleParadigmList(paradigm_list, data_dir):  # lemma_to_paradigm,lemma_to_mlcs):
    """
    Because the calculation of full affix sets can take a long time, this function
    allows you to save the resulting data structures in files that can be directly 
    loaded for later use. 
    """
    with open(data_dir + "paradigm_list.pickle", "wb") as f:
        import pickle
        pickle.dump(paradigm_list, f)
    print("Pickled the paradigm_list")


#    with open("lemma_to_paradigm.pickle","wb") as f:
#        pickle.dump(lemma_to_paradigm,f)
#    print "Pickled the lemma_to_paradigm assignments"
#    with open("lemma_to_mlcs.pickle","wb") as f:
#        pickle.dump(lemma_to_mlcs,f)
#    print "Pickled the lemma_to_paradigm assignments"

def loadPickledParadigmList(para_file):  # ,lem_file):
    """
    This function loads saved data structures from the function pickleParadigmList.
    """
    import pickle
    paradigm_list = pickle.load(open(para_file, "rb"))
    #    lemma_to_paradigm = pickle.load(open(lem_file,"rb"))
    return paradigm_list  # , lemma_to_paradigm


def gather_affixes(paradigm_list):
    prefixes = set()
    infixes = set()
    suffixes = set()
    for paradigm in paradigm_list:
        for i in paradigm.keys():
            if paradigm[i][0] != "":
                prefixes.add(paradigm[i][0])
            if paradigm[i][2] != "":
                suffixes.add(paradigm[i][2])
            if len(paradigm[i][1]) != 0:
                for j in paradigm[i][1]:
                    infixes.add(j)
    print("Prefixes:", len(prefixes), "\nInfixes:", len(infixes), "\nSuffixes:", len(suffixes))
    return prefixes, infixes, suffixes


def get_wordlist(data):
    """
    Builds a set of inflected forms to be used to calculate average word length.
    This figure is used in converting the average length of affix classes (prefixes,
    infixes, suffixes) into 
    """
    word_list = list()
    for lemma in data.keys():
        for ft_vec in data[lemma].keys():
            word_list.append(data[lemma][ft_vec])
    print("Words:", len(word_list))
    return word_list


def avg_affix_length(affix_set):
    """
    Finds the average length of strings in a set. This is applied to the set of infl words 
    as well as the sets of different affix types. 
    """
    if len(affix_set) == 0:
        return 0
    else:
        total_len = 0
        for affix in affix_set:
            total_len += len(affix)
        avg_affix_len = float(total_len) / len(affix_set)
        return avg_affix_len

# SOME MAIN CODE
# s = [("muero","mood=IND;tense=PRS;aspect=IPFV;person=1;number=SG"),("mueres","mood=IND;tense=PRS;aspect=IPFV;person=2;number=SG"),("muere","mood=IND;tense=PRS;aspect=IPFV;person=3;number=SG"),("morimos","mood=IND;tense=PRS;aspect=IPFV;person=1;number=PL"),("morís","mood=IND;tense=PRS;aspect=IPFV;person=2;number=PL"),("mueren","mood=IND;tense=PRS;aspect=IPFV;person=3;number=PL"),("moría","mood=IND;tense=PST;aspect=IPFV;person=1;number=SG"),("morías","mood=IND;tense=PST;aspect=IPFV;person=2;number=SG"),("moría","mood=IND;tense=PST;aspect=IPFV;person=3;number=SG"),("moríamos","mood=IND;tense=PST;aspect=IPFV;person=1;number=PL"),("moríais","mood=IND;tense=PST;aspect=IPFV;person=2;number=PL"),("morían","mood=IND;tense=PST;aspect=IPFV;person=3;number=PL"),("morí","mood=IND;tense=PST;aspect=PFV;person=1;number=SG"),("moriste","mood=IND;tense=PST;aspect=PFV;person=2;number=SG"),("murió","mood=IND;tense=PST;aspect=PFV;person=3;number=SG"),("morimos","mood=IND;tense=PST;aspect=PFV;person=1;number=PL"),("moristeis","mood=IND;tense=PST;aspect=PFV;person=2;number=PL"),("murieron","mood=IND;tense=PST;aspect=PFV;person=3;number=PL"),("moriré","mood=IND;tense=FUT;aspect=IPFV/PFV;person=1;number=SG"),("morirás","mood=IND;tense=FUT;aspect=IPFV/PFV;person=2;number=SG"),("morirá","mood=IND;tense=FUT;aspect=IPFV/PFV;person=3;number=SG"),("moriremos","mood=IND;tense=FUT;aspect=IPFV/PFV;person=1;number=PL"),("moriréis","mood=IND;tense=FUT;aspect=IPFV/PFV;person=2;number=PL"),("morirán","mood=IND;tense=FUT;aspect=IPFV/PFV;person=3;number=PL"),("moriría","mood=COND;tense=PRS;aspect=IPFV/PFV;person=1;number=SG"),("morirías","mood=COND;tense=PRS;aspect=IPFV/PFV;person=2;number=SG"),("moriría","mood=COND;tense=PRS;aspect=IPFV/PFV;person=3;number=SG"),("moriríamos","mood=COND;tense=PRS;aspect=IPFV/PFV;person=1;number=PL"),("moriríais","mood=COND;tense=PRS;aspect=IPFV/PFV;person=2;number=PL"),("morirían","mood=COND;tense=PRS;aspect=IPFV/PFV;person=3;number=PL"),("muera","mood=SBJV;tense=PRS;aspect=IPFV/PFV;person=1;number=SG"),("mueras","mood=SBJV;tense=PRS;aspect=IPFV/PFV;person=2;number=SG"),("muera","mood=SBJV;tense=PRS;aspect=IPFV/PFV;person=3;number=SG"),("muramos","mood=SBJV;tense=PRS;aspect=IPFV/PFV;person=1;number=PL"),("muráis","mood=SBJV;tense=PRS;aspect=IPFV/PFV;person=2;number=PL"),("mueran","mood=SBJV;tense=PRS;aspect=IPFV/PFV;person=3;number=PL"),("muriera","mood=SBJV;tense=PST;aspect=IPFV;person=1;number=SG"),("murieras","mood=SBJV;tense=PST;aspect=IPFV;person=2;number=SG"),("muriera","mood=SBJV;tense=PST;aspect=IPFV;person=3;number=SG"),("muriéramos","mood=SBJV;tense=PST;aspect=IPFV;person=1;number=PL"),("murierais","mood=SBJV;tense=PST;aspect=IPFV;person=2;number=PL"),("murieran","mood=SBJV;tense=PST;aspect=IPFV;person=3;number=PL"),("muriese","mood=SBJV;tense=PST;aspect=IPFV;person=1;number=SG;lgspec=LGSPEC2"),("murieses","mood=SBJV;tense=PST;aspect=IPFV;person=2;number=SG;lgspec=LGSPEC2"),("muriese","mood=SBJV;tense=PST;aspect=IPFV;person=3;number=SG;lgspec=LGSPEC2"),("muriésemos","mood=SBJV;tense=PST;aspect=IPFV;person=1;number=PL;lgspec=LGSPEC2"),("murieseis","mood=SBJV;tense=PST;aspect=IPFV;person=2;number=PL;lgspec=LGSPEC2"),("muriesen","mood=SBJV;tense=PST;aspect=IPFV;person=3;number=PL;lgspec=LGSPEC2"),("muriere","mood=SBJV;tense=FUT;aspect=IPFV/PFV;person=1;number=SG"),("murieres","mood=SBJV;tense=FUT;aspect=IPFV/PFV;person=2;number=SG"),("muriere","mood=SBJV;tense=FUT;aspect=IPFV/PFV;person=3;number=SG"),("muriéremos","mood=SBJV;tense=FUT;aspect=IPFV/PFV;person=1;number=PL"),("muriereis","mood=SBJV;tense=FUT;aspect=IPFV/PFV;person=2;number=PL"),("murieren","mood=SBJV;tense=FUT;aspect=IPFV/PFV;person=3;number=PL"),("muere","mood=IMP;polarity=POS;politeness=INFM;person=2;number=SG"),("muera","mood=IMP;polarity=POS;politeness=FORM;person=2;number=SG"),("muramos","mood=IMP;polarity=POS;person=1;number=PL"),("morid","mood=IMP;polarity=POS;politeness=INFM;person=2;number=PL"),("mueran","mood=IMP;polarity=POS;person=3;number=PL"),("no mueras","mood=IMP;polarity=NEG;politeness=INFM;person=2;number=SG"),("no muera","mood=IMP;polarity=NEG;politeness=FORM;person=2;number=SG"),("no muramos","mood=IMP;polarity=NEG;person=1;number=PL"),("no muráis","mood=IMP;polarity=NEG;person=2;number=PL"),("no mueran","mood=IMP;polarity=NEG;person=3;number=PL")]
# #s = [("ktabtu","feat_vec1"),("'aktubu","feat_vec2"),("taktubuuna","feat_vec3"),("yaktubaani","feat_vec4")]
# final_template, template_dict_by_fv, lcs = template_gen(s)
# final_template, template_dict_by_fv, lcs = template_gen(s,template_dict_by_fv)
# cand_list = cand_gen_paradigm(final_template,lcs)
# for i in final_template:
#     print(i, final_template[i])
# print(lcs)
# print(template_dict_by_fv["mood=IND;tense=PRS;aspect=IPFV;person=1;number=SG"])
