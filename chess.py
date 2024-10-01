import sys
import copy
from collections import Counter
import tkinter
import os
from tkinter import *
from tkinter import messagebox

MAX_TURNS = 50
FRAME_WIDTH = 1200
FRAME_HEIGHT = 800
BOARD_WIDTH = 400
BUTTON_WIDTH = 50
STATUS_WIDTH = 24
STATUS_PAD = 10
BOARD_FILES = BOARD_RANKS = 8

# GUI

class position: # forward declaration
	pass

class ChessMainWnd(tkinter.Frame):
	GUIboard = []
	rc = 0
	cc = 0
	NO_SELECTION, FROM_SELECTED, TO_SELECTED = range(3)
	selectionstate = NO_SELECTION
	GUImovestart = position()
	GUImoveend = position()
	
	def __init__(s, parent, game):
		try:
			s.gm = game
			tkinter.Frame.__init__(s, parent)
			s.bigpane = Frame(s,height=FRAME_HEIGHT, width = FRAME_HEIGHT)
			s.bigpane.pack(side=LEFT, fill = Y)
			
			s.boardpane = Frame(s.bigpane)
			s.boardpane.pack(side=LEFT, expand = 1)

			root = parent
			root.title("Chess")
			
			root.bind("<<TurnChange>>",s.turn_change)
			
			s.labelframe = LabelFrame(s.bigpane, text="")
			s.labelframe.pack(fill="both", expand="yes")
			s.l1text = StringVar()
			s.l2text = StringVar()
			s.l2 = Label(s.labelframe, textvariable = s.l2text, padx = STATUS_PAD, pady = 1, width = STATUS_WIDTH, justify = "center")
			s.l2text.set("")
			s.l1 = Label(s.labelframe, textvariable = s.l1text, padx = STATUS_PAD, pady = 1, width = STATUS_WIDTH, justify = "center")
			s.l1text.set(s.game_details())
			s.l1.pack()
			s.l2.pack()
			
			img = PhotoImage(file=get_this_dir() + 'chess.gif')
			root.tk.call('wm', 'iconphoto', root._w, img)
			
			menubar = Menu(root)

			# create a pulldown menu, and add it to the menu bar
			filemenu = Menu(menubar, tearoff=0)
			filemenu.add_command(label="New", command=s.new)
			filemenu.add_command(label="Open", command=s.load)
			filemenu.add_command(label="Save", command=s.gm.save_game)
			filemenu.add_separator()
			filemenu.add_command(label="Exit", command=s.exit)
			menubar.add_cascade(label="Game", menu=filemenu)

			# create more pulldown menus
			optionsmenu = Menu(menubar, tearoff=0)
			optionsmenu.add_command(label="Computer control", command=s.computer_control)
			optionsmenu.add_command(label="Player control", command=s.player_control)
			optionsmenu.add_command(label="Play computer move", command=s.play)
			menubar.add_cascade(label="Control", menu=optionsmenu)

			# create more pulldown menus
			advancedmenu = Menu(menubar, tearoff=0)
			advancedmenu.add_command(label="Statistics", command=s.showstats)
			menubar.add_cascade(label="Advanced", menu=advancedmenu)

			helpmenu = Menu(menubar, tearoff=0)
			helpmenu.add_command(label="About", command=s.help)
			menubar.add_cascade(label="Help", menu=helpmenu)

			# display the menu
			root.config(menu=menubar)
			
			#create a list of buttons		
			for r in range(BOARD_RANKS):
				GUIrows = []
				for c in range(BOARD_FILES):
					s.rc = int(r)
					s.cc = int(c)				
					p = game.cboard.grid[r][c]
					alt_txt, im = s.set_square_image(p, r, c)
					if b_images:
						b = tkinter.Button(s.boardpane, image=im, borderwidth=0, bd = 0, bg = "grey", command = s.button_click, highlightcolor = "red" )
					else:
						b = tkinter.Button(s.boardpane, text = alt_txt, borderwidth=0, bd = 0, bg = "grey", command = s.button_click, highlightcolor = "red" )
					GUIrows.append(b) 
				s.GUIboard.append(GUIrows)
			
			s.display()
			s.pack(side='top')
			
		except:
			print("ChessMainWnd::__init__ : Unexpected exception: ",sys.exc_info()[:2])
		
	def turn_change(s, val):	
		if s.gm.players[s.gm.cplayer].b_computer:
			s.play()
			
	def exit(s):
		s.quit()
		s.destroy()
		
	def recreate_board(s):
		for r in range(BOARD_RANKS):
				for c in range(BOARD_FILES):
					s.rc = int(r)
					s.cc = int(c)				
					p = s.gm.cboard.grid[r][c]
					alt_txt, im = s.set_square_image(p, r, c)
					
					if b_images:
						b = s.GUIboard[r][c]['image'] = im
						b = s.GUIboard[r][c]['bg'] = 'grey'
					else:
						b = s.GUIboard[r][c]['text'] = alt_txt
						b = s.GUIboard[r][c]['bg'] = 'grey'
			
		s.l1text.set(s.game_details())
		
	def computer_control(s):
		if not s.gm.players[s.gm.cplayer].b_computer:
			s.gm.players[s.gm.cplayer].b_computer = True
			messagebox.showinfo("Control change", "The computer now has control of " + str(s.gm.players[s.gm.cplayer].name))
			s.play()
		else:
			messagebox.showwarning("Control change", "The computer already has control of " + str(s.gm.players[s.gm.cplayer].name))
			
	def player_control(s):
		if s.gm.players[1-s.gm.cplayer].b_computer:
			s.gm.players[1-s.gm.cplayer].b_computer = False
			messagebox.showinfo("Control change", "You now have control of " + str(s.gm.players[1-s.gm.cplayer].name))		
		else:
			messagebox.showwarning("Control change", "You already have control of " + str(s.gm.players[1-s.gm.cplayer].name))
		
	def help(s):
		hs = s.gm.build_helpstring()
		messagebox.showinfo("Chess",hs)
		
	def showstats(s):
		ss = s.gm.build_stats()
		messagebox.showinfo("Stats",ss)	
	
	def new(s):
		s.gm.turn = 1
		s.gm.cplayer = 1
		s.gm.new_game()
		s.recreate_board()
		s.l2text.set("")
	  
	def load(s):
		if s.gm.load_game():
			s.recreate_board()
			s.l2text.set("")
		else:
			messagebox.showinfo("Open","No saved game was found.")
	
	def game_details(s):
		game_details = s.gm.players[s.gm.cplayer].name + "'s turn"
		return game_details
			
	def set_square_image(s, p, row, col):
		pos = position(row, col)
		btp = s.gm.basic_type(p)
		for each in s.gm.players[0].positions:
			if each == pos:
				# convert player 1 to lower case:
				btp = btp.lower()
				break
	
		alt_txt = " "
		if b_images:
			if ((row*(BOARD_RANKS + 1))+col) % 2 == 0:
				im = light
			else:
				im = dark
		else:
			im = None
		if btp != '.':
			alt_txt = btp
			if btp == 'p' and b_images:
				if im == light:
					im = lpawnd
				else:
					im = dpawnd
			elif btp == 'P' and b_images:
				if im == light:
					im = lpawn
				else:
					im = dpawn
			elif btp == 'b' and b_images:
				if im == light:
					im = lbishopd
				else:
					im = dbishopd
			elif btp == 'B' and b_images:
				if im == light:
					im = lbishop
				else:
					im = dbishop
			elif btp == 'r':
				if im == light and b_images:
					im = lrookd
				elif b_images:
					im = drookd
			elif btp == 'R':
				if im == light and b_images:
					im = lrook
				elif b_images:
					im = drook
			elif btp == 'n'  and b_images:
				if im == light:
					im = lknightd
				else:
					im = dknightd
			elif btp == 'N' and b_images:
				if im == light:
					im = lknight
				else:
					im = dknight
			elif btp == 'k':
				if im == light and b_images:
					im = lkingd
				elif b_images:
					im = dkingd
			elif btp == 'K':
				if im == light and b_images:
					im = lking
				elif b_images:
					im = dking
			elif btp == 'q' and b_images:
				if im == light:
					im = lqueend
				else:
					im = dqueend
			elif btp == 'Q' and b_images:
				if im == light:
					im = lqueen
				else:
					im = dqueen

		return (alt_txt,im)
			
	def display(s):
		try:
			for h in range(1,BOARD_FILES + 1):
				tkinter.Label(s.boardpane, text = chr(ord ("A")+h-1), borderwidth=0, height = 3 ).grid(row=0, column = h)
			for r in range(1,BOARD_RANKS + 1):
				tkinter.Label(s.boardpane, text= str((BOARD_RANKS + 1)-r), borderwidth=0, width = 5).grid(row=r, column=0)
				for c in range(1,BOARD_FILES + 1):
					# put the buttons in the array on the grid
					s.GUIboard[r-1][c-1].grid(row=r,column=c)
				tkinter.Label(s.boardpane, text= str((BOARD_RANKS + 1)-r), borderwidth=0, width = 5 ).grid(row=r, column=BOARD_FILES + 1)
			for h in range(1,BOARD_FILES + 1):
				tkinter.Label(s.boardpane, text = chr(ord ("A")+h-1), borderwidth=0, height = 3 ).grid(row=BOARD_RANKS + 1, column = h)
		except:
			print("ChessMainWnd::display : Unexpected exception: ",sys.exc_info()[:2])
			
	def button_click(s):
		try:
			# calculating from window parameters what square is being clicked
			y = s.winfo_pointery()
			x = s.winfo_pointerx()
			rx = s.winfo_rootx()
			ry = s.winfo_rooty()
			hx = s.winfo_reqwidth()
			hy = s.winfo_reqheight()
			
			borderx = int((hx - BOARD_WIDTH - s.l1.winfo_reqwidth())/2)
			bordery = int((hy - BOARD_WIDTH)/2)
			
			dx = x-rx
			dy = y-ry
			
			cl = int((dx-borderx)/BUTTON_WIDTH)
			rw = int((dy-bordery)/BUTTON_WIDTH)
			
			#is this ours?
			if not s.gm.is_ours(position(rw,cl),s.gm.cplayer) and \
				s.selectionstate == s.NO_SELECTION:
				pass
			elif s.selectionstate == s.NO_SELECTION:
				s.GUIboard[rw][cl]['bg'] = 'red'
				s.selectionstate = s.FROM_SELECTED
				s.GUImovestart = position(rw, cl)
			elif s.selectionstate == s.FROM_SELECTED:
				if s.GUImovestart.row == rw and s.GUImovestart.col == cl:
					#deselect the move
					s.GUImovestart.row = -1
					s.GUImovestart.col = -1
					s.selectionstate = s.NO_SELECTION
					s.GUIboard[rw][cl]['bg'] = 'grey'
				else:
					s.GUIboard[rw][cl]['bg'] = 'red'
					s.selectionstate = s.TO_SELECTED
					s.GUImoveend = position(rw, cl)
					if s.move():
						s.display_move()
					s.selectionstate = s.NO_SELECTION
					s.GUIboard[s.GUImovestart.row][s.GUImovestart.col]['bg'] = 'grey'
					s.GUIboard[s.GUImoveend.row][s.GUImoveend.col]['bg'] = 'grey'
					s.GUImovestart.row = -1
					s.GUImovestart.col = -1
					s.GUImoveend.row = -1
					s.GUImoveend.col = -1
					
			# generate a TurnChange event - useful in allowing the computer to play moves
			s.event_generate("<<TurnChange>>", when="tail")
		except:
			print("ChessMainWnd::button_click : Unexpected exception: ",sys.exc_info()[:2])
		
	def enable_our_positions(s):
		for row in range(len(s.GUIboard)):
			for col in range(len(row)):
				if s.gm.is_ours(position(row, col), s.gm.cplayer):
					s.GUIboard[row][col]['state'] == ENABLED
				else:
					s.GUIboard[row][col]['state'] == DISABLED
					
	def play(s):
		try:
			if s.gm.b_game_over == False:
				s.gm.computer_turn(gm.cplayer)# finds a move and makes it
				s.GUImovestart.row = s.gm.players[s.gm.cplayer].last_move.start_pos.row
				s.GUImovestart.col = s.gm.players[s.gm.cplayer].last_move.start_pos.col
				s.GUImoveend.row = s.gm.players[s.gm.cplayer].last_move.end_pos.row
				s.GUImoveend.col = s.gm.players[s.gm.cplayer].last_move.end_pos.col
				
				cmd = s.gm.create_move(s.GUImovestart, s.GUImoveend)
				
				s.execute_move(cmd)
				s.display_move()
				
				s.selectionstate = s.NO_SELECTION
				s.GUImovestart.row = -1
				s.GUImovestart.col = -1
				s.GUImoveend.row = -1
				s.GUImoveend.col = -1
				
				# generate a TurnChange event - useful in allowing the computer to play moves
				s.event_generate("<<TurnChange>>", when="tail")
		except:
			print("ChessMainWnd::play : Unexpected exception: ",sys.exc_info()[:2])
			
	def display_move(s):
		try:
			alt_txt, im = s.set_square_image(s.gm.cboard.grid[s.GUImovestart.row][s.GUImovestart.col], \
				s.GUImovestart.row, s.GUImovestart.col)
			if b_images:		
				s.GUIboard[s.GUImovestart.row][s.GUImovestart.col]['image'] = im
				s.GUIboard[s.GUImovestart.row][s.GUImovestart.col]['text'] = ""
			else:
				s.GUIboard[s.GUImovestart.row][s.GUImovestart.col]['image'] = None
				s.GUIboard[s.GUImovestart.row][s.GUImovestart.col]['text'] = alt_txt
				b = tkinter.Button(s.boardpane, text = alt_txt, borderwidth=0, bd = 0, bg = "grey", command = s.ButtonClick, highlightcolor = "red" )
			
			alt_txt, im = s.set_square_image(s.gm.cboard.grid[s.GUImoveend.row][s.GUImoveend.col], \
				s.GUImoveend.row, s.GUImoveend.col)
			if b_images:		
				s.GUIboard[s.GUImoveend.row][s.GUImoveend.col]['image'] = im
				s.GUIboard[s.GUImoveend.row][s.GUImoveend.col]['text'] = ""
			else:
				s.GUIboard[s.GUImoveend.row][s.GUImoveend.col]['image'] = None
				s.GUIboard[s.GUImoveend.row][s.GUImoveend.col]['text'] = alt_txt					
			s.display()
			#if debug: s.gm.print_board()
		except:
			print("ChessMainWnd:display_move : Unexpected exception: ",sys.exc_info()[:2])
		
	def execute_move(s, cmd):
		#common to human and computer moves
		try:
			score = [1]
			score[0] = 0
			s.gm.cplayer = 1 - s.gm.cplayer
			if s.gm.in_check(gm.cplayer, score, position(), position(), None):
				s.l2text.set("CHECK")
			if s.gm.in_check_mate(gm.cplayer, False):
				s.l2text.set("CHECK MATE : " + str(s.gm.players[1-s.gm.cplayer].name) + " wins")
				messagebox.showinfo("CHECK MATE",str(s.gm.players[1-s.gm.cplayer].name) + " wins")
				s.gm.b_game_over = True
				s.gm.players[0].b_computer = False
				s.gm.players[1].b_computer = False
			elif s.gm.is_stalemate():
				s.l2text.set ("The game is A DRAW - the same move has been made three times now.")
				s.gm.b_game_over = True
				s.gm.players[0].b_computer = False
				s.gm.players[1].b_computer = False
			elif s.gm.cplayer == 1:
				s.gm.turn += 1
			if gm.turn > MAX_TURNS:
				messagebox.showinfo("DRAW","The game is a draw - " + str(MAX_TURNS) + " moves have been made without victory.")
				s.gm.b_game_over = True
				s.gm.players[0].b_computer = False
				s.gm.players[1].b_computer = False
			
			s.l1text.set(s.game_details())
			s.l2text.set("(" + str(s.gm.players[1-s.gm.cplayer].name) +"'s move: " + cmd + ")")
		except:
			print("ChessMainWnd::execute_move : Unexpected exception: ",sys.exc_info()[:2])
				
	def move(s):
		try:
			if s.gm.b_game_over == False:
				cmd = s.gm.create_move(s.GUImovestart, s.GUImoveend)
				if s.gm.validate_move(cmd, s.gm.cplayer):
					s.gm.move_piece(cmd, s.gm.cplayer)
					s.execute_move(cmd)
					return True
			return False
			#invalid move
		except:
			print("ChessMainWnd::move : Unexpected exception: ",sys.exc_info()[:2])

# GLOBALS -----------------------------------------------------------

#debug control - set to False to remove debug messages
debug = False
GUI = True


def build_helpstring()	:
	hs = ""
	if not GUI:
		hs += "\n"
	hs += "Chess\n\n"
	hs += "Written by Jamie Mitchinson\n"
	
	if not GUI:
		hs += "\n----\n"
		hs += "All moves can be expressed in form a1-b2, where the first pair is the source\n"
		hs += "position and the second pair represents the destination. Note that the castling\n"
		hs += "move can be attempted by moving the king two spaces - e.g. a kingside castling\n"
		hs += "could be attempted by e1-g1 or e8-g8. The move of the rook is then implicit.\n\n"
	else:
		hs += "\n"
	if GUI:
		hs += "Menu commands are:\n\n"
		hs += "computer control - computer takes over as this player.\n"
		hs += "player control - user takes control over the OTHER player.\n"
		hs += "play computer move - let the computer play the move.\n\n"
	else:
		hs += "Commands are:\n\n"
		hs += "computer - computer takes over as this player.\n"
		hs += "me - user takes control over the other player.\n"
		hs += "play - let the computer play the move.\n\n"
	
	hs += "open\t- loads a saved game. Only one saved position is allowed.\n"
	hs += "save\t- Saves a game. This will save over any previous saved game.\n"
	hs += "new\t- New game.\n"
	hs += "exit\t- Exit the program.\n"
	hs += "stats\t- Shows game statistics.\n\n"
	return hs

def trace(s):
	if debug:
		print(s)
		
def user_input():
	cmd = input("\n> ")
	cmd = cmd.lower()
	return cmd
		
def to_endline( end_pos, player):
	return end_pos.row == (1-player)*(BOARD_RANKS-1)	

def off_backline(our_pos, end_pos, distance, player):
	if (our_pos.row == int(player*(BOARD_RANKS-1))) and (abs(end_pos.row - our_pos.row) >= distance):
		return True
	else:
		return False	
		
def get_this_dir():
	path = os.path.dirname(os.path.realpath(__file__)) + "\\"
	return path
				
if GUI:
	top = tkinter.Tk()	
	here = get_this_dir()
	
	b_images = True
	try:
		dark = tkinter.PhotoImage(file = here + 'darksquare.gif')
		light = tkinter.PhotoImage(file = here + 'lightsquare.gif')
		lpawn = tkinter.PhotoImage(file = here + 'lightpawn.gif')
		lpawnd = tkinter.PhotoImage(file = here + 'lightpawnD.gif')
		dpawn = tkinter.PhotoImage(file = here + 'darkpawn.gif')
		dpawnd = tkinter.PhotoImage(file = here + 'darkpawnD.gif')
		lrook = tkinter.PhotoImage(file = here + 'lightrook.gif')
		lrookd = tkinter.PhotoImage(file = here + 'lightrookD.gif')
		drook = tkinter.PhotoImage(file = here + 'darkrook.gif')
		drookd = tkinter.PhotoImage(file = here + 'darkrookD.gif')
		lknight = tkinter.PhotoImage(file = here + 'lightknight.gif')
		lknightd = tkinter.PhotoImage(file = here + 'lightknightD.gif')
		dknight = tkinter.PhotoImage(file = here + 'darkknight.gif')
		dknightd = tkinter.PhotoImage(file = here + 'darkknightD.gif')
		lbishop = tkinter.PhotoImage(file = here + 'lightbishop.gif')
		lbishopd = tkinter.PhotoImage(file = here + 'lightbishopD.gif')
		dbishop = tkinter.PhotoImage(file = here + 'darkbishop.gif')
		dbishopd = tkinter.PhotoImage(file = here + 'darkbishopD.gif')
		lking = tkinter.PhotoImage(file = here + 'lightking.gif')
		lkingd = tkinter.PhotoImage(file = here + 'lightkingD.gif')
		dking = tkinter.PhotoImage(file = here + 'darkking.gif')
		dkingd = tkinter.PhotoImage(file = here + 'darkkingD.gif')
		lqueen = tkinter.PhotoImage(file = here + 'lightqueen.gif')
		lqueend = tkinter.PhotoImage(file = here + 'lightqueenD.gif')
		dqueen = tkinter.PhotoImage(file = here + 'darkqueen.gif')
		dqueend = tkinter.PhotoImage(file = here + 'darkqueenD.gif')
	except:
		# any failure: no panic - revert to simple text descriptions
		messagebox.showinfo("Display problem","One or more bitmaps could be found - pieces will be represented instead by text.")
		b_images = False
		
# -------------------------------------------------------------------

# structures

class position(object):
	row = -1
	col = -1
	def __init__(s, r = -1, c = -1):
		s.row = r
		s.col = c
	def __eq__(s, other):
		return (s.row == other.row and s.col == other.col)
	
	def __ne__(s, other):
		return not(s == other)
		
	def __lt__(s, other):
		if s.row < other.row:
			return True
		elif s.row > other.row:
			return False
		if s.col < other.col:
			return True
		elif s.col > other.col:
			return False
		else:
			return False

	def __gt__(s, other):
		return other < s
		
	def is_valid(s):
		return s.row in range(BOARD_RANKS) and s.col in range(BOARD_FILES)
		
	def __str__(s):
		return '[' + str(s.row) + ':' + str(s.col) + ']'

class pastmove(object):
	def __init__(s, start = position(), end = position()):
		s.start_pos = start
		s.end_pos = end
		
	def __eq__(s, other):
		if s == None and other == None:
			return True
		if (s == None and other != None) or \
			(s != None and other == None):
			return False
		return s.start_pos == other.start_pos and s.end_pos == other.end_pos
	
	def __ne__(s, other):
		return not(s == other)
		
	def __lt__(s, other):
		if s.start_pos < other.start_pos:
			return True
		elif s.start_pos > other.start_pos:
			return False
		if s.end_pos < other.end_pos:
			return True
		elif s.end_pos > other.end_pos:
			return False
		return False
		
	def __iter__(s):
		# explanation of this ludicrously complicated return type:
		# 1. The return must be enclosed in a tuple or list to be hashable
		# 2. The tuple or list inside can contain only ONE item - not a list (or every item will
		# 	 be considered an element in its own right)
		# 3. The one item must be a tuple of a list containing all the items in a flat format, so
		# 	 that they are counted as one item.
		
		# Might still be worth revisiting though - I have a feeling it could be simplified
		return iter(list([tuple(list([s.start_pos.row, s.start_pos.col, s.end_pos.row, s.end_pos.col]))]))
		
class pastmoves(object):
	def __init__(s, other = None):
		s.pastmove_set = Counter()
	
class board(object):
	def __init__(s, other = None):
		s.grid = [] 
		for r in range(BOARD_RANKS):  
			row = []
			for c in range(BOARD_FILES):
				if other == None:
					row.append('.') 
				else:
					row.append(other.grid[r][c])
			s.grid.append(row)
	
	def __str__(s):
		return s.grid
	
	def __eq__(s, other):
		if s is None and other is None:
			return True
		if (s is None and other is not None) or \
			(s is not None and other is None):
			return False
		for r in range(BOARD_RANKS):  
			for c in range(BOARD_FILES):
				if s.grid[r][c] != other.grid[r][c]:
					return False
		return True
		
	def __lt__(s, other):
		for r in range(BOARD_RANKS):  
			for c in range(BOARD_FILES):
				if s.grid[r][c] < other.grid[r][c]:
					return True
				elif s.grid[r][c] > other.grid[r][c]:
					return False
		return False
	
	def __ne__(s, other):
		return not(s == other)
		
	def __iter__(s):
		return iter(s.grid)

class pastboards(object):
	board_set = Counter()
	def __init__(s, other = None):
		pass

class player(object):
	b_computer = False
	pieces = list("PPPPPPPPSNBQLBNS")
	last_piece_moved = -1
	"""
	P = pawn
	E = pawn vulnerable to en passant
	R = moved rook
	S = unmoved rook
	N = knight
	B = bishop
	Q = queen
	K = moved king
	L = unmoved king
	"""	
	name = ""
	
	def __init__(s,name):
		s.last_move = pastmove()
		s.piecemoves = []
		for i in range(16):
			s.piecemoves.append(pastmoves())
		s.name = name
		s.positions = []
		s.set_pieces()
		
	def get_position(s, index):
		return s.positions(index)
		
	def push_back_pos(s, pos):
		s.positions.append(pos)
		
	def get_name(s):
		return s.name
		
	def set_name(s, n):
		name = n
		
	def set_pieces(s):
		b_computer = False
		pieces = list("PPPPPPPPSNBQLBNS")
		last_piece_moved = -1
		name = ""
	
class gameobject(object):
	def __init__(s, other = None):
		if (other == None):
			s.b_GUIinitialised = False
			s.cboard = board()
			s.past_boards = pastboards()
			s.turn = 1
			s.players = []
			s.players.append(player("Black"))
			s.players.append(player("White"))
			s.cplayer = 1
			s.b_game_over = False
		else:
			s.cboard = board(other.cboard)
			s.past_boards = other.past_boards
			s.turn = other.turn
			s.players = other.players
			s.players[0] = other.players[0]
			s.players[1] = other.players[1]
			s.cplayer = other.cplayer
			s.b_game_over = False
		
	def print_all_variables(s):
		# debug only
		print ("Turn: " + str(s.turn))
		print ("Current player number: " + str(s.cplayer))
		for each_player in s.players:
			print (each_player.name)
		print (s.cboard.grid)
		print("")
	
	def print_pieces(s):	
		for each_player in s.players:
			print(each_player.get_name())
			for j in range(len(each_player.pieces)):
				print (each_player.pieces[j] + " " + str(each_player.positions[j].row) + " " + str(each_player.positions[j].col) )
			print("")
	
	def print_pastmoves(s):	
		for each_player in s.players:
			print(each_player.get_name())
			for k in range(len(each_player.piecemoves)):
				print("Piece ",k)
				for l in each_player.piecemoves[k].pastmove_set.elements():
					print(l, " x ", each_player.piecemoves[k].pastmove_set[l])
			print("")
			
	def basic_type(s, p):
		# for those pieces that could be used in unusual moves (en passant, castling), we record the pieces
		# with a different character to track this. But we still want to know what they are, fundamentally.
		if p == 'L': p = 'K'
		elif p == 'E': p = 'P'
		elif p == 'S': p = 'R'
		elif p == 'l': p = 'k'
		elif p == 'e': p = 'p'
		elif p == 's': p = 'r'
		return p	
			
	def validate_move(s, cmd, iplayer):
		if len(cmd) != 5:
			print("\nThat move is not allowed.\n")
			return False
		start_pos = end_pos = position()
		trace("validate_move calling get_move_coords: " + cmd)
		# TO DO: remove above
		start_pos, end_pos = s.get_move_coords(cmd)
		
		if not start_pos.is_valid() or not end_pos.is_valid():
			print("\nThat move is not allowed.\n")
			return False
		
		ourpiece = -1
		theirpiece = -1
		if s.cboard.grid[start_pos.row][start_pos.col] == '.':
			print("\nThere's no piece to move from there.\n")
			return False
		else:# find out if it's one of ours
			for i in range(len(s.players[iplayer].positions)):
				if s.players[iplayer].positions[i] == start_pos:
					ourpiece = i
					break
			if ourpiece == -1:
				print("\nThat's not your piece to move...\n")
				return False
		
		b_dest_empty = True
		if s.cboard.grid[end_pos.row][end_pos.col] != '.':
			b_dest_empty = False
			for i in range (len(s.players[1-iplayer].positions)):
				if s.players[1-iplayer].positions[i] == end_pos:
					theirpiece = i
					break
			if theirpiece == -1:
				print("\nThat position is occupied by one of your pieces already.\n")
				return False
			
		piece = s.cboard.grid[start_pos.row][start_pos.col]
		destination = s.cboard.grid[end_pos.row][end_pos.col]
		dummyscore = [1]
		dummyscore[0] = 0

		# pawns
		if s.basic_type(piece) == 'P': # en passant pawn
			# pawns can move 2 down from 2nd row, or 1, or 1 diagonally forward if there is another piece in the way
			if iplayer == 0 and (start_pos.row == 1 and end_pos.row == 3 and start_pos.col == end_pos.col):
				#valid - 2 moves forward, if unoccupied
				if (not b_dest_empty) or s.cboard.grid[int((start_pos.row + end_pos.row)/2)][start_pos.col] != '.':
					if not GUI: print("\nNot a valid move.\n")
					return False
				else:
					return not s.in_check(iplayer, dummyscore, start_pos, end_pos, None) # can't leave ourself in check
			elif iplayer == 1 and start_pos.row == 6 and end_pos.row == 4 and start_pos.col == end_pos.col:
				#valid -  2 moves forward, if unoccupied
				if (not b_dest_empty) or s.cboard.grid[int((start_pos.row + end_pos.row)/2)][start_pos.col] != '.':
					if not GUI: print("\nNot a valid move.\n")
					return False
				else:
					return not s.in_check(iplayer, dummyscore, start_pos, end_pos, None) # can't leave ourself in check
			elif (iplayer == 0 and (end_pos.row - start_pos.row == 1)) or \
				(iplayer == 1 and (start_pos.row - end_pos.row == 1)):
				# could be valid
				if  (abs(end_pos.col - start_pos.col) == 1 and destination != '.') or \
					(abs(end_pos.col - start_pos.col) == 1 and destination == '.' and s.cboard.grid[end_pos.row + (iplayer*2 -1)][end_pos.col] == 'E') :
					#diagonal move, either to take a piece directly or to take a pawn on passant
					# move the right piece in the positions list, if it's one of theirs
					for i in range (len(s.players[1-iplayer].positions)):
						if s.players[1-iplayer].positions[i] == end_pos:
							return not s.in_check(iplayer, dummyscore, start_pos, end_pos, None) # can't leave ourself in check
						if s.players[1-iplayer].positions[i].col == end_pos.col and \
							s.players[1-iplayer].positions[i].row == end_pos.row +(iplayer*2)-1 :
							if s.players[1-iplayer].pieces[i] == 'E':
								return not s.in_check(iplayer, dummyscore, start_pos, end_pos, None) # can't leave ourself in check
								# an en passant diagonal move
					if not GUI: print("\nNot a valid move.\n")
					return False
				elif end_pos.col == start_pos.col:
					#valid -  1 move forward, if unoccupied
					if not b_dest_empty:
						if not GUI: print("\nNot a valid move.\n")
						return False
					else:
						return not s.in_check(iplayer, dummyscore, start_pos, end_pos, None) # can't leave ourself in check
				else:
					if not GUI: print("\nNot a valid move.\n")
					return False
			else:
				if not GUI: print("\nNot a valid move.\n")
				return False

		# knight
		# 2 x 1, anywhere
		if piece == 'N':
			if  (abs(end_pos.col - start_pos.col) == 1 and abs(end_pos.row - start_pos.row) == 2)  or \
				(abs(end_pos.col - start_pos.col) == 2 and abs(end_pos.row - start_pos.row) == 1) :
				if b_dest_empty or (not theirpiece == -1):
					return not s.in_check(iplayer, dummyscore, start_pos, end_pos, None) # can't leave ourself in check
				else:
					return False
			else:
				return False

		# rook
		if s.basic_type(piece) == 'R':  #unmoved rook
			if end_pos.col == start_pos.col or end_pos.row == start_pos.row: # can't both be equal anyway
				# direction is OK, at least. Now check what's in the way...
				distance = max( abs(end_pos.col - start_pos.col), abs(end_pos.row - start_pos.row) )
				if s.check_path(start_pos, end_pos, distance, b_dest_empty, theirpiece, iplayer, False):
					return not s.in_check(iplayer, dummyscore, start_pos, end_pos, None) # can't leave ourself in check
			return False

		# bishop
		if piece == 'B':
			if  abs(end_pos.col - start_pos.col) == abs(end_pos.row - start_pos.row) : # horizontal distance = vertical
				# direction is OK, at least. Now check what's in the way...
				distance = abs(end_pos.col - start_pos.col)
				if s.check_path(start_pos, end_pos, distance, b_dest_empty, theirpiece, iplayer, False):
					return not s.in_check(iplayer, dummyscore, start_pos, end_pos, None) # can't leave ourself in check
			return False

		# queen or king
		if piece == 'Q' or s.basic_type(piece) == 'K': #unmoved king
			if  abs(end_pos.col - start_pos.col) == abs(end_pos.row - start_pos.row) or	\
				(end_pos.col == start_pos.col or end_pos.row == start_pos.row) :		
				# direction is OK, at least. Now check what's in the way...
				distance = max(  abs(end_pos.col - start_pos.col) , \
					max(abs(end_pos.col - start_pos.col), abs(end_pos.row - start_pos.row)) )	# if h/v
				if distance == 1 or piece == 'Q': # Kings can only move one space
					if s.check_path(start_pos, end_pos, distance, b_dest_empty, theirpiece,iplayer, False):
						return not s.in_check(iplayer, dummyscore, start_pos, end_pos, None) # can't leave ourself in check
				elif distance == 2 and end_pos.row == start_pos.row and (start_pos.row == iplayer*(BOARD_RANKS-1)):
					# this may be a castling attempt:
					# Castling is permissible if and only if all of the following conditions hold:
					# 1. The king and the chosen rook are on the player's first rank.
					# 2. Neither the king nor the chosen rook have previously moved.
					#    (Use L for an unmoved king, and S for an unmoved rook)
					rook_pos = position()
					if s.cboard.grid[iplayer*(BOARD_RANKS-1)][0] == 'S' and s.cboard.grid[iplayer*(BOARD_RANKS-1)][4] == 'L' and start_pos.col == 4 and end_pos.col == 2:
						rook_pos.col = 0
					elif s.cboard.grid[iplayer*(BOARD_RANKS-1)][7] == 'S' and s.cboard.grid[iplayer*(BOARD_RANKS-1)][4] == 'L' and start_pos.col == 4 and end_pos.col == 6:
						rook_pos.col = 7
					else:
						return False # one or both of the king and the rook have moved from their starting position (even if they've since returned
					rook_pos.row = iplayer*(BOARD_RANKS-1)

					# 3. There are no pieces between the king and the chosen rook (NOT merely where the king moves to.)			
					if not s.check_path(start_pos, rook_pos, distance, b_dest_empty, theirpiece, iplayer,False):
						return False
					
					# 4. The king is not currently in check.
					if s.in_check(iplayer, dummyscore, position(), position(), None):
						return False

					# 5. The king does not pass through a square that is attacked by an enemy piece.
					#    - Modify check_path to call in_check for every square it passes through...
					if not s.check_path(start_pos, end_pos, distance, b_dest_empty, theirpiece, iplayer, True): # b_checkcheck
						return False

					# 6. The king does not end up in check. (True of any legal move.)
					return not s.in_check(iplayer, dummyscore, start_pos, end_pos, None) # end_pos is the new king pos, NOT the rook pos...
					# Note : I believe the rook manoeuvre will always be valid now, because if the king's path is clear, so must be the rook's.
			return False
	
	def show_help(s):
		helptext = build_helpstring() # this allows the GUI to use the same formatted text
		print(helptext)
		
	def get_move_coords(s, cmd):
		start = position()
		end = position()
		#trace("get_move_coords: " + cmd); # TO DO: remove
		try:
			cmd = cmd.lower()
			if cmd[1].isdigit() and cmd[4].isdigit():
				start.row = BOARD_RANKS - int(cmd[1])
				end.row = BOARD_FILES - int(cmd[4])
				start.col = ( ord(cmd[0]) - ord('a') )
				end.col = ( ord(cmd[3]) - ord('a') )
		except:				
			print("Unexpected error in command or coordinates: ",sys.exc_info()[:2])
		return (start, end)
		
	def get_capture_value(s, piece):
		# add scores for takeover of their piece
		if s.basic_type(piece) =='P':
			value = 3
		elif piece == 'N':
			value = 5
		elif s.basic_type(piece) ==  'R':
			value = 6
		elif piece == 'B':
			value = 7
		elif piece == 'Q':
			value = 9
		elif s.basic_type(piece) == 'K':
			value = 10
		# not scoring an en passant move - but I think we could do that outside, as it's only possible to take a pawn anyway
		else:
			value = 0
			# may be a blank space
		return value
			
	def move_piece(s, cmd, iplayer, b_AI = False):
		start_pos = end_pos = position()
		trace("move_piece calling get_move_coords: " + cmd)
		# TO DO: remove above
		start_pos, end_pos = s.get_move_coords(cmd)
		b_stalemate = False
		ourindex = -1
		# move the right piece in the positions list
		for i in range(len(s.players[iplayer].positions)):
			if s.players[iplayer].positions[i] == start_pos:
				s.players[iplayer].positions[i] = end_pos
				ourindex = i
				storedboard = board(s.cboard)
				# To use these boards in a Counter object, they must be immutable. So
				# we're destroying all list-ness by flattening it, then making a tuple:
				storedboard = [item for sublist in storedboard for item in sublist]
				storedboard = tuple(storedboard)
				s.past_boards.board_set.update(storedboard)
				pm = pastmove(start_pos, end_pos)
				pm = tuple(pm)
				s.players[iplayer].piecemoves[i].pastmove_set.update(pm)
				break
		
		# If we've taken a piece...
		for each_pos in s.players[1-iplayer].positions:
			if each_pos == end_pos:
				pos = position()# i.e. invalidate it
				each_pos.row = -1
				each_pos.col = -1
				break

		# move the piece on the board:
		piece = s.cboard.grid[start_pos.row][start_pos.col]
		#orig_dest = s.cboard.grid[end_pos.row][end_pos.col]
		s.cboard.grid[start_pos.row][start_pos.col] = '.'
		assert (s.basic_type(s.cboard.grid[end_pos.row][end_pos.col]) != 'K') # we should never have reached this point
		s.cboard.grid[end_pos.row][end_pos.col] = piece
		if debug or not GUI: print("Moved.")
		s.players[iplayer].last_piece_moved = ourindex
		
		# if the king is moving from its start position...
		if s.players[iplayer].pieces[ourindex] == 'L':
			s.players[iplayer].pieces[ourindex] = 'K'
			s.cboard.grid[end_pos.row][end_pos.col] = 'K'
			# is this a castling?
			if abs(start_pos.col - end_pos.col) == 2:
				# castling - we've moved the king, and now we have to move the rook to the space between
				if start_pos.col == 4 and end_pos.col == 6: # kingside rook - position 16
					s.players[iplayer].pieces[15] = 'R'
					s.players[iplayer].positions[15].col = 5
					s.cboard.grid[start_pos.row][5] = 'R'
					s.cboard.grid[start_pos.row][7] = '.'
				else: # queenside
					s.players[iplayer].pieces[8] = 'R'
					s.players[iplayer].positions[8].col = 3
					s.cboard.grid[start_pos.row][3] = 'R'
					s.cboard.grid[start_pos.row][0] = '.'
		
		# if the rook is moving from its start position...
		if s.players[iplayer].pieces[ourindex] == 'S':
			s.players[iplayer].pieces[ourindex] = 'R'
			s.cboard.grid[end_pos.row][end_pos.col] = 'R'
		
		# check for an en passant move:
		v_dir = 1 # down
		if iplayer == 1:
			v_dir = -1 # up
		if  piece == 'P' and s.cboard.grid[end_pos.row - v_dir][end_pos.col] == 'E' :
			# capture the opponent's piece, en passant:
			s.cboard.grid[end_pos.row - v_dir][end_pos.col] = '.'
			print("Pawn captured, en passant.")
			for each_pos in s.players[1-iplayer].positions:
				if (each_pos.row == end_pos.row - v_dir) and (each_pos.col == end_pos.col):
					each_pos.row -= 1
		
		# revert en passant - if any of the opponent's pawns are still en passant from the last move, then they will now revert to their normal status.
		for i in range(len(s.players[1-iplayer].positions)):
			if  s.players[1-iplayer].pieces[i] == 'E':
				s.players[1-iplayer].pieces[i] = 'P'
				if s.players[1-iplayer].positions[i].row in range(BOARD_RANKS):
					s.cboard.grid[s.players[1-iplayer].positions[i].row][s.players[1-iplayer].positions[i].col] = 'P'
				
		# has our pawn become en passant in this move?
		if  piece == 'P' and ((iplayer == 0 and end_pos.row == 3) or (iplayer == 1 and end_pos.row == 4)) :
			# if this position was achieved with a 2 square move...
			if abs(start_pos.row - end_pos.row) == 2:
				# and there is any adjacent opposing piece...
				for each_pos in s.players[1-iplayer].positions:
					if  (each_pos.row == end_pos.row) and abs(each_pos.col - end_pos.col) == 1 :
						s.cboard.grid[end_pos.row][end_pos.col] = 'E'    #signifies en passant will be restored at the start of the next turn
						s.players[iplayer].pieces[ourindex] = 'E'		# ditto - allows the state to be saved
		
		# Can a pawn be promoted?
		if  piece == 'P' and ((iplayer == 0 and end_pos.row == (BOARD_RANKS-1)) or (iplayer == 1 and end_pos.row == 0)) :
			# Promotion
			if b_AI == True:
				s.cboard.grid[end_pos.row][end_pos.col] = 'Q'
				for i in range(len(s.players[iplayer].pieces)):
					if s.players[iplayer].positions[i] == end_pos:
						s.players[iplayer].pieces[i] = s.cboard.grid[end_pos.row][end_pos.col]
				print("The pawn has been promoted.")
			else:
				print("The pawn has been promoted. What piece do you want to convert it to? You may choose a knight, rook, bishop or queen.")
				b_converted = False
				while not b_converted:
					input = user_input()
					input = input.lower()

					if input == "queen":
						s.cboard.grid[end_pos.row][end_pos.col] = 'Q'
					elif input == "bishop":
						s.cboard.grid[end_pos.row][end_pos.col] = 'B'
					elif input == "rook":
						s.cboard.grid[end_pos.row][end_pos.col] = 'R'
					elif input == "knight":
						s.cboard.grid[end_pos.row][end_pos.col] = 'N'
					if s.cboard.grid[end_pos.row][end_pos.col] != 'P':
						b_converted = True
					
					for i in range(len(s.players[iplayer].pieces)):
						if s.players[iplayer].positions[i] == end_pos:
							s.players[iplayer].pieces[i] = s.cboard.grid[end_pos.row][end_pos.col]
				print("Thank you. The pawn has been promoted.")
		s.print_board()
		s.players[iplayer].last_move.end_pos.row = end_pos.row
		s.players[iplayer].last_move.end_pos.col = end_pos.col
		s.players[iplayer].last_move.start_pos.row = start_pos.row
		s.players[iplayer].last_move.start_pos.col = start_pos.col
		
	def check_path(s, start_pos, end_pos, distance, \
		b_dest_empty, theirpiece, player_num, b_checkcheck):
		try:
			if (distance < 1):
				trace("ERROR: Distance = " + str(distance) + " start_pos = " + str(start_pos) + " end_pos = " + str(end_pos))		
			# any direction
			dir_down = (end_pos.row - start_pos.row) / distance # i.e. can be -1, 0, or 1
			dir_right = (end_pos.col - start_pos.col) / distance 
			
			trace("checkPath: " +str(start_pos.row) +  ":" + str(start_pos.col) + " - " + str(end_pos.row) + ":" + str(end_pos.col) + " dirDown=" + str(dir_down) + " dir_right=" + str(dir_right))
			# TO DO: remove above

			for i in range(1,distance):
				col_movement = int(dir_right * i)
				row_movement = int(dir_down * i)
				test = position(start_pos.row + row_movement,start_pos.col + col_movement)
				if not test.is_valid():
					break
				if s.cboard.grid[start_pos.row + row_movement][start_pos.col + col_movement] != '.':
					return False # can't take the piece if it's only on the way, and it can't be our own
				if b_checkcheck:
					# further check required - this position may be empty, but for the castling we need to
					# know it cannot be attacked by another piece. In effect, we test as if the king were
					# in that space.
					dummyscore = [1]
					dummyscore[0] = 0
					if s.in_check(iplayer, dummyscore, start_pos, end_pos, None):
						return False
		except:
			print("check_path : Unexpected exception: ",sys.exc_info()[:2])				
		# final check - the destination square:
		if b_dest_empty or theirpiece != -1:
			return True
		else:
			return False
		
	def common_scoring(s, b_in_check, hiscore, check_direction, our_value, their_value, king_value, bAI, iplayer):
		try:
			THEM_AGAINST_KING,THEM_AGAINST_CURRENT,THEM_AGAINST_PIECE,US_AGAINST_KING,US_AGAINST_PIECE,NO_MORE = range(6)		
			if check_direction == THEM_AGAINST_KING:
				b_in_check = True
				hiscore -= 500
			if check_direction == THEM_AGAINST_KING or check_direction == THEM_AGAINST_PIECE:
				hiscore -= our_value * (1 + (our_value >= 9))
				# TO DO: if this is the only place our_value is used - we should instead just change the value of Q or K at source 
			if check_direction == THEM_AGAINST_CURRENT:
				hiscore += our_value * (1 + (our_value >= 9))
			if check_direction == US_AGAINST_KING:
				if s.get_num_pieces(iplayer) > 5:
					hiscore -= int(king_value/1.4) # don't provide too much encouragement to check before it's going to work
			if check_direction == US_AGAINST_PIECE:
				hiscore += int(their_value / 1.5)	
		except:
			print("Unexpected error in common_scoring: ",sys.exc_info()[:2])
			
		return (bAI and not b_in_check)
		
	def in_check(s, player, hisc, start_pos, end_pos, gm):
		trace("inCheck: " + str(start_pos.row) + ":" + str(start_pos.col) + " - " + str(end_pos.row) + ":" + str(end_pos.col))
		# make a copy of the board and positions arrays, only modified so that any tentative move is overlaid.

		# simulating pass by reference for the score, because ints are immutable (wrapping it in an 1-element list]
		try:
			hiscore = hisc[0] # award 10 pts for a move that takes king - test check
			
			iplayer = player # allows us to play about with the player without causing confusion outside
			bAI = False # whether we are using this to grade a computer's move
			if hiscore > 0:
				bAI = True
			b_in_check = False
			
			if (gm is None):
				pm = copy.deepcopy(s)# doesn't seem to do a deep copy at all - no improvement
				pm.players = copy.deepcopy(s.players) # OK now
				pm.cboard = copy.deepcopy(s.cboard)
				# grid can't be deep copied this way
				pm.cboard.grid = []
				
				for y in range(len(s.cboard.grid)):
					for x in range(len(s.cboard.grid)):
						row = []
						row.append(s.cboard.grid[y][x])	
					pm.cboard.grid.append(row)
					# Note: Doesn't copy. The players array has this information though.
				
				#assert(id(pm.cboard.grid[1][0]) != id(s.cboard.grid[1][0]) ) # TO DO: restore when we tidy this up
				assert(id(pm.players[1]) != id(s.players[1]) )
				assert(id(pm.players[1].positions[0]) != id(s.players[1].positions[0]) )
				# if either of these assert, then either the board, players or positions
				# are not being copied properly
				
				pm.players = copy.deepcopy(s.players)
				pm.cboard.grid = copy.deepcopy(s.cboard.grid)
			else:
				pm = gameobject(gm)
				
			# i.e. either construct a copy of the actual game, or a simulated game passed in.
			THEM_AGAINST_KING,THEM_AGAINST_CURRENT,THEM_AGAINST_PIECE,US_AGAINST_KING,US_AGAINST_PIECE,NO_MORE = range(6)		
			# 0 THEM_AGAINST_KING							 					M:1 \
			# 1 THEM_AGAINST_CURRENT - the opportunity cost (of not moving)		M:1 \
			# 2 THEM_AGAINST_PIECE, - against the piece we've just moved		M:1 \
			# 3 US_AGAINST_KING, - check										M:1 \
			# 4 US_AGAINST_PIECE, - against other pieces 						1:M \
			# 5 NO_MORE

			nullpos = position() # for comparison
			king_value = s.get_capture_value('K')
						
			if start_pos != nullpos:
				# add scores for takeovers
				our_value = s.get_capture_value(pm.cboard.grid[start_pos.row][start_pos.col])
				their_value = s.get_capture_value(pm.cboard.grid[end_pos.row][end_pos.col])
								
				hiscore += their_value * 2 #pieces taken immediately have to be more valuable than those could be taken in the next turn...
				# add the proposed move to the copy of the board
				
				pm.cboard.grid[end_pos.row][end_pos.col] = pm.cboard.grid[start_pos.row][start_pos.col]
				pm.cboard.grid[start_pos.row][start_pos.col] = '.'
									
				for p_ind in range(len(pm.players[iplayer].positions)):
					if pm.players[iplayer].positions[p_ind] == start_pos:
						new_pos = position()
						new_pos.row = end_pos.row
						new_pos.col = end_pos.col
						pm.players[iplayer].positions[p_ind] = new_pos
						# At the moment this still just references end_pos (see note above),
						# meaning the array reverts back without our knowledge or permission.
						# So instead, I'm using a little code further down to compensate.
						break		
			else:
				end_pos = pm.players[iplayer].positions[12] # for when we call it to check check AFTER a move
				# required by the en passant code to show our king isn't a pawn
				assert end_pos.col in range(BOARD_FILES)
				our_value = their_value = 0
			
			# also need to remove a captured piece, if there is one.
			for each_pos in pm.players[1-iplayer].positions:
				if each_pos == end_pos:
					each_pos = position()
		
			# from this point on in the function, always use pm. syntax in front of members and function...

			check_direction = THEM_AGAINST_KING

			while check_direction != NO_MORE:
				# go through all pieces, and all their moves - if any can move on the king, return True
				# for each piece:
				if bAI == False or (check_direction == THEM_AGAINST_KING):
					target_pos = pm.players[iplayer].positions[12]		
					#if bAI == True: # TO DO: comment this line back in, as soon as we work out how to fix
									# the assignment of our piece to its new position in the array ,earlier on
					# if the piece we're proposing moving is the king, then we don't want to check against where the king WAS, but rather where the king WILL BE.
					if s.basic_type(pm.cboard.grid[end_pos.row][end_pos.col]) == 'K':
						target_pos = end_pos
				elif check_direction == THEM_AGAINST_CURRENT:
					target_pos = start_pos
				elif check_direction == THEM_AGAINST_PIECE:
					target_pos = end_pos 
				elif check_direction == US_AGAINST_KING:
					target_pos = pm.players[iplayer].positions[12] # (iplayer has been reversed at this point)
				elif check_direction == US_AGAINST_PIECE:
					target_pos = end_pos

				op_dir = iplayer * 2 -1
				index = 0
							
				for index in range(len(pm.players[1-iplayer].positions)):
					tpiece = pm.players[1-iplayer].pieces[index]
				
					op_pos = pm.players[1-iplayer].positions[index]
					if check_direction == THEM_AGAINST_CURRENT:
						op_pos = s.players[1-iplayer].positions[index]
						# use existing grid, in case the move assumes the oppo piece is taken 
					if not op_pos.is_valid():
						continue
					if check_direction == US_AGAINST_PIECE:
						# in this context op_pos represents our piece, and target_pos is the opponent's
						target_pos = op_pos
						op_pos = end_pos
						their_value = s.get_capture_value(pm.cboard.grid[target_pos.row][target_pos.col])
						tpiece = pm.cboard.grid[end_pos.row][end_pos.col]
					
					# pawns
					if s.basic_type(tpiece) == 'P':
						# for all moves, capturing or not:
						if check_direction == THEM_AGAINST_PIECE and ((target_pos.row == 0 and iplayer == 1) or (target_pos.row == (BOARD_RANKS-1) and iplayer == 0)):
							# if this will be a promotion move, the penalty should be the value of the queen
							our_value = s.get_capture_value('Q')
						if target_pos == op_pos and (check_direction == US_AGAINST_PIECE):
							# no points for taking a piece we've already taken
							pass
						elif end_pos == op_pos and (check_direction == THEM_AGAINST_KING or check_direction == THEM_AGAINST_PIECE):
							pass
							# This piece would already have been taken, therefore it can't threaten our pieces.
						# diagonal move creates check
						else:
							if (op_pos.row + op_dir == target_pos.row) and ( abs(op_pos.col - target_pos.col) == 1 ) :
								if not s.common_scoring(b_in_check, hiscore, check_direction, our_value, their_value, king_value, bAI, iplayer):
									return True
									
							# en passant move creates check
							if  (tpiece == 'E') and \
								(op_pos.row == target_pos.row) and \
								abs(op_pos.col - target_pos.col) == 1 :
								if not s.common_scoring(b_in_check, hiscore, check_direction, our_value, their_value, king_value, bAI, iplayer):
									return True
						
					# knight
					if tpiece == 'N':
						if target_pos == op_pos and (check_direction == US_AGAINST_PIECE):
							# no points for taking a piece we've already taken
							pass
						elif end_pos == op_pos and (check_direction == THEM_AGAINST_KING or check_direction == THEM_AGAINST_PIECE):
							pass
						elif (abs(op_pos.row - target_pos.row) == 1 and abs(op_pos.col - target_pos.col) == 2)  or \
							(abs(op_pos.col - target_pos.col) == 1 and abs(op_pos.row - target_pos.row) == 2) :
							if not s.common_scoring(b_in_check, hiscore, check_direction, our_value, their_value, king_value, bAI, iplayer):
								return True
						
					# rook
					if s.basic_type(tpiece) == 'R':
						if target_pos == op_pos and (check_direction == US_AGAINST_PIECE):
							# no points for taking a piece we've already taken
							pass
						elif end_pos == op_pos and (check_direction == THEM_AGAINST_KING or check_direction == THEM_AGAINST_PIECE):
							pass
						elif op_pos.col == target_pos.col or op_pos.row == target_pos.row: # can't both be equal anyway
							if op_pos == target_pos:
								continue
							# direction is OK, at least. Now check what's in the way...
							distance = max( abs(op_pos.col - target_pos.col), abs(op_pos.row - target_pos.row))
							if  pm.check_path(op_pos, target_pos, distance, False, True, iplayer, False) : # returns True if the target can be captured
								if not s.common_scoring(b_in_check, hiscore, check_direction, our_value, their_value, king_value, bAI, iplayer):
									return True
							
						# not assuming check:
						if check_direction == US_AGAINST_KING:
							if  (abs((op_pos.col - target_pos.col)) == 2 and \
								abs((op_pos.row - target_pos.row)) == 1) or \
								(abs((op_pos.col - target_pos.col)) == 2 and \
								abs((op_pos.row - target_pos.row)) == 1):
								hiscore += 2 # small incentive for a move close enough to cut the king's moves, even if it's not check
					
					# bishop
					if tpiece == 'B':
						if target_pos == op_pos and (check_direction == US_AGAINST_PIECE):
							# no points for taking a piece we've already taken
							pass
						elif end_pos == op_pos and (check_direction == THEM_AGAINST_KING or check_direction == THEM_AGAINST_PIECE):
							pass
						else:	
							if  abs(op_pos.col - target_pos.col) == abs(op_pos.row - target_pos.row) : # horizontal distance = vertical
								# direction is OK, at least. Now check what's in the way...
								distance = abs(op_pos.col - target_pos.col)
								if  pm.check_path(op_pos, target_pos, distance, False, True, iplayer, False) :
									if not s.common_scoring(b_in_check, hiscore, check_direction, our_value, their_value, king_value, bAI, iplayer):
										return True
									
						# not assuming check:
						if check_direction == US_AGAINST_KING:
							if  abs(op_pos.col - target_pos.col) == 2 and \
								 abs(op_pos.row - target_pos.row) == 2 :
								hiscore += 3 # incentive for a move close enough to cut the king's moves
							
					# queen or king
					if s.basic_type(tpiece) == 'K' or tpiece == 'Q':
						if target_pos == op_pos and (check_direction == US_AGAINST_PIECE):
							# no points for taking a piece we've already taken
							pass
						elif end_pos == op_pos and (check_direction == THEM_AGAINST_KING or check_direction == THEM_AGAINST_PIECE):
							pass
						else:
							if  abs(op_pos.col - target_pos.col) == abs(op_pos.row - target_pos.row) or \
								(op_pos.col == target_pos.col or op_pos.row == target_pos.row) :
								# direction is OK, at least. Now check what's in the way...
								assert (op_pos != target_pos)
								if (op_pos == target_pos):
									continue
								distance = max(  abs(op_pos.col - target_pos.col) ,	\
									max(abs(op_pos.col - target_pos.col), abs(op_pos.row - target_pos.row)) )	# if h/v
								if distance == 1 or tpiece == 'Q': # Kings can only move one space
									if  pm.check_path(op_pos, target_pos, distance, False, True, iplayer, False) :
										if not s.common_scoring(b_in_check, hiscore, check_direction, our_value, their_value, king_value, bAI, iplayer):
											return True
									
						# not assuming check:
						if check_direction == US_AGAINST_KING:
							if  abs(op_pos.col - target_pos.col) == 2 or \
								abs(op_pos.row - target_pos.row) == 2 :
								hiscore += 2 # incentive for a move close enough to cut the king's moves
			
				if bAI == True:
					check_direction += 1
					if check_direction == US_AGAINST_KING:
						iplayer = 1-iplayer
					elif check_direction == US_AGAINST_PIECE:
						iplayer = 1-iplayer
					trace("State = " + str(check_direction) + ", player = " + str(iplayer))
				else:
					check_direction = NO_MORE
			
			# penalise the move if we moved the same piece in the previous turn
			if bAI:
				if s.players[iplayer].pieces[s.players[iplayer].last_piece_moved] == pm.cboard.grid[start_pos.row][start_pos.col]:
					hiscore -=3
					if pm.cboard.grid[start_pos.row][start_pos.col] == 'Q' and s.get_num_pieces(1-iplayer) < 4:
						# penalise the move if we moved the same queen in the previous turn (in addition to the general penalty below)
						# this will give other pieces the chance to move in for the kill in the end game
						hiscore -= 5
				
			finalhiscore = hiscore
			trace("finalhiscore = " + str(finalhiscore))
			hisc[0] = finalhiscore
			if not bAI:
				return False
			else:
				return b_in_check
		except:
			print("in_check : Unexpected exception: ",sys.exc_info()[:2])
			
	def create_prospective_move(s, hiscore, move_score, our_pos, end_pos):
		hiscore = move_score
		return s.create_move(our_pos, end_pos), hiscore
		
	def score_directions_loop(s, i, p, b_move, hiscore, s_move, our_pos, iplayer):
		try:
			global smove
			smove = s_move
			NUM_DIRS = 4 * (1 + (s.basic_type(p) == 'K' or p == 'Q'))
			num_our_pieces = s.get_num_pieces(iplayer)
			num_their_pieces = s.get_num_pieces(1-iplayer)
				
			for dir in range(NUM_DIRS):
				if s.basic_type(p) == 'R':
					dx = dy = 0
					if dir == 0: dx = -1
					elif dir == 1: dx = 1
					elif dir == 2: dy = -1
					elif dir == 3: dy = 1
				elif p == 'B':
					dx = dy = -1
					if dir == 0: dx = dy = 1
					elif dir == 1: dx = 1
					elif dir == 2: dy = 1
				elif s.basic_type(p) == 'K' or p == 'Q':	
					dx = dy = 0
					if dir == 0: dy = -1
					elif dir == 1:
						dx = 1
						dy = -1
					elif dir == 2: dx = 1
					elif dir == 3: dx = dy = 1
					elif dir == 4: dy = 1
					elif dir == 5: 
						dx = -1
						dy = 1
					elif dir == 6: dx = -1
					elif dir == 7: dx = dy = -1
					
				end_pos = position(our_pos.row, our_pos.col)
				offset = 1
				b_cont = True
				while b_cont:
					end_pos.row = end_pos.row + dy
					end_pos.col = end_pos.col + dx
					# in bounds?
					if not end_pos.is_valid():
						b_cont = False
					else:
						if not s.is_ours(end_pos, iplayer): # possible
							movescore = [1]
							movescore[0] = 1001
							if not s.in_check(iplayer, movescore, our_pos, end_pos, None):
								if b_move:
									pmv = pastmove(our_pos, end_pos)					
									if s.players[iplayer].piecemoves[i].pastmove_set[tuple(pmv)] > 0:
										pm2 = tuple(pmv)
									for l in s.players[iplayer].piecemoves[i].pastmove_set.elements():
										s1, s2, s3, s4 = l
										if our_pos.row == s1 and our_pos.col == s2 and end_pos.row == s3 and end_pos.col == s4:
											movescore[0] -= s.players[iplayer].piecemoves[i].pastmove_set[l] * 3 # i.e. penalise repeat moves
											break
									if p == 'B':
										if off_backline(our_pos,end_pos, 2, iplayer):
											movescore[0] += 2
									if s.basic_type(p) == 'K':
										if (num_our_pieces < num_their_pieces) and (num_our_pieces < 5) and (our_pos.row != (iplayer*(BOARD_RANKS-1))) and (end_pos.row == (iplayer * (BOARD_RANKS-1))):
											movescore[0] -= 2 # subtle hint not to move king into the far home corner in the later stages when under pressure
									if hiscore < movescore[0]:
										smove, hiscore = s.create_prospective_move(hiscore, movescore[0], our_pos, end_pos)
								else:
									# False indicates only that we are not scoring - i.e. there is a valid move, therefore no further processing required
									return (False, "")
							if s.is_ours(end_pos, 1-iplayer): # theirs - we can't go on then
								b_cont = False
						else:
							b_cont = False
					if s.players[iplayer].pieces[i] == 'L' and dy == 0 and abs(end_pos.col - our_pos.col) == 2:
						# castling - taken from validate_move

						# Castling is permissible if and only if all of the following conditions hold:
						# 1. The king and the chosen rook are on the player's first rank.
						# 2. Neither the king nor the chosen rook have previously moved.
						#    (Use L for an unmoved king, and S for an unmoved rook)
						
						rook_pos = position()
						if s.cboard.grid[iplayer*(BOARD_RANKS-1)][0] == 'S' and s.cboard.grid[iplayer*(BOARD_RANKS-1)][4] == 'L' and our_pos.col == 4 and end_pos.col == 2:
							rook_pos.col = 0
						elif s.cboard.grid[iplayer*(BOARD_RANKS-1)][7] == 'S' and s.cboard.grid[iplayer*(BOARD_RANKS-1)][4] == 'L' and our_pos.col == 4 and end_pos.col == 6:
							rook_pos.col = 7
						else:
							b_cont = False # one or both of the king and the rook have moved from their starting position (even if they've since returned
						rook_pos.row = iplayer*(BOARD_RANKS-1)

						theirpiece = s.is_ours(end_pos,1-iplayer) - 1 # technically this requires an actual index but for the moment, -1 means not theirs
						b_dest_empty = (not s.is_ours(end_pos,1-iplayer)) and (not s.is_ours(end_pos,iplayer))
					
						# 3. There are no pieces between the king and the chosen rook (NOT merely where the king moves to.)			
						if not s.check_path(our_pos, rook_pos, abs(end_pos.col - our_pos.col), b_dest_empty, theirpiece, iplayer,False):
							b_cont = False
			
						# 4. The king is not currently in check.
						movescore = [1]
						movescore[0] = 0
						if s.in_check(iplayer, movescore, position(), position(), None):
							b_cont = False

						# 5. The king does not pass through a square that is attacked by an enemy piece.
						#    - Modify check_path to call in_check for every square it passes through...
						if not s.check_path(our_pos, end_pos, abs(end_pos.col - our_pos.col), b_dest_empty, theirpiece, iplayer, True):
							b_cont = False

						# 6. The king does not end up in check. (True of any legal move.)
						# Rook manouevre is already proven as valid
						movescore = [1]
						movescore[0] = 1003
						if not s.in_check(iplayer, movescore, our_pos, end_pos, None): #new king pos, NOT the rook pos...
							if b_move:
								pmv = pastmove(our_pos, end_pos)
								movescore[0] -= s.players[iplayer].piecemoves[i].pastmove_set[tuple(pmv)] * 3 # i.e. penalise repeat moves
								if hiscore < movescore[0]:
									smove, hiscore = s.create_prospective_move(hiscore, movescore[0], our_pos, end_pos)
									#s_pos = our_pos
									#e_pos = end_pos
							else:
								return (False, "")
						else:
							b_cont = False
						# The move is good
					if s.basic_type(s.players[iplayer].pieces[i]) == 'K':
						b_cont = False # Kings can only move one space
		except:
			print("score_directions_loop : Unexpected exception: ",sys.exc_info()[:2])	
		trace("smove = " + smove)
		return (True, smove)
		
	def in_check_mate(s, iplayer, b_move):
		try:
			global s_move
			s_move = "."
			# player here represents the next player, after the last move. We want to know if our player has any possible move.
			# loop through every piece.
			our_dir = 1 - iplayer * 2
			hiscore = 0
			movescore = 1000

			# to evaluate in random order...
			#from random import shuffle
			#my_indexes = [y for y in range(len(s.players[iplayer].positions))]
			#shuffle(my_indexes)
			my_indexes = [8,3,12,13,9,11,2,6,5,7,0,1,15,4,10,14]
			# use a fixed array like above if we want to test this version against the C++ version
		
			op_king_pos = position(s.players[1-iplayer].positions[0])

			for ind in range (len(s.players[iplayer].positions)):
				# translate from index array - this should make it consider moves from all the same pieces, in a random order
				i = my_indexes[ind]
				our_pos = s.players[iplayer].positions[i]
				if not our_pos.is_valid():
					continue # this piece was taken already
				end_pos = position()
			
				# pawns
				# diagonal move creates check
				p = s.players[iplayer].pieces[i]
				if s.basic_type(p) == 'P':
					trace("\ta pawn")
					# one forward
					end_pos.row = our_pos.row + our_dir
					end_pos.col = our_pos.col
					if  (not s.is_ours(end_pos, iplayer)) and (not s.is_ours(end_pos, 1-iplayer)) :
						movescore = [1]
						movescore[0] = 1002
						if not s.in_check(iplayer, movescore, our_pos, end_pos, None):
							# this would get us out of check - we can leave now
							if b_move:
								if our_pos.col > 0 and s.cboard.grid[iplayer * (BOARD_RANKS-1)][our_pos.col - 1] == 'B' or our_pos.col < 7 and s.cboard.grid[iplayer * (BOARD_RANKS-1)][our_pos.col + 1] == 'B':
									# frees a bishop
									movescore[0] += 2
								if to_endline(end_pos, iplayer):
									movescore[0] += 4
								if hiscore < movescore[0]:
									s_move, hiscore = s.create_prospective_move(hiscore, movescore[0], our_pos, end_pos)
							else:
								return False
					# two forward
					if (our_pos.row == 1 and our_dir == 1) or (our_pos.row == (BOARD_RANKS-1) and our_dir == -1):
						end_pos.row = int(our_pos.row + our_dir * 2)
						end_pos.col = int(our_pos.col)
						if not s.is_ours(end_pos, iplayer):
							if s.cboard.grid[end_pos.row][end_pos.col] == '.' and s.cboard.grid[int((our_pos.row + end_pos.row)/2)][int(our_pos.col)] == '.':
								movescore = [1]
								movescore[0] = 1003
								if not s.in_check(iplayer, movescore, our_pos, end_pos, None):
									if b_move:
										if our_pos.col > 0 and s.cboard.grid[iplayer * (BOARD_RANKS-1)][our_pos.col - 1] == 'B' or our_pos.col < 7 and s.cboard.grid[iplayer * (BOARD_RANKS-1)][our_pos.col + 1] == 'B':
											# frees a bishop
											movescore[0] += 2
										if hiscore < movescore[0]:
											s_move, hiscore = s.create_prospective_move(hiscore, movescore[0], our_pos, end_pos)
									else:
										return False
					# diagonals, taking a piece
					# try left, then right:
					for ep_dir in range(-1,2,2):
						if (our_pos.col + ep_dir) in range(BOARD_FILES):
							end_pos.row = our_pos.row + our_dir
							end_pos.col = our_pos.col + ep_dir
							ep_pos = position(our_pos.row, end_pos.col)
							if  s.is_ours(end_pos, 1-iplayer) and not(s.is_ours(ep_pos, 1-iplayer) and s.cboard.grid[our_pos.row][end_pos.col] == 'E') :
								# if we call is_ours with the other player, it's effectively an "is_theirs" function
								# this comparison also makes sure we don't steal the en passant case below
								movescore = [1]
								movescore[0] = 1002
								if not s.in_check(iplayer, movescore, our_pos, end_pos, None):
									if b_move:
										if to_endline(end_pos, iplayer):
											movescore[0] += 4
										if hiscore < movescore[0]:
											s_move, hiscore = s.create_prospective_move(hiscore, movescore[0], our_pos, end_pos)
									else:
										return False
								else:
									pass
					# en passant - possibly still taking a piece
					# diagonals, taking a piece
					# try left, then right:
					for ep_dir in range(-1,2,2):
						if (our_pos.col + ep_dir) in range(BOARD_FILES):
							end_pos.row = our_pos.row + our_dir
							end_pos.col = our_pos.col + ep_dir
							ep_pos = position(our_pos.row, end_pos.col)
							if ep_pos.is_valid() and not s.is_ours(end_pos, iplayer):
								# here it gets difficult. It isn't enough to pass in the normal diagonal move,
								# because the pawn we take en passant may also affect check. So we will
								# create a temporary modified board for this single circumstance and 
								# pass a reference to it to check in, AND the diagonal move.
								if s.is_ours(ep_pos, 1-iplayer) and s.cboard.grid[our_pos.row][end_pos.col] == 'E':
									gm = gameobject(s) # proposed move
									# now replace the captured en passant pawn
									gm.cboard.grid[our_pos.row][end_pos.col] = '.'
									for index in range(len(gm.players[1-iplayer].positions)):
										if gm.players[1-iplayer].positions[index] == ep_pos:
											gm.players[1-iplayer].positions[index] = position()

									# if it turns out the position we move the pawn into also contains an opposing piece, this will be handled explicity in in_check.
									movescore = [1]
									movescore[0] = 1004
									if not s.in_check(iplayer, movescore, our_pos, end_pos, gm): 
										if b_move:
											if hiscore < movescore[0]:
												s_move, hiscore = s.create_prospective_move(hiscore, movescore[0], our_pos, end_pos)
										else:
											return False
					# finally, promotion doesn't matter for determining check-mate, as a piece of any type can't move until the next go anyway
				elif p == 'N':
					trace("\ta knight")
					# the eight combinations:
					for y in range(-2,3,1):
						for x in range(-2,3,1):
							if x == 0 or y == 0:
								continue
							end_pos.row = our_pos.row
							end_pos.col = our_pos.col
							if abs(x) != abs(y):
								end_pos.row = end_pos.row + y
								end_pos.col = end_pos.col + x
								if not end_pos.is_valid():
									continue # out of bounds try next combo
								if not s.is_ours(end_pos, iplayer):
									movescore = [1]
									movescore[0] = 1001
									if not s.in_check(iplayer, movescore, our_pos, end_pos, None):
										if b_move:
											pmv = pastmove(our_pos, end_pos)					
											if s.players[iplayer].piecemoves[i].pastmove_set[tuple(pmv)] > 0:
												pm2 = tuple(pmv)
											for l in s.players[iplayer].piecemoves[i].pastmove_set.elements():
												s1, s2, s3, s4 = l
												if our_pos.row == s1 and our_pos.col == s2 and end_pos.row == s3 and end_pos.col == s4:
													movescore[0] -= s.players[iplayer].piecemoves[i].pastmove_set[l] * 3 # i.e. penalise repeat moves
													break
											if off_backline(our_pos,end_pos, 2, iplayer):
												movescore[0] += 2
											if hiscore < movescore[0]:
												s_move, hiscore = s.create_prospective_move(hiscore, movescore[0], our_pos, end_pos)
										else:
											return False
				elif s.basic_type(p) == 'R' or p == 'B' or s.basic_type(p) == 'K' or p == 'Q':
					trace("\ta rook or bishop or queen or king")
					#s_move = "sfh"
					trace ("s_move = " + str(s_move))
					bRet, s_move = s.score_directions_loop(i, p, b_move, hiscore, s_move, our_pos, iplayer)
					trace ("s_move = " + str(s_move))
					#bRet, s_move = s.score_directions_loop(i, p, b_move, hiscore, our_pos, iplayer)
					#bRet, s_pos, e_pos = s.score_directions_loop(i, p, b_move, hiscore, our_pos, iplayer)
					"""s_move = create_move(s_pos, e_pos)
					#trace("here") # TO DO remove
					#if not s.score_directions_loop(i, p, b_move, hiscore, our_pos, iplayer):"""
					if not bRet:
						# False indicates only that we are not scoring - i.e. there is a valid move, therefore no further processing required
						return False
			if hiscore > 0 and b_move:
				s.move_piece(s_move, iplayer, True) # computer makes a move for us
				if not GUI: print(s_move)
		except:
			print("in_check_mate : Unexpected exception: ",sys.exc_info()[:2])
		return True
	
	def is_ours(s, pos, iplayer):
		for each_pos in s.players[iplayer].positions:
			if each_pos == pos:
				return True
		return False
		
	def computer_turn(s, iplayer):
		return s.in_check_mate(iplayer, True)
		
	def create_move(s, start_pos, end_pos):
		s_move = chr(ord('A') + (start_pos.col)) + str(BOARD_RANKS - start_pos.row) + '-' + chr(ord('A') + (end_pos.col)) + str(BOARD_RANKS - end_pos.row)
		return s_move
		
	def build_stats(s):
		# used for both console and GUI versions
		ss = ""
		if not GUI:
			ss += "\n"
		p = None
		for i in range (len(s.players)):
			b_found = False
			ss += s.players[i].name + ":\t taken " 
			for j in range(len(s.players[i].pieces)):
				taken = position(-1,-1)
				p = s.players[1-i].pieces[j]
				if s.players[1-i].positions[j] == taken:
					b_found = True
					ss += s.basic_type(p) + " "
			if not b_found:
				ss += "no pieces"
			ss += '\n'
		ss += '\n'
		
		return ss
		
	def show_stats(s):
		ss = build_stats()
		print(ss)
		
	def get_num_pieces(s, iplayer):
		total = 0
		for each_pos in s.players[iplayer].positions:
			if each_pos.row in range(BOARD_RANKS):
				total = total + 1
		return total
		
	def is_stalemate(s):
		pass
		
	def create_positions(s):
		try:
			del s.players[0].positions [:]
			del s.players[1].positions [:]
			
			#pawns
			for i in range(BOARD_FILES):
				pos = position(1,i)
				s.players[0].positions.append(pos)
				pos = position(BOARD_RANKS-2,i)
				s.players[1].positions.append(pos)
			
			#others
			for i in range(BOARD_FILES):
				pos = position(0,i)
				s.players[0].positions.append(pos)
				pos = position(BOARD_RANKS-1,i)
				s.players[1].positions.append(pos)
		except:
			print("Unexpected error creating initial positions:", sys.exc_info()[:2])
		
	
	def create_board(s):
		try:
			for i in range(BOARD_RANKS):
				for j in range(BOARD_FILES):
					s.cboard.grid[i][j] = '.'
		except:
			print("Unexpected error creating the board:", sys.exc_info()[:2])
			
	def place_pieces(s):
		try:
			for each in s.players:
				for i in range(0,len(each.pieces)):
					row = int(each.positions[i].row)
					col = int(each.positions[i].col)
					piece = each.pieces[i]
					s.cboard.grid[row][col] = piece 
		except:
			print("Unexpected exception: ",sys.exc_info()[:2])
			print("Pieces have not been placed on the board properly.")
			
	def print_board(s):
		try:
			if GUI and not debug:
				return
			bchar = u"\u2591" # light shaded block
			print("_"*65)
			print("\nType 'load', 'save', 'new', 'quit', or a move e.g. (a1-b2)\nType 'help' for a full list of instructions.\n")
	
			y = "ABCDEFGH"
			print("    A  B  C  D  E  F  G  H\n")
			print("   " + bchar + (bchar*23) + bchar )
			
			for row in range(BOARD_RANKS):
				print (" " + str(BOARD_RANKS - row) + " " + bchar, end = "")	
				for column in range(BOARD_FILES):
					# do a conversion of the board now:
					p = s.cboard.grid[row][column]
					cdir = 'v' # down
					pos = position(row, column)
					p = s.basic_type(p)
					for each in s.players[0].positions:
						if each == pos:
							cdir = '^' # up (player 2)
							# convert player 1 to lower case:
							p = p.lower()
							break
					if p == '.':
						p = ' '
						cdir = ' '
					print(cdir + p, end = "")
					if column < (BOARD_FILES - 1):
						print (bchar,end = "")
				print( bchar + " " + str(BOARD_RANKS - row)) 
				print ("   " + bchar + (bchar*23) + bchar)	
			print("\n    A  B  C  D  E  F  G  H\n")

		except:
			print("Unexpected exception: ",sys.exc_info()[:2])
			print("The board has not been shown successfully.")
		
	def reset_board(s):
		try:
			s.create_board()
		except:
			print("Unexpected exception: ",sys.exc_info()[:2])
			print("Note that the board may not have been reset properly.")
			
	def load_game(s):
		# get names and positions
		filename = "chess_saved_game.txt"
		my_file = None
		try:
			my_file = open(filename, "r")
			# players already exists - just write over it
			for each in s.players:
				each.name = my_file.readline()
				# don't want the new line though
				each.name = each.name[:len(each.name)-1:]
				for y in range(len(each.positions)):
					ln = my_file.readline()
					p = ln[0]
					each.pieces[y] = p
					offset = 2
					if ln[offset] == '-':
						offset += 1
						row = -int(ln[offset])
					else:
						row = int(ln[offset])
					offset+=2
					if ln[offset] == '-':
						offset += 1
						col = -int(ln[offset])
					else:
						col = int(ln[offset])
					pos = position(row, col)
					each.positions[y] = pos
			ln = my_file.readline()
			s.cplayer = int(ln[0])
			ln = my_file.readline()
			s.turn = int(ln[:len(ln)-1:])
			
		except:
			if my_file != None: my_file.close()
		
		#reload the board
		return s.make_board()
			
	def save_game(s):
		filename = "chess_saved_game.txt"
		my_file = None
		try:
			my_file = open(filename, "w")
			for each in s.players:
				my_file.write(each.name + "\n")
				for y in range(len(each.positions)):
					my_file.write(each.pieces[y] + " " + str(each.positions[y].row) + " " + str(each.positions[y].col))
					my_file.write("\n")
			my_file.write(str(int(s.cplayer)) + "\n")
			my_file.write(str(s.turn) + "\n")
			messagebox.showinfo("Save","Game saved.")
		except:
			print("Unexpected error: ",sys.exc_info()[:2])
			if my_file != None: my_file.close()
		
	def new_game(s):
		try:
			for each in s.players:
				each.set_pieces()
				each.b_computer = False
				for j in each.piecemoves:
					j.pastmove_set.clear()
			s.past_boards.board_set.clear()
			s.create_positions()
			if s.make_board():
				return True
			else:
				return False
		except SystemExit as e:
			# This will happen when the GUI exits
			sys.exit(e)
		except:
			print("Unexpected error in new_game: ",sys.exc_info()[:2])
		
	def make_board(s):
		bRet = True
		try:
			s.reset_board()
			s.place_pieces()

			if GUI and s.b_GUIinitialised == False:
				MainWnd = ChessMainWnd(top, s)
				s.b_GUIinitialised = True
				top.mainloop()
				quit()

		except SystemExit as e:
			sys.exit(e)
		except:
			print("make_board : unexpected error: ",sys.exc_info()[:2])
			bRet = False
		return bRet

gm = gameobject()
		
def main():
	if not GUI:	
		print("Chess")
		print("=" * 5)

	try:
		if gm.new_game():
		# this loop is for the console - 
			while True:
				score = [1]
				score[0] = 0
				# signals we're not valuing a move for AI (1000+ if so)
				print (gm.players[gm.cplayer].name + "'s turn:")
				
				if gm.turn > MAX_TURNS:
					print("\nThe game is A DRAW - " + str(MAX_TURNS) + " moves have been made without victory.")
					gm.b_game_over = True
					gm.players[0].b_computer = False
					gm.players[1].b_computer = False
					
				if GUI:
					top.mainloop()	
					# won't return until we've made a move
					
				if gm.players[gm.cplayer].b_computer:
					cmd = "play"
				else:
					cmd = user_input()

				# All these calls are covered by their own exception handling. If they fail, they
				# don't necessarily prevent other options from working, so we don't quit the program.
				if cmd == "exit": break
				if cmd == "new":
					gm.turn = 1
					gm.cplayer = 1
					gm.new_game()
					gm.b_game_over = False
				elif cmd == "save":
					gm.save_game()
				elif cmd == "open":
					if gm.load_game():
						gm.b_game_over = False
					else:
						print("\nNo saved game was found.\n")
				elif cmd == "all":
					gm.print_all_variables()
				elif cmd == "board":
					gm.print_board()
				elif cmd == "pastmoves":
					gm.print_pastmoves()
				elif cmd == "stats":
					gm.show_stats()
				elif cmd == "pieces":
					gm.print_pieces()
				elif cmd == "help":
					gm.show_help()
				elif cmd == "checkcheck": # for debug only
					if gm.in_check(gm.cplayer, score, position(), position(), None ):
						print("\nCHECK\n") 
					else:
						print("\nNo check\n")
				elif cmd == "computer":
					if not gm.players[gm.cplayer].b_computer:
						gm.players[gm.cplayer].b_computer = True
						print("\nThe computer now has control of this player.\n")
					else:
						print("\nThe computer already has control of this player.\n")
				elif cmd == "me":
					if gm.players[1-gm.cplayer].b_computer == True:
						gm.players[gm.cplayer].b_computer = False
						print ("\nYou now have control of the other player.\n")
					else:
						print ("\nYou already have control of the other player.\n")	
				elif cmd == "play":
					gm.computer_turn(gm.cplayer)# finds a move and makes it
					gm.cplayer = not gm.cplayer
					if gm.in_check(gm.cplayer, score, position(), position(), None):
						print("\nCHECK")
					if gm.in_check_mate(gm.cplayer, False):
						print("CHECK MATE")
						print(gm.players[1-gm.cplayer].name + " wins")
						gm.b_game_over = True
						gm.players[0].b_computer = False
						gm.players[1].b_computer = False
					elif gm.is_stalemate():
						print("\nThe game is A DRAW - the same move has been made three times now.")
						gm.b_game_over = True
						gm.players[0].b_computer = False
						gm.players[1].b_computer = False
					elif gm.cplayer == 1:
						gm.turn += 1
				elif not gm.b_game_over:
					# maybe this is an actual move then!
					if gm.validate_move(cmd, gm.cplayer):
						print(cmd)
						gm.move_piece(cmd, gm.cplayer)
						gm.cplayer = 1 - gm.cplayer
						if gm.in_check(gm.cplayer, score, position(), position(), None):
							print("CHECK")
						if gm.in_check_mate(gm.cplayer, False):
							print ("\nCHECK MATE")
							print(gm.players[1-gm.cplayer].name + " wins")
							gm.b_game_over = True
							gm.players[0].b_computer = False
							gm.players[1].b_computer = False
						elif gm.is_stalemate():
							print ("\nThe game is A DRAW - the same move has been made three times now.")
							gm.b_game_over = True
							gm.players[0].b_computer = False
							gm.players[1].b_computer = False
						elif gm.cplayer == 1:
							gm.turn += 1
		else:
			pass
			# GUI exit
			
	except SystemExit as e:
		# This will happen when the GUI exits
		sys.exit(e)
	except:
		print("Unexpected exception: ", sys.exc_info()[:2])
		print("The program will now close.")
		
		exc = "Chess program failed due to the following exception: " + str(sys.exc_info()[:2])
		sys.exit(exc)

if __name__ == '__main__':
    main()
	