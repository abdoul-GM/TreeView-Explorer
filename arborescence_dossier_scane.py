import os
import customtkinter as ctk
from tkinter import filedialog, ttk, messagebox
import subprocess
import platform

# Configuration de l'UI
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class FolderExplorerApp(ctk.CTk):
    
    def __init__(self):
        super().__init__()
        self.title("🗂️ Explorateur de Dossier")
        self.geometry("950x650")
        self.minsize(900, 600)

        # Variables
        self.current_tree_data = ""
        self.folder_selected = ""

        # Interface
        self.create_widgets()

    def create_widgets(self):
        # Barre supérieure
        top_frame = ctk.CTkFrame(self)
        top_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(top_frame, text="🗂️ Explorateur d'Arborescence de Dossier", font=("Arial", 22)).pack(side="left", padx=10)
        ctk.CTkButton(top_frame, text="📁 Choisir un dossier", command=self.browse_folder).pack(side="right", padx=10)
        


        # Zone de recherche
        search_frame = ctk.CTkFrame(self)
        search_frame.pack(fill="x", padx=10, pady=(0, 10))
        self.search_entry = ctk.CTkEntry(search_frame, placeholder_text="🔍 Rechercher dans l’arborescence...", width=400)
        self.search_entry.pack(side="left", padx=10)
        ctk.CTkButton(search_frame, text="Rechercher", command=self.search_tree).pack(side="left")

        # Boutons Copier et Exporter
        bottom_frame = ctk.CTkFrame(self)
        bottom_frame.pack(pady=10)

        # Sous-frame pour contenir les boutons côte à côte
        button_container = ctk.CTkFrame(bottom_frame)
        button_container.pack()

        # Boutons côte à côte centrés
        ctk.CTkButton(button_container, text="📋 Copier l’arborescence", command=self.copy_to_clipboard).pack(side="left", padx=10)
        ctk.CTkButton(button_container, text="📝 Exporter en .txt", command=self.export_tree).pack(side="left", padx=10)

        # Vue arborescente (TreeView)
        self.tree = ttk.Treeview(self)
        self.tree.pack(fill="both", expand=True, padx=20, pady=10)
        self.tree.heading("#0", text="Fichiers & Dossiers", anchor="w")

        # Ouvrir le dossier ou le fichier lorsqu’on double-clique sur un item
        self.tree.bind("<Double-1>", self.open_item)


    def browse_folder(self):
        path = filedialog.askdirectory()
        if path:
            self.folder_count = 0
            self.file_count = 0
            self.folder_selected = path
            self.tree.delete(*self.tree.get_children())  # Clear tree
            self.current_tree_data = self.build_tree(path)
            self.populate_tree(path)

    def copy_to_clipboard(self):
        if not self.current_tree_data:
            messagebox.showwarning("Aucune donnée", "Veuillez d'abord sélectionner un dossier.")
            return
        try:
            self.clipboard_clear()
            self.clipboard_append(f"Arborescence de : {self.folder_selected}\n\n{self.current_tree_data}\n\n")
            self.clipboard_append(f"📁 Dossiers : {self.folder_count} | 📄 Fichiers : {self.file_count}")
        except Exception as e:
            messagebox.showerror("Erreur", f"Échec de la copie :\n{e}")


    def build_tree(self, path, indent=""):
        """Retourne une chaîne texte représentant l’arborescence, dossiers en premier."""
        result = ""
        try:
            items = sorted(os.listdir(path))
        except PermissionError:
            return indent + "🔒 [Permission Denied]\n"

        folders = [item for item in items if os.path.isdir(os.path.join(path, item))]
        files = [item for item in items if not os.path.isdir(os.path.join(path, item))]

        for item in folders:
            self.folder_count += 1
            full_path = os.path.join(path, item)
            result += f"{indent}📁 {item}/\n"
            result += self.build_tree(full_path, indent + "    ")

        for item in files:
            self.file_count += 1
            result += f"{indent}📄 {item}\n"

        return result


    def populate_tree(self, path, parent=""):
        """Ajoute les dossiers puis fichiers dans le TreeView."""
        try:
            items = sorted(os.listdir(path))
            folders = [item for item in items if os.path.isdir(os.path.join(path, item))]
            files = [item for item in items if not os.path.isdir(os.path.join(path, item))]

            for item in folders:
                full_path = os.path.join(path, item)
                node = self.tree.insert(parent, "end", text=f"📁 {item}", open=False)
                self.populate_tree(full_path, node)

            for item in files:
                self.tree.insert(parent, "end", text=f"📄 {item}")

        except PermissionError:
            self.tree.insert(parent, "end", text="🔒 [Permission Denied]")

    def open_item(self, event):
        selected = self.tree.selection()
        if selected:
            path = self._get_full_path(selected[0])
            if os.path.exists(path):
                if platform.system() == "Windows":
                    os.startfile(path)
                elif platform.system() == "Darwin":
                    subprocess.call(["open", path])
                else:  # Linux
                    subprocess.call(["xdg-open", path])

    def _get_full_path(self, item):
        parts = []
        while item:
            parts.insert(0, self.tree.item(item, "text")[2:])
            item = self.tree.parent(item)
        return os.path.join(self.folder_selected, *parts)


    def export_tree(self):
        if not self.current_tree_data:
            messagebox.showwarning("Aucun dossier", "Veuillez d'abord sélectionner un dossier.")
            return

        # Nom du fichier basé sur le dossier scanné
        folder_name = os.path.basename(self.folder_selected.rstrip("/\\"))
        default_filename = f"{folder_name}_arborescence.txt"

        # Chemin proposé par défaut
        export_dir = os.path.join(os.path.expanduser("~"), "Desktop", "Arborescences_Exportée")
        os.makedirs(export_dir, exist_ok=True)  # Crée le dossier s’il n’existe pas

        # Boîte de dialogue avec chemin et nom de fichier préremplis
        default_path = os.path.join(export_dir, default_filename)
        file = filedialog.asksaveasfilename(
            initialfile=default_filename,
            initialdir=export_dir,
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt")]
        )

        if file:
            try:
                with open(file, "w", encoding="utf-8") as f:
                    f.write(f"Arborescence de : {self.folder_selected}\n\n")
                    f.write(f"📁 Dossiers : {self.folder_count} | 📄 Fichiers : {self.file_count}\n\n")
                    f.write(self.current_tree_data)
                messagebox.showinfo("✅ Exportation réussie", f"Fichier enregistré ici :\n{file}")
            except Exception as e:
                messagebox.showerror("Erreur", f"Échec de l'enregistrement :\n{e}")


    def search_tree(self):
        """Filtre l’affichage du TreeView par mot-clé."""
        keyword = self.search_entry.get().strip().lower()
        
        for item in self.tree.get_children():
            self._search_in_branch(item, keyword)

        if not keyword:
            # Réattache tous les nœuds
            for item in self.tree.get_children():
                self._reattach_all(item)
                self.tree.item(item, open=False)
            return

    def _reattach_all(self, item):
        self.tree.reattach(item, self.tree.parent(item), "end")
        for child in self.tree.get_children(item):
            self._reattach_all(child)

    def _search_in_branch(self, item, keyword):
        text = self.tree.item(item, "text").lower()
        match = keyword in text
        self.tree.item(item, open=match)

        for child in self.tree.get_children(item):
            child_match = self._search_in_branch(child, keyword)
            match = match or child_match

        # Affiche ou cache
        self.tree.detach(item) if keyword and not match else self.tree.reattach(item, self.tree.parent(item), "end")
        return match

# Exécution
if __name__ == "__main__":
    app = FolderExplorerApp()
    app.mainloop()
