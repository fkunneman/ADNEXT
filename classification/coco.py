#!/usr/bin/env 

import colibricore

class Coco:

    def __init__(self, tmp, txtfile):
        self.classfile = tmp + ".colibri.cls"
        self.textfile = txtfile
        self.corpusfile = tmp + ".colibri.dat"

        self.classencoder = colibricore.ClassEncoder()
        self.classencoder.build(self.textfile)
        self.classencoder.save(self.classfile)
        self.classencoder.encodefile(self.textfile, self.corpusfile)
        self.classdecoder = colibricore.ClassDecoder(self.classfile)

    def return_counts(self, tokens, length):
        options = colibricore.PatternModelOptions(mintokens = tokens, maxlength = length)
        patternmodel = colibricore.UnindexedPatternModel()
        patternmodel.train(self.corpusfile, options)
        pattern_counts = []
        for pattern, count in patternmodel.items():
            pattern_counts.append(pattern.tostring(self.classdecoder), count)
        sorted_pattern_counts = sorted(pattern_counts, key = lambda k : k[1], reverse = True)
        return sorted_pattern_counts
