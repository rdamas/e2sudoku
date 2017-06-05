# -*- coding: utf-8 -*-
from enigma import eTimer, getDesktop, gFont, RT_HALIGN_CENTER, RT_VALIGN_CENTER
from Components.ActionMap import NumberActionMap
from Components.Label import Label
from Components.Sources.CanvasSource import CanvasSource   
from Components.Sources.StaticText import StaticText   
from Screens.Screen import Screen
from Tools.Directories import resolveFilename, SCOPE_PLUGINS

from random import randint

from __init__ import _

def argb(a,r,g,b):
	return (a<<24)|(r<<16)|(g<<8)|b

class Cell():
	color = { 
		"black": argb(0,0,0,0), 
		"text1": argb(0,0,0,0xe0), 
		"text2": argb(0,0xe0,0,0), 
		"dark":  argb(0,0xd9,0xd9,0xc5), 
		"light": argb(0,0xff,0xff,0xff), 
		"focus": argb(0,0xff,0xfa,0xcd)
	}
	w = 100
	h = 100
	fontsize = 48
	
	def __init__(self,canvas,x,y,val):
		self.canvas = canvas
		self.x = x
		self.y = y
		self.val = val
		self.block = self.getBlock()
		self.hasFocus = False
		self.isReadOnly = val != " "

	# Flag setzen, ob das Feld den Fokus hat oder nicht.
	# Gibt self zurück, damit die Methode chainable ist.
	def setFocus(self, hasFocus):
		self.hasFocus = hasFocus
		return self
	
	def getVal(self):
		if self.val != " ":
			return self.val
		return 0
	
	def setVal(self, val):
		if not self.isReadOnly:
			if val == 0:
				val = " "
			self.val = val
		return self
	
	# In welchem Dreier-Block befindet sich die Zelle?
	# Zur Bestimmung der Hintergrundfarbe.
	def getBlock(self):
		return (self.y)/3*3+(self.x)/3
	
	def getBgColor(self):
		if self.hasFocus:
			return Cell.color["focus"]
		if self.block % 2 == 0:
			return Cell.color["dark"]
		else:
			return Cell.color["light"]
		
	def getColor(self):
		if self.isReadOnly:
			return Cell.color["text1"]
		else:
			return Cell.color["text2"]
		
	def getX(self):
		return (self.x+1)*Cell.w
	
	def getY(self):
		return (self.y+1)*Cell.h
	
	# Eine Zelle zeichnen:
	# Für den Rahmen eine schwarze Zelle
	# Darin eine etwas kleinere Zelle mit der Hintergrundfarbe
	# Darin die gewählte Zahl in der Textfarbe
	def draw(self):
		bg = self.getBgColor()
		frame = Cell.color["black"]
		color = self.getColor()
		self.canvas.fill(self.getX(), self.getY(), Cell.w, Cell.h, Cell.color["black"])
		self.canvas.fill(self.getX()+2, self.getY()+2, Cell.w-4, Cell.h-4, bg)
		self.canvas.writeText(self.getX()+2, self.getY()+2, Cell.w-4, Cell.h-4, 
			color, bg, gFont("Regular", Cell.fontsize), str(self.val), 
			RT_HALIGN_CENTER|RT_VALIGN_CENTER)
		self.canvas.flush()
		return self
		
class Sudoku(Screen):
	version = "2017-06-05 0.1.1"
	skin = { "fhd" : """
		<screen name="E2Sudoku" position="0,0" size="1920,1080" title="Sudoku" flags="wfNoBorder">
			<widget source="Canvas" render="Canvas" position="0,0" size="1080,1080" />
			<widget name="runtime" position="1200,100" size="400,50" font="Regular;36"/>
			<widget name="message" position="1200,175" size="700,50" font="Regular;30"/>
			<widget name="level" position="1200,250" size="700,50" font="Regular;30"/>
			<widget source="key_red" render="Label" position="1200,950" zPosition="1" size="250,50" font="Regular;24" halign="center" valign="center" backgroundColor="#f01010" foregroundColor="#ffffff" transparent="0" />
			<widget source="key_green" render="Label" position="1500,950" zPosition="1" size="250,50" font="Regular;24" halign="center" valign="center" backgroundColor="#10a010" foregroundColor="#ffffff" transparent="0" />
			<widget source="key_yellow" render="Label" position="1200,325" zPosition="1" size="250,50" font="Regular;24" halign="center" valign="center" backgroundColor="#f0f010" foregroundColor="#303030" transparent="0" />
			<widget source="key_blue" render="Label" position="1500,325" zPosition="1" size="250,50" font="Regular;24" halign="center" valign="center" backgroundColor="#0000e0" foregroundColor="#ffffff" transparent="0" />
		</screen>
	""",
	
			"hd" : """
		<screen name="E2Sudoku" position="0,0" size="1280,720" title="Sudoku" flags="wfNoBorder">
			<widget source="Canvas" render="Canvas" position="0,0" size="720,720" />
			<widget name="runtime" position="800,66" size="400,33" font="Regular;24"/>
			<widget name="message" position="800,117" size="400,33" font="Regular;20"/>
			<widget name="level" position="800,167" size="400,33" font="Regular;20"/>
			<widget source="key_red" render="Label" position="800,633" zPosition="1" size="190,33" font="Regular;16" halign="center" valign="center" backgroundColor="#f01010" foregroundColor="#ffffff" transparent="0" />
			<widget source="key_green" render="Label" position="1000,633" zPosition="1" size="190,33" font="Regular;16" halign="center" valign="center" backgroundColor="#10a010" foregroundColor="#ffffff" transparent="0" />
			<widget source="key_yellow" render="Label" position="800,217" zPosition="1" size="190,33" font="Regular;16" halign="center" valign="center" backgroundColor="#f0f010" foregroundColor="#303030" transparent="0" />
			<widget source="key_blue" render="Label" position="1000,217" zPosition="1" size="190,33" font="Regular;16" halign="center" valign="center" backgroundColor="#0000e0" foregroundColor="#ffffff" transparent="0" />
		</screen>
	"""
	}
	levelMap = [ _("Beginner"), _("Simple"), _("Medium"), _("Hard"), _("Impossible")]
	
	def __init__(self, session):
		self.adaptScreen()
		
		self.skin = Sudoku.skin[self.useskin]
		self.session = session
		Screen.__init__(self, session)
		
		self["actions"] =  NumberActionMap(["ColorActions", "ChannelUpDownActions", "SetupActions", "DirectionActions"], {
			"cancel":      self.cancel,
			"up":          self.moveUp,
			"down":        self.moveDown,
			"left":        self.moveLeft,
			"right":       self.moveRight,
			"channelUp":   self.moveToPrevBlock,
			"channelDown": self.moveToNextBlock,
			"red":         self.setupBoard,
			"green":       self.newGame,
			"yellow":      self.levelDown,
			"blue":        self.levelUp,
			"0":           self.enter,
			"1":           self.enter,
			"2":           self.enter,
			"3":           self.enter,
			"4":           self.enter,
			"5":           self.enter,
			"6":           self.enter,
			"7":           self.enter,
			"8":           self.enter,
			"9":           self.enter,
		}, -1)
		
		self["Canvas"] = CanvasSource()
		
		self["message"] = Label("")
		
		self["key_red"] = StaticText(_("Start over"))
		self["key_green"] = StaticText(_("New Board"))
		self["key_yellow"] = StaticText(_("Simpler"))
		self["key_blue"] = StaticText(_("Harder"))

		self.level = 0
		self["level"] = Label(_("Level: %s") % (Sudoku.levelMap[self.level],))
		
		sudokudb = resolveFilename(SCOPE_PLUGINS, "Extensions/E2Sudoku/sudoku.db")
		self.conn = open(sudokudb, "rb")
		
		self["runtime"] = Label()
		self.timer = eTimer()
		self.timer.callback.append(self.timerCallback)

		self.gamenum = randint(0,999) + 1000*self.level

		self.setupBoard()
		
	def timerCallback(self):
		self.runtime += 1
		self["runtime"].setText(_("Stop watch: %02d:%02d") % (self.runtime / 60, self.runtime % 60))
	
	# Für ein neues Spiel wird lediglich die gamenum neu gewürfelt und
	# dann das Board neu aufgebaut.
	def newGame(self):
		self.gamenum = randint(0,999) + 1000*self.level
		self.setupBoard()
	
	# Ein neues Board aufbauen und anzeigen
	def setupBoard(self):
		# Ein zufällig ausgesuchtes Board zu einem Level aus der Sudoku-DB holen
		lev = (self.level,)
		
		game = self.getBoard(self.gamenum)
		
		self["message"].setText(_("Sudoku #%d") % (self.gamenum,))

		# (x,y) ist die Position der ausgeählten Zelle.
		self.x = 4
		self.y = 4
		
		# Wenn in jeder Zeile und Spalte die Zahlensumme 45 steht,
		# ist das Sudoku gelöst; in rowsum wird über die Zeilen-
		# und Spaltensummen Buch geführt. Die ersten 9 Felder werden
		# für die Spaltensummen benutzt, die zweiten 9 Felder für die
		# Zeilensummen. 
		self.rowsum = [0] * 18
		# fieldSet führt Buch darüber, wieviele Felder insgesamt gesetzt sind.
		self.fieldsSet = 0
		
		self["Canvas"].fill(0,0,self.fb_h,self.fb_h, argb(33,255,255,255))

		# board speichert die Instanzen der Sudoku-Cells 
		self.board = []
		
		# Das ausgesuchte Board aufbauen, Spalten- und Zeilensummen 
		# sowie Anzahl gesetzte Felder initialisieren, 
		for y in range(0,9):
			for x in range(0,9):
				hasFocus = x == self.x and y == self.y
				val = game[x+9*y]
				self.board.append( Cell(self["Canvas"],x,y,val).setFocus(hasFocus).draw() )
				if val != " ":
					self.rowsum[y]   += int(val)
					self.rowsum[9+x] += int(val)
					self.fieldsSet   += 1
		
		self["Canvas"].flush()
		self.isTimerRunning = False
		self.runtime = 0
		self["runtime"].setText(_("Stop watch: %02d:%02d") % (0,0))
	
	def getBoard(self, num):
		self.conn.seek(41 * num)
		bytes = self.conn.read(41)

		game = ""
		for x in range(41):
			nib = ord(bytes[x])
			nib1 = nib % 16
			nib2 = nib >> 4;
			game += str(nib1)
			if nib2 != 13:
				game += str(nib2)
		return game.replace("0", " ")
		
	def cancel(self):
		self.timer.stop()
		self.conn.close()
		self.close()
	
	def moveUp(self):
		self.move("up")
		
	def moveDown(self):
		self.move("down")
		
	def moveLeft(self):
		self.move("left")
		
	def moveRight(self):
		self.move("right")
		
	def moveToNextBlock(self):
		self.move("next")
		
	def moveToPrevBlock(self):
		self.move("prev")
	
	# Cursor-Bewegungen am Board anzeigen
	def move(self,direction):
		cell = self.board[self.x + self.y*9]
		cell.setFocus(False).draw()
		
		if direction == "up":
			self.y = (self.y-1) % 9
		elif direction == "down":
			self.y = (self.y+1) % 9
		elif direction == "left":
			self.x = (self.x-1) % 9
		elif direction == "right":
			self.x = (self.x+1) % 9
		elif direction == "prev":
			oldx = self.x
			self.y = ((self.y)/3*3) + 1
			self.x = ((self.x+3)/3*3) % 9 + 1
			if oldx > self.x:
				self.y = (self.y + 3) % 9
		elif direction == "next":
			oldx = self.x
			self.y = ((self.y)/3*3) + 1
			self.x = ((self.x-3)/3*3) % 9 + 1
			if oldx < self.x:
				self.y = (self.y - 3) % 9
			
		cell = self.board[self.x + self.y*9]
		cell.setFocus(True).draw()
	
	# Zahlentasten am Board darstellen
	def enter(self, val):
		if val == "0":
			val = " "
		# Muss der Timer gestartet werden?
		if not self.isTimerRunning:
			if self.fieldsSet == 81:
				# Das Spiel ist beendet - nichts machen
				return
			else:
				self.runtime = 0
				self.isTimerRunning = True
				self.timer.start(1000)
			
		# Zeilen- und Spaltensumme sowie Anzahl der gesetzten Felder
		# updaten.
		cell = self.board[self.x + self.y*9]
		oldval = int(cell.getVal())
		self.rowsum[self.y] -= oldval
		self.rowsum[9+self.x] -= oldval
		if oldval != 0:
			self.fieldsSet -= 1
		
		cell.setVal(val).draw()
		
		# newval wird neu geholt, weil die Zelle read-only sein könnte.
		# Dann wird der übergebene val natürlich nicht gesetzt.
		newval = int(cell.getVal())
		self.rowsum[self.y] += newval
		self.rowsum[9+self.x] += newval
		if newval != 0:
			self.fieldsSet += 1
		
		# Wenn alle 81 Felder besetzt sind, prüfen, ob das Board gelöst ist
		if self.fieldsSet == 81:
			if self.isSolved():
				self.timer.stop()
				self.isTimerRunning = False
				self["message"].setText(_("You solved the Board."))
			else:
				self["message"].setText(_("The Board contains errors."))
	
	# Prüfen, ob ein Board gelöst ist. Dazu müssen alle Zeilen- und 
	# Spaltensummen 45 betragen (Summe der Zahlen 1-9)
	def isSolved(self):
		for rowsum in self.rowsum:
			if rowsum != 45:
				return False
		return True
	
	# Level verändern
	def levelUp(self):
		if self.level < 4:
			self.level += 1
		self["level"].setText(_("Level: %s") % (Sudoku.levelMap[self.level],))
	
	def levelDown(self):
		if self.level > 0:
			self.level -= 1
		self["level"].setText(_("Level: %s") % (Sudoku.levelMap[self.level],))
	
	# Anhand der Desktop-Größe einige Variablen anpassen;
	# so sollte es egal sein, ob ein SD, HD oder FHD-Skin benutzt wird.
	def adaptScreen(self):
		self.fb_w = getDesktop(0).size().width()
		self.fb_h = getDesktop(0).size().height()
		if self.fb_w < 1280:
			Cell.w = 50
			Cell.h = 50
			Cell.fontsize = 24
			self.useskin = "hd"
		elif self.fb_w < 1920:
			Cell.w = 66
			Cell.h = 66
			Cell.fontsize = 30
			self.useskin = "hd"
		else:
			Cell.w = 100
			Cell.h = 100
			Cell.fontsize = 48
			self.useskin = "fhd"
		
	
