from tkinter import Tk, Label, Entry, Button
from PIL import Image, ImageTk
from tkinter import filedialog

# Initialize Tkinter window
root = Tk()
root.geometry("600x600")

# Create the label to display the image
label = Label(root, bg="gray", width=600, height=400)
label.grid(row=1, columnspan=6)

# Global variable to store the currently loaded image
current_image = None
original_image = None
tk_img = None

def upload_image():
    global current_image
    global original_image
    file_path = filedialog.askopenfilename()
    
    if file_path:
        # Open image file
        current_image = Image.open(file_path).convert("RGB")
        original_image = Image.open(file_path).convert("RGB")
        # Create a label and add the image to it
        
        update_main_image(current_image)


def update_main_image(im):
    """Update the main image on the label."""
    global tk_img
    # Resize the image to fit within the window dimensions
    # Convert the image to Tkinter format
    tk_img = ImageTk.PhotoImage(im)
    # Update the label with the new image
    label.config(image=tk_img)


uploadButton = Button(root, text="Upload", command= upload_image)
uploadButton.grid(row=0,column=0)
 
def removeRed(im, red_amount):
    # Remove the red of each pixel and create a new image
    width, height = im.size
    pixels = list(im.getdata())
    newPixels = []
    for p in pixels:
        (r,g,b) = p
        # Using 'red_amount' red
        newPixels.append((red_amount,g,b))
    im2 = Image.new("RGB", (width,height))
    im2.putdata(newPixels)
    return im2

def filter1():
    global current_image
    if current_image is not None:
        red_to_remove = int(red_amount.get())
        if 0 <= red_to_remove <= 255:
            # Apply the filter to the current image
            current_image = removeRed(current_image, red_to_remove)
            # Update the main display with the filtered image
            update_main_image(current_image)

def filter2():
    pass
def filter3():
    pass
def filter4():
    pass
def filter5():
    pass
def filter6():
    global current_image
    if current_image is not None:
        # Apply the filter to the current image
        current_image = original_image
        # Update the main display with the filtered image
        update_main_image(current_image)

 
button1 = Button(root , text="Remove Red", command=filter1)

red_amount = Entry(root, textvariable="Red Amount")
red_amount.grid(row=4, column=0)  

button2 = Button(root , text="Filter2", command=filter2)
button3 = Button(root , text="Filter3", command=filter3)
button4 = Button(root , text="Filter4", command=filter4)
button5 = Button(root , text="Filter5", command=filter5)
button6 = Button(root, text="Reset", command=filter6)

button1.grid(row=3,column=0)
button2.grid(row=3,column=1)
button3.grid(row=3,column=2)
button4.grid(row=3,column=3)
button5.grid(row=3,column=4)
button6.grid(row=3,column=5)
 
 
# Run the window's main loop
root.mainloop()