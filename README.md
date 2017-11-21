# bpg2
A proof-of-concept work to combine blockchain technology to store openGPG signed documents.

I think in the near future thgis is the way to sign, store and archive important documents.

It simulated the workflow of the way I envision this to work in the future
* First somebody uploades a document into the system (or use a web service for that eventualy).
* Then the document signing gets assigned to one or more persons.
* Then, when these persons log in, they get a list of documents to sign.
* The sign the documents and the result is added/archived to the blockchain.

# Installation

Steps to install on Linux:
* Download multichain from https://www.multichain.com/download-install/
* Install GPG on your system
* Install multichain somewhere on your system. I used the root directory of this git repo for that.
* Edit the bpg2.conf file to match your environment, you can use bpg2.conf.sample for inspiration


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
The gpg environment is created inside the root directory of the checked out git repo (subdir gnupg).
I use the GNUPHOME environment variable for that.
I developed this using multichain 1.0.1. 

