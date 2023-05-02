# importing the necessary modules 
# Importing the necessary modules 
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk

import threading

import urllib.request
from io import BytesIO

import yt_dlp as youtube_dl
import re
import os



class YoutubeDownloadWindow(tk.Tk):
    

    def get_unique_resolutions(self, inf_dict):
        resolutions = {}
        for format in inf_dict['formats']:
            if re.match(r'^\d+p', format['format_note']) :
                resolution_id = format['format_id']
                resolution = format['format_note']
                if 'HDR' in resolution:
                    resolution = re.search(r'\d+p\d* HDR', resolution)[0]
                resolutions[resolution ] =resolution_id
                
        resolutions = [(v, k) for k, v in resolutions.items()]
        return sorted(resolutions, key=lambda k: [int(k[1].split('p')[0]), k[1].split('p')[-1]])


    def download_info_dict(self):
        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio/best',
            'forcejson': True,
            'dump_single_json': True,
        }
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(self.video_url.get(), download=False)
        return info_dict

    def download_thumbnail(self, url):
        with urllib.request.urlopen(url) as url:
            img_data = url.read()
        return img_data

    def create_pil_image(self, img_data):
        img = Image.open(BytesIO(img_data))
        img.thumbnail((120, 120))
        return img

    def create_photo_image(self, img):
        return ImageTk.PhotoImage(img)

    def display_image_and_title(self, info_dict, photo2):
        label = tk.Label(self.image_frame, image=photo2)
        label.grid(row = 0 , padx = 5, pady = 5)
        label.configure(image=photo2)
        label.image = photo2

        text_label = tk.Label(
            self.image_frame,
            text=info_dict['title'],
            font=("Arial", 8, "bold"),
            bg="#FFFFFF",
            fg="#000000"
        )
        text_label.grid(row=1, padx=5, pady=5)

    def create_resolutions_label(self):
        resolutions_label = tk.Label(
            self.entry_frame,
            text="Resolutions:",
            font=("verdana", "10"),
            bg="#FEE4E3",
            fg="#000000",
            anchor=tk.SE
        )
        resolutions_label.grid(row=2, column=0, padx=5, pady=5, sticky=tk.E)

    def create_resolutions_dropdown(self, info_dict):
        resolutions = self.get_unique_resolutions(info_dict)
        self.resolutions_fields['values'] = [res[1] for res in resolutions]
        self.ids = {res[1]: res[0] for res in resolutions}
        self.resolutions_fields.current(0)
        self.resolutions_fields.grid(row=2, column=1, pady=5)

    def set_image(self):
        info_dict = self.download_info_dict()
        img_data = self.download_thumbnail(info_dict['thumbnail'])
        img = self.create_pil_image(img_data)
        photo2 = self.create_photo_image(img)
        self.display_image_and_title(info_dict, photo2)
        self.create_resolutions_label()
        self.create_resolutions_dropdown(info_dict)

    def progress_hook(self , data):
        if data['status'] == 'downloading':
            downloaded = data['downloaded_bytes']

            total = data['total_bytes']  if data.get('total_bytes' ,None) else data['total_bytes_estimate']
            percentage = downloaded / total * 100
            percentage = round(percentage, 2)
           
            self.progress_bar["value"] =  percentage
            self.progress_bar.update()
            
            self.style.configure('text.Horizontal.TProgressbar', text='{:g} %'.format(percentage))
        


    def setup_ydl_opts(self):
        # Retrieve the string from the entry fields
        format = self.ids[self.resolutions_fields.get()]
        download_folder = self.download_dir.get()

        return {
            'format': f"{format}+bestaudio",
            'merge_output_format': 'mkv' ,
            'progress_hooks': [self.progress_hook],
            'outtmpl': os.path.join(
                download_folder, '%(title)s-%(format)s.%(ext)s'
            ),
        }

    def download_video(self):
        # Retrieve the string from the entry fields
        youtube_url = self.video_url.get()
        download_folder = self.download_dir.get()

        # Check if the entry fields are not empty
        if youtube_url and download_folder:
            # Display progress bar
            self.progress_bar.grid(column=0, row=0, columnspan=2, padx=10, pady=20)

            # Set up options for youtube-dl
            ydl_opts = self.setup_ydl_opts()

            # Download the video
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                ydl.download([youtube_url])

            # Hide progress bar and show download complete message
            self.progress_bar.grid_remove()
            messagebox.showinfo(title='Download Complete', message='Video has been downloaded successfully.')
        else:
            # Display error message for empty fields
            messagebox.showerror("Empty Fields", "Fields are empty!")




    def browse_folder(self):
        # using the askdirectory() method of the filedialog module to select the directory  
        download_path = filedialog.askdirectory(initialdir = "D:\Downloads", title = "Select the folder to save the video")  
        # using the set() method to set the directory path in the entry field  
        self.download_dir.set(download_path)  
        
        if self.video_url.get()=="" : 
            return
    
        download_thread = threading.Thread(target=self.set_image)
        download_thread.start()
    
    def download_video_thread(self):
        download_thread = threading.Thread(target=self.download_video)
        download_thread.start()

   
    def reset(self):
        self.video_url.set("")  
        self.download_dir.set("")  
        self.url_field.focus_set()  
    
    def exit(self):  
        self.destroy()
        
    def __init__(self):
        super().__init__()

        
    
        # setting the title of the window  
        self.title("YouTube Downloader By WAHIB M.")  
    
        # setting the size and position of the window  
        self.geometry("580x380+700+250")  
    
        # disabling the resizable option for better UI  
        self.resizable(0, 0)  
    
        # configuring the background color of the window  
        self.config(bg = "#FEE4E3")  
        
    
        # configuring the icon of the window  
        ##self.iconbitmap("download1.ico")  
    
        # adding frames to the window using the Frame() widget  
        header_frame = tk.Frame(self, bg = "#FEE4E3") 
        self.image_frame = tk.Frame(self, bg = "#FEE4E3")  
        self.entry_frame = tk.Frame(self, bg = "#FEE4E3")  
        button_frame = tk.Frame(self, bg = "#FEE4E3")  
        progress_frame = tk.Frame(self, bg = "#FEE4E3")
    
        # using the pack() method to set the positions of the frames  
        header_frame.pack() 
        self.image_frame.pack()   
        self.entry_frame.pack()  
        button_frame.pack()  
        progress_frame.pack()
    
        # ------------------------- the header_frame frame -------------------------  
        
        
        header_label = tk.Label(  
            header_frame,  
            text = "YouTube Video Downloader",  
            font = ("verdana", "14", "bold"),  
            bg = "#FEE4E3",  
            anchor = tk.SE  
            )  
    
        # using the grid() method to set the position of the labels in the grid format
        header_label.grid(row = 0, column = 1, padx = 10, pady = 10)  
    
        # ------------------------- the self.entry_frame frame -------------------------  
    
        # adding the labels to the self.entry_frame frame using the Label() widget  
        url_label = tk.Label(  
            self.entry_frame,  
            text = "Video URL:",  
            font = ("verdana", "10"),  
            bg = "#FEE4E3",  
            fg = "#000000",  
            anchor = tk.SE  
            )  
        des_label = tk.Label(  
            self.entry_frame,  
            text = "Destination:",  
            font = ("verdana", "10"),  
            bg = "#FEE4E3",  
            fg = "#000000",  
            anchor = tk.SE  
            )  
        
        
        
    
        # using the grid() method to set the position of the labels in the grid format  
        url_label.grid(row = 0, column = 0, padx = 5, pady = 5, sticky = tk.E)  
        des_label.grid(row = 1, column = 0, padx = 5, pady = 5, sticky = tk.E)  
        
    
        # creating the objects of the StringVar() class  
        self.video_url = tk.StringVar()  
        self.download_dir = tk.StringVar()  
    
        # adding the entry fields to the self.entry_frame frame using the Entry() widget  
        self.url_field = tk.Entry(  
            self.entry_frame,  
            textvariable = self.video_url,  
            width = 35,  
            font = ("verdana", "10"),  
            bg = "#FFFFFF",  
            fg = "#000000",  
            relief = tk.GROOVE  
            )  
        des_field = tk.Entry(  
            self.entry_frame,  
            textvariable = self.download_dir,  
            width = 26,  
            font = ("verdana", "10"),  
            bg = "#FFFFFF",  
            fg = "#000000",  
            relief = tk.GROOVE  
            )  
        

        # using the grid() method to set the position of the entry fields in the grid format  
        self.url_field.grid(row = 0, column = 1, padx = 5, pady = 5, columnspan = 2)  
        des_field.grid(row = 1, column = 1, padx = 5, pady = 5) 
        
        resolution = tk.StringVar()
        
        
        
        self.resolutions_fields = ttk.Combobox(self.entry_frame, state= "readonly", width = 20, font = ("verdana", "8"))
        
        # adding a button to the self.entry_frame frame using the Button() widget  
        browse_button = tk.Button(  
            self.entry_frame,  
            text = "Browse",  
            width = 7,  
            font = ("verdana", "10"),  
            bg = "#FF9200",  
            fg = "#FFFFFF",  
            activebackground = "#FFE0B7",  
            activeforeground = "#000000",  
            relief = tk.GROOVE,  
            command = self.browse_folder  
            )  
        
        
        # using the grid() method to set the position of the button in the grid format  
        browse_button.grid(row = 1, column = 2, padx = 5, pady = 5)  
        
        
        self.style = ttk.Style(self)
        self.style.layout('text.Horizontal.TProgressbar',
                    [('Horizontal.Progressbar.trough',
                    {'children': [('Horizontal.Progressbar.pbar',
                                    {'side': 'left', 'sticky': 'ns'})],
                        'sticky': 'nswe'}),
                    ('Horizontal.Progressbar.label', {'sticky': ''})])
        self.style.configure('text.Horizontal.TProgressbar', text='0 %')

        self.progress_bar = ttk.Progressbar(progress_frame,   orient = tk.HORIZONTAL, style='text.Horizontal.TProgressbar',
                length = 250, mode = 'determinate')
        
        self.progress_bar.grid(column=0, row=0, columnspan=2, padx=10, pady=20)
        
        #hide the progress bar
        self.progress_bar.grid_remove()
        
        
        # ------------------------- the button_frame frame -------------------------  
    
        # adding the buttons to the button_frame frame using the Button() widget  
        download_button = tk.Button(  
            button_frame,  
            text = "Download",  
            width = 12,  
            font = ("verdana", "10"),  
            bg = "#15EF5F",  
            fg = "#FFFFFF",  
            activebackground = "#97F9B8",  
            activeforeground = "#000000",  
            relief = tk.GROOVE,  
            command = self.download_video_thread  
            )  
        reset_button = tk.Button(  
            button_frame,  
            text = "Clear",  
            width = 12,  
            font = ("verdana", "10"),  
            bg = "#23B1E6",  
            fg = "#FFFFFF",  
            activebackground = "#C3E6EF",  
            activeforeground = "#000000",  
            relief = tk.GROOVE,  
            command = self.reset  
            )  
        close_button = tk.Button(  
            button_frame,  
            text = "Exit",  
            width = 12,  
            font = ("verdana", "10"),  
            bg = "#F64247",  
            fg = "#FFFFFF",  
            activebackground = "#F7A2A5",  
            activeforeground = "#000000",  
            relief = tk.GROOVE,  
            command = self.exit  
            )  
    
        # using the grid() method to set the position of the buttons in the grid format  
        download_button.grid(row = 0, column = 0, padx = 5, pady = 10)  
        reset_button.grid(row = 0, column = 1, padx = 5, pady = 10)  
        close_button.grid(row = 0, column = 2, padx = 5, pady = 10)  
        




if __name__ == "__main__":
    app = YoutubeDownloadWindow()
    app.mainloop()
