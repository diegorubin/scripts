#!/usr/bin/env python

import re
import dbus

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
    content = clean_content(content)

    task_list = re.match("task:(.+)", label)
    if task_list:
        process_task(task_list.group(1), content)

def clean_content(content):
    content = content.replace("<br clear=\"none\"/>","\n")
    content = content.replace("<div>","")
    content = content.replace("</div>","")
    return content

def process_task(task_list, content):
    remote_object = connect_to_gnomato()
    description = "[Desenvolvimento] - %s" % content
    dbus_interface = "com.diegorubin.Gnomato"

    if remote_object:
        exists = remote_object.TaskExists(task_list, description,
            dbus_interface = dbus_interface)
        if exists == "false":
            remote_object.CreateTask(task_list, description,
                dbus_interface = dbus_interface)

def connect_to_gnomato():
    bus = dbus.SessionBus()
    try:
        remote_object = bus.get_object("com.diegorubin.Gnomato",
                                   "/com/diegorubin/Gnomato")
        return remote_object
    except:
        return None

if __name__ == "__main__":
    process_notes()

