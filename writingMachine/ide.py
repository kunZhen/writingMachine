import os
import tkinter as tk
from tkinter import filedialog, messagebox

# Global variables for main window, right panel text widget, and current file
window = None
text_right = None
current_file = None

def init_ide():
    global file_listbox, window, text_right  # Reference global variables

    # Create the main window
    window = tk.Tk()
    window.title("Champi")
    window.geometry("1000x800")

    # Set the icon for the window
    icon = tk.PhotoImage(file="icon.png")
    window.iconphoto(False, icon)

    # Create a toolbar at the top
    toolbar = tk.Frame(window, bg="gray30")
    toolbar.pack(side=tk.TOP, fill=tk.X)

    # Button to import files
    import_button = tk.Button(toolbar, text="Import", command=import_file,
                              bg="gray60", fg="black", padx=20, pady=5, font=("Arial", 7))
    import_button.pack(side=tk.LEFT, padx=10, pady=5)

    # Button to create a new file
    new_button = tk.Button(toolbar, text="New", command=create_new_file,
                           bg="gray60", fg="black", padx=20, pady=5, font=("Arial", 7))
    new_button.pack(side=tk.LEFT, padx=10, pady=5)

    # Button to save the current file
    save_button = tk.Button(toolbar, text="Save", command=save_file,
                            bg="gray60", fg="black", padx=20, pady=5, font=("Arial", 7))
    save_button.pack(side=tk.LEFT, padx=10, pady=5)

    # Button to compile code
    compile_button = tk.Button(toolbar, text="Compile", command=compile_code,
                               bg="gray60", fg="black", padx=20, pady=5, font=("Arial", 7))
    compile_button.pack(side=tk.LEFT, padx=10, pady=5)

    # Create a main pane window to split the window into two sections
    paned_main = tk.PanedWindow(window, orient=tk.VERTICAL, sashwidth=5, bg="gray")  # Vertical panel
    paned_main.pack(fill=tk.BOTH, expand=True)

    # Top pane (left and right)
    paned_top = tk.PanedWindow(paned_main, orient=tk.HORIZONTAL, sashwidth=5, bg="gray")

    # Create frame for the left panel
    frame_left = tk.Frame(paned_top, bg="lightgray")
    frame_left.pack(fill=tk.BOTH, expand=True)

    # Create listbox to display files in the left panel
    file_listbox = tk.Listbox(frame_left, bg="gray50", fg="black", selectbackground="#87CEEB")
    file_listbox.pack(fill=tk.BOTH, expand=True)

    # Load files into the listbox on startup
    load_files(file_listbox)

    # Bind selection event to open the selected file
    file_listbox.bind("<<ListboxSelect>>", lambda event: open_selected_file(file_listbox, text_right))

    # Create frame for the right panel
    frame_right = tk.Frame(paned_top, bg="gray80")
    frame_right.pack(fill=tk.BOTH, expand=True)

    # Create scrollbars for the right panel
    scroll_right_y = tk.Scrollbar(frame_right)
    scroll_right_x = tk.Scrollbar(frame_right, orient=tk.HORIZONTAL)

    # Create text widget in the right panel with line numbers
    line_numbers_right = tk.Text(frame_right, width=4, bg="gray60", fg="black", state="disabled", font=("Consolas", 10),
                                 padx=5, pady=5, bd=0, relief=tk.FLAT)
    line_numbers_right.pack(side=tk.LEFT, fill=tk.Y)

    text_right = tk.Text(frame_right, wrap=tk.NONE, bg="gray60", fg="black", font=("Consolas", 10),
                         padx=5, pady=5, bd=0, relief=tk.FLAT,
                         yscrollcommand=lambda *args: [scroll_right_y.set(*args),
                                                       update_line_numbers(text_right, line_numbers_right)],
                         xscrollcommand=lambda *args: scroll_right_x.set(*args))

    text_right.pack(fill=tk.BOTH, expand=True)

    # Update line numbers on key release or mouse wheel events
    text_right.bind("<KeyRelease>", lambda event: update_line_numbers(text_right, line_numbers_right))
    text_right.bind("<MouseWheel>", lambda event: update_line_numbers(text_right, line_numbers_right))

    # Add the top pane to the main pane
    paned_top.add(frame_left, stretch="always")
    paned_top.add(frame_right, stretch="always")

    paned_top.paneconfig(frame_left, width=300)  # Set width of left panel
    paned_top.paneconfig(frame_right, width=700)

    # Add the top pane to the main pane
    paned_main.add(paned_top, stretch="always")

    # Create frame for the bottom panel (terminal)
    frame_terminal = tk.Frame(paned_main, bg="gray70")
    frame_terminal.pack(fill=tk.BOTH, expand=True)

    # Create scrollbar for the terminal panel
    scroll_terminal_y = tk.Scrollbar(frame_terminal)

    # Create scrollable text widget for the terminal panel
    text_terminal = tk.Text(frame_terminal, wrap=tk.NONE,
                            yscrollcommand=lambda *args: update_scroll(scroll_terminal_y, text_terminal, 'y', *args),
                            bg="gray30", fg="black")
    text_terminal.pack(fill=tk.BOTH, expand=True)

    # Add the terminal frame to the main pane
    paned_main.add(frame_terminal, stretch="always")
    paned_main.paneconfig(frame_terminal, height=200)

    # Start the window loop
    window.mainloop()

def update_scroll(scroll, widget, axis, *args):
    # Update vertical or horizontal scroll position
    if axis == 'y':
        scroll.set(*args)
        widget.update_idletasks()  # Update widget display
        widget.yview_moveto(args[0])  # Update view

    elif axis == 'x':
        scroll.set(*args)
        widget.update_idletasks()  # Update widget display
        widget.xview_moveto(args[0])  # Update view

def update_line_numbers(text_widget, line_numbers_widget):
    # Update line numbers in the left panel
    line_numbers_widget.config(state="normal")
    line_numbers_widget.delete("1.0", "end")

    # Get number of lines in the text widget
    line_count = int(text_widget.index('end').split('.')[0])

    # Insert line numbers aligned with the text
    for i in range(1, line_count):
        line_numbers_widget.insert(f"{i}.0", f"{i:>2}  \n")  # Format line numbers

    line_numbers_widget.config(state="disabled")

def load_files(listbox):
    """Load existing files from the 'files' directory and display in the Listbox"""
    listbox.delete(0, tk.END)  # Clear the listbox
    files = os.listdir("files")
    for file in files:
        if file.endswith(".txt"):  # Show only .txt files
            listbox.insert(tk.END, file)

def create_new_file():
    global text_right, window, current_file  # Reference global variables

    # Prompt user for the new file name
    new_file_name = filedialog.asksaveasfilename(defaultextension=".txt",
                                                 filetypes=[("Text files", "*.txt")],
                                                 initialdir="files",
                                                 title="Create New File")
    if new_file_name:
        # Create an empty file
        with open(new_file_name, 'w') as new_file:
            new_file.write("")  # Empty initially

        # Set the current file
        current_file = new_file_name

        # Clear right panel and allow editing of the new file
        text_right.config(state=tk.NORMAL)
        text_right.delete(1.0, tk.END)  # Clear text
        window.title(f"Champi - {new_file_name}")  # Change window title

        # Reload the file list
        load_files(file_listbox)

def open_selected_file(listbox, text_widget):
    """Open the selected file from the Listbox"""
    global current_file
    selected_file = listbox.get(tk.ACTIVE)
    if selected_file:
        filepath = os.path.join("files", selected_file)
        current_file = filepath  # Set the current file
        with open(filepath, 'r') as file:
            content = file.read()
        text_widget.delete(1.0, tk.END)  # Clear existing text
        text_widget.insert(tk.END, content)  # Load file content
        window.title(f"Champi - {selected_file}")  # Change window title

def save_file():
    global text_right, current_file  # Reference global variables

    if current_file:
        # Get content from the right panel
        content = text_right.get(1.0, tk.END)

        # Save content to the current file
        with open(current_file, 'w') as file:
            file.write(content)

        print(f"File saved: {current_file}")
    else:
        save_as_file()

def save_as_file():
    global current_file
    # Dialog to save the file as
    file_name = filedialog.asksaveasfilename(defaultextension=".txt",
                                             filetypes=[("Text files", "*.txt")],
                                             initialdir="files",
                                             title="Save As")
    if file_name:
        current_file = file_name
        save_file()  # Save to the new file

def import_file():
    global file_listbox

    # Open a file dialog to select a file from any location on the computer
    file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")],
                                           title="Import File")
    if file_path:
        # Get the filename from the selected path
        file_name = os.path.basename(file_path)
        # Define the destination path in the 'files' directory
        destination = os.path.join("files", file_name)

        # Check if the file already exists in the destination folder
        if os.path.exists(destination):
            # Ask the user if they want to overwrite the existing file
            overwrite = input(f"File '{file_name}' already exists. Do you want to overwrite it? (yes/no): ")
            if overwrite.lower() != 'yes':
                return

        try:
            # Read the content from the selected file
            with open(file_path, 'r') as source_file:
                content = source_file.read()
            # Write the content to the destination file
            with open(destination, 'w') as dest_file:
                dest_file.write(content)

            # Reload the file list to reflect the newly imported file
            load_files(file_listbox)
            print(f"File imported successfully: {file_name}")
        except Exception as e:
            # Print an error message if there was an issue during the file import
            print(f"Error importing file: {e}")
def compile_code():
    # Get the content from the text widget
    content = text_right.get(1.0, tk.END)  # Get all text including end-of-line character

    # Split the content into lines
    lines = content.splitlines()

    # Print each line with its line number
    for line_number, line in enumerate(lines, start=1):
        print(f"Line {line_number}: {line}")