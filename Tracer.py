# coding=gbk
import urllib
import urllib2
import cookielib
import requests
# bencode (B-encode), used for future torrent analysis
import bencode
import random
import re
from threading import Timer 
import time
# disk
from ctypes import *
import win32file
# fix encoding
import sys
reload(sys)
sys.setdefaultencoding( "utf-8" )

content = 0
def torrentTitle(titleid):
    #opener7 = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie))
    #titleno = bytes(titleid)
    #print titleno
    #titleUrl = 'https://pt.sjtu.edu.cn/details.php?id='+titleno
    #result3 = opener7.open(titleUrl)
    #content = result3.read()
    #print content
    patternfree = re.compile('<script language="JavaScript" src="ajaxbasic.js" type="text/javascript"></script><h1 align=\'center\'>(.+?)(?:</h1>|&nbsp;)')
    title = re.findall(patternfree,content)
    #print title[0]
    #for element in title:
    #    print unicode(element,'utf-8')
    #    break
    if len(title) == 0 :
        return '[Invalid torrent title]'
    return unicode(title[0],'utf-8')

def torrentSize(titleid):
    #opener8 = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie))
    #titleno = bytes(titleid)
    #print titleno
    #titleUrl = 'https://pt.sjtu.edu.cn/details.php?id='+titleno
    #result8 = opener8.open(titleUrl)
    #content = result8.read()
    #print content
    patternfree = re.compile('<td class="rowfollow" valign="top" align=\'left\'><b>.+?</b>(.+?)&nbsp;')
    title = re.findall(patternfree,content)
    #print title[0]
    #for element in title:
    #    print unicode(element,'utf-8')
    #    break
    if len(title) == 0 :
        return '[Invalid torrent size]'
    return unicode(title[0],'utf-8')


# UserSetFree.txt
#   The head of free torrent. In case of a break from too many un-free torrents.
# UserSetDownload.txt
#   Force download from user. Remote download of torrent, regardless of its free status.
# round
#   A round is one traversal from PT, covering hundreds of torrents.
round = 0
# innersleep
#   The sleep time between two torrent inquiries. It MUST be bigger than 2.5.
#   To avoid pattern detection, we use:
#   innersleep = random.uniform(innersleep0, innersleep1);
innersleep0 = 6
innersleep1 = 10
# outersleep
#   The sleep time between two rounds.
#   To avoid pattern detection, we use:
#   outersleep = random.uniform(outersleep0, outersleep1);
outersleep0 = 100
outersleep1 = 150
# searchfront & searchend
#   The search of torrent will cover:[s-searchend,s+searchfront].
searchfront = 200
searchend = 150
# userdownscan
#   The largest mean time between two user download check
userdownscan = 600
# disk
#   The disk used for download
disk = 'f:'
#   The threshold for status warning
diskThreshold = 0.1
#   The reserve space on the disk (GB)
diskReserve = 1
# End of parameters

start_time = time.strftime('[Status] Start time: %Y-%m-%d %H:%M:%S\n')
start_timero = time.strftime('%Y-%m-%d %H:%M:%S')
loglist = []
diskExhausted = 0
while 1:
    print '\nRound: '+bytes(round)+ ' start.'
    print 'Current time:'+time.strftime('%Y-%m-%d %H:%M:%S')+' (Program started from:'+ start_timero+')\n'
    list = []
    downloadlist = []
    
    #print 'sss'
    #[start]Read the list
    file = open('torrentlist.txt','r')
    #print 'sss'
 
    while 1:
        line = file.readline()
        if not line:
            break
        list.append(int(line))
    
    #print 'sss'
    file.close

    #[start]user set
    ufile = open('ptpy-setting\UserSetFree.txt','r')
    
    user_pass_flag = 0
    userid = 0
    while 1:
        line = ufile.readline()
        if not line:
            break
        userid=int(line)
    
    ufile.close()
    #[end]user set

    #[start]user download
    udfile = open('ptpy-setting\UserSetDownload.txt','r')
    
    user_download_pass_flag = 0
    userdownloadid = 0
    while 1:
        line = udfile.readline()
        if not line:
            break
        downloadlist.append(int(line))
    #print len(downloadlist)
    udfile.close()
    #[end]user download
    
    print '[Round '+bytes(round)+' '+time.strftime('%Y-%m-%d %H:%M:%S')+'] Max torrent:'+bytes(max(list))
    #[end]Read the list

    free_to_write = []

    #[start]single turn
    timer_interval=0.1
    def delayrun(): 
        print '[Round '+bytes(round)+' '+time.strftime('%Y-%m-%d %H:%M:%S')+'] Single round started ( PT-Torrent from ' + bytes(max(list)+searchfront) + ' to ' + bytes(max(list)-searchend) + ' )'
    t=Timer(timer_interval,delayrun) 
    t.start()

    #[start]update status
    fw = open('ptpy-setting\status.txt','w+')
    fw.write(time.strftime('# Status report from PT-free-py\n'))
    current_time = time.strftime('[Status] Update time: %Y-%m-%d %H:%M:%S\n\n')
    fw.write(start_time)
    fw.write(current_time)
    fw.write('[Status] Round: '+bytes(round)+'\n')
    fw.write('[Status] Max torrent number: '+bytes(max(list))+'\n')
    fw.write('[Status] Torrent number range: '+bytes(max(list)-searchend)+' - '+bytes(max(list)+searchfront)+'\n')
    fw.write('[Status] Free torrent count: '+bytes(len(list))+'\n\n')

    sectorsPerCluster, bytesPerSector, numFreeClusters, totalNumClusters = win32file.GetDiskFreeSpace(disk)
    # get free space
    freespace = (numFreeClusters * sectorsPerCluster * bytesPerSector) /(1024.0 * 1024.0 * 1024.0)
    # get total space
    totalspace = (totalNumClusters * sectorsPerCluster * bytesPerSector) /(1024.0 * 1024.0 * 1024.0)
    # I don't use the function 'round' here because there is a variable 'round' in main.
    if freespace/totalspace < diskThreshold:
        fw.write('[Warning] Free space in '+disk.upper()+' is low ('+ '%.2f' % (freespace/totalspace*100)+'%).\n')
    fw.write('[Disk] In disk '+disk.upper()+' Free space: '+'%.2f' % freespace+'GB. Total space: '+'%.2f' % totalspace+'GB.\n')
    if freespace < diskReserve:
        fw.write('[Error] Free space in '+disk.upper()+' is below critical value ('+'%.2f' % diskReserve+'GB), Tracer has stopped.\n')
        diskExhausted = 1
    #[end]update status
    fw.write('\n')
    #[start]PT-ID and PT-pwd
    idpwdfile = open('PT-id-pwd.txt','r')
    ptuserf = idpwdfile.readline()
    if not ptuserf:
        print '[Error] Invalid PT-user-ID'
        break
    l = len(ptuserf)

    ptuser = ptuserf[0:l-1]
    ptpwd = idpwdfile.readline()
    if not ptpwd:
        print '[Error] Invalid PT-user-Password'
        break
    idpwdfile.close()
    #print 'c' + ptuser + 'a' + ptpwd + 'b'
    #[end]PT-ID and PT-pwd
    
    filename = 'cookie.txt'

    cookie = cookielib.MozillaCookieJar(filename)
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie))
    #params = {'username': ptuser, "password": ptpwd, "checkcode" : "XxXx"}
    #strcode = '\'username\':\''+ ptuser + '\',\'password\':\'' + ptpwd + '\',\'checkcode\':\'XxXx\''
    postdata = urllib.urlencode({
    			'username':ptuser,
    			'password':ptpwd,
                        'checkcode':'XxXx'
    		})
    #postdata = urllib.urlencode(params)
    loginUrl = 'https://pt.sjtu.edu.cn/takelogin.php'

    result = opener.open(loginUrl,postdata)

    cookie.save(ignore_discard=True, ignore_expires=True)

    #[start]single run

    # The ID in the single run
    no=max(list)+searchfront
    searchhead=max(list)+searchfront

    if userid == 0:
        print 'Invalid user setting.'
        user_pass_flag = 1
    else:        
        for element in list:
            if element == userid:
                print '[Round '+bytes(round)+' '+time.strftime('%Y-%m-%d %H:%M:%S')+'] '+'PT-Torrent '+bytes(userid)+' (from user setting [Free]) has already been downloaded.'
                fw.write('[Free setting] PT-Torrent '+bytes(userid)+' [Complete]\n')
                
                user_pass_flag = 1
                break
        if user_pass_flag == 0:
            no = userid
            print '[Round '+bytes(round)+' '+time.strftime('%Y-%m-%d %H:%M:%S')+'] '+'PT-Torrent '+bytes(userid)+' (from user setting [Free]) will be downloaded.'
            fw.write('[Free setting] PT-Torrent '+bytes(userid)+' [Downloading]\n')
            #loglist.append('[Log] [Round '+bytes(round)+' '+time.strftime('%Y-%m-%d %H:%M:%S')+'] : [Free setting] PT-Torrent '+bytes(userid)+' [Downloading]\n')
            
    fw.write('\n')

    breakflag = 0
    if len(downloadlist) == 0:
        print 'Invalid user download setting.'
        user_download_pass_flag = 1
    else:
        for userdownloadid in downloadlist:
            if breakflag == 0:
                user_download_pass_flag = 0
         
                for element in list:
                    if element == userdownloadid:
                        print '[Round '+bytes(round)+' '+time.strftime('%Y-%m-%d %H:%M:%S')+'] '+'PT-Torrent '+bytes(userdownloadid)+' (from user setting [Download]) has already been downloaded.'
                        fw.write('[Force download] PT-Torrent '+bytes(userdownloadid)+' [Complete]\n')
                        #loglist.append('[Log] Seed '+bytes(userdownloadid)+' [Complete]\n')
                        #print torrentSize(userdownloadid)
                        #loglist.append('[Log] [Round '+bytes(round)+' '+time.strftime('%Y-%m-%d %H:%M:%S')+'] [TEST]: [Force download] PT-Torrent '+bytes(userdownloadid)+' [Complete]\n')
                        user_download_pass_flag = 1
                        break
                 
                if user_download_pass_flag == 0:
                    no = userdownloadid
                    print '[Round '+bytes(round)+' '+time.strftime('%Y-%m-%d %H:%M:%S')+'] '+'PT-Torrent '+bytes(userdownloadid)+' (from user setting [Download]) will be downloaded.'
                    fw.write('[Force download] PT-Torrent '+bytes(userdownloadid)+' [Downloading]\n')
                    #loglist.append('[Log] [Round '+bytes(round)+' '+time.strftime('%Y-%m-%d %H:%M:%S')+'] : [Force download] PT-Torrent '+bytes(userdownloadid)+' [Downloading]\n')
                    breakflag = 1
            else:
                fw.write('[Force download] PT-Torrent '+bytes(userdownloadid)+' [Pending]\n')
    
    #[start]Write logs
    fw.write('\n')
    for element in loglist:
        fw.write(element)
    #[end]Write logs
    fw.close()
    if diskExhausted == 1:
        print '[Error] Disk exhausted'
        break
    # user_pass_flag == 0
    #   user setting is correct and will be downloaded
    # user_download_pass_flag == 0
    #   user download setting is correct and will be downloaded
    restartflag = 0
    timesleep = 0
    while (no>max(list)-searchend or user_pass_flag == 0 or user_download_pass_flag == 0):
        innersleep = random.uniform(innersleep0, innersleep1)
        # check user update
        timesleep = timesleep + innersleep
        restartflag = 0
        if timesleep > userdownscan:
            timesleep = 0
            #[start]user download
            udilist = []
            udifile = open('ptpy-setting\UserSetDownload.txt','r')
            while 1:
                line = udifile.readline()
                if not line:
                    break
                udilist.append(int(line))
            #print len(downloadlist)
            udifile.close()
            #[end]user download
            for udiid in udilist:
                udiflag = 0
                for element in list:
                    if element == udiid:
                        udiflag = 1
                        break              
                if udiflag == 0:
                    no = udiid
                    print '[Round '+bytes(round)+' '+time.strftime('%Y-%m-%d %H:%M:%S')+'] '+'Routine check for user download: [Restart]'
                    restartflag = 1
            if restartflag == 0:
                print '[Round '+bytes(round)+' '+time.strftime('%Y-%m-%d %H:%M:%S')+'] '+'Routine check for user download: [Passed]'
        if restartflag == 1:
            break
    
        time.sleep(innersleep) 
        #print 'sleep:'+bytes(innersleep)+'\n';
        
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie))
    
        showno = bytes(no)

        gradeUrl = 'https://pt.sjtu.edu.cn/details.php?id='+showno

        #print 'aaa'

        result3 = opener.open(gradeUrl)

        #[start]Search for free pattern
        content = result3.read()
        #print content
        patternfree = re.compile('font class=\'free\'')
        itemsfree = re.findall(patternfree,content)
        pattern30 = re.compile('font class=\'d30down\'')
        items30 = re.findall(pattern30,content)
        
        pattern50 = re.compile('font class=\'halfdown\'')
        items50 = re.findall(pattern50,content)
        
        pattern70 = re.compile('font class=\'d70down\'')
        items70 = re.findall(pattern70,content)
        pattern2up = re.compile('font class=\'twoup\'')
        items2up = re.findall(pattern2up,content)
        
        patternnone = re.compile('class="rowhead"')
        itemsnone = re.findall(patternnone,content)
        
        if (user_download_pass_flag != 0):
            if (itemsfree):
                print '[Round '+bytes(round)+' '+time.strftime('%Y-%m-%d %H:%M:%S')+'] '+'PT-Torrent '+showno+ ' ('+bytes(searchhead-no+1)+'/'+bytes(searchfront+searchend)+')'+' is [Free].'
            elif (items30):
                print '[Round '+bytes(round)+' '+time.strftime('%Y-%m-%d %H:%M:%S')+'] '+'PT-Torrent '+showno+ ' ('+bytes(searchhead-no+1)+'/'+bytes(searchfront+searchend)+')'+' is [Download for 30%].'
                no = no - 1
                continue
            elif (items50):
                print '[Round '+bytes(round)+' '+time.strftime('%Y-%m-%d %H:%M:%S')+'] '+'PT-Torrent '+showno+ ' ('+bytes(searchhead-no+1)+'/'+bytes(searchfront+searchend)+')'+' is [Download for 50%].'
                no = no - 1
                continue
            elif (items70):
                print '[Round '+bytes(round)+' '+time.strftime('%Y-%m-%d %H:%M:%S')+'] '+'PT-Torrent '+showno+ ' ('+bytes(searchhead-no+1)+'/'+bytes(searchfront+searchend)+')'+' is [Download for 70%].'
                no = no - 1
                continue
            elif (items2up):
                print '[Round '+bytes(round)+' '+time.strftime('%Y-%m-%d %H:%M:%S')+'] '+'PT-Torrent '+showno+ ' ('+bytes(searchhead-no+1)+'/'+bytes(searchfront+searchend)+')'+' is [Upload for 2X].'
                no = no - 1
                continue
            elif not (itemsnone):
                print '[Round '+bytes(round)+' '+time.strftime('%Y-%m-%d %H:%M:%S')+'] '+'PT-Torrent '+showno+ ' ('+bytes(searchhead-no+1)+'/'+bytes(searchfront+searchend)+')'+' is [Invalid].'
                no = no - 1
                continue
            else:
                print '[Round '+bytes(round)+' '+time.strftime('%Y-%m-%d %H:%M:%S')+'] '+'PT-Torrent '+showno+ ' ('+bytes(searchhead-no+1)+'/'+bytes(searchfront+searchend)+')'+' is [Regular].'
                no = no - 1
                continue
        #[end]Search for free pattern
    
        #[start]Search in the list
        flag = 0
        for element in list:
            if element == no:
                print '[Round '+bytes(round)+' '+time.strftime('%Y-%m-%d %H:%M:%S')+'] '+'PT-Torrent '+showno+' ('+bytes(searchhead-no+1)+'/'+bytes(searchfront+searchend)+')'+' has already been downloaded.'
                no = no - 1
                flag = 1
                break
        if flag == 1:
            continue      
        #[end]Search in the list   
    
        DownloadUrl = 'https://pt.sjtu.edu.cn/download.php?id='+showno

        result2 = opener.open(DownloadUrl)

        fw2 = open('.\\torrent\\'+showno+'.torrent','wb+')

        #fy = open('y.torrent','r')
        #print result2

        while True:
            stream = result2.readline()
            #s2 = fy.readline()
            if stream:
                fw2.write(stream)
            else:
                break
    
        fw2.close()

        flist = open('torrentlist.txt','a')
        flist.write(showno+'\n')
        flist.close()
        print '[Round '+bytes(round)+' '+time.strftime('%Y-%m-%d %H:%M:%S')+'] '+'PT-Torrent '+showno+' is listed for download.'
        #print '[Round '+bytes(round)+' '+time.strftime('%Y-%m-%d %H:%M:%S')+'] '+'PT-Torrent '+showno+' ('+bytes(searchhead-no+1)+'/'+bytes(searchfront+searchend)+')'+' is listed for download.'
        print '--Name:'+torrentTitle(no)
        print '--Size:'+torrentSize(no)
        if user_pass_flag == 0:
            loglist.append('[Log] [Round '+bytes(round)+' '+time.strftime('%Y-%m-%d %H:%M:%S')+'] : PT-Torrent '+showno+' (from user setting [Free]) is listed for download.\n')
        if user_download_pass_flag == 0:
            loglist.append('[Log] [Round '+bytes(round)+' '+time.strftime('%Y-%m-%d %H:%M:%S')+'] : PT-Torrent '+showno+' (from user setting [Download]) is listed for download.\n')
        if user_pass_flag == 1 and user_download_pass_flag == 1:
            loglist.append('[Log] [Round '+bytes(round)+' '+time.strftime('%Y-%m-%d %H:%M:%S')+'] : PT-Torrent '+showno+' (free torrent) is listed for download.\n')
        loglist.append('[Log] --Name:'+torrentTitle(no)+'\n')
        loglist.append('[Log] --Size:'+torrentSize(no)+'\n')
        no = no - 1
        if user_pass_flag == 0 or user_download_pass_flag == 0:
            break
    #[end]single run
        
    print '\nRound: '+bytes(round)+ ' end.'
    round = round + 1
    outersleep = random.uniform(outersleep0, outersleep1)
    if restartflag == 0:
        time.sleep(outersleep)
    #print result.read()

