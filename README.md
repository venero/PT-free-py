# PT-free-py
PT-free-py is a python program for scaning and downloading free torrents at PuTao (https://pt.sjtu.edu.cn/).

It can also be used for remote download.

## Configuring PT-free-py
### **utorrent**
Set *load .torrent automatically from* (red box) to the **/torrent** directory.

![utorrent setting](https://raw.githubusercontent.com/venero/PT-free-py/master/mdpic/1.PNG)
### User name and password
Create a new file **PT-id-pwd.txt**, write your user ID at the first line, and write your password at the second line, like:
```c
username

password
```

### Runing
There is no background running scheme for this program currently, thus the only way to run it is to use `python` and check the Console for its output.

The status information is also avliable at **/ptpy-setting/status.txt**.

![running](https://raw.githubusercontent.com/venero/PT-free-py/master/mdpic/2.PNG)
## Layout
### Free scan
Use this program to download free torrents to a directory **/DIR**, set utorrent to automatically scan **/DIR** and load torrents from it.
### Remote download
Use any net-disk to synchronize the **/ptpy-setting** directory, and update **UserSetDownload.txt** with target PT-Torrent ID.

## Notes
### Free scan
- Torrent list is kept in **torrentlist.txt**, you probably wonder why I didn't scan the **/torrent** directory.
Well, (1) **utorrent** might delete the torrent file in some settings (as the above figure shows: *[checkbox] delete loaded torrent*).
(2) **utorrent** changes the name of the torrent file once it has been downloaded.
(3) The torrents can be deleted afterwards, which saves space.
~~(4) The above are just nonsense, I just too lazy to write the code to scan the **/torrent** directory.~~

- Frequency can not be higher than 2.5s per inquiry, otherwise the inquiry will be denied by PuTao.
There is **no recovery** in this program, you can view your status at **/ptpy-setting/status.txt** and judge whether the program has stoped.

- `innersleep` and `outersleep` halts the program with a random amount of time.
I'm trying to make it looks like someone was refreshing the pages once in a while.

### Remote download
- `userdownscan = 600` means that the program will scan **UserSetDownload.txt** every `600` seconds.
Lower scan cool down can be implemented, but quite unneccessarily, since most of the time this file is unchanged.

### Hashcheck
- `Hashcheck.py` is a by-product of PT-free-py, it checks whether two files are the same.
During my debugging, the torrents downloaded by this program somehow mismatches the torrent downloaded by chrome.
I use this to check the hash of two torrents.
