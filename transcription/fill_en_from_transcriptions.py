#!/usr/bin/env python3
"""Fill Question_EN and Answer_EN fields in deck.json from media transcription files."""

import argparse
import json
import re
import sys
from pathlib import Path


QUESTIONS_EN_VOCAB = {
    "Identify the tagged bony feature.": {
        "de": "Welches Knochenmerkmal ist hier markiert?",
        "fr": "Quel repère osseux est ici indiqué ?",
    },
    "Identify the tagged bone.": {
        "de": "Welcher Knochen ist hier markiert?",
        "fr": "Quel os est ici indiqué ?",
    },
    "Identify the tagged bone. Be specific.": {
        "de": "Welcher Knochen ist hier markiert? Bitte genau angeben.",
        "fr": "Quel os est ici indiqué ? Soyez précis·e.",
    },
    "Based on the image below, identify whether the bone is from the left or right side of the body.": {
        "de": "Stammt dieser Knochen aus der linken oder rechten Körperhälfte?",
        "fr": "Cet os provient-il du côté gauche ou du côté droit du corps ?",
    },
    "Which muscle inserts at the tagged bony feature?": {
        "de": "Welcher Muskel setzt an diesem Knochenmerkmal an?",
        "fr": "Quel muscle s'insère sur ce repère osseux ?",
    },
    "Identify the tagged structure.": {
        "de": "Welche Struktur ist hier markiert?",
        "fr": "Quelle structure est ici indiquée ?",
    },
    "Which muscle originates at the tagged bony feature?": {
        "de": "Welcher Muskel entspringt an diesem Knochenmerkmal?",
        "fr": "Quel muscle prend son origine sur ce repère osseux ?",
    },
    "Which muscles originate at the tagged bony feature?": {
        "de": "Welche Muskeln entspringen an diesem Knochenmerkmal?",
        "fr": "Quels muscles prennent leur origine sur ce repère osseux ?",
    },
    "Which muscles insert at the tagged bony feature?": {
        "de": "Welche Muskeln setzen an diesem Knochenmerkmal an?",
        "fr": "Quels muscles s'insèrent sur ce repère osseux ?",
    },
    "What is the embryological origin of the tagged structure?": {
        "de": "Welchen embryologischen Ursprung hat diese Struktur?",
        "fr": "Quelle est l'origine embryologique de cette structure ?",
    },
    "Identify the tagged mucous-lined air space.": {
        "de": "Welcher schleimhautausgekleidete Luftraum ist hier markiert?",
        "fr": "Quel espace aérien tapissé de muqueuse est ici indiqué ?",
    },
    "Where does the tagged mucous-lined air space drain?": {
        "de": "Wohin drainiert dieser schleimhautausgekleidete Luftraum?",
        "fr": "Où se draine cet espace aérien tapissé de muqueuse ?",
    },
    "Where does the tagged mucous-lined air space drain? Be specific.": {
        "de": "Wohin drainiert dieser schleimhautausgekleidete Luftraum? Bitte genau angeben.",
        "fr": "Où se draine cet espace aérien tapissé de muqueuse ? Soyez précis·e.",
    },
    "Based on the image below, identify whether the bone is from the left side or right side of the body.": {
        "de": "Stammt dieser Knochen aus der linken oder rechten Körperhälfte?",
        "fr": "Cet os provient-il du côté gauche ou du côté droit du corps ?",
    },
    "If a patient were to sustain a fracture at the indicated location, which structure might be vulnerable to tearing?": {
        "de": "Welche Struktur könnte bei einer Fraktur an dieser Stelle verletzungsgefährdet sein (Ruptur)?",
        "fr": "En cas de fracture à l'endroit indiqué, quelle structure serait susceptible d'être déchirée ?",
    },
    "If a patient were to sustain a fracture at the indicated location, which structure might be vulnerable to injury?": {
        "de": "Welche Struktur könnte bei einer Fraktur an dieser Stelle verletzungsgefährdet sein?",
        "fr": "En cas de fracture à l'endroit indiqué, quelle structure serait susceptible d'être lésée ?",
    },
    "If a patient were to sustain a fracture at the indicated location, which structures might be vulnerable to injury?": {
        "de": "Welche Strukturen könnten bei einer Fraktur an dieser Stelle verletzungsgefährdet sein?",
        "fr": "En cas de fracture à l'endroit indiqué, quelles structures seraient susceptibles d'être lésées ?",
    },
    "At which vertebral level does the tagged structure pass through the diaphragm?": {
        "de": "Auf welcher Wirbelkörperhöhe durchquert diese Struktur das Zwerchfell?",
        "fr": "À quel niveau vertébral cette structure traverse-t-elle le diaphragme ?",
    },
    "Considering the location indicated by the tag, which type of functional fibers is carried by this cranial nerve segment — sensory, motor, or both?": {
        "de": "Welcher Typ funktioneller Fasern wird von diesem Hirnnervenabschnitt geleitet — sensorisch, motorisch oder beides?",
        "fr": "Quel type de fibres fonctionnelles ce segment du nerf crânien véhicule-t-il — sensitif, moteur, ou les deux ?",
    },
    "For the cranial nerve segment that's tagged, which type of functional fibers does it contain — sensory, motor, or both?": {
        "de": "Welcher Typ funktioneller Fasern ist in diesem markierten Hirnnervenabschnitt enthalten — sensorisch, motorisch oder beides?",
        "fr": "Quel type de fibres fonctionnelles ce segment du nerf crânien contient-il — sensitif, moteur, ou les deux ?",
    },
    "From which level(s) of the sympathetic chain does the tagged structure predominantly arise?": {
        "de": "Aus welcher/welchen Ebene(n) des Sympathikusgrenzstrangs geht diese Struktur überwiegend hervor?",
        "fr": "De quel(s) niveau(x) de la chaîne sympathique cette structure est-elle principalement issue ?",
    },
    "Identify the tagged feature.": {
        "de": "Welches Merkmal ist hier markiert?",
        "fr": "Quel élément est ici indiqué ?",
    },
    "Identify the tagged meningeal layer.": {
        "de": "Welche Meningealhaut ist hier markiert?",
        "fr": "Quelle couche méningée est ici indiquée ?",
    },
    "Identify the tagged space.": {
        "de": "Welcher Raum ist hier markiert?",
        "fr": "Quel espace est ici indiqué ?",
    },
    "Identify the tagged structure. Be specific.": {
        "de": "Welche Struktur ist hier markiert? Bitte genau angeben.",
        "fr": "Quelle structure est ici indiquée ? Soyez précis·e.",
    },
    "Identify the tagged vertebra. Be specific.": {
        "de": "Welcher Wirbel ist hier markiert? Bitte genau angeben.",
        "fr": "Quelle vertèbre est ici indiquée ? Soyez précis·e.",
    },
    "Identify the vertebra shown below.": {
        "de": "Welcher Wirbel ist hier abgebildet?",
        "fr": "Quelle vertèbre est représentée ci-dessous ?",
    },
    "Identify the vertebra shown below. Be specific.": {
        "de": "Welcher Wirbel ist hier abgebildet? Bitte genau angeben.",
        "fr": "Quelle vertèbre est représentée ci-dessous ? Soyez précis·e.",
    },
    "If the indicated structure were damaged at the labeled location, which function(s) might be compromised?": {
        "de": "Welche Funktion(en) könnten bei einer Schädigung dieser Struktur an der markierten Stelle beeinträchtigt sein?",
        "fr": "En cas de lésion de cette structure à l'endroit indiqué, quelle(s) fonction(s) pourrait(-ent) être compromise(s) ?",
    },
    "Name the type of hernia that passes adjacent to a defect in the tagged structure.": {
        "de": "Welcher Hernientyp verläuft benachbart zu einem Defekt in dieser Struktur?",
        "fr": "Quel type de hernie passe à proximité d'un défect de cette structure ?",
    },
    "Name the type of hernia that passes immediately lateral to the tagged structure.": {
        "de": "Welcher Hernientyp verläuft unmittelbar lateral dieser Struktur?",
        "fr": "Quel type de hernie passe immédiatement en dehors de cette structure ?",
    },
    "Name the type of hernia that passes immediately medial to the tagged structure.": {
        "de": "Welcher Hernientyp verläuft unmittelbar medial dieser Struktur?",
        "fr": "Quel type de hernie passe immédiatement en dedans de cette structure ?",
    },
    "Name the type of hernia that passes through a defect in the tagged structure (between the level of the xiphoid process and umbilicus).": {
        "de": "Welcher Hernientyp tritt durch einen Defekt in dieser Struktur (zwischen Processus xiphoideus und Nabel)?",
        "fr": "Quel type de hernie passe à travers un défect de cette structure (entre le processus xiphoïde et l'ombilic) ?",
    },
    "Name the type of hernia that passes through the tagged region.": {
        "de": "Welcher Hernientyp tritt durch diese Region?",
        "fr": "Quel type de hernie passe à travers cette région ?",
    },
    "Name the type of hernia that passes through the tagged structure.": {
        "de": "Welcher Hernientyp tritt durch diese Struktur?",
        "fr": "Quel type de hernie passe à travers cette structure ?",
    },
    "Name the type(s) of hernias that can pass through the tagged structure.": {
        "de": "Welche Hernientypen können durch diese Struktur treten?",
        "fr": "Quel(s) type(s) de hernie(s) peut(-vent) passer à travers cette structure ?",
    },
    "The tagged structure is formed by the aponeuroses of which muscles?": {
        "de": "Durch die Aponeurosen welcher Muskeln wird diese Struktur gebildet?",
        "fr": "Par les aponévroses de quels muscles cette structure est-elle formée ?",
    },
    "The tagged structure is formed by the aponeurosis of which muscle?": {
        "de": "Durch die Aponeurose welchen Muskels wird diese Struktur gebildet?",
        "fr": "Par l'aponévrose de quel muscle cette structure est-elle formée ?",
    },
    "What are the actions of the tagged structure?": {
        "de": "Welche Funktionen hat diese Struktur?",
        "fr": "Quelles sont les actions de cette structure ?",
    },
    "What cell bodies are found in the tagged structure? Be specific.": {
        "de": "Welche Zellkörper sind in dieser Struktur zu finden? Bitte genau angeben.",
        "fr": "Quels corps cellulaires se trouvent dans cette structure ? Soyez précis·e.",
    },
    "What foramen does the tagged structure pass through?": {
        "de": "Durch welches Foramen verläuft diese Struktur?",
        "fr": "Par quel foramen cette structure passe-t-elle ?",
    },
    "What foramina does the tagged structure pass through?": {
        "de": "Durch welche Foramina verläuft diese Struktur?",
        "fr": "Par quels foramina cette structure passe-t-elle ?",
    },
    "What is the action of the tagged structure?": {
        "de": "Welche Funktion hat diese Struktur?",
        "fr": "Quelle est l'action de cette structure ?",
    },
    "What is the embryological origin of the cortex of the tagged structure?": {
        "de": "Welchen embryologischen Ursprung hat die Kortex dieser Struktur?",
        "fr": "Quelle est l'origine embryologique du cortex de cette structure ?",
    },
    "What is the embryological origin of the hepatocytes of the tagged structure?": {
        "de": "Welchen embryologischen Ursprung haben die Hepatozyten dieser Struktur?",
        "fr": "Quelle est l'origine embryologique des hépatocytes de cette structure ?",
    },
    "What is the embryological origin of the medulla of the tagged structure?": {
        "de": "Welchen embryologischen Ursprung hat die Medulla dieser Struktur?",
        "fr": "Quelle est l'origine embryologique de la médulla de cette structure ?",
    },
    "What is the embryological origin of the stroma and capsule of the tagged structure?": {
        "de": "Welchen embryologischen Ursprung haben Stroma und Kapsel dieser Struktur?",
        "fr": "Quelle est l'origine embryologique du stroma et de la capsule de cette structure ?",
    },
    "What is the innervation of the tagged structure?": {
        "de": "Wie wird diese Struktur innerviert?",
        "fr": "Quelle est l'innervation de cette structure ?",
    },
    "What is the origin and insertion of the tagged structure?": {
        "de": "Wo liegen Ursprung und Ansatz dieser Struktur?",
        "fr": "Quels sont l'origine et le point d'insertion de cette structure ?",
    },
    "What is the predominant type of efferent information carried by the tagged structure? Be specific.": {
        "de": "Welcher Typ efferenter Information wird überwiegend von dieser Struktur geleitet? Bitte genau angeben.",
        "fr": "Quel est le type prédominant d'information efférente véhiculée par cette structure ? Soyez précis·e.",
    },
    "Where do the fibers of the tagged structure primarily synapse to provide sympathetic innervation to organs in the abdomen?": {
        "de": "Wo schalten die Fasern dieser Struktur überwiegend um, um die sympathische Innervation der Bauchorgane zu gewährleisten?",
        "fr": "Où les fibres de cette structure font-elles principalement synapse pour assurer l'innervation sympathique des organes abdominaux ?",
    },
    "Which nerve primarily delivers preganglionic sympathetic inputs to the tagged structure?": {
        "de": "Welcher Nerv liefert überwiegend präganglionäre sympathische Afferenzen zu dieser Struktur?",
        "fr": "Quel nerf achemine principalement les influx sympathiques préganglionnaires vers cette structure ?",
    },
    "Which nerve provides preganglionic fibers responsible for enhancing motility in the tagged structure?": {
        "de": "Welcher Nerv liefert präganglionäre Fasern, die die Motilität dieser Struktur steigern?",
        "fr": "Quel nerf fournit les fibres préganglionnaires responsables de l'augmentation de la motilité de cette structure ?",
    },
    "Which nerve provides preganglionic fibers responsible for stimulating enzyme secretion in the tagged structure?": {
        "de": "Welcher Nerv liefert präganglionäre Fasern, die die Enzymsekretion in dieser Struktur stimulieren?",
        "fr": "Quel nerf fournit les fibres préganglionnaires responsables de la stimulation de la sécrétion enzymatique dans cette structure ?",
    },
    "Which nerve supplies preganglionic fibers responsible for enhancing motility in the tagged structure?": {
        "de": "Welcher Nerv versorgt diese Struktur mit präganglionären Fasern, die die Motilität steigern?",
        "fr": "Quel nerf envoie les fibres préganglionnaires responsables de l'augmentation de la motilité de cette structure ?",
    },
    "Which nerve supplies preganglionic fibers that stimulate acid secretion and increase motility in the tagged structure?": {
        "de": "Welcher Nerv versorgt diese Struktur mit präganglionären Fasern, die die Säuresekretion stimulieren und die Motilität steigern?",
        "fr": "Quel nerf envoie les fibres préganglionnaires qui stimulent la sécrétion acide et augmentent la motilité de cette structure ?",
    },
    "Which nerve supplies preganglionic fibers that trigger the release of bile from the tagged structure?": {
        "de": "Welcher Nerv versorgt diese Struktur mit präganglionären Fasern, die die Gallenfreisetzung auslösen?",
        "fr": "Quel nerf envoie les fibres préganglionnaires qui déclenchent la libération de bile depuis cette structure ?",
    },
    "Which nerves provide preganglionic fibers responsible for enhancing motility in the tagged structure?": {
        "de": "Welche Nerven liefern präganglionäre Fasern, die die Motilität dieser Struktur steigern?",
        "fr": "Quels nerfs fournissent les fibres préganglionnaires responsables de l'augmentation de la motilité de cette structure ?",
    },
    "Which spinal cord level(s) contribute to the formation of the tagged structure?": {
        "de": "Welche Rückenmarkssegmente tragen zur Bildung dieser Struktur bei?",
        "fr": "Quel(s) niveau(x) médullaire(s) contribue(nt) à la formation de cette structure ?",
    },
    "Which vital structures are enclosed within the tagged structure?": {
        "de": "Welche lebenswichtigen Strukturen sind in dieser Struktur eingeschlossen?",
        "fr": "Quelles structures vitales sont contenues dans cette structure ?",
    },
    "Based on the image below, identify whether the lung is from the left or right side of the body.": {
        "de": "Stammt die abgebildete Lunge von der linken oder rechten Körperseite?",
        "fr": "Le poumon illustré ci-dessous provient-il du côté gauche ou droit du corps ?",
    },
    "From which ventral rami does the tagged structure predominantly arise?": {
        "de": "Aus welchen Rami ventrales geht diese Struktur vorwiegend hervor?",
        "fr": "De quels rameaux ventraux cette structure provient-elle principalement ?",
    },
    "Identify the tagged impression.": {
        "de": "Welche Impression ist hier markiert?",
        "fr": "Quelle impression est ici indiquée ?",
    },
    "Identify the tagged region.": {
        "de": "Welche Region ist hier markiert?",
        "fr": "Quelle région est ici indiquée ?",
    },
    "Identify the tagged structures.": {
        "de": "Welche Strukturen sind hier markiert?",
        "fr": "Quelles structures sont ici indiquées ?",
    },
    "Name one symptom that would occur following damage to the tagged structure.": {
        "de": "Welches Symptom könnte bei einer Schädigung dieser Struktur auftreten?",
        "fr": "Quel symptôme pourrait survenir en cas de lésion de cette structure ?",
    },
    "The indicated area receives drainage from which anatomical structure?": {
        "de": "Von welcher anatomischen Struktur erhält das markierte Gebiet seinen Abfluss?",
        "fr": "De quelle structure anatomique la zone indiquée reçoit-elle le drainage ?",
    },
    "The indicated area receives drainage from which anatomical structures?": {
        "de": "Von welchen anatomischen Strukturen erhält das markierte Gebiet seinen Abfluss?",
        "fr": "De quelles structures anatomiques la zone indiquée reçoit-elle le drainage ?",
    },
    "Through which part of the vagina can fluid accumulation in the tagged structure be drained/ aspirated?": {
        "de": "Durch welchen Abschnitt der Vagina kann eine Flüssigkeitsansammlung in dieser Struktur drainiert/aspiriert werden?",
        "fr": "Par quelle partie du vagin une accumulation de liquide dans cette structure peut-elle être drainée/aspirée ?",
    },
    "Through which part of the vagina can fluid accumulation in the tagged structure be drained/aspirated?": {
        "de": "Durch welchen Abschnitt der Vagina kann eine Flüssigkeitsansammlung in dieser Struktur drainiert/aspiriert werden?",
        "fr": "Par quelle partie du vagin une accumulation de liquide dans cette structure peut-elle être drainée/aspirée ?",
    },
    "What are the embryological origins of the tagged structure?": {
        "de": "Welche embryologischen Ursprünge hat diese Struktur?",
        "fr": "Quelles sont les origines embryologiques de cette structure ?",
    },
    "What are the two embryological sources that converge at the tagged structure?": {
        "de": "Welche zwei embryologischen Quellen vereinigen sich an dieser Struktur?",
        "fr": "Quelles sont les deux sources embryologiques qui convergent au niveau de cette structure ?",
    },
    "What cranial nerve provides sensory innervation to the mucosa highlighted in yellow?": {
        "de": "Welcher Hirnnerv innerviert die gelb hervorgehobene Mukosa sensibel?",
        "fr": "Quel nerf crânien assure l'innervation sensitive de la muqueuse surlignée en jaune ?",
    },
    "What foramen does the tagged structure exit the skull through?": {
        "de": "Durch welches Foramen verlässt diese Struktur den Schädel?",
        "fr": "Par quel foramen cette structure quitte-t-elle le crâne ?",
    },
    "What is the embryological origin of the C-cells found within the tagged structure?": {
        "de": "Welchen embryologischen Ursprung haben die C-Zellen in dieser Struktur?",
        "fr": "Quelle est l'origine embryologique des cellules C présentes dans cette structure ?",
    },
    "What is the embryological origin of the cartilaginous, muscular, and connective tissue components of the tagged structure?": {
        "de": "Welchen embryologischen Ursprung haben die knorpeligen, muskulären und bindegewebigen Anteile dieser Struktur?",
        "fr": "Quelle est l'origine embryologique des composantes cartilagineuse, musculaire et conjonctive de cette structure ?",
    },
    "What is the embryological origin of the epithelium of the internal lining of the tagged structure?": {
        "de": "Welchen embryologischen Ursprung hat das Epithel der inneren Auskleidung dieser Struktur?",
        "fr": "Quelle est l'origine embryologique de l'épithélium du revêtement interne de cette structure ?",
    },
    "What is the embryological origin of the highlighted structure?": {
        "de": "Welchen embryologischen Ursprung hat die hervorgehobene Struktur?",
        "fr": "Quelle est l'origine embryologique de la structure mise en évidence ?",
    },
    "What is the embryological origin of the oocytes in the tagged structure?": {
        "de": "Welchen embryologischen Ursprung haben die Oozyten in dieser Struktur?",
        "fr": "Quelle est l'origine embryologique des ovocytes présents dans cette structure ?",
    },
    "What is the embryological origin of the primordial germ cells in the tagged structure?": {
        "de": "Welchen embryologischen Ursprung haben die Urkeimzellen in dieser Struktur?",
        "fr": "Quelle est l'origine embryologique des cellules germinales primordiales présentes dans cette structure ?",
    },
    "What is the sensory innervation of the tagged structure?": {
        "de": "Wie wird diese Struktur sensibel innerviert?",
        "fr": "Quelle est l'innervation sensitive de cette structure ?",
    },
    "What is the typical positional description of the tagged structure, referring to its orientation and angle relative to the vagina and cervix?": {
        "de": "Wie lautet die typische Lagebeschreibung dieser Struktur hinsichtlich ihrer Orientierung und Winkelstellung gegenüber Vagina und Zervix?",
        "fr": "Quelle est la description positionnelle typique de cette structure en termes d'orientation et d'angle par rapport au vagin et au col de l'utérus ?",
    },
    "What nerve carries general sensory information from the tagged region?": {
        "de": "Welcher Nerv leitet die allgemein-sensible Information aus dieser Region weiter?",
        "fr": "Quel nerf transporte l'information sensitive générale provenant de cette région ?",
    },
    "What nerve carries postganglionic parasympathetic fibers to the tagged structure?": {
        "de": "Welcher Nerv führt postganglionäre parasympathische Fasern zu dieser Struktur?",
        "fr": "Quel nerf achemine les fibres parasympathiques postganglionnaires vers cette structure ?",
    },
    "What nerve carries special visceral afferent (taste) information from the tagged region?": {
        "de": "Welcher Nerv leitet die speziell-viszerale afferente (gustatorische) Information aus dieser Region weiter?",
        "fr": "Quel nerf transporte l'information afférente viscérale spéciale (gustative) provenant de cette région ?",
    },
    "What nerve provides sensory innervation to the mucosa highlighted in yellow?": {
        "de": "Welcher Nerv innerviert die gelb hervorgehobene Mukosa sensibel?",
        "fr": "Quel nerf assure l'innervation sensitive de la muqueuse surlignée en jaune ?",
    },
    "What nerve provides sensory innervation to the tagged structure?": {
        "de": "Welcher Nerv innerviert diese Struktur sensibel?",
        "fr": "Quel nerf assure l'innervation sensitive de cette structure ?",
    },
    "What nerves provide sensory innervation to the tagged structure?": {
        "de": "Welche Nerven innervieren diese Struktur sensibel?",
        "fr": "Quels nerfs assurent l'innervation sensitive de cette structure ?",
    },
    "What other artery does the tagged structure anastomose with?": {
        "de": "Mit welcher anderen Arterie anastomosiert diese Struktur?",
        "fr": "Avec quelle autre artère cette structure s'anastomose-t-elle ?",
    },
    "What structure passes through the indicated foramen?": {
        "de": "Welche Struktur verläuft durch das markierte Foramen?",
        "fr": "Quelle structure passe par le foramen indiqué ?",
    },
    "What structures pass through the indicated foramen?": {
        "de": "Welche Strukturen verlaufen durch das markierte Foramen?",
        "fr": "Quelles structures passent par le foramen indiqué ?",
    },
    "What type of efferent information is carried by the tagged structure? Be specific.": {
        "de": "Welche Art efferenter Information wird von dieser Struktur geleitet? Bitte genau angeben.",
        "fr": "Quel type d'information efférente cette structure transporte-t-elle ? Soyez précis·e.",
    },
    "What was the name of the tagged structure during fetal development?": {
        "de": "Wie wurde diese Struktur während der Fetalentwicklung bezeichnet?",
        "fr": "Quel était le nom de cette structure au cours du développement fœtal ?",
    },
    "Where are the post-ganglionic parasympathetic cell bodies that innervate the tagged structure located?": {
        "de": "Wo befinden sich die postganglionären parasympathischen Zellkörper, die diese Struktur innervieren?",
        "fr": "Où se situent les corps cellulaires parasympathiques postganglionnaires qui innervent cette structure ?",
    },
    "Where does the tagged structure drain?": {
        "de": "Wohin drainiert diese Struktur?",
        "fr": "Où cette structure se draine-t-elle ?",
    },
    "Where does the tagged structure drain? Be specific.": {
        "de": "Wohin drainiert diese Struktur? Bitte genau angeben.",
        "fr": "Où cette structure se draine-t-elle ? Soyez précis·e.",
    },
    "Which component of the heart\u2019s conduction system is located within the tagged structure?": {
        "de": "Welche Komponente des Erregungsleitungssystems des Herzens befindet sich in dieser Struktur?",
        "fr": "Quel composant du système de conduction cardiaque se situe dans cette structure ?",
    },
    "Which dominancy is displayed by the heart shown below?": {
        "de": "Welchen Versorgungstyp weist das abgebildete Herz auf?",
        "fr": "Quel type de dominance le cœur illustré ci-dessous présente-t-il ?",
    },
    "Which nerves deliver sympathetic and parasympathetic inputs to the tagged structure?": {
        "de": "Welche Nerven leiten sympathische und parasympathische Impulse zu dieser Struktur?",
        "fr": "Quels nerfs acheminent les afférences sympathiques et parasympathiques vers cette structure ?",
    },
}

def parse_image_src(html: str) -> str | None:
    """Extract the image filename from an <img> tag."""
    match = re.search(r"""src=["']([^"']+)["']""", html)
    return match.group(1) if match else None


def build_answer_en(labels: list[dict]) -> str:
    """Build answer_en string from labels array.

    Single label, no details:    "Calcaneus"
    Single label, with details:  "Pectineal Line | Pectineus m."
    Multiple details:            "Linea Aspera | Adductor brevis m.; Adductor longus m."
    Multiple labels, no details: "Ilium | AIIS"
    Multiple labels + details:   "Ilium | AIIS; Rectus femoris m."

    With multiple labels, "|" is the label separator, so the label/detail
    boundary falls back to "; " to avoid collision.
    """
    multi_label = len(labels) > 1
    label_detail_sep = "; " if multi_label else " | "
    parts = []
    for label in labels:
        text = label["text"]
        details = label.get("details", [])
        if details:
            parts.append(f"{text}{label_detail_sep}{'; '.join(details)}")
        else:
            parts.append(text)
    return " | ".join(parts)


def load_transcriptions(transcriptions_dir: Path) -> dict[str, dict]:
    """Load all transcription JSON files into a dict keyed by filename (e.g. 'OsteologyUL1.jpeg')."""
    transcriptions = {}
    for path in transcriptions_dir.glob("*.json"):
        data = json.loads(path.read_text(encoding="utf-8"))
        filename = data.get("file", "")
        if filename:
            transcriptions[filename] = data
    return transcriptions


def fill_deck(
    deck_path: Path,
    transcriptions_dir: Path,
    overwrite: bool,
    fill_german_question: bool = False,
    fill_french_question: bool = False,
) -> dict:
    """Fill fields in deck.json from transcriptions and vocabulary.

    Returns stats dict with counts.
    """
    deck = json.loads(deck_path.read_text(encoding="utf-8"))
    transcriptions = load_transcriptions(transcriptions_dir)

    stats = {
        "question_en_filled": 0,
        "question_de_filled": 0,
        "question_fr_filled": 0,
        "answer_filled": 0,
        "skipped_no_transcription": 0,
        "skipped_existing": 0,
        "skipped_no_translation": 0,
    }

    def process_deck(node):
        for note in node.get("notes", []):
            fields = note["fields"]
            question_img = parse_image_src(fields[0])
            answer_img = parse_image_src(fields[4])

            # Resolve question_en from transcription
            q_en = None
            if question_img:
                q_transcription = transcriptions.get(question_img)
                if q_transcription and q_transcription.get("type") == "question":
                    q_en = q_transcription.get("question_en", "")

            # Fill Question_EN (fields[1])
            if question_img:
                if q_en:
                    if overwrite or not fields[1].strip():
                        fields[1] = q_en
                        stats["question_en_filled"] += 1
                    else:
                        stats["skipped_existing"] += 1
                else:
                    stats["skipped_no_transcription"] += 1

            # Fill Question_DE (fields[2])
            if fill_german_question and q_en:
                translation = QUESTIONS_EN_VOCAB.get(q_en, {}).get("de")
                if translation:
                    if overwrite or not fields[2].strip():
                        fields[2] = translation
                        stats["question_de_filled"] += 1
                    else:
                        stats["skipped_existing"] += 1
                else:
                    stats["skipped_no_translation"] += 1

            # Fill Question_FR (fields[3])
            if fill_french_question and q_en:
                translation = QUESTIONS_EN_VOCAB.get(q_en, {}).get("fr")
                if translation:
                    if overwrite or not fields[3].strip():
                        fields[3] = translation
                        stats["question_fr_filled"] += 1
                    else:
                        stats["skipped_existing"] += 1
                else:
                    stats["skipped_no_translation"] += 1

            # Fill Answer_EN (fields[6])
            if answer_img:
                a_transcription = transcriptions.get(answer_img)
                if a_transcription and a_transcription.get("type") == "answer":
                    labels = a_transcription.get("labels", [])
                    if labels:
                        a_en = build_answer_en(labels)
                        if overwrite or not fields[6].strip():
                            fields[6] = a_en
                            stats["answer_filled"] += 1
                        else:
                            stats["skipped_existing"] += 1
                    else:
                        stats["skipped_no_transcription"] += 1
                else:
                    stats["skipped_no_transcription"] += 1

        for child in node.get("children", []):
            process_deck(child)

    process_deck(deck)

    deck_path.write_text(json.dumps(deck, indent=4, ensure_ascii=False) + "\n", encoding="utf-8")
    return stats


def main():
    parser = argparse.ArgumentParser(description="Fill Question_EN and Answer_EN in deck.json from media transcriptions.")
    parser.add_argument(
        "--deck",
        type=Path,
        default=Path("deck.json"),
        help="Path to deck.json (default: deck.json)",
    )
    parser.add_argument(
        "--transcriptions",
        type=Path,
        default=Path("media-transcriptions"),
        help="Path to media-transcriptions directory (default: media-transcriptions)",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing values. Default: only fill empty fields.",
    )
    parser.add_argument(
        "--fill-german-question",
        action="store_true",
        help="Fill Question_DE from the vocabulary dictionary.",
    )
    parser.add_argument(
        "--fill-french-question",
        action="store_true",
        help="Fill Question_FR from the vocabulary dictionary.",
    )
    args = parser.parse_args()

    if not args.deck.exists():
        print(f"Error: deck file not found: {args.deck}", file=sys.stderr)
        sys.exit(1)
    if not args.transcriptions.is_dir():
        print(f"Error: transcriptions directory not found: {args.transcriptions}", file=sys.stderr)
        sys.exit(1)

    # Warn if translations are requested but vocab is not filled in
    if args.fill_german_question and not any(v.get("de") for v in QUESTIONS_EN_VOCAB.values()):
        print("Warning: no German translations in QUESTIONS_EN_VOCAB yet.", file=sys.stderr)
    if args.fill_french_question and not any(v.get("fr") for v in QUESTIONS_EN_VOCAB.values()):
        print("Warning: no French translations in QUESTIONS_EN_VOCAB yet.", file=sys.stderr)

    stats = fill_deck(
        args.deck,
        args.transcriptions,
        args.overwrite,
        fill_german_question=args.fill_german_question,
        fill_french_question=args.fill_french_question,
    )

    print(f"Question_EN filled:         {stats['question_en_filled']}")
    if args.fill_german_question:
        print(f"Question_DE filled:         {stats['question_de_filled']}")
    if args.fill_french_question:
        print(f"Question_FR filled:         {stats['question_fr_filled']}")
    print(f"Answer_EN filled:           {stats['answer_filled']}")
    print(f"Skipped (existing):         {stats['skipped_existing']}")
    print(f"Skipped (no transcription): {stats['skipped_no_transcription']}")
    if args.fill_german_question or args.fill_french_question:
        print(f"Skipped (no translation):   {stats['skipped_no_translation']}")


if __name__ == "__main__":
    main()
