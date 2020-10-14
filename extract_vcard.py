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

def parse_addressbook(addressbook_name, addressbook_xml, args):
    mydoc = ET.fromstring(addressbook_xml)
    try:
        os.makedirs(os.path.join(args.vcard_dir,addressbook_name))
    except FileExistsError:
        pass
    addresses=[]
    for r in mydoc.findall('./d:response', 
                    namespaces={'d':'DAV:', 'card':'urn:ietf:params:xml:ns:carddav'}):
        hrefs=[]
        for href in r.findall('./d:href',
                        namespaces={'d':'DAV:', 'card':'urn:ietf:params:xml:ns:carddav'}):
                    hrefs.append(href.text)
        card_data=[]
        for card in r.findall('*//card:address-data',
                        namespaces={'d':'DAV:', 'card':'urn:ietf:params:xml:ns:carddav'}):
                    card_data.append(card.text)
        vcard_filename=hrefs[0].split('/')[-1]
        if not vcard_filename:
            continue
        print("processing: {}".format(vcard_filename))
        if args.individual:
            with open(os.path.join(args.vcard_dir,addressbook_name,vcard_filename),'w') as vcard_file:
                vcard_file.write("\n".join(card_data))
        addresses.append(card_data)
    if args.full:
        print("writing full vcard")
        with open(os.path.join(args.vcard_dir,addressbook_name+'.vcs'), 'w') as full_addressbook:
            for card_entry in addresses:
                # full_calendar.write(cal_entry.to_ical())
                full_addressbook.write("\n".join(card_entry))

        

if __name__ == "__main__":
    env_vars=['CARDDAV_URI','CARDDAV_USER','CARDDAV_PASSWORD','CARDDAV_ADDRESSBOOKS']
    env_defaults={}
    for v in env_vars:
        if v=='CARDDAV_ADDRESSBOOKS':
            res=env(v)
            if res:
                env_defaults[v]=res.split()
            else:
                env_defaults[v]=res
        else:
            env_defaults[v]=env(v)
    parser = argparse.ArgumentParser(description='Extract VCARD from CardDav Export')
    parser.add_argument('--carddav-uri', default=env_defaults['CARDDAV_URI'])
    parser.add_argument('--carddav-user', default=env_defaults['CARDDAV_USER'])
    parser.add_argument('--carddav-password', default=env_defaults['CARDDAV_PASSWORD'])
    parser.add_argument('--carddav-addressbook', dest='carddav_addressbooks', metavar='CARDDAV_ADDRESSBOOK', action='append', default=env_defaults['CARDDAV_ADDRESSBOOKS'], help='use multiple entries for multiple addressbooks')
    parser.add_argument('--netrc-file', default=os.environ['HOME'])
    parser.add_argument('--filename', 
                    help='XML file with addressbook entries exported via CardDav')
    parser.add_argument('--no-individual', dest='individual', action="store_false")
    parser.add_argument('--write-individual', dest='individual', action="store_true", default=True)
    parser.add_argument('--no-full', dest='full', action="store_false")
    parser.add_argument('--write-full', dest='full', action="store_true", default=False)

    parser.add_argument('--vcard-dir', default='./vcard')

    args = parser.parse_args()

    if args.carddav_uri and args.carddav_addressbooks:
        # we have remote calendars to fetch
        username=args.carddav_user
        password=args.carddav_password
        if args.netrc_file:
            import netrc
            import urllib.parse
            uri=urllib.parse.urlparse(args.carddav_uri)
            n=netrc.netrc(args.netrc_file)
            (username,account,password)=n.authenticators(uri.hostname)
        # start fetching...
        import requests
        my_headers={
            "Content-Type": "text/xml",
            "Depth": "1",
        }
        my_data="<propfind xmlns='DAV:'><prop><address-data xmlns=\"urn:ietf:params:xml:ns:carddav\"/></prop></propfind>"
        for addressbook in args.carddav_addressbooks:
            url="{uri}/{addressbook}".format(uri=args.carddav_uri,addressbook=addressbook)
            r=requests.request('PROPFIND',url, 
                    headers=my_headers,
                    data=my_data,
                    auth=(username,password))
            parse_addressbook(addressbook, r.text, args)
    elif args.filename:
        addressbook_filename=args.filename
        addressbook_name=addressbook_filename.split('/')[-1].split('.')[0]
        with open(addressbook_filename, 'r') as f:
            parse_addressbook(addressbook_name, f.read(), args)


