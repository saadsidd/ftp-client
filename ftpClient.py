# An FTP Client coded in Python on Windows OS. The tkinter module was used to create the UI and
# ftplib module handles the server navigation/commands. The program has 2 parts:
# a login window, and main client window upon successful login.

from tkinter import *               # importing all UI features necessary for creating client window
from tkinter import messagebox 
import ftplib                       # contains the FTP functions used
from socket import gaierror         # for catching invalid ftp address error
import os                           # for opening files after downloading them


# ============================================================================
# ------ ftp client login screen ---------------------------------------------
# ============================================================================

loginWindow = Tk()

# revert status bar back to "Ready" after error/confirmation messages
def backToReady():
    statusBar.config(text='Ready', fg='black')

def closeLoginWindow():
    loginWindow.destroy()

# check whether login is valid before moving to FTP client window
def loginCheck(event):
    global site_address
    global site_username
    global site_password
    site_address = loginFTP.get()
    site_username = loginUsername.get()
    site_password = loginPassword.get()
    try:                                                                 # checking if login credentials are valid
        ftplib.FTP(site_address)
        ftplib.FTP(site_address).login(site_username, site_password)
        loginWindow.destroy()                                            # if login is successful, destroy login window
    except TimeoutError:                                                 # error handling
        statusBar.config(text='Error:  Connection attempt timed out', fg='red')
        statusBar.after(4000, backToReady)
    except ConnectionRefusedError:
        statusBar.config(text='Error:  Target refused connection attempt', fg='red')
        statusBar.after(4000, backToReady)
    except gaierror:
        statusBar.config(text='Error:  Invalid FTP address', fg='red')
        statusBar.after(4000, backToReady)
    except ftplib.error_perm:
        statusBar.config(text='Error:  Incorrect login', fg='red')
        statusBar.after(4000, backToReady)
    except Exception:
        statusBar.config(text='Error:  Unreachable network', fg='red')
        statusBar.after(4000, backToReady)

# creating the login window and centering on screen based on resolution
loginWindow.title('FTP Server Login')
windowWidth_1 = 300
windowHeight_1 = 150
xCoordWindow = (loginWindow.winfo_screenwidth() / 2) - (windowWidth_1 / 2)
yCoordWindow = (loginWindow.winfo_screenheight() / 2) - (windowHeight_1 / 2)
loginWindow.geometry('%dx%d+%d+%d' % (windowWidth_1, windowHeight_1, xCoordWindow, yCoordWindow))
loginWindow.resizable(0, 0)                             # make window unable to resize
loginWindow.iconbitmap(r'ftp_icon.ico')
loginWindow.protocol('WM_DELETE_WINDOW', closeLoginWindow)

# frames
frame0 = Frame(loginWindow)                             # main frame to hold frames frame1 & frame2
frame0.pack(fill=BOTH, expand=TRUE)
frame1 = Frame(frame0)                                  # left frame to hold labels
frame1.pack(side=LEFT, fill=X, expand=TRUE)
frame2 = Frame(frame0)                                  # right frame to hold entries
frame2.pack(side=RIGHT, fill=X, expand=TRUE)

# labels for ftp://, username, password
Label(frame1, text='ftp://').pack(pady=(10,0), anchor=E)
Label(frame1, text='Username: ').pack(pady=5, anchor=E)
Label(frame1, text='Password: ').pack(anchor=E)

# entry fields for login
loginFTP = Entry(frame2)
loginFTP.pack(pady=(10,0), anchor=W)
loginUsername = Entry(frame2)
loginUsername.pack(pady=5, anchor=W)
loginPassword = Entry(frame2, show='*')
loginPassword.pack(anchor=W)

# submit button
button0 = Button(loginWindow, text='Login', bd=3, width=15)
button0.pack(pady=7)

loginWindow.bind('<Return>', loginCheck)             # press "Return" key to submit entry and call loginCheck
button0.bind('<Button-1>', loginCheck)               # button press to submit entry and call loginCheck

# status bar for displaying login errors
statusBar = Label(loginWindow, text='Ready', bd=1, relief=SUNKEN, anchor=W)
statusBar.pack(side=BOTTOM, fill=X, expand=TRUE, pady=(5,2))

# keep login window running to stay on screen
loginWindow.mainloop()



# ============================================================================
# --------- ftp client window ------------------------------------------------
# ============================================================================

# ask for confirmation before exiting
def closeWindow():
    if messagebox.askokcancel('Exit', 'Exit program?'):
        try:
            ftp.quit()
            root.destroy()
        except Exception:               # simply destroy root to end program incase ftp.quit() is timed out and causes error
            root.destroy()

# displaying commands list in new centered window when "?" help button is pressed
def helpDisplay():
    helpWindow = Tk()
    helpWindow.title('Help')
    helpWindow.resizable(0, 0)
    topLevelFrame = Frame(helpWindow, padx=5, pady=5)
    topLevelFrame.pack(fill=BOTH, expand=TRUE)
    helpFrame = LabelFrame(topLevelFrame, text='Commands', padx=10, pady=(15))
    helpFrame.pack(fill=BOTH, expand=TRUE)
    Label(helpFrame, text='cd [dir]          :   access directory').pack(anchor=W)
    Label(helpFrame, text='cd ..               :   move up 1 directory').pack(anchor=W)
    Label(helpFrame, text='get [file]        :   download file').pack(anchor=W)
    Label(helpFrame, text='put [file]        :   upload file').pack(anchor=W)
    Label(helpFrame, text='rename [fileOld > fileNew]   :   change file name using >').pack(anchor=W)
    Label(helpFrame, text='mkdir [dir]    :   create new directory').pack(anchor=W)
    Label(helpFrame, text='rmdir [dir]     :   remove directory').pack(anchor=W)
    Label(helpFrame, text='delete [file]   :   delete file').pack(anchor=W)
    Label(helpFrame, text='op [file]         :   download then open file').pack(anchor=W)
    Label(helpFrame, text='exit                 :   close program').pack(anchor=W)
    helpWindow.update()
    help_width = helpWindow.winfo_width()
    help_height = helpWindow.winfo_height()
    root_width = root.winfo_width()
    root_height = root.winfo_height()
    helpWindow.geometry('+%d+%d' % (root.winfo_x() + (root_width - help_width) / 2, root.winfo_y() + (root_height - help_height) / 2))
    helpWindow.iconbitmap(r'ftp_icon.ico')

# get command from entry box
def getEntry(event):
    userCommand = entry1.get()
    entry1.delete('0', 'end')           # clear entry field
    if userCommand == '':               # ignore input get if entry field is empty
        pass
    else:
        ftp_command(userCommand)        # pass entry to ftp_command for execution

# takes in command from entry box and executes accordingly
def ftp_command(input):
    inputs = input.split(' ', 1)        # split first word of user input to compare with if/elif statements to decide action

    # ----- Commands -----
    # cd - open directory (cd .. to move up a directory)
    # get - download file
    # put - upload file
    # delete - delete file
    # rename - rename file
    # mkdir - create a new directory
    # rmdir - remove a directory
    # op - open file (if not on local machine, download first then open)
    # exit - close ftp client

    try:                                # exception for catching FTP timeout error
        if inputs[0] == 'cd':           # change directory
            try:
                ftp.cwd(inputs[1])
            except ftplib.error_perm:
                statusBar.config(text='Error: invalid directory', fg='red')
                statusBar.after(2000, backToReady)
            except IndexError:
                statusBar.config(text='Error: enter a valid directory', fg='red')
                statusBar.after(2000, backToReady)
            except Exception:
                statusBar.config(text='Error: unable to change directory', fg='red')
                statusBar.after(2000, backToReady)
            ftp_print()
        
        elif inputs[0] == 'get':        # download file
            try:
                ftp.retrbinary('RETR ' + inputs[1], open(inputs[1], 'wb').write)
                statusBar.config(text='File download successful', fg='green')
                statusBar.after(2000, backToReady)
            except ftplib.error_perm:
                statusBar.config(text='Error: failed to download file', fg='red')
                statusBar.after(2000, backToReady)
            except Exception:
                statusBar.config(text='Error: unable to download file', fg='red')
                statusBar.after(2000, backToReady)
            ftp_print()

        elif inputs[0] == 'put':        # upload file
            try:
                ftp.storbinary('STOR ' + inputs[1], open(inputs[1], 'rb'))
                statusBar.config(text='File "' + inputs[1] + '" upload successful', fg='green')
                statusBar.after(4000, backToReady)
            except FileNotFoundError:
                statusBar.config(text='Error: no such file "' + inputs[1] + '"', fg='red')
                statusBar.after(3000, backToReady)
            except Exception:
                statusBar.config(text='Error: unable to upload file', fg='red')
                statusBar.after(2000, backToReady)
            ftp_print()

        elif inputs[0] == 'delete':     # delete file
            try:
                ftp.delete(inputs[1])
                statusBar.config(text='File "' + inputs[1] + '" deleted', fg='green')
                statusBar.after(6000, backToReady)
            except ftplib.error_perm:
                statusBar.config(text='Error: unable to find file "' + inputs[1] + '"', fg='red')
                statusBar.after(3000, backToReady)
            except Exception:
                statusBar.config(text='Error: unable to delete file', fg='red')
                statusBar.after(2000, backToReady)
            ftp_print()
        
        elif inputs[0] == 'rename':     # rename file
            inputs = inputs[1].split(' > ')
            try:
                ftp.rename(inputs[0], inputs[1])
                statusBar.config(text='File name changed from "' + inputs[0] + '" to "' + inputs[1] + '"', fg='green')
                statusBar.after(4000, backToReady)
            except ftplib.error_perm:
                statusBar.config(text='Error: "' + inputs[0] + '" file not found', fg='red')
                statusBar.after(3000, backToReady)
            except IndexError:
                statusBar.config(text='Error: invalid file name', fg='red')
                statusBar.after(2000, backToReady)
            except Exception:
                statusBar.config(text='Error: name change operation failed', fg='red')
                statusBar.after(2000, backToReady)
            ftp_print()
        
        elif inputs[0] == 'mkdir':      # create a new directory
            try:
                ftp.mkd(inputs[1])
                statusBar.config(text='Directory "' + inputs[1] + '" successfully created', fg='green')
                statusBar.after(4000, backToReady)
            except Exception:
                statusBar.config(text='Error: unable to create directory', fg='red')
                statusBar.after(2000, backToReady)
            ftp_print()

        elif inputs[0] == 'rmdir':      # delete a directory
            try:
                ftp.rmd(inputs[1])
                statusBar.config(text='Directory "' + inputs[1] + '" successfully removed', fg='green')
                statusBar.after(6000, backToReady)
            except ftplib.error_perm:
                statusBar.config(text='Error: directory "' + inputs[1] + '" not found or not empty', fg='red')
                statusBar.after(5000, backToReady)
            except Exception:
                statusBar.config(text='Error: unable to remove directory', fg='red')
                statusBar.after(2000, backToReady)
            ftp_print()
        
        elif inputs[0] == 'op':         # open file. if not present, download file then open
            try:
                if os.path.isfile(inputs[1]):
                    os.startfile(inputs[1])
                    statusBar.config(text='Opening file...', fg='green')
                    statusBar.after(5000, backToReady)
                else:
                    if inputs[1] in ftp.nlst():
                        statusBar.config(text='Downloading and opening file...', fg='green')
                        ftp.retrbinary('RETR ' + inputs[1], open(inputs[1], 'wb').write)
                        statusBar.after(5000, backToReady)
                        os.startfile(inputs[1])
                    else:
                        statusBar.config(text='Error: file "' + inputs[1] + '" not found for download', fg='red')
                        statusBar.after(5000, backToReady)
            except Exception:
                statusBar.config(text='Error: unable to download and open file', fg='red')
                statusBar.after(2000, backToReady)
            ftp_print()
        
        elif inputs[0] == 'exit':      # exit program by calling closeWindow() for confirmation
            closeWindow()
    except Exception:
       messagebox.showerror('Error', 'FTP Error: 421 Timeout\nRestart client')

# prints the current directory contents
def ftp_print():

    # ----- directoryItems content example -----
    # [0]     drwxrwxr-x      d is directory , rwx is permission of owner, group, others (r=read, w=write, x=execute)
    # [1]     2               number of immediate subdirectories + parent directory + itself (so 2 means no subdirectories)
    # [2]     0               UID of user
    # [3]     0               GID of user
    # [4]     32768           size
    # [5]     Dec             month
    # [6]     11              date
    # [7]     2016            year
    # [8]      My             title
    # [9]     Photos           ''
    # [10]     ...             ''
    # [11]     ...             ''

    textbox.config(state='normal')                                          # allow textbox to be editable
    textbox.delete('1.0', END)                                              # clear the text box
    textbox.insert(INSERT, 'Current Directory ' + ftp.pwd() + '\n\n')       # display current accessed directory

    lengthMax = 0
    directoryItems = []
    ftp.retrlines('LIST', directoryItems.append)                            # all ftp data of current directory stored in dictionItems for parsing

    for i in range(len(directoryItems)):
        directoryItems[i] = directoryItems[i].split()                       # split long string into its own items
        directoryItems[i][8] = ' '.join(directoryItems[i][8:])              # combine title into one item
        directoryItems[i][5] = ' '.join(directoryItems[i][5:8])             # combine the month, date, year
        if lengthMax < len(directoryItems[i][8]):                           # get the longest title for column adjustment purposes
            lengthMax = len(directoryItems[i][8])
        if directoryItems[i][0][0] == 'd':                                  # check whether it is directory or a file so we can show 'dir' in the first column when needed
            directoryItems[i][0] = 'dir'
            directoryItems[i][4] = ''
        else:
            directoryItems[i][0] = '   '
        
        # depending on how big the size of folder/file is, divide and attach appropriate unit
        if directoryItems[i][4] != '' and int(directoryItems[i][4]) >= 1073741824:
            directoryItems[i][4] = round(int(directoryItems[i][4]) / 1073741824, 1)
            directoryItems[i][4] = str(directoryItems[i][4]) + ' GB'
        elif directoryItems[i][4] != '' and int(directoryItems[i][4]) >= 1048576:
            directoryItems[i][4] = round(int(directoryItems[i][4]) / 1048576, 1)
            directoryItems[i][4] = str(directoryItems[i][4]) + ' MB'
        elif directoryItems[i][4] != '' and int(directoryItems[i][4]) >= 1024:
            directoryItems[i][4] = round(int(directoryItems[i][4]) / 1024)
            directoryItems[i][4] = str(directoryItems[i][4]) + ' kB'
        elif directoryItems[i][4] != '':
            directoryItems[i][4] = directoryItems[i][4] + ' B'
    
    # displaying headers NAME, SIZE, and DATE MODIFIED
    textbox.insert(INSERT, '      ' + 'NAME'.ljust(lengthMax+11) + 'SIZE' + '          DATE MODIFIED  ' + '\n      ' +'---------'.ljust(lengthMax+6) + '---------     ------------------\n')
    
    # displaying folder/file names, size, and date modified
    for i in range(len(directoryItems)):
        textbox.insert(INSERT, directoryItems[i][0] + '   ' + directoryItems[i][8].ljust(lengthMax) + directoryItems[i][4].rjust(15) + directoryItems[i][5].rjust(23) + '  \n')
    
    textbox.config(state='disabled')                                        # disable textbox editability

# main FTP client window code
try:
    with ftplib.FTP(site_address, timeout=1000) as ftp:                         # use given ftp ip address from login to assign to 'ftp'
        ftp.login(site_username, site_password)                                 # login using credentials from login window

        root = Tk()

        # create and center the ftp client window
        root.title('FTP Client')
        root.iconbitmap(r'ftp_icon.ico')
        windowWidth_2 = 600
        windowHeight_2 = 600
        xCoordWindow = (root.winfo_screenwidth() / 2) - (windowWidth_2 / 2)
        yCoordWindow = (root.winfo_screenheight() / 2) - (windowHeight_2 / 2)
        root.geometry('%dx%d+%d+%d' % (windowWidth_2, windowHeight_2, xCoordWindow, yCoordWindow))
        root.protocol('WM_DELETE_WINDOW', closeWindow)                          # checks with closeWindow function if sure to close

        # status bar for displaying ftp command response
        statusBar = Label(root, text='Ready', bd=1, relief=SUNKEN, anchor=SW, padx=3)
        statusBar.pack(side=BOTTOM, fill=X, anchor=S)
        statusBar.config(font=('default', 10))

        # frame
        frame3 = Frame(root, width=600, height=50)                              # frame to hold submit button
        frame3.pack(side=BOTTOM)
        frame3.propagate(0)
        frame2 = Frame(root, borderwidth=1, width=600, height=50)               # frame to hold 'command' label, entry box and help button
        frame2.pack(side=BOTTOM, anchor=S)
        frame2.propagate(0)
        frame1 = Frame(root, borderwidth=5, width=600)                          # frame to hold text box, scrollbars & server title
        frame1.pack(side=TOP, fill=BOTH, expand=TRUE, anchor=N)

        # labels
        serverTitle = Label(frame1, text='serverTitle', font=('helvetica' , 13))
        serverTitle.pack(side=TOP, fill=X)

        # text box and scrollbars
        scrolly = Scrollbar(frame1)
        scrolly.pack(side=RIGHT, fill=Y)
        scrollx = Scrollbar(frame1, orient=HORIZONTAL)
        scrollx.pack(side=BOTTOM, fill=X)
        textbox = Text(frame1, yscrollcommand=scrolly.set, xscrollcommand=scrollx.set, wrap=NONE)
        textbox.pack(side=LEFT, fill=BOTH, expand=TRUE)
        scrolly.config(command=textbox.yview)
        scrollx.config(command=textbox.xview)

        # buttons
        button1 = Button(frame3, text='Submit', width=25)                       # submit button for ftp commands
        button1.pack(side=TOP)
        helpButtonPhoto = PhotoImage(file='helpbutton_icon.png')                # replace standard button with picture of blue/white "?"
        helpButton = Button(frame2)                                             # help button for displaying commands list
        helpButton.config(image=helpButtonPhoto, width=25, height=25, bd=1, command=helpDisplay)
        helpButton.pack(side=RIGHT, anchor=S, padx=(0, 60))
        Label(frame2, text='Command: ').pack(side=LEFT, pady=(20, 0), padx=(75, 0))

        # entry field
        entry1 = Entry(frame2, width=50)                                        # entry box for ftp commands
        entry1.pack(side=LEFT, pady=(20, 0))

        root.bind('<Return>', getEntry)                                         # press "Return" key to submit entry
        button1.bind('<Button-1>', getEntry)                                    # button press to submit entry

        serverTitle['text'] = ftp.getwelcome()                                  # fill server title label with ftp welcome message
        
        ftp_print()                                                             # display parent directory on first login

        root.mainloop()                                                         # keep root window running to stay on screen
except:
    pass