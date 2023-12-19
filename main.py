import sqlite3
import tkinter as tk
from tkinter import messagebox, simpledialog
from tkinter import ttk

# ...
DATABASE_FILE = 'datasource.sqlite'


class LoginPage:
    def connect_to_database(self):
        return sqlite3.connect(DATABASE_FILE)

    def __init__(self, root, on_login_success):
        self.root = root
        self.root.title("Page de Connexion")

        # Définir la taille de la fenêtre et le positionnement au centre de l'écran
        window_width = 400
        window_height = 300
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        x_position = (screen_width - window_width) // 2
        y_position = (screen_height - window_height) // 2
        root.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

        # Style pour les widgets ttk
        style = ttk.Style()
        style.configure('TLabel', font=('Arial', 12), foreground='#333')  # Couleur du texte
        style.configure('TEntry', font=('Arial', 12))

        # Couleur de fond de la fenêtre
        root.configure(bg='#f0f0f0')

        # Création des widgets
        self.frame = ttk.Frame(root, padding=(20, 20, 20, 20), style='TFrame')  # Marge intérieure
        self.frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))  # Expansion dans toutes les directions

        self.username_label = ttk.Label(self.frame, text="Nom d'utilisateur:")
        self.username_label.grid(row=0, column=0, padx=10, pady=10, sticky="e")

        self.username_entry = ttk.Entry(self.frame)
        self.username_entry.grid(row=0, column=1, padx=10, pady=10)

        self.password_label = ttk.Label(self.frame, text="Mot de passe:")
        self.password_label.grid(row=1, column=0, padx=10, pady=10, sticky="e")

        self.password_entry = ttk.Entry(self.frame, show="*")
        self.password_entry.grid(row=1, column=1, padx=10, pady=10)

        self.login_button = ttk.Button(self.frame, text="Se Connecter", command=self.login)
        self.login_button.grid(row=2, column=1, pady=10)

        self.create_user_button = ttk.Button(self.frame, text="Enregistrer un nouvel utilisateur",
                                             command=self.create_user)
        self.create_user_button.grid(row=3, column=1, pady=10)



        # Fonction de rappel en cas de connexion réussie
        self.on_login_success = on_login_success

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        conn = self.connect_to_database()
        cursor = conn.cursor()

        # Vous pouvez ajouter ici la logique de vérification des informations de connexion
        # Pour cet exemple, nous supposerons que l'utilisateur est toujours valide
        cursor.execute("SELECT password FROM utilisateur WHERE nom= ?", (username,))
        conn.commit()
        mdp=cursor.fetchone()[0]
        print(mdp)
        cursor.execute("SELECT id FROM utilisateur WHERE nom= ?", (username,))
        usid=cursor.fetchone()[0]
        print(usid)
        if password == mdp:
            messagebox.showinfo("Connexion réussie", "Bienvenue, " + username + "!")
            # Appeler la fonction de rappel en cas de connexion réussie
            cursor.execute("INSERT INTO users (utilisateur) VALUES (?)",(usid,))
            conn.commit()
            self.on_login_success()
        else:
            messagebox.showerror("Erreur de Connexion", "Nom d'utilisateur ou mot de passe incorrect.")

    def create_user(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        conn = self.connect_to_database()
        cursor = conn.cursor()

        cursor.execute("INSERT INTO utilisateur(nom, password) VALUES (?, ?)", (username, password,))
        conn.commit()
        conn.close()
        # Vous pouvez ajouter ici la logique pour enregistrer un nouvel utilisateur
        # Pour cet exemple, affichons simplement un message


class ContactManagerApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Gestionnaire de Contacts")
        self.master = master
        conn = self.connect_to_database()
        cursor = conn.cursor()
        cursor.execute("SELECT utilisateur FROM users ORDER BY id DESC LIMIT 1;")
        last_user = cursor.fetchone()
        self.userid = last_user[0] if last_user else None
        conn.commit()
        cursor.execute("DELETE FROM users WHERE id =(SELECT MAX(id) FROM users)");
        conn.commit()
        conn.close()
        # Couleur de fond pour les boutons
        add_button_color = "#4CAF50"
        update_button_color = "#2196F3"
        delete_button_color = "#FF5722"

        # Configuration des boutons
        button_config = {'fg': 'black', 'command': self.add_user_info, 'border': 5, 'font': ('Helvetica', 12)}

        self.addButton = tk.Button(master, text="Ajouter un contact", bg=add_button_color, **button_config)
        self.addButton.pack(pady=10, padx=20, ipadx=10, fill=tk.X)

        button_config['command'] = self.update_user
        self.updateButton = tk.Button(master, text="Mettre à jour un contact", bg=update_button_color, **button_config)
        self.updateButton.pack(pady=10, padx=20, ipadx=10, fill=tk.X)

        button_config['command'] = self.delete_user_with_confirmation
        self.deleteButton = tk.Button(master, text="Supprimer un contact", bg=delete_button_color, **button_config)
        self.deleteButton.pack(pady=10, padx=20, ipadx=10, fill=tk.X)

        self.search_entry = tk.Entry(master, font=('Helvetica', 12))
        self.search_entry.pack(pady=10, padx=20, ipadx=10, fill=tk.X)
        self.search_entry.bind('<KeyRelease>', lambda event: self.search_users(event))

        self.userListBox = tk.Listbox(master, selectmode=tk.SINGLE, font=('Helvetica', 12))
        self.userListBox.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)

        self.userListBox.bind('<Double-Button-1>', lambda event: self.show_user_details)

        # Ajouter deux boutons pour le tri
        self.sort_alphabetical_button = tk.Button(root, text="Tri alphabétique", command=self.load_users_alphabetical)
        self.sort_alphabetical_button.pack(pady=10, padx=20, ipadx=10, fill=tk.X)

        self.sort_custom_button = tk.Button(root, text="Tri personnalisé", command=self.load_users_custom)
        self.sort_custom_button.pack(pady=10, padx=20, ipadx=10, fill=tk.X)
        self.load_users()


    def connect_to_database(self):
        return sqlite3.connect(DATABASE_FILE)

    def demander_avec_validation(self, question):
        response = messagebox.askquestion("Validation", f"{question} (Oui/Non)")
        return response == 'yes'

    def demander_numero_telephone(self, question):
        while True:
            numero = simpledialog.askstring("Numéro de téléphone", question)
            if numero.isdigit() and len(numero) == 10:
                return numero
            messagebox.showerror("Erreur",
                                 "Numéro invalide. Veuillez entrer un numéro de téléphone valide (10 chiffres).")

    def add_user_info(self):
        conn = self.connect_to_database()
        cursor = conn.cursor()

        # Demander à l'utilisateur s'il souhaite ajouter un nouveau contact
        ajouter_contact = self.demander_avec_validation("Voulez-vous ajouter un nouveau contact ?")

        if not ajouter_contact:
            messagebox.showinfo("Opération annulée", "Opération annulée.")
            conn.close()
            return

        # Créer une fenêtre pour saisir les informations du contact
        user_info_window = tk.Toplevel(self.master)
        user_info_window.title("Ajouter un contact")

        # Utiliser StringVar pour lier les valeurs des Entry
        fname_var = tk.StringVar()
        name_var = tk.StringVar()
        tel1_var = tk.StringVar()
        tel2_var = tk.StringVar()
        email_var = tk.StringVar()
        anniv_var = tk.StringVar()
        notes_var = tk.StringVar()

        # Créer des Labels et Entry pour chaque information
        tk.Label(user_info_window, text="Prénom:").grid(row=0, column=0, sticky="w")
        tk.Entry(user_info_window, textvariable=fname_var).grid(row=0, column=1)

        tk.Label(user_info_window, text="Nom:").grid(row=1, column=0, sticky="w")
        tk.Entry(user_info_window, textvariable=name_var).grid(row=1, column=1)

        tk.Label(user_info_window, text="Numéro principal:").grid(row=2, column=0, sticky="w")
        tk.Entry(user_info_window, textvariable=tel1_var).grid(row=2, column=1)

        tk.Label(user_info_window, text="Numéro secondaire:").grid(row=3, column=0, sticky="w")
        tk.Entry(user_info_window, textvariable=tel2_var).grid(row=3, column=1)

        tk.Label(user_info_window, text="E-mail:").grid(row=4, column=0, sticky="w")
        tk.Entry(user_info_window, textvariable=email_var).grid(row=4, column=1)

        tk.Label(user_info_window, text="Date d'anniversaire:").grid(row=5, column=0, sticky="w")
        tk.Entry(user_info_window, textvariable=anniv_var).grid(row=5, column=1)

        tk.Label(user_info_window, text="Commentaires:").grid(row=6, column=0, sticky="w")
        tk.Entry(user_info_window, textvariable=notes_var).grid(row=6, column=1)

        # Bouton pour valider l'ajout
        tk.Button(user_info_window, text="Ajouter", command=lambda: self.add_user_from_window(user_info_window,
                                                                                            fname_var.get(),
                                                                                            name_var.get(),
                                                                                            tel1_var.get(),
                                                                                            tel2_var.get(),
                                                                                            email_var.get(),
                                                                                            anniv_var.get(),
                                                                                            notes_var.get())).grid(
            row=7, column=0, columnspan=2, pady=10)

        def on_close():
            user_info_window.destroy()
            conn.close()

        user_info_window.protocol("WM_DELETE_WINDOW", on_close)

    def add_user_from_window(self, window, fname, name, tel1, tel2, email, anniv, notes):
        # Ajouter l'utilisateur à la base de données
        conn = self.connect_to_database()
        cursor = conn.cursor()
        print(self.userid)

        # Vérifier si un utilisateur avec le même nom existe déjà
        cursor.execute("SELECT id FROM users WHERE nom = ? AND prenom = ? AND utilisateur = ?",
                       (name, fname, self.userid))
        existing_user = cursor.fetchone()
        print(existing_user)
        if existing_user:
            # Demander à l'utilisateur s'il est sûr de vouloir ajouter un utilisateur existant
            confirmation = messagebox.askquestion("Utilisateur existant",
                                                  "Un utilisateur avec le même nom existe déjà. Voulez-vous quand même ajouter ce contact ?")

            if confirmation == 'no':
                # Fermer la fenêtre
                window.destroy()
                conn.close()
                return

        cursor.execute(
            "INSERT INTO users (prenom, nom, tel1, tel2, mail, bday, notes, utilisateur) VALUES (?, ?, ?, ?, ?, ?, ?,? )",
            (fname, name, tel1, tel2, email, anniv, notes, self.userid))
        conn.commit()

        messagebox.showinfo("Contact ajouté", "Contact ajouté avec succès.")

        # Fermer la fenêtre
        window.destroy()

        # Recharger la liste des utilisateurs
        self.load_users()

    def update_user(self):
        conn = self.connect_to_database()
        cursor = conn.cursor()

        # Demander à l'utilisateur l'ID du contact à modifier
        user_id_to_update = self.get_selected_user_id()

        if user_id_to_update is None:
            messagebox.showinfo("Sélection requise", "Veuillez sélectionner un utilisateur à mettre à jour.")
            conn.close()
            return

        # Créer une fenêtre pour saisir les nouvelles informations du contact
        user_info_window = tk.Toplevel(self.master)
        user_info_window.title("Mettre à jour un contact")

        # Utiliser StringVar pour lier les valeurs des Entry
        fname_var = tk.StringVar()
        name_var = tk.StringVar()
        tel1_var = tk.StringVar()
        tel2_var = tk.StringVar()
        email_var = tk.StringVar()
        anniv_var = tk.StringVar()
        notes_var = tk.StringVar()

        # Récupérer les informations actuelles de l'utilisateur
        cursor.execute("SELECT prenom, nom, tel1, tel2, mail, bday, notes FROM users WHERE id = ?", (user_id_to_update,))
        user_info = cursor.fetchone()

        # Remplir les StringVar avec les informations actuelles
        fname_var.set(user_info[0])
        name_var.set(user_info[1])
        tel1_var.set(user_info[2])
        tel2_var.set(user_info[3])
        email_var.set(user_info[4])
        anniv_var.set(user_info[5])
        notes_var.set(user_info[6])

        # Créer des Labels et Entry pour chaque information
        tk.Label(user_info_window, text="Prénom:").grid(row=0, column=0, sticky="w")
        tk.Entry(user_info_window, textvariable=fname_var).grid(row=0, column=1)

        tk.Label(user_info_window, text="Nom:").grid(row=1, column=0, sticky="w")
        tk.Entry(user_info_window, textvariable=name_var).grid(row=1, column=1)

        tk.Label(user_info_window, text="Numéro principal:").grid(row=2, column=0, sticky="w")
        tk.Entry(user_info_window, textvariable=tel1_var).grid(row=2, column=1)

        tk.Label(user_info_window, text="Numéro secondaire:").grid(row=3, column=0, sticky="w")
        tk.Entry(user_info_window, textvariable=tel2_var).grid(row=3, column=1)

        tk.Label(user_info_window, text="E-mail:").grid(row=4, column=0, sticky="w")
        tk.Entry(user_info_window, textvariable=email_var).grid(row=4, column=1)

        tk.Label(user_info_window, text="Date d'anniversaire:").grid(row=5, column=0, sticky="w")
        tk.Entry(user_info_window, textvariable=anniv_var).grid(row=5, column=1)

        tk.Label(user_info_window, text="Commentaires:").grid(row=6, column=0, sticky="w")
        tk.Entry(user_info_window, textvariable=notes_var).grid(row=6, column=1)

        # Bouton pour valider la mise à jour
        tk.Button(user_info_window, text="Mettre à jour",
                  command=lambda: self.update_user_from_window(user_info_window, user_id_to_update, fname_var.get(),
                                                               name_var.get(), tel1_var.get(), tel2_var.get(),
                                                               email_var.get(), anniv_var.get(), notes_var.get())).grid(
            row=7, column=0, columnspan=2, pady=10)

        def on_close():
            user_info_window.destroy()
            conn.close()

        user_info_window.protocol("WM_DELETE_WINDOW", on_close)

    def update_user_from_window(self, window, user_id, fname, name, tel1, tel2, email, anniv, notes):
        # Mettre à jour l'utilisateur dans la base de données
        conn = self.connect_to_database()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE users SET prenom=?, nom=?, tel1=?, tel2=?, mail=?, bday=?, notes=? WHERE id=?",
            (fname, name, tel1, tel2, email, anniv, notes, user_id))
        conn.commit()

        messagebox.showinfo("Contact mis à jour", "Contact mis à jour avec succès.")

        # Fermer la fenêtre
        window.destroy()

        # Recharger la liste des utilisateurs
        self.load_users()

    def delete_user_with_confirmation(self):
        # Récupérer l'ID de l'utilisateur à supprimer
        user_id_to_delete = self.get_selected_user_id()

        if user_id_to_delete is None:
            messagebox.showinfo("Sélection requise", "Veuillez sélectionner un utilisateur à supprimer.")
            return

        # Confirmer la suppression
        confirmation = messagebox.askquestion("Confirmation",
                                              f"Voulez-vous vraiment supprimer l'utilisateur avec l'ID {user_id_to_delete}?")

        if confirmation == 'yes':
            # Supprimer l'utilisateur de la base de données
            conn = self.connect_to_database()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM users WHERE id = ?", (user_id_to_delete,))
            conn.commit()

            messagebox.showinfo("Utilisateur supprimé",
                                f"Utilisateur avec l'ID {user_id_to_delete} supprimé avec succès.")

            # Recharger la liste des utilisateurs
            self.load_users()

    def get_selected_user_id(self):
        # Obtenir l'index sélectionné dans la liste des utilisateurs
        selected_index = self.userListBox.curselection()

        if not selected_index:
            return None

        # Obtenir l'ID de l'utilisateur à partir de la chaîne de la liste
        selected_user_str = self.userListBox.get(selected_index)
        user_id = int(selected_user_str.split(":")[1].split(",")[0])

        return user_id

    def show_user_details(self):
        # Obtenir l'ID de l'utilisateur sélectionné
        user_id = self.get_selected_user_id()

        if user_id is None:
            messagebox.showinfo("Sélection requise", "Veuillez sélectionner un utilisateur pour afficher les détails.")
            return

        # Récupérer les détails de l'utilisateur
        conn = self.connect_to_database()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id=?", (user_id,))
        user_details = cursor.fetchone()
        conn.close()

        # Afficher les détails dans une nouvelle fenêtre
        details_window = tk.Toplevel(self.master)
        details_window.title("Profil détaillé")

        labels = ["ID", "Nom", "Prénom", "Tél. Principal", "Tél. Secondaire", "E-mail", "Anniversaire", "Commentaires"]
        for i, label in enumerate(labels):
            tk.Label(details_window, text=label).grid(row=i, column=0, padx=5, pady=5)
            tk.Label(details_window, text=str(user_details[i])).grid(row=i, column=1, padx=5, pady=5)

    def load_users_alphabetical(self):
        # Méthode pour charger les utilisateurs dans l'ordre alphabétique
        self.load_users(sort_criteria="alphabetical")

    def load_users_custom(self):
        # Méthode pour charger les utilisateurs selon un critère personnalisé
        self.load_users(sort_criteria="custom")

    def load_users(self, sort_criteria=None):
        conn = self.connect_to_database()
        cursor = conn.cursor()

        # Charger tous les utilisateurs en fonction du critère de tri
        if sort_criteria == "alphabetical":
            cursor.execute("SELECT id, nom, prenom FROM users WHERE utilisateur = ? ORDER BY nom, prenom;",
                           (self.userid,))
        elif sort_criteria == "custom":
            # Tri dans l'ordre inverse de l'alphabétique
            cursor.execute("SELECT id, nom, prenom FROM users WHERE utilisateur = ? ORDER BY nom DESC, prenom DESC;",
                           (self.userid,))
        else:
            cursor.execute("SELECT id, nom, prenom FROM users WHERE utilisateur = ?;", (self.userid,))

        users = cursor.fetchall()

        # Effacer la liste actuelle
        self.userListBox.delete(0, tk.END)

        # Ajouter les utilisateurs à la liste
        for user in users:
            user_str = f"ID: {user[0]}, Nom: {user[1]}, Prénom: {user[2]}"
            self.userListBox.insert(tk.END, f" Nom: {user[1]}, Prénom: {user[2]}")

        # Fermer la connexion
        conn.close()

    def open_search_window(self):
        # Fonction pour ouvrir une nouvelle fenêtre de recherche
        search_window = tk.Toplevel(self.master)
        search_window.title("Recherche")

        search_entry = tk.Entry(search_window)
        search_entry.pack(pady=10, padx=10)
        search_entry.bind('<KeyRelease>',
                          lambda event, se=search_entry, lb=self.userListBox: self.search_users(event, se, lb))

        self.userListBox = tk.Listbox(search_window, selectmode=tk.SINGLE)
        self.userListBox.pack(pady=10, padx=200, fill=tk.BOTH, expand=True, side=tk.LEFT, anchor=tk.N)

        self.userListBox.bind('<Double-Button-1>', lambda event: self.show_user_details_from_search())

    def search_users(self, event):
        # Fonction pour rechercher les utilisateurs par nom directement dans la fenêtre principale
        conn = self.connect_to_database()
        cursor = conn.cursor()

        # Obtenir le terme de recherche à partir du widget Entry
        search_term = self.search_entry.get()

        # Charger les utilisateurs correspondant à la recherche
        cursor.execute("SELECT id, nom, prenom FROM users WHERE nom LIKE ? OR prenom LIKE ?;",
                       ('%' + search_term + '%', '%' + search_term + '%'))
        users = cursor.fetchall()

        # Effacer la liste actuelle du widget Listbox
        self.userListBox.delete(0, tk.END)

        # Ajouter les utilisateurs à la liste
        for user in users:
            user_str = f"ID: {user[0]}, Nom: {user[1]}, Prénom: {user[2]}"
            self.userListBox.insert(tk.END, user_str)

        # Fermer la connexion
        conn.close()
    def show_user_details_from_search(self):

        # Obtenir l'ID de l'utilisateur sélectionné depuis la fenêtre de recherche
        user_id = self.get_selected_user_id_from_search(self.userListBox)


        if user_id is None:
            messagebox.showinfo("Sélection requise", "Veuillez sélectionner un utilisateur pour afficher les détails.")
            return

        # Récupérer les détails de l'utilisateur
        conn = self.connect_to_database()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id=?", (user_id,))
        user_details = cursor.fetchone()
        conn.close()


        # Afficher les détails dans une nouvelle fenêtre
        details_window = tk.Toplevel(self.master)
        details_window.title("Profil détaillé")

        labels = ["ID", "Nom", "Prénom", "Tél. Principal", "Tél. Secondaire", "E-mail", "Anniversaire", "Commentaires"]
        for i, label in enumerate(labels):
            tk.Label(details_window, text=label).grid(row=i, column=0, padx=5, pady=5)
            tk.Label(details_window, text=str(user_details[i])).grid(row=i, column=1, padx=5, pady=5)

    def get_selected_user_id_from_search(self, userListBox):
        # Obtenir l'index sélectionné dans la liste des utilisateurs depuis la fenêtre de recherche
        selected_index = userListBox.curselection()

        if not selected_index:
            return None

        # Obtenir l'ID de l'utilisateur à partir de la chaîne de la liste
        selected_user_str = userListBox.get(selected_index)
        user_id = int(selected_user_str.split(":")[1].split(",")[0])

        return user_id



# Créer une instance de la classe ContactManagerApp
if __name__ == "__main__":
    root = tk.Tk()

    def on_login_success():
        # Fonction à appeler lorsque la connexion réussit
        login_page.frame.destroy()  # Fermer la fenêtre de connexion
        app = ContactManagerApp(root)

    login_page = LoginPage(root, on_login_success)
    root.mainloop()
