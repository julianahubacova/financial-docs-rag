"""
Génère un mémo d'investissement fictif en PDF, pour servir de document de test.
Aucune donnée réelle — tout est inventé.
Lance : python data/make_sample_pdf.py
"""
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch

doc = SimpleDocTemplate(
    "data/sample_memo.pdf", pagesize=letter,
    topMargin=1 * inch, bottomMargin=1 * inch,
)
styles = getSampleStyleSheet()
story = []

def h(txt):
    story.append(Paragraph(txt, styles["Heading2"]))
    story.append(Spacer(1, 6))

def p(txt):
    story.append(Paragraph(txt, styles["Normal"]))
    story.append(Spacer(1, 10))

story.append(Paragraph("Mémo d'investissement — Série A", styles["Title"]))
story.append(Spacer(1, 6))
p("Société cible : Boréal Logistics inc. (fictif). "
  "Secteur : logistique du dernier kilomètre. Siège : Montréal, Québec.")

h("1. Résumé de la transaction")
p("Boréal Logistics lève une ronde de série A de 12 M$ CA. "
  "BDC Capital envisage un investissement de 3 M$ pour une participation "
  "de 8,5 % sur une base entièrement diluée. La valorisation pré-money "
  "proposée est de 35 M$. Le chef de file de la ronde est un fonds de "
  "capital-risque montréalais non nommé.")

h("2. Thèse d'investissement")
p("La société exploite une plateforme d'optimisation de tournées de "
  "livraison alimentée par apprentissage automatique. Le revenu récurrent "
  "annuel (ARR) atteint 4,2 M$, en croissance de 140 % sur douze mois. "
  "La marge brute est de 68 %. Le taux de rétention net des revenus "
  "s'établit à 118 %.")

h("3. Principaux risques")
p("Concentration client : les trois plus gros clients représentent 46 % "
  "de l'ARR. Dépendance à un fournisseur cloud unique. Concurrence accrue "
  "de joueurs américains disposant de capitaux importants. Le taux de "
  "désabonnement (churn) logo est de 9 % par an.")

h("4. Conditions et clauses")
p("La ronde est structurée en actions privilégiées de série A avec une "
  "préférence de liquidation non participante de 1x. Un droit de "
  "participation proportionnelle (pro rata) est accordé aux investisseurs "
  "existants. Une clause anti-dilution à moyenne pondérée à base large "
  "est prévue. La période d'exclusivité proposée est de 45 jours.")

h("5. Recommandation")
p("L'équipe recommande de poursuivre la vérification diligente (due "
  "diligence) approfondie, en priorisant la validation de la "
  "concentration client et de la durabilité de la marge. Une décision "
  "finale est attendue au comité d'investissement du prochain trimestre.")

doc.build(story)
print("PDF créé : data/sample_memo.pdf")
