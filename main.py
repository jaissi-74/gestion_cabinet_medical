from address_book import AddressBookFile

def print_menu():
    print("\n" + "="*40)
    print("       CARNET D'ADRESSES")
    print("="*40)
    print("1. Ajouter un contact")
    print("2. Supprimer un contact")
    print("3. Afficher les contacts")
    print("4. Exporter en CSV")
    print("5. Quitter")
    print("="*40)

def main():
    book = AddressBookFile()
    print("Bienvenue dans votre carnet d'adresses.")

    while True:
        print_menu()
        choice = input("Votre choix : ").strip()

        if choice == '1':
            name  = input("Nom        : ").strip()
            email = input("Email      : ").strip()
            phone = input("Téléphone  : ").strip()
            ok, msg = book.add_contact(name, email, phone)
            print(f"→ {msg}")

        elif choice == '2':
            email = input("Email du contact à supprimer : ").strip()
            ok, msg = book.remove_contact(email)
            print(f"→ {msg}")

        elif choice == '3':
            contacts = book.display_contacts()
            if not contacts:
                print("→ Aucun contact enregistré.")
            else:
                print(f"\n{'─'*50}")
                for c in contacts:
                    print(f"  {c}")
                print(f"{'─'*50}")
                print(f"  Total : {len(contacts)} contact(s)")

        elif choice == '4':
            ok, msg = book.export_to_csv()
            print(f"→ {msg}")

        elif choice == '5':
            print("Au revoir !")
            break

        else:
            print("→ Choix invalide. Entrez un nombre entre 1 et 5.")

if __name__ == "__main__":
    main()
