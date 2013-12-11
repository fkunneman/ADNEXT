#! /usr/bin/env python

from __future__ import division
from collections import defaultdict
import math

def generate_frequencies(instances,feature_string):
    label_frequency = defaultdict(int)
    feature_frequency = defaultdict(int)
    feature_label_frequency = defaultdict(lambda : defaultdict(int))
    #obtain feature and label frequencies
    for instance in instances:     
        label = instance["label"]
        label_frequency[label] += 1
        for feature in instance[feature_string]:
            feature_frequency[feature] += 1
            feature_label_frequency[feature][label] += 1
    return label_frequency,feature_frequency,feature_label_frequency

def infogain(label_frequency,feature_frequency,feature_label_frequency):
    feature_infogain = {}
    num_instances = sum([x for x in label_frequency.values()])
    problabels = [(label_frequency[x] / num_instances) for x in label_frequency.keys()] 
    entropy_before = -sum([p * math.log(p,2) for p in problabels]) #entropy before splitting
    for feature in feature_frequency.keys(): #compute for each feature
        frequency = feature_frequency[feature]
        inverse_frequency = num_instances - frequency
        p1 = frequency / num_instances
        p0 = inverse_frequency / num_instances
        probs1 = [(feature_label_frequency[label][feature] / frequency) for label in label_frequency.keys()]
        probs0 = [((label_frequency[label] - feature_label_frequency[label][feature]) / inverse_frequency) for label in label_frequency.keys()]
        entropy1 = (-sum([p * math.log(p,2) for p in probs1 if p != 0])) * p1
        entropy0 = (-sum([p * math.log(p,2) for p in probs0 if p != 0])) * p0
        entropy_after = entropy1 + entropy0 #class entropy of instances with the feature
        infogain = entropy_before - entropy_after 
        feature_infogain[feature] = infogain
    return feature_infogain

def ltqnorm(p):
    """
    Modified from the author's original perl code (original comments follow below)
    by dfield@yahoo-inc.com.  May 3, 2004.

    Lower tail quantile for standard normal distribution function.

    This function returns an approximation of the inverse cumulative
    standard normal distribution function.  I.e., given P, it returns
    an approximation to the X satisfying P = Pr{Z <= X} where Z is a
    random variable from the standard normal distribution.

    The algorithm uses a minimax approximation by rational functions
    and the result has a relative error whose absolute value is less
    than 1.15e-9.

    Author:      Peter John Acklam
    Time-stamp:  2000-07-19 18:26:14
    E-mail:      pjacklam@online.no
    WWW URL:     http://home.online.no/~pjacklam
    """

    if p < 0.0005:
        p = 0.0005
    elif p > 0.9995:
        p = 0.9995

    # Coefficients in rational approximations.
    a = (-3.969683028665376e+01,  2.209460984245205e+02, \
         -2.759285104469687e+02,  1.383577518672690e+02, \
         -3.066479806614716e+01,  2.506628277459239e+00)
    b = (-5.447609879822406e+01,  1.615858368580409e+02, \
         -1.556989798598866e+02,  6.680131188771972e+01, \
         -1.328068155288572e+01 )
    c = (-7.784894002430293e-03, -3.223964580411365e-01, \
         -2.400758277161838e+00, -2.549732539343734e+00, \
          4.374664141464968e+00,  2.938163982698783e+00)
    d = ( 7.784695709041462e-03,  3.224671290700398e-01, \
          2.445134137142996e+00,  3.754408661907416e+00)

    # Define break-points.
    plow  = 0.02425
    phigh = 1 - plow

    # Rational approximation for lower region:
    if p < plow:
       q  = math.sqrt(-2*math.log(p))
       return (((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5]) / \
               ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1)

    # Rational approximation for upper region:
    if phigh < p:
       q  = math.sqrt(-2*math.log(1-p))
       return -(((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5]) / \
                ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1)

    # Rational approximation for central region:
    q = p - 0.5
    r = q*q
    return (((((a[0]*r+a[1])*r+a[2])*r+a[3])*r+a[4])*r+a[5])*q / \
           (((((b[0]*r+b[1])*r+b[2])*r+b[3])*r+b[4])*r+1)

def bns(pair,label_frequency,feature_label_frequency):
    feature_bns = {}
    #print label_frequency,feature_label_frequency
    for feature in feature_label_frequency.keys():
        tp = feature_label_frequency[feature][pair[0]]
        pos = label_frequency[pair[0]]
        fp = feature_label_frequency[feature][pair[1]]
        neg = label_frequency[pair[1]]
        tpr = tp/pos
        fpr = fp/neg
        bns = round((abs(ltqnorm(tpr) - ltqnorm(fpr))),2)
#        print feature,pair,tp,pos,fp,neg,tpr,fpr,bns
        feature_bns[feature] = bns
    return feature_bns

def return_idf(train_vectors):
    num_docs = len(train_vectors)
    df = defaultdict(int)
    idf = {}
    for instance in train_vectors:
        features = instance["sparse"]
        for feature in features.keys():
            df[feature] += 1

    for feature in df.keys():
        idf[feature] = math.log((num_docs/df[feature]),10)

    return idf
