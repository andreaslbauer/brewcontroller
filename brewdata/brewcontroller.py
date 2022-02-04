from brewdata import apis, relaiscontrol
import datetime
import logging
import time
import threading
import os

class Channel:

    # class init function
    def __init__(self, channelid):
        self.channelid = channelid
        self.temperature = 0
        self.time = timestr = datetime.datetime.now().strftime('%H:%M:%S')
        self.target = 66.0
        self.status = "TBD"
        self.statuscode = -1
        self.program = "Maintain Temperature"

        # load target from files
        self.load()

    # update measured data members
    def update(self):
        temp = apis.getTemperatureData(self.channelid)
        if (temp != None):
            self.temperature = temp
            self.time = datetime.datetime.now().strftime('%H:%M:%S')
        return temp

    # load data from persistent store
    def load(self):
        try:
            file = open("brewcontrollercfg" + str(self.channelid) + ".txt", "r")
            targetvalue = file.read()
            file.close()
            self.target = float(targetvalue)

        except:
            pass

    # load data from persistent store
    def store(self):
        file = open("brewcontrollercfg" + str(self.channelid) + ".txt", "w")
        file.write(str(self.target))
        file.close()


class Controller:

    # class init function
    def __init__(self, numberChannels):
        self.numberchannels = numberChannels
        self.channels = [] * self.numberchannels
        for i in range(0, self.numberchannels):
            self.channels.append(Channel(i + 1))

    # load all channel data
    def load(self):
        for i in range(0, self.numberchannels):
            self.channels[i].load()

    # store all channel data
    def store(self):
        for i in range(0, self.numberchannels):
            self.channels[i].store()

    # execute the main control loop that checks temperature, target and turn on/off the relais
    def runControlLoop(self):
        pid = os.getpid()
        logging.info("Controller thread started for %s channels, PID %i", self.numberchannels, pid)

        try:
            pidfile = open("brewcontrollerpid.txt", "w")
            pidfile.write(str(pid))
            pidfile.close()

        except Exception as e:
            logging.error("Exception when trying to write pid file")
            logging.error(e)

        time.sleep(3)

        keeprunning = True
        while keeprunning:

            pidfromfile = "1"

            try:
                pidfile = open("brewcontrollerpid.txt", "r")
                pidfromfile = pidfile.read()
                pidfile.close()
                logging.info("Latest PID from file is %s",
                             pidfromfile)

            except Exception as e:
                logging.error("Exception when trying to read pid file in controller thread")
                logging.error(e)

            if (pid != int(pidfromfile)):
                logging.info("Controller thread PID is %i, latest PID from file is %s, exiting controller thread", pid, pidfromfile)
                keeprunning = False
            else:

                #logging.info("Controller thread %i running, managing %i sensors", pid, self.numberchannels)
                for c in range(0, self.numberchannels):
                    try:

                        channel = self.channels[c]
                        channel.program = apis.getProgramName()

                        channel.update()
                        t = channel.temperature

                        logging.info("Looping channel %i - temperature is %f, target is %f",
                                     channel.channelid, t, channel.target)

                        if (t != None):

                            if (t > channel.target) and (channel.statuscode != 0):
                                relaiscontrol.relaisOff(channel.channelid)
                                channel.status = "Off"
                                channel.statuscode = 0
                                logging.info("Channel %i - temperature is %f, target is %f, turn relais off",
                                             channel.channelid, t, channel.target)
                            elif (t < channel.target) and channel.statuscode != 1:
                                relaiscontrol.relaisOn(channel.channelid)
                                channel.status = "Heating"
                                channel.statuscode = 1
                                logging.info("Channel %i - temperature is %f, target is %f, turn relais on",
                                             channel.channelid, t, channel.target)

                    except Exception as e:
                        logging.error("Channel %i - unable to get temperature for channel", c + 1)
                        logging.error(e)

                    time.sleep(10)

        logging.info("Controller thread is exiting")


# initialize global data
controller = Controller(2)


def startThreads():
    # start the control thread
    logging.info("Create controller thread")
    controllerthread = threading.Thread(target=controller.runControlLoop, daemon=False, args=())
    controllerthread.start()
    logging.info("Controller thread has been created")

startThreads()