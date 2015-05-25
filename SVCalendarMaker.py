__author__ = 'CaroB'

from PyQt4 import QtGui
import sys
from bs4 import BeautifulSoup
import time
import pytz
import datetime

"""
    MAIN WINDOW
    * Main GUI
    * Contains Widget and Core
"""

class MainWindow(QtGui.QMainWindow):

    def __init__(self, app):
        super(MainWindow, self).__init__()

        self.setWindowTitle('SV Calendar Maker')
        self.setMaximumSize(400, 150)
        self.setMinimumSize(250, 150)


        self._app = app

        self.main_widget = MainWidget(self, app)
        self.setCentralWidget(self.main_widget)

"""
    MAIN WIDGET
    * GUI Part
    * Pick Time zone
    * Load SVPlanning HTML page
    * Save as iCalendar
"""
class MainWidget(QtGui.QWidget):

    def __init__(self, parent, app):
        super(MainWidget, self).__init__(parent)

        # Core linking
        self._app = app

        #
        # GUI with PyQt
        #

        self.main_v_layout = QtGui.QVBoxLayout(self)

        # Time Zones
        self.h_layout_5 = QtGui.QHBoxLayout()
        self.combobox_timezones = QtGui.QComboBox()
        self.combobox_timezones.addItem("-- Select Destination Time Zone --")
        for zone in pytz.common_timezones:
            self.combobox_timezones.addItem(zone)

        self.combobox_timezones.currentIndexChanged['QString'].connect(self.tzChanged)

        self.h_layout_5.addWidget(self.combobox_timezones)

        # Open File
        self.h_layout_1 = QtGui.QHBoxLayout()
        self.line_edit_filename = QtGui.QLineEdit()
        self.line_edit_filename.setReadOnly(True)
        self.open_button = QtGui.QPushButton("Open")
        self.open_button.clicked.connect(self.open)

        self.h_layout_1.addWidget(self.line_edit_filename)
        self.h_layout_1.addWidget(self.open_button)

        # Label Info
        self.h_layout_2 = QtGui.QHBoxLayout()
        self.label_info = QtGui.QLabel()

        self.h_layout_2.addWidget(self.label_info)

        # Choose format and Save
        self.h_layout_3 = QtGui.QHBoxLayout()
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.save_button = QtGui.QPushButton("Save as")
        self.save_button.clicked.connect(self.saveAs)

        self.h_layout_3.addItem(spacerItem)
        self.h_layout_3.addWidget(self.save_button)

        #
        spacerItem2 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)

        # Close
        self.h_layout_4 = QtGui.QHBoxLayout()
        spacerItem3 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.howto_button = QtGui.QPushButton("HOW TO USE")
        self.howto_button.clicked.connect(self.howTo)
        self.close_button = QtGui.QPushButton("Close")
        self.close_button.clicked.connect(self.close)

        self.h_layout_4.addItem(spacerItem3)
        self.h_layout_4.addWidget(self.howto_button)
        self.h_layout_4.addWidget(self.close_button)

        # Layout
        self.main_v_layout.addLayout(self.h_layout_5)
        self.main_v_layout.addLayout(self.h_layout_1)
        self.main_v_layout.addLayout(self.h_layout_3)
        self.main_v_layout.addLayout(self.h_layout_2)
        self.main_v_layout.addItem(spacerItem2)
        self.main_v_layout.addLayout(self.h_layout_4)

    """
        Open SVPlanning HTML page
    """
    def open(self):
        filename = self._app.filename()
        filename = QtGui.QFileDialog.getOpenFileName(self, 'Open File', filename or '',
                                                     "HTML page (*.htm *.html)")

        filename = str(filename)
        if not filename:
            return

        self.label_info.setText("")
        self.line_edit_filename.setText(filename)
        self._app.setFilename(filename)
        self._app.openHtmlSoup(filename)

        if self._app.shifts():
            self._app.makeCalendar(self._app.shifts())

    """
        Save SVPlanning loaded as iCalendar
    """
    def saveAs(self):
        filename = self._app.filename()

        filename = QtGui.QFileDialog.getSaveFileName(self, 'Save Calendar', filename or '', "iCalendar (*.ics)")
        filename = str(filename)
        if not filename:
            return

        if self._app._writer.ics():
            self._app.writeCalendar(filename)
            self.label_info.setText("Save " + filename)
            print "Save " + filename
        else:
            self.label_info.setText("Nothing to save")
            print "Nothing to save"

    """
        Explanations how this soft works
    """
    def howTo(self):
        MESSAGE = "<p>1 - Go to your SV schedule on the website :</p>" \
                "<p>\tLog into your account at " \
                "<a href=\"http://sis.siggraph.org\">http://sis.siggraph.org/</a></p>" \
                "<p>\tClick on \"Student Volunteer System\"</p>" \
                "<p>\tSelect \"Student Schedules\"</p>" \
                "<p>2 - Save the web page (as HTML)</p>" \
                "<p>3 - Open this page in SV CALENDAR MAKER</p>" \
                "<p>4 - Save it as .iCalendar</p>" \
                "<p>5 - You're done! You can load your calendar on your smartphone or web agenda</p>" \
                "<p>Enjoy!, Caro</p>"

        reply = QtGui.QMessageBox.information(self, "How To Use the SV CALENDAR MAKER", MESSAGE)

    """
        Set selected Timezone to the Core
    """
    def tzChanged(self, str):
        if str == "-- Select Destination Time Zone --":
            str = "UTC"
        self._app.setTimezone(str)

    """
        Close SVCalendarMaker
    """
    def close(self):
        print "Goodbye!"
        self.parent().close()




"""

    CORE
    * Shift = 1 event in SVPlanning
    * Parser = read info from HTML page
    * Writer = translate HTML info to iCalendar info
    * App = holds all info

"""

"""
    SHIFT
    * Contains all following info
        * data
        * number of shift
        * location
        * starting date and time
        * ending date and time
        * duration of shift
        * title of shift - what you're supposed to do
        * additional info and description of task
        * if you can swap this shift with someone else
"""
class Shift(object):
    def __init__(self, date=None, shift_nb=None):
        super(Shift, self).__init__()

        self._date = date
        self._shift_nb = shift_nb
        self._venue = None
        self._start = None
        self._end = None
        self._duration = None
        self._job = None
        self._text = None
        self._swappable = None

    def date(self):
        return self._date

    def setDate(self, date):
        self._date = date

    def shiftNb(self):
        return self._shift_nb

    def setShiftNb(self, shift):
        self._shift_nb = shift

    def venue(self):
        return self._venue

    def setVenue(self, venue):
        self._venue = venue

    def start(self):
        return self._start

    def setStart(self, start):
        self._start = start

    def end(self):
        return self._end

    def setEnd(self, end):
        self._end = end

    def duration(self):
        return self._duration

    def setDuration(self, dur):
        self._duration = dur

    def job(self):
        return self._job

    def setJob(self, job):
        self._job = job

    def text(self):
        return self._text

    def setText(self, txt):
        self._text = txt

    def swappable(self):
        return self._swappable

    def setSwappable(self, swappable):
        self._swappable = swappable

    def to_print(self):
        print "SHIFT " + str(self.shiftNb())
        print self.date()
        print self.venue()
        print self.start()
        print self.end()
        print self.duration()
        print self.job()
        print self.text()
        print self.swappable()
        print "_______"

"""
    PARSER
    * Reads info from HTML page using beautifulsoup library
    * Stores each shift from SVPlanning in a Shift object
"""
class Parser(object):
    def __init__(self):
        super(Parser, self).__init__()

        self._filename = None
        self._shifts = None

    def filename(self):
        return self._filename

    def setFilename(self, name):
        self._filename = name

    def shifts(self):
        return self._shifts

    def setShifts(self, shifts):
        self._shifts = shifts

    def openHtmlSoup(self, filename):
        soup = None

        with open (filename, "r") as myfile:
            data = myfile.read()
            soup = BeautifulSoup(data)

        if soup:
            self.extractTags(soup)

    def extractTags(self, soup):
        shifts = []
        date = None
        current_shift = None

        trs = soup.find_all('tr')

        for tr in trs:
            if tr.find('td', {'class' : 'Date text'}):
                date = tr.find('td', {'class' : 'Date text'}).string

            if tr.find('td', {'class' : 'Shift text'}):
                current_shift = Shift(date, tr.find('td', {'class' : 'Shift text'}).string)

            if tr.find('td', {'class' : 'Venue text'}):
                if not current_shift.venue():
                    current_shift.setVenue(tr.find('td', {'class' : 'Venue text'}).string)
                else:
                    print "Venue Error"

            if tr.find('td', {'class' : 'Start time'}):
                if not current_shift.start():
                    current_shift.setStart(tr.find('td', {'class' : 'Start time'}).string)
                else:
                    print "Start Error"

            if tr.find('td', {'class' : 'End time'}):
                if not current_shift.end():
                    current_shift.setEnd(tr.find('td', {'class' : 'End time'}).string)
                else:
                    print "End Error"

            if tr.find('td', {'class' : 'Duration numeric'}):
                if not current_shift.duration():
                    current_shift.setDuration(tr.find('td', {'class' : 'Duration numeric'}).string)
                else:
                    print "Duration Error"

            if tr.find('td', {'class' : 'JobDesc text'}):
                if not current_shift.job():
                    current_shift.setJob(tr.find('td', {'class' : 'JobDesc text'}).string)
                else:
                    print "Job Error"

            if tr.find('td', {'class' : 'Special text'}):
                if not current_shift.text():
                    current_shift.setText(tr.find('td', {'class' : 'Special text'}).string)
                else:
                    print "Text Error"

            if tr.find('td', {'class' : 'Swappable bool'}):
                if not current_shift.swappable():
                    current_shift.setSwappable(tr.find('td', {'class' : 'Swappable bool'}).string)
                    shifts.append(current_shift)
                else:
                    print "Swappable Error"

        self._shifts = shifts

"""
    WRITER
    * writes read Shifts from HTML to iCalendar
"""
class Writer(object):
    def __init__(self, tz):
        super(Writer, self).__init__()

        self._timezone = tz
        self._ics = ""

    def timezone(self):
        return self._timezone

    def setTimezone(self, tz):
        self._timezone = str(tz)

    def ics(self):
        return self._ics

    def setIcs(self, ics):
        self._ics = ics

    def _initIcs(self):
        self._ics = "BEGIN:VCALENDAR\nVERSION:2.0\nPRODID:-//CaroB.//SV Calendar Maker\n"
        self._makeTimeZone()

    def _makeTimeZone(self):
        winter_offset = pytz.timezone(self._timezone).localize(datetime.datetime(1967,10,29)).strftime('%z')
        winter_name = pytz.timezone(self._timezone).localize(datetime.datetime(1967,10,29)).tzname()
        summer_offset = pytz.timezone(self._timezone).localize(datetime.datetime(1987,04,05)).strftime('%z')
        summer_name = pytz.timezone(self._timezone).localize(datetime.datetime(1987,04,05)).tzname()

        self._ics += "BEGIN:VTIMEZONE\n"
        self._ics += "TZID:" + self._timezone + "\n"
        self._ics += "X-LIC-LOCATION:" + self._timezone + "\n"
        self._ics += "BEGIN:DAYLIGHT\n"
        self._ics += "TZOFFSETFROM:" + winter_offset + "\n"
        self._ics += "TZOFFSETTO:" + summer_offset + "\n"
        self._ics += "TZNAME:" + summer_name + "\n"
        self._ics += "DTSTART:19870405T020000\n"
        self._ics += "RRULE:FREQ=DAILY\n"
        self._ics += "END:DAYLIGHT\n"
        self._ics += "BEGIN:STANDARD\n"
        self._ics += "TZOFFSETFROM:" + summer_offset + "\n"
        self._ics += "TZOFFSETTO:" + winter_offset + "\n"
        self._ics += "TZNAME:" + winter_name + "\n"
        self._ics += "DTSTART:19671029T020000\n"
        self._ics += "RRULE:FREQ=DAILY\n"
        self._ics += "END:STANDARD\n"
        self._ics += "END:VTIMEZONE\n"

    def makeCalendar(self, shifts):
        self._initIcs()

        for shift in shifts:
            s = self.makeShift(shift)
            self._ics += s

        self._ics += "END:VCALENDAR\n"

    def _makeStamp(self):
        gm_time = time.gmtime()

        Y = "{0:04d}".format(gm_time[0])
        M = "{0:02d}".format(gm_time[1])
        D = "{0:02d}".format(gm_time[2])

        H = "{0:02d}".format(gm_time[3])
        MIN = "{0:02d}".format(gm_time[4])
        S = "{0:02d}".format(gm_time[5])

        stamp = Y + M + D + "T" + H + MIN + S + "Z"
        return stamp

    def makeShift(self, shift):
        res = "BEGIN:VEVENT\nCATEGORIES:Shift\n"
        res += "DTSTAMP:" + self._makeStamp() + "\n"
        res += "UID:" + str(shift.shiftNb()) + "\n"
        res += "DTSTART;TZID=" + self._timezone + ":" + self.makeDate(shift.date(), shift.start()) + "\n"
        res += "DTEND;TZID=" + self._timezone + ":" + self.makeDate(shift.date(), shift.end()) + "\n"
        res += "SUMMARY:" + str(shift.job()) + "\n"
        res += "LOCATION:" + str(shift.venue()) + "\n"
        res += "DESCRIPTION:Shift #" + str(shift.shiftNb()) + " | Swappable : " + str(shift.swappable())
        res += " | Duration : " + str(shift.duration()) + " "
        if (shift.text()):
            res += " | Description : " + str(shift.text()) + "\n"
        else:
            res += "\n"
        res += "END:VEVENT\n"

        return res

    def makeDate(self, date, time):
        decomp = date.split()[1].split('-')
        y = decomp[2]
        d = decomp[0]
        m = self.findMonth(decomp[1])

        decomp = time.split(':')
        h = decomp[0]
        min = decomp[1]
        s = decomp[2]

        date = y + m + d + "T" + h + min + s
        return date

    def findMonth(self, m):
        if m == "Jan":
            return "01"
        elif m == "Feb":
            return "02"
        elif m == "Mar":
            return "03"
        elif m == "Apr":
            return "04"
        elif m == "May":
            return "05"
        elif m == "Jun":
            return "06"
        elif m == "Jul":
            return "07"
        elif m == "Aug":
            return "08"
        elif m == "Sep":
            return "09"
        elif m == "Oct":
            return "10"
        elif m == "Nov":
            return "11"
        elif m == "Dec":
            return "12"

    def writeCalendar(self, filename):
        print "TZ " + self._timezone
        with open (filename, "w") as myfile:
            myfile.write(self._ics)
            myfile.close()

"""
    APP
    * Main Core module
    * holds Parser and Writer objects to load HTML page and transforms it as iCalendar
"""
class App(object):
    def __init__(self):
        super(App, self).__init__()

        self._parser = Parser()
        self._writer = Writer("UTC")

        print "Welcome to SV Calendar Maker\n"

    def timezone(self):
        return self._writer.timezone()

    def setTimezone(self, tz):
        self._writer.setTimezone(tz)

    def filename(self):
        return self._parser.filename()

    def setFilename(self, name):
        self._parser.setFilename(name)

    def shifts(self):
        return self._parser.shifts()

    def setShifts(self, s):
        self._parser.setShifts(s)

    def openHtmlSoup(self, filename):
        self._parser.openHtmlSoup(filename)

    def ics(self):
        return self._writer.ics()

    def setIcs(self, i):
        self._writer.setIcs(i)

    def makeCalendar(self, shifts):
        self._writer.makeCalendar(shifts)

    def writeCalendar(self, filename):
        self._writer.writeCalendar(filename)

"""
    MAIN FUNCTION
    * Entry point
    * Launches application
"""
def main():
    qt_app = QtGui.QApplication([])

    app = App()

    w = MainWindow(app)
    w.show()
    qt_app.exec_()


if __name__ == '__main__':
    main()