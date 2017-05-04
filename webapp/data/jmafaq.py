# -*- coding: utf-8 -*-

import csv
import os
import re

try:
    # Python 3
    from urllib import request
except ImportError:
    # Python 2
    import urllib2 as request

from bs4 import BeautifulSoup 

def extractFaqURL(url):
  html = request.urlopen(url).read()
  soup = BeautifulSoup(html, "html.parser")
  faqs = soup.find_all("ul", class_="pagelink mtx")

  urls = []
  for faq in faqs:
    for a in faq.findAll('a'):
      try:
        pattern = r"^http://"
        if re.match(pattern , a.attrs['href']):
          # urls.append(a.attrs['href'])
          pass
        else:
          urls.append(url + a.attrs['href'])
      except Exception as ex:
        print(ex)

  # print(urls)
  return urls

def extractFaqText(url):
  html = request.urlopen(url).read()
  
  soup = BeautifulSoup(html, "html.parser")
  if soup.find_all("div", class_="qa-box"):
    main = soup.find_all("div", class_="qa-box")
  else:
    main = soup.find_all("div", id="main")
  
  for faq in main:
    tag = faq.find("div", class_="mtx")
    if tag:
      tag.clear()
    
    tag = faq.find_all(["h2","p"])
    
    dict={}
    ### print(tag)
    for t in tag:
      del(t["id"])
      del(t["mtx"])
      # print(t)
      # print(dir(t))
      # print(t.name)
      if t.name=="h2":
        ### print("Q !!!")
        ### print(str(t.text).strip('\n\r'))
        question=str(t.text).strip('\n\r').replace('\r','').replace('\n','')
        dict[question]=""
      else:
        ### print("A !!!")
        ### print(t.text + "\n")
        ### print(str(t.text).strip('\n\r'))
        answer=str(t.text).strip('\n\r').replace('\r','').replace('\n','')
        if dict[question]:
          answer=dict[question] + answer
        dict[question]=answer
      
    ### print(dict)
    for key, value in dict.items():
      print("question:\r\n", key)
      print("answer:\r\n", value)
    
  return dict

if __name__ == "__main__":
  if os.path.isfile("faq.tsv"):
    os.remove("faq.tsv")
  
  with open('faq.tsv', 'w', newline='', encoding="UTF-8") as csvfile:
    fieldnames = ['question', 'answer']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter='\t', quoting=csv.QUOTE_NONNUMERIC)
    writer.writeheader()
    
    url = "http://www.jma.go.jp/jma/kishou/know/faq/"
    urls = extractFaqURL(url)
    ### urls = ["http://www.jma.go.jp/jma/kishou/know/faq/faq1.html"]
    ### urls = ["http://www.jma.go.jp/jma/kishou/know/faq/faq25.html"]
    for url in urls:
      if url in {"http://www.jma.go.jp/jma/kishou/know/faq/../yougo_hp/mokuji.html", "http://www.jma.go.jp/jma/kishou/know/faq/../../minkan/q_a_m.html", "http://www.jma.go.jp/jma/kishou/know/faq/../../minkan/q_a_s.html"}:
        pass
      else:
        try:
          print(url)
          dict=extractFaqText(url)
          
          for key, value in dict.items():
            writer.writerow({'question': key, 'answer': value})
        except Exception as ex:
          print(ex)
