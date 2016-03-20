#!/usr/bin/env python

import re

from os import environ
from evernote.api.client import EvernoteClient
from evernote.edam.notestore import NoteStore

TOKEN = environ.get("EVERNOTE_TOKEN")
NOTE_BOOK = environ.get("EVERNOTE_NOTE_BOOK")

def process_notes():
    client = EvernoteClient(token=TOKEN, sandbox=False)
    note_store = client.get_note_store()

    filter = NoteStore.NoteFilter()
    filter.notebookGuid = NOTE_BOOK

    note_list = note_store.findNotes(TOKEN, filter, 0, 100)

    for note in note_list.notes:
        content = note_store.getNoteContent(TOKEN, note.guid)
        find_labels(content)


def find_labels(content):
    pattern = re.compile("\[(.+?)\](.*?)\[\/(.+?)]")
    iterator = pattern.finditer(content)
    for m in iterator:
        process_label(m.group(1), m.group(2))

def process_label(label, content):
    print label
    print clean_content(content)

def clean_content(content):
    content = content.replace("<br clear=\"none\"/>","\n")
    content = content.replace("<div>","")
    content = content.replace("</div>","")
    return content


if __name__ == "__main__":
    process_notes()

