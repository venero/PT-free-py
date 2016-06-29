import hashlib

file1 = 'xx.torrent'
file2 = 'y.torrent'

hasher = hashlib.md5()
with open(file1, 'rb') as afile:
    buf = afile.read()
    hasher.update(buf)
print '[Hash]'+file1+': '+(hasher.hexdigest())

hasher2 = hashlib.md5()
with open(file2, 'rb') as bfile:
    buf = bfile.read()
    hasher2.update(buf)
print '[Hash]'+file2+': '+(hasher2.hexdigest())

if hasher.hexdigest() == hasher2.hexdigest():
    result = '[result] '+ file1 + ' and '+ file2 + ' are the same.'
else:
    result = '[result] '+ file1 + ' and '+ file2 + ' are different.'

print result

fw = open(file1,'rb')

fy = open(file2,'rb')

# count is the number of inconsistent pairs
count = 0

# Below 'while' shows how to stop the iteration when '3' pairs of inconsistency happens
#while count < 3:
while True:
    #print 'in'
    stream = fw.readline()
    s2 = fy.readline()
    if (not stream) and (not s2):
        break
    print ' '
    print '------------------'    
    print ' '
    if True:
        if s2 != stream:
            print '[Inconsistent]'            
            print ' ['+file1+']'
            print '  [Length]:'+bytes(len(stream))+' [Content]:'
            print stream      
            print '------'           
            print ' ['+file2+']'
            print '  [Length]:'+bytes(len(s2))+' [Content]:'
            print s2        
            count = count + 1
        if s2 == stream:
            print '[Consistent]'            
            print ' ['+file1+']'
            print '  [Length]:'+bytes(len(stream))+' [Content]:'
            print stream      
            print '------'      
            print ' ['+file2+']'
            print '  [Length]:'+bytes(len(s2))+' [Content]:'
            print s2             
            count = 0
        #print fw.name
        #print fw.mode
        #print fw.encoding
        #print fw.closed
    else:
        print stream            
        print 'xxxx'
        print s2                 
        print 'yyyy'
        count = count + 1
    
fw.close()
fy.close()

print ' '
print '******'
print ' '
print result
