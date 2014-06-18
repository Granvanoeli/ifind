from Yieldgen import RandomYieldGenerator, ConstantYieldGenerator, LinearYieldGenerator
from Mine import Mine




ryg = RandomYieldGenerator(depth=10,max=5,min=0)
cyg = ConstantYieldGenerator(depth=10, max=5, min=0)
lyg = LinearYieldGenerator(depth=10, max=5, min=0)

r = ryg.make_yields()
print r

c = cyg.make_yields()
print c

l = lyg.make_yields()
print l



m = Mine(ryg,1)
m2= Mine(cyg,1)
m3= Mine(lyg,1)

m.show_mine()
m2.show_mine()
m3.show_mine()


__author__ = 'gabriele'
# import random
# a =26
# b =34
# c = 6
#
# cue_range = []
#
# r = random.randint(a,b)
#
# print r
#
# gold = 30
# span = 4
# upper_limit = gold+span
# lower_limit = gold-span
# print upper_limit
# print lower_limit
#
# cue = random.randint(lower_limit, upper_limit)
#
# print cue
#
# for x in range(c):
#     cue_range.append(a)
#     print x
#
# array = Yieldgen.constant_yield(10)
#
# print "Yield array"
#
# for c in array:
#     print c
#
# arraycue = Cuegen.make_cue(array, 0.8)
#
# print "arraycue"
#
# for p in arraycue:
#     print p
#
#
# yield_array = Yi
# accuracy = [0.8, 0.6, 0.4, 0.3, 0.2]
#
# for a in accuracy:
#     span = Cuegen.cue_function(a)
#     upper_limit = yield_array[0]+span
#     lower_limit = yield_array[0]-span
#
#     Cuegen.make_cue(yield_array, a)
#
#     print "-----------"
#     print span
#     print "-----------"
#     print upper_limit
#     print lower_limit


#array = [25, 25, 25, 25, 25, 25, 25, 25]
#c = Cuegen.make_cue(array, 0.9)
#print c


#max = 10
#for d in range(max, 0):
#    print d