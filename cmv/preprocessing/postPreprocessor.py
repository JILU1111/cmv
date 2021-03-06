import re

from spacy.en import English

from cmv.preprocessing.preprocess import normalize_from_body
from cmv.preprocessing.metadata import Metadata
from cmv.preprocessing.discourseClassifier import DiscourseClassifier
from cmv.preprocessing.frameClassifier import FrameClassifier

class PostPreprocessor:
    cmv_pattern = re.compile('cmv:?', re.IGNORECASE)
    nlp = English()
    
    def __init__(self, data, op=False, lower=False, frames=True, discourse=False):
        '''
        data - text, a string
        op - boolean indicating whether to remove the auto-moderator additions to OPs in CMV
        lower - boolean indicating whether to lowercase
        discourse - boolean for discourse features
        frames - boolean for frame semantic features
        '''
        
        self.data = data
        self.op = op
        self.lower = lower

        self.metadata = Metadata()
        
        self.discourseClassifier = None 
        if discourse:
            self.discourseClassifier = DiscourseClassifier()

        self.frameClassifier = None
        if frames:
            self.frameClassifier = FrameClassifier()

        self._processedData = None
        
    def cleanup(self, text):
        
        cleaned_text = normalize_from_body(text, op=self.op, lower=self.lower)
        cleaned_text = self.cmv_pattern.sub('', cleaned_text)
        cleaned_text = cleaned_text.replace('\t', ' ')

        parsed_text = [self.nlp(unicode(i)) for i in cleaned_text.split('\n')]
        return parsed_text
        
    def preprocess(self, text):
        '''
        takes in a text string and returns a list of metadata dictionaries, one for each sentence
        
        text - a document string
        '''
        
        parsed_text = list(self.cleanup(text))
        split_sentences = []
        for paragraph in parsed_text:
            for sent in paragraph.sents:
                split_sentences.append(sent)

        processed_post = self.metadata.addMetadata(split_sentences)
        if self.frameClassifier:
            processed_post = self.frameClassifier.addFrames(processed_post)        
        if self.discourseClassifier:
            processed_post.update(self.discourseClassifier.addDiscourse(processed_post))

        return processed_post

    @property
    def processedData(self):
        if self._processedData is None:
            self._processedData = self.preprocess(self.data)
        return self._processedData
                    
    
    
