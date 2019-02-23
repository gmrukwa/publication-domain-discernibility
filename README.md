# publication-domain-discernibility
Analysis of publication domain by statistical analysis of word counts.

# Technical Feasibility Check

Feasibility was checked more-or-less during the topic selection classes.
Proposed flow is as follows:

1) Specify domains to gather papers for
2) Use Microsoft Academic Knowledge API to find publications for a domain
3) Download found publications
4) Convert PDFs to TXT
5) Use TFIDF embedding to produce paper features
6) Use ANOVA / nonparametric alternative for checking, which words make
a difference

## Microsoft Academic Knowledge API

Flow of the API is simple:

1) Select domain by constructing query expression with **interpret**
endpoint.
2) Use **evaluate** endpoint with provided query to find papers in the domain.

Several links may be useful:

- [Interpret domain as an query expression API docs](https://docs.microsoft.com/en-us/azure/cognitive-services/academic-knowledge/interpretmethod)
- [Interpret endpoint test](https://dev.labs.cognitive.microsoft.com/docs/services/56332331778daf02acc0a50b/operations/56332331778daf06340c9666/console)
- [Query evaluation API docs](https://docs.microsoft.com/en-us/azure/cognitive-services/academic-knowledge/evaluatemethod)
- [Evaluate endpoint test](https://dev.labs.cognitive.microsoft.com/docs/services/56332331778daf02acc0a50b/operations/565d753be597ed16ac3ffc03/console)
- [API keys](https://labs.cognitive.microsoft.com/en-us/subscriptions)
- [Paper entity attributes](https://docs.microsoft.com/en-us/azure/cognitive-services/academic-knowledge/paperentityattributes)

## Conversion of PDF to TXT

There is a package `pdftotext` for Python 2 and 3.

- [pip](https://pypi.org/project/pdftotext/)
- [GitHub](https://github.com/jalan/pdftotext)

## Extraction of TFIDF Text Features

There is an implementation in Python within a package called `scikit-learn`.
You can check it [here](https://scikit-learn.org/stable/modules/generated/sklearn.feature_extraction.text.TfidfVectorizer.html).
There are some parameters to play with - understanding them may be key to success.
[Here](https://pl.wikipedia.org/wiki/TFIDF) you can find theoretical background.
