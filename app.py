from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
from PIL import Image as PILImage
import os

app = Flask(__name__)

# Configure upload folder
UPLOAD_FOLDER = 'static/uploads'
LOAD_TEMPLATE = 'static/template_images/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['LOAD_TEMPLATE'] = LOAD_TEMPLATE
# Configure processed folder
PROCESSED_FOLDER = 'static/processed'
app.config['PROCESSED_FOLDER'] = PROCESSED_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

# Helper function: Remove red filter
def set_color(im, color_amount, color):
    width, height = im.size
    pixels = list(im.getdata())
    if(color == "red"):
        new_pixels = [(color_amount, g, b) for r, g, b in pixels]
    if(color == "green"):
        new_pixels = [(r, color_amount, b) for r, g, b in pixels]
    if(color == "blue"):
        new_pixels = [(r, g, color_amount) for r, g, b in pixels]
    new_image = PILImage.new("RGB", (width, height))
    new_image.putdata(new_pixels)
    return new_image


def make2D(L, width):
    n_list = []
    group_list = []
    step = 0
    for li in range( len(L) ):
        group_list.append( L[li] )
        step += 1
        if( step == width ):
            n_list.append(group_list)
            group_list = []
            step = 0
    
    if(len(group_list) > 0): 
        n_list.append(group_list)
    return n_list

def flatten(L):
    # 2D list -> 1D list (each row in order)
    new_list = []
    for r in range(len(L)):
        for c in range(len(L[0])):
            new_list.append(L[r][c])
    
    return new_list


def insert(im, smallImage):
    width, height = im.size
    img_data = make2D(list(im.getdata()), width) 

    width_2, height_2 = smallImage.size
    img_2_data = make2D(list(smallImage.getdata()), width_2)

    result_data = []
    img_2_r = 0
    img_2_c = 0
    
    for r in range(height):
        img_2_c = 0
        if (r < height_2 and r):
            for c in range(width):
                if (c < width_2 ):
                    result_data.append(img_2_data[img_2_r][img_2_c])
                    img_2_c += 1
                else: 
                    result_data.append(img_data[r][c])
            img_2_r += 1 
        else:
            for c in range(width):
                result_data.append(img_data[r][c])
            
    im2 = PILImage.new("RGB", (width,height)) 
    im2.putdata(result_data)
    return im2

def rotate_single(img, steps):
    steps = max(1, min(steps, 3))
    pixels = img
    rotated_img = []
    starting = True
    # Using the given parameter steps to rotate n times 90 degrees clockwise.
    while steps > 0:
    # Rotates the 2d list 90 degrees clockwise
        for r in range(len(pixels)-1, -1, -1):
            t_row = []
            # Creates the temporary row, which will be added to rotated_img
            for c in range(len(pixels[0])):
                t_row.append(pixels[r][c])
            
            if (starting == True):
                # Sets the base structure of rotated_img
                for p in range(len(t_row)):
                    rotated_img.append([t_row[p]])
                starting = False
            else :
                # Just adds to the structure
                for p in range(len(t_row)):
                    rotated_img[p].append(t_row[p])
            
        if(steps-1 > 0):
            pixels = rotated_img
            rotated_img = []
            starting = True
            steps -= 1
        else:
            return rotated_img

# Gets one img, and inserts img_2 over img in the given position
# coordinates (row, column) or (y, x)
def insert_image(img, img_2, position): 
    # img is type Image to insert data
    width, height = img.size
    img_data = make2D(list(img.getdata()), width)
    
    # Takes a Image object or a 2d list
    if(type(img_2) == list):
        height_2 = len(img_2)
        width_2 = len(img_2[0])
        img_data_2 = img_2
    else:
        width_2, height_2 = img_2.size
        img_data_2 = make2D(list(img_2.getdata()), width_2)
    
    
    # Setting coordinates limits
    if (position[0] + height_2 > height): 
        position = ((height - height_2), position[1])
        
    if (position[1] + width_2 > width): 
        position = (position[0], (width - width_2))
    
    if (position[0] < 0): 
        position = (0, position[1])
        
    if (position[1] < 0): 
        position = (position[0], 0)
    
    result_data = []
    img_2_r = 0
    img_2_c = 0
    
    # Inserting data into result_data depending on the position
    for r in range(height):
        img_2_c = 0
        if (r >= position[0] and r < (position[0] + width_2)):
            for c in range(width):
                if (c >= position[1] and c < (position[1] + height_2)):
                    result_data.append(img_data_2[img_2_r][img_2_c])
                    img_2_c += 1
                else: 
                    result_data.append(img_data[r][c])
            img_2_r += 1 
        else:
            for c in range(width):
                result_data.append(img_data[r][c])
    if(type(img_2) == list):
        return result_data
    else:
        output_img = PILImage.new("RGB", (width, height))
        output_img.putdata(result_data)
        return output_img

def rotate(im):
    # Creates 4 copies of the Image, rotated in different directions
    width, height = im.size
    pixels = make2D(list(im.getdata()), width)

    final_img = PILImage.new("RGB", (width*2, height*2))
    final_img_data = []

    # Images, a 2d list [image, (coordinates)] in order: left-right, top-bottom
    # coordinates organized (row, column) or (y, x).
    # images order in list: 270-degrees, 0-degrees, 90-degrees, 180-degrees
    images = [
                [ rotate_single(pixels, 3), (0, 0) ],
                [ pixels, (0, width) ],
                [ rotate_single(pixels, 1), (height, width) ],
                [ rotate_single(pixels, 2), (height, 0) ]
            ]
    # Inserting images and saving the data together
    for image in images:
        final_img_data = insert_image(final_img, image[0], image[1])
        final_img.putdata(final_img_data)
    return final_img


# Route: Image processing
@app.route("/", methods=["GET", "POST"])
def index():
    image_url = None
    template_images = [
                        "blur.jpg",
                        "checkerboard.jpg",
                        "emboss.jpg",
                        "high_pass.jpg",
                        "outline.jpg",
                        "sharpen.jpg",
                        "x_y_edge.jpg"
                    ]
    
    server_error = None
    
    mask_settings = {   
                        "status": False,
                        "size": None,
                        "data": [],
                    }
    for i in range(len(template_images)):
        template_images[i] = os.path.join(app.config["LOAD_TEMPLATE"], template_images[i])
    if request.method == "POST":
        # Handle file upload for new image
        if "change_image" in request.form and "image" in request.files :
            file = request.files["image"]   
            if file:
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
                file.save(filepath)
                image_url = filepath

        # Handle "Remove Red" filter
        if("set_color" in request.form and not "current_image" in request.form):
            server_error = "Please select an image first."
            
        elif("set_color" in request.form and not request.form.get("red_amount") and not request.form.get("green_amount") and not request.form.get("blue_amount")):
            server_error = "Please insert at least one color value."
            
        elif "set_color" in request.form and "current_image" in request.form:
            current_image_path = request.form["current_image"]
            if os.path.exists(current_image_path):
                im = PILImage.open(current_image_path).convert("RGB")

                red_amount = request.form.get("red_amount")
                green_amount = request.form.get("green_amount")
                blue_amount = request.form.get("blue_amount")
                if(red_amount):
                    processed_image = set_color(im, int(red_amount), "red")
                    
                if(green_amount):
                    processed_image = set_color(im, int(green_amount), "green")
                    
                if(blue_amount):
                    processed_image = set_color(im, int(blue_amount), "blue")
                # Save the processed image
                processed_path = current_image_path.replace("uploads", "processed")
                processed_image.save(processed_path)
                image_url = processed_path


        # Handle "Reset Image"
        if "reset" in request.form and "current_image" in request.form:
            current_image_path = request.form["current_image"]
            if os.path.exists(current_image_path):
                image_url = current_image_path.replace("processed", "uploads")

        # Rotates the image clockwise
        if "rotate" in request.form and "current_image" in request.form:
            current_image_path = request.form["current_image"]
            if os.path.exists(current_image_path):
                im = PILImage.open(current_image_path).convert("RGB")
                if(im.size[0] == im.size[1]):
                    processed_image = rotate(im)
                    processed_path = current_image_path.replace("uploads", "processed")
                    processed_image.save(processed_path)
                    image_url = processed_path
                else:
                    server_error = "The image must have the same width and height."
        elif("rotate" in request.form and not "current_image" in request.form):
            server_error = "Please select an image first."

        if "insert_img" in request.form and "current_image" in request.form:
            current_image_path = request.form["current_image"]
            if os.path.exists(current_image_path):
                file = request.files["little_img"]
                if file:
                    filename = secure_filename(file.filename)
                    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
                    file.save(filepath)
                    x_coordinate = int(request.form.get("x-coordinate", 0))
                    y_coordinate = int(request.form.get("y-coordinate", 0))
                    
                    small_img = PILImage.open(filepath).convert("RGB")
                    im = PILImage.open(current_image_path).convert("RGB")
                    if (im.size[0] - (small_img.size[0] + y_coordinate) < 0 or im.size[1] - (small_img.size[1] + x_coordinate) < 0):
                        server_error = f"Image outside of range. Your bigger image is: {im.size[1]} x {im.size[0]}"

                    processed_image = insert_image(im, small_img, (x_coordinate, y_coordinate))
                    
                    processed_path = current_image_path.replace("uploads", "processed")
                    processed_image.save(processed_path)
                    image_url = processed_path
        elif("insert_img" in request.form and not "current_image" in request.form):
            server_error = "Please select an image first."

        if "set_mask_settings" in request.form:
            mask_size = int(request.form.get("mask_size"))
            # Checks if the size is odd, and must be True.
            if (mask_size % 2 == 1):
                output_mask = []
                # Creates a 2d list to render and apply the mask values into it.
                for row in range(mask_size):
                    output_mask.append([])
                    for col in range(mask_size):
                        output_mask[row].append([])
                mask_settings["status"] = True
                mask_settings["size"] = mask_size
                mask_settings["data"] = output_mask
            else:
                server_error = "The mask size must be an odd number."

    return render_template("index.html",
                        template_images = template_images, 
                        image_url = image_url,
                        server_error = server_error,
                        mask_settings = mask_settings
                        )

if __name__ == "__main__":
    app.run(debug=True)
