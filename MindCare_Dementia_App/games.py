import random
OBJECTS=[("apple","Apple","🍎"),("cup","Cup","☕"),("key","Key","🔑"),("book","Book","📘"),("flower","Flower","🌼"),("clock","Clock","🕒"),("ball","Ball","⚽"),("hat","Hat","🧢"),("bread","Bread","🍞"),("phone","Phone","📱"),("car","Car","🚗"),("fish","Fish","🐟")]
COLORS=[("red","Red","🔴"),("blue","Blue","🔵"),("green","Green","🟢"),("yellow","Yellow","🟡"),("purple","Purple","🟣"),("orange","Orange","🟠")]
PAIRS=[(("cup","Cup","☕"),("tea","Tea","🫖")), (("key","Key","🔑"),("lock","Lock","🔒")), (("toothbrush","Toothbrush","🪥"),("toothpaste","Toothpaste","🧴")), (("book","Book","📘"),("reading","Reading","👓")), (("shoe","Shoe","👟"),("sock","Sock","🧦"))]
def item(t): return {"id":t[0],"label":t[1],"emoji":t[2]}
def make(key,p):
    if key=="sequence":
        seq=[random.choice(COLORS) for _ in range(p["count"])]
        return {"type":key,"sequence":[x[0] for x in seq],"display":[item(x) for x in seq],"choices":[item(x) for x in COLORS],"delay":p["delay"]}
    if key=="missing_object":
        chosen=random.sample(OBJECTS,p["count"]); missing=random.choice(chosen)
        return {"type":key,"items":[item(x) for x in chosen if x!=missing],"choices":[item(x) for x in chosen],"answer":missing[0]}
    if key=="association":
        pairs=random.sample(PAIRS,p["count"]); left=[item(x[0]) for x in pairs]; right=[item(x[1]) for x in pairs]; random.shuffle(right)
        return {"type":key,"left":left,"right":right,"answers":{x[1][0]:x[0][0] for x in pairs}}
    if key=="recognition":
        n=p["remember"]; target=random.sample(OBJECTS,n); distract=random.sample([x for x in OBJECTS if x not in target],p["choices"]-n)
        choices=target+distract; random.shuffle(choices)
        return {"type":key,"targets":[item(x) for x in target],"choices":[item(x) for x in choices]}
