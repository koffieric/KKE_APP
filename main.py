from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.image import Image
from fpdf import FPDF
import datetime, os, math

LICENCE_FILE="/storage/emulated/0/Download/cacao_licence_kke.txt"
LOGO_FILE=None
for p in ["kke_logo.png","/storage/emulated/0/Download/kke_logo.png","/storage/emulated/0/kke_logo.png"]:
    if os.path.exists(p):
        LOGO_FILE=p
        break

class CacaoApp(App):
    def build(self):
        self.total=0; self.nb=0; self.pdf_count=0
        if os.path.exists(LICENCE_FILE):
            try:
                with open(LICENCE_FILE,'r') as f:
                    t=f.read()
                    if 'count=' in t:
                        self.pdf_count=int(t.split('count=')[1].split()[0])
            except: pass
        box=BoxLayout(orientation='vertical',padding=10,spacing=3)
        if LOGO_FILE:
            try: box.add_widget(Image(source=LOGO_FILE,size_hint_y=0.25))
            except: pass
        self.lab=Label(text=f'KKE KOUASSI K E\nEssai {self.pdf_count}/5\nOM:0749425861 Wave:0171872289',size_hint_y=0.22)
        box.add_widget(self.lab)
        self.prix=TextInput(hint_text='Prix kg ex 2800',input_filter='int',multiline=False,size_hint_y=0.1)
        box.add_widget(self.prix)
        self.poids=TextInput(hint_text='Poids total ex 89, 150, 334',input_filter='float',multiline=False,size_hint_y=0.1)
        box.add_widget(self.poids)
        self.nom_prod=TextInput(hint_text='Nom Producteur',multiline=False,size_hint_y=0.1)
        box.add_widget(self.nom_prod)
        self.code_input=TextInput(hint_text='Code activation',multiline=False,size_hint_y=0.1)
        box.add_widget(self.code_input)
        for txt,fn in [("ACTIVER CODE",self.activer),("PAYER 2000F 1 MOIS - Wave 0171872289",self.info_mois),("PAYER 5000F A VIE - OM 0749425861",self.info_vie),("AJOUTER POIDS",self.ajouter),("GENERER PDF KKE",self.generer_pdf)]:
            b=Button(text=txt,size_hint_y=0.09); b.bind(on_press=fn); box.add_widget(b)
        return box
    def info_mois(self,i): self.lab.text="Pour 2000F 1 MOIS: Wave 0171872289"
    def info_vie(self,i): self.lab.text="Pour 5000F A VIE: OM 0749425861"
    def activer(self,i):
        c=self.code_input.text.strip().upper()
        if c.startswith("KKE-VIE-"):
            with open(LICENCE_FILE,'w') as f: f.write(f"VIE\ncount={self.pdf_count}")
            self.lab.text="LICENCE VIE ACTIVE - Illimite!"
        elif c.startswith("KKE-MOIS-"):
            with open(LICENCE_FILE,'w') as f: f.write(f"MOIS\ncount={self.pdf_count}")
            self.lab.text="LICENCE MOIS ACTIVE!"
        else: self.lab.text="Code invalide"
        self.code_input.text=""
    def check_licence(self):
        if not os.path.exists(LICENCE_FILE): return self.pdf_count<5
        try:
            with open(LICENCE_FILE,'r') as f:
                l=f.read()
                if "VIE" in l or "MOIS" in l: return True
        except: pass
        return self.pdf_count<5
    def ajouter(self,i):
        try:
            p=float(self.poids.text)
            if p<1 or p>5000: return
            self.total+=p
            self.nb=math.ceil(self.total/89)
            pleins=int(self.total//89)
            reste=self.total%89
            prix=int(self.prix.text) if self.prix.text else 1000
            self.lab.text=f"{self.total}kg = {self.nb} sacs\n{pleins} pleins + {reste:.1f}kg = {self.total*prix}F"
            self.poids.text=""
        except: self.lab.text="Entre prix et poids"
    def generer_pdf(self,i):
        if not self.check_licence():
            self.lab.text="ESSAI 5/5 TERMINE - PAYER"
            return
        try:
            pdf=FPDF(); pdf.add_page()
            if LOGO_FILE:
                try:
                    pdf.image(LOGO_FILE, x=65, y=10, w=80)
                    pdf.set_y(95)
                except: pdf.set_y(10)
            else: pdf.set_y(10)
            pdf.set_font("Arial","B",16)
            pdf.cell(0,12,"RECU CACAO KOUASSI K E",ln=True,align='C')
            pdf.set_font("Arial",size=11)
            pdf.ln(5)
            pdf.cell(0,7,f"Date: {datetime.datetime.now().strftime('%d/%m/%Y')}",ln=True)
            pdf.cell(0,7,f"Producteur: {self.nom_prod.text}",ln=True)
            pdf.cell(0,7,f"Poids Total: {self.total} kg",ln=True)
            pdf.cell(0,7,f"Sacs (89kg/sac): {self.nb} sacs",ln=True)
            prix=int(self.prix.text) if self.prix.text else 1000
            pdf.cell(0,7,f"Total: {self.total*prix} FCFA",ln=True)
            pdf.ln(8)
            pdf.cell(90,10,"Producteur",border=1,align='C')
            pdf.cell(90,10,"Acheteur KKE",border=1,ln=True,align='C')
            pdf.cell(90,30,"",border=1)
            pdf.cell(90,30,"K K E",border=1,ln=True,align='C')
            pdf.ln(5)
            pdf.set_font("Arial","I",8)
            pdf.cell(0,5,"KOUASSI K E - OM:0749425861 Wave:0171872289",align='C')
            out="/storage/emulated/0/Download/recu_cacao_KKE.pdf"
            pdf.output(out); pdf.output("recu_cacao_KKE.pdf")
            self.pdf_count+=1
            with open(LICENCE_FILE,'w') as f: f.write(f"count={self.pdf_count}")
            self.lab.text=f"PDF OK {self.pdf_count}/5 - Dans Download"
        except Exception as e: self.lab.text=f"Erreur {e}"

CacaoApp().run()