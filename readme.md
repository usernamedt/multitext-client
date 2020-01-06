Daniil Zakhlystov

**Multi-user text editor - client app.**

Connects to the server by ip address and port specified in launch parameters.
Requires python 3.7 or higher. Cross-platform.

On the launch, you will be asked to log in with existing account or create a
 new one.
 After login, you can open existing file (yours or shared with you by other
  users) or you can create a new file and edit it from as many devices
  simultaneously (like in Google Docs). 
  
To open menu, press Control-C.

To use cut/copy/paste/delete options open menu and go to Edit section.
Also, you can past the text straight from the terminal app (experimental
 feature)  

If you want to share the file with
   another user, choose File > Share in menu and then specify a username of
    the user you want to share your file with.  
    
To save file, choose File > Save in menu

**Usage:**

launch.py [-h] [-i IP] [-p PORT]

optional arguments:

  -h, --help            show help message
  
  -i IP, --ip IP        destination server ip
  
  -p PORT, --port PORT  destination server port

**Launch sample:**

python launch.py -i 127.0.0.1 -p 8080
