from tkinter import *
from tkinter import colorchooser, filedialog, simpledialog
from PIL import Image, ImageDraw, ImageTk
from io import BytesIO
from PIL import ImageGrab



class Whiteboard:
    def __init__(self, root):
        self.root = root
        self.root.title("Whiteboard")

        # Default brush settings
        self.brush_color = "black"
        self.brush_size = 5
        self.active_tool = "brush"
        self.start_pos = None
        self.drawn_items = []
        self.undo_stack = []
        self.redo_stack = []

        # Canvas setup
        self.canvas_width = 800
        self.canvas_height = 600
        self.canvas = Canvas(self.root, width=self.canvas_width, height=self.canvas_height)
        self.canvas.pack()

        # Binding mouse events
        self.canvas.bind("<B1-Motion>", self.draw)
        self.canvas.bind("<ButtonRelease-1>", self.release)

        # Menu setup
        self.menu = Menu(self.root)
        self.root.config(menu=self.menu)

        # File menu
        self.file_menu = Menu(self.menu, tearoff=False)
        self.menu.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_command(label="Save", command=self.save_file)
        self.file_menu.add_command(label="Open", command=self.open_file)

        # Brush menu
        self.brush_menu = Menu(self.menu, tearoff=False)
        self.menu.add_cascade(label="Brush", menu=self.brush_menu)
        self.brush_menu.add_command(label="Color", command=self.change_brush_color)
        self.brush_menu.add_command(label="Size", command=self.change_brush_size)

        # Tool menu
        self.tool_menu = Menu(self.menu, tearoff=False)
        self.menu.add_cascade(label="Tool", menu=self.tool_menu)
        self.tool_menu.add_command(label="Brush", command=self.activate_brush)
        self.tool_menu.add_command(label="Eraser", command=self.activate_eraser)
        self.tool_menu.add_command(label="Line", command=self.activate_line)
        self.tool_menu.add_command(label="Rectangle", command=self.activate_rectangle)
        self.tool_menu.add_command(label="Text", command=self.activate_text)

        # Shape Fill menu
        self.fill_menu = Menu(self.menu, tearoff=False)
        self.menu.add_cascade(label="Shape Fill", menu=self.fill_menu)
        self.fill_menu.add_command(label="Solid Color", command=self.fill_shape)
        self.fill_menu.add_command(label="No Fill", command=self.no_fill_shape)

        # Shape Outline menu
        self.outline_menu = Menu(self.menu, tearoff=False)
        self.menu.add_cascade(label="Shape Outline", menu=self.outline_menu)
        self.outline_menu.add_command(label="Color", command=self.change_outline_color)
        self.outline_menu.add_command(label="Size", command=self.change_outline_size)

        # Selection menu
        self.selection_menu = Menu(self.menu, tearoff=False)
        self.menu.add_cascade(label="Selection", menu=self.selection_menu)
        self.selection_menu.add_command(label="Select", command=self.activate_selection)
        self.selection_menu.add_command(label="Move", command=self.activate_move)

        # Layers menu
        self.layers_menu = Menu(self.menu, tearoff=False)
        self.menu.add_cascade(label="Layers", menu=self.layers_menu)
        self.layers_menu.add_command(label="New Layer", command=self.add_layer)
        self.layers_menu.add_command(label="Delete Layer", command=self.delete_layer)
        self.layers_menu.add_command(label="Move Layer Up", command=self.move_layer_up)
        self.layers_menu.add_command(label="Move Layer Down", command=self.move_layer_down)
        self.layers_menu.add_command(label="Hide Layer", command=self.hide_layer)
        self.layers_menu.add_command(label="Show Layer", command=self.show_layer)

        # Undo and Redo buttons
        self.undo_button = Button(self.root, text="Undo", command=self.undo)
        self.undo_button.pack(side=LEFT)
        self.redo_button = Button(self.root, text="Redo", command=self.redo)
        self.redo_button.pack(side=LEFT)

        # Clear button
        self.clear_button = Button(self.root, text="Clear", command=self.clear_canvas)
        self.clear_button.pack(side=LEFT)

    def draw(self, event):
        if self.active_tool == "brush":
            x1, y1 = (event.x - self.brush_size), (event.y - self.brush_size)
            x2, y2 = (event.x + self.brush_size), (event.y + self.brush_size)
            item = self.canvas.create_oval(x1, y1, x2, y2, fill=self.brush_color, outline=self.brush_color)
            self.drawn_items.append(item)
        elif self.active_tool == "eraser":
            items = self.canvas.find_overlapping(event.x - self.brush_size, event.y - self.brush_size,
                                                 event.x + self.brush_size, event.y + self.brush_size)
            for item in items:
                self.canvas.delete(item)
        elif self.active_tool == "text":
            self.canvas.focus_set()

    def release(self, event):
        if self.active_tool in ["brush", "eraser"]:
            self.save_to_undo_stack()
        elif self.active_tool == "text":
            text = simpledialog.askstring("Text Input", "Enter text:")
            if text:
                x, y = event.x, event.y
                item = self.canvas.create_text(x, y, text=text, fill=self.brush_color)
                self.drawn_items.append(item)
                self.save_to_undo_stack()

    def change_brush_color(self):
        color = colorchooser.askcolor(initialcolor=self.brush_color)
        if color[1] is not None:
            self.brush_color = color[1]

    def change_brush_size(self):
        size = simpledialog.askinteger("Brush Size", "Enter brush size:", initialvalue=self.brush_size)
        if size is not None:
            self.brush_size = size

    def activate_brush(self):
        self.active_tool = "brush"

    def activate_eraser(self):
        self.active_tool = "eraser"

    def activate_line(self):
        self.active_tool = "line"
        self.canvas.bind("<Button-1>", self.start_shape)
        self.canvas.bind("<ButtonRelease-1>", self.end_shape)

    def activate_rectangle(self):
        self.active_tool = "rectangle"
        self.canvas.bind("<Button-1>", self.start_shape)
        self.canvas.bind("<ButtonRelease-1>", self.end_shape)

    def activate_text(self):
        self.active_tool = "text"

    def fill_shape(self):
        if self.drawn_items:
            for item in self.drawn_items:
                self.canvas.itemconfig(item, fill=self.brush_color)

    def no_fill_shape(self):
        if self.drawn_items:
            for item in self.drawn_items:
                self.canvas.itemconfig(item, fill="")

    def change_outline_color(self):
        color = colorchooser.askcolor(initialcolor=self.brush_color)
        if color[1] is not None:
            self.brush_color = color[1]
            if self.drawn_items:
                for item in self.drawn_items:
                    self.canvas.itemconfig(item, outline=self.brush_color)

    def change_outline_size(self):
        size = simpledialog.askinteger("Outline Size", "Enter outline size:", initialvalue=self.brush_size)
        if size is not None:
            self.brush_size = size
            if self.drawn_items:
                for item in self.drawn_items:
                    self.canvas.itemconfig(item, width=self.brush_size)

    def activate_selection(self):
        self.active_tool = "selection"
        self.canvas.bind("<Button-1>", self.start_selection)
        self.canvas.bind("<ButtonRelease-1>", self.end_selection)

    def activate_move(self):
        self.active_tool = "move"
        self.canvas.bind("<Button-1>", self.start_move)

    def start_selection(self, event):
        self.start_pos = (event.x, event.y)

    def end_selection(self, event):
        x1, y1 = self.start_pos
        x2, y2 = event.x, event.y
        items = self.canvas.find_enclosed(x1, y1, x2, y2)
        self.canvas.select_clear()
        for item in items:
            self.canvas.select_item(item)

    def start_move(self, event):
        item = self.canvas.find_closest(event.x, event.y)[0]
        self.canvas.move(item, 0, 0)  # Bring the item to the top
        self.start_pos = (event.x, event.y)

    def add_layer(self):
        layer = Frame(self.root, bd=1, relief=SUNKEN)
        layer.pack(side=LEFT)
        canvas = Canvas(layer, width=self.canvas_width, height=self.canvas_height)
        canvas.pack()
        self.canvas.bind("<Button-1>", lambda event: self.start_shape(event, canvas))
        self.canvas.bind("<ButtonRelease-1>", lambda event: self.end_shape(event, canvas))

    def delete_layer(self):
        if len(self.root.pack_slaves()) > 1:
            layer = self.root.pack_slaves()[-1]
            layer.pack_forget()

    def move_layer_up(self):
        layers = self.root.pack_slaves()
        if len(layers) > 1:
            current_layer = layers[-1]
            current_layer.pack_forget()
            current_layer.pack(side=LEFT)

    def move_layer_down(self):
        layers = self.root.pack_slaves()
        if len(layers) > 1:
            current_layer = layers[-1]
            next_layer = layers[-2]
            current_layer.pack_forget()
            current_layer.pack(in_=next_layer, side=LEFT)

    def hide_layer(self):
        layers = self.root.pack_slaves()
        if len(layers) > 1:
            current_layer = layers[-1]
            current_layer.pack_forget()

    def show_layer(self):
        layers = self.root.pack_slaves()
        if len(layers) > 1:
            current_layer = layers[-1]
            current_layer.pack(side=LEFT)

    def start_shape(self, event, canvas=None):
        self.start_pos = (event.x, event.y)
        if canvas:
            self.canvas = canvas

    def end_shape(self, event, canvas=None):
        if self.active_tool == "line":
            self.canvas.create_line(self.start_pos[0], self.start_pos[1], event.x, event.y,
                                    fill=self.brush_color, width=self.brush_size)
        elif self.active_tool == "rectangle":
            self.canvas.create_rectangle(self.start_pos[0], self.start_pos[1], event.x, event.y,
                                          fill=self.brush_color, outline=self.brush_color)
        if canvas:
            self.canvas = self.root.pack_slaves()[-1]
        self.save_to_undo_stack()

    def save_to_undo_stack(self):
        image = self.get_canvas_image()
        self.undo_stack.append(image)
        self.redo_stack = []

    def undo(self):
        if len(self.undo_stack) > 1:
            image = self.undo_stack.pop()
            self.redo_stack.append(image)
            self.load_canvas_image(self.undo_stack[-1])

    def redo(self):
        if self.redo_stack:
            image = self.redo_stack.pop()
            self.undo_stack.append(image)
            self.load_canvas_image(image)

    def save_file(self):
        filename = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG Files", "*.png")])
        if filename:
            image = self.get_canvas_image()
            image.save(filename)

    def open_file(self):
        filename = filedialog.askopenfilename(filetypes=[("Image Files", "*.png *.jpg *.jpeg")])
        if filename:
            image = Image.open(filename)
            self.canvas.delete("all")
            self.canvas_image = ImageTk.PhotoImage(image)
            self.canvas.create_image(0, 0, anchor=NW, image=self.canvas_image)
            self.undo_stack = [image]

    def clear_canvas(self):
        self.canvas.delete("all")
        self.drawn_items = []
        self.undo_stack = []
        self.redo_stack = []

    def get_canvas_image(self):
        self.canvas.update()
        image = ImageGrab.grab(self.canvas.winfo_rootx(), self.canvas.winfo_rooty(),
                               self.canvas.winfo_rootx() + self.canvas_width,
                               self.canvas.winfo_rooty() + self.canvas_height)
        return image

    def load_canvas_image(self, image):
        self.canvas.delete("all")
        self.canvas_image = ImageTk.PhotoImage(image)
        self.canvas.create_image(0, 0, anchor=NW, image=self.canvas_image)
        self.drawn_items = []

root = Tk()
app = Whiteboard(root)
root.mainloop()
