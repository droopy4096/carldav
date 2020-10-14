#!/bin/env python

from xml.etree.ElementTree import ElementTree

import sys
import json
import os.path
import os
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Extract VCARD from CardDav Export')
    parser.add_argument('filename', 
                    help='XML file with addressbook entries exported via CardDav')
    parser.add_argument('--no-individual', dest='individual', action="store_false")
    parser.add_argument('--write-individual', dest='individual', action="store_true", default=True)
    parser.add_argument('--no-full', dest='full', action="store_false")
    parser.add_argument('--write-full', dest='full', action="store_true", default=False)

    parser.add_argument('--vcard-dir', default='./vcard')

    args = parser.parse_args()

    addressbook_filename=args.filename

    mydoc = ElementTree(file=addressbook_filename)
    addressbook_name=addressbook_filename.split('/')[-1].split('.')[0]
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

        

