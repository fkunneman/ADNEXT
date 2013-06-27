
import evalset
import sys

labels = sys.argv[1]
testrnk = sys.argv[2]
labels_2 = sys.argv[3]
testrnk_2 = sys.argv[4]

es = evalset.Evalset()
es.set_instances_lcs(labels,testrnk)
es.set_instances_lcs(labels_2,testrnk_2)
es.print_results()

