# _*_ coding: utf-8 _*_

import os
list=0

# 1;
list += 1
print "zhuang >>> %d" %(list)
print "hello world"
# 2:
list += 1
print "zhuang >>> %d" %(list)
print os.listdir("./../")
# 3:
list += 1
print "zhuang >>> %d" %(list)
for root, dirs, files in os.walk('./../'):
    print root,dirs,files
# 4:
list += 1
print "zhuang >>> %d" %(list)
for root, dirs, files in os.walk('./../'):
    # open('myfile.txt', 'a').write(root+dirs+files)
    open('out/myfile_test.txt', 'a').write("%s %s %s\n" % (root,dirs,files))
