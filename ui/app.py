import os
import time

from tkinter import *

import cv2
import PIL.Image  # TODO edit this approach
import PIL.ImageTk

from .models import (
    MediaFile,
    Product,
    DeletedFile,
    ProductEdit,
    session,
)

BASEDIR = os.path.abspath(os.path.dirname(__file__))
MEDIA_DIR = os.path.join(BASEDIR, "assets/")
VIDEO_FILE_TYPES = ['mp4', 'avi', 'mov']

class App:
    def __init__(self, window, window_title):
        #Set window attributes
        self.window = window
        self.window.configure(background='black')
        self.window.title(window_title)

        # Set top and bottom Frames
        self.bottom_frame = Frame(self.window, background='black')
        self.bottom_frame.pack(side=BOTTOM, fill=BOTH)

        # Set window to fullscreen state
        self.fullscreen_state = True
        self.window.attributes("-fullscreen", self.fullscreen_state)

        # Get Products to display
        self.products_dir = self.get_products()

        # Create a canvas that can fit the above video source size
        self.thumbnail = Thumbnail(
            window=self.window,
            products=self.products_dir,
        )
        self.thumbnail.pack(fill=BOTH, expand=YES)

        #Create Frame to display products
        self.products = Products(
            parent=self.bottom_frame,
            products=self.products_dir,
        )
        self.products.pack(anchor=SW, padx=20, pady=20)

        # Events waiting in the GUI infinite Loop
        self.window.bind("<Return>", self.toggle_fullscreen)
        self.update_data()
        self.thumbnail.update_frame()
        self.window.mainloop()
        
    def get_products(self):
        """Returns dictionary of products to be displayed to keep in memory"""
        products = session.query(Product).filter(Product.is_displayed).all()
        products_dir = {}
        for product in products:
            products_dir[product.product_id] = {
                'name' : product.name,
                'thumbnail' : product.thumbnail,
            }
        return products_dir

    def toggle_fullscreen(self, event=None):
        self.fullscreen_state = not self.fullscreen_state  # Just toggling the boolean
        self.window.attributes("-fullscreen", self.fullscreen_state)
        return "break"

    def delete_files(self):
        """Function to delete files"""
        files_to_delete = session.query(DeletedFile).filter(DeletedFile.deleted==False).all()
        for file in files_to_delete:
            if file is not None and 'default-thumbnail' not in file.filename:
                try:
                    os.remove(os.path.join(MEDIA_DIR, file.filename))
                except Exception as e:
                    print("Unable to delete file, {}".format(e))
                file.deleted = True
                session.add(file)
        session.commit()

    def update_data(self):
        """The following repeating function rereads the database, 
        updating every value and then deletes any pending files
        knowing that it won't try to access them"""
        unapplied_editions =  session.query(ProductEdit).filter(ProductEdit.was_applied==False).all()
        # Check for any pending changes
        if unapplied_editions:
            # Destroying children in both Thumbnail and Products
            self.thumbnail.destroy()
            for widget in self.products.winfo_children():
                widget.destroy()
            self.products.destroy()

            self.products_dir = self.get_products()

            self.thumbnail = Thumbnail(window=self.window, products=self.products_dir)
            self.thumbnail.pack()
            self.thumbnail.update_frame()

            self.products = Products(parent=self.bottom_frame, products=self.products_dir)
            self.products.pack(anchor=SW, padx=20, pady=20)

            # Change the event status to was_applied
            for edition in unapplied_editions:
                edition.was_applied = True

            # Check for any pending files to delete from disk
            if session.query(DeletedFile).filter(DeletedFile.deleted==False).all():
                # Delete deleted-mediafiles from disk
                self.delete_files()
        self.window.after(10000, self.update_data)

#TODO correct resizing only happens after the second frame is called
class Thumbnail(Canvas):
    def __init__(self, window, products, *args, **kwargs):
        Canvas.__init__(self, window, *args, **kwargs)
        self.config(bg='black', highlightbackground='black')
        self.bind("<Configure>", self.on_resize)
        self.height = self.winfo_reqheight()
        self.width = self.winfo_reqwidth()
        # Create in-memory dictionary for fast access
        self.products_dir = products
        # Create list with indexes of products for better iteration
        self.product_id_list = [product_id for product_id in self.products_dir]
        # Index of the current product being displayed from product_id_list
        # We want to start with the first one and move along the list
        self.current_product_index = 0
        # update will be called every delay seconds, get_video_source
        # will assign either 0.02 if mediafile is a video, or 6 if
        # it is an image
        self.delay = 1000
        self.video_source = self.get_video_source()
        try:
            self.vid = MyVideoCapture(self.video_source)
            self.vid_ratio = self.vid.ratio
        except ValueError:
            self.get_next_video()

    def on_resize(self, event):
        """Function that is called everytime the canvas is resized"""
        self.width = event.width
        self.height = event.height
        # resize the canvas 
        self.config(width=self.width, height=self.height)

    def get_video_source(self):
        """Gets video source by looking for the specific item id inside the
        products_dir"""
        video_source = self.products_dir[
            self.product_id_list[self.current_product_index]
            ]['thumbnail']
        # Edit delay seconds depending if file is video or image
        if any([video_file_type in video_source for video_file_type in VIDEO_FILE_TYPES]):
            self.delay = 20
        else:
            self.delay = 5000
        return video_source

    def update_frame(self):
        """Get frame from video source"""
        ret, frame = self.vid.get_frame()

        if ret:
            # Resizing frame
            frame = cv2.resize(frame, (self.width, int(self.width/self.vid_ratio)))
            self.photo = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(frame))
            self.create_image(0, 0, image=self.photo, anchor=NW)
            # delays updating of the thumbnail depending on the filetype
            self.after(self.delay, self.update_frame)
        else:
            self.get_next_video()
            self.update_frame()
    
    def get_next_video(self):
        """Updates video_source by Moving one index item up
        the product_id_list, if the last product_id has been reached,
        it goes back to the first (0) index item"""
        try:
            self.current_product_index += 1
            self.video_source = self.get_video_source()
        except IndexError:
            self.current_product_index = 0
            self.video_source = self.get_video_source()
        try:
            self.vid = MyVideoCapture(self.video_source)
        except ValueError:
            self.get_next_video()
        self.vid_ratio = self.vid.ratio

class MyVideoCapture:
    def __init__(self, video_source):
        # Open the video source
        self.vid = cv2.VideoCapture(os.path.join(MEDIA_DIR, video_source))
        if not self.vid.isOpened():
            #TODO log this shit
            print("Unable to open video source: {}".format(video_source))
            raise ValueError("Unable to open video source", video_source)

        # Get video source width, height and fps
        self.width = self.vid.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height = self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT)
        self.ratio = self.width/self.height

    def get_frame(self):
        #TODO handle this better
        if self.vid.isOpened():
            ret, frame = self.vid.read()
            if ret:
                # Returns a boolean success flag (ret) and the current frame converted to BGR
                return (ret, cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            else:
                return (ret, None)

    # Release the video source when the object is destroyed
    def __del__(self):
        if self.vid.isOpened():
            self.vid.release()

class Products(Frame):
    def __init__(self, parent, products, *args, **kwargs):
        Frame.__init__(self, parent, *args, **kwargs)
        self.products = products

        self.config(background='black')

        # Create two containers, one for each row that will display max 5 products
        # for a total of max 10 displayed products
        self.product_names_container1 = Frame(self, background='black')
        self.product_names_container1.pack(side=LEFT, padx=20)
        self.product_names_container2 = Frame(self, background='black')
        self.product_names_container2.pack(side=LEFT, padx=20)
        self.get_product_names()
    
    def get_product_names(self):
        # Destroying children
        for widget in self.product_names_container1.winfo_children():
            widget.destroy()
        for widget in self.product_names_container2.winfo_children():
            widget.destroy()

        self.product_names = [
            self.products[product]['name'] for product in self.products
        ]

        # First column
        for name in self.product_names[:5]:
            product_name = name
            
            widget = ProductName(self.product_names_container1, product_name)
            widget.pack(side=TOP, anchor=W)

        # Second column
        for name in self.product_names[5:]:
            product_name = name

            widget2 = ProductName(self.product_names_container2, product_name)
            widget2.pack(side=TOP, anchor=W)

class ProductName(Frame):
    def __init__(self, parent, product_name=""):
        Frame.__init__(self, parent, background='black')
        self.product_name = product_name
        self.product_name_lbl = Label(self, text=self.product_name, font=('clean', 18), fg='white', bg='black')
        self.product_name_lbl.pack(side=TOP, anchor=W)
