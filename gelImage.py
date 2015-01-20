#!/usr/bin/python

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Copyright (C) 2015 Paul Saary
#


import wx
import wx.lib.wxcairo
import cairo

import os.path

# new image:
# to load images:
from PIL import Image
import PIL.ImageOps 
import numpy

import math


labelList = {
				"abc": ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z'],
				"ABC": ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
				
			}


class DrawingArea(wx.Panel):
	'''Class to provide the drawing, not really a good idea I guess.
		maybe a single class would be enough'''
	def __init__ (self ,parent, title, infos, ladders ):
		super(DrawingArea , self).__init__ (parent=parent,id=wx.ID_ANY)
		self.infos 		= infos
		self.ladders 	= ladders
		
		# some variables
		self.leftclicks = []
		self.dragging 	= [False,False]
		
		
		self.imagePos 	= (0,0)
		self.imagePath 	= False
		self.imageCrop	= False		# if image should be croped
		self.imageExport= [False,False]
		self.drawExport = False
		self.ImageClick = False
				
		self.drawnLadders	= []
		self.tempLadder 	= False
		self.ladderFontSize = int(self.infos['fontsize'])  #px
		
		self.laneMarkers 	= []
		
		

		
		self.objPath    = {}
		
		#self.SetDoubleBuffered(True)
		self.Bind(wx.EVT_PAINT, self.OnPaint)
		
		self.Bind(wx.EVT_LEFT_UP, self.OnLeftUp)
		self.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)
		self.Bind(wx.EVT_MOTION, self.OnMotion)
		
	def updateGUI(self, infos=False):

		# update infos
		if infos != False:
			self.infos = infos
			
		# update some var
		self.ladderFontSize = int(self.infos['fontsize'])  #px
		
		self.OnPaint("non")
	
	
	def returnInfo(self):
		return self.infos

	def OnPaint(self, e):

		
		dc = wx.PaintDC(self)
		dc.SetBackground(wx.Brush("White"))
		dc.Clear() 
		self.cr = wx.lib.wxcairo.ContextFromDC(dc)
		
		width, height = self.GetVirtualSize()	# set hight and width. Its 100, 100 
		ratio = float(height)/float(width)
		

		
		if width != 0 and height != 0 and height > 100 and width > 100:
			#self.cr.scale(width*ratio,height)
			#self.cr.scale(0.001, 0.001) 			# make it 1000*ratiox1000
			self.cr.translate (width/2,height/2)
		
			self.DoDrawing() 
		
		self.dc = dc
	
	def OnLeftDown(self,e):
		
		x, y = self.ScreenToClient(wx.GetMousePosition())
		x2, y2 = self.cr.device_to_user(x,y)
		self.dragging[0] = (x2,y2)
		self.dragging[1] = (x2,y2)
		
		#self.leftclicks.append[(x,y)]
		
		
		
		# check if the click is on the image:
		if self.imagePath != False:
			self.ImageClick = False
			self.cr.append_path(self.imagePath) 
			inFill = self.cr.in_fill(x2,y2) 
			inStroke = self.cr.in_stroke(x2,y2)

			# check if mouse hit a path:
			if inFill == True or inStroke == True:
				self.ImageClick  = True
		#self.cr.fill()
		
		if self.infos["currentAction"] == "SelectExport":
			self.drawExport = True
			
		
		
	
	def OnLeftUp(self,event):
		x, y = self.ScreenToClient(wx.GetMousePosition())
		x2, y2 = self.cr.device_to_user(x,y)
		
		self.tempLadder = False
		
		# if draw lader lines:
		if self.infos["currentAction"] == "drawLadderLines":
			self.drawnLadders[len(self.drawnLadders)-1][3].append((x2,y2))
			

		
		# now allow drawing lines
		if self.infos["currentAction"]=="addLadder":
			self.infos["currentAction"] = "drawLadderLines"
		
		if self.infos["currentAction"] == "SelectExport":
			# reset, save, reset another
			self.drawExport = False
			self.saveFile()
			self.infos["currentAction"] = False
	
		if self.infos["currentAction"] == 'LabelLanes':
			self.laneMarkers.append((x2,y2))
		
		self.updateGUI()
		
		
		
		
		return True   
	
	def OnMotion(self, event): 
		
		# dragg and drop:
		if event.Dragging() and event.LeftIsDown():
			
			# previous x2, y2:
			x2Prev, y2Prev = self.dragging[1]
			x, y = self.ScreenToClient(wx.GetMousePosition())
			x2, y2 = self.cr.device_to_user(x,y)
			self.dragging[1] = (x2,y2)
			
			if self.infos["currentAction"]=="addLadder":
				
				# remove the last item, as this is the temp ladder
				if self.tempLadder != False:
					self.drawnLadders.pop()
				
				# make a list for ladder handling
				selLadder = self.infos["ladder"]
				self.tempLadder = [selLadder,self.dragging[0],self.dragging[1],[]]
				self.drawnLadders.append(self.tempLadder)
				
			
			elif self.ImageClick == True and self.infos["currentAction"] == "MoveImage":	
				# current position:
				cx, cy = self.imagePos
				
				newX = cx + x2-x2Prev
				newY = cy + y2-y2Prev
				
				self.imagePos = (newX, newY)
			
			elif self.infos["currentAction"] == "RotateImage":	
				# current position:
				self.infos["rotate"] = 0.01 * (self.dragging[0][0] - self.dragging[1][0])
			
			elif self.infos["currentAction"] == "CropImage":
				self.imageCrop=[False,False]
				self.imageCrop[0] = self.dragging[0]
				self.imageCrop[1] = (x2,y2)
				
			elif self.infos["currentAction"]== "SelectExport":
				# select area to export:
				self.imageExport=[False,False]
				self.imageExport[0] = self.dragging[0]
				self.imageExport[1] = (x2,y2)
				
			else:
				print "nothing to do"
				
			self.updateGUI()
		


	
	def hitTest(self):
		
		hit = None
		x, y = self.ScreenToClient(wx.GetMousePosition())	
		
		# get the mouse positions
		x2, y2 = self.cr.device_to_user(x,y)
		
		for item in self.objPath:
			path = self.objPath[item]
			self.cr.append_path(path)
			inFill = self.cr.in_fill(x2,y2) 
			inStroke = self.cr.in_stroke(x2,y2)
			
			# check if mouse hit a path:
			if inFill == True or inStroke == True:
				hit = path
			self.cr.fill()
		
		return hit
		
	
	def DoDrawing(self):
		# first the image, as background
		self.openFile()
		
		# crop:
		self.drawCrop()
		
		# ladder
		self.drawLadder()
		
		# draw labels?
		if len(self.laneMarkers) > 0:
			self.drawLabels()
		# draw export?
		self.selectExportRange()
		
		
		'''
		self.cr.set_source_rgb (0.2 , 0.23 , 0.9)
		self.cr.rectangle(10 , 15, 90, 60)
		self.cr.fill()

		self.cr.set_source_rgb(0.9 , 0.1 , 0.1)
		self.cr.rectangle(130 , 15, 90, 60)
		self.cr.fill()'''
		
		

		
	def openFile(self):
		if self.infos["file"] != False:
			

			
			# rectangle for the image
			posx, posy = self.imagePos
			posx = posx - self.infos["imageWidth"]/2
			posy = posy - self.infos["imageHight"]/2
			
			posxB = posx + self.infos["imageWidth"]/2
			posyB = posy + self.infos["imageHight"]/2
			
			
			#self.cr.translate(posxB,posyB)
			
			# rotate canvas?
			self.cr.rotate(self.infos["rotate"])
			
			self.cr.rectangle(posx, posy,self.infos["imageWidth"],self.infos["imageHight"])
			# copy path
			self.imagePath = self.cr.copy_path()
			#self.cr.clip()
			#self.cr.new_path()
			
			# make the image
			imageSurface = cairo.ImageSurface(cairo.FORMAT_A1, 800,800)
			image = imageSurface.create_for_data(self.infos["imageData"], cairo.FORMAT_RGB24, self.infos["imageWidth"], self.infos["imageHight"])

			self.cr.set_source_surface(image,posx,posy)
			
			# paint the image
			self.cr.paint()
			self.cr.stroke()
			
			# rotate back!
			self.cr.rotate(-self.infos["rotate"])
			#self.cr.translate(0,0)

			#imageSurface.destroy()


	# Ladders
	def drawLadder(self):
		
		unit = self.infos["unit"]


		for ladder in self.drawnLadders:
			name 	= ladder[0]
			start 	= ladder[1]
			stop  	= ladder[2]
			
			# where are the fragments on the gel?
			positions = ladder[3]
			ypositions = []
			xpositions = []
			for i in positions:
				xpositions.append(i[0])
				ypositions.append(i[1])
				
			# get middle x range for lines:
			if len(positions) > 0:
				averageX = sum(xpositions)/len(xpositions)
			else:
				averageX = 0
			
			# fragments of ladder
			fragments = self.ladders[name]
			lines = sorted(fragments, reverse=True)	# sort the ladder
		
			
		
			# get the largest and smalles dna fragment
			small  = lines[len(lines)-1]
			large = lines[0]
		
			# we need m and n of the linear function y = m*log(x)+n

			m = (stop[1] - start[1])/(math.log10(small)-math.log10(large))
			n = start[1] - m * math.log10(large)
			

			i = 0
			for l in lines:
			
				# if kilo add a point:
				if unit[:1] == "k":
					num = str(round(float(l)/float(1000),2))
					parts = num.split(".")
					number = "%s.%s" % (parts[0],parts[1])
				else:
					number = str(l)
				text = "%s %s" % (number, unit)
				
				position = m * math.log10(l) + n							# position of the line
				
				# only draw if we did not yet specify the bands
				# or if there is one by click!
				if len(ypositions) == 0 or i < len(ypositions):
					
					
					self.cr.select_font_face('Arial', cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
					self.cr.set_font_size(self.ladderFontSize ); #px
					self.cr.set_source_rgb (0,0,0)
					xbearing, ybearing, TextWidth, TextHeight, xadvance, yadvance = self.cr.text_extents(text)
					
					
					# check if ladder is to be drawn right or left:
					if averageX >= start[0]:
						# it is left of the image:
						ladderSite=True
					
						self.cr.move_to(start[0]-TextWidth,position); 
					else:
						self.cr.move_to(start[0],position); 
						ladderSite=False
					
					self.cr.show_text(text)
				
					if i <= len(ypositions) and len(ypositions) > 0:
						# also draw the line for this fragment
						self.cr.set_source_rgb(0,0,0) # Solid color
						self.cr.set_line_width(1) # or 0.1
						if ladderSite:
							self.cr.move_to(start[0]+3,position-self.ladderFontSize/2)
							self.cr.line_to(start[0]+7,position-self.ladderFontSize/2)
							self.cr.line_to(averageX-8,ypositions[i])						
							self.cr.line_to(averageX,ypositions[i])
						else:
							self.cr.move_to(start[0]-3,position-self.ladderFontSize/2)
							self.cr.line_to(start[0]-7,position-self.ladderFontSize/2)
							self.cr.line_to(averageX+8,ypositions[i])						
							self.cr.line_to(averageX,ypositions[i])
						self.cr.stroke()
				
				i = i+1


		return True
	
	def drawCrop(self):

		# depending on the values we draw 4 white boxes:
		# upper white box
		if self.imageCrop != False:
			
			posX1 = self.imageCrop[0][0]
			posY1 = self.imageCrop[0][1]
			
			posX2 = self.imageCrop[1][0]
			posY2 = self.imageCrop[1][1]
			width, height = self.GetVirtualSize()	# set hight and width. Its 100, 100 
			
			
			
			self.cr.set_source_rgba(1,1,1,1) # Solid color
			self.cr.set_line_width(0) # or 0.1
			
			# left white box
			self.cr.rectangle(-width/2, -height/2, width/2+posX1,height)
			self.cr.fill()
			
			# right box
			self.cr.rectangle(posX2, -height/2, width/2-posX2,height)
			self.cr.fill()
		
			# upper box:
			self.cr.rectangle(-width/2, -height/2, width,height/2+posY1)
			self.cr.fill()
			
			#lower
			self.cr.rectangle(-width/2, posY2,  width,height/2-posY2)
			self.cr.fill()
		
		return True
			

	def drawLabels(self):
		sumx =0 
		sumy =0
		for xy in self.laneMarkers:
			sumx = sumx+xy[0]
			sumy = sumy+xy[1]
		
		averageX = float(sumx)/len(self.laneMarkers)
		averageY = float(sumy)/len(self.laneMarkers)
		
		markertype = self.infos['marks']
		if markertype == "ABC" or markertype == "abc":
			markerLst = labelList[markertype]
		else:
			# normal numbers
			markerLst = range(1,len(self.laneMarkers)+1)
		
		i = 0
		for pos in self.laneMarkers:

			if i >= len(markerLst):
				newI = i-(len(markerLst))
				A = markerLst[newI]
				text = "%s.%d" % (A, newI+1)
			else: 
				text = markerLst[i]
			# make str
			text = str(text)
			
			self.cr.select_font_face('Arial', cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
			self.cr.set_font_size(self.ladderFontSize ); #px
			self.cr.set_source_rgb (0,0,0)
			xbearing, ybearing, TextWidth, TextHeight, xadvance, yadvance = self.cr.text_extents(text)
			
			self.cr.move_to(pos[0]-TextWidth/2, averageY)
			self.cr.show_text(text)
			
			i = i + 1
				
			
		
	
	def selectExportRange(self):
		''' drag and drop to select range for export'''
		if self.drawExport:
			x = self.imageExport[0][0]
			y = self.imageExport[0][1]
			width = self.imageExport[1][0]-x
			height= self.imageExport[1][1]-y
			
			self.cr.set_source_rgba(0,0,0,0.8) # Solid color
			self.cr.set_line_width(1) # or 0.1
			self.cr.rectangle(x,y,width, height)
			self.cr.stroke()
		return True
	
	def saveFile(self):
		
		# show dialog
		saveFileDialog = wx.FileDialog(self, "Save your image file", "", self.infos["path"],
				                       "Image files (*.png)|*.png;", wx.FD_SAVE )
		# check if file was opened
		if saveFileDialog.ShowModal() == wx.ID_CANCEL:
			return     # the user changed idea...

		# proceed loading the file chosen by the user
		# this can be done with e.g. wxPython input streams:
		self.infos["fileExport"] = (saveFileDialog.GetPath())
		# add .png
		if self.infos["fileExport"][-4:] != ".png" and self.infos["fileExport"][-4:] != ".PNG":
			self.infos["fileExport"] = "%s%s" %(self.infos["fileExport"],".png")
		
		self.saveSnapshot()
		
	
	def saveSnapshot(self):
		dcSource = self.dc
		# based largely on code posted to wxpython-users by Andrea Gavana 2006-11-08
		if self.imageExport == False:
			#no crop:
			size = dcSource.Size
			width = size.width
			height = size.height
			offx=0
			offy=0
		else:
			#size should be calculatet here!
			size = dcSource.Size
			x = self.imageExport[0][0]
			y = self.imageExport[0][1]
			
			x2 = self.imageExport[1][0]
			y2 = self.imageExport[1][1]
			
			offx, offy	= self.cr.user_to_device(x,y)
			 
			width 	= x2-x
			height 	= y2-y
				

		# Create a Bitmap that will later on hold the screenshot image
		# Note that the Bitmap must have a size big enough to hold the screenshot
		# -1 means using the current default colour depth
		bmp = wx.EmptyBitmap(width, height)

		# Create a memory DC that will be used for actually taking the screenshot
		memDC = wx.MemoryDC()

		# Tell the memory DC to use our Bitmap
		# all drawing action on the memory DC will go to the Bitmap now
		memDC.SelectObject(bmp)

		# Blit (in this case copy) the actual screen on the memory DC
		# and thus the Bitmap
		memDC.Blit( 0, # Copy to this X coordinate
			0, # Copy to this Y coordinate
			width, # Copy this width
			height, # Copy this height
			dcSource, # From where do we copy?
			offx, # What's the X offset in the original DC?
			offy  # What's the Y offset in the original DC?
			)

		# Select the Bitmap out of the memory DC by selecting a new
		# uninitialized Bitmap
		memDC.SelectObject(wx.NullBitmap)

		img = bmp.ConvertToImage()
		img.SaveFile(self.infos["fileExport"], wx.BITMAP_TYPE_PNG)


		# reset variable
		self.imageExport = False
	
	# to remove ladders if wished
	def removeLadders(self):
		self.drawnLadders = []
		self.infos["currentAction"] = False
		return True
	
	def remLabels(self):
		self.laneMarkers = []
		self.infos["currentAction"] = False
		return True












class gelImage(wx.Frame):

	def __init__(self, *args, **kwargs):
		super(gelImage, self).__init__(*args, **kwargs) 
		
		# INFOS, is the state of out little programm
		self.infos = {	"file": False, 
						"path": "/", 
						"ladder": False, 
						"currentAction": None, 
						"rotate": 0,
						"marks":"ABC",
						"fontsize": 11}
		
		self.StartInfos = self.infos
		
		# some ladders, feel free to add some
		self.ladders = {"Eurogentec smartLadder":[10000,8000,6000,5000,4000,3000,2500,2000,1500,1000,800,600],
						"NEB 1 kb DNA Ladder":[10000,8000,6000,5000,4000,3000,2000,1500,1000,500],
						"NEB Low Molecular Weight DNA Ladder":[766,500,350,300,250,200,150,100,75,50,25],
						"Thermo Scientific GeneRuler DNA Ladder Mix": [10000,8000,6000,5000,4000,3500,3000,2500,2000,1500,1200,1000,900,800,700,600,500,400,300,200,100],
						"Thermo Scientific GeneRuler 100 bp DNA Ladder ": [1000,900,800,700,600,500,400,300,200,100]}
						
		self.units = ["bp","kbp","Da","kDa","u","ku"]

		self.InitUI()
		
	def updateGUI(self):
		# update infos if changed
		self.infos = self.cairo.returnInfo()
		self.cairo.updateGUI(self.infos)

	def InitUI(self):
		#----------------------------------------------------
		# Build menu bar and submenus   

		menubar = wx.MenuBar()
		# file menu containing quit menu item
		fileMenu = wx.Menu() 

		
		#fileMenu = wx.Menu() 
		open_file = wx.MenuItem(fileMenu, 1, 'Open Image\tCTRL+O')
		fileMenu.AppendItem(open_file)
		self.Bind(wx.EVT_MENU, self.OnOpen, open_file)
		
		save_file = wx.MenuItem(fileMenu, wx.ID_ANY, 'Save Image\tCTRL+S')
		fileMenu.AppendItem(save_file)
		self.Bind(wx.EVT_MENU, self.OnSave, save_file)
		
		save_file = wx.MenuItem(fileMenu, wx.ID_ANY, 'Export selection Image\tCTRL+SHIFT+S')
		fileMenu.AppendItem(save_file)
		self.Bind(wx.EVT_MENU, self.selectExport, save_file)
		
		#quit_item = wx.MenuItem(fileMenu, wx.ID_EXIT, 'Quit\tCtrl+W')
		#fileMenu.AppendItem(quit_item)
		#self.Bind(wx.EVT_MENU, self.OnQuit, quit_item)
		
		menubar.Append(fileMenu, '&File')  
		
		
		# edit menu
		editMenu = wx.Menu()
		
		action = wx.MenuItem(editMenu, wx.ID_ANY, 'Put Ladder\tCTRL+L')
		editMenu.AppendItem(action)
		self.Bind(wx.EVT_MENU, self.PutLadder, action)
		
		action = wx.MenuItem(editMenu, wx.ID_ANY, 'Move Image\tCTRL+M')
		editMenu.AppendItem(action)
		self.Bind(wx.EVT_MENU, self.MoveImage, action)
		
		action = wx.MenuItem(editMenu, wx.ID_ANY, 'Invert Image\tCTRL+I')
		editMenu.AppendItem(action)
		self.Bind(wx.EVT_MENU, self.invertImage, action)
		
		
		action = wx.MenuItem(editMenu, wx.ID_ANY, 'Rotate Image\tCTRL+R')
		editMenu.AppendItem(action)
		self.Bind(wx.EVT_MENU, self.rotateImage, action)
		
		action = wx.MenuItem(editMenu, wx.ID_ANY, 'Crop Image\tCTRL+K')
		editMenu.AppendItem(action)
		self.Bind(wx.EVT_MENU, self.crop, action)
		
		action = wx.MenuItem(editMenu, wx.ID_ANY, 'Label lanes\tCTRL+J')
		editMenu.AppendItem(action)
		self.Bind(wx.EVT_MENU, self.labelLanes, action)
		
		menubar.Append(editMenu, 'Edit') 
		    

		# help menu containing about menu item
		helpMenu = wx.Menu() 
		about_item = wx.MenuItem(helpMenu, wx.ID_ABOUT, '&About\tCtrl+A')
		helpMenu.AppendItem(about_item)
		#~ self.Bind(wx.EVT_MENU, self.OnAboutBox, about_item)
		menubar.Append(helpMenu, '&Help')     

		self.SetMenuBar(menubar)

		#----------------------------------------------------
		# Build window layout

		panel = wx.Panel(self)        
		vbox = wx.BoxSizer(wx.HORIZONTAL)
		
		sizer_v = wx.BoxSizer(wx.HORIZONTAL)
		

		control = wx.Panel(panel)
		hbox2 = wx.BoxSizer(wx.VERTICAL)

		# add controls:#		
		font      = wx.Font(9, wx.DEFAULT, wx.NORMAL, wx.BOLD)			
		
		# text ladder:
		self.txtLadder        = wx.StaticText(control, -1, 'select ladder:')
		self.txtLadder.SetFont(font)
		
		
		self.laddersSel = []
		for l in self.ladders:
			self.laddersSel.append(l)
		
		self.LadderSelect = wx.ComboBox(control,size=wx.DefaultSize,	choices=self.laddersSel)
		self.LadderSelect.Bind(wx.EVT_COMBOBOX, self.onLadSelect)
		self.LadderSelect.SetStringSelection(self.laddersSel[0])
		self.infos["ladder"] = self.laddersSel[0]
		

		
		
		# unit:
		self.txtUnit        = wx.StaticText(control, -1, 'select unit:')
		self.txtUnit.SetFont(font)
		self.unitSelect = wx.ComboBox(control,size=wx.DefaultSize,	choices=self.units)
		self.unitSelect.Bind(wx.EVT_COMBOBOX, self.onUnitSelect)
		self.unitSelect.SetStringSelection(self.units[0])
		self.infos["unit"] = self.unitSelect.GetStringSelection()
		
		self.removeLadders      = wx.Button(control,-1, "remove Ladders")		# add enzyme
		self.removeLadders.Bind(wx.EVT_BUTTON, self.remLadder)
		
		
		# label type:
		self.txtLabel        = wx.StaticText(control, -1, 'select label:')
		self.txtLabel.SetFont(font)
		self.labelSelect = wx.ComboBox(control,size=wx.DefaultSize,	choices=["ABC","abc","123"])
		self.labelSelect.Bind(wx.EVT_COMBOBOX, self.onLabelSelect)
		self.labelSelect.SetStringSelection("ABC")
		self.infos["marks"] = self.labelSelect.GetStringSelection()
		
		self.removeLabels      = wx.Button(control,-1, "remove Labels")		# add enzyme
		self.removeLabels.Bind(wx.EVT_BUTTON, self.remLabels)
		
		
		# font size
		fontsitzes = map(str,  range(6,40))
		self.txtFontsize        = wx.StaticText(control, -1, 'font size:')
		self.txtFontsize.SetFont(font)
		self.labelFontsize = wx.ComboBox(control,size=wx.DefaultSize,	choices=fontsitzes)
		self.labelFontsize.Bind(wx.EVT_COMBOBOX, self.onFontsizeSelect)
		self.labelFontsize.SetStringSelection(str(self.infos["fontsize"]))

		
		
		# color:
		#self.txtcolorFront        = wx.StaticText(control, -1, 'font color:')
		#self.txtcolorFront.SetFont(font)
		#self.colorFront 	= wx.TextCtrl(control, -1, size=(180,-1),style=wx.TE_PROCESS_ENTER)
		
		### add elements to control pannel
		
		# fontsize:
		hbox2.Add(self.txtFontsize)
		hbox2.Add(self.labelFontsize)
		
		
		# ladder
		hbox2.Add(self.txtLadder)
		hbox2.Add(self.LadderSelect)
		
		#unit
		hbox2.Add(self.txtUnit)
		hbox2.Add(self.unitSelect)
		
		hbox2.Add(self.removeLadders)
		
		# labels
		hbox2.Add(self.txtLabel)
		hbox2.Add(self.labelSelect)
		hbox2.Add(self.removeLabels)
		
		# color font
		#hbox2.Add(self.txtcolorFront)
		#hbox2.Add(self.colorFront)
		
		self.cairo = DrawingArea(panel, "drawing pannel", self.infos,self.ladders )
		
		
		control.SetSizer(hbox2)
		
		
		
		gridsizer = wx.FlexGridSizer(rows=1, cols=2, vgap=3, hgap=10)
		#gridsizer.AddGrowableCol(0)					# make cols growable
		gridsizer.AddGrowableCol(1)
		gridsizer.AddGrowableRow(0)
		
		gridsizer.Add(control,0, wx.EXPAND | wx.ALL, 0)
		gridsizer.Add(self.cairo, 0, wx.EXPAND | wx.ALL, 0)
		
		vbox.Add(gridsizer, 1, wx.EXPAND|wx.ALL, 15)
		
	
		panel.SetSizer(vbox) 
		self.Maximize()
		self.SetTitle('gelImage')
		self.Centre()

	def OnQuit(self, e):
		self.Close()
		
	def OnOpen(self, e):
		# reset settings:
		self.infos = self.StartInfos
		
		# show dialog
		openFileDialog = wx.FileDialog(self, "Open image file", "", "",
				                       "Image files (*.png, *.TIF)|*.png;*.PNG;*.tif;*.TIF", wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
		
		# check if file was opened
		if openFileDialog.ShowModal() == wx.ID_CANCEL:
			return     # the user changed idea...

		# proceed loading the file chosen by the user
		# this can be done with e.g. wxPython input streams:
		self.infos["file"] = (openFileDialog.GetPath())
		
		# read file
		self.infos["image"] = Image.open(self.infos["file"])
		self.infos["image"] = self.infos["image"].convert("RGBA") # convert so tiffs work well

		self.infos["image"].putalpha(256) # create alpha channel
		self.infos["imageData"]  = numpy.array(self.infos["image"])

		
		height, width, channels = self.infos["imageData"].shape
		self.infos["imageWidth"] = width
		self.infos["imageHight"] = height
		
		self.infos["image_original"] = self.infos["image"]
		
		# set mode to move image
		self.infos["currentAction"]="MoveImage"
		# update GUI
		self.updateGUI()
		
		# set filepath:
		self.infos['path'] 		= "%s%s" %(os.path.dirname(self.infos["file"]),"/")
		self.infos['filename'] 	= os.path.basename(self.infos["file"])
		

		
		# set name
		self.SetTitle("gelImage - %s" % (self.infos['filename']))
	
	def OnSave(self, e):
		self.cairo.saveFile()
	
	def invertImage(self, e):
		
		image = self.infos["image"]
		
		if image.mode == 'RGBA':
			r,g,b,a = image.split()
			rgb_image = Image.merge('RGB', (r,g,b))

			inverted_image = PIL.ImageOps.invert(rgb_image)

			r2,g2,b2 = inverted_image.split()

			self.infos["image"] = Image.merge('RGBA', (r2,g2,b2,a))

			#final_transparent_image.save('new_file.png')

		else:
			self.infos["image"] = PIL.ImageOps.invert(image)
			#inverted_image.save('new_name.png')
			
		self.infos["image"].putalpha(256) # create alpha channel
		self.infos["imageData"]  = numpy.array(self.infos["image"])
		height, width, channels = self.infos["imageData"].shape
		self.infos["imageWidth"] = width
		self.infos["imageHight"] = height
		self.updateGUI()
		
		return True
	

	def rotateImage(self,e):
		self.infos["currentAction"]="RotateImage"
		self.updateGUI()
		
		return False
	
	def PutLadder(self, e):
		self.infos["currentAction"]="addLadder"
		return True
		
	def MoveImage(self, e):
		self.infos["currentAction"]="MoveImage"

		return True
	
	def crop(self, e):
		self.infos["currentAction"]="CropImage"
		return True

	def labelLanes(self,e):
		self.infos["currentAction"]="LabelLanes"
		return True
	
	def selectExport(self,e):
		self.infos["currentAction"]="SelectExport"
		return True
				
	def onSelect(self, e):
		return True
	
	def onLadSelect(self, e):
		self.infos["ladder"] = self.LadderSelect.GetStringSelection()
		self.infos["currentAction"]="addLadder"
		
	def onUnitSelect(self, e):
		self.infos["unit"] = self.unitSelect.GetStringSelection()
		self.updateGUI()
	
	def onLabelSelect(self,e):
		self.infos["marks"] = self.labelSelect.GetStringSelection()
		self.infos["currentAction"]="LabelLanes"
		self.updateGUI()
	
	def onFontsizeSelect(self, e):
		self.infos["fontsize"] = self.labelFontsize.GetStringSelection()
		print self.infos["fontsize"]
		self.updateGUI()
	
	def remLadder(self,e):
		self.cairo.removeLadders()
		self.updateGUI()
		
	def remLabels(self, e):
		self.cairo.remLabels()
		self.updateGUI()
	
	


def main():
    ex = wx.App()
    f = gelImage(None)
    f.Show(True)  
    ex.MainLoop()  

if __name__ == '__main__':
    main()

