# -*- coding: utf-8 -*-
#!/usr/bin/env python

import wx
#import Image
from PIL import Image
import numpy


class imgvisualizar(wx.Frame):

	imagem = ''
	def __init__(self, parent,id):

		self.p = parent

		wx.Frame.__init__(self, parent, id, 'Visualizar Imagens')
		self.panel = wx.Panel(self)

		imgvisualizar.imagem = self.imagem.split('|')[0]

		width, height = wx.DisplaySize()
		try:

			im = Image.open(self.imagem)
			if   im.size[0] < 100:	Tamanho = 100
			elif im.size[0] > 700:	Tamanho = 700
			else:	Tamanho = im.size[0]
		
			self.pictureMaxSize = Tamanho

			img = wx.EmptyImage(self.pictureMaxSize, self.pictureMaxSize)
			self.imageCtrl = wx.StaticBitmap(self.panel, wx.ID_ANY, wx.BitmapFromImage(img))

			self.mainSizer = wx.BoxSizer(wx.VERTICAL)
			self.mainSizer.Add(self.imageCtrl, 0, wx.ALL|wx.CENTER, 5)
			self.panel.SetSizer(self.mainSizer)
			self.mainSizer.Fit(self)
			
			self.draw( self.imagem )

			info = wx.StaticText(self.panel,-1,"{ Informaçoes }",pos=(5,5))
			info.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		except Exception, _reTornos:
			
			cabe = wx.StaticText(self.panel,-1,"Imagem Não Localizada \n\n"+str( _reTornos ),pos=(0,0))
			cabe.SetForegroundColour('#A52A2A')
			cabe.SetFont(wx.Font(15,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))


	def draw(self, filename) :

		image_name = filename
		wx.Log.SetLogLevel(0) #--:[ Nao aparecer a menssagem ICCP: knpwn incorrect sRGB file ]
		img = wx.Image(filename, wx.BITMAP_TYPE_ANY)
		
		W = img.GetWidth()
		H = img.GetHeight()
		if W > H:
			NewW = self.pictureMaxSize
			NewH = self.pictureMaxSize * H / W
		else:
			NewH = self.pictureMaxSize
			NewW = self.pictureMaxSize * W / H
		img = img.Scale(NewW,NewH)
		self.imageCtrl.SetBitmap(wx.BitmapFromImage(img))
		self.panel.Refresh()
		self.mainSizer.Fit(self)
