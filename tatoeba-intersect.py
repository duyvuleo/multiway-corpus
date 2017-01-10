#!/usr/bin/env python3
# By Jon Dehdari, 2017

import os

maxlinks = 1000000

code_freq_filename = os.path.join('data', 'lang_codes_iso-639-3_freq.tsv')
code_filename = os.path.join('data', 'lang_codes_iso-639-3.tsv')

codes = {}
codes_rev = {}
links = {}
sents = {}
lang_set = set()

def main():
    import sys

    langs = sys.argv[1:]

    # Bijective mapping between ISO 639-3 language codes and their (macro-)language name.  Eg. eng:'English'
    with open(code_filename) as code_file:
        for line in code_file:
            code, lang = line.rstrip().split('\t')
            codes[code] = lang
            codes_rev[lang] = code

    # Normalize user-supplied langage names/codes to codes (eg. eng)
    for lang in langs:
        if lang in codes: # code is in ISO standard
            lang_set.add(lang)
        elif lang in codes_rev:
            lang_set.add(codes_rev[lang])
        else:
            print('"%s" is neither an ISO 639-3 code nor ISO 639-3 (macro-)language name' % lang, file=sys.stderr)
            sys.exit()

    # Find language with fewest entries in Tatoeba dataset.
    # This was already done to get code_freq_filename, using the following command:
    # cut -f 2 sentences.csv | sort | uniq -c | sort -rn | tr -s ' ' |
    #   cut -d ' ' -f 3 > data/lang_codes_iso-639-3_freq.tsv
    with open(code_freq_filename) as code_freq_file:
        code_freq = code_freq_file.read().split()
        least_freq_code = ''
        for code in code_freq:
            if code in lang_set:
                least_freq_code = code
        print("Smallest Language:", least_freq_code, file=sys.stderr)


    # Relations between translation sentences
    with open('links.csv') as link_file:
        for line in link_file:
            key, val = line.rstrip().split('\t')
            key = int(key)
            val = int(val)
            # links take up a lot of memory
            if key > maxlinks or val > maxlinks:
                continue
            if key in links:
                links[key].add(val)
            else:
                links[key] = set([val])

    # Translation sentences
    with open('sentences.csv') as sentences_file:
        for line in sentences_file:
            id, code, sent = line.rstrip().split('\t')
            if code in lang_set:
                ...



if __name__ == '__main__':
    main()
