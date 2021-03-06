#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ## ###############################################
#
# interfaceTools.py
# Contains all the tools for creating an interface
#
# Autor: Charlie Brian Monterrubio Lopez
# License: MIT
#
# ## ###############################################

from tkinter import *    # Carga módulo tk (widgets estándar)
from tkinter import filedialog as fd
from tkinter import ttk  # Carga ttk (para widgets nuevos 8.5+)
from tkinter import messagebox
from PIL import ImageTk, Image

import cv2 
import os
import src.oibread as oib
import src.tiff as tif

# Define la ventana principal de la aplicación
mainWindow = Tk() 
psftypes = ['psf.ISOTROPIC | psf.EXCITATION','psf.ISOTROPIC | psf.EMISSION','psf.ISOTROPIC | psf.WIDEFIELD','psf.ISOTROPIC | psf.CONFOCAL',
'psf.ISOTROPIC | psf.TWOPHOTON','psf.GAUSSIAN | psf.EXCITATION','psf.GAUSSIAN | psf.EMISSION','psf.GAUSSIAN | psf.WIDEFIELD','psf.GAUSSIAN | psf.CONFOCAL',
'psf.GAUSSIAN | psf.TWOPHOTON','psf.GAUSSIAN | psf.EXCITATION | psf.PARAXIAL','psf.GAUSSIAN | psf.EMISSION | psf.PARAXIAL','psf.GAUSSIAN | psf.WIDEFIELD | psf.PARAXIAL',
'psf.GAUSSIAN | psf.CONFOCAL | psf.PARAXIAL','psf.GAUSSIAN | psf.TWOPHOTON | psf.PARAXIAL']
file = ''
filesName = []
filesPath = []
statusBar = None
tensor_img = None
panelImg = None
cmbxFile, opcSF = (None, None)
windows_img = []
infoFile = {}

def openFile():
	"""This function open files of type .oib .tif and .bmp"""
	global file, tensor_img, panelImg
	filepath = fd.askopenfilename(initialdir = os.getcwd(), title = 'Select a file', defaultextension = '*.*', filetypes = (('oib files','*.oib'),('lsm files','*.lsm'),('tiff files','*.tiff'),('tif files','*.tif'),('bmp files','*.bmp'),('png files','*.png'),('jpg files','*.jpg')))
	if(len(filepath)>0):
		try:
			nameFile = filepath.split('/')[-1]
			if(os.path.splitext(nameFile)[1]=='.tif' or os.path.splitext(nameFile)[1]=='.tiff' or os.path.splitext(nameFile)[1]=='.lsm'):
				tensor_img = tif.readTiff(filepath)
				from src.imageFunctions import istiffRGB
				if(not(istiffRGB(tensor_img.shape))):
					print('File: ', nameFile)
					print(tensor_img.shape)
					
					if(tensor_img.ndim==4 or tensor_img.ndim==3):
						venImg = NewWindow(filepath, image = True)
						venImg.desplay_image(tensor_img)
						windows_img.append(venImg)	
					else:
						venImg = NewWindow(filepath, image = True)
						venImg.placeImage(tensor_img)
						venImg.tensor_img = tensor_img
						windows_img.append(venImg)
					
			elif(os.path.splitext(nameFile)[1]=='.oib'):
				print('File: ', nameFile)
				tensor_img = oib.get_matrix_oib(filepath)
				print(tensor_img.shape)
				
				venImg = NewWindow(filepath, image = True)
				venImg.desplay_image(tensor_img)
				windows_img.append(venImg)
			else:
				import cv2
				print('File: ', nameFile)
				matrix_img = cv2.imread(filepath)
				venImg = NewWindow(filepath, image = True)
				venImg.placeImage(matrix_img)
				venImg.tensor_img = matrix_img
				windows_img.append(venImg)
		except:
			messagebox.showinfo(message='Format not supported')				
	
def saveFile():
	"""This function save files of type .oib .tif and .bmp"""
	global cmbxFile, opcSF
	if(len(windows_img)>0):
		opcSF = NewWindow('Save File','300x100')
		opcSF.createLabel('What image do you want to save?',20,20)
		windows_img_names = getNamesWindows()
		cmbxFile = opcSF.createCombobox2(windows_img_names,20,50)
		opcSF.createButton('Save', saveFileEvent, 'bottom')
	else: 
		messagebox.showinfo(message='No file has been opened')
	
def saveFileEvent():
	global cmbxFile, opcSF
	import tifffile
	import os
	import numpy as np
	from src.imageFunctions import istiffRGB
	selected_file = cmbxFile.current()
	image = windows_img[selected_file].tensor_img
	namewin = windows_img[selected_file].nameWindow
	
	try:
		if(image.ndim==4):
			savepath = fd.asksaveasfilename(initialdir = os.getcwd(),title = 'Select a file', defaultextension = '.tif', initialfile = namewin, filetypes = (('tif files','*.tif'),))
			if (savepath!=''):
				tifffile.imsave(savepath, np.uint16(image*(65535/image.max())), imagej=True)
				printMessage('Saved file: '+savepath)
		if(image.ndim==3):
			savepath = fd.asksaveasfilename(initialdir = os.getcwd(),title = 'Select a file', defaultextension = '.tif', initialfile = namewin, filetypes = (('tif files','*.tif'),('png files','*.png'),('jpg files','*.jpg'),('bmp files','*.bmp')))
			if(not(istiffRGB(image.shape))):			
				tifffile.imsave(savepath, np.uint16(image*(65535/image.max())), imagej=True)
				printMessage('Saved file: '+savepath)
			else: 
				cv2.imwrite(savepath, image)
				printMessage('Saved file: '+savepath)	
		if(image.ndim==2):	
			savepath = fd.asksaveasfilename(initialdir = os.getcwd(),title = 'Select a file', defaultextension = '.png', initialfile = namewin, filetypes = (('png files','*.png'),('jpg files','*.jpg'),('bmp files','*.bmp')))
			cv2.imwrite(savepath, image)
			printMessage('Saved file: '+savepath)
		opcSF.destroy()	
	except:
		messagebox.showinfo(message='Error when trying to save the file, try again')
		print("Error: ", sys.exc_info()[0])
		
def printMessage(message):
	print(message)
	statusBar.configure(text = message)

def getNamesWindows():
	names = []
	for window_object in windows_img:
		names.append(window_object.nameWindow)
	return names
	
def getFormatTime(time):
	print(time)
	minutes = int(time/60)
	seconds = int(time%60)
	return (minutes, seconds)
	
def createWindowMain():
	"""Definition of the main window"""
	# Define la ventana principal de la aplicación
	#mainWindow = Tk() 
	mainWindow.geometry('500x50') # anchura x altura
	# Asigna un color de fondo a la ventana. 
	mainWindow.configure(bg = 'beige')
	# Asigna un título a la ventana
	mainWindow.title('IFC Microspy')
	#mainWindow.iconbitmap('icon/ifc.ico')
	mainWindow.tk.call('wm', 'iconphoto', mainWindow._w, PhotoImage(file='src/icon/ifc.png'))
	mainWindow.resizable(width=False,height=False)
	#return mainWindow
	
#def createMenu(mainWindow):
def createMenu():
	"""This function creates a menu"""
	#Barra superior
	menu = Menu(mainWindow)
	mainWindow.config(menu=menu)
	return menu
	
def createOption(menu):
	"""This function creates a menu option"""
	opc = Menu(menu, tearoff=0)
	return opc
	
def createCommand(opc, labelName, commandName):
	"""This function creates a command"""
	opc.add_command(label=labelName, command = commandName)
	
def createCascade(menu, labelName, option):
	"""This function creates a tab main"""
	menu.add_cascade(label=labelName, menu=option)
	
def createButton(text, command, side):
	"""This function creates a button"""
	ttk.Button(mainWindow, text=text, command=command).pack(side=side)
	
def createEntry(stringVar,x,y):
	"""This function creates a entry"""
	entry = ttk.Entry(mainWindow, textvariable=stringVar)
	entry.place(x=x, y=y)
	return entry

def createLabel(text,x,y):
	"""This function creates a label"""
	label = Label(mainWindow, text=text, font=("Arial", 12)).place(x=x, y=y)
	
def createStringVar():
	"""This function creates a StringVar"""
	nombre = StringVar()
	return nombre
	
def createStatusBar():
	"""This function creates a status bar"""
	global statusbar
	v = os.popen('git tag').read().split('\n')
	statusbar = Label(mainWindow, text='IFC Microspy '+v[0], bd=1, relief=SUNKEN, anchor=W)
	statusbar.pack(side=BOTTOM, fill=X)
	return statusbar
	
class NewWindow:
	"""This class contains the functions to define a window"""
	
	def __init__(self,nameWindow,size = None, image = False):
		if image:
			self.nameFile = nameWindow.split('/')[-1]
			self.nameWindow = self.nameFile.split('.')[0]
			self.path = nameWindow
			self.img, self.tensor_img = (None, None)
			self.axisz_max, self.axisc_max, self.posz, self.posc = (0, 0, 0, 0)
		else: 
			self.nameWindow = nameWindow
			self.nameFile, self.path = (None, None)
			
		self.window = Toplevel(mainWindow)
		self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
		self.window.geometry(size) # (width, height)
		#self.window.configure(bg = 'beige')
		self.window.tk.call('wm', 'iconphoto', self.window._w, PhotoImage(file='src/icon/ifc.png'))
		self.window.resizable(width=False,height=False)
		self.window.title(self.nameWindow)
				
		
	def on_closing(self):
		print('Closed: ', self.nameWindow)
		if (self.nameWindow in filesName):
			filesName.remove(self.nameWindow)
		if (self in windows_img):
			windows_img.remove(self)
		self.window.destroy()	
			
	def destroy(self):
		self.window.destroy()
		
	def placeImage(self,img):
		resized = self.resize_image_percent(img, 60)
		self.img = ImageTk.PhotoImage(image=Image.fromarray(resized))
		self.panel = Label(self.window, image = self.img)
		self.panel.image = self.img
		self.panel.pack()

	def placeImageTensor(self,img):
		
		# resize image
		resized = self.resize_image_percent(img, 60)
		
		self.img = ImageTk.PhotoImage(image=Image.fromarray(resized))
		self.panel = Label(self.window, image = self.img)
		self.panel.image = self.img
		self.panel.pack()
		return self.panel
		
	def createButton(self,text, command, side):
		ttk.Button(self.window, text=text, command=command).pack(side=side)	

	def createButtonXY(self,text, command, x, y):
		ttk.Button(self.window, text=text, command=command).place(x=x,y=y)	
		
	def createLabel(self,text,x,y):
		#Label(self.window, text=text).pack(anchor=CENTER)
		label = Label(self.window, text=text, font=("Arial", 12)).place(x=x, y=y)

	def createEntry(self,stringVar,x,y, width=10,disabled=False):
		if disabled:
			entry = ttk.Entry(self.window, width=width)
			entry.insert(0,stringVar)
			entry.configure(state=DISABLED)
		else:
			entry = ttk.Entry(self.window, width=width)
		entry.insert(0, stringVar)
		entry.place(x=x, y=y)
		return entry
		
	def createCombobox(self,x,y):
		global files
		dropdown = ttk.Combobox(self.window, state="readonly",values = psftypes, width=40)
		dropdown.place(x=x, y=y)
		if (len(filesName)>0):
			dropdown.current(0)
		dropdown.current(13)
		return dropdown		
		
	def createCombobox2(self,values,x,y):
		dropdown = ttk.Combobox(self.window, state="readonly",values = values, width=40)
		dropdown.place(x=x, y=y)
		if (len(values)>0):
			dropdown.current(0)
		return dropdown
		
	def scrollbarz(self, maxpos):
		self.scrollbarz = Scrollbar(self.window, orient=HORIZONTAL, command=self.scrollImagez)
		self.scrollbarz.pack(side=BOTTOM,fill=X)
		
		self.listboxz = Listbox(self.window, yscrollcommand=self.scrollbarz.set)
		for i in range(10+maxpos):
			self.listboxz.insert("end", '')
		self.listboxz.place(x=50,y=50)
		return self.scrollbarz
		
	def scrollbarc(self, maxpos, zscroll = True):
		if zscroll:
			self.scrollbarc = Scrollbar(self.window, orient=HORIZONTAL, command=self.scrollImagec)
			self.scrollbarc.pack(side=BOTTOM,fill=X)
		else:
			self.scrollbarc = Scrollbar(self.window, orient=HORIZONTAL, command=self.scrollImagecs)
			self.scrollbarc.pack(side=BOTTOM,fill=X)		
		
		self.listboxc = Listbox(self.window, yscrollcommand=self.scrollbarc.set)
		for i in range(10+maxpos):
			self.listboxc.insert("end", '')
		self.listboxc.place(x=50,y=50)
		return self.scrollbarc
		
	def createStatusBar(self):
		self.text = 'c:'+str(self.posc+1)+'/'+str(self.axisc_max)+' z:'+str(self.posz+1)+'/'+str(self.axisz_max)
		self.statusbar = Label(self.window, text=self.text, bd=1, relief=SUNKEN, anchor=W)
		self.statusbar.pack(side=TOP, fill=X)
		return self.statusbar
		
	def update_axes(self, axisc_max, axisz_max):
		self.axisz_max = axisz_max
		self.axisc_max = axisc_max
		
	def resize_image_percent(self, img, percent):
		import cv2
		import numpy as np
		import src.imageFunctions as imf
		width = int(img.shape[1] * percent / 100)
		height = int(img.shape[0] * percent / 100)
		dim = (width, height)	
		
		# resize image
		resized = cv2.resize(img, dim, interpolation = cv2.INTER_LINEAR)
		
		return imf.normalizar(resized)
		
	def scrollImagez(self, *args):
		if ('-1' in args and self.posz > 0):
			self.posz = self.posz - 1
		
		if ('1' in args and self.posz < self.axisz_max-1):
			self.posz = self.posz + 1
			
		print(self.posc,self.posz)
		self.text = 'c:'+str(self.posc+1)+'/'+str(self.axisc_max)+' z:'+str(self.posz+1)+'/'+str(self.axisz_max)
		self.statusbar.configure(text = self.text)
		resized = self.resize_image_percent(self.tensor_img[self.posz,self.posc,:,:],60)
		self.img = ImageTk.PhotoImage(image=Image.fromarray(resized))

		self.panelImg['image'] = self.img
		self.panelImg.image = self.img
		self.scrollbarz.config(command=self.listboxz.yview(self.posz))	
		
	def scrollImagec(self, *args):
		if ('-1' in args and self.posc > 0):
			self.posc = self.posc - 1
		
		if ('1' in args and self.posc < self.axisc_max-1):
			self.posc = self.posc + 1
			
		print(self.posc,self.posz)
		self.text = 'c:'+str(self.posc+1)+'/'+str(self.axisc_max)+' z:'+str(self.posz+1)+'/'+str(self.axisz_max)
		self.statusbar.configure(text = self.text)
		resized = self.resize_image_percent(self.tensor_img[self.posz,self.posc,:,:],60)
		self.img = ImageTk.PhotoImage(image=Image.fromarray(resized))

		self.panelImg['image'] = self.img
		self.panelImg.image = self.img			
		self.scrollbarc.config(command=self.listboxc.yview(self.posc))	
		
	def scrollImagecs(self, *args):

		if ('-1' in args and self.posc > 0):
			self.posc = self.posc - 1
		if ('1' in args and self.posc < self.axisc_max-1):
			self.posc = self.posc + 1
			
		print(self.posc,self.posz)
		self.text = 'c:'+str(self.posc+1)+'/'+str(self.axisc_max)
		self.statusbar.configure(text = self.text)
		resized = self.resize_image_percent(self.tensor_img[self.posc,:,:],60)
		self.img = ImageTk.PhotoImage(image=Image.fromarray(resized))

		self.panelImg['image'] = self.img
		self.panelImg.image = self.img			
		self.scrollbarc.config(command=self.listboxc.yview(self.posc))		
		
	def desplay_image(self, tensor_img):
		self.tensor_img = tensor_img
		if tensor_img.ndim == 4:
			self.update_axes(tensor_img.shape[1],tensor_img.shape[0])
			self.createStatusBar()
			scrollz = self.scrollbarz(tensor_img.shape[0]-1)
			scrollc = self.scrollbarc(tensor_img.shape[1]-1)
			self.panelImg = self.placeImageTensor(tensor_img[0,0,:,:])
		
		if tensor_img.ndim == 3:
			self.update_axes(tensor_img.shape[0],0)
			self.createStatusBar()
			scrollc = self.scrollbarc(tensor_img.shape[0]-1, zscroll=False)
			self.panelImg = self.placeImageTensor(tensor_img[0,:,:])
