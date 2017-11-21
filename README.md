# bpg2
A proof-of-concept work to combine blockchain technology to store openGPG signed documents.

The software shown here was used during a talk I gave at the T-DOSE open source conference in 2017.
A recording can be found on YouTube: https://youtu.be/BXIpFC5LJE0

I think in the near future this is the way to sign, store and archive important documents.

It simulates the workflow of the way I envision this to work in the future
* First somebody uploades a document into the system (or use a web service for that eventualy).
* Then the document signing gets assigned to one or more persons.
* Then, when these persons log in, they get a list of documents to sign.
* The sign the documents and the result is added/archived to the blockchain.

## Some sort of political statement on the why
I strongly believe that this kind of software should not come exclusively from some closed source vendor.
This kind of public infrastructure is way to important for society to rely on commercial companies.
If those companies provide commercial services for an open source solution, or a closed source one that is based on open standards
(preferably with more than a single implementation) that would be fine. 

# Installation

Steps to install on Linux:
* Download multichain from https://www.multichain.com/download-install/
* Install GPG on your system
* install sqlite3 on your system.
* Install multichain somewhere on your system. I used the root directory of this git repo for that.
* Create a virtual Python environment. Example: "virtualenv venv"
* Install all needed Python libraries: Example: "pip install -r requirements.txt"
* There is, at the time of wriing, a bug in the Savoir library. So open venv/lib/python2.7/site-packages/Savoir/__init__.py and change the line
to read "from Savoir import *".
* That's it. Go start the app: "./go.sh". It will 

The steps to initialize the blockchain software are done when you start multichain for the first time *from the application!*

# Starting and working with the application
* Execute the go.sh script, it should come back saying it started a flask application on localhost with port 5000.
* Point your browser to http://127.0.0.1:5000
* First click on "admin" and click on "start multichain". After a few seconds and a refresh of the page it should tell you it is running.
* Now you can click on "getinfo" to see some info about the system.
* Select "upload" to upload a file you would like to sign. Any file will do (no guarantees when you are uploading BIG files). 
* Select "assign" to select an uploaded file, and after submitting selecting the users that should put a signature on this file.
The system comes default with 2 digital signatues for users "test2" and "test3" (user "test1" did not survice the development phase).
The passwords are also "test2" and "test3".
* Select "sign" to pretent to be a user that should see the documents he needs to sign.
* Enter the password for the key (The passwords are also "test2" and "test3") to sign a document. 
After signing it gets added to the blockchain and you will see a transaction id as proof. 
Reloading the page at this time will just add it again.
* Select "check" to check a documents signature. It will show you all documents added to the blockchain.
Select the timestamp of the document you would like to check and it will show you the outcome of the check.

# hacking
So, if you have come this far, there is still hope for you :-).
Here are some notes that may come in handy.

* This is not briljant code (yet). This is a proof-of-concept and for demonstration purposes.
* It should be expanded with proper authentication, proper use of libs, and a proper workflow library should be added. 
* The gpg environment is created inside the root directory of the checked out git repo (subdir gnupg).
* I use the GNUPHOME environment variable for that.
* I developed this using multichain 1.0.1. 
* I use a small sqlite database to keep track of queued documents (to link a gpg key hash to a document filename)
* This is a play-around application. I do not delete records from the upload directory nor from the sqlite database.
This is a proof-of-concept kind of thing (but I am repeating myself here).
* If you enter an invalid url you get a random 404 error message. 
In the directory static/404 there are a few images that will randomly be shown.
I tried to make sure that the license allows them to be shared, but if anybody claims otherwise I will be more than happy to remove them.
Feel free to add your own if you like.  

Thanks for your attention.
Kind regards,
Jeroen Baten
November 2017
