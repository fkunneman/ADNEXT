
import frog

class Frogger:

    def __init__(self,t):
        self.frogger = frog.Frog(frog.FrogOptions(threads=t),"/vol/customopt/uvt-ru/etc/frog/frog-twitter.cfg")

    def return_entities(self,sentences):
        for sentence in sentences:
            ners = []
            tokens = self.frogger.process(sentence)
            for token in tokens:
                if token['ner'] != 'O':
                    ners.append(token['ner'])
            print(sentence,ners)
        

