import tkinter as tk
from tkinter import ttk
from PIL import ImageTk, Image
from plot_alt_keo import plot
from plot_temp_mlt import plot_temp_mlt
from plot_polar_mlt import plot_polar_mlt
import idlsave 
from tkinter.filedialog import askopenfilename
from spacepy.pybats import gitm as bin_gitm

SMC_FILE = '[ None Selected ]'
gitm = None

#def gitm_from_binary():
#    gitm['']

def plot_alt_keo(entries, image_label):
    althigh = float(entries['althigh'].get())
    altlow = float(entries['altlow'].get())
    latslow = float(entries['latslow'].get())
    latshigh = float(entries['latshigh'].get())
    lonlow = float(entries['lonlow'].get())
    lonhigh = float(entries['lonhigh'].get())
    gtimelow = float(entries['gtimelow'].get())
    gtimeshigh = float(entries['gtimeshigh'].get())
    mltplot = float(entries['mltplot'].get())

    img_file = plot(gitm, althigh, altlow, latslow, latshigh, lonlow, lonhigh, gtimelow, gtimeshigh, mltplot)

    set_image(image_label, img_file)

def plot_polar(entries, image_label):
    altset = float(entries['altset'].get())
    latslow = float(entries['latslow'].get())
    latshigh = float(entries['latshigh'].get())
    lonlow = float(entries['lonlow'].get())
    lonhigh = float(entries['lonhigh'].get())
    gtimelow = float(entries['gtimelow'].get())
    gtimeshigh = float(entries['gtimeshigh'].get())
    nmlt = int(entries['nmlt'].get())
    nlat = int(entries['nlat'].get())

    img_file = plot_polar_mlt(gitm, altset, latslow, latshigh, lonlow, lonhigh, gtimelow, gtimeshigh, nmlt, nlat)

    set_image(image_label, img_file)

def plot_temp(entries, image_label):
    altset = float(entries['altset'].get())
    latslow = float(entries['latslow'].get())
    latshigh = float(entries['latshigh'].get())
    lonlow = float(entries['lonlow'].get())
    lonhigh = float(entries['lonhigh'].get())
    gtimelow = float(entries['gtimelow'].get())
    gtimeshigh = float(entries['gtimeshigh'].get())
    nmaglats = int(entries['nmaglats'].get())

    img_file = plot_temp_mlt(gitm, altset, latslow, latshigh, lonlow, lonhigh, gtimelow, gtimeshigh, nmaglats)

    set_image(image_label, img_file)

def makeform(root, fields, titles):
    entries = {}
    for field in fields.keys():
        title = titles[field]
        default_value = fields[field]
        row = tk.Frame(root)
        lab = tk.Label(row, width=25, text=title+": ", anchor='w')
        if field == 'mltplot':
            ent = ttk.Scale(row, style='TickScale', from_=0, to=23, orient=tk.HORIZONTAL)
            ent.set(20)
            row.pack(side=tk.TOP, 
                     fill=tk.X, 
                     padx=5, 
                     pady=5)
            lab.pack(side=tk.LEFT)
            ent.pack(side=tk.LEFT, 
                     expand=tk.NO, 
                     fill=tk.X)
            entries[field] = ent
        else:
            ent = ttk.Entry(row)
            ent.insert(0, "%s" % default_value)
            row.pack(side=tk.TOP, 
                     fill=tk.X, 
                     padx=5, 
                     pady=5)
            lab.pack(side=tk.LEFT)
            ent.pack(side=tk.LEFT, 
                     expand=tk.NO, 
                     fill=tk.X)
            entries[field] = ent


    return entries

def resize(w, h, w_box, h_box, pil_image):
    '''
    resize a pil_image object so it will fit into
    a box of size w_box times h_box, but retain aspect ratio
    '''
    f1 = 1.0*w_box/w  # 1.0 forces float division in Python2
    f2 = 1.0*h_box/h
    factor = min([f1, f2])
    #print(f1, f2, factor)  # test
    # use best down-sizing filter
    width = int(w*factor)
    height = int(h*factor)
    return pil_image.resize((width, height), Image.ANTIALIAS)

def set_image(label, path):
    w_img_box = 400
    h_img_box = 500
 
    image = Image.open(path)
    
    w, h = image.size
    pil_image_resized = resize(w, h, w_img_box, h_img_box, image)

    img = ImageTk.PhotoImage(pil_image_resized)
    label.configure(image=img)
    label.image = img

def base_frame(root, fields, titles):
    container = tk.Frame(root)
    
    rightContainer = tk.Frame(container)
    
    w_img_box = 400
    h_img_box = 500
    image = Image.open('placeholder.jpg')
    w, h = image.size
    pil_image_resized = resize(w, h, w_img_box, h_img_box, image)
    img = ImageTk.PhotoImage(pil_image_resized)  

    label = tk.Label(rightContainer, image=img, width=w_img_box, height=h_img_box)
    label.pack(padx=20, pady=5)
    rightContainer.pack(side=tk.RIGHT)

    leftContainer = tk.Frame(container)
    ents = makeform(leftContainer, fields, titles)
    leftContainer.pack(side=tk.LEFT)
    return (container, ents, label)
    

def temp_frame(root):
    # Field names for alt_keo and default values
    temp_fields = { 
        'altset': 190, 
        'latslow': 40, 
        'latshigh': 90, 
        'lonlow': 0, 
        'lonhigh': 360, 
        'gtimelow': -1042.5, 
        'gtimeshigh': -1042.25,  
        'nmaglats': 80,
        }

    temp_titles = { 
        'altset': 'Altitude', 
        'latslow': 'Latitude (Lower Bound)', 
        'latshigh': 'Latitude (Upper Bound)', 
        'lonlow': 'Longitude (Lower Bound)' , 
        'lonhigh': 'Latitude (Upper Bound)', 
        'gtimelow': 'Julien Time (Lower Bound)',  
        'gtimeshigh': 'Julien Time (Upper Bound)',
        'nmaglats': 'Number Mag Lats'
        }

    base, ents, image = base_frame(root, temp_fields, temp_titles)
    b1 = ttk.Button(base, text='Plot',
           command=(lambda e=ents: plot_temp(e, image)))
    b1.pack(side=tk.LEFT, padx=5, pady=5)
    return base

def polar_frame(root):
    # Field names for alt_keo and default values
    polar_fields = { 
        'altset': 120, 
        'latslow': 35, 
        'latshigh': 90, 
        'lonlow': 0, 
        'lonhigh': 360, 
        'gtimelow': -1042.5, 
        'gtimeshigh': -1042.25,  
        'nmlt': 25,
        'nlat': 21,
        }

    polar_titles = { 
        'altset': 'Altitude', 
        'latslow': 'Latitude (Lower Bound)', 
        'latshigh': 'Latitude (Upper Bound)', 
        'lonlow': 'Longitude (Lower Bound)' , 
        'lonhigh': 'Latitude (Upper Bound)', 
        'gtimelow': 'Julien Time (Lower Bound)',  
        'gtimeshigh': 'Julien Time (Upper Bound)',
        'nmlt': 'Number MLTs',
        'nlat': 'Number Latitudes'
        }

    base, ents, image = base_frame(root, polar_fields, polar_titles)
    b1 = ttk.Button(base, text='Plot',
           command=(lambda e=ents: plot_polar(e, image)))
    b1.pack(side=tk.LEFT, padx=5, pady=5)
    return base

def alt_keo_frame(root):
    # Field names for alt_keo and default values
    alt_keo_fields = { 
        'althigh': 500, 
        'altlow': 200, 
        'latslow': 40, 
        'latshigh': 90, 
        'lonlow': 0, 
        'lonhigh': 360, 
        'gtimelow': -1042.5,  
        'gtimeshigh': -1042.25,
        'mltplot': 20
        }

    alt_keo_titles = { 
        'althigh': 'Altitude (Upper Bound)', 
        'altlow': 'Altitude (Lower Bound)', 
        'latslow': 'Latitude (Lower Bound)', 
        'latshigh': 'Latitude (Upper Bound)', 
        'lonlow': 'Longitude (Lower Bound)' , 
        'lonhigh': 'Latitude (Upper Bound)', 
        'gtimelow': 'Julien Time (Lower Bound)',  
        'gtimeshigh': 'Julien Time (Upper Bound)',
        'mltplot': 'MLT'
        }
    base, ents, image = base_frame(root, alt_keo_fields, alt_keo_titles)
    b1 = ttk.Button(base, text='Plot',
           command=(lambda e=ents: plot_alt_keo(e, image)))
    b1.pack(side=tk.LEFT, padx=5, pady=5)
    return base

def load_file(file_label):
    global gitm
    SMC_FILE = askopenfilename()
    print(SMC_FILE)
    if '.save' in SMC_FILE:
        gitm = idlsave.read(SMC_FILE)
    elif '.bin' in SMC_FILE:
        # Loading binary
        print('here')
        gitm = bin_gitm.GitmBin(SMC_FILE)
        for key in gitm.keys():
            print(key)

    file_label.configure(text="Data File: %s" % SMC_FILE)


if __name__ == '__main__':
    root = tk.Tk()
    root.tk.call('source', 'azure-dark.tcl')
    # Set the theme with the theme_use method
    ttk.Style().theme_use('azure-dark')

    root.title('GITM Visualization Helper')

    
    file_container = ttk.Frame(root, style='Card')
    file_label = tk.Label(file_container, width=100, text="Data File: %s" % SMC_FILE, anchor='w')
    b1 = ttk.Button(file_container, text='Load File',
           command=(lambda : load_file(file_label)))
    file_label.pack(side=tk.LEFT, padx=5, pady=5)
    b1.pack(side=tk.RIGHT, padx=12, pady=5)

    file_container.pack(side=tk.TOP, fill="x", padx=16, pady=16, expand=1,)
    
    # Content setup
    tabControl = ttk.Notebook(root)
    tab1 = alt_keo_frame(tabControl)
    tab2 = polar_frame(tabControl)
    tab3 = temp_frame(tabControl)
    tabControl.add(tab1, text='Alt/Keo')
    tabControl.add(tab2, text='Polar')
    tabControl.add(tab3, text='Temperature')
    tabControl.pack(expand=1, fill="both", padx=16, pady=16)
    
    root.mainloop()
