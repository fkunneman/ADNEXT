#! /usr/bin/env python

from __future__ import division

from collections import defaultdict
import math

from pynlpl import evaluation
from sklearn.metrics import auc
import time_functions

class Evalset():

    def __init__(self):
        self.instances = []

    def add_instances(self,instances,score=False,text=False,tid=False):
        for instance_tokens in instances:
            instance = Evalset.Instance(instance_tokens[0],instance_tokens[1])
            if score:
                instance.set_score(instance_tokens[2])
            if text:
                instance.set_text(instance_tokens[3])
            else:
                instance.set_text("-")
            if tid:
                instance.set_tid(instance_tokens[4])
            else:
                instance.set_tid("-")
            self.instances.append(instance)

    def calculate_general(self):
        self.ce = evaluation.ClassEvaluation()
        for instance in self.instances:
            self.ce.append(instance.label,instance.classification) 

    def calculate_outcome(self):
        results = [["Class","Precision","Recall","F1","TPR","FPR","AUC","Samples",
            "Classifications","Correct"]]
        for label in sorted(list(set(self.ce.goals))):
            label_results = [self.ce.precision(cls=label),self.ce.recall(cls=label),self.ce.fscore(cls=label),
                self.ce.tp_rate(cls=label),self.ce.fp_rate(cls=label),
                auc([0,self.ce.fp_rate(cls=label),1],[0,self.ce.tp_rate(cls=label),1]),
                (self.ce.tp[label] + self.ce.fn[label]),(self.ce.tp[label] + self.ce.fp[label]),self.ce.tp[label]]
            results.append([label] + [round(x,2) for x in label_results])
        micro_results = [self.ce.precision(),self.ce.recall(),self.ce.fscore(),self.ce.tp_rate(),self.ce.fp_rate(),
            auc([0,self.ce.fp_rate(),1],[0,self.ce.tp_rate(),1]),len(self.ce.observations),len(self.ce.observations)]
        results.append(["micro"] + [str(round(x,2)) for x in micro_results] + [" "])
        return results

    def calculate_rmse(self):
        responsiveness_vals = []
        rmse_vals = []
        ae_vals = []
        plot_vals = defaultdict(list)
        d = False
        before = 0
        for i,instance in enumerate(self.instances):
            target = instance.label
            if (target == "during" or target == "after") and not d:
                before = i
                d = True
            prediction = instance.classification
            if not target == "during" and not target == "after":
                if prediction == "during" or prediction == "after":
                    responsiveness_vals.append(0)
                else:
                    if int(prediction) > 0:
                        responsiveness_vals.append(0)
                    else:
                        responsiveness_vals.append(1)
                        dif = abs(int(target) - int(prediction))
#                        print target,prediction,dif
                        ae_vals.append(dif)
                        rmse_vals.append(dif*dif)
                        plot_vals[int(target)].append(dif)
        try: 
            responsiveness = round(sum(responsiveness_vals)/len(responsiveness_vals),2)  
        except:
            responsiveness = 0
        try:
            rmse = round(math.sqrt(sum(rmse_vals)/len(rmse_vals)),2)
            mae = round(sum(ae_vals)/len(ae_vals),2)
#            print rmse_vals,rmse,mae
        except:
#            print [(x.label,x.classification) for x in self.instances]
            rmse = 0
            mae = 0
        plot_vals_mean = [(v,(sum(plot_vals[v]) / len(plot_vals[v]))) \
            for v in sorted(plot_vals.keys())]
        try:
            return [rmse,mae,int(self.instances[0].label),before,responsiveness,plot_vals_mean]
        except:
            return [rmse,mae,'x',before,responsiveness,plot_vals_mean]

    def accuracy_at(self,value,condition):
        for instance in self.instances:
            target = instance.label
            prediction = instance.classification
            if target == "during" or target == "after":
                return None
            if condition == "estimation":
                if prediction == value:
                    dif = abs(int(target) - int(prediction))
                    return (int(target),int(prediction),dif)
            if condition == "threshold":
                score = float(instance.score)
                if score > int(value):
                    dif = abs(int(target) - int(prediction))
                    return (int(target),int(prediction),dif)

    def calculate_accuracy(self):
        correct = 0
        for i,instance in enumerate(self.instances):
            if instance.label == "during" or instance.label == "after":
                try:
                    print "calc",round((correct/i),2)
                    return round((correct/i),2)
                except:
                    return 0.0
                break
            elif instance.label == instance.classification:
                correct += 1
        
    def return_rankedfp(self,n,c):
        return sorted([[str(y) for y in [x.id,x.text,x.label,x.classification,x.score]] for x in self.instances if \
            x.classification == c and x.label != c],key = lambda z : z[4],reverse=True)

    def return_ranked_score(self,n):
        return sorted([[str(y) for y in [x.id,x.text,x.label,x.classification,x.score]] for x in self.instances], key = \
            lambda y : y[4],reverse=True)

    class Instance():
        
        def __init__(self,label,classification):
            self.label = label
            self.classification = classification

        def set_label(self,label):
            self.label = label
        
        def set_classification(self,classification):
            self.classification = classification

        def set_score(self,score):
            self.score = score

        def set_text(self,text):
            self.text = text

        def set_tid(self,tid):
            self.id = tid
