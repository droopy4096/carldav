#!/bin/env python

from xml.etree.ElementTree import ElementTree
import xml.etree.ElementTree as ET

import sys
import json
import os.path
import os
import argparse

def env(var_name):
    try:
        return os.environ[var_name]
    except KeyError:
        return None

def parse_calendar(calendar_name,calendar_xml,args):
    mydoc = ET.fromstring(calendar_xml)
    try:
        os.makedirs(os.path.join(args.ical_dir,calendar_name))
    except FileExistsError:
        pass
    calendars=[]
    for r in mydoc.findall('./d:response', 
                    namespaces={'d':'DAV:', 'cal':'urn:ietf:params:xml:ns:caldav'}):
        hrefs=[]
        for href in r.findall('./d:href',
                        namespaces={'d':'DAV:', 'cal':'urn:ietf:params:xml:ns:caldav'}):
                    hrefs.append(href.text)
        cal_data=[]
        for cal in r.findall('*//cal:calendar-data',
                        namespaces={'d':'DAV:', 'cal':'urn:ietf:params:xml:ns:caldav'}):
                    if not cal.text:
                        continue
                    crlf_text=cal.text.replace("\n","\r\n")
                    cal_data.append(cal.text)
        ical_filename=hrefs[0].split('/')[-1]
        if not ical_filename:
            continue
        print("processing: {}".format(ical_filename))
        if args.individual:
            with open(os.path.join(args.ical_dir,calendar_name,ical_filename),'w') as ical_file:
                ical_file.write("\r\n".join(cal_data))
        calendars.append(cal_data)
    if args.full:
        print("writing full ical")
        with open(os.path.join(args.ical_dir,calendar_name+'.ics'), 'w') as full_calendar:
            for cal_entry in calendars:
                full_calendar.write("\r\n".join(cal_entry))

if __name__ == "__main__":
    env_vars=['CALDAV_URI','CALDAV_USER','CALDAV_PASSWORD','CALDAV_CALENDARS']
    env_defaults={}
    for v in env_vars:
        if v=='CALDAV_CALENDARS':
            res=env(v)
            if res:
                env_defaults[v]=res.split()
            else:
                env_defaults[v]=res
        else:
            env_defaults[v]=env(v)
    parser = argparse.ArgumentParser(description='Extract ical from CalDav Export')
    parser.add_argument('--caldav-uri', default=env_defaults['CALDAV_URI'])
    parser.add_argument('--caldav-user', default=env_defaults['CALDAV_USER'])
    parser.add_argument('--caldav-password', default=env_defaults['CALDAV_PASSWORD'])
    parser.add_argument('--caldav-calendar', dest='caldav_calendars', metavar='CALDAV_CALENDAR', action='append', default=env_defaults['CALDAV_CALENDARS'], help='use multiple entries for multiple calendars')
    parser.add_argument('--netrc-file', default=os.environ['HOME'])
    parser.add_argument('--filename', 
                    help='XML file with calendar entries exported via CalDav')
    parser.add_argument('--no-individual', dest='individual', action="store_false")
    parser.add_argument('--write-individual', dest='individual', action="store_true", default=True)
    parser.add_argument('--no-full', dest='full', action="store_false")
    parser.add_argument('--write-full', dest='full', action="store_true", default=False)

    parser.add_argument('--ical-dir', default='./ical')

    args = parser.parse_args()

    if args.caldav_uri and args.caldav_calendars:
        # we have remote calendars to fetch
        username=args.caldav_user
        password=args.caldav_password
        if args.netrc_file:
            import netrc
            import urllib.parse
            uri=urllib.parse.urlparse(args.caldav_uri)
            n=netrc.netrc(args.netrc_file)
            (username,account,password)=n.authenticators(uri.hostname)
        # start fetching...
        import requests
        my_headers={
            "Content-Type": "text/xml",
            "Depth": "1",
        }
        my_data="<propfind xmlns='DAV:'><prop><calendar-data xmlns='urn:ietf:params:xml:ns:caldav'/></prop></propfind>"
        for calendar in args.caldav_calendars:
            url="{uri}/{calendar}".format(uri=args.caldav_uri,calendar=calendar)
            r=requests.request('PROPFIND',url, 
                    headers=my_headers,
                    data=my_data,
                    auth=(username,password))
            parse_calendar(calendar,r.text,args)

    elif args.filename:
        calendar_filename=args.filename
        calendar_name=calendar_filename.split('/')[-1].split('.')[0]
        with open(calendar_filename,'r') as f:
            parse_calendar(calendar_name,f.read(),args)
