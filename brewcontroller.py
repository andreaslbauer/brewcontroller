#!/usr/bin/python3

import logging

# set up the logger
logging.basicConfig(filename="/tmp/brewcontroller.log", format='%(asctime)s %(levelname)s %(message)s',
                    level=logging.INFO)

import webapp
import time
from brewdata import brewcontroller
import socket
import requests
import os
import threading

controllerthread = None


# the main routine
if __name__ == '__main__':

    # log start up message
    logging.info("***************************************************************")
    logging.info("Brew Controller Application has started")
    logging.info("Running %s", __file__)
    logging.info("Working directory is %s", os.getcwd())

    try:
        hostname = socket.gethostname()
        webapp.OurHostName = hostname
        externalip = requests.get('https://api.ipify.org').text
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 1))  # connect() for UDP doesn't send packets
        localipaddress = s.getsockname()[0]
        logging.info("Hostname is %s", hostname)
        logging.info("Local IP is %s and external IP is %s", localipaddress, externalip)

    except Exception as e:
        logging.exception("Exception occurred")
        logging.error("Unable to get network information")

    # start the controller threads

    logging.getLogger('werkzeug').level = logging.ERROR

    webapp.app.run(debug=True, host='0.0.0.0', port = 8000)



