from collections import defaultdict


def read_csv(filename):
    feature_to_word = defaultdict(list)
    words = []
    with open(filename) as file:
        for line in file:
            inflection, fv = line.split(',')

            # ignore any inflection that contains spaces
            if ' ' in inflection:
                continue

            for feature in fv.strip().split(';'):
                feature_to_word[feature].append(inflection)
                words.append(inflection)
    print(words)
    print_dict(feature_to_word)


def print_dict(d):
    print(d.keys())
    for key, value in d.items():
        print("{}: {}".format(key, ', '.join(value)))


def main():
    read_csv('test_tur.csv')


if __name__ == '__main__':
    main()
