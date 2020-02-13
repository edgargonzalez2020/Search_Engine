import math
import os
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
from nltk.tokenize import RegexpTokenizer
from collections import Counter
from functools import reduce
class Engine:
  def __init__(self, path_to_file):
    self.path = path_to_file
    self.token_count = {}
    self.words = {}
    self.exclude = set(stopwords.words('english'))
    self.stemmer = PorterStemmer()
    self.prepare_words()
  def prepare_words(self):
    self.file_count = 0
    for filename in os.listdir(self.path):
      self.file_count += 1
      f = open(os.path.join(self.path, filename))
      doc = f.read()
      f.close()
      doc = doc.lower()
      #if filename not in self.token_count:
      #  self.token_count[filename] = {}
      #tokenizer = RegexpTokenizer(r'[a-zA-Z]+')
      #all_words = tokenizer.tokenize(doc)
      #tokenized_words = []
      #for x in all_words:
      #  if x in self.exclude:
      #    continue
      #  stemmed = self.stemmer.stem(x)
      #  if stemmed not in self.token_count[filename]:
      #    self.token_count[filename][stemmed] = 0
      #  self.token_count[filename][stemmed] += 1
      #  tokenized_words.append(stemmed)

      tokenized_words = map(lambda x: self.stemmer.stem(x), filter(lambda y: y not in self.exclude, tokenizer.tokenize(doc)))
      self.token_count[filename] = Counter(tokenized_words)
      counted = {}
      for word in tokenized_words:
        if word not in self.words:
          self.words[word] = (self.token_count[filename][word],0)
        if word not in counted:
          counted[word] = False
        if not counted[word]:
          self.words[word] = (self.token_count[filename][word], self.words[word][1] + 1)
          counted[word] = True
  def get_idf(self, token):
    try:
      _, count = self.words[token]
      return math.log(self.file_count / count , 10)
    except KeyError:
      return -1
  def get_weight(self, filename, token):
    if token not in self.token_count[filename]:
      return 0
    tokens = { k: tfidf(k,v) for k,v in self.token_count[filename].items()  }
    total = 0
    for _,count in tokens.items():
      total += (count ** 2)
    total = math.sqrt(total)
    return tokens[token] / total
def tfidf(token, count):
  return (1 + math.log(count , 10)) * engine.get_idf(token)
def main():
  root = './presidential_debates'
  global engine
  engine = Engine(root)
  print("%.12f" % getweight("2012-10-03.txt","health"))
def getidf(token):
  return engine.get_idf(token)
def getweight(filename, token):
  return engine.get_weight(filename, token)
if __name__ == '__main__':
  main()


