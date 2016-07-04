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
# End of parameters

start_time = time.strftime('Start time: %Y-%m-%d %H:%M:%S\n')
start_timero = time.strftime('%Y-%m-%d %H:%M:%S')

while True:
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
    
    print 'Max torrent:'+bytes(max(list))
    #[end]Read the list

    free_to_write = []

    #[start]single turn
    timer_interval=0.1
    def delayrun(): 
        print 'Single turn started'
    t=Timer(timer_interval,delayrun) 
    t.start()



    #[start]update status
    fw = open('ptpy-setting\status.txt','w+')
    fw.write(time.strftime('Status report from PT-free-py\n'))
    current_time = time.strftime('Update time: %Y-%m-%d %H:%M:%S\n\n')
    fw.write(start_time)
    fw.write(current_time)
    fw.write('Round: '+bytes(round)+'\n')
    fw.write('Max torrent number: '+bytes(max(list))+'\n')
    fw.write('Free torrent count: '+bytes(len(list))+'\n\n')
    #fw.close()
    #[end]update status

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
                print '[Round '+bytes(round)+' '+time.strftime('%Y-%m-%d %H:%M:%S')+'] '+'PT-Torrent '+bytes(userid)+' (from user setting [free]) has already been downloaded.'
                fw.write('[Free setting] Seed '+bytes(userid)+' [Complete]\n')
                user_pass_flag = 1
                break
        if user_pass_flag == 0:
            no = userid
            print '[Round '+bytes(round)+' '+time.strftime('%Y-%m-%d %H:%M:%S')+'] '+'PT-Torrent '+bytes(userid)+' (from user setting [free]) will be downloaded.'
            fw.write('[Free setting] Seed '+bytes(userid)+' [Downloading]\n')
            
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
                        print '[Round '+bytes(round)+' '+time.strftime('%Y-%m-%d %H:%M:%S')+'] '+'PT-Torrent '+bytes(userdownloadid)+' (from user setting [download]) has already been downloaded.'
                        fw.write('[Force download] Seed '+bytes(userdownloadid)+' [Complete]\n')
                        user_download_pass_flag = 1
                        break
                 
                if user_download_pass_flag == 0:
                    no = userdownloadid
                    print '[Round '+bytes(round)+' '+time.strftime('%Y-%m-%d %H:%M:%S')+'] '+'PT-Torrent '+bytes(userdownloadid)+' (from user setting [download]) will be downloaded.'
                    fw.write('[Force download] Seed '+bytes(userdownloadid)+' [Downloading]\n')
                    breakflag = 1
            else:
                fw.write('[Force download] Seed '+bytes(userdownloadid)+' [Pending]\n')
            
    fw.close()
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
        pattern = re.compile('font class=\'free\'')
        items = re.findall(pattern,content)
        if (user_download_pass_flag != 0):
            if (items):
                print '[Round '+bytes(round)+' '+time.strftime('%Y-%m-%d %H:%M:%S')+'] '+'PT-Torrent '+showno+ ' ('+bytes(searchhead-no)+'/'+bytes(searchfront+searchend)+')'+' is free.'
            else:
                print '[Round '+bytes(round)+' '+time.strftime('%Y-%m-%d %H:%M:%S')+'] '+'PT-Torrent '+showno+ ' ('+bytes(searchhead-no)+'/'+bytes(searchfront+searchend)+')'+' is not free.'
                no = no - 1
                continue
        #[end]Search for free pattern
    
        #[start]Search in the list
        flag = 0
        for element in list:
            if element == no:
                print '[Round '+bytes(round)+' '+time.strftime('%Y-%m-%d %H:%M:%S')+'] '+'PT-Torrent '+showno+' ('+bytes(searchhead-no)+'/'+bytes(searchfront+searchend)+')'+' has already been downloaded.'
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
        print 'Download complete. (Torrent '+showno+')'
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

