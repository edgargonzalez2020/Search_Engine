import copy
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
    tokenized_query = list(map(lambda x: self.stemmer.stem(x), tokenized_query))
    query_count = Counter(tokenized_query)
    query_count = { k: 1 + math.log(v) for k,v in query_count.items() }
    values = list(query_count.values())
    values[0] = values[0] ** 2
    factor = math.sqrt(reduce(lambda x,y: x + y *y, values))
    query_count = {token: count / factor for token,count in query_count.items()}
    postings_list, all_files = self.get_top_10_postings(query_count)
    return self.cosine_similarity(postings_list, query_count, all_files)
  def cosine_similarity(self, postings_list, query, all_files):
    if len([x for x in postings_list.values() if x == [] ]) == len(postings_list.keys()):
      return None, 0
    sets = []
    counts = {files:len([x for x in postings_list.values() if x != []]) for files in all_files}
    last = { k: v[-1] for k,v in postings_list.items() if v != [] }
    occurences = Counter()
    weights = {k: 0 for k in all_files}
    for posting in postings_list:
      sets.append(set(postings_list[posting]))
      for file_ in postings_list[posting]:
        occurences[file_] += 1
    for files in all_files:
      for token in query.keys():
        if files in postings_list[token] and counts[files] > 0:
          dot_product = query[token] * self.tfidf_document[files][token]
          weights[files] += dot_product
          counts[files] -= 1
          postings_list[token].remove(files)
        else:
          if postings_list[token] != [] and counts[files] > 0:
            dot_product = query[token] * self.tfidf_document[last[token]][token]
            weights[files] += dot_product
            counts[files] -= 1
    maximum = max(weights, key=weights.get)
    if occurences[maximum] != len(query.keys()):
      return "fetch more", 0
    return (maximum, weights[maximum]) if occurences[maximum] == len(query.keys()) else ("fetch more", 0)

  def get_top_10_postings(self, query_count):
    postings_list = { k: [] for k in query_count.keys() }
    all_files = []
    for token in query_count.keys():
      top_10 = sorted([(files, self.tfidf_document[files])
        for files in self.files if token in self.tfidf_document[files]], key=lambda kv: kv[1][token], reverse=True)
      postings_list[token] = [x[0] for x in top_10[:10]]
      all_files.extend([x[0] for x in top_10])
    return postings_list, all_files
def tfidf(token, count):
  return (1 + math.log(count , 10)) * engine.get_idf(token)

def main():
  root = './presidential_debates'
  global engine
  engine = Engine(root)
  print("(%s, %.12f)" % query("vector entropy"))
  print("(%s, %.12f)" % query("terror attack"))
  print("(%s, %.12f)" % query("health insurance wall street"))
  print("(%s, %.12f)" % query("particular constitutional amendment"))
def getidf(token):
  return engine.get_idf(token)

def getweight(filename, token):
  return engine.get_weight(filename, token)

def query(qstring):
  return engine.get_query(qstring.lower())
if __name__ == '__main__':
  main()


