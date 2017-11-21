#!/usr/bin/env python
#
# bpg2 is an application to add digitally signed documents to a blockchain
# Copyright (C) 2017 Jeroen Baten
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""This is a PoC script to upload a file, gpg sign it, add to a blockchain,
and extract and verify it."""

__author__ = "Jeroen Baten"
__copyright__ = "Copyright 2017, Jeroen Baten"
__credits__ = ["Jeroen Baten"]
__license__ = "GNU Affero General Public License"
__version__ = "1.0"
__maintainer__ = "Jeroen Baten"
__email__ = "jbaten@i2rs.nl"
__status__ = "Proof of Concept"
__version__ = "$Id$"

# all the imports
import os
from os import listdir
from os.path import expanduser, isfile
from os.path import join
import time
import binascii
import sqlite3
from pprint import pprint, pformat
from random import choice
import socket
import commands
import gnupg
from flask import Flask, request, g, redirect, url_for, render_template, flash
from werkzeug.utils import secure_filename
from Savoir import Savoir


APP = Flask(__name__)  # create the application instance :)
APP.config.from_object(__name__)  # load config from this file , bpg2.py

# Load default config and override config from an environment variable
APP.config.update(dict(
    DATABASE=os.path.join(APP.root_path, 'bpg2.db'),
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='admin',
    MULTICHAIN='multichain-1.0.1',
    UPLOAD_FOLDER='uploaded',
    SIGNED_FOLDER='signed',
    CHECK_FOLDER='check'
))
APP.config.from_envvar('BPG2_SETTINGS', silent=True)

# Define needed port and interface
RPCPORT = 8570
RPCHOST = 'localhost'
CHAINNAME = 'documents'

CHAINSOFTWARELOCATION = os.path.join(APP.root_path, APP.config['MULTICHAIN'])
HOME = expanduser("~")  # we really nned this, otherwise directory expansion screws up
MULTICHAINDATALOCATION = HOME + "/.multichain/" + CHAINNAME + "/"
MULTICHAINDATALOCATION = os.path.abspath(MULTICHAINDATALOCATION)

# Get userid and password for API from ~/.multichain/documents/multichain.conf
MULTICHAINCONFIGFILE = HOME + "/.multichain/" + CHAINNAME + "/multichain.conf"


def connect_db():
    """Connects to the specific database."""
    returnvalue = sqlite3.connect(APP.config['DATABASE'])
    returnvalue.row_factory = sqlite3.Row
    return returnvalue


def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


@APP.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()
    return error

@APP.route('/')
def index():
    """Show homepage"""
    return render_template('index.html')


def checkmultichainrunning():
    """
    Check if the MultiChain deamon is listening on his port.
    :return: True if alive
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        multichainstatus = False
        sock.bind(("127.0.0.1", RPCPORT))
    except socket.error as err:
        # if e.errno == 98:
        #    print("Port is in use")
        print "Got error: " + pformat(err)
        multichainstatus = True
    return multichainstatus


def getlogincredentials():
    """Find multichain login credentials in config file"""
    fil = open(MULTICHAINCONFIGFILE)
    rpcuser = None
    rpcpassword = None
    for line in iter(fil):
        # print line
        if 'rpcuser' in line:
            rpcuser = line.split("=")[1].rstrip()
        if 'rpcpassword' in line:
            rpcpassword = line.split("=")[1].rstrip()
    fil.close()
    return rpcuser, rpcpassword


@APP.route('/admin')
def admin(multichainstatus=None):
    """Find status of mailchaind. Running or not?"""
    multichainstatus = checkmultichainrunning()
    pprint(multichainstatus)
    return render_template('admin.html', multichainstatus=multichainstatus)


@APP.route('/multichain/', methods=['GET', 'POST'])
def multichainstartstop(multichainstatus=None):
    """Display MultiChain status"""
    multichainstatus = checkmultichainrunning()
    if request.method == 'POST':
        if request.form['do'] == "start":
            # Start multichain
            # Is there already a repository?
            print "Checking existence of " + MULTICHAINDATALOCATION
            # os.system("ls -l " + multichainDataLocation)
            if not os.path.exists(MULTICHAINDATALOCATION):
                # create directory
                # os.makedirs(multichainDataLocation)
                # If not initialise: multichain-util create [chain-name]
                # -maximum-block-size=16777216
                # -datadir=application path
                # default-rpc-port	Default IP port to use for JSON-RPC calls to multichaind
                #   (can be overridden by each node using the rpcport runtime parameter).
                print "Initialise documents blockchain"
                cmd = CHAINSOFTWARELOCATION + "/multichain-util create " + CHAINNAME \
                      + " -maximum-block-size=1000000000 " \
                      + " -default-rpc-port=" + str(RPCPORT)
                print "Executing cmd:"+cmd
                result = os.system(cmd)
                print result
                # Now create the dox stream:
                # multichain-1.0.1/multichain-cli  documents create stream dox true
                # '{"description":"[documents dox Stream]
                # All documents should uuencoded and gpg signed."}'
                cmd = CHAINSOFTWARELOCATION + "/multichain-cli " + CHAINNAME \
                      + " create stream dox true '{\"description\":\"[documents dox Stream] " \
                      "All documents should uuencoded and gpg signed.\"}'"
                print "Executing cmd:" + cmd
                result = os.system(cmd)
                print result
                # Now this user must subscribe to this stream
                # multichain-cli documents subscribe dox
                cmd = CHAINSOFTWARELOCATION + "/multichain-cli " + CHAINNAME + " subscribe dox "
                print "Executing cmd:" + cmd
                result = os.system(cmd)
                print "Number of transactions: " + str(len(str(result)))
                print result
            else:
                print "Directory " + MULTICHAINDATALOCATION + " exists, so no initialisation."

            # Initialise the chain: multichaind chain1 -daemon
            # Is it already running?
            # multichainStatus=checkMultiChainRunning
            try:
                print "Starting multichain daemon"
                cmd = CHAINSOFTWARELOCATION + "/multichaind " + CHAINNAME + " -daemon "
                print "Executing cmd:" + cmd
                os.system(cmd)
            except socket.error as err:
                if err.errno == 98:
                    print "Port is already in use. Daemon already running."

            # Check if running: getinfo call
            # cmd=chainSoftwareLocation + "/multichain-cli " + chainname + "  getinfo"
            # print "Executing cmd:" + cmd
            # os.system(cmd)
            #
            # cmd = chainSoftwareLocation + "/multichain-cli " + chainname + "  listpermissions"
            # print "Executing cmd:" + cmd
            # os.system(cmd)
            #
            # cmd = chainSoftwareLocation + "/multichain-cli " + chainname + "  getaddresses"
            # print "Executing cmd:" + cmd
            # os.system(cmd)

            # Is it running now? Should be through getinfo call
            multichainstatus = checkmultichainrunning
            # multichainStatus=True

        if request.form['do'] == "stop":
            # TODO Stop multichain:  stop command was issued through the API
            multichainstatus = False

    return render_template('admin.html', multichainStatus=multichainstatus)


@APP.route('/getinfo')
def getinfo(message=""):
    """Show several informations"""
    multichainstatus = checkmultichainrunning()
    if multichainstatus:
        rpcuser, rpcpassword = getlogincredentials()
        api = Savoir(rpcuser, rpcpassword, RPCHOST, str(RPCPORT), CHAINNAME)
        message = "<pre>"
        message = message + "<h2>Multichaind getinfo</h2>"
        message = message + pformat(api.getinfo())
        # List available streams
        message = message + "</pre>"
        message = message + "<h2>Blockchain streams</h2>"
        message = message + "<pre>"
        message = message + pformat(api.liststreams())
        message = message + "</pre>"
        # List transactions on stream 'dox'
        message = message + "<h2>Blockchain transactions on stream 'dox'</h2>"
        message = message + "<pre>"
        message = message + pformat(api.liststreamitems('dox'))
        message = message + "</pre>"
        # liststreamkeyitems: This works like liststreamitems,
        # but listing items with the given key only.
        # message = message + "<h2>Blockchain keys on stream 'dox'</h2>"
        # message = message + "<pre>"
        # message = message + pformat(api.liststreamkeyitems('dox'))
        # message = message + "</pre>"
        # liststreamkeyitems
        message = message + "<h2>Blockchain liststreamkeys on stream 'dox'</h2>"
        message = message + "<pre>"
        message = message + pformat(api.liststreamkeys('dox'))
        message = message + "</pre>"

    # Show some database info
    mydb = get_db()
    print "Database info:"
    pprint(mydb)
    # curs = mydb.cursor()
    message = message + "</pre>"
    message = message + "<h2>Database info</h2>"
    message = message + "<pre>"
    for line in mydb.iterdump():
        print '%s\n' % line
        message = message + line + "\n"
    message = message + "</pre>"
    print "Message send to template:"
    pprint(message)
    return render_template('admin.html', multichainstatus=multichainstatus, message=message)


@APP.route('/upload', methods=['GET', 'POST'])
def upload_file():
    """Upload a file"""
    directory = os.path.join(APP.root_path, APP.config['UPLOAD_FOLDER'])
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        uploadfile = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if uploadfile.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if uploadfile:
            filename = secure_filename(uploadfile.filename)
            pprint(filename)

            pprint(directory)
            uploadfile.save(join(directory, filename))
            # return redirect(url_for('uploaded_file',filename=filename))

    # Build list of files in uploaded directory
    uploadedfiles = [f for f in listdir(directory) if isfile(join(directory, f))]
    return render_template('upload.html', uploadedFiles=uploadedfiles)


@APP.route('/assigndoc', methods=['GET', 'POST'])
def assigndoc(uploadedfiles=None, document=None):
    """Assign needed signatures to uploaded file."""
    if request.method == 'POST':
        if request.form['document'] is not None:
            document = request.form['document']
            pprint(document)
            # Find all available keys
            # Doc: http://pythonhosted.org/gnupg/gnupg.html
            gnu_path = os.path.join(APP.root_path, "gnupg")
            gpg = gnupg.GPG(homedir=gnu_path)  # ,verbose=8)
            gpg.encoding = 'utf-8'
            public_keys = gpg.list_keys(secret=False)  # same as gpg.list_keys(False)
            pprint(public_keys)
            key_list = []
            for key in public_keys:
                key_list.append({"key": key["fingerprint"], "uid": key["uids"][0]})
            return render_template('assignsig.html', keyList=key_list, document=document)
    else:
        # present a selection list of documents to be signed
        directory = os.path.join(APP.root_path, APP.config['UPLOAD_FOLDER'])
        uploadedfiles = [f for f in listdir(directory) if isfile(join(directory, f))]
    return render_template('assigndoc.html', uploadedFiles=uploadedfiles, document=document)


@APP.route('/assignsig', methods=['GET', 'POST'])
def assignsig(document=None):
    """Assign signature to file"""
    # Handle posted data
    if request.method == 'POST':
        # pprint(request.form['neededsigs'])
        if request.form['neededsigs'] is not None:
            document = request.form['document']
            print "Acquiring needed sigs"
            neededsigs = request.form.getlist('neededsigs')
            # Now we need to add these to the sign queue in the database
            for gpgkey in neededsigs:
                # Add this key + document to the queue
                mydb = get_db()
                my_cursor = mydb.cursor()
                query = "insert into signqueue(gpgkey,document) values" \
                      " ('" + gpgkey + "','" + document + "');"
                pprint(query)
                my_cursor.execute(query)
                mydb.commit()

            return render_template('assignsig.html', keyList=None, document=document)
    return redirect("/assigndoc", code=302)


@APP.route('/sign', methods=['GET', 'POST'])
def sign(uid=None):
    """Show files needed to be signed by user."""
    if request.method == 'POST':
        # pprint(request.form['neededsigs'])
        if request.form['uid'] is not None:
            uid = request.form['uid']
            pprint(uid)
            # retrieve all outstanding work
            my_db = get_db()
            my_cursor = my_db.cursor()
            query = "select * from signqueue where gpgkey='" + uid + "';"
            pprint(query)
            documents = []
            for row in my_cursor.execute(query):
                pprint(row)
                documents.append(row["document"])
            return render_template('sign.html', documents=documents, uid=uid)
    else:
        gnu_path = os.path.join(APP.root_path, "gnupg")
        gpg = gnupg.GPG(homedir=gnu_path)  # ,verbose=8)
        gpg.encoding = 'utf-8'
        public_keys = gpg.list_keys(secret=False)  # same as gpg.list_keys(False)
        pprint(public_keys)
        key_list = []
        for key in public_keys:
            key_list.append({"key": key["fingerprint"], "uid": key["uids"][0]})
        return render_template('sign.html', keyList=key_list)
    return render_template('sign.html')


@APP.route('/signature', methods=['GET', 'POST'])
def signature(uid=None, document=None, passphrase=None):
    """Add signed document to blockchain."""
    multichain_status = checkmultichainrunning()
    if multichain_status:
        if request.method == 'POST':
            print "Handling POST..."
            if request.form.get('passphrase', None) is not None:
                print "We have a passphrase..."
                passphrase = request.form.get('passphrase', None)
                if request.form.get('uid') is not None:
                    uid = request.form.get('uid', None)
                    rpcuser, rpcpassword = getlogincredentials()
                    api = Savoir(rpcuser, rpcpassword, RPCHOST, str(RPCPORT), CHAINNAME)
                    print "we have a uid : " + uid
                    if request.form.get('document', None) is not None:
                        document = request.form.get('document')
                        print "we have a document : " + document
                        # gnu_path = os.path.join(APP.root_path, "gnupg")
                        # TODO: refactor to use gpgme lib?
                        # gpg = gnupg.GPG(homedir=gnuPath)
                        # Now we convert document to uuencode64
                        # upload_directory = os.path.join(APP.root_path,
                        #                                 APP.config['UPLOAD_FOLDER'])
                        # signed_directory = os.path.join(APP.root_path,
                        #                                 APP.config['SIGNED_FOLDER'])
                        file_in = os.path.join(os.path.join(APP.root_path,
                                                            APP.config['UPLOAD_FOLDER']),
                                               document)
                        file_out = os.path.join(os.path.join(APP.root_path,
                                                             APP.config['SIGNED_FOLDER']),
                                                document) + ".gpg"
                        # We sign the document, plain and simple:
                        #  gpg --sign --local-user <userhash>  --output <outputfile>
                        # --passphrase <passphrase>  <filetosign>
                        cmd = "gpg --batch --yes --sign --local-user " + uid + \
                            " --passphrase " + passphrase + " --output " + file_out + " " + file_in
                        pprint(cmd)
                        os.system(cmd)
                        # and now we store the document in the blockchain
                        with open(file_out, "rb") as signed_document_file:
                            content = signed_document_file.read()
                        payload = binascii.hexlify(content)
                        # publish	stream, key, data-hex: Publishes an item in stream,
                        # passed as a stream name, ref or creation txid,
                        # with key provided in text form and data-hex in hexadecimal.
                        result = api.publish('dox', document, payload)
                        flash("Transaction ('" + result + "') added to the blockchain.")
                    else:
                        flash("missing document")
                else:
                    flash("Missing UID")
                # return render_template('signature.html', uid=uid, document=document)

            else:
                if request.form.get('uid', None) is not None:
                    uid = request.form.get('uid', None)
                    if request.form.get('document', None) is not None:
                        document = request.form.get('document', None)
                        return render_template('signature.html', uid=uid, document=document)
    else:
        flash("Multichain not running.")

    return render_template('sign.html')


@APP.route('/check', methods=['GET', 'POST'])
def check(documents=None, document=None, versions=None):
    """Check signature of file"""
    multichain_status = checkmultichainrunning()
    if multichain_status:
        if request.method == 'POST':
            print "Handling POST..."
            rpcuser, rpcpassword = getlogincredentials()
            api = Savoir(rpcuser, rpcpassword, RPCHOST, str(RPCPORT), CHAINNAME)
            if request.form.get('document', None) is not None:
                print "We have a document..."
                document = request.form.get('document', None)
                # retrieve versions of document
                versions = []
                # liststreamkeyitems: stream key (verbose=false)
                # (count=10) (start=-count) (local-ordering=false)
                # This works like liststreamitems, but listing items
                # with the given key only.

                transactions = api.liststreamkeyitems('dox', document)
                # we are only interested in txid and blocktime
                for transaction in transactions:
                    # blocktime:  $ date -d @
                    datum = time.strftime('%Y-%m-%d %H:%M:%S',
                                          time.localtime(transaction["blocktime"]))
                    versions.append({"txid": transaction["txid"], "datum": datum})
            elif request.form.get('txid', None) is not None:
                print "We have a txid..."
                txid = request.form.get('txid', None)
                print txid
                # Now get all info for this transaction
                # getstreamitem	stream txid
                # (verbose=false)	Retrieves a specific item with txid from stream,
                # passed as a stream name, ref or creation txid,
                # to which the node must be subscribed.
                # Set verbose to true for additional information about the item's transaction.
                # If an item's data is larger than the maxshowndata runtime parameter,
                # it will be returned as an object whose fields can be used with gettxoutdata.
                result1 = api.getstreamitem('dox', txid, True) # does not always work: So use:
                pprint(result1)
                vout = result1["vout"]
                #
                # gettxoutdata	txid vout (count-bytes=INT_MAX) (start-byte=0)
                # Returns the data embedded in output vout of transaction txid,
                # in hexadecimal. This is particularly useful if a stream item's
                # data is larger than the maxshowndata runtime parameter.
                # Use the count-bytes and start-byte parameters to retrieve
                # part of the data only.
                result2 = api.gettxoutdata(txid, vout)
                # destination_file = os.path.join(APP.root_path,
                #                                 APP.config['CHECK_FOLDER'],
                #                                 "result2.txt")
                # print "Writing result2 to '" + str(destination_file) + "'."
                # with open(destination_file, "wb") as output_file:
                #     output_file.write(pformat(result2))

                # Find directory to dump result in
                destination_file = os.path.join(APP.root_path,
                                                APP.config['CHECK_FOLDER'],
                                                result1["key"])
                # reverse this: payload = binascii.hexlify(content)
                print "Retrieving payload in binary form."
                payload = binascii.unhexlify(result2)
                print "Writing output to '" + str(destination_file) + "'."
                with open(destination_file, "wb") as output_file:
                    output_file.write(payload)
                # $ gpg --verify file
                cmd = "gpg --verify " + destination_file
                pprint(cmd)
                status, output = commands.getstatusoutput(cmd)
                output = output.replace('\n', '<br />')
                print "program output: ", output
                print "program exit status: " + str(status)
                # write output to file
                # destinationFile = os.path.join(app.root_path,
                # app.config['CHECK_FOLDER'], result["key"]) + ".cmdoutput"
                # with open(destinationFile, "wb") as output_file:
                #    output_file.write(output)
                #    output_file.write("\n\n\n")
                flash(output)

        else:
            # liststreamitems stream1 false 999999
            rpcuser, rpcpassword = getlogincredentials()
            api = Savoir(rpcuser, rpcpassword, RPCHOST, str(RPCPORT), CHAINNAME)
            keys = api.liststreamkeys('dox')
            # pprint(keys)
            documents = []
            for key in keys:
                # pprint(key)
                documents.append(key["key"])
    else:
        flash("Multichain not running.")

    return render_template('check.html', documents=documents, document=document, versions=versions)


# Just kidding! :-)
@APP.errorhandler(404)
def page_not_found():
    """Display random 404 error page"""
    # create list of 404 images in directory "404"
    names = os.listdir(os.path.join(APP.static_folder, '404'))
    img_url = url_for('static', filename=os.path.join('404', choice(names)))

    return render_template('page_not_found.html', img_url=img_url), 404
    # return render_template('page_not_found.html',image=image), 404
