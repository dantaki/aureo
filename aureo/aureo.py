#!/usr/bin/env python
from argparse import RawTextHelpFormatter
import argparse
import base64
import folium
from folium import IFrame
from folium.plugins import MarkerCluster
from glob import glob
import os
import random
import sys
#####################
__version__='0.0.1'
__usage__='''
       d888 8888     888 8888888b.  8888888888 .d88888b.  
      d8888 8888     888 888   Y88b 888       d88P" "Y88b 
     d88P88 8888     888 888    888 888       888     888 
    d88P 88 8888     888 888   d88P 8888888   888     888 
   d88P  88 8888     888 8888888P"  888       888     888 
  d88P   88 8888     888 888 T88b   888       888     888 
 d888888888 8Y88b. .d88P 888  T88b  888       Y88b. .d88P 
d88P     88  "Y88888P"   888   T88b 8888888888 "Y88888P"  
             
             numismatic database cartographer 
---------------------------------------------------------
Version:  {}
Author:   Danny Antaki <dantaki at ucsd dot com>
About:    map generator for coin collections
Usage:    aureo [-h] <-db database> <-loc locations> [options]

Required Arguments:
    -db     PATH      coin database file
    -loc    PATH      mint location file 

Options:
    -img    PATH      folder containing images
    -w      STR       weight unit [default: g] 
    -o      STR       output prefix [default: aureo]
    -h                print this message and exit

Notes:
    the database and location file must be tab delimited

    for an example of the database file, please refer to 
    coindb.txt on github: https://github.com/dantaki/aureo

    the location file must contain this header in this order:
    'Mint Latitude Longitude' with decimal coordinates

    images must be jpegs 800 x 800 pixels, 300 dpi
    filenames must be in this exact format: 
        ImagePrefix.[obv|rev].jpg

    the 'ImagePrefix' column in the database file must
    defined to include images in aureo maps

'''.format(__version__)

def exit(message=''):
	sys.stderr.write(message+__usage__+'\n')
	sys.exit(0)
#def rand_pos():
#	"""return a random float to jitter the markers"""
#	return (random.randint(1, 10))/100.
#def jitter(a):
#	return [ a[0]+rand_pos(), a[1]+rand_pos() ]
class Args(object):
	def __init__(self):
		parser = argparse.ArgumentParser(formatter_class=RawTextHelpFormatter, usage=__usage__, add_help=False)
		parser.add_argument('-db',type=str, required=True,default=None)
		parser.add_argument('-loc',type=str, required=True,default=None)
		parser.add_argument('-img',type=str,required=False,default=None)
		parser.add_argument('-w',type=str, required=False,default='g')
		parser.add_argument('-o',type=str, required=False,default='aureo')
		parser.add_argument('-h','-help',required=False,action="store_true", default=False)
		args = parser.parse_args()
	
		if args.h == True: exit()	
		args_dict = vars(args)
		for k in args_dict: setattr(self,k,args_dict[k])

class Aureo(object):
	def __init__(self,coindb=None):
		self.loc=None # [float(lat),float(lon)]
		self.obv=None # obverse image
		self.rev=None # reverse image
		self.popup_text=None #text on map marker popup
		self.iframe_size=500
		self.popup=None #popup object for a marker
	def update_loc(self,Loc=None):
		"""set the location for a coin"""
		if not hasattr(self, 'Mint'): exit('ERROR: check to see if database is missing Mint in the header\n\n')
		if Loc.get(self.Mint)==None: sys.stderr.write('WARNING: {} not in location file\n'.format(self.Mint))
		else: self.loc = Loc[self.Mint]

	def update_img(self,Img=None):
		""" update the images for a coin"""
		if not hasattr(self, 'ImagePrefix'): exit('ERROR: check to see if database is missing ImagePrefix in the header\n\n')
		sides = ['obv','rev']
		for s in sides:
			key = (self.ImagePrefix.replace(' ','').lower(),s)
			if Img.get(key)==None: 
				sys.stderr.write('WARNING: {} side not found for {}\nCheck the image filename if they are formatted correctly\n'.format(s,self.ImagePrefix))
			else: 
				# do this magic for placing jpgs in folium popups
				encoder = base64.b64encode(open(Img[key], 'rb').read()).decode() 
				_html = '<img src="data:image/jpeg;base64,{}" style="width:50%; height:50%;">'.format
				setattr(self,s,_html(encoder))
	
	def update_popup_text(self,Args):
		"""define the popup text"""
		# Aureo attributes to convert to popup text
		attr = [
			'Authority',('MinDate','MaxDate'),('Denomination','RIC'),('Mint','Region'),
			'Mintmark','Weight','Obverse','ObverseType','Reverse','ReverseType','Notes'
			]
		text=[]
		for i,e in enumerate(attr):
			t=[]
			if type(e)==str: e=[e]
			for a in e: 
				if not hasattr(self,a): continue
				pre,suf = '',''
				# make the first two lines bold, no prefix
				if i <2: pre,suf = '<strong>','</strong>'
				# add a prefix for other unpaired attributes
				elif len(e)==1: 
					pre = '<it>'+a.replace('Type',' Type')+':</it> '
				# add a horizontal line for obverse and reverse entries
				if a=='Obverse' or a=='Reverse': pre='<hr />'+pre
				if a=='ReverseType': suf=suf+'<hr />'
				# add the weight unit
				if a=='Weight': suf = Args.w+suf
				# add RIC in prefix
				if a=='RIC': pre=pre+'RIC '
				entry = getattr(self,a)
				# skip if entry is not defined
				if entry == 'None' or entry==None or entry=='' or entry=='NaN' or entry=='NA' or entry=='.': continue
				t.append(pre+getattr(self,a)+suf)
			token=', '
			if 'Date' in e[0]: token='-'
			if len(t)>0:
				text.append(token.join(t))
		self.popup_text='</br >'.join(text).replace('"','')

	def update_popup(self,):
		"""define the frame for the popup"""
		obv,rev='','' # images
		if self.obv!=None: obv=self.obv
		if self.rev!=None: rev=self.rev
		self.popup = IFrame(obv+rev+'<br />'+self.popup_text,width=self.iframe_size,height=self.iframe_size)

def load_db(coindb):
	"""
	return a list of Aureo objects.
	the Aureo object will cointain helper functions to 
	process images and text for the map
	"""
	Coins = []
	with open(coindb,'r') as f:
		header = f.readline().rstrip().split('\t')
		columns = dict(enumerate(header))
		for l in f:
			r = l.rstrip().split('\t')
			Coin = Aureo()
			for i,e in enumerate(r):
				setattr(Coin,columns[i],e)
			Coins.append(Coin)
	return Coins

def load_loc(loc):
	"""
	return a dict of mint -> [lat, lon]
	"""
	Loc = {}
	with open(loc,'r') as f:
		f.readline() #skip header
		for l in f: 
			mint, lat, lon = l.rstrip().split('\t')[0 : 3]
			Loc[mint]=[float(lat),float(lon)]
	return Loc

def load_img(img):
	"""
    returns a dict of [(imageprefix,obv/rev)] = path 
	"""
	imgs = {}
	if not img.endswith('/'): img=img+'/'
	for f in glob(img+"*.jpg"):
		pre = f.split('/')[-1].replace('.jpg','').split('.')
		side = pre.pop().lower()
		if side != 'obv' and side != 'rev': 
			sys.stderr.write('WARNING: {} side is ambiguous\nimage filenames must be formatted as ImagePrefix.rev.jpg or ImagePrefix.obv.jpg\n'.format(f))
			continue
		imageprefix= '.'.join(pre).lower()
		imgs[(imageprefix,side)]=f
	return imgs

def draw_map(lat=41.892929,lon=12.485366):
	"""define starting location
		here it is the Senate House of Rome
	"""
	Map = folium.Map(location=[lat,lon],zoom_start=4.25)
	folium.TileLayer('stamenwatercolor').add_to(Map)
	return Map

def color_map():
	"""icon color map for Roman coins"""
	colr = {}
	colr['denarius']='lightgray'
	colr['aureus']='orange'
	colr['solidus']='orange'
	colr['antoninianus']='gray'
	colr['ae']='darkred'
	return colr

def main():
	"""MAIN FUNCTION"""
	sys.setrecursionlimit(int(1e6))
	args = Args()
	Coins = load_db(args.db)
	Loc = load_loc(args.loc)
	Img = None
	if args.img !=None: Img = load_img(args.img)
	cm=color_map()
	Map = draw_map()
	Markers = [] 
	for Coin in Coins:
		# update coin location
		Coin.update_loc(Loc)
		# add popup text
		Coin.update_popup_text(args)
		# add images if given
		if Img != None:
			Coin.update_img(Img)
		# update popup
		Coin.update_popup()
		# load up markers
		# skip if there is no location
		if Coin.loc==None:continue
		tooltip=''
		if hasattr(Coin,'Denomination'): tooltip=getattr(Coin,'Denomination')
		colr='black'
		if cm.get(tooltip.lower())!=None: colr=cm[tooltip.lower()]
		# color the coins prefixed with AE the same
		if tooltip.lower().startswith('ae'): colr=cm['ae']
		mindate,maxdate=None,None
		if hasattr(Coin,'MinDate'): mindate=getattr(Coin,'MinDate')
		if hasattr(Coin,'MaxDate'): maxdate=getattr(Coin,'MaxDate')
		if mindate==maxdate and maxdate!=None: tooltip=maxdate+' '+tooltip
		if mindate!=maxdate and maxdate!=None and mindate!=None: tooltip=mindate+'-'+maxdate+' '+tooltip
		if hasattr(Coin,'Authority'): tooltip=getattr(Coin,'Authority')+' '+tooltip
		Markers.append(
			folium.Marker(
			#jitter(Coin.loc), # geographic location
			Coin.loc, # geographic location, no jitter
			popup=folium.Popup(Coin.popup),
			tooltip=tooltip,
			icon=folium.Icon(icon='glyphicon-usd',color=colr,),
			)
		)
	# make marker cluster
	Mc = MarkerCluster().add_to(Map)
	#add markers to map and save
	for M in Markers: M.add_to(Mc)
	Mc.add_to(Map)
	Map.save('{}.html'.format(args.o))
	sys.stdout.write('\n'+'-'*45+'\n  output  --->  {}.html'.format(args.o)+'\n\nopen in a web browser and enjoy aureo!\n'+'-'*45+'\n')

if __name__=='__main__': main()