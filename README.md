# Purpose

Set of tools to export .ics/.vcs files from existing CalDAV/CardDAV server.

use `--help` option to learn more about all available options. 

# Sample use

## Fetch and extract .ics/.vcs files

```shell
python extract_ical.py \
    --netrc-file=netrc \
    --caldav-uri=https://owncloud.myhost.net/remote.php/dav/calendars/droopy \
    --caldav-calendar=personal \
    --caldav-calendar=other-shared-cal
```

```shell
python extract_vcard.py \
    --carddav-uri https://owncloud.myhost.net/remote.php/dav/addressbooks/users/droopy \
    --carddav-addressbook=family-contacts \
    --carddav-addressbook=contacts \
    --netrc-file=netrc 
```

## extract .ics/.vcs from pre-fetched XML

```shell
python extract_ical.py \
    --filename=personal.xml
```

```shell
python extract_vcard.py \
    --filename=contacts.xml
```
