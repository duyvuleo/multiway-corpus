#!/usr/bin/env python3
# By Jon Dehdari, 2017

""" Builds an n-way multilingual corpus.  See the README.md for more details. """

import os

corpus_prefix = 'corpus.'

code_freq_filename = os.path.join('data', 'lang_codes_iso-639-3_freq.tsv')
code_filename = os.path.join('data', 'lang_codes_iso-639-3.tsv')

codes = codes_rev = {}
links = {}
sents = {}
lang_sent_ids = {}
files = {}
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

    # Initialize a set of ID's, for each language
    lang_sent_ids['All'] = set()
    for lang in lang_set:
        lang_sent_ids[lang] = set()

    # Find language with fewest entries in Tatoeba dataset.
    # This was already done to get code_freq_filename, using the following command:
    # cut -f 2 sentences.csv | sort | uniq -c | sort -rn | tr -s ' ' |
    #   cut -d ' ' -f 3 > data/lang_codes_iso-639-3_freq.tsv
    with open(code_freq_filename) as code_freq_file:
        code_freq = code_freq_file.read().split()
        smallest_lang_code = ''
        for code in code_freq:
            if code in lang_set:
                smallest_lang_code = code
        print("Smallest Language:", smallest_lang_code, file=sys.stderr)


    # Storing all translation sentences would be really memory inefficient,
    # so we trade-off space for time, processing this file twice.  First we
    # build-up a set of all sentence-id's for the smallest language.  Then, later,
    # we pass through the file again, printing the sentence if it's a translation
    # of one of the smallest language ID's.
    smallest_lang_sents = {}
    print("Processing sentences from smallest language ...", file=sys.stderr)
    with open('sentences.csv') as sentences_file:
        for line in sentences_file:
            id, code, sent = line.rstrip().split('\t')
            id = int(id)
            if code in lang_set:
                lang_sent_ids[code].add(id)
                lang_sent_ids['All'].add(id)
            if code == smallest_lang_code: # this is a sentence from the smallest lang
                if id in smallest_lang_sents:
                    print("this shouldn't happen")
                else:
                    smallest_lang_sents[id] = {smallest_lang_code: sent}
    print("smallest_lang_sents:", smallest_lang_sents)
    print("lang_sent_ids:", lang_sent_ids)


    # Relations between translation sentences
    print("Processing links ...", file=sys.stderr)
    with open('links.csv') as link_file:
        for line in link_file:
            key, val = line.rstrip().split('\t')
            key = int(key)
            val = int(val)
            # Ignore links that don't involve the languages we're interested in
            if key not in lang_sent_ids['All'] or val not in lang_sent_ids['All']:
                continue
            if key in links:
                links[key].add(val)
            else:
                links[key] = set([val])

    print("links=%s" % links)

    # Open all output files
    for code in lang_set:
        filename = corpus_prefix + code
        try:
            files[code] = open(filename, 'w')
        except OSError as err:
            print(err)

    print("Processing sentences from specified languages ...", file=sys.stderr)
    with open('sentences.csv') as sentences_file:
        for line in sentences_file:
            id, code, sent = line.rstrip().split('\t')
            id = int(id)
            if code in lang_set and code != smallest_lang_code and id in links:
                for small_id in links[id]:
                    # This takes the first translation, ignoring subsequent ones
                    if small_id in smallest_lang_sents and code not in smallest_lang_sents[small_id]:
                        smallest_lang_sents[small_id][code] = sent

    print("smallest_lang_sents:", smallest_lang_sents)

    # Now print sets that have all language translations
    output_sent_num = 0
    for _, val in smallest_lang_sents.items():
        if val.keys() == lang_set:
            output_sent_num += 1
            for lang, sent in val.items():
                print(sent, file=files[lang])

    print("Output %i lines" % output_sent_num)

    # Close all output files
    for _, f in files.items():
        f.close()


if __name__ == '__main__':
    main()
