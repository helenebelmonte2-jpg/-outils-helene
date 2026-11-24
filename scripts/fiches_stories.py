"""Génère les fiches stories (HTML -> Google Docs) pour chaque jour de la stratégie."""
import os
OUT = "fiches"
STRAT = """<h2>Rappel : ta stratégie stories de la semaine</h2>
<table border="1" cellpadding="6"><tr><th>Jour</th><th>Thème</th></tr>
<tr><td>Lundi</td><td>Valeur + CTA</td></tr>
<tr><td>Mardi</td><td>Fausse croyance → vraie croyance (« On dit souvent que… »)</td></tr>
<tr><td>Mercredi</td><td>Sur toi, en lien avec ta niche</td></tr>
<tr><td>Jeudi</td><td>Avis : clientes, amies, entourage…</td></tr>
<tr><td>Vendredi</td><td>Valeur + CTA</td></tr>
<tr><td>Samedi</td><td>Lifestyle</td></tr>
<tr><td>Dimanche</td><td>Boîte à questions</td></tr></table>"""

def table(rows, h=("Idée", "Exemple de story")):
    r = "".join(f"<tr><td>{a}</td><td>{b}</td></tr>" for a, b in rows)
    return f'<table border="1" cellpadding="6"><tr><th>{h[0]}</th><th>{h[1]}</th></tr>{r}</table>'

def page(title, intro, ideas, typical, rules, extra=""):
    ol = "".join(f"<li>{x}</li>" for x in typical)
    ul = "".join(f"<li>{x}</li>" for x in rules)
    return f"""<html><head><meta charset="utf-8"></head><body>
<h1>{title}</h1>{intro}
<h2>Idées de stories</h2>{table(ideas)}
<h2>Exemple de journée type (5 à 8 stories)</h2><ol>{ol}</ol>
<h2>Les règles pour que ça marche</h2><ul>{ul}</ul>{extra}
{STRAT}</body></html>"""

FICHES = {
"stories_valeur_cta": page(
 "Fiche : les stories valeur + CTA (lundi et vendredi)",
 "<p><b>C'est quoi ?</b> Tu donnes un vrai conseil utile, gratuit, que ton abonnée peut appliquer tout de suite. Puis tu l'invites à passer à l'action : t'écrire.</p><p><b>Pourquoi ça marche :</b> tu prouves ton expertise. Elle se dit « si elle donne déjà ça gratuitement, imagine en accompagnement ». C'est là que naissent les conversations en message, puis les appels.</p>",
 [("🍽️ L'assiette idéale", "Photo de ton assiette : ½ légumes, ¼ protéines, ¼ féculents. « Mon assiette pour être calée jusqu'au soir »"),
  ("🔍 Lecture d'étiquette", "Au supermarché : « Ce produit soi-disant healthy… regarde le sucre 👀 »"),
  ("🔄 Les remplacements", "« Au lieu du granola → flocons d'avoine + fruits. Même plaisir, 2× moins de sucre »"),
  ("🌙 Spécial horaires décalés", "« Ce que je mange pendant une garde de nuit pour ne pas grignoter »"),
  ("🍫 Les fringales", "« Fringale de 16 h ? 3 encas qui calent vraiment »"),
  ("💧 Les petites habitudes", "« Un grand verre d'eau avant chaque repas : voici pourquoi »"),
  ("🛒 La liste de courses", "« Les 10 aliments toujours dans mon frigo »")],
 ["Accroche : « Tu grignotes l'après-midi ? Regarde ça 👇 »",
  "Le problème : pourquoi ça arrive (1 phrase)",
  "Le conseil n° 1 (photo ou vidéo de toi)",
  "Le conseil n° 2",
  "Quiz ou sondage : « Tu le savais ? » Oui / Non",
  "Récap en 1 phrase",
  "CTA : « Tu veux savoir ce qui bloque TA perte de poids ? Écris-moi DÉCLIC 💌 »"],
 ["<b>Un seul sujet</b> par jour, avec des conseils simples et concrets.",
  "<b>Montre-toi</b> : face caméra ou tes vraies assiettes, c'est plus crédible.",
  "<b>Toujours finir par un CTA clair</b> : « Écris-moi DÉCLIC » (en message, pas en commentaire).",
  "Jamais les mots « régime » ou « diète » pour ta méthode : toujours « rééquilibrage alimentaire ».",
  "Les meilleurs sujets = les questions qu'on te pose en message : note-les !"]),

"stories_on_dit_souvent": page(
 "Fiche : les stories fausse croyance → vraie croyance (mardi)",
 "<p><b>C'est quoi ?</b> Tu prends une idée reçue sur la perte de poids (« On dit souvent que… ») et tu la démontes (« En réalité… »).</p><p><b>Pourquoi ça marche :</b> ça surprend, ça fait réagir, et ça te positionne comme experte. Tes abonnées se disent « ah, c'est pour ça que ça n'a jamais marché pour moi ! ».</p>",
 [("Déjà utilisées (24/11)", "Manger moins · Manger le soir fait grossir · Si je craque, j'ai tout gâché"),
  ("À utiliser", "« Il faut supprimer le pain et les féculents »"),
  ("À utiliser", "« Il faut faire beaucoup de sport pour perdre du poids »"),
  ("À utiliser", "« Le sucré, c'est interdit »"),
  ("À utiliser", "« Les produits light font maigrir »"),
  ("À utiliser", "« Sauter un repas aide à perdre du poids »"),
  ("À utiliser", "« Il faut se peser tous les jours »"),
  ("À utiliser", "« Les fruits, on peut en manger à volonté »"),
  ("À utiliser", "« Perdre du poids, c'est une question de volonté »")],
 ["« On dit souvent que… » idée reçue n° 1 + <b>sticker Quiz</b> Vrai / Faux",
  "« En réalité… » la réponse (idéalement filmée face caméra)",
  "« On dit souvent que… » idée reçue n° 2 + Quiz",
  "« En réalité… »",
  "« On dit souvent que… » idée reçue n° 3 + Quiz",
  "« En réalité… »",
  "CTA : « Laquelle on t'a déjà dite ? Écris-moi DÉCLIC »"],
 ["<b>3 idées reçues maximum</b> par mardi : garde les autres pour les semaines suivantes.",
  "<b>Style natif</b> Instagram (texte sur fond coloré), pas de visuels trop « design ».",
  "<b>Toujours un quiz</b> sur l'idée reçue : le suspense fait taper, et les réponses boostent ta portée.",
  "Réponse courte : 20 mots maximum, lisible en 3 secondes.",
  "Modèle prêt à réutiliser : je te refais les visuels avec les nouvelles idées reçues quand tu veux."]),

"stories_sur_moi": page(
 "Fiche : les stories sur toi, en lien avec ta niche (mercredi)",
 "<p><b>C'est quoi ?</b> Tu parles de toi, mais toujours en rapport avec la perte de poids, la nourriture et ta vie de femme débordée.</p><p><b>Pourquoi ça marche :</b> on achète à quelqu'un qu'on connaît et à qui on s'identifie. Ton histoire (complexes, kilos repris, peur de manger, déclic) est ta meilleure arme.</p>",
 [("🩺 Ta vie de soignante", "« Aide-soignante depuis plus de 15 ans : voici comment je gère mes repas avec mes horaires »"),
  ("📖 Ton histoire", "« Ado, j'étais très complexée… » (un morceau de ton parcours chaque mercredi)"),
  ("💡 Ton déclic", "« Le jour où j'ai compris que la privation ne servait à rien »"),
  ("😔 Tes anciens échecs", "« J'ai essayé plusieurs coachs… et j'ai tout repris. Voilà ce qui manquait »"),
  ("💛 Ton pourquoi", "« Pourquoi j'ai créé Oser se choisir »"),
  ("🎯 Tes valeurs", "« Chez moi, jamais de régime, jamais de culpabilité. Voilà pourquoi »"),
  ("🙋‍♀️ Tes coulisses de coach", "« Je prépare le plan alimentaire d'une cliente » (sans info perso)")],
 ["Accroche : « Je ne vous ai jamais raconté ça… »",
  "Le moment de ton histoire (photo ou face caméra)",
  "Ce que tu ressentais à ce moment-là",
  "Sondage : « Toi aussi tu as déjà vécu ça ? » 🙋‍♀️ / Non",
  "Ce que tu as appris / ce qui a changé",
  "Le lien avec ton accompagnement",
  "CTA doux : « Si tu te reconnais, écris-moi MOI 💌 »"],
 ["<b>Toujours un lien avec ta niche</b> : on parle de toi pour qu'elles se reconnaissent.",
  "<b>Sois sincère</b>, même sur les moments difficiles, mais partage seulement ce que tu veux. Jamais de photos avant/après.",
  "<b>Face caméra</b> le plus possible : c'est le jour où ta voix compte le plus.",
  "Tu peux reprendre ton carrousel « Mon histoire » en morceaux, un mercredi à la fois.",
  "Termine par une question ou un CTA doux, pas par de la vente forcée."]),

"stories_avis": page(
 "Fiche : les stories avis (jeudi)",
 "<p><b>C'est quoi ?</b> Tu montres ce que les autres disent de toi : clientes, amies, collègues, abonnées.</p><p><b>Pourquoi ça marche :</b> une personne qui parle de toi est plus crédible que toi qui parles de toi. C'est ce qui rassure avant d'acheter.</p><p><b>Tu as peu de témoignages ? Pas de panique.</b> Tout ce qui montre que tu aides déjà, ou que les gens réagissent à ton contenu, compte comme preuve sociale.</p>",
 [("💬 Messages d'abonnées", "Capture (prénom et photo cachés) : « Merci pour ton astuce, j'ai testé ! »"),
  ("🗳️ Résultats de sondages", "« 82 % d'entre vous grignotent le soir… vous n'êtes pas seules ! »"),
  ("🙋‍♀️ Questions reçues", "« On m'a demandé… » : ça montre qu'on te fait confiance"),
  ("👭 Amies et entourage", "Une amie, une collègue soignante qui dit ce que tu lui as apporté (avec son accord)"),
  ("❤️ Commentaires", "Capture d'un beau commentaire sous un Reel"),
  ("🎁 Retours sur ton test DÉCLIC", "« Ce test m'a ouvert les yeux » (avec accord)"),
  ("🏆 Tes clientes fondatrices", "Dès que tu as tes premières clientes : leurs retours, leurs victoires (pas que la balance)")],
 ["Accroche : « Regardez le message que j'ai reçu ce matin 🥹 »",
  "La capture (prénom caché)",
  "Ton petit mot : ce que ça te fait",
  "Une 2e capture ou le résultat d'un sondage",
  "« Toi aussi tu veux ce déclic ? »",
  "CTA : « Écris-moi DÉCLIC 💌 »"],
 ["<b>Toujours demander l'accord</b> et cacher le prénom et la photo.",
  "<b>Garde chaque gentil message</b> dans un album « Avis » sur ton téléphone : c'est ton stock pour les jeudis.",
  "Les victoires hors balance comptent aussi : énergie, sommeil, confiance, vêtements qui vont mieux.",
  "Mets les meilleures dans ta story à la une « Retour clientes ».",
  "Si tu n'as rien un jeudi : partage les résultats d'un sondage ou une question reçue."]),

"stories_boite_a_questions": page(
 "Fiche : les stories boîte à questions (dimanche)",
 "<p><b>C'est quoi ?</b> Tu ouvres un sticker « Pose-moi tes questions », puis tu réponds en story.</p><p><b>Pourquoi ça marche :</b> tes abonnées interagissent, tu découvres leurs vrais blocages (des idées de contenus gratuites !), et tu montres ton expertise en direct.</p>",
 [("📦 Le sticker", "« Pose-moi ta question perte de poids, je réponds à tout 💬 »"),
  ("🎯 Thème précis", "« Spécial horaires décalés : pose-moi tes questions ! »"),
  ("🍽️ Spécial repas", "« Une question sur tes repas ? Je te réponds »"),
  ("😅 Questions perso", "« Pose-moi une question sur moi ! » (pour créer du lien)"),
  ("🔁 Si personne ne répond", "Réponds à des questions qu'on t'a déjà posées en message (prénom caché)")],
 ["Le matin : story avec le <b>sticker questions</b> (+ une photo de toi souriante)",
  "Rappel l'après-midi : « Il reste quelques heures pour me poser tes questions ! »",
  "Le soir : tes réponses, <b>1 question = 1 story</b>, idéalement face caméra",
  "Une réponse plus longue = une idée de Reel pour la semaine",
  "Dernière story : « Tu veux aller plus loin ? Écris-moi DÉCLIC 💌 »"],
 ["<b>Réponds face caméra</b> : 15-20 secondes par question.",
  "<b>Garde les questions</b> : ce sont tes idées de Reels et de stories pour les semaines suivantes.",
  "Si une question touche à la santé (maladie, traitement, TCA), oriente vers un médecin ou un diététicien.",
  "Les premières fois, il y aura peu de questions : c'est normal, continue chaque dimanche.",
  "Tu peux répondre à une question en DM et proposer d'en parler en appel."]),
}

for name, html in FICHES.items():
    open(os.path.join(OUT, name + ".html"), "w").write(html)
    print(name)
