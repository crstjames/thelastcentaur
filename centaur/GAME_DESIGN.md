# The Last Centaur — Game Design

> Status: **agreed, building.** This replaces the three-path design in `DESIGN.md`.

## Decisions so far

| | |
|---|---|
| Structure | **One long path**: a prologue, three acts (spear, shield, armor) and a finale |
| Feel | **Opaque, Myst-like.** No goals stated, no quest log. Everything you need is in the world. |
| Map | **Fixed, hand-placed.** Every player gets the same world. |
| Input | Classic commands (`look`, `n`, `take`, …) always work directly. The LLM handles everything else. |
| Combat | Stays as is: win if you have what it takes, get driven back if not |
| Hints | **Soft.** The world reacts when you're close. There's no hint command. |
| Story | **Greek myth, retold.** Centaur Prime recovers his spear, shield and armor, kills Ixion, and frees the captive herd. See *The story*. |
| Ending | **One ending.** Ixion dies and the Stables are opened. |
| Choices | Only some encounters offer spare/kill (the Bound Guardian, the Ker). Ixion is always killed. |
| Danger | Wolves bite at night in the Awakening Woods. |

## Design pillars

1. **Fair opacity.** The game never tells you what to do, but every solution can be worked out from things you can find *before* you need them. The solver proves this mechanically (see *Fairness*).
2. **Do, don't just carry.** Items are tools, not keys. Holding the Focus opens nothing; holding it up to sunlight in the right place does.
3. **Learn a rule, use it everywhere.** The world has a few consistent laws. Learning them is the real progression.
4. **The world remembers.** Tiles keep a memory of what happened there. Some memories were there before you arrived.
5. **Free choices have consequences.** You won't get softlocked, but how you solve things shapes the ending.

## The story

> Status: **agreed and built** for the Prologue and Acts I–III. The finale is next.

The rule for this story: **steal from Greek myth.** Every name and big idea comes from real myth, then gets bent to fit. The myth gives it weight; our version gives it a revenge plot.

**Tone:** Kratos's pride and fury, Jason Bourne's amnesia (the body remembers before the mind does), and Maximus's honour and vengeance. The hero is honourable. The villain is not. There's no moral twist about the hero; it's a story about restoring centaur pride.

### The world

For as long as anyone remembers, the centaur herds ran free across the land. Men feared them, envied them, and most of all wanted to *ride* them. The **Lapiths**, a kingdom of horse-tamers, spent generations learning to break horses. They wanted to break centaurs too.

### The villain: Ixion, the Bridle-King

- **The myth:** Ixion was a Lapith king who reached above his station. He tried to seduce Hera, Zeus tricked him with a cloud shaped like her, and from that union came **Centaurus, father of all centaurs**. Zeus bound Ixion to a **burning wheel** for eternity.
- **Our version:** Ixion is a centaur who claims the old Ixion's blood and took his name. If centaurs came from a man, he says, they can go back to being men. He preaches that **the horse half is the curse**: the beast in centaurs makes them proud, wild and forever at war, and the only way to survive in a world of men is to **take the bridle**.
- His creed comes in three steps, each worse than the last:
  1. **Kneel** to the Lapith kings.
  2. **Be shod and bridled.** Serve as their war-mounts and be ridden into battle.
  3. **Be Unmade.** The Lapiths' sorcery burns away the hooves and the horse body and remakes a centaur as a man: smaller, weaker, "civilised", and safe.
- Centaurs who follow him are **the Bridled**. The Free Herds call him **the Bridle-King** behind his back. He wears a **golden bridle as a crown**, and his sigil is a **wheel**, a nod to the myth.
- His ally is **King Pirithous** of the Lapiths, who is Ixion's son in the myth. Pirithous gave him the sorcery of Unmaking.

### The hero: Centaur Prime

*(Placeholder name. The real name comes later.)*

- Warlord of the **Free Herds**: the greatest and proudest centaur alive, and the most honourable. He has never knelt.
- When Ixion's creed split the herds, Prime led the Free Herds against the Bridled and their Lapith allies in **the War of the Bridle**. In the myth, the centaurs and the Lapiths fought a great war that began at Pirithous's wedding. This is that war, retold.
- It ended in one last battle. When the dust settled, Prime was the only one standing, on either side. He believes he is **the last centaur**.
- His war gear is legendary: **an ash spear, a shield and a bronze cuirass**. He lost all three.

### Before the game

*(The player never sees this directly. It comes back as memories.)*

1. **The war.** The Free Herds fight the Bridled. Prime wins and everyone else dies. Somewhere on the field he spares a Lapith captain, Caeneus, and the captain carries Prime's fallen shield away.
2. **The rumour.** Years later, word drifts in from the villages of men: a centaur in the north wears a golden bridle as a crown. Horses are going missing. So are foals. **Ixion lives.**
3. **The ride north.** Prime goes alone, in a rage, against all sense, because that's what pride does.
4. **The ambush.** At Ixion's threshold, the Bridle-King uses the Lapith sorcery on him. He doesn't kill Prime. He **bridles his mind**, taking his strength, his memory and his name. Prime's spear, shield and armor are stripped from him and scattered.

### The game

You wake on cold earth in the woods. You don't know who you are, but your body does. Your hands know how to hold a weapon, you understand wolves, and you carry a rage with nowhere to aim it.

Three quests each win back one piece of your war gear. **Each piece breaks part of the bridle on your mind** and brings back part of who you are.

| | Act I | Act II | Act III |
|---|---|---|---|
| **Who you meet** | **Melia**, an ash-tree dryad | **Caeneus**, a Lapith captain (human) | **Silenus**, an old satyr (half-beast) |
| **What you win** | **The Spear** | **The Shield** | **The Armor** |
| **What comes back** | Who you **are** | What you **lost** | Who **did this** |

#### Act I: Melia and the Spear

- **The myth:** The Meliae were the nymphs of the ash tree, born from the blood of Ouranos. Ash was the wood of the great spears: Achilles' spear was cut from an ash on Mount Pelion.
- **Our version:** Melia is the dryad of an ancient ash in her grove. Prime's spear was cut from *her* tree, so she knows the spear and she knows him. She is patient, ancient and cryptic. She won't simply hand it over: Ixion's servants hid the spear in the Crystal Caves, and she tells you how to find your way in.
- **When you grip the spear:** the body remembers first. You're a warrior and a centaur, and you once led the Free Herds. You still have no name, only the feeling of thousands of hooves behind you.
- **Gameplay:** you can fight now. The wolves stop being a threat.

#### Act II: Caeneus and the Shield

- **The myth:** Caeneus was the Lapith hero who couldn't be wounded. In the war with the centaurs no weapon could pierce him, so in the end the centaurs buried him under pine trunks.
- **Our version:** Caeneus fought Prime in the last battle and lost. Prime spared him. He carried Prime's shield off the field out of respect. A Lapith can't hang a centaur's shield in his tent, so he laid it under a cairn with Prime's dead. He's a Lapith and Prime's enemy, but he despises what Pirithous and Ixion did with the sorcery. This is the Gladiator note: enemies who honour each other.
- He won't speak to you at first. Once you can read the names of your Honor Guard on his trophy standards, he shows you the way into your old stronghold. Then you face the bound spirits of those same warriors, which Ixion chained to the valley as his guardian.
- **When you raise the shield:** you remember the last battle. Every centaur fell, on both sides, and you walked off the field alone. Now you know what you lost: everyone. You believe you are the last.

#### Act III: Silenus and the Armor

- **The myth:** Silenus was the oldest of the satyrs, Dionysus's drunken tutor, and the wisest creature in the world. King Midas caught him and forced him to share his wisdom.
- **Our version:** Silenus is half-beast himself, and men hunt satyrs too, so he hates Ixion with a passion. He appears only at dusk, usually drunk, and speaks in riddles. He gives you half the path through the Twilight Glade, and the rest you have to find yourself.
- Your armor hangs in the Forgotten Grove, guarded by the **Ker**, a death-spirit bound to Ixion. You can get past only cloaked and at night.
- **When you put the armor on:** you remember everything. The rumour, the ride north, the golden bridle, Ixion's face. You know where he is.
- **The pool:** look into the still water at night and, for the first time, you see yourself as you really are. Centaur Prime, in full war gear.

### The finale: Ixion

- With spear, shield and armor, the bridle on your mind is broken, and the way to Ixion's stronghold opens.
- **You fight Ixion and you kill him.** There's no spare-or-kill choice and no moral test. This is vengeance, and centaur pride restored by force. The fight follows the game's usual combat rule: with all three pieces you win, and without them you're driven back.
- **The twist: the Stables.** Under the stronghold you find dozens of captured centaurs, shod, bridled and chained, waiting their turn to be Unmade. You were never the last.
- You break their chains and lead them out into the open. **The Free Herds run again.**

### The title

*The Last Centaur* starts as Prime's grief: he believes he is the last of his kind. By the end it means **the last centaur who never knelt**, and the one the herd is reborn from.

### Myth sources

| Our story | The myth it comes from |
|---|---|
| Ixion, the Bridle-King | Ixion, Lapith king, father of the centaurs through Nephele (the cloud), bound to a burning wheel |
| King Pirithous, Ixion's ally | Pirithous, Lapith king and son of Ixion |
| The War of the Bridle | The Centauromachy, the war between the centaurs and the Lapiths that began at Pirithous's wedding |
| Melia, the ash dryad | The Meliae, ash-tree nymphs; Achilles' ash spear from Mount Pelion |
| Caeneus, the Lapith captain | Caeneus, the invulnerable Lapith who fought the centaurs and was buried under pine trunks |
| Silenus, the old satyr | Silenus, eldest satyr, tutor of Dionysus, captured by Midas for his wisdom |
| The Crystal Focus, cut by the Oreads | The Oreads, nymphs of the mountains |
| The Cloak of Nyx | Nyx, the primordial goddess of Night |
| The Ker, guardian of the grove | The Keres, death-spirits of violent death |
| Ixion's wheel sigil | The burning wheel Zeus bound Ixion to |
| *(Possible cameo)* Chiron | The wisest and most honourable centaur, teacher of heroes. He could be the Free Herds' founding legend, the one Prime's honour is measured against. |

### Still to decide

- **Prime's real name.** For now it's *Centaur Prime*. The name could come back at the pool, as the "I remember who I am" moment.
- **Pride counter.** It's still tracked (killing the kneeling guardian, killing the Ker), but nothing reads it yet. One option: it decides how many captives follow you out of the Stables.

## World laws

These are the rules the player learns. Each act introduces one, and they stay true everywhere.

| Law | How it shows up | Taught in |
|---|---|---|
| **Look closer.** Descriptions contain things you can examine. | `examine roots` in the starting woods finds the old map | Prologue |
| **Crystals sing near what's hidden.** | Near a hidden thing, tiles in highland/crystal areas mention ringing, louder as you get closer (hot/cold). | Act I |
| **Time matters.** Some things only work at certain hours. | The clock runs dawn, day, dusk, night as you take turns. `wait` skips ahead. | Act I |
| **Runes speak to those who remember.** | Once the spear brings your memory back, the Free Herds' runes become readable everywhere, including ones you passed earlier. | Act I → II |
| **The dead walk at dusk.** | Spirits, winds and Silenus appear at dusk. | Act II |
| **Shadows hide the hidden.** | With the Cloak of Nyx, at night, you can pass things that would otherwise see you. | Act III |

## The path

Fourteen beats across a prologue, three acts and a finale. For each beat: what the player sees, what they have to figure out, and where the clue is.

**The carvings.** The "in your hand" carvings stay, without the time loop. Prime cut them on his ride north to Ixion, as a soldier's habit: marks for whoever came after, and for himself if he didn't come back. Now, with no memory, you're following your own trail.

### Prologue: Awakening

**1. Waking** (Awakening Woods)
- You wake powerless, with no memory. The tile already has a carving: *Carved here, in your hand: "Ixion lives. I ride north to end it."* The name means nothing to you yet.
- Wolves circle. You can't fight them yet (no weapon), but they don't block you. They bite if you linger here at night.
- The description mentions roots and scratched bark. `examine roots` finds the **Old Map**, your own war map. This teaches the first law: look closer.

### Act I: The Spear (Melia)

**2. Melia** (Melia's Grove)
- A grove of ash trees. The dryad of the eldest ash steps out of its bark. She knows you: your spear's shaft was cut from her tree. *"You've come back. Not as you left."*
- Ixion's servants hid the spear. She gives one riddle: *"What you lost still sings in the high places. Listen for it at first light."*

**3. The singing stones** (highlands near the Mystic Mountains)
- Highland tiles mention crystals ringing, louder as you approach one specific ordinary tile. `search` or `examine` the ringing crystal there to find the **Crystal Focus**, a lens cut by the Oreads (mountain nymphs).
- Clue: Melia's riddle, plus the ringing itself.

**4. The sealed caves** (Crystal Caves)
- A shimmering wall blocks the entrance. Raise the Focus **while the sun is up** and the wall opens. At night the Focus is dark and cold. This teaches the time law.
- Clues: the Focus's lore, Melia's "first light", and a carving: *"Sunlight, not torchlight."*

**5. The spear** (inside the caves)
- A mural shows the War of the Bridle. The Free Herds charge under three banners: white at the front, amber behind, violet at the rear. At the head of the charge rides a centaur with an ash spear, and **the markings are yours**. Across from them, under a golden bridle, are the Bridled and their Lapith riders.
- Three crystals: amber, violet and white. `strike` them in the banners' order. A wrong order gives *"discord"*, and the sequence resets.
- The chord splits the floor and reveals **the Ash Spear**. Gripping it brings back the **first memory**: you're a warrior and a centaur, and you led the Free Herds. And the Free Herds' **runes** are words again.
- The runes beside the mural: *"The spear of the Prime. Sealed in stone by order of the Bridle-King, until the herds are no more."*

### Act II: The Shield (Caeneus)

**6. Caeneus** (the Lapith Camp)
- A man's camp, ringed by centaur battle standards taken as trophies. A broad Lapith in bronze, without a scar on him (Caeneus, whom no weapon could wound), turns his back: *"I know what you are."*
- With the runes back, you can `read` the standards: the names of your Honor Guard, one marked *"fell at the valley, guarding the way,"* and at the top a name that's been cut away. Then he talks: *"So you remember. I took those from the field. I couldn't leave them in the mud."* He tells you how to reach your old stronghold: *"Enter it as your herd did, the night it fell: from where the sun never reaches."*

**7. The stronghold** (the Ruined Stronghold)
- You can only enter from **the north**. From any other side: *"collapsed walls and rubble."*
- On a stone bier in the hall lies the **Horn of the Fallen**, the Honor Guard's horn. The bier's runes: *"A Prime's strength is in the stopping of his spear."* This is the clue for beat 10.

**8. The shield** (Warriors' Rest)
- A cairn over the graves of your Honor Guard. Its runes glow only while you carry the spear.
- Clue: a carving near the stronghold: *"The old spear wakes the old stones."*
- Beneath the glowing stones, wrapped in a Lapith soldier's red cloak, is **your Bronze Shield**. Caeneus carried it off the field and gave it back to your dead. Raising it brings back the **second memory**: the last battle. Everyone fell, on both sides, and you walked off the field alone.
- Back at the camp, Caeneus explains: *"A Lapith can't hang a centaur's shield in his tent. So I gave it to your dead."*

**9. The valley mouth** (Enchanted Valley)
- Spectral winds drive you back. Blow the horn at the valley mouth **at dusk**, when the dead walk, and the spirits part.
- Clues: the horn's description, the shapes in the dusk wind, and a carving: *"The dead walk at dusk."*

**10. The Bound Guardian** (Enchanted Valley)
- Ixion chained the spirits of your fallen Honor Guard to the valley, with a golden bridle across their faces. With spear and shield, you win, and the Guardian **kneels**.
- `spare` it: the bridle falls away, and a young centaur of your Honor Guard says *"Prime. You came back for us,"* and is freed. Or `kill` it. **Both** free the valley so you can't get stuck, but killing adds to your hidden **pride**.
- Caeneus reacts to which you chose, and points you to Silenus at the crossroads at dusk.

### Act III: The Armor (Silenus)

**11. Silenus** (the Crossroads)
- By day the crossroads is empty, apart from **cloven hoofprints that end mid-stride**.
- At dusk Silenus is there with a wineskin. Ixion gave your armor to a death-spirit to guard in the grove where the shadows move. You'll need the cloak in the glade, and he gives *half* the way: *"Twice toward the cold star…"*
- The other half is in your own carvings on two twilight tiles: *"…then once toward sunset, then the cold star one last time."*

**12. The Twilight Glade**
- Enter, and you're lost: every wrong step puts you back where you came in.
- Walk **north, north, west, north**. "Cold star" means north and "sunset" means west, and that compass language is consistent across every clue.
- Reward: the **Cloak of Nyx**, woven from Night herself.

**13. The armor** (the Forgotten Grove)
- The **Ker**, a death-spirit bound to Ixion, sees everything except someone **cloaked, at night**.
- Your **Bronze Armor** hangs from the largest tree. Taking it brings back the **third memory**: the rumour, the ride north, the golden bridle, Ixion's face.
- You can choose to `kill` the Ker while unseen (adds pride) or simply slip past.
- A still pool lies at the grove's heart. `look into pool` in the armor and you see yourself as you really are: **Centaur Prime**, in full war gear. The last of the bridle on your mind breaks.

### Finale (not built yet)

**14. Ixion's Hold**
- With the bridle broken, the way north to Ixion's Hold opens.
- You fight Ixion with spear, shield and armor, and **you kill him**.
- Beneath the Hold you find **the Stables**: captive centaurs, shod and chained, waiting to be Unmade. You break their chains and lead the Free Herds out.

## Map (fixed)

`y=0` is the south edge. Twelve landmarks are used. The Warriors' Armory and the Crystal Outpost are cut for now; they could come back later as optional secrets.

```
9  .  .  .  .  .  D  .  .  .  .     D  Ixion's Hold         (5,9)
8  .  .  .  .  .  .  .  .  .  .
7  .  .  C  .  .  F  .  .  V  .     C  Crystal Caves        (2,7)
6  .  h  .  .  .  .  R  .  .  .     F  Forgotten Grove      (5,7)
5  .  .  .  .  G  .  .  .  .  .     V  Enchanted Valley     (8,7)
4  .  M  .  .  .  .  .  .  A  .     h  hidden Focus tile    (1,6)
3  .  .  .  .  .  X  .  .  .  .     R  Warriors' Rest       (6,6)
2  .  .  .  .  .  .  .  .  .  .     G  Twilight Glade       (4,5)
1  .  .  H  .  .  .  .  .  W  .     M  Mystic Mountains     (1,4)
0  .  .  .  .  .  S  .  .  .  .     A  Ruined Stronghold    (8,4)  enter from (8,5)
   0  1  2  3  4  5  6  7  8  9     X  Crossroads           (5,3)
                                    H  Melia's Grove        (2,1)
                                    W  Lapith Camp          (8,1)
                                    S  Awakening Woods      (5,0)
```

The **ordinary tiles** keep their generated names and descriptions from a **fixed seed**, so they're the same for every player. They can be replaced with handwritten ones later.

## Engine changes this needs

| Mechanic | What it is |
|---|---|
| **Clock** | Each turn advances time through dawn, day, dusk and night (about 6 turns each). `wait` skips to the next phase. Descriptions reflect the time. |
| **Features** | Nouns in a tile that you can examine or use, e.g. roots, cairn, mural, pool. They can hide things or react. |
| **Interactions** | The core rule: *verb + (item) + place/feature + (time) + (needs)* → *effects*. Effects can reveal an item, open a landmark, set a flag, grant an ability, add to pride, write a memory or show a message. |
| **Abilities** | Reading runes, regained with the spear. It changes what you can see and do. |
| **Signals** | Hot/cold cues computed from distance to a hidden target (the singing crystals, the glowing runes). |
| **Approach gates** | A landmark that can only be entered from a given direction (the ruins). |
| **Lost woods** | A landmark that requires a move sequence once you're inside (the Glade). |
| **Echoes** | Pre-written "in your hand" memories, placed on tiles when the world is built. |
| **Pride** | A hidden counter. Nothing reads it yet. |
| **Finale** | The fight with Ixion and the Stables. |

`content.py` drops the three-path tables. Paths are replaced by features, interactions, echoes, memories and the finale. Everything stays data, and the engine stays generic.

## Fairness: the solver's new job

Every gated interaction lists the clues that point to it. The solver explores the game state (position, inventory, flags, abilities, time of day, clues seen) and only allows an interaction once at least one of its clues has been seen. If the game can be won under that rule, every puzzle can be worked out from things the player has actually encountered. The tests enforce this, so adding a puzzle without a clue fails the build.

## The LLM narrator's rules

- **The engine is the referee.** The LLM turns free text into one engine command, or says it doesn't understand. It never decides outcomes.
- **It never reveals anything.** It only rewrites facts the engine returned. It may not mention items, places or solutions the engine didn't. It never hints.
- **Experimenting gets acknowledged.** "I hum back at the crystals" gets a real in-world response even when nothing happens, so the world feels responsive instead of like a parser saying no.
- **Descriptions stick.** The first time you visit a tile, its richer description is saved in that tile's memory, so the place never changes on a second look.
- Classic commands skip the LLM entirely.

## Build order

1. ~~**Mechanics plus the Prologue and Act I**, playable: clock, features, interactions, signals, echoes, abilities. Walkthrough and fairness tests.~~ Done.
2. ~~**Act II and Act III**: approach gates, lost woods, pride.~~ Done.
3. ~~**Re-skin to the Greek-myth story**: Melia, Caeneus, Silenus; spear, shield, armor.~~ Done.
4. **Finale**: Ixion's Hold, the fight, the Stables.
5. **LLM narrator.**
6. ~~**Delete the old `src/` tree**, the three-path content and the old tests.~~ Done.

## Settled questions

- **Story:** the Greek-myth revenge story in *The story* replaces the time loop.
- **Ending:** one. Kill Ixion, free the Stables.
- **Wolves:** bite at night.
- **Spare/kill:** only some encounters (the Bound Guardian, the Ker). Never Ixion.
