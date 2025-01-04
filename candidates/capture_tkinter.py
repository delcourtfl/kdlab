import tkinter as tk

# tkinter is made with TCL, which is a GUI library that specializes in integrating with your OS environment to make windows that follow your OS's style. It streamlines the process of creating and managing windows, getting input, using fonts, and layout management. Since TCL emphasizes looks and simplicity, it's really slow.

def main():
    
    def on_key_press(event):
        """Handles key press events and displays the pressed key."""
        label.config(text=event.char)  # Update the label with the pressed key

    # Create the main window
    root = tk.Tk()
    root.title("Keypress Display")
    root.geometry("400x400")
    root.configure(bg="white")

    label = tk.Label(root, text='', font=("Arial", 300), bg="white", fg="black")
    label.pack(expand=True)

    # Bind key press events
    root.bind("<KeyPress>", on_key_press)

    # Run the application
    root.mainloop()

if __name__ == "__main__":
    main()