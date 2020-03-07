import math
import os
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
from nltk.tokenize import RegexpTokenizer
from collections import Counter
from collections import defaultdict
from functools import reduce

def getidf(token):
  pass
def getweight(filename, token):
  pass
def query(qstring):
  pass

class Search:
  def __init__(self, path_to_file):
    self.path = path_to_file
    self.files = []
    self.tokens = {}
    self.stemmer = PorterStemmer()
    self.tokenizer = RegexpTokenizer(r'[a-zA-z]+')
    self.stopwords = stopwords.words('english')
    self.prepare_docs()
  def prepare_docs(self):
    for filename in os.listdir(self.path):
      self.files.append(filename)
      f = open(os.path.join(self.path, filename))
      doc = f.read().lower()
      f.close()
      tokenized_words = list(map(lambda x: self.stemmer.stem(x),
                             list(filter(lambda x: x not in self.stopwords, self.tokenizer.tokenize(doc)))))
      self.tokens[filename] = Counter(tokenized_words)
    #pre-proccesing for getidf
    self.tfidf_vectors = {k: None for k in self.files}
    self.tfidf_words = defaultdict(int)
    for files in self.files:
      for token in self.tokens[files]:
        self.tfidf_words[token] += 1
        self.tfidf_vectors[files] = {token: (1 + math.log10(count)) * self.get_idf(token) for token,count in self.tokens[files].items()}

    #{k:v for k,v in sorted(self.normalize({token: 1 + math.log10(count) for token,count in self.tokens[files].items()}).items(), key = lambda x: x[1], reverse=True)}
  def get_idf(self, token):
    n = self.tfidf_words[token]
    return math.log10(len(self.files) / n) if n != 0 else -1
  def normalize(self, vector):
    factor = math.sqrt(sum(i ** i for i in vector.values()))
    return {k: v / factor for k,v in vector.items()}

def main():
  search = Search('./presidential_debates')

if __name__ == '__main__':
  main()
