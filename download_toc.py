#!/usr/bin/python

import requests
from BeautifulSoup import BeautifulSoup
import random
import time
import datetime
from datetime import timedelta
import optparse
import re


def get_issue_dates(start_date, end_date):
    """ Returns a list of all the Mondays in the specified date range
        (technically a superset of actual issue dates, since there isn't
        a new issue every week).""" 

    # Shift start date to first Monday in range
    start_shift = (7 - start_date.weekday()) % 7
    start_date = start_date + timedelta(start_shift)

    # Shift end date to last Monday in range
    end_shift = (end_date.weekday()) % 7
    end_date = end_date - timedelta(end_shift)

    issue_dates = []
    for n in range(0, int((end_date - start_date + timedelta(1)).days), 7):
        issue_dates += [start_date + timedelta(n)]

    print str(len(issue_dates)) + " dates in range"
    return issue_dates


def create_url(date):
    """ Returns the URL of the table of contents for a given date.""" 
    base_url = 'http://www.newyorker.com/magazine/toc/'
    (y, m, d) = str(date).split('-')
    url = base_url + y + '/' + m + '/' + d + '/toc'
    return url


def create_file_path(date, directory):
    """ Returns the location to save the HTML for a given issue.""" 
    (y, m, d) = str(date).split('-')
    if directory[-1] != '/':
        directory += '/'
    return directory + y + '-' + m + '-' + d + '.html'
    

def pause():
    """ Pauses for a random amount of time."""
    pause_length = 3 + abs(random.normalvariate(0, 10))
    print "Pausing for " + str(int(pause_length)) + " seconds"
    time.sleep(pause_length)
    

def download_toc(date, directory):
    """ Downloads the table of contents for a given issue date and saves it
        to the specified directory."""
    url = create_url(date)
    headers = { 'User-Agent' : 'Mozilla/4.0 (compatible; MSIE 6.1; Windows XP)' }
    r = requests.get(url, headers=headers)
    if r.status_code != 200:
        print str(date) + ': Status code ' + str(r.status_code)
    else:
        file_path = create_file_path(date, directory)
        f = open(file_path, 'w')
        f.write(r.content)
        f.close()
        print str(date) + ': Page downloaded'


def main():

    # Parse options
    parser = optparse.OptionParser()
    parser.add_option('-s', '--start_date', dest='start_date')
    parser.add_option('-e', '--end_date', dest='end_date')
    parser.add_option('-d', '--directory', dest="directory")
    options, args = parser.parse_args()

    # Required options
    if not options.start_date and not options.end_date:
        parser.error('--start_date and --end_date required')

    # Make sure dates are formatted correctly   
    year_re = re.compile(r'^(\d{4})$')
    date_re = re.compile(r'^(\d{4})-(\d{2})-(\d{2})$')
    
    m1 = re.match(date_re, options.start_date)
    m2 = re.match(year_re, options.start_date)
    if m1 != None:
        (y, m, d) = m1.groups()
        start_date = datetime.date(int(y), int(m), int(d))
    elif m2 != None:
        y = m2.group()
        start_date = datetime.date(int(y), 1, 1)
    else:
        parser.error('--start_date must be of format "YYYY" or "YYYY-MM-DD"')
        
    m3 = re.match(date_re, options.end_date)
    m4 = re.match(year_re, options.end_date)
    if m3 != None:
        (y, m, d) = m3.groups()
        end_date = datetime.date(int(y), int(m), int(d))
    elif m4 != None:
        y = m4.group()
        end_date = datetime.date(int(y), 12, 31)
    else:
        parser.error('--end_date must be of format "YYYY" or "YYYY-MM-DD"')

    # Save files to current directory if none specified
    if not options.directory:
        directory = "./"
    else:
        directory = options.directory

    issue_dates = get_issue_dates(start_date, end_date)
    for date in issue_dates:
        download_toc(date, directory)
        pause()


if __name__ == '__main__':
    main()
    
