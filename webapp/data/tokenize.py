# -*- coding: utf-8 -*-

import csv
import os

from janome.tokenizer import Tokenizer
# from gensim import corpora, matutils
# from gensim import corpora

if __name__ == "__main__":
  if not os.path.isfile("faq.tsv"):
    exit
  
  t = Tokenizer()
  
  dict={}
  with open('faq.tsv', 'r', newline='', encoding="UTF-8") as csvfile:
    reader = csv.reader(csvfile, delimiter='\t')
    for row in reader:
      # print('\n'.join(row))
      print("question:\n" + row[0])
      # print("answer:\n" + row[1])
    
      try:
          tokendata = t.tokenize(row[0])
      except:
          continue
      
      words=[]
      for token in tokendata:
      ###   base, part = token.base_form, token.part_of_speech
      ###   
      ###   print(base)
      ###   print(part)
      ###   
      ###   if '動詞' in part:
      ###       # print(base)
      ###       # pass
      ###       words.append(base)
      ###   elif '名詞' in part:
      ###       # print(base)
      ###       # pass
      ###       words.append(base)
      ###   elif '形容詞' in part:
      ###       # print(base)
      ###       # pass
      ###       words.append(base)
        words.append(token.surface)
      
      # print(" ".join(words))
      question=" ".join(words)
      dict[question]=row[1]
    
    ### print(dict)
    ### for key, value in dict.items():
    ###   print("question:\r\n", key)
    ###   print("answer:\r\n", value)

  with open('faq.tokenized.tsv', 'w', newline='', encoding="UTF-8") as csvfile:
    fieldnames = ['question', 'answer']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter='\t', quoting=csv.QUOTE_NONNUMERIC)
    writer.writeheader()
    
    try:
      for key, value in dict.items():
        writer.writerow({'question': key, 'answer': value})
    except Exception as ex:
      print(ex)
