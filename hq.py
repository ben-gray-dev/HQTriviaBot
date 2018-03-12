'''
Created on Jan 16, 2018

@author: Bgray
'''
import nltk
import pprint
from multiprocessing import Pool as ThreadPool
from functools import partial
import pytesseract
from PIL import Image
from PIL import *
import pyscreenshot as ImageGrab
from googleapiclient.discovery import build
ALLOWED_POS = ["NNP", "JJ", "NN", "NNS"]

SERVICE = build("customsearch", "v1", developerKey="AIzaSyDqDHpn-TrHX_Wz6IP5u20oxHyC-ghzYe4")


def isAllowedPOS(word):
    if ALLOWED_POS.__contains__(word):
        return True
    return False        


    
def processImage():
    img = Image.open('hqtest3.png')
    result = pytesseract.image_to_string(img)
    questionMark = result.find("?")
    holder = "\n"
    space_one = result.index(holder, questionMark)
    space_two = result.index(holder,space_one + 1)
    space_three = result.index(holder, space_two + 1)
    question = result[:questionMark]  
    print("question = " + question) 
    
    question = cleanQuestion(question)
    print("parsed q: " + question)
    googleSearch(question)
    option_a = result[space_one:space_two]
    option_b = result[space_two:space_three]
    option_c = result[space_three:]
    print("option a: " + option_a)
    print("option b: " + option_b)
    print("option c: " + option_c)
    performSearch(question, option_a,option_b,option_c)



   
def performSearch(question, option_a, option_b, option_c):
    a_hits = 0
    b_hits = 0
    c_hits = 0
    wordList = question.split(" ")
    inputs = [question + option_a,question + option_b,question + option_c]
    options = [option_a, option_b, option_c]
    pool = ThreadPool(13)
    googleResults = pool.map(googleSearch, inputs)
    frontPageTitles = frontPageHits(question)
    pool.close()
    pool.join()
    for idx in range(len(frontPageTitles)):
        if frontPageTitles[idx].find(str(option_a).strip()) != -1:
            a_hits = a_hits + 1
        elif frontPageTitles[idx].find(str(option_b).strip()) != -1:
            b_hits = b_hits + 1
        elif frontPageTitles[idx].find(str(option_c).strip()) != -1:
            c_hits = c_hits + 1
    frontHits = [a_hits, b_hits, c_hits]
    #wikiResults = pool.map(partial(wikipediaScrape, words = wordList), options)
  
    printAnswer(googleResults,options, frontHits)

def frontPageHits(query):
    titles = []
    res = SERVICE.cse().list(q = query,  
                             cx = '010429115029273274119:yaspvvpboqa',
                            ).execute()
    for idx in range(0,5):
        titles.append(str(res['items'][idx]['title']))
    return titles

def googleSearch( query):
    res = SERVICE.cse().list(q = query,  
                             cx = '010429115029273274119:yaspvvpboqa',
                            ).execute()
    return int(res['searchInformation']['totalResults'])



def wikipediaScrape(query, words):
    hits = 0
   
    service = build("customsearch", "v1", developerKey="AIzaSyArOH08gJ7WFkGbhcTpme-62j98ZBDy2wM")
    res = service.cse().list(q = query,  
                             cx = '003988968989930263059:8aznr9i3kq0',
                            ).execute()
    if (int(res['searchInformation']['totalResults']) > 0):
        summary = res['items'][0]['snippet']
   
        for idx, word in enumerate(words):
            if (summary.find(words[idx]) != -1):
                hits = hits + 1
        return hits

     
     
     
def cleanQuestion(question):
    finalString = " "
    if (question.find('"') != -1):
        firstQuote =  question.index('"')
        lastQuote = question.index('"', firstQuote + 1)
        newQuestion = question[firstQuote + 1:lastQuote]
        question = question.replace(newQuestion, " ")
        return newQuestion
    
    
    question_token = nltk.word_tokenize(question)
    question = nltk.pos_tag(question_token)
  
    for idx,word in enumerate(question):
        if (isAllowedPOS(question[idx][1])):
            finalString = finalString + " " + question[idx][0]
    return finalString

    
    
   
def printAnswer(google, options, frontPage):  
   
    num_a = google[0]
    num_b = google[1]
    num_c = google[2]
    front_a = frontPage[0]
    front_b = frontPage[1]
    front_c = frontPage[2]
    print("A ===== " + str(num_a) + "  hits = " + str(front_a))
    print("B ===== " + str(num_b) + "  hits = " + str(front_b))
    print("C ===== " + str(num_c) + "  hits = " + str(front_c))
    
    answer = ""
    winner = max(num_a,num_b,num_c)


    if winner == num_a:
        answer = str(options[0])
    elif winner == num_b:
        answer = str(options[1])
    else:
        answer = str(options[2])
    print("**************************************************" + "\nANSWER = " + answer + "\n**************************************************")
    
  




def main():
    im=ImageGrab.grab(bbox=(150,400,750,2000)) # X1,Y1,X2,Y2
    im.save("screenshot.png")
    processImage()

   
       




if __name__ == '__main__':
    main()


    
