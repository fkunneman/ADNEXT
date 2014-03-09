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

    def add_instances(self,instances,score=False):
        for instance_tokens in instances:
            instance = Evalset.Instance(instance_tokens[0],instance_tokens[1])
            if score:
                instance.set_score(instance_tokens[3])
            self.instances.append(instance)

    def calculate_general(self):
        ce = evaluation.ClassEvaluation()
        for instance in self.instances:
            ce.append(instance.label,instance.classification) 
        results = [["Class","Precision","Recall","F1","TPR","FPR","AUC","Samples",
            "Classifications","Correct"]]
        for label in sorted(list(set(ce.goals))):
            label_results = [ce.precision(cls=label),ce.recall(cls=label),ce.fscore(cls=label),
                ce.tp_rate(cls=label),ce.fp_rate(cls=label),
                auc([0,ce.fp_rate(cls=label),1],[0,ce.tp_rate(cls=label),1]),
                (ce.tp[label] + ce.fn[label]),(ce.tp[label] + ce.fp[label]),ce.tp[label]]
            results.append([label] + [round(x,2) for x in label_results])
        micro_results = [ce.precision(),ce.recall(),ce.fscore(),ce.tp_rate(),ce.fp_rate(),
            auc([0,ce.fp_rate(),1],[0,ce.tp_rate(),1]),len(ce.observations),len(ce.observations)]
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
                        ae_vals.append(dif)
                        rmse_vals.append(dif*dif)
                        plot_vals[int(target)].append(dif)
        responsiveness = round(sum(responsiveness_vals)/len(responsiveness_vals),2)  
        try:
            rmse = round(math.sqrt(sum(rmse_vals)/len(rmse_vals)),2)
            mae = round(sum(ae_vals)/len(ae_vals),2)
        except:
            print [(x.label,x.classification) for x in self.instances]
            rmse = 0
            mae = 0
        plot_vals_mean = [(v,(sum(plot_vals[v]) / len(plot_vals[v]))) \
            for v in sorted(plot_vals.keys())]
        return [rmse,mae,int(self.instances[0].label),before,responsiveness,plot_vals_mean]

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
                    return round((correct/(i-1)),2)
                except:
                    return 0.0
                break
            if instance.label == instance.classification:
                correct += 1
        

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
