import collections
from itertools import chain, zip_longest
from pprint import pprint

from django.db.models import Q

from .models import Product

# Product search helpers

STOP_WORDS = ['de', 'à', 'le', 'la', 'aux']


def clean_search_result(result_list: list):
    """
    take a result list  and remove duplicates tuple ignoring second element of the tuple.
        :param result_list: list of tuple like (product, weight)
        :type result_list: list
    """

    # already seen value
    seen = set()
    for item in result_list:
        compare = item[0]
        # yield item only if it's not already in seen set
        if compare not in seen:
            seen.add(compare)
            yield item


def remove_none(list_to_clean: list):
    """
    Remove all None value from provided list.
        :param list_to_clean: the list to remove None value in
        :type list_to_clean:  list
    """
    return [value for value in list_to_clean if value is not None]


def search_product(terms: str):
    """
    Use provided terms to return a list of product with relevancy weigth
        :param terms: searched terms in products table
        :type terms: str
    """
    result = []

    # transform terms to list
    base_terms_list = terms.split(' ')

    if base_terms_list == ['']:
        return []

    # create combination of terms
    temp_terms_groups = zip_longest(*[base_terms_list[i:] for i in range(len(base_terms_list))])

    # Remove None values from terms combinations
    cleanded_terms_groups = map(remove_none, temp_terms_groups)

    # sort terms combinations by length
    sorted_terms_groups = sorted(cleanded_terms_groups, key=lambda x: len(x), reverse=True)

    for terms_list in sorted_terms_groups:

        terms_str = ' '.join(terms_list)
        query_filter_list = []
        weigth = len(terms_list)

        # search exact terms combination
        if terms_str not in STOP_WORDS:
            result += [(product, weigth * 2) for product in Product.objects.filter(product_name__icontains=terms).exclude(nutrition_grade_fr='')]

            # search unordered terms combination
            for word in terms_list:
                query_filter_list.append(Q(product_name__icontains=word))

            result += [(product, (weigth * 2) - 1) for product in Product.objects.filter(*query_filter_list).exclude(nutrition_grade_fr='')]

    # remove duplicate values
    cleaned_result = list(clean_search_result(result))

    # sort results
    sorted_result = sorted(cleaned_result, key=lambda x: x[1], reverse=True)

    return sorted_result


# Autocompletion helpers

def clearText(text):

    return text.lower()


def create_corpus():
    corpus = [clearText(element[0]) for element in Product.objects.all().values_list('product_name')]
    return corpus


def get_unigrams(corpus):
    unigrams = {}
    for element in corpus:
        print(element)
        for unigram in element.split(' '):
            if unigram in unigrams:
                unigrams[unigram] += 1
            else:
                unigrams[unigram] = 1
    unigrams = collections.OrderedDict(sorted(unigrams.items(), key=lambda t: t[1], reverse=True))
    pprint(unigrams)


def get_ngrams(corpus, n):
    words = []
    ngrams = {}
    for word_list in [elt.split(' ') for elt in corpus]:
        # print(word_list)
        #     for word in word_list:
        #         words.append(word)
        words = [' '.join(name) for name in zip(*[word_list[i:] for i in range(n)])]
        for ngram in words:
            if ngram in ngrams:
                ngrams[ngram] += 1
            else:
                ngrams[ngram] = 1

    ngrams = collections.OrderedDict(sorted(ngrams.items(), key=lambda t: t[1], reverse=True))
    # for el in words:
    #     print(el)
    pprint(ngrams)
