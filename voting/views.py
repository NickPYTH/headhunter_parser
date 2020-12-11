from django.shortcuts import render
from django.template.response import TemplateResponse
from django.http import HttpResponse

import nltk 
from nltk.probability import FreqDist
from nltk import word_tokenize
nltk.download('punkt')
nltk.download('wordnet')

from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
import pandas as pd

from nltk.stem import PorterStemmer, WordNetLemmatizer
from nltk.stem.snowball import SnowballStemmer
from nltk.corpus import wordnet

from nltk.corpus import stopwords
nltk.download('stopwords')

from sklearn.ensemble import RandomForestClassifier
import requests
# Create your views here.

def vote_list(request):
    return render(request, "index.html")

def index(request):
    if request.method == "POST":
        name = request.POST.get("search")
        num = request.POST.get("vac_num")
        area = request.POST.get("area")
        options = request.POST.get("options")

        stop_words = stopwords.words("russian")
        search = ""
        search += name + " AND " + area
        if options != None and len(options) != 0:
            search += " ("
            options_list = str(options).split()
            for word in options_list:
                search += " OR " + word
            search += " )"

        x=[]
        vacancies_num = int(num)
        euro_val = 88
        usd_val = 75
        tax = 0.13
        for i in range(vacancies_num):
            url = 'https://api.hh.ru/vacancies'
            par = {
                    'text' : search, 
                }
            r = requests.get(url, params=par)
            e=r.json()
            x.append(e)

            for j in x:

                for i in j['items']:
                    if i['salary'] != None:
                        if isinstance(i['salary'], int):
                            salary = i['salary']
                        else:
                            if i['salary']['from'] == None:
                                i['salary']['from'] = 0
                            if i['salary']['to'] == None:
                                i['salary']['from'] = 1000000
                            if i['salary']['currency'] == "RUR":
                                if i['salary']['to'] == None:
                                    i['salary']['to'] = i['salary']['from']
                                else:
                                    i['salary']['to'] = i['salary']['to']

                            if i['salary']['currency'] == "USD":
                                i['salary']['from'] = i['salary']['from'] * usd_val
                                if i['salary']['to'] == None:
                                    i['salary']['to'] = i['salary']['from']
                                else:
                                    i['salary']['to'] = i['salary']['to'] * usd_val

                            if i['salary']['currency'] == "EUR":
                                i['salary']['from'] = i['salary']['from'] * euro_val
                                if i['salary']['to'] == None:
                                    i['salary']['to'] = i['salary']['from']
                                else:
                                    i['salary']['to'] = i['salary']['to'] * euro_val

                            if i['salary']['from'] != None and i['salary']['to'] != None:
                                salary = (i['salary']['from'] + i['salary']['to'])/2
                            else:
                                salary = i['salary']['from']

                            if i['salary']['gross'] == False and salary != None:
                                salary *= 1-tax
                                i['salary'] = int(salary)
                            
                            i['snippet'] = i['snippet']

                            #i['area'] = i['area']['name']

        
        df = pd.DataFrame(x[0]['items'])
        if df.empty:
            data = {
                "results" : 0,
            }
            return render(request, "index.html", context=data)

        for i in range(vacancies_num):
            if i != 0:
                df = df.append(x[i]['items'])
        
        df.drop([
                'premium', 'type', 'address', 'response_url', 'sort_point_distance', 
                'employer', 'created_at', 'published_at','archived', 'apply_alternate_url', 
                'insider_interview', 'url', 'alternate_url', 'relations', 
                'contacts', 'schedule', 'working_days', 'working_time_intervals',
                'working_time_modes', 'accept_temporary', 'department', 'response_letter_required',
                'has_test', 'id'], axis='columns', inplace=True)
        df.reset_index().to_csv('hh.csv', header=False, index=False)

        my_stop_words = [',', '.', '...', '/', '<', '>', '/highlighttext', '(', ')'
        ,'highlighttext', '&', 'quot', ';', 'c', ':', ':', '»', '«', 'т.е', '–', '-' ]
        for word in my_stop_words:
            stop_words.append(word)

        sentences_without_stop_words = []
        for record in df.snippet:
            sentence = record['requirement']
            if sentence != None:
                words = nltk.word_tokenize(sentence)
                without_stop_words = [word for word in words if not word in stop_words]
                sentences_without_stop_words.append(without_stop_words)

        exceptions_word = ['АСУ', 'Core', 'Django']
        sentences_stemmer_words = []
        stemmer = PorterStemmer()
        sentence_med = []
        for sentence in sentences_without_stop_words:
            for word in sentence:
                if word not in exceptions_word:
                    sentence_med.append(stemmer.stem(word))
                else:
                    sentence_med.append((word))
            sentences_stemmer_words.append(sentence_med)
            sentence_med = []

        soft_skills = []
        soft_skills_statistic = []
        for sentence in sentences_stemmer_words:
            for word in sentence:
                if word in soft_skills:
                    soft_skills_statistic.append(word)

        one_sentence = ''
        glue_sentences = []
        for sentence in sentences_stemmer_words:
            for word in sentence:
                one_sentence += word + ' '
            glue_sentences.append(one_sentence)
            one_sentence = ''
        
        text = ''
        for i in glue_sentences:
            text += i

        text_tokens = word_tokenize(text)
        pairs = []
        i = 0
        temp = ''
        for token in text_tokens:
            if i == 1:
                pairs.append(temp)
                i = 0
                temp = ''
                temp = token
            else:
                i += 1
                temp += ' ' + token
        text = nltk.Text(pairs)
        fdist = FreqDist(text)

        lst = fdist.most_common(10)
        count = 1
        new_lst = []
        for i in lst:
            new_lst.append([i, count])
            count+=1

        res = {
            "data" : new_lst,
            "len" : range(10),

        }
     

        data = {
            "name" : name,
            "num" : num,
            "res" : res,
            "results" : 1,
        }
        return render(request, "index.html", context=data)
    
    else:
        data = {
                "results" : 2,
            }
        return render(request, "index.html", context=data)
