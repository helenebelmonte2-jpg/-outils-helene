export WORDS=transcript.json CROP="812:530:426:0"
M=/home/user/-outils-helene/scripts/mofu.py
r(){ python3 -I $M video.mp4 "$1" "$2" "$3" "$4" "out/$5" "$6" 2>&1 | tail -1; }
r 0.0 75.7 "Tu reprends du poids après chaque régime ?" "Ce n'est pas un [manque de volonté] :" MOFU_01_reprendre_apres_regime.mp4 "volonté,méthode,restriction,plaisir"
r 87.3 144.0 "Pourquoi ton corps [stocke tout]" "après un régime trop strict :" MOFU_02_corps_stocke.mp4 "économie,énergie,stocker,stocke,fatigué,peur"
r 144.0 228.1 "Pourquoi tu as encore plus envie" "de ce que tu [t'interdis] :" MOFU_03_frustration.mp4 "frustration,interdit,nutella,plaisir"
r 228.1 305.0 "Un carré de chocolat ne fait pas grossir." "Ce qui fait grossir, [c'est ça] :" MOFU_04_foutu_pour_foutu.mp4 "foutu,abandonne,chocolat,plaisir,pizza"
r 383.2 435.6 "Une soignante ne mange pas comme" "quelqu'un qui fait du [8h-17h] :" MOFU_05_rythme_de_vie.mp4 "rythme,soignante,horaires,plaisir"
r 609.8 693.9 "Pas besoin de te priver pour maigrir." "Tout est une question d'[équilibre] :" MOFU_06_equilibre.mp4 "équilibre,équilibré,chocolat,sport,plaisir"
r 745.1 833.5 "Perdre 10 kg en 15 jours ?" "Voilà pourquoi tu vas [tout reprendre] :" MOFU_07_perte_progressive.mp4 "progressive,stabilisation,habitudes,écart,écarts"
r 897.3 971.9 "Le secret n°1 pour ne jamais" "[reprendre tes kilos] :" MOFU_08_se_faire_accompagner.mp4 "accompagner,objectif,extérieur,habitudes"
