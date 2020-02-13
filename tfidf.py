import os
import math
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
from nltk.tokenize import RegexpTokenizer
from collections import Counter

class Processor:
  def __init__(self, path_to_dir):
    self.path = path_to_dir
    self.words = {} # Key: Filename, Value: tokenized words
    self.tf_idf = {}
    self.files = [] # List of files
    self.exclude = stopwords.words('english')
    self.stemmer = PorterStemmer()
    self.prepare_words()
  def prepare_words(self):
    count = 0
    for filename in os.listdir(self.path):
      count += 1
      self.files.append(os.path.join(self.path,filename))
      full_name = os.path.join(self.path, filename)
      f = open(full_name, 'r', encoding='UTF-8')
      doc = f.read()
      f.close()
      doc = doc.lower()
      tokenizer = RegexpTokenizer(r'[a-zA-Z]+')
      tokenized_words = tokenizer.tokenize(doc)
      filtered_words =  [self.stemmer.stem(word) for word in tokenized_words]
      self.words[filename] = Counter(filter(lambda x: x not in self.exclude, filtered_words))
    self.document_count = count

    for filename, counts in self.words.items():
      for token, count in counts.items():
        idf = self.get_idf(token)
        tf = 1 + math.log(count, 10)
        tfidf = tf * idf
        if filename not in self.tf_idf:
          self.tf_idf[filename] = {}
        else:
          self.tf_idf[filename][token] = tfidf

  def get_idf(self,token):
    found = False
    count = 0
    for k,v in self.words.items():
      if token in v:
        found = True
        count += 1
    return math.log(self.document_count / count, 10) if found else -1
  def get_weight(self,filename, token):
    counts = self.tf_idf[filename]
    factor = math.sqrt(sum([x ** 2 for x in counts.values()]))
    return counts[token] / factor

def main():
  root = './presidential_debates'
  global engine
  engine = Processor(root)
  print("%.12f" % getweight("1976-10-22.txt","agenda"))
def getidf(token):
  print(engine.get_idf(token))

def getweight(filename, token):
  return engine.get_weight(filename, token)

if __name__ == '__main__':
  main()
