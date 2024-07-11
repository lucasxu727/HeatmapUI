# Lucas Xu, Highschool Intern @ UAlberta, 7/11/2024 (MM/DD/YYYY)
#Python 3.11.9, WindowsOS 11 
#UI of a heatmap designed to visualize the amount of people per room
#main var/classes: class PannableCanvas, root, button_zoomin, button_zoomout, slider
import tkinter as tk
import tkinter.font as tkFont
from PIL import Image, ImageTk, ImageDraw
import csv
import json
import pandas as pd

#Canvas init, canvas to hold a pannable image of the map
class PannableCanvas(tk.Frame):
    #define parameters and initialize
    def __init__(self, master, image_path, max_width, max_height, rooms, current_hour, *args, **kwargs):

        #init parent class holding canvas
        super().__init__(master,*args,**kwargs)

        #create class args to be made public
        self.image_path = image_path
        self.max_width = max_width
        self.max_height = max_height
        self.current_scale = 1.0
        self.tk_image = None
        self.rooms = rooms
        self.current_hour = current_hour
        self.display_height = max_height
        self.display_width = max_width
        self.shapes = []
        
        #canvas init
        self.canvas = tk.Canvas(self, width=max_width, height=max_height, bg='white')
        self.canvas.grid(row=0,column=0, sticky = "nsew")

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        #image init
        self.image = self.scale_image(image_path, max_width, max_height, self.current_scale)

        self.canvas_image = self.canvas.create_image(0,0, anchor=tk.NW, image=self.image)
        self.canvas.config(scrollregion=self.canvas.bbox(tk.ALL))
        
        
        #mouse init
        self.canvas.bind("<ButtonPress-1>", self.start_pan)
        self.canvas.bind("<B1-Motion>", self.pan)                                                 

        #center canvas
        self.center_canvas()

        #loop through shapes in file and draw
        for _, row in self.rooms.iterrows():
            if row['hour'] == self.current_hour:
                self.draw_shapes(row)

    #scale the image to fit the canvas
    #HEIGHT AND WIDTH SWITCHED DUE TO THE 90 DEGREE ROTATE
    def scale_image(self, image_path, max_width, max_height, scale):
        try:
            image = Image.open(image_path)
        except Exception as e:
            print(f"Error opening image: {e}")
            return None
            
        original_width, original_height = image.size

        #recalculate width and heigh via aspect ratio
        aspect_ratio = original_width/original_height

        dw = max_width - original_width
        dh = max_height - original_height
        
        if dw > dh:
            new_width = max_height
            new_height = new_width / aspect_ratio
        else:
            new_height = max_width
            new_width = new_height * aspect_ratio

        new_height = int(new_height * scale)
        new_width = int(new_width * scale)

        self.display_height = new_width
        self.display_width = new_height
        
        #resize using calculated dimensions
        new_image = image.resize((new_width, new_height), Image.LANCZOS)
        new_image = new_image.rotate(-90, expand=True)
        tk_image = ImageTk.PhotoImage(new_image)
        return tk_image

    #redraw image and all shapes for when zoomin/zoomout is called or hour change
    def update_image(self):
        self.image = self.scale_image(self.image_path, self.max_width, self.max_height, self.current_scale)
        self.canvas.itemconfig(self.canvas_image, image=self.image)
        self.canvas.config(scrollregion=self.canvas.bbox(tk.ALL))

        #delete old shapes
        for shape in self.shapes:
            self.canvas.delete(shape['id'])

        self.shapes.clear()

        #create new shapes
        for _, row in self.rooms.iterrows():
            if row['hour'] == self.current_hour:
                self.draw_shapes(row)

    #zoom in
    def zoom_in(self):
        if self.current_scale * 1.2 <= 3:
            self.current_scale *= 1.2 
            self.update_image()
    #zoom out
    def zoom_out(self):
        if self.current_scale / 1.2 >= 1.0:
            self.current_scale /= 1.2
            self.update_image()
            
    #track starting coords
    def start_pan(self, event):
        self.canvas.scan_mark(event.x, event.y)
        print(f'{self.canvas.canvasx(event.x)}, {self.canvas.canvasy(event.y)}')
        
    #drag with scan_dragto
    def pan(self, event):
        self.canvas.scan_dragto(event.x, event.y, gain=1)

    #calculate colour of shape from green to red based off of how many people
    def calc_color(self, n):
        #scale of 1-10, 10 being max power
        val = min(n/10, 1)
        red = int(val * 255)
        green = int((1-val) * 255)

        #translate into hex
        color = f'#{red:02x}{green:02x}00'
        return color

    #draw all shapes of the current hour to be overlayed on the image using coordinates and draw.polygon()
    def draw_shapes(self, room):
        
        #init values for polygon
        color = self.calc_color(room['people'])
        alpha = 128
        coords = [coord * self.current_scale for coord in room['coords']]

        #create image with RGBA values for translucent effect
        img = Image.new('RGBA', (self.display_width, self.display_height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        #fill the image with a polygon of calculated colour
        #polygons by default do not take alpha values, hence the image was created
        draw.polygon(coords, fill=(int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16), alpha), outline='black')
        
        tk_img = ImageTk.PhotoImage(img)

        image_item = self.canvas.create_image(0, 0, anchor=tk.NW, image=tk_img)

        #add shapes into list for easy access when updating
        self.shapes.append({'id': image_item, 'original_coords': coords, 'image': tk_img})

    #center the canvas
    def center_canvas(self):
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        image_width = self.image.width()
        image_height = self.image.height()

        if image_width > canvas_width:
            self.canvas.xview_moveto((image_width - canvas_width) / 2 / image_width)
        else:
            self.canvas.xview_moveto(0.5 - canvas_width / image_width / 2)

        if image_height > canvas_height:
            self.canvas.yview_moveto((image_height - canvas_height) / 2 / image_height)
        else:
            self.canvas.yview_moveto(0.5 - canvas_height / image_height / 2)

        # Adjust the scroll region to accommodate zoom
        self.canvas.config(scrollregion=self.canvas.bbox(tk.ALL))

def zoom_out():
    canvas.zoom_out()

def zoom_in():
    canvas.zoom_in()

#update value of the slider to show the data of specified hour
def slider_change(value):
    canvas.current_hour = int(value)
    canvas.update_image()

#function for changing the hour for button_change()
def change_hour():
    global after_id
    current_val = slider.get()
    if current_val == 23:
        current_val = 0
    if button_video.image == pause_img:
        if current_val + 1 < 24:
            current_val += 1
            slider.set(current_val)
            canvas.update_image()
            after_id = root.after(1000, change_hour)
        else:
            return
  
#play pause function for play pause button
def button_change():
    global after_id
    #if the images are currently paused
    if button_video.image == play_img:
        button_video.config(image = pause_img)
        button_video.image = pause_img
        change_hour()
    else:
        #if the iamges are currently playing
        button_video.config(image = play_img)
        button_video.image = play_img
        if after_id is not None:
            root.after_cancel(after_id)  # Cancel the scheduled increment
            after_id = None

        

# window init
root = tk.Tk()
root.title("HeatMap UI")
root.geometry("1600x1000")
root.config(bg='white', pady=100, padx=100)
root.state('zoomed')

max_width = 1600
max_height = 800

# Load and display an imageLLL
image_path = '1stFloor.png' 

#frame and button init
top_frame = tk.Frame(root, bg = 'white')
button_zoomin = tk.Button(top_frame, text = "+", width=4, height=2, relief='solid', bg='white', activebackground='white', activeforeground='black', borderwidth=1, highlightbackground = 'grey', command=zoom_in)
button_zoomin.pack(side = 'right', expand = False, pady=10)
button_zoomout = tk.Button(top_frame, text = "-", width=4, height=2, relief='solid',bg='white', activebackground='white', activeforeground='black',  borderwidth=1, highlightbackground = 'grey', command=zoom_out)
button_zoomout.pack(side = 'right', expand = False, pady=10)

#load images for play/pause button
play_path = Image.open('play.png')
play_path = play_path.resize((35,35), Image.LANCZOS)
pause_path = Image.open('pause.png')
pause_path = pause_path.resize((35,35), Image.LANCZOS)
play_img = ImageTk.PhotoImage(play_path)
pause_img = ImageTk.PhotoImage(pause_path)
button_video = tk.Button(top_frame, image=play_img, width=35, height=35, relief='solid', bg='white', activebackground='white', activeforeground='black', borderwidth=1, highlightbackground = 'grey', command=button_change)
button_video.image = play_img
button_video.pack(side = 'left', pady=10)

slider = tk.Scale(top_frame, from_ = 0, to=23, orient='horizontal', command=slider_change, length = 300)
slider.pack(pady=20, padx = 20)

top_frame.pack()

#data selection for canvas init
filename = 'data1.csv'

#open file and convert to pandas object + format
try:
    df = pd.read_csv(filename)
except ValueError as e:
    print(f"Error reading JSON: {e}")

df['coords'] = df['coords'].apply(json.loads)

hour = 0

#canvas init
canvas = PannableCanvas(root, image_path, max_width, max_height, df, hour)
canvas.pack(fill=tk.BOTH, expand=True)


slider.config(resolution= 1)

# Run the main event loop
root.mainloop()