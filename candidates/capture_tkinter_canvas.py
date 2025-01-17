import tkinter as tk

# tkinter is made with TCL, which is a GUI library that specializes in integrating with your OS environment to make windows that follow your OS's style. It streamlines the process of creating and managing windows, getting input, using fonts, and layout management. Since TCL emphasizes looks and simplicity, it's really slow.

def main():
    
    def on_key_press(event):
        """Handles key press events and displays the pressed key."""
        canvas.delete("all")  # Clear the canvas
        canvas.create_text(200, 200, text=event.char, font=("Arial", 300), fill="black")  # Display the key

    # Create the main window
    root = tk.Tk()
    root.title("Keypress Display")
    root.geometry("400x400")
    root.configure(bg="white")

    # Create a canvas for drawing
    canvas = tk.Canvas(root, width=400, height=400, bg="white")
    canvas.pack()

    # Bind key press events
    root.bind("<KeyPress>", on_key_press)

    # Run the application
    root.mainloop()

if __name__ == "__main__":
    main()