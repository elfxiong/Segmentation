"""Longest common subsequence and longest common substring functions
Found on Wiki
"""


# subsequence


def m_longest_common_subsequence_2(s):
    """An iterative method to compute MLCS"""
    from starter_code import LCS as longest_common_subsequence

    # Correct me if I'm wrong but I think unsorted list is faster
    lst = list(s)

    lcs = lst[0]
    for string in lst[1:]:
        lcs = longest_common_subsequence(lcs, string)

    return lcs


def lcs_length(X, Y):
    m = len(X)
    n = len(Y)
    # An (m+1) times (n+1) matrix
    C = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if X[i - 1] == Y[j - 1]:
                C[i][j] = C[i - 1][j - 1] + 1
            else:
                C[i][j] = max(C[i][j - 1], C[i - 1][j])
    return C


def back_track_all(C, X, Y, i, j):
    if i == 0 or j == 0:
        return {""}
    elif X[i - 1] == Y[j - 1]:
        return set([Z + X[i - 1] for Z in back_track_all(C, X, Y, i - 1, j - 1)])
    else:
        R = set()
        if C[i][j - 1] >= C[i - 1][j]:
            R.update(back_track_all(C, X, Y, i, j - 1))
        if C[i - 1][j] >= C[i][j - 1]:
            R.update(back_track_all(C, X, Y, i - 1, j))
        return R


def all_lcs(X, Y):
    """find *all* longest common subsequence"""
    return back_track_all(lcs_length(X, Y), X, Y, len(X), len(Y))


def m_longest_common_subsequence_3(iterable):
    """Find longest common subsequence for all strings in the iterable"""
    lst = list(iterable)

    lcs = lst[0]
    for string in lst[1:]:
        lcs = all_lcs(lcs, string).pop()  # TODO select a LCS instead of popping the last one

    return lcs


# substring


def longest_common_substring(s1, s2):
    m = [[0] * (1 + len(s2)) for i in range(1 + len(s1))]
    longest, x_longest = 0, 0
    for x in range(1, 1 + len(s1)):
        for y in range(1, 1 + len(s2)):
            if s1[x - 1] == s2[y - 1]:
                m[x][y] = m[x - 1][y - 1] + 1
                if m[x][y] > longest:
                    longest = m[x][y]
                    x_longest = x
            else:
                m[x][y] = 0
    return s1[x_longest - longest: x_longest]


def m_longest_common_substring(it):
    lst = list(it)

    lcs = lst[0]
    for string in lst[1:]:
        lcs = longest_common_substring(lcs, string)

    return lcs
