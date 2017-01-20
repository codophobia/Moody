from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.conf import settings
from models import Song,Playlist
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.core import serializers
import json
import cv2
from music.forms import DocumentForm
from django.core.files.storage import FileSystemStorage
from sklearn.svm import SVC
from sklearn.externals import joblib
import dlib
import os
import math
import numpy as np 
from PIL import Image


@csrf_exempt
def upload(request):
	if request.method == 'POST' and request.FILES['picture']:
		myfile = request.FILES['picture']
		fs = FileSystemStorage()
		filename = fs.save(myfile.name, myfile)
		uploaded_file_url = fs.url(filename)
		f = uploaded_file_url.split('/')
		fname = f[2]
		s = Song()
		s.song_title = filename
		s.file = fname
		s.save()
		return redirect('home')
def home(request):
	song = Song.objects.all()
	context = {"songs":song} 
	return render(request,'music/base.html',context)

@csrf_exempt
def playlist(request):
	playlists = Playlist.objects.all()
	data = serializers.serialize('json', playlists)
	return HttpResponse(data, content_type="application/json")
	
@csrf_exempt
def songs(request):
	song = Song.objects.all()
	data = serializers.serialize('json', song)
	return HttpResponse(data, content_type="application/json")

@csrf_exempt
def next(request):
	if request.method == 'POST':
		isplay = int(request.POST['isplay'])
		currsong = request.POST['currsong']
		if(isplay == 0):
			next_song = Song.objects.all().filter(song_title__gt = currsong)[:1]
			if not next_song:
				next_song = Song.objects.all()[:1]
		else:
			pname = request.POST['pname']
			p = Playlist.objects.get(name=pname)
			next_song = p.songs.all().filter(song_title__gt = currsong)[:1]
			if not next_song:
				p = Playlist.objects.get(name=pname)
				next_song = p.songs.all()[:1]
		data = serializers.serialize('json', next_song)
		return HttpResponse(data, content_type="application/json")

@csrf_exempt
def prev(request):
	if request.method == 'POST':
		isplay = int(request.POST['isplay'])
		currsong = request.POST['currsong']
		if(isplay == 0):
			next_song = Song.objects.all().filter(song_title__lt = currsong).last()
		else:
			pname = request.POST['pname']
			p = Playlist.objects.get(name=pname)
			next_song = p.songs.all().filter(song_title__lt = currsong).last()
		data = serializers.serialize('json', [next_song])
		return HttpResponse(data, content_type="application/json")
@csrf_exempt
def psongs(request):
	if request.method == 'POST':
		name = (request.POST['name'])
		p = Playlist.objects.get(name=name)
		songs = p.songs.all()
		data = serializers.serialize('json', songs)
		return HttpResponse(data, content_type="application/json")

@csrf_exempt
def createplaylist(request):
	if request.method == 'POST':
		name = (request.POST['name'])
		p = Playlist()
		p.name = name
		p.save()
		return HttpResponse("success")

@csrf_exempt
def deletesong(request):
	if request.method == 'POST':
		song = (request.POST['song'])
		Song.objects.filter(song_title = song).delete()
		return HttpResponse("success")

@csrf_exempt
def deleteplaylistsong(request):
	if request.method == 'POST':
		song = (request.POST['song'])
		playlist = request.POST['playlist']
		s = Song.objects.get(song_title=song)
		p = Playlist.objects.get(name=playlist)
		p.songs.remove(s)
		return HttpResponse("success")

@csrf_exempt
def addplaylistsongs(request):
	if request.method == 'POST':
		name = (request.POST['name'])
		songs = Song.objects.all()
		data = serializers.serialize('json', songs)
		return HttpResponse(data, content_type="application/json")

@csrf_exempt
def deleteplaylist(request):
	if request.method == 'POST':
		song = (request.POST['playlist'])
		Playlist.objects.filter(name=song).delete()
		return HttpResponse("success")
@csrf_exempt
def addtoplaylist(request):
	if request.method == 'POST':
		name = request.POST['name']
		songs = request.POST.getlist('songs[]')
		p = Playlist.objects.get(name=name)
		for s in songs:
			s = Song.objects.get(song_title = s)
			p.songs.add(s)
		return HttpResponse("success")


