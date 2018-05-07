from __future__ import division
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.shortcuts import render
from django.views.generic import View
from django.http import HttpResponse

from rest_framework.views import APIView
from rest_framework.response import Response

User = get_user_model()

class HomeView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'charts4.html', {"customers": 10})

class DataView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'charts2.html', {"customers": 10})


def get_data(request, *args, **kwargs):
    import PyPDF2
    import re
    from nltk.corpus import reuters
    from nltk.stem.snowball import SnowballStemmer
    from nltk.stem import PorterStemmer
    import nltk
    import datetime, re, sys
    from sklearn.feature_extraction.text import TfidfVectorizer
    from random import randint
    import math
    
    #text = []
    a = ""
    pdfFileObj = open('/home/ubuntu/mysite/polls/vaccine.pdf', 'rb')
    pdfReader = PyPDF2.PdfFileReader(pdfFileObj)

    pdfWriter = PyPDF2.PdfFileWriter()

    for page in range(pdfReader.numPages):
        
        text = pdfReader.getPage(page).extractText().replace('\n', ' ')
        text = text.replace('\n', ' ')
        #text = text.replace('\t', ' ')
        a += text
        #p = text.extractText().strip('\n\n')
        #add +=text
        #a += text
    #a.replace('Evaluation', 'influenza')
    a = re.sub(r"[0-9]+[(.;,)]+","",a)

    def tokenize_and_stem(text):
        tokens = [word for sent in nltk.sent_tokenize(text) for word in nltk.word_tokenize(sent)]
        filtered_tokens = []
        # filter out any tokens not containing letters (e.g., numeric tokens, raw punctuation)
        stemmer=PorterStemmer()
        for token in tokens:
            if re.search('[a-zA-Z]', token):
                filtered_tokens.append(token)
        stems = [stemmer.stem(t) for t in filtered_tokens]
        return stems

    token_dict = {}
    for article in reuters.fileids():
        token_dict[article] = reuters.raw(article)
            
    tfidf = TfidfVectorizer(tokenizer=tokenize_and_stem, stop_words='english', decode_error='ignore')
    #print('building term-document matrix... [process started: ' + str(datetime.datetime.now()) + ']')
    sys.stdout.flush()

    tdm = tfidf.fit_transform(token_dict.values()) # this can take some time (about 60 seconds on my machine)
    #print('done! [process finished: ' + str(datetime.datetime.now()) + ']')

    feature_names = tfidf.get_feature_names()

    new_list = ""
    article_id = randint(0, tdm.shape[0] - 1)
    article_text = text
    #for b in a.split('.'):
    sent_scores = []
    for sentence in nltk.sent_tokenize(a):
        score = 0
        sent_tokens = tokenize_and_stem(sentence)
        for token in (t for t in sent_tokens if t in feature_names):
            score += tdm[article_id, feature_names.index(token)]
        sent_scores.append((score / len(sent_tokens), sentence))

    summary_length = int(math.ceil(len(sent_scores) / 5))
    sent_scores.sort(key=lambda sent: sent[0])
    #print ('*** SUMMARY ***')
    for summary_sentence in sent_scores[:summary_length]:
    
    	new_list += summary_sentence[1] + '\n'
    #new_list=new_list.replace(".", "\n")
    response = HttpResponse(new_list, content_type='text/plain')
    return response
    
	#return render(data, 'charts.html') # http response


class ChartData(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, format=None):
        import PyPDF2
        from nltk.tokenize import word_tokenize
        from nltk.corpus import stopwords
        from collections import Counter

        text = ""
        pdfFileObj = open('/home/ubuntu/mysite/polls/vaccine.pdf', 'rb')
        pdfReader = PyPDF2.PdfFileReader(pdfFileObj)

        #print(pdf.numPages)
        for page in range(pdfReader.numPages):
                pageObj = pdfReader.getPage(page).extractText()
                text += pageObj

        text = text.replace('\n', ' ')
        tok = word_tokenize(text)
        
        s = []
        for a in tok:
                s.append(a.lower())
        
        words2 = open('/home/ubuntu/words.txt', 'r')
        
        words3 = []
        words3 = words2.read()  

        punctuations = ['(',')',';',':','[',']',',', '...', '.', '&']

        stop_words = stopwords.words('english')
        
        keywords = [word for word in s if not word in stop_words and not word in punctuations and not word in words3]

        cnt = Counter()
        words = []
        count1 = []
        for word in keywords:
                cnt[word] += 1
        top = cnt.most_common(10)
        for (a, b) in top:
                words.append(a)
                count1.append(b)

        #qs_count = User.objects.all().count()
        #labels = ["Users", "Blue", "Yellow", "Green", "Purple", "Orange"]
        #default_items = [qs_count, 23, 2, 3, 12, 2]
        data = {
                "labels": words,
                "default": count1,
        }
        return Response(data)
