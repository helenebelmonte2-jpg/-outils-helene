# Source : vidéo YouTube « haut en jean » (WeTransfer du 28/11, video.mp4 1280x720, 17 min, sous-titres incrustés en bas)
export WORDS=transcript.json CROP="865:565:207:0"
M=/home/user/-outils-helene/scripts/mofu.py
r(){ python3 -I $M video.mp4 "$1" "$2" "$3" "$4" "out/$5" "$6" 2>&1 | tail -1; }
r 49.7 137.35 "Tu dis toujours « je commence lundi » ?" "Voilà pourquoi tu [craques le soir] :" MOFU_J1_lundi.mp4 "lundi,restriction,craqué,faim,motivation"
r 137.4 199.5 "Motivée le matin, tu craques le soir ?" "Ce n'est pas [ta faute] :" MOFU_J2_motivation.mp4 "motivation,émotion,discipline,frustration,autoriser"
r 199.6 244.9 "Avant de vouloir perdre du poids," "pose-toi [cette question] :" MOFU_J3_cause.mp4 "pourquoi,cause,grossesse,travail,choc"
r 327.1 414.2 "Tu dévores tout en rentrant du travail ?" "Moi aussi, [j'étais comme toi] :" MOFU_J4_soignante.mp4 "restriction,soignante,placards,craque,culpabiliser,fatiguée"
r 422.5 505.6 "Le régime de ta voisine" "ne marchera [jamais sur toi] :" MOFU_J5_voisine.mp4 "adapté,voisine,rythme,shampoing,méthode"
r 538.6 624.4 "Tu manges quand tu t'ennuies ?" "Découvre ton [profil de mangeuse] :" MOFU_J6_mangeuse.mp4 "mangeuse,ennui,émotion,refuge,nourriture,récompenser,estomac,muscle"
r 889.7 946.6 "Tu te dis « je me dégoûte »" "devant le miroir ? [Fais ça] :" MOFU_J7_miroir.mp4 "miroir,amie,belle,aimer,investir,corps"
