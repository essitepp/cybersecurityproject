from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt

import sqlite3

from .models import Note

@login_required
def index(request):
  notes = Note.objects.filter(owner = request.user)
  context = { 'user': request.user, 'notes': notes }
  return render(request, 'notes/index.html', context)


@login_required
def add_note(request):
  if request.method == 'POST':
    title = request.POST.get('note_title')
    text = request.POST.get('note_text')
    query = "INSERT INTO notes_note (owner_id, note_title, note_text) VALUES (%s, '%s', '%s')" % ( request.user.id, title, text)

    conn = sqlite3.connect('db.sqlite3')
    c = conn.cursor()
    c.execute(query)
    conn.commit()
    conn.close()

  return redirect('/')


#sql injection fixed
@login_required
def add_note_2(request):
  if request.method == 'POST':
    title = request.POST.get('note_title')
    text = request.POST.get('note_text')
    note = Note.objects.create(note_title=title, note_text=text, owner=request.user)

  return redirect('/')


@csrf_exempt
def delete_note(request, note_id):
  if request.method == 'POST':
    note = Note.objects.get(pk=note_id)
    note.delete()
  return redirect('/')


#access control and authentication fixed
@login_required
def delete_note_2(request, note_id):
  if request.method == 'POST':
    note = Note.objects.get(pk=note_id)
    if note.owner == request.user:
      note.delete()
  return redirect('/')