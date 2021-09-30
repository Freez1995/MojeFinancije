from tkinter import *
import sqlite3
from tkcalendar import DateEntry
from tkinter import messagebox
from datetime import date


conn = sqlite3.connect('Financije.db')
c = conn.cursor()

# Kreiranje tablica ako se baza tek kreirala
c.execute('''CREATE TABLE IF NOT EXISTS PRIMANJA
             ([ID] INTEGER PRIMARY KEY,[Opis] text, [Iznos] integer, [Datum] text)''')

c.execute('''CREATE TABLE IF NOT EXISTS OTPLATA_NA_RATE
             ([ID] INTEGER PRIMARY KEY,[Opis] text, [Iznos_rate] integer, [Broj_rata] text, [Datum_kupnje] text)''')

c.execute('''CREATE TABLE IF NOT EXISTS SKIDANJE_S_RAČUNA
             ([ID] INTEGER PRIMARY KEY,[Opis] text, [Iznos] integer, [Date] text)''')

c.execute('''CREATE TABLE IF NOT EXISTS KASICA
             ([ID] INTEGER PRIMARY KEY, [Stanje_računa] integer)''')

# Ubacivanje nule u tablicu za kasnije lakse rukovanje
c.execute('SELECT * FROM KASICA')
check = c.fetchone()
if check is None:
    c.execute('INSERT INTO KASICA VALUES (?, ?);', (None, 0.0))

conn.commit()


class FinancialCalc:
    def __init__(self, master):
        # Kreiranje potrebnih lista:
        self.lista_trenutnih_rata = list()
        self.lista_unesenih_rata = list()
        self.dict_id_buttona = dict()

        # Start screen - definiranje Button-a i prozora:
        self.master = master
        self.master.title("Kalkulator troška")
        self.master.geometry("300x300")
        self.master.resizable(False, False)

        self.prihodi_button = Button(master, text="Prihod", width=15, command=self.prihodi_deiconify)
        self.prihodi_button.place(x=95, y=85)
        self.potrosnja_button = Button(master, text="Potrošnja", width=15, command=self.potrosnja_deiconify)
        self.potrosnja_button.place(x=95, y=120)
        self.otplata_na_rate_button = Button(master, text="Otplata na rate", width=15,
                                             command=self.otplata_na_rate_deiconify)
        self.otplata_na_rate_button.place(x=95, y=155)
        self.izlistanje_button = Button(master, text="Izlistanje", width=15)
        self.izlistanje_button.place(x=95, y=190)

        # Skidanje_s_računa TopLevel - definiranje Label-a, Entry-a i Button-a:
        self.pt_top = Toplevel()
        self.pt_top.withdraw()
        self.pt_opis_label = Label(self.pt_top, text="Opis:", font=("Helvetica", 11), anchor="w")
        self.pt_opis_label.place(x=8, y=10)
        self.pt_opis_entry = Entry(self.pt_top, justify="center", width=15)
        self.pt_opis_entry.place(x=10, y=30)
        self.pt_cijena_label = Label(self.pt_top, text="Cijena:", font=("Helvetica", 11), anchor='w')
        self.pt_cijena_label.place(x=8, y=50)
        self.pt_cijena_entry = Entry(self.pt_top, justify="center", width=15)
        self.pt_cijena_entry.place(x=10, y=70)
        self.pt_rate_label = Label(self.pt_top, text="Broj rata:", font=("Helvetica", 11), anchor='w')
        self.pt_rate_label.place(x=8, y=90)
        self.pt_rate_entry = Entry(self.pt_top, justify="center", width=10)
        self.pt_rate_entry.place(x=10, y=110)
        self.pt_datum_kupnje_label = Label(self.pt_top, text="Datum kupnje:", font=("Helvetica", 11), anchor='w')
        self.pt_datum_kupnje_label.place(x=8, y=130)
        self.pt_datum_kupnje_entry = DateEntry(self.pt_top, width=12, background="darkblue",
                                               foreground="white", borderwidth=2, date_pattern="dd/MM/yyyy")
        self.pt_datum_kupnje_entry.place(x=10, y=155)

        self.pt_unos_btn = Button(self.pt_top, text="Unos", width=15, command=self.osobni_trosak_execute)
        self.pt_unos_btn.place(x=165, y=105)
        self.pt_povratak_btn = Button(self.pt_top, text="Povratak", width=15,
                                      command=lambda: (self.master.deiconify(), self.pt_top.withdraw()))
        self.pt_povratak_btn.place(x=165, y=145)

        # Unos primanja TopLevel - definiranje Label-a, Entry-a i Button-a:
        self.prihod_top = Toplevel()
        self.prihod_top.withdraw()
        self.prihod_opis_label = Label(self.prihod_top, text="Opis:", font=("Helvetica", 11), anchor="w")
        self.prihod_opis_label.place(x=8, y=10)
        self.prihod_opis_entry = Entry(self.prihod_top, justify="center", width=15)
        self.prihod_opis_entry.place(x=10, y=30)
        self.prihod_iznos_label = Label(self.prihod_top, text="Iznos:", font=("Helvetica", 11), anchor='w')
        self.prihod_iznos_label.place(x=8, y=50)
        self.prihod_iznos_entry = Entry(self.prihod_top, justify="center", width=15)
        self.prihod_iznos_entry.place(x=10, y=70)
        self.prihod_datum_kupnje_label = Label(self.prihod_top, text="Datum uplate:",
                                               font=("Helvetica", 11), anchor='w')
        self.prihod_datum_kupnje_label.place(x=8, y=90)
        self.prihod_datum_kupnje_entry = DateEntry(self.prihod_top, width=12, background="darkblue",
                                                   foreground="white", borderwidth=2, date_pattern="dd/MM/yyyy")
        self.prihod_datum_kupnje_entry.place(x=10, y=110)

        self.prihod_unos_btn = Button(self.prihod_top, text="Unos", width=15, command=self.prihodi_execute)
        self.prihod_unos_btn.place(x=165, y=105)
        self.prihod_povratak_btn = Button(self.prihod_top, text="Povratak", width=15,
                                          command=lambda: (self.master.deiconify(), self.prihod_top.withdraw()))
        self.prihod_povratak_btn.place(x=165, y=145)

        #   Otplata_na_rate TopLevel - definiranje
        self.onr_top = Toplevel()
        self.onr_top.withdraw()
        self.onr_top.protocol("WM_DELETE_WINDOW", lambda: (self.master.deiconify(), self.onr_top.withdraw()))
        self.onr_top.title("Kalkulator troška")
        self.onr_label = Label(self.onr_top, text="Popis otplate na rate:", font=("Helvetica", 11, "underline", "bold"))
        self.onr_opis_label = Label(self.onr_top, text="Opis dugovanja:", font=("Helvetica", 11, "underline", "bold"))
        self.onr_oznacena_rata_label = Label(self.onr_top, text="Opis:", font=("Helvetica", 11))
        self.onr_broj_rata_label = Label(self.onr_top, text="Broj rata:", font=("Helvetica", 11))
        self.onr_iznos_rate_label = Label(self.onr_top, text="Iznos rate:", font=("Helvetica", 11))
        self.onr_datum_isplate_label = Label(self.onr_top, text="Datum isplate:", font=("Helvetica", 11))

        self.onr_oznacena_rata_txt = Label(self.onr_top, text="", font=("Helvetica", 11))
        self.onr_broj_rata_txt = Label(self.onr_top, text="", font=("Helvetica", 11))
        self.onr_iznos_rate_txt = Label(self.onr_top, text="", font=("Helvetica", 11))
        self.onr_datum_isplate_txt = Label(self.onr_top, text="", font=("Helvetica", 11))

        self.onr_pl_sve_btn = Button(self.onr_top, text="Plati sve", width=11, command=self.plati_sve)
        self.onr_pl_pojed_btn = Button(self.onr_top, text="Plati odabrano", command=self.plati_odabrano)
        self.onr_izmjeni_btn = Button(self.onr_top, text="Izmjeni", width=10, command= self.izmijeni)
        self.ukupno_label = Label(self.onr_top, text="Ukupni trošak:", font=("Helvetica", 11))
        self.ukupno_entry = Entry(self.onr_top, font=("Helvetica", 10), justify="center", width=10)

        self.onr_oznacena_rata_entry = Entry(self.onr_top, font=("Helvetica", 11))
        self.onr_broj_rata_entry = Entry(self.onr_top, font=("Helvetica", 11))
        self.onr_iznos_rate_entry = Entry(self.onr_top, font=("Helvetica", 11))
        self.onr_promjena_datuma_kupnje_entry = Entry(self.onr_top, font=("Helvetica", 11))
        self.onr_spremi_izmijene_btn = Button(self.onr_top, text="Spremi", width=10, command=self.spremi_izmjene)

    def izmijeni(self):
        self.onr_datum_isplate_label.config(text="Datum kupnje:")
        self.onr_spremi_izmijene_btn.grid(row=5, column=6)
        self.onr_oznacena_rata_entry.grid(row=1, column=5, padx=5, sticky="S")
        self.onr_broj_rata_entry.grid(row=2, column=5, padx=5)
        self.onr_iznos_rate_entry.grid(row=3, column=5, padx=5)
        self.onr_promjena_datuma_kupnje_entry.grid(row=4, column=5, padx=5)

    def spremi_izmjene(self):
        self.onr_spremi_izmijene_btn.grid_forget()
        self.onr_datum_isplate_label.config(text="Datum isplate:")
        c.execute('UPDATE OTPLATA_NA_RATE SET Opis=?, Iznos_rate=?, Broj_rata=?, Datum_kupnje=? WHERE Opis=?',
                  (self.onr_oznacena_rata_entry.get(), int(self.onr_iznos_rate_entry.get()),
                   self.onr_broj_rata_entry.get(),self.onr_promjena_datuma_kupnje_entry.get(),
                   self.onr_oznacena_rata_txt.cget("text")))
        conn.commit()
        self.onr_oznacena_rata_entry.grid_forget()
        self.onr_broj_rata_entry.grid_forget()
        self.onr_iznos_rate_entry.grid_forget()
        self.onr_promjena_datuma_kupnje_entry.grid_forget()
        self.povlacenje_opisa(self.onr_oznacena_rata_entry.get())

    def plati_sve(self):
        c.execute('SELECT * FROM OTPLATA_NA_RATE')
        lista_rata = c.fetchall()
        for rata in lista_rata:
            broj_rata = rata[3].split("/")
            broj_rata_novo = str(int(broj_rata[0]) + 1) + "/" + broj_rata[1]
            danasnji_dan = date.today()
            danasnji_dan_format = danasnji_dan.strftime("%d/%m/%Y")
            c.execute('INSERT INTO SKIDANJE_S_RAČUNA VALUES (?, ?, ?, ?);',
                      (None, rata[1] + "(" + broj_rata_novo + ")", rata[2], danasnji_dan_format))
            c.execute('SELECT Stanje_računa FROM KASICA WHERE ID=?', (1,))
            trenutno_stanje = c.fetchone()[0]
            novo_stanje = trenutno_stanje - float(rata[2])
            c.execute('UPDATE KASICA SET Stanje_računa = ? WHERE ID = 1', (novo_stanje,))
            conn.commit()
            if int(rata[3].split("/")[0])+1 == int(rata[3].split("/")[1]):
                c.execute('DELETE FROM OTPLATA_NA_RATE WHERE Opis = ?', (rata[1],))
                conn.commit()
                btn_za_brisat = self.dict_id_buttona[rata[1]]
                btn_za_brisat.destroy()
                self.dict_id_buttona.pop(rata[1])
                if rata[1] in self.lista_trenutnih_rata:
                    self.lista_trenutnih_rata.remove(rata[1])
            else:
                c.execute('UPDATE OTPLATA_NA_RATE SET Broj_rata = ? WHERE Opis = ?', (broj_rata_novo, rata[1],))
                conn.commit()

    def plati_odabrano(self):
        opis_rate = self.onr_oznacena_rata_txt.cget("text")
        broj_rata = self.onr_broj_rata_txt.cget("text").split("/")
        danasnji_dan = date.today()
        danasnji_dan_format = danasnji_dan.strftime("%d/%m/%Y")
        broj_rata_novo = str(int(broj_rata[0]) + 1) + "/" + broj_rata[1]
        c.execute('INSERT INTO SKIDANJE_S_RAČUNA VALUES (?, ?, ?, ?);',
                  (None, opis_rate + "(" + broj_rata_novo + ")", self.onr_iznos_rate_txt.cget("text").split(" ")[0],
                   danasnji_dan_format))
        c.execute('SELECT Stanje_računa FROM KASICA WHERE ID=?', (1,))
        trenutno_stanje = c.fetchone()[0]
        novo_stanje = trenutno_stanje - float(self.onr_iznos_rate_txt.cget("text").split(" ")[0])
        c.execute('UPDATE KASICA SET Stanje_računa = ? WHERE ID = 1', (novo_stanje,))
        conn.commit()
        if int(broj_rata[0]) + 1 >= int(broj_rata[1]):
            c.execute('DELETE FROM OTPLATA_NA_RATE WHERE Opis = ?', (opis_rate,))
            conn.commit()
            btn_za_brisat = self.dict_id_buttona[opis_rate]
            btn_za_brisat.destroy()
            self.dict_id_buttona.pop(opis_rate)
            if opis_rate in self.lista_trenutnih_rata:
                self.lista_trenutnih_rata.remove(opis_rate)
            self.onr_oznacena_rata_txt.config(text="")
            self.onr_broj_rata_txt.config(text="")
            self.onr_iznos_rate_txt.config(text="")
            self.onr_datum_isplate_txt.config(text="")
        else:
            c.execute('UPDATE OTPLATA_NA_RATE SET Broj_rata = ? WHERE Opis = ?', (broj_rata_novo, opis_rate,))
            conn.commit()
            self.povlacenje_opisa(opis_rate)

    def povlacenje_opisa(self, opis):
        c.execute('SELECT * FROM OTPLATA_NA_RATE WHERE Opis=?;', (opis,))
        datum_kupnje_za_entry = ""
        for x in c:
            datum_kupnje_za_entry = x[4]
            dodaj_godinu = 0
            self.onr_oznacena_rata_txt.config(text=x[1])
            self.onr_iznos_rate_txt.config(text=str(x[2]) + " kn")
            self.onr_broj_rata_txt.config(text=x[3])
            datum_racunanje = int(x[4].split("/")[1]) + int(x[3].split("/")[1])
            while datum_racunanje > 12:
                datum_racunanje -= 12
                dodaj_godinu += 1
            datum_isplate = str(datum_racunanje) + "/" + str(int(x[4].split("/")[2])+dodaj_godinu)
            self.onr_datum_isplate_txt.config(text=datum_isplate)

        self.onr_oznacena_rata_entry.delete(0, END)
        self.onr_oznacena_rata_entry.insert(0, self.onr_oznacena_rata_txt.cget("text"))
        self.onr_broj_rata_entry.delete(0, END)
        self.onr_broj_rata_entry.insert(0, self.onr_broj_rata_txt.cget("text"))
        self.onr_iznos_rate_entry.delete(0, END)
        self.onr_iznos_rate_entry.insert(0, self.onr_iznos_rate_txt.cget("text").split(" ")[0])
        self.onr_promjena_datuma_kupnje_entry.delete(0, END)
        self.onr_promjena_datuma_kupnje_entry.insert(0, datum_kupnje_za_entry)

    def otplata_na_rate_deiconify(self):
        # Otplata_na_rate TopLevel - definiranje prozora:
        self.master.withdraw()
        self.onr_top.deiconify()
        self.onr_label.grid(row=0, columnspan=3, sticky="NESW")
        self.onr_opis_label.grid(row=0, column=5, sticky="NESW")
        self.onr_oznacena_rata_label.grid(row=1, column=4, padx=5, sticky="SE")
        self.onr_broj_rata_label.grid(row=2, column=4, padx=5, sticky="E")
        self.onr_iznos_rate_label.grid(row=3, column=4, padx=5, sticky="E")
        self.onr_datum_isplate_label.grid(row=4, column=4, padx=5, sticky="E")

        self.onr_oznacena_rata_txt.grid(row=1, column=5, padx=5, sticky="SWE")
        self.onr_broj_rata_txt.grid(row=2, column=5, padx=5, sticky="NSWE")
        self.onr_iznos_rate_txt.grid(row=3, column=5, padx=5, sticky="NSWE")
        self.onr_datum_isplate_txt.grid(row=4, column=5, padx=5, sticky="NSWE")

        x = self.master.winfo_x()
        y = self.master.winfo_y()
        self.onr_top.geometry(f"+{x}+{y}")

        #   Definiranje buttona povlačenjem podataka iz baze
        c.execute('SELECT Opis FROM OTPLATA_NA_RATE')
        lista_opisa_rata = list()
        for opis in c:
            lista_opisa_rata.append(opis[0])
        kolona = 0
        red = 1
        for b in self.dict_id_buttona.values():
            b.destroy()
        self.dict_id_buttona.clear()
        for opis in lista_opisa_rata:
            # Davanje funckije svakom Button-u
            funkcija = lambda x=opis: self.povlacenje_opisa(x)
            rata_button = Button(self.onr_top, text=opis, width=10, command=funkcija)
            rata_button.grid(row=red, column=kolona, padx=5, pady=5)
            self.dict_id_buttona[opis] = rata_button
            kolona += 1
            if kolona == 3:
                red += 1
                kolona = 0
        #   Definiranje položaja Button widgeta na temelju auto-kreiranja Buttona rata
        if red < 5:
            red = 5
        if red >= 5:
            red += 1
        self.onr_pl_sve_btn.grid(row=red, column=4, pady=5)
        self.onr_pl_pojed_btn.grid(row=red, column=5, padx=2, pady=5)
        self.onr_izmjeni_btn.grid(row=red, column=6, padx=12, pady=5)
        self.ukupno_label.grid(row=red, column=0, pady=5)
        self.ukupno_entry.grid(row=red, column=1, pady=5, sticky="W")
        x = self.master.winfo_x()
        y = self.master.winfo_y()
        self.onr_top.geometry(f"+{x}+{y}")

    def prihodi_deiconify(self):
        # Prihodi TopLevel - definiranje prozora:
        self.master.withdraw()
        self.prihod_top.deiconify()
        self.prihod_top.protocol("WM_DELETE_WINDOW", lambda: (self.master.deiconify(), self.prihod_top.withdraw()))
        self.prihod_top.title("Kalkulator troška")
        self.prihod_top.geometry("300x200")
        self.prihod_top.resizable(False, False)
        x = self.master.winfo_x()
        y = self.master.winfo_y()
        w = self.prihod_top.winfo_width()
        h = self.prihod_top.winfo_height()
        self.prihod_top.geometry("%dx%d+%d+%d" % (w, h, x + 0, y + 0))

    def potrosnja_deiconify(self):
        # Osobni_trosak TopLevel - definiranje prozora:
        self.master.withdraw()
        self.pt_top.deiconify()
        self.pt_top.protocol("WM_DELETE_WINDOW", lambda: (self.master.deiconify(), self.pt_top.withdraw()))
        self.pt_top.title("Kalkulator troška")
        self.pt_top.geometry("300x200")
        self.pt_top.resizable(False, False)
        x = self.master.winfo_x()
        y = self.master.winfo_y()
        w = self.pt_top.winfo_width()
        h = self.pt_top.winfo_height()
        self.pt_top.geometry("%dx%d+%d+%d" % (w, h, x + 0, y + 0))

    def prihodi_execute(self):
        # Povlačenje unosa iz Entry-a i unos u bazu podataka:
        prihod_opis = self.prihod_opis_entry.get()
        prihod_iznos = self.prihod_iznos_entry.get()
        prihod_datum = self.prihod_datum_kupnje_entry.get()
        c.execute('INSERT INTO PRIMANJA VALUES (?, ?, ?, ?);', (None, prihod_opis, prihod_iznos, prihod_datum))
        c.execute('SELECT Stanje_računa FROM KASICA WHERE ID=?', (1,))
        trenutno_stanje = c.fetchone()[0]
        novo_stanje = float(trenutno_stanje) + float(prihod_iznos)
        c.execute('UPDATE KASICA SET Stanje_računa = ? WHERE ID = 1', (novo_stanje,))
        conn.commit()

    def osobni_trosak_execute(self):
        # Povlačenje unosa iz Entry-a i unos u bazu podataka:
        ot_opis = self.pt_opis_entry.get()
        ot_cijena = self.pt_cijena_entry.get()
        ot_rate = self.pt_rate_entry.get()
        ot_datum_kupnje = self.pt_datum_kupnje_entry.get()
        if ot_rate == "" or ot_rate == "0":
            c.execute('SELECT Stanje_računa FROM KASICA WHERE ID=?', (1,))
            trenutno_stanje = c.fetchone()[0]
            novo_stanje = trenutno_stanje - float(ot_cijena)
            c.execute('UPDATE KASICA SET Stanje_računa = ? WHERE ID = 1', (novo_stanje,))
            c.execute('INSERT INTO SKIDANJE_S_RAČUNA VALUES (?, ?, ?, ?);',
                      (None, ot_opis, ot_cijena, ot_datum_kupnje))
            conn.commit()
            self.pt_opis_entry.delete("0", END)
            self.pt_cijena_entry.delete("0", END)
            self.pt_rate_entry.delete("0", END)
        else:
            if ot_opis in self.lista_trenutnih_rata:
                messagebox.showinfo("Obavijest", "Naziv opisa rate je već u bazi, molim upišite drugi naziv")
            else:
                c.execute('INSERT INTO OTPLATA_NA_RATE VALUES (?, ?, ?, ?, ?);',
                          (None, ot_opis, round(float(ot_cijena) / float(ot_rate), 2), "0/" + str(ot_rate),
                           ot_datum_kupnje))
                self.lista_trenutnih_rata.append(ot_opis)
                self.pt_opis_entry.delete("0", END)
                self.pt_cijena_entry.delete("0", END)
                self.pt_rate_entry.delete("0", END)
                conn.commit()

root = Tk()
my_gui = FinancialCalc(root)
root.mainloop()
