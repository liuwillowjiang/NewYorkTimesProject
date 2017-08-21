import urllib2
import urllib
import requests
import json
import sys
import nltk
import unicodedata
import operator
from nltk.corpus import stopwords
import time

from bs4 import BeautifulSoup

#Used for getting the right path to Matplotlib
import sys
sys.path.append("/Library/Python/2.7/site-packages/")
sys.path.append("/System/Library/Frameworks/Python.framework/Versions/2.7/Extras/lib/python/")

def getText(link):
    resultText = ""
    try:
        f=requests.get(link)
        soup = BeautifulSoup(f.text, "lxml")


        for tag in soup.find_all( "p", { "class" : "story-body-text" } ):
            resultText += unicodedata.normalize('NFKD', tag.text).encode('ascii','ignore').lower()

        if(resultText == ""):
            for tag in soup.find_all( "meta", { "name" : "description" } ):
                content = tag.get("content")
                resultText += content.lower()
                #resultText += unicodedata.normalize('NFKD', content).encode('ascii','ignore')

    except:
        resultText = "Error in getText(). Link: {}".format(link)

    return resultText

nyt_api='57a304d04cda50b91f901d920d6e255a:2:75154687'

def getUrls():
    resultUrls = []
    p=0
    while True:
        try:
            url='http://api.nytimes.com/svc/search/v2/articlesearch.json?&fl=web_url&fq=glocations:("China")&begin_date=20160101&end_date=20160501&sort=oldest&page=' + str(p) + '&api-key=57a304d04cda50b91f901d920d6e255a%3A2%3A75154687'
            p=p+1
            json_obj=urllib2.urlopen(url)
            data=json.load(json_obj)
            print('processing page ' + str(p))
            for item in data['response']['docs']:
                #print item['web_url']
                resultUrls.append(item['web_url'])
                time.sleep(0.5) 
        except:
            print('the last page is ' + str(p))
            break
        
    return resultUrls

def getFreq(text):
    tokens = nltk.word_tokenize(text)
    freq = nltk.FreqDist(tokens)

    #Use that to get the plot
    #freq.plot(50,cumulative=False)
    
    return dict(freq.items())



print "=================================="
print "Getting articles' url"
urls = getUrls()



print "=================================="
print "Getting each article's word frequencies"

allFreqs = []
for url in urls:
    text = getText(url)
    freq = getFreq(text)
    allFreqs.append(freq)
    #print freq
    #print "=================================="

print "=================================="
print "Combining all the frequencies"

combinedFreq = dict([])
for freq in allFreqs:
    for word in freq:
        if word in combinedFreq :
            combinedFreq[word] = combinedFreq[word] + freq[word]
        else:
            combinedFreq[word] = freq[word]

print "=================================="
print "Filtering out stop words"

stopwords = nltk.corpus.stopwords.words('english')
stopwords.extend(['.', ',', '|', '$' , 'said', 'would','mr.','ms.','states','also','one','last','first','could',
                  'year','years','like','many',':','?','time','according','including','percent','two','recent','country','may',
                  'much','make','group','even'])
deleteList = []
for w in combinedFreq:
    if w in stopwords:
        deleteList.append(w)

for w in deleteList:
    del combinedFreq[w]

print "=================================="
print "Sorting the frequencies' in reverse order"

sortedCombinedFreq = sorted(combinedFreq.items(), key=operator.itemgetter(1), reverse=True)

print "=================================="
print "The 100 most frequent words"
print sortedCombinedFreq[:100]
