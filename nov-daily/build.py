import json
N="NET"; F="FACT"
P={ # product lines for captions
 "M1":("📘 All 32 Questioned Documents PYQs, solved: NET-Cracker Module 1 · link in bio","#questioneddocuments","Questioned Documents"),
 "M4":("📘 All 36 Toxicology PYQs, solved: NET-Cracker Module 4 · link in bio","#forensictoxicology","Toxicology"),
 "M5":("📘 All 18 Fingerprint PYQs, solved: NET-Cracker Module 5 · link in bio","#fingerprints","Fingerprints"),
 "M6":("📘 All 39 Ballistics PYQs, solved: NET-Cracker Module 6 · link in bio","#ballistics","Ballistics"),
 "M9":("🎁 This whole module is FREE: NET-Cracker Module 9 · link in bio","#cyberforensics","Cyber Forensics"),
 "BIO":("📗 All 120 FACT 2026 Biology questions, solved: FACToids · link in bio","#forensicbiology","Forensic Biology"),
 "BAL":("📗 All 120 FACT 2026 Ballistics & Physics questions, solved: FACToids · link in bio","#ballistics","Ballistics"),
}
R=[
("14",N,"M4","2019","66","The antidote for methanol poisoning is:",["Ethylene glycol","Milk of magnesia","Amphetamine","Ethyl alcohol"],"D","Ethanol competes with methanol for alcohol dehydrogenase, blocking its conversion into toxic formaldehyde and formic acid.","🧪","Methanol poisoning: what's the antidote?"),
("15",F,"BIO","","54","A bloodstain on a horizontal surface is 8 mm wide and 16 mm long. At what angle did the drop strike?",["15°","45°","30°","60°"],"C","Impact angle = sin⁻¹(width ÷ length) = sin⁻¹(8/16) = sin⁻¹(0.5) = 30°.","🩸","Bloodstain maths: 8 mm wide, 16 mm long. What's the impact angle?"),
("16",N,"M1","2019","95","In handwriting comparison, 't' crossings and 'i'/'j' dots are considered as:",["Embellishments","Diacritics","Abbreviation","Minuscules"],"B","Diacritics are the small dots and cross-strokes added to letters; their placement and shape are habitual and compared closely.","✍️","What are 'i' dots and 't' crossings called in handwriting comparison?"),
("17",F,"BIO","","90","Which immunoglobulin mainly crosses the placenta in Rh incompatibility?",["IgA","IgE","IgM","IgG"],"D","IgG is the only antibody class that crosses the placenta, which is why it causes haemolytic disease of the newborn.","🧬","Rh incompatibility: which antibody crosses the placenta?"),
("18",N,"M9","2020","80","An Android device's encrypted data can be wiped remotely using:",["Find My Phone service","Google Sync","iCloud","Search My Sync"],"A","Google's Find My Device can remotely lock or wipe a lost Android phone. iCloud is Apple's equivalent.","📱","How can an Android phone's data be wiped remotely?"),
("19",F,"BAL","","98","How much constriction is there in a Quarter Choke shotgun?",["0.25 cm","0.25 mm","10/4 mm","1/2 mm"],"B","A Quarter Choke constricts the muzzle by about 0.25 mm. More constriction means a tighter shot pattern.","🎯","Quarter Choke: how much constriction?"),
("20",N,"M6","2019","97","A '12-bore' gun's barrel diameter is equal to:",["12 mm","The diameter of a lead ball weighing 1/12 lb","The diameter of a steel ball weighing 1/12 lb","12 inches"],"B","12 lead balls that exactly fit the bore weigh one pound, so each ball weighs 1/12 lb.","🔫","What does '12-bore' actually mean?"),
("21",F,"BIO","","95","Which plant material is MOST likely to give a false-positive benzidine test for blood?",["Potato","Onion","Garlic","Horseradish"],"D","Horseradish is rich in peroxidase, which mimics haemoglobin's peroxidase-like activity in the test.","🌱","Which vegetable can fool the benzidine blood test?"),
("22",N,"M5","2019","53","Which of these is NOT part of computer scanning and digitisation of a fingerprint?",["Indexing","Restriction","Feature extraction","Segmentation"],"B","Digital processing uses segmentation, feature extraction and indexing. 'Restriction' is not a step.","🖐️","Digital fingerprints: spot the odd step out."),
("23",F,"BIO","","78","After the 2017 expansion, how many STR loci are in the FBI's CODIS core panel?",["13","16","20","30"],"C","CODIS expanded from the original 13 core loci (1997) to 20 in 2017.","🧬","CODIS core STR loci after 2017: how many?"),
("24",N,"M1","2020","81","Erased writing in which ink can be restored by sulphocyanic acid fuming?",["Printing inks","Iron base inks","Indian inks","Ball pen inks"],"B","Residual iron salts react with thiocyanate to form blood-red ferric thiocyanate, making the erased writing readable again.","🖋️","Sulphocyanic acid fuming restores which erased ink?"),
("25",F,"BIO","","116","Which one is NOT a stage of the hair growth cycle?",["Anagen","Catagen","Medullagen","Telogen"],"C","The real stages are anagen (growth), catagen (transition) and telogen (rest). 'Medullagen' is made up.","💇","Hair growth cycle: which stage is fake?"),
("26",N,"M1","2018","74","Which technique is destructive in ink examination of a document?",["TLC (Thin Layer Chromatography)","VSC (Video Spectral Comparator)","ALS (Alternate Light Source)","IR microscopy"],"A","TLC needs a tiny plug of ink cut out and dissolved. VSC, ALS and IR examine the ink in place.","🔬","Ink analysis: which technique destroys the sample?"),
("27",F,"BIO","","99","Which is a known PCR inhibitor found in stool samples?",["Hemoglobin","Urea","Bile salts","Bacteria"],"C","Bile salts interfere with the polymerase, so faecal evidence needs extra purification before DNA amplification.","🧪","Which stool component blocks PCR?"),
("28",N,"M1","2021","43","A device that inks, embosses or perforates a money value onto a document is a:",["Photocopier","Check writer","Facsimile","Dandy roll"],"B","A check writer imprints the amount on cheques specifically to stop it being altered.","💵","Which device imprints the amount on a cheque?"),
("29",F,"BIO","","94","Which plant tissue is most useful in forensic wood identification?",["Parenchyma","Xylem","Phloem","Cambium"],"B","Xylem's vessels, tracheids and ray patterns differ between species, so it identifies the wood.","🪵","Forensic botany: which tissue identifies wood?"),
("30",N,"M1","2024","75","Variation in line width from pressure on a flexible split nib is known as:",["Line quality","Shading","Pen pressure","Fundamental difference"],"B","Shading is the widening of a stroke from extra pressure on a flexible nib, not the same as overall pen pressure.","✒️","Flexible nib, wider stroke. What's it called?"),
]
reels=[]; caps={}
for d,ex,prod,yr,q,qt,opts,ans,exp,emo,hook in R:
    id=f"nd-{d}"
    if ex==N:
        tag=f"UGC NET · PYQ {yr} · Q{q}"; src=f"From NET-Cracker Module {prod[1:]} · {P[prod][2]}"+(" (free)" if prod=="M9" else "")
        first=f"{P[prod][2]} PYQ · UGC NET Forensic Science {yr} {emo}"; share="Send this to your NET study partner 📩"; tags=f"#ugcnet #ugcnetforensicscience {P[prod][1]} #forensicscience #tfss"
    else:
        sub="Biology" if prod=="BIO" else "Ballistics"
        tag=f"FACT 2026 · {sub} · Section B"; book="Forensic Biological Sciences" if prod=="BIO" else "Forensic Ballistics and Physical Sciences"
        src=f"From FACToids of {book} · Q{q}"; first=f"{P[prod][2]} quiz · FACT 2026 {emo}"; share="Tag a friend preparing for FACT 📩"; tags=f"#factexam #fact2026 {P[prod][1]} #forensicscience #tfss"
    reels.append(dict(id=id,tag=tag,question=qt,options=opts,answer=ans,explanation=exp,reel_explain=exp,source=src))
    caps[id]=dict(date=f"2026-11-{d}T13:00:00",text=f"{first}\n{hook} You have 5 seconds.\n\nComment your answer before the reveal 👇\n{share}\n\n{P[prod][0]}\n\n{tags}")
json.dump(reels,open("nov-daily/reels.json","w"),ensure_ascii=False,indent=1)
json.dump(caps,open("nov-daily/captions.json","w"),ensure_ascii=False,indent=1)
print(len(reels))
