#!/usr/bin/env python3
"""Pilot: fill Text_Question_EN (index 4) for 8 diverse sample cards."""

import json

DRAFTS = {
    "e50JfD9$iW": "Which long, paired, strap-like muscle of the anterior abdominal wall originates from the pubic crest and pubic symphysis, inserts onto the xiphoid process and the costal cartilages of ribs 5–7, and lies within the rectus sheath on either side of the linea alba?",
    "fYj~p.4!1#": "Which paired vertical muscle lying within the rectus sheath between the pubic symphysis and the xiphoid process, and what segmental nerves provide its motor innervation?",
    "Ec;--r_)*_": "Which paired vertical muscle of the anterior abdominal wall running from the pubic crest to the xiphoid process and lower costal cartilages, and what are its principal actions?",
    "DK@|D/K*5|": "Which paired vertical muscle sits within the rectus sheath on either side of the linea alba, and what are its bony origin and insertion?",
    "yjb[wf;=Qp": "Which unpaired fibrous cord runs in the midline on the inner surface of the anterior abdominal wall from the apex of the bladder to the umbilicus — raising the median umbilical fold of the parietal peritoneum — and what is its embryological origin?",
    "ssB^9xbL#[": "Which paired, robust bony part of the first cervical vertebra lies between the anterior and posterior arches and bears the superior articular facet for the occipital condyles and the inferior articular facet for the axis?",
    "Ql2GU:D+mP": "Which branch of the common carotid artery ascends without giving off any cervical branches to supply the brain and orbit, and through which bony canal does it enter the skull base?",
    "r-]eDpx!tQ": "When examining an isolated os coxae in standard anatomical orientation, which three anatomical landmarks indicate its superior, lateral, and anterior aspects (thereby revealing which side of the body it comes from)?",
}


def walk(node, visit):
    for n in node.get("notes", []):
        visit(n)
    for c in node.get("children", []):
        walk(c, visit)


def main():
    path = "deck.json"
    with open(path) as f:
        data = json.load(f)

    updated = []

    def visit(note):
        guid = note.get("guid")
        if guid in DRAFTS:
            fields = note["fields"]
            assert fields[4] == "", f"{guid}: Text_Question_EN not empty: {fields[4]!r}"
            fields[4] = DRAFTS[guid]
            updated.append(guid)

    walk(data, visit)

    missing = set(DRAFTS) - set(updated)
    if missing:
        raise SystemExit(f"GUIDs not found: {missing}")

    with open(path, "w") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    print(f"Updated {len(updated)} cards")


if __name__ == "__main__":
    main()
