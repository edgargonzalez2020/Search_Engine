
import math
import os
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
from nltk.tokenize import RegexpTokenizer
from collections import Counter
from collections import OrderedDict
from functools import reduce
from operator import itemgetter
class Engine:
  def __init__(self, path_to_file):
    self.path = path_to_file
    self.files = []
    self.token_count = {}
    self.words = {}
    self.tfidf_document = {}
    self.exclude = set(stopwords.words('english'))
    self.stemmer = PorterStemmer()
    self.prepare_words()

  def prepare_words(self):
    self.file_count = 0
    for filename in os.listdir(self.path):
      self.files.append(filename)
      self.file_count += 1
      f = open(os.path.join(self.path, filename))
      doc = f.read()
      f.close()
      doc = doc.lower()
      self.tokenizer = RegexpTokenizer(r'[a-zA-Z]+')
      tokenized_words=list(map(lambda x: self.stemmer.stem(x),
        filter(lambda y: y not in self.exclude, self.tokenizer.tokenize(doc))))
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
    for filename in self.files:
      for token in self.token_count[filename].keys():
        if filename not in self.tfidf_document:
          self.tfidf_document[filename] = {}
        self.tfidf_document[filename][token] = (1 + math.log(self.token_count[filename][token], 10)) * self.get_idf(token)
      total = 0
      for _, count in self.tfidf_document[filename].items():
        total += (count ** 2)
      total = math.sqrt(total)
      self.tfidf_document[filename] = { token: count / total
          for token, count in self.tfidf_document[filename].items()}
      self.tfidf_document[filename] = { k: v
          for k,v in sorted(self.tfidf_document[filename].items(), key = lambda x: x[1], reverse=True) }
    try:
      _, count = self.words[token]
      return math.log(self.file_count / count , 10)
    except KeyError:
      return -1
  def get_idf(self, token):
    try:
      _,count = self.words[token]
      return math.log(self.file_count / count, 10)
    except KeyError:
      return -1
  def get_weight(self, filename, token):
    if token not in self.token_count[filename]:
      return 0
    return self.tfidf_document[filename][token]
  def get_query(self, qstring):
    tokenized_query = self.tokenizer.tokenize(qstring)
    query_count = Counter(tokenized_query)
    query_count = { k: 1 + math.log(v) for k,v in query_count.items() }
    values = list(query_count.values())
    values[0] = values[0] ** 2
    factor = math.sqrt(reduce(lambda x,y: x + y *y, values))
    query_count = {token: count / factor for token,count in query_count.items()}
    postings_list = self.get_top_10_postings(query_count)
    self.cosine_similarity(postings_list, query_count)
  def cosine_similarity(self, postings_list, query):
    sets = []
    occurences = Counter()
    weights = {}
    total_non_zero_terms = len([x for x in postings_list.values() if x != []])
    print(total)
    for posting in postings_list:
      sets.append(set(postings_list[posting]))
      for file_ in postings_list[posting]:
        occurences[file_] += 1
    common = set.intersection(*sets)
    all_files = set.union(*sets)
    for file_ in occurences:
      for token in query.keys():


  def get_top_10_postings(self, query_count):
    postings_list = { k: [] for k in query_count.keys() }
    limit = 9
    old_value = float('-inf')
    for token in query_count.keys():
      for filename in self.files:
        if token not in self.tfidf_document[filename]:
          continue
        value = self.tfidf_document[filename][token]
        if value >= old_value and limit >= 0:
          postings_list[token].append(filename)
        limit -= 1
      limit = 9
    return postings_list
def tfidf(token, count):
  return (1 + math.log(count , 10)) * engine.get_idf(token)

def main():
  root = './presidential_debates'
  global engine
  engine = Engine(root)
  print("(%s, %.12f)" % query("health insurance wall street"))
def getidf(token):
  return engine.get_idf(token)

def getweight(filename, token):
  return engine.get_weight(filename, token)

def query(qstring):
  return engine.get_query(qstring.lower())
if __name__ == '__main__':
  main()


