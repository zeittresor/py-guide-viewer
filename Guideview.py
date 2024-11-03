import tkinter as tk
from tkinter import filedialog, messagebox, colorchooser
import re
import uu
import io
from PIL import Image, ImageTk
import pygame

# Guideview by Zeittresor
# Requirements: Make sure you have installed PIL using "pip install Pillow" as long with PyGame using "pip install pygame".

class AmigaGuideViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("AmigaGuide Viewer")
        self.nodes = {}
        self.current_node = None
        self.history = []
        self.history_index = -1
        self.language = 'en'  # Default language is English
        self.center_text = False  # Whether to center the text
        self.images = []  # Keep references to images to prevent garbage collection
        self.audio_playing = False

        # Initialize pygame mixer for audio playback
        pygame.mixer.init()

        # Create the menu
        self.create_menu()

        # Main frame
        main_frame = tk.Frame(root)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Text widget with scrollbar
        self.text = tk.Text(main_frame, wrap=tk.WORD, font=("Arial", 12))
        self.text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar = tk.Scrollbar(main_frame, command=self.text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.text.config(yscrollcommand=scrollbar.set)

        # Navigation bar
        nav_frame = tk.Frame(root)
        nav_frame.pack(fill=tk.X)

        self.back_button = tk.Button(nav_frame, text=self.get_label('Back'), command=self.go_back)
        self.back_button.pack(side=tk.LEFT)

        self.forward_button = tk.Button(nav_frame, text=self.get_label('Forward'), command=self.go_forward)
        self.forward_button.pack(side=tk.LEFT)

        self.update_nav_buttons()

    def create_menu(self):
        """Creates the menu bar and menus."""
        menubar = tk.Menu(self.root)

        # File menu
        self.file_menu = tk.Menu(menubar, tearoff=0)
        self.file_menu.add_command(label=self.get_label('Open File'), command=self.open_file)
        menubar.add_cascade(label=self.get_label('File'), menu=self.file_menu)

        # Options menu
        self.options_menu = tk.Menu(menubar, tearoff=0)
        self.options_menu.add_command(label=self.get_label('Background Color'), command=self.change_background_color)
        # Language submenu
        self.language_menu = tk.Menu(self.options_menu, tearoff=0)
        self.language_menu.add_command(label='English', command=lambda: self.change_language('en'))
        self.language_menu.add_command(label='Deutsch', command=lambda: self.change_language('de'))
        self.language_menu.add_command(label='Français', command=lambda: self.change_language('fr'))
        self.options_menu.add_cascade(label=self.get_label('Language'), menu=self.language_menu)
        self.options_menu.add_checkbutton(label=self.get_label('Center Text'), command=self.toggle_center_text)
        menubar.add_cascade(label=self.get_label('Options'), menu=self.options_menu)

        self.root.config(menu=menubar)

    def get_label(self, text):
        """Returns the label text based on the selected language."""
        labels = {
            'en': {
                'File': 'File',
                'Open File': 'Open File',
                'Options': 'Options',
                'Background Color': 'Background Color',
                'Language': 'Language',
                'Center Text': 'Center Text',
                'Back': 'Back',
                'Forward': 'Forward',
                'No valid nodes found in the file.': 'No valid nodes found in the file.',
                'Warning': 'Warning',
                'Error': 'Error',
                'File not found.': 'File not found.',
                'Error loading file:': 'Error loading file:',
                'Node not found.': "Node not found.",
                'Open AmigaGuide File': 'Open AmigaGuide File',
                'Choose Background Color': 'Choose Background Color',
            },
            'de': {
                'File': 'Datei',
                'Open File': 'Datei öffnen',
                'Options': 'Optionen',
                'Background Color': 'Hintergrundfarbe',
                'Language': 'Sprache',
                'Center Text': 'Zentrieren',
                'Back': 'Zurück',
                'Forward': 'Vorwärts',
                'No valid nodes found in the file.': 'Keine gültigen Knoten in der Datei gefunden.',
                'Warning': 'Warnung',
                'Error': 'Fehler',
                'File not found.': 'Datei nicht gefunden.',
                'Error loading file:': 'Fehler beim Laden der Datei:',
                'Node not found.': "Knoten nicht gefunden.",
                'Open AmigaGuide File': 'AmigaGuide-Datei öffnen',
                'Choose Background Color': 'Hintergrundfarbe wählen',
            },
            'fr': {
                'File': 'Fichier',
                'Open File': 'Ouvrir le fichier',
                'Options': 'Options',
                'Background Color': 'Couleur de fond',
                'Language': 'Langue',
                'Center Text': 'Centrer le texte',
                'Back': 'Précédent',
                'Forward': 'Suivant',
                'No valid nodes found in the file.': 'Aucun nœud valide trouvé dans le fichier.',
                'Warning': 'Avertissement',
                'Error': 'Erreur',
                'File not found.': 'Fichier non trouvé.',
                'Error loading file:': 'Erreur lors du chargement du fichier :',
                'Node not found.': "Nœud non trouvé.",
                'Open AmigaGuide File': 'Ouvrir le fichier AmigaGuide',
                'Choose Background Color': 'Choisir la couleur de fond',
            }
        }
        return labels[self.language].get(text, text)

    def open_file(self):
        """Opens a file dialog and loads the selected AmigaGuide file."""
        file_path = filedialog.askopenfilename(
            title=self.get_label("Open AmigaGuide File"),
            filetypes=[("AmigaGuide Files", "*.guide"), ("All Files", "*.*")]
        )
        if file_path:
            self.load_amiga_guide(file_path)
            if "MAIN" in self.nodes:
                self.show_node("MAIN", add_to_history=True)
            elif self.nodes:
                first_node = list(self.nodes.keys())[0]
                self.show_node(first_node, add_to_history=True)
            else:
                messagebox.showwarning(self.get_label("Warning"), self.get_label("No valid nodes found in the file."))

    def change_background_color(self):
        """Opens a color chooser to change the background color."""
        color = colorchooser.askcolor(title=self.get_label("Choose Background Color"))
        if color[1]:
            self.text.config(bg=color[1])

    def change_language(self, lang_code):
        """Changes the language to the selected one."""
        self.language = lang_code
        self.create_menu()
        self.update_labels()

    def update_labels(self):
        """Updates all labels and buttons to reflect the current language."""
        # Update navigation buttons
        self.back_button.config(text=self.get_label('Back'))
        self.forward_button.config(text=self.get_label('Forward'))

        # Update centering if needed
        if self.center_text:
            self.text.tag_configure('center', justify='center')
            self.text.tag_add('center', '1.0', 'end')
        else:
            self.text.tag_configure('center', justify='left')
            self.text.tag_remove('center', '1.0', 'end')

    def toggle_center_text(self):
        """Toggles centering of the text content."""
        self.center_text = not self.center_text
        self.text.tag_configure('center', justify='center')
        if self.center_text:
            self.text.tag_add('center', '1.0', 'end')
        else:
            self.text.tag_remove('center', '1.0', 'end')

    def load_amiga_guide(self, file_path):
        """Parses the AmigaGuide file and stores nodes in a dictionary."""
        self.nodes.clear()
        self.history = []
        self.history_index = -1
        self.stop_audio()  # Stop any playing audio
        try:
            # Open the file with the correct encoding
            with open(file_path, "r", encoding='latin-1') as file:
                content = file.read()

            # Regex for nodes
            nodes = re.findall(r'@node\s+"(.*?)"\s+"(.*?)"(.*?)@endnode', content, re.DOTALL | re.IGNORECASE)
            for name, title, text in nodes:
                self.nodes[name.upper()] = text.strip()

            if not self.nodes:
                messagebox.showwarning(self.get_label("Warning"), self.get_label("No valid nodes found in the file."))
            else:
                print(f"Found nodes: {', '.join(self.nodes.keys())}")

        except FileNotFoundError:
            messagebox.showerror(self.get_label("Error"), f"{self.get_label('File not found.')}: {file_path}")
        except Exception as e:
            messagebox.showerror(self.get_label("Error"), f"{self.get_label('Error loading file:')} {e}")

    def show_node(self, node_name, add_to_history=False):
        """Displays the content of a specific node."""
        node_name = node_name.upper()
        if node_name in self.nodes:
            if add_to_history:
                # Update history when displaying a new node
                # Remove entries after the current index
                self.history = self.history[:self.history_index+1]
                self.history.append(node_name)
                self.history_index += 1

            self.current_node = node_name
            content = self.nodes[node_name]
            self.text.config(state=tk.NORMAL)
            self.text.delete(1.0, tk.END)
            self.insert_content_with_formatting(content)
            self.text.config(state=tk.DISABLED)

            self.update_nav_buttons()
        else:
            messagebox.showwarning(self.get_label("Warning"), f"{self.get_label('Node not found.')}: '{node_name}'")

    def insert_content_with_formatting(self, content):
        """Parses AmigaGuide formatting, links, images, and displays them."""
        self.text.config(state=tk.NORMAL)
        self.text.delete(1.0, tk.END)
        self.images.clear()  # Clear the image references
        pos = 0
        stack = []
        # Counter for unique link tags
        link_counter = 0

        # Replace bullet points and ASCII emojis before processing
        content = self.replace_ascii_emojis(content)

        while pos < len(content):
            # Search for the next tag, link, or uuencoded block
            tag_match = re.search(r'@{\w+}|@{/\w*}|@{"|begin\s+\d+\s+\S+', content[pos:])
            if not tag_match:
                # No more tags, insert remaining text
                text = content[pos:]
                if stack:
                    tags = tuple(stack)
                    self.text.insert(tk.END, text, tags)
                else:
                    self.text.insert(tk.END, text)
                break

            start = pos + tag_match.start()
            end = pos + tag_match.end()
            tag_text = tag_match.group(0)

            # Insert text before the tag
            if start > pos:
                text = content[pos:start]
                if stack:
                    tags = tuple(stack)
                    self.text.insert(tk.END, text, tags)
                else:
                    self.text.insert(tk.END, text)

            # Process the tag
            if tag_text.startswith('@{') and tag_text.endswith('}'):
                # Formatting start or end tag
                tag_content = tag_text[2:-1]
                if tag_content == 'b':
                    stack.append('bold')
                elif tag_content == 'ub':
                    if 'bold' in stack:
                        stack.remove('bold')
                elif tag_content == 'u':
                    stack.append('underline')
                elif tag_content == 'uu':
                    if 'underline' in stack:
                        stack.remove('underline')
                else:
                    # Unknown tag, ignore
                    pass
                pos = end
            elif tag_text == '@{"':
                # Link tag found, parse the entire link
                link_match = re.match(r'@{"(.*?)"\s+link\s+"(.*?)"(?:\s+\d+)?}', content[start:])
                if link_match:
                    link_text = link_match.group(1)
                    link_target = link_match.group(2)
                    link_end = start + link_match.end()

                    # Insert text before the button
                    if stack:
                        tags = tuple(stack)
                    else:
                        tags = ()

                    # Create button
                    btn = tk.Button(
                        self.text,
                        text=link_text,
                        padx=2,
                        pady=0,
                        relief=tk.RAISED,
                        bd=2,
                        fg="blue",
                        cursor="hand2",
                        font=("Arial", 12, "underline")
                    )
                    btn.bind("<Button-1>", lambda e, target=link_target: self.show_node(target, add_to_history=True))

                    # Insert button into the text widget
                    self.text.window_create(tk.END, window=btn)
                    self.text.insert(tk.END, " ", tags)  # Space after the button

                    pos = link_end
                else:
                    # Could not parse the link, insert as normal text
                    self.text.insert(tk.END, tag_text)
                    pos = end
            elif tag_text.startswith('begin'):
                # Possibly a uuencoded block (image or audio)
                uu_match = re.match(r'begin\s+\d+\s+(\S+)(.*?)\nend', content[start:], re.DOTALL)
                if uu_match:
                    filename = uu_match.group(1)
                    uu_data = uu_match.group(2)
                    uu_end = start + uu_match.end()

                    # Decode the uuencoded data
                    try:
                        decoded_data = self.decode_uu_data(f"begin {filename}{uu_data}\nend")
                        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                            # Handle image
                            image = Image.open(io.BytesIO(decoded_data))
                            photo = ImageTk.PhotoImage(image)
                            self.images.append(photo)  # Keep a reference to avoid garbage collection

                            # Insert image into the text widget
                            self.text.image_create(tk.END, image=photo)
                            self.text.insert(tk.END, "\n")  # Newline after the image
                        elif filename.lower().endswith('.mp3'):
                            # Handle audio
                            if self.current_node == 'MAIN':
                                self.play_audio(decoded_data)
                        else:
                            # Unknown file type, insert as text
                            self.text.insert(tk.END, content[start:uu_end])
                    except Exception as e:
                        print(f"Error decoding data: {e}")
                        # Insert the uuencoded data as text if decoding fails
                        self.text.insert(tk.END, content[start:uu_end])

                    pos = uu_end
                else:
                    # Not a valid uuencoded block, insert as text
                    self.text.insert(tk.END, tag_text)
                    pos = end
            else:
                # Unknown tag, insert as text
                self.text.insert(tk.END, tag_text)
                pos = end

        # Apply centering if enabled
        if self.center_text:
            self.text.tag_configure('center', justify='center')
            self.text.tag_add('center', '1.0', 'end')
        else:
            self.text.tag_configure('center', justify='left')
            self.text.tag_remove('center', '1.0', 'end')

    def decode_uu_data(self, uu_content):
        """Decodes uuencoded data and returns bytes."""
        uu_file = io.StringIO(uu_content)
        out_file = io.BytesIO()
        uu.decode(uu_file, out_file)
        return out_file.getvalue()

    def replace_ascii_emojis(self, text):
        """Replaces ASCII emojis with Unicode emojis and bullet points with emojis."""
        # Define a mapping of ASCII emojis to Unicode emojis
        emoji_mapping = {
            ':)': '😊',
            ':-)': '😊',
            ':(': '☹️',
            ':-(': '☹️',
            ':D': '😃',
            ':-D': '😃',
            ';)': '😉',
            ';-)': '😉',
            ':o': '😮',
            ':-o': '😮',
            ':p': '😛',
            ':-p': '😛',
            '<3': '❤️',
            'o/': '👋',
            ':-|': '😐',
            ':|': '😐',
        }

        # Replace bullet points "o " at the beginning of a line with "📌 "
        text = re.sub(r'(?m)^\s*o\s+', '📌 ', text)
        text = re.sub(r'(?m)^\s*-\s+', '• ', text)

        # Replace ASCII emojis
        for ascii_emoji, unicode_emoji in emoji_mapping.items():
            text = text.replace(ascii_emoji, unicode_emoji)

        return text

    def play_audio(self, audio_data):
        """Plays the given audio data (MP3) in a loop."""
        self.stop_audio()
        try:
            # Save audio data to a temporary file-like object
            audio_file = io.BytesIO(audio_data)
            pygame.mixer.music.load(audio_file)
            pygame.mixer.music.play(loops=-1)  # Play indefinitely

            self.audio_playing = True
        except Exception as e:
            print(f"Error playing audio: {e}")
            self.audio_playing = False

    def stop_audio(self):
        """Stops the audio playback if any."""
        if self.audio_playing:
            pygame.mixer.music.stop()
            self.audio_playing = False

    def update_nav_buttons(self):
        """Updates the state of the back and forward buttons."""
        if self.history_index > 0:
            self.back_button.config(state=tk.NORMAL)
        else:
            self.back_button.config(state=tk.DISABLED)

        if self.history_index < len(self.history) - 1:
            self.forward_button.config(state=tk.NORMAL)
        else:
            self.forward_button.config(state=tk.DISABLED)

    def go_back(self):
        """Navigates to the previous node."""
        if self.history_index > 0:
            self.history_index -= 1
            node_name = self.history[self.history_index]
            self.show_node(node_name, add_to_history=False)
        self.update_nav_buttons()

    def go_forward(self):
        """Navigates to the next node."""
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            node_name = self.history[self.history_index]
            self.show_node(node_name, add_to_history=False)
        self.update_nav_buttons()

    def on_closing(self):
        """Handles application closing."""
        self.stop_audio()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = AmigaGuideViewer(root)
    root.geometry("800x600")
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
