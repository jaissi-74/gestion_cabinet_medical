import tkinter as tk
from tkinter import ttk, messagebox
from address_book import AddressBookDB
from auth import verify_admin, seed_default_admin

# ─────────────────────────────────────────────
#  LOGIN WINDOW
# ─────────────────────────────────────────────

class LoginWindow:
    def __init__(self, on_success):
        self.on_success = on_success
        self.root = tk.Tk()
        self.root.title("Connexion — Administrateur")
        self.root.geometry("340x220")
        self.root.resizable(False, False)
        self._build()

    def _build(self):
        tk.Label(self.root, text="Carnet d'adresses", font=("Arial", 14, "bold")).pack(pady=14)
        frame = tk.Frame(self.root)
        frame.pack(padx=30, fill="x")

        tk.Label(frame, text="Utilisateur :").grid(row=0, column=0, sticky="w", pady=4)
        self.user_var = tk.StringVar()
        tk.Entry(frame, textvariable=self.user_var, width=22).grid(row=0, column=1, pady=4)

        tk.Label(frame, text="Mot de passe :").grid(row=1, column=0, sticky="w", pady=4)
        self.pw_var = tk.StringVar()
        tk.Entry(frame, textvariable=self.pw_var, show="*", width=22).grid(row=1, column=1, pady=4)

        self.msg = tk.Label(self.root, text="", fg="red", font=("Arial", 10))
        self.msg.pack()

        tk.Button(self.root, text="Se connecter", width=16,
                  command=self._login, bg="#0052CC", fg="white").pack(pady=10)

    def _login(self):
        u = self.user_var.get().strip()
        p = self.pw_var.get().strip()
        if verify_admin(u, p):
            self.root.destroy()
            self.on_success()
        else:
            self.msg.config(text="Identifiants incorrects.")

    def run(self):
        self.root.mainloop()


# ─────────────────────────────────────────────
#  MAIN APPLICATION WINDOW
# ─────────────────────────────────────────────

CATEGORIES = ["General", "Patient", "Fournisseur", "Laboratoire", "Client", "Collègue"]

class AppWindow:
    def __init__(self):
        self.book = AddressBookDB()
        self.root = tk.Tk()
        self.root.title("Carnet d'adresses — Gestion des contacts")
        self.root.geometry("850x560")  # Légèrement élargi pour accommoder le nouveau bouton
        self._build()
        self._refresh_list()

    def _build(self):
        frameH = tk.Frame(self.root, bg="#0052CC", pady=8)
        frameH.pack(fill="x")
        tk.Label(frameH, text="📋  Carnet d'adresses",
                 bg="#0052CC", fg="white", font=("Arial", 14, "bold")).pack(side="left", padx=16)
        tk.Label(frameH, text="Base de données SQLite",
                 bg="#0052CC", fg="#cce0ff", font=("Arial", 10)).pack(side="right", padx=16)

        content = tk.Frame(self.root)
        content.pack(fill="both", expand=True, padx=10, pady=8)

        form_frame = tk.LabelFrame(content, text="Contact", padx=10, pady=10)
        form_frame.pack(side="left", fill="y", padx=(0, 8))

        labels = ["Nom", "Email", "Téléphone", "Adresse", "Entreprise"]
        self.entries = {}
        for i, lab in enumerate(labels):
            tk.Label(form_frame, text=lab + " :").grid(row=i, column=0, sticky="w", pady=3)
            var = tk.StringVar()
            tk.Entry(form_frame, textvariable=var, width=24).grid(row=i, column=1, pady=3)
            self.entries[lab] = var

        tk.Label(form_frame, text="Catégorie :").grid(row=len(labels), column=0, sticky="w", pady=3)
        self.cat_var = tk.StringVar(value="General")
        ttk.Combobox(form_frame, textvariable=self.cat_var,
                     values=CATEGORIES, state="readonly", width=21).grid(row=len(labels), column=1, pady=3)

        # ── Zone des boutons inférieure
        btn_frame = tk.Frame(form_frame)
        btn_frame.grid(row=len(labels)+1, column=0, columnspan=2, pady=10)
        
        tk.Button(btn_frame, text="Ajouter",    width=8, bg="#28a745", fg="white",
                  command=self._add).pack(side="left", padx=2)
        tk.Button(btn_frame, text="Supprimer",  width=8, bg="#dc3545", fg="white",
                  command=self._remove).pack(side="left", padx=2)
        tk.Button(btn_frame, text="Modifier",   width=8, bg="#ffc107", fg="black",
                  command=self._update).pack(side="left", padx=2)
        # Nouveau bouton "Afficher" demandé pour charger toutes les informations
        tk.Button(btn_frame, text="Afficher",   width=8, bg="#17a2b8", fg="white",
                  command=self._display_details).pack(side="left", padx=2)
                  
        tk.Button(btn_frame, text="Effacer",    width=8,
                  command=self._clear_form).pack(side="left", padx=2)

        search_frame = tk.Frame(form_frame)
        search_frame.grid(row=len(labels)+2, column=0, columnspan=2, pady=4)
        tk.Label(search_frame, text="Recherche :").pack(side="left")
        self.search_var = tk.StringVar()
        tk.Entry(search_frame, textvariable=self.search_var, width=16).pack(side="left", padx=4)
        tk.Button(search_frame, text="🔍", command=self._search).pack(side="left")
        tk.Button(search_frame, text="✕", command=self._refresh_list).pack(side="left")

        tk.Button(form_frame, text="Exporter en CSV", width=24,
                  command=self._export).grid(row=len(labels)+3, column=0, columnspan=2, pady=6)

        right = tk.Frame(content)
        right.pack(side="left", fill="both", expand=True)

        frameM = tk.Frame(right)
        frameM.pack(fill="both", expand=True)

        self.listbox = tk.Listbox(frameM, font=("Courier", 11), selectbackground="#0052CC",
                                  selectforeground="white", activestyle="none")
        self.listbox.pack(side="left", fill="both", expand=True)
        scrollbar = tk.Scrollbar(frameM, orient="vertical", command=self.listbox.yview)
        scrollbar.pack(side="right", fill="y")
        self.listbox.config(yscrollcommand=scrollbar.set)
        self.listbox.bind("<<ListboxSelect>>", self._on_select)

        frameB = tk.Frame(right, pady=4)
        frameB.pack(fill="x")
        self.count_label = tk.Label(frameB, text="0 contact(s)", fg="gray")
        self.count_label.pack(side="left", padx=4)

    # ── Actions ─────────────────────────────

    def _add(self):
        name    = self.entries["Nom"].get().strip()
        email   = self.entries["Email"].get().strip()
        phone   = self.entries["Téléphone"].get().strip()
        address = self.entries["Adresse"].get().strip()
        company = self.entries["Entreprise"].get().strip()
        cat     = self.cat_var.get()

        if not name or not email or not phone:
            messagebox.showwarning("Champs manquants", "Nom, email et téléphone sont obligatoires.")
            return
        ok, msg = self.book.add_contact(name, email, phone, cat, address, company)
        if ok:
            self._clear_form()
            self._refresh_list()
        messagebox.showinfo("Résultat", msg)

    def _update(self):
        """Action du bouton Modifier : met à jour le contact en prenant l'email comme référence"""
        name    = self.entries["Nom"].get().strip()
        email   = self.entries["Email"].get().strip()  # L'email sert d'identifiant unique
        phone   = self.entries["Téléphone"].get().strip()
        address = self.entries["Adresse"].get().strip()
        company = self.entries["Entreprise"].get().strip()
        cat     = self.cat_var.get()

        if not email:
            messagebox.showwarning("Email manquant", "L'email est obligatoire pour identifier le contact à modifier.")
            return

        if not name or not phone:
            messagebox.showwarning("Champs manquants", "Le nom et le téléphone ne peuvent pas être vides.")
            return

        # Appel de la fonction de mise à jour
        ok, msg = self.book.update_contact(name, email, phone, cat, address, company)
        if ok:
            self._refresh_list()  # Actualise la liste de droite
            messagebox.showinfo("Succès", msg)
        else:
            messagebox.showerror("Erreur", msg)
    
    def _remove(self):
        sel = self.listbox.curselection()
        if not sel:
            messagebox.showwarning("Sélection", "Sélectionnez un contact dans la liste.")
            return
        item = self.listbox.get(sel[0])
        email = item.split("|")[1].strip()
        if messagebox.askyesno("Confirmer", f"Supprimer {email} ?"):
            ok, msg = self.book.remove_contact(email)
            self._refresh_list()
            messagebox.showinfo("Résultat", msg)

    def _display_details(self):
        """Action du bouton Afficher : remplit le formulaire avec l'intégralité des données SQLite"""
        sel = self.listbox.curselection()
        if not sel:
            messagebox.showwarning("Sélection", "Veuillez sélectionner un contact dans la liste d'abord.")
            return
        
        item = self.listbox.get(sel[0])
        email = item.split("|")[1].strip()
        
        # Récupération de la liste complète pour chercher l'objet en profondeur
        all_contacts = self.book.display_contacts()
        contact_complet = next((c for c in all_contacts if c.email.lower() == email.lower()), None)
        
        if contact_complet:
            # Remplissage complet du formulaire à gauche
            self.entries["Nom"].set(contact_complet.name)
            self.entries["Email"].set(contact_complet.email)
            self.entries["Téléphone"].set(contact_complet.phone)
            
            # Injection sécurisée des attributs dynamiques (s'ils existent dans l'objet)
            self.entries["Adresse"].set(getattr(contact_complet, 'address', ''))
            self.entries["Entreprise"].set(getattr(contact_complet, 'company', ''))
            
            cat = getattr(contact_complet, 'category', 'General')
            if cat in CATEGORIES:
                self.cat_var.set(cat)
            else:
                self.cat_var.set("General")
        else:
            messagebox.showerror("Erreur", "Impossible de charger les détails complets.")

    def _search(self):
        q = self.search_var.get().strip()
        if not q:
            return
        results = self.book.search(q)
        self._populate_list(results)

    def _refresh_list(self):
        contacts = self.book.display_contacts()
        self._populate_list(contacts)

    def _populate_list(self, contacts):
        self.listbox.delete(0, tk.END)
        for c in contacts:
            self.listbox.insert(tk.END, f"  {c.name:<22} | {c.email:<30} | {c.phone}")
        self.count_label.config(text=f"{len(contacts)} contact(s)")

    def _on_select(self, event):
        # Laissé vide pour que le remplissage complet soit déclenché par le bouton "Afficher"
        pass

    def _clear_form(self):
        for var in self.entries.values():
            var.set("")
        self.cat_var.set("General")

    def _export(self):
        ok, msg = self.book.export_csv()
        messagebox.showinfo("Export CSV", msg)

    def run(self):
        self.root.mainloop()


# ─────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────

def launch():
    AddressBookDB()  # Initialise le fichier de base de données contacts.db
    seed_default_admin()

    def open_app():
        app = AppWindow()
        app.run()

    login = LoginWindow(on_success=open_app)
    login.run()


if __name__ == "__main__":
    launch()