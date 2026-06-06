import tkinter as tk
from tkinter import ttk, messagebox
import webbrowser
from urllib.parse import quote
from datetime import datetime, timedelta
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
        self.root.title("Carnet d'adresses — Gestion des contacts & RDV")
        self.root.geometry("900x680")  # Élargi et rehaussé pour inclure la grille de l'agenda
        self._build()
        self._refresh_list()
        self._update_agenda_slots()

    def _build(self):
        # 1. En-tête bleu
        frameH = tk.Frame(self.root, bg="#0052CC", pady=8)
        frameH.pack(fill="x")
        tk.Label(frameH, text="📋  Gestionnaire de Cabinet Médical",
                 bg="#0052CC", fg="white", font=("Arial", 14, "bold")).pack(side="left", padx=16)
        tk.Label(frameH, text="Base de données SQLite",
                 bg="#0052CC", fg="#cce0ff", font=("Arial", 10)).pack(side="right", padx=16)

        # 2. Zone de contenu principale
        content = tk.Frame(self.root)
        content.pack(fill="both", expand=True, padx=10, pady=8)

        # 3. Formulaire de gauche (Fiche contact)
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

        # 4. Zone des boutons d'actions contacts
        btn_frame = tk.Frame(form_frame)
        btn_frame.grid(row=len(labels)+1, column=0, columnspan=2, pady=10)
        
        tk.Button(btn_frame, text="Ajouter",    width=8, bg="#28a745", fg="white", command=self._add).pack(side="left", padx=2)
        tk.Button(btn_frame, text="Modifier",   width=8, bg="#ffc107", fg="black", command=self._update).pack(side="left", padx=2)
        tk.Button(btn_frame, text="Supprimer",  width=8, bg="#dc3545", fg="white", command=self._remove).pack(side="left", padx=2)
        tk.Button(btn_frame, text="Afficher",   width=8, bg="#17a2b8", fg="white", command=self._display_details).pack(side="left", padx=2)
        tk.Button(btn_frame, text="Effacer",    width=8, command=self._clear_form).pack(side="left", padx=2)

        # 5. Zone de recherche
        search_frame = tk.Frame(form_frame)
        search_frame.grid(row=len(labels)+2, column=0, columnspan=2, pady=4)
        tk.Label(search_frame, text="Recherche :").pack(side="left")
        self.search_var = tk.StringVar()
        tk.Entry(search_frame, textvariable=self.search_var, width=16).pack(side="left", padx=4)
        tk.Button(search_frame, text="🔍", command=self._search).pack(side="left")
        tk.Button(search_frame, text="✕", command=self._refresh_list).pack(side="left")

        # 6. Cadre de Communication
        comm_frame = tk.LabelFrame(form_frame, text="💬 Communication", padx=6, pady=6, fg="#0052CC")
        comm_frame.grid(row=len(labels)+3, column=0, columnspan=2, pady=8, sticky="ew")

        tk.Button(comm_frame, text="🟢 Message WhatsApp", bg="#25D366", fg="white", font=("Arial", 9, "bold"), command=self._send_whatsapp, width=22).pack(pady=3)
        tk.Button(comm_frame, text="📧 Envoyer un Email", bg="#ea4335", fg="white", font=("Arial", 9, "bold"), command=self._send_email, width=22).pack(pady=3)

        tk.Button(form_frame, text="Exporter en CSV", width=24, command=self._export).grid(row=len(labels)+4, column=0, columnspan=2, pady=4)

        # 7. Zone de droite (Séparée en haut: Liste de contacts / en bas: Agenda des RDV)
        right = tk.Frame(content)
        right.pack(side="left", fill="both", expand=True)

        # --- Bloc du haut de la zone droite (Liste de contacts) ---
        frameM = tk.LabelFrame(right, text="Liste des Contacts")
        frameM.pack(fill="both", expand=True, pady=(0, 6))

        self.listbox = tk.Listbox(frameM, font=("Courier", 11), selectbackground="#0052CC", selectforeground="white", activestyle="none")
        self.listbox.pack(side="left", fill="both", expand=True)
        scrollbar = tk.Scrollbar(frameM, orient="vertical", command=self.listbox.yview)
        scrollbar.pack(side="right", fill="y")
        self.listbox.config(yscrollcommand=scrollbar.set)

        self.count_label = tk.Label(right, text="0 contact(s)", fg="gray")
        self.count_label.pack(anchor="w", padx=4)

        # --- Bloc du bas de la zone droite : AGENDA DE GESTION DES RDV (Partie 9) ---
        agenda_frame = tk.LabelFrame(right, text="📅 Agenda & Planification des RDV (Intervalles de 30 min)", padx=8, pady=8, fg="#0052CC")
        agenda_frame.pack(fill="x", pady=6)

        # Choix de la date
        date_sel_frame = tk.Frame(agenda_frame)
        date_sel_frame.pack(fill="x", pady=4)
        tk.Label(date_sel_frame, text="Choisir une date : ", font=("Arial", 10, "bold")).pack(side="left")
        
        # Génération des 7 prochains jours éligibles
        self.available_dates = [(datetime.now() + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)]
        self.agenda_date_var = tk.StringVar(value=self.available_dates[0])
        
        date_combo = ttk.Combobox(date_sel_frame, textvariable=self.agenda_date_var, values=self.available_dates, state="readonly", width=14)
        date_combo.pack(side="left", padx=4)
        date_combo.bind("<<ComboboxSelected>>", lambda e: self._update_agenda_slots())

        # Conteneur de la grille des boutons de créneaux horaires
        self.slots_container = tk.Frame(agenda_frame)
        self.slots_container.pack(fill="x", pady=6)

        # Liste des créneaux de 30 minutes de 09:00 à 17:00
        self.time_slots = [
            "09:00 - 09:30", "09:30 - 10:00", "10:00 - 10:30", "10:30 - 11:00",
            "11:00 - 11:30", "11:30 - 12:00", "14:00 - 14:30", "14:30 - 15:00",
            "15:00 - 15:30", "15:30 - 16:00", "16:00 - 16:30", "16:30 - 17:00"
        ]
        self.slot_buttons = {}

    # ── Actions & Logique ─────────────────────────────

    def _update_agenda_slots(self):
        """Met à jour l'état visuel des boutons en désactivant les créneaux déjà réservés"""
        # On vide l'ancienne grille de boutons
        for widget in self.slots_container.winfo_children():
            widget.destroy()
        self.slot_buttons.clear()

        selected_date = self.agenda_date_var.get()
        # Appel à la BDD pour récupérer la liste des chaînes de créneaux réservés
        booked_slots = self.book.get_booked_slots(selected_date)

        # Recréation de la grille (4 colonnes de boutons de créneaux)
        for index, slot in enumerate(self.time_slots):
            row = index // 4
            col = index % 4
            
            if slot in booked_slots:
                # Si le créneau est pris, le bouton est désactivé (state="disabled")
                btn = tk.Button(self.slots_container, text=slot, width=16, bg="#e0e0e0", fg="gray", state="disabled")
            else:
                # Si disponible, il est cliquable et vert clair
                btn = tk.Button(self.slots_container, text=slot, width=16, bg="#d4edda", fg="#155724",
                                command=lambda s=slot: self._book_slot_action(s))
            
            btn.grid(row=row, column=col, padx=4, pady=4)
            self.slot_buttons[slot] = btn

    def _book_slot_action(self, slot_time):
        """Déclenche la réservation du créneau pour le contact sélectionné au formulaire"""
        email = self.entries["Email"].get().strip()
        name = self.entries["Nom"].get().strip()
        selected_date = self.agenda_date_var.get()

        if not email or not name:
            messagebox.showwarning("Aucun patient", "Veuillez d'abord afficher ou sélectionner un contact complet à gauche pour lui attribuer le RDV.")
            return

        conf = messagebox.askyesno("Confirmer RDV", f"Voulez-vous réserver le créneau {slot_time} le {selected_date} pour le patient {name} ?")
        if conf:
            ok, msg = self.book.book_appointment(selected_date, slot_time, email)
            if ok:
                messagebox.showinfo("Succès", msg)
                self._update_agenda_slots() # Rafraîchit l'agenda pour désactiver la case choisie
            else:
                messagebox.showerror("Erreur", msg)

    # ── Actions Contacts Classiques ─────────────────────────────

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
        name    = self.entries["Nom"].get().strip()
        email   = self.entries["Email"].get().strip()
        phone   = self.entries["Téléphone"].get().strip()
        address = self.entries["Adresse"].get().strip()
        company = self.entries["Entreprise"].get().strip()
        cat     = self.cat_var.get()

        if not email:
            messagebox.showwarning("Email manquant", "L'email est obligatoire.")
            return
        if not name or not phone:
            messagebox.showwarning("Champs manquants", "Le nom et le téléphone ne peuvent pas être vides.")
            return

        ok, msg = self.book.update_contact(name, email, phone, cat, address, company)
        if ok:
            self._refresh_list()
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
        sel = self.listbox.curselection()
        if not sel:
            messagebox.showwarning("Sélection", "Veuillez sélectionner un contact dans la liste d'abord.")
            return
        
        item = self.listbox.get(sel[0])
        email = item.split("|")[1].strip()
        
        all_contacts = self.book.display_contacts()
        contact_complet = next((c for c in all_contacts if c.email.lower() == email.lower()), None)
        
        if contact_complet:
            self.entries["Nom"].set(contact_complet.name)
            self.entries["Email"].set(contact_complet.email)
            self.entries["Téléphone"].set(contact_complet.phone)
            self.entries["Adresse"].set(getattr(contact_complet, 'address', ''))
            self.entries["Entreprise"].set(getattr(contact_complet, 'company', ''))
            
            cat = getattr(contact_complet, 'category', 'General')
            if cat in CATEGORIES:
                self.cat_var.set(cat)
            else:
                self.cat_var.set("General")
        else:
            messagebox.showerror("Erreur", "Impossible de charger les détails complets.")

    def _send_whatsapp(self):
        phone = self.entries["Téléphone"].get().strip()
        name = self.entries["Nom"].get().strip()
        cat = self.cat_var.get()

        if not phone:
            messagebox.showwarning("Téléphone manquant", "Veuillez sélectionner un contact.")
            return

        if cat == "Patient":
            message = f"Bonjour M./Mme {name},\n\nNous vous confirmons votre rendez-vous au cabinet médical. Veuillez vous présenter 10 minutes à l'avance.\n\nCordialement."
        elif cat == "Laboratoire":
            message = f"Bonjour,\n\nNous vous contactons concernant le dossier de notre patient pour demander les résultats d'analyses correspondants.\n\nCordialement."
        else:
            message = f"Bonjour {name},\n\nCordialement."

        message_encoded = quote(message)
        phone_cleaned = "".join(filter(str.isdigit, phone))
        
        if phone_cleaned.startswith("0") and len(phone_cleaned) == 10:
            phone_cleaned = "212" + phone_cleaned[1:]

        url = f"https://wa.me/{phone_cleaned}?text={message_encoded}"
        webbrowser.open(url)

    def _send_email(self):
        email = self.entries["Email"].get().strip()
        name = self.entries["Nom"].get().strip()
        cat = self.cat_var.get()

        if not email:
            messagebox.showwarning("Email manquant", "Veuillez sélectionner un contact.")
            return

        if cat == "Patient":
            subject = "Confirmation de rendez-vous — Cabinet Médical"
            body = f"Bonjour M./Mme {name},\n\nNous vous confirmons par la présente votre prochain rendez-vous au sein de notre cabinet.\n\nCordialement."
        elif cat == "Laboratoire":
            subject = "Demande de résultats d'analyses"
            body = f"Bonjour,\n\nMerci de bien vouloir nous transmettre les résultats d'analyses concernant nos patients communs.\n\nCordialement."
        else:
            subject = "Contact — Cabinet Médical"
            body = f"Bonjour {name},\n\nCordialement."

        url = f"mailto:{email}?subject={quote(subject)}&body={quote(body)}"
        webbrowser.open(url)

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
    AddressBookDB()
    seed_default_admin()

    def open_app():
        app = AppWindow()
        app.run()

    login = LoginWindow(on_success=open_app)
    login.run()


if __name__ == "__main__":
    launch()