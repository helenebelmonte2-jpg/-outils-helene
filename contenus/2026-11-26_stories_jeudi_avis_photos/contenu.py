# Stories du jeudi (avis) sur les photos d'Hélène – 26/11/2026
# Uniquement des photos PAS encore publiées (mardi : meal prep, flans, gamelle, selfie rose déjà utilisés)
P = "contenus/2026-11-24_stories_lifestyle_photos/photos/"
STORIES = [
 {"photo": P + "7_cafe.jpg", "y": 300, "blocs": [
    ("Petit café et je lis vos commentaires…", 48, "white", "b"),
    ("Regardez ce qu'on m'a demandé cette semaine", 62, "pink")]},
 {"photo": P + "4_poire_voiture.jpg", "y": 230, "blocs": [
    ("En commentaire :", 44, "white", "b"),
    ("« Je voudrais que tu m'envoies tous les aliments que je peux manger »", 56, "dark"),
    ("Et une autre : « Heu… la liste ne doit pas être longue… »", 46, "white", "b")]},
 # story 3 = vidéo des courses (story_03.mp4), texte ci-dessous incrusté
 # stats du sondage de mardi (« Toi aussi tu manges tard ? » Oui 38 % / Non 62 %), sur son selfie du 26/11
 {"photo": "contenus/photos/photo_2026-11-26_selfie_tshirt_blanc.png", "y": 1330, "blocs": [
    ("Vous avez répondu à mon sondage !", 46, "white", "b"),
    ("38 % d'entre vous mangent tard le soir", 58, "pink"),
    ("Bonne nouvelle : ce n'est pas l'heure qui fait grossir, c'est ta journée entière qui compte", 44, "dark", "b")]},
 # story 5 (CTA) : fond rose natif (story_05_natif.py) – la photo salle est déjà publiée dans le carrousel « Mon histoire »
]
VIDEO = {"video": P + "video_courses.mp4", "y": 230, "blocs": [
    ("Eh bien si !", 62, "pink"),
    ("Regarde mes courses : légumes, fruits, féculents…", 52, "white"),
    ("La liste de ce que tu peux manger est BIEN plus longue que tu crois", 50, "dark")]}
