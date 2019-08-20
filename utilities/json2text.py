from textblob import TextBlob
import argparse
import json
import re
import sys
import imp
imp.reload(sys)

# http://jira.demandmedia.net/browse/CME-1568
class FileReader(object):
    def __init__(self, path="", out=""):
        self.path = path
        self.out_path = out

    def __iter__(self):
        with open(self.path) as handle:
            for line in handle:
                yield line

class CategoryReader(FileReader):
    def __init__(self, **kargs):
        super(CategoryReader, self).__init__(**kargs)

    def _text_worker(self):
        try:
            self.category = self.obj['fixed_category'][0]['title']
        except:
            self.category = ''

    def process(self):
        with open(self.out_path, 'wt') as out:
            for line in self.__iter__():
                self.obj = json.loads(line)
                self._text_worker()
                if self.category is not None:
                    print(self.obj['_id'], self.category, sep="\t", file=out)

class TextReader(FileReader):
    def __init__(self, **kargs):
        super(TextReader, self)
        super(TextReader, self).__init__(**kargs)

    def _text_worker(self):
        self.text = ""
        self.keys = ['content',
                    # 'tip',
                     #'warning',
                     'title',
                     #'things_needed',
                     'transcript',
                     # 'summary',
##                     'description',
                     'mediaurlanchortext', # CuratedList
                     'text', # Transcript
                     ]
        self.regex = "(\n|\*|<br>|'\[|\[|\]|\(http.*\)|_)"
        def _interpret(blob):

            if isinstance(blob, list):
                for obj in blob:
                    _interpret(obj)
            elif isinstance(blob, dict):
                for k, value in list(blob.items()):
                    if k in self.keys and value:

                        if 'title' in k:# and value.lower().startswith('step'):
                            continue


                        elif 'description' in  k:
                            self.text = str(value).replace('\n','') + self.text

                        elif isinstance(value, str):
                            self.text += " " + str(value).replace('\n','')


                    else:
                        if 'references' not in k and 'fixed_category' not in k:
                            _interpret(value)

        _interpret(self.obj)
##        _interpret({'sections': self.obj['_archive'].get('sections',{}), 'description':self.obj['_archive'].get('description',''), 'summary':self.obj['_archive'].get('summary','')})


##        self.text = re.findall('[a-z]+', HTMLParser.HTMLParser().unescape(self.text.replace('\n','').lower()))


    def process(self):
        with open(self.out_path, 'wt') as out:
            for line in self.__iter__():
                self.obj = json.loads(line)
                #if '.html' in self.obj['_id']:
                self._text_worker()
                if self.text is not None:
                    print(self.obj['_id'], self.text, sep="\t", file=out)

    def json2text(self, json_object):
        self.obj = json_object
        self._text_worker()
        if (self.text is not None):
            return self.obj['_id'], self.text




if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="""Provide path to mongoexport json file""")
    parser.add_argument('-f', '--file', type=str, help="Path to JSON file")
    parser.add_argument('-o', '--out', type=str, help="Path to output file")
    args = parser.parse_args()

    fr = TextReader(path=args.file, out=args.out)
    # fr = CategoryReader(path=args.file, out=args.out)
    fr.process()
