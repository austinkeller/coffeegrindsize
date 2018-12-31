#Import the necessary packages
from tkinter import filedialog
from tkinter import *
from PIL import ImageTk, Image
import time

#Temporary for debugging purposes
import pdb
stop = pdb.set_trace

# === Default Parameters for analysis and plotting ===

#Default value for image thresholding (%)
def_threshold = 58.8

#Default value for the pixel scale (pixels/millimeters)
def_pixel_scale = 0.177

#Default value for the maximum diameter of a single cluster (pixels)
#Smaller values will speed up the code slightly
def_max_cluster_axis = 500

#Default value for the minimum surface of a cluster (pixels squared)
def_min_surface = 2

#Default value for the minimum roundness of a cluster (no units)
#Roundness is defined as the ratio of cluster to all pixels in the smallest circle that encompasses all pixels of a cluster
def_min_roundness = 0

#Default X axis range for the histogram (variable units)
def_min_x_axis = 0
def_max_x_axis = 1000

#Default name for the session (used for output filenames)
def_session_name = "JG_PSD"

#Python class for the user interface window
class coffeegrindsize_GUI:
	
	#Actions to be taken on initialization of user interface window
	def __init__(self,root):
		
		# === Set some object variables that will not be garbage collected ===
		
		#This variable will contain the object of the image currently displayed
		self.image_id = None
		
		#This is the display scale for zooming in/out
		self.scale = 1.0
		
		#Remember the root object for the full user interface so that the methods of coffeegrindsize_GUI can refer to it
		self.master = root
		
		#The first row where options or buttons will be displayed
		self.options_row = 1
		
		#The width of text entries for adjustable options
		self.width_entries = 6
		
		#Horizontal spaces around the option labels
		self.title_padx = 12
		
		#Horizontal and vertical spaces around the toolbar buttons
		self.toolbar_padx = 6
		self.toolbar_pady = 6
		
		#Size in pixels of the canvas where the pictures and figures will be displayed
		self.canvas_width = 1000
		self.canvas_height = 800
		
		#Set the window title
		self.master.title("Coffee Particle Size Distribution by Jonathan Gagne")
		
		#Create a toolbar with buttons to launch various steps of analysis
		toolbar_bg = "gray90"
		toolbar = Frame(self.master, bg=toolbar_bg)
		toolbar.pack(side=TOP, fill=X)
		
		#Create a status bar at the bottom of the window
		self.status_var = StringVar()
		self.status_var.set("Idle...")
		status = Label(self.master, textvariable=self.status_var, anchor=W, bg="grey", relief=SUNKEN)
		status.pack(side=BOTTOM, fill=X)
		
		# === Initialize the main frame that will contain option buttons and settings and the image ===
		self.frame_options = Frame(root)
		self.frame_options.pack()
		
		# === Build the adjustable keyword options ===
		
		#This adds a vertical spacing in the options frame
		self.label_separator()
		
		#All options related to image thresholding
		self.label_title("Threshold Step:")
		
		#Value of fractional threshold in units of flux in the blue channel of the image
		self.threshold_var = self.label_entry(def_threshold, "Threshold:", "%")
		
		self.label_separator()
		
		#All options related to particle detection
		self.label_title("Particle Detection Step:")
		
		#Physical size of one pixel in the coffee grounds picture
		#For now this needs to be input manually
		self.pixel_scale_var = self.label_entry(def_pixel_scale, "Pixel Scale:", "mm/pix")
		
		#Maximum cluster diameter that should be considered a valid coffee particle
		self.max_cluster_axis_var = self.label_entry(def_max_cluster_axis, "Maximum Cluster Diameter:", "pix")
		
		#Minumum cluster surface that should be considered a valid coffee particle
		self.min_surface_var = self.label_entry(def_min_surface, "Minimum Cluster Surface:", "pix^2")
		
		#Minimum cluster roundness that should be considered a valid coffee particle
		#Roundess is defined between 0 and 1 where 1 is a perfect circle. It represents the fraction of thresholded pixels inside the smallest circle that encompasses the farthest thresholded pixels in one cluster
		self.min_roundness_var = self.label_entry(def_min_roundness, "Minimum Roundness:", "")

		self.label_separator()
		
		#All options related to plotting histograms
		self.label_title("Histogram Options:")
		
		# === This block of lines creates a drop-down menu === (will eventually be a method)
		self.histogram_type = StringVar(self.master)
		
		#List the possible types of hisograms that can be plotted
		#default_choice = 'Number Fraction vs Particle Diameter'
		#choices = { 'Number Fraction vs Particle Diameter','Extracted Fraction vs Particle Surface','Surface Fraction vs Particle Surface'}
		default_choice = 'NumDiam'
		choices = { 'NumDiam', 'NumSurf'}
		self.histogram_type.set(default_choice) # set the default option
		
		#Display the histogram type menu
		histogram_type_label = Label(self.frame_options, text="Histogram Type:")
		histogram_type_menu = OptionMenu(self.frame_options, self.histogram_type, *choices)
		histogram_type_label.grid(row=self.options_row,sticky=E)
		histogram_type_menu.grid(row=self.options_row,column=1,columnspan=2,sticky=W)
		
		#Link the histogram selection to an internal variable
		self.histogram_type.trace('w', self.change_dropdown_histogram_type)
		
		self.options_row += 1
		
		#X axis range for the histogram figure
		self.xmin_var = self.label_entry(def_min_x_axis, "Minimum X Axis:", "")
		self.xmax_var = self.label_entry(def_max_x_axis, "Maximum X Axis:", "")
		
		#Whether the X axis of the histogram should be in logarithm format
		#This is a checkbox
		xlog_var = IntVar()
		xlog_var.set(1)
		checkbox1 = Checkbutton(self.frame_options, text="Logarithmic X axis",variable=xlog_var)
		checkbox1.grid(row=self.options_row,columnspan=2,sticky=E)
		
		self.options_row += 1
		
		self.label_separator()
		
		#All options related to saving output data
		self.label_title("Output Options:")
		
		#The base of the output file names
		self.session_name_var = self.label_entry(def_session_name, "Base of File Names:", "", columnspan=2, width=self.width_entries*3)
		
		#Add a few horizontal spaces
		for i in range(12):
			self.label_separator()
		
		#Button for resetting all options to default
		reset_params_button = Button(self.frame_options, text="Reset to Default Parameters", command=self.reset_status)
		reset_params_button.grid(row=self.options_row,column=0)
		self.options_row += 1
		
		#Button for resetting zoom in the displayed image
		reset_zoom_button = Button(self.frame_options, text="Reset Zoom Parameters", command=self.reset_zoom)
		reset_zoom_button.grid(row=self.options_row,column=0)

		# === Create a canvas to display images and figures ===
		
		#Initialize the canvas
		image_canvas_bg = "gray40"
		self.image_canvas = Canvas(self.frame_options, width=self.canvas_width, height=self.canvas_height, bg=image_canvas_bg)
		self.image_canvas.grid(row=0,column=3,rowspan=145)
		
		#Prevent the image canvas to shrink when labels are placed in it
		self.image_canvas.pack_propagate(0)
		
		#Display a label when no image was loaded
		self.noimage_label = Label(self.image_canvas, text="No Image Loaded", anchor=CENTER, bg=image_canvas_bg, font='Helvetica 18 bold', width=self.canvas_width, height=self.canvas_height)
		self.noimage_label.pack(side=LEFT)
		
		# === Populate the toolbar with buttons for analysis ===
		
		#Button to open an image of the coffee grounds picture
		open_image_button = Button(toolbar, text="Open Image...", command=self.open_image,highlightbackground=toolbar_bg)
		open_image_button.pack(side=LEFT, padx=self.toolbar_padx, pady=self.toolbar_pady)
		
		#Button to apply image threshold
		threshold_image_button = Button(toolbar, text="Threshold Image...", command=self.threshold_image,highlightbackground=toolbar_bg)
		threshold_image_button.pack(side=LEFT, padx=self.toolbar_padx, pady=self.toolbar_pady)
		
		#Button to launch the particle detection analysis
		psd_button = Button(toolbar, text="Launch Particle Detection Analysis...", command=self.launch_psd,highlightbackground=toolbar_bg)
		psd_button.pack(side=LEFT, padx=self.toolbar_padx, pady=self.toolbar_pady)
		
		#Button to display histogram figures
		histogram_button = Button(toolbar, text="Create Histogram Figure...", command=self.create_histogram,highlightbackground=toolbar_bg)
		histogram_button.pack(side=LEFT, padx=self.toolbar_padx, pady=self.toolbar_pady)
		
		#Button to output data to the disk
		save_button = Button(toolbar, text="Save Data...", command=self.launch_psd,highlightbackground=toolbar_bg)
		save_button.pack(side=LEFT, padx=self.toolbar_padx, pady=self.toolbar_pady)

		# === Create a menu bar (File, Edit...) ===
		menu = Menu(root)
		root.config(menu=menu)

		#Create a FILE submenu
		subMenu = Menu(menu)
		menu.add_cascade(label="File", menu=subMenu)
		
		#Add an option to open images from disk
		subMenu.add_command(label="Open Image...", command=self.open_image)
		subMenu.add_separator()
		
		#Add an option for debugging
		subMenu.add_command(label="Python Debugger...", command=self.pdb_call)
		subMenu.add_separator()
		
		#Add an option to quit
		subMenu.add_command(label="Quit", command=quit)

		# === Create drag and zoom options for the image canvas ===
		
		#Always keep track of the mouse position (this is used for zooming toward the cursor)
		self.image_canvas.bind('<Motion>', self.motion)
		
		#Set up key bindins for dragging the image
		self.image_canvas.bind("<ButtonPress-1>", self.move_start)
		self.image_canvas.bind("<B1-Motion>", self.move_move)
		
		#Set up key bindings for zooming in and out with the i/o keys
		self.image_canvas.bind_all("i", self.zoomerP)
		self.image_canvas.bind_all("o", self.zoomerM)
	
	#Method to register changes in the histogram type option
	def change_dropdown_histogram_type(self, *args):
		#This is not coded yet
		print(self.histogram_type.get())
	
	#Method to display a label in the options frame
	def label_entry(self, default_var, text, units_text, columnspan=None, width=None):
		
		#Default width is located in the internal class variables
		if width is None:
			width = self.width_entries
		
		#Introduce a variable to be linked with the entry dialogs
		data_var = StringVar()
		
		#Set variable to default value
		data_var.set(str(default_var))
		
		#Display the label for the name of the option
		data_label = Label(self.frame_options, text=text)
		data_label.grid(row=self.options_row,sticky=E)
		
		#Display the data entry box
		data_entry = Entry(self.frame_options, textvariable=data_var, width=width)
		data_entry.grid(row=self.options_row,column=1,columnspan=columnspan)
		
		#Display the physical units of this option
		data_label_units = Label(self.frame_options, text=units_text)
		data_label_units.grid(row=self.options_row,column=2,sticky=W)
		
		#Update the row where next labels and entries will be displayed
		self.options_row += 1
		
		#Return value of the bound variable to the caller
		return data_var
	
	#Method to display a title for option groups
	def label_title(self, text):
		title_label = Label(self.frame_options, text=text, font='Helvetica 18 bold')
		title_label.grid(row=self.options_row, sticky=W, padx=self.title_padx)
		self.options_row += 1
	
	#Method to display a vertical blank separator in the options frame
	def label_separator(self):
		separator_label = Label(self.frame_options, text="")
		separator_label.grid(row=self.options_row)
		self.options_row += 1
	
	#Method to redraw the image after a zoom
	def redraw(self, x=0, y=0):
	        
	        if self.image_id:
	            self.image_canvas.delete(self.image_id)
	        iw, ih = self.img.size
	        size = int(iw * self.scale), int(ih * self.scale)
	        self.image_obj = ImageTk.PhotoImage(self.img.resize(size))
	        self.image_id = self.image_canvas.create_image(x, y, image=self.image_obj)
	        
	#Method to set the starting point of a drag
	def move_start(self, event):
		self.image_canvas.scan_mark(event.x, event.y)
	
	#Method to execute the move of a drag
	def move_move(self, event):
		self.image_canvas.scan_dragto(event.x, event.y, gain=1)
	
	#Method to track the mouse position
	def motion(self, event):
	    self.mouse_x, self.mouse_y = event.x, event.y

	#Method to apply a zoom in
	def zoomerP(self, event):
		
		#Get current coordinates of image
		image_x, image_y = self.image_canvas.coords(self.image_id)
		
		#Include effect of drag
		image_x -= self.image_canvas.canvasx(0)
		image_y -= self.image_canvas.canvasy(0)
		
		#Get original image size
		orig_nx, orig_ny = self.img.size
		
		#Determine cursor position on original image coordinates (x,y -> alpha, beta)
		mouse_alpha = orig_nx/2 + (self.mouse_x-image_x)/self.scale
		mouse_beta = orig_ny/2 + (self.mouse_y-image_y)/self.scale
		
		#Change the scale of image
		self.scale *= 2
		
		#Determine pixel position for the center of the new zoomed image
		new_image_x = self.mouse_x - (mouse_alpha - orig_nx/2)*self.scale
		new_image_y = self.mouse_y - (mouse_beta - orig_ny/2)*self.scale
		
		#Include effect of drag
		new_image_x += self.image_canvas.canvasx(0)
		new_image_y += self.image_canvas.canvasy(0)
		
		#Redraw image at the desired position
		self.redraw(x=new_image_x, y=new_image_y)
	
	#Method to apply a zoom out
	def zoomerM(self, event):
		
		#Get current coordinates of image
		image_x, image_y = self.image_canvas.coords(self.image_id)
		
		#Include effect of drag
		image_x -= self.image_canvas.canvasx(0)
		image_y -= self.image_canvas.canvasy(0)
		
		#Get original image size
		orig_nx, orig_ny = self.img.size
		
		#Determine cursor position on original image coordinates (x,y -> alpha, beta)
		mouse_alpha = orig_nx/2 + (self.mouse_x-image_x)/self.scale
		mouse_beta = orig_ny/2 + (self.mouse_y-image_y)/self.scale
		
		#Change the scale of image
		self.scale *= 0.5
		
		#Determine pixel position for the center of the new zoomed image
		new_image_x = self.mouse_x - (mouse_alpha - orig_nx/2)*self.scale
		new_image_y = self.mouse_y - (mouse_beta - orig_ny/2)*self.scale
		
		#Include effect of drag
		new_image_x += self.image_canvas.canvasx(0)
		new_image_y += self.image_canvas.canvasy(0)
		
		#Redraw image at the desired position
		self.redraw(x=new_image_x, y=new_image_y)
	
	#Method to trigger the Python debugger
	def pdb_call(self):
		pdb.set_trace()
	
	#Method to reset zoom
	def reset_zoom(self):
		
		#Update the user interface status
		self.status_var.set("Zoom Parameters Reset to Defaults...")
		
		#Set back the scale to its original value when the image was loaded
		self.scale = self.original_scale
		
		#Reset the effect of dragging
		self.image_canvas.xview_moveto(0)
		self.image_canvas.yview_moveto(0)
		
		#Redraw the image
		self.redraw(x=self.canvas_width/2, y=self.canvas_height/2)
		
		#Update the user interface
		self.master.update()
	
	#Method to reset status
	def reset_status(self):
		
		#Update the user interface status
		self.status_var.set("Parameters Reset to Defaults...")
		
		#Reset all options to their default values
		self.threshold_var.set(str(def_threshold))
		self.pixel_scale_var.set(str(def_pixel_scale))
		self.max_cluster_axis_var.set(str(def_max_cluster_axis))
		self.min_surface_var.set(str(def_min_surface))
		self.min_roundness_var.set(str(def_min_roundness))
		self.xmin_var.set(str(def_min_x_axis))
		self.xmax_var.set(str(def_max_x_axis))
		self.session_name_var.set(str(def_session_name))
		
		#Update the user interface
		self.master.update()
	
	#Method to open an image from the disk
	def open_image(self):
		
		#Update root to avoid problems with file dialog
		self.master.update()
		image_filename = "/Users/gagne/Documents/IDL/IDL_resources/Kinu3.4_1_sub_detection_final.png"
		
		#Do not delete
		#Invoke a file dialog to select image
		#image_filename = filedialog.askopenfilename(initialdir="/",title="Select a PNG image",filetypes=(("png files","*.png"),("all files","*.*")))
		
		# === Display image if filename is set ===
		# Hitting cancel in the filedialog will therefore skip the following steps
		if image_filename != "":
			
			#Open image
			self.img = Image.open(image_filename)
			
			#Determine smallest zoom such that the full image fits in the canvas
			width_factor = self.canvas_width/self.img.size[0]
			height_factor = self.canvas_height/self.img.size[1]
			scale_factor = min(width_factor,height_factor)
			nx = round(scale_factor*self.img.size[0])
			ny = round(scale_factor*self.img.size[1])
				
			#Interpret the image with tkinter
			self.image_obj = ImageTk.PhotoImage(self.img)
			
			#Set the resulting scale in an internal variable
			self.scale = scale_factor
			self.original_scale = scale_factor
			
			#Delete any object that was currently displayed
			self.noimage_label.pack_forget()
			
			#Refresh the image
			self.redraw(x=self.canvas_width/2+3, y=self.canvas_height/2+3)
			
			#Refresh the user interface status
			self.status_var.set("Image opened: "+image_filename)
			
			#Refresh the state of the user interface window
			self.master.update()
	
	#Method to apply image threshold
	def threshold_image(self):
		print("Not coded yet")
		
		#Testing a live update of the user interface status
		for i in range(12):
			time.sleep(1)
			self.status_var.set("Iteration #"+str(i))
			self.master.update()
	
	#Method to launch particle detection analysis
	def launch_psd(self):
		print("Not coded yet")
	
	#Method to create histogram
	def create_histogram(self):
		print("Not coded yet")
	
	#Method to save data to disk
	def save_data(self):
		print("Not coded yet")
	
	#Method to quit user interface
	def quit(self):
		print("Not coded yet")
		pdb.set_trace()

# === Main loop and call to the user interface window ===

#Invoke tkinter package
root = Tk()

#Call the user interface
coffeegrindsize_GUI(root)

#Refresh user interface in a try statement to avoid UTF-8 crashes when the user interface tries to interpret unrecognized inputs like an Apple trackpad
while True:
    try:
        root.mainloop()
        break
    except UnicodeDecodeError:
        pass