# The Last Centaur — Game Design

> Status: **agreed, building.** This replaces the three-path design in `DESIGN.md`.

## Decisions so far

| | |
|---|---|
| Structure | **One long path** that weaves all three disciplines (insight, valor, shadow) into a single game |
| Feel | **Opaque, Myst-like.** No goals stated, no quest log. Everything you need is in the world. |
| Map | **Fixed, hand-placed.** Every player gets the same world. |
| Input | Classic commands (`look`, `n`, `take`, …) always work directly. The LLM handles everything else. |
| Combat | Stays as is: win if you have what it takes, get driven back if not |
| Hints | **Soft.** The world reacts when you're close. There's no hint command. |
| Endings | All endings are valid. The hardest, trickiest one is the true one: you become **The Last Centaur**. |
| Choices | Only some encounters offer spare/kill (Valor ward, Phantom Assassin, finale). |
| Danger | Wolves bite at night in the Awakening Woods. |

## Design pillars

1. **Fair opacity.** The game never tells you what to do, but every solution can be worked out from things you can find *before* you need them. The solver proves this mechanically (see *Fairness*).
2. **Do, don't just carry.** Items are tools, not keys. Holding the Focus opens nothing; holding it up to sunlight in the right place does.
3. **Learn a rule, use it everywhere.** The world has a few consistent laws. Learning them is the real progression.
4. **The world remembers.** Tiles keep a memory of what happened there. Some memories were there before you arrived.
5. **Free choices have consequences.** You won't get softlocked, but how you solve things shapes the ending.

## The story (proposal)

What the player slowly pieces together. None of this is ever stated outright.

- You are Centaur Prime. You started the **War of Seven Herds**. Your pride nearly wiped out your people.
- The three mentors (the Hermit Druid, the Fallen Warrior and the Shadow Scout) survived the war. Together they raised **the barrier**. It split you in two: your body woke powerless in the woods, and your **power and pride** took shape as the **Shadow Centaur** on the throne.
- The barrier is held by **three wards**: Insight, Valor and Shadow. Each mentor guards one, and each ward is a **test of whether you've changed**.
- **This has happened before.** You've done all this already and ended up back here. Your past self scratched notes into the world for you, in your own hand. (They appear as tile memories: *"Carved here, in your hand: …"*.)
- The question the Hermit asks in their first line ("Will you learn from our past, or repeat it?") is the question the ending answers.

## World laws

These are the rules the player learns. Each act introduces one, and they stay true everywhere.

| Law | How it shows up | Taught in |
|---|---|---|
| **Look closer.** Descriptions contain things you can examine. | `examine roots` in the starting woods finds the old map | Prologue |
| **Crystals sing near what's hidden.** | Near a hidden thing, tiles in highland/crystal areas mention ringing, louder as you get closer (hot/cold). | Act I |
| **Time matters.** Some things only work at certain hours. | The clock runs dawn, day, dusk, night as you take turns. `wait` skips ahead. | Act I |
| **Runes speak to those who remember.** | After the Insight ward breaks, carved runes become readable everywhere, including ones you passed earlier. | Act I → II |
| **The dead walk at dusk.** | Spirits, winds and the Scout appear at dusk. | Act II |
| **Shadows hide the hidden.** | With the cloak, at night, you can pass things that would otherwise see you. | Act III |

## The path

Fourteen beats across a prologue, three acts and a finale. For each beat: what the player sees, what they have to figure out, and where the clue is.

### Prologue: Awakening

**1. Waking** (Awakening Woods)
- You wake powerless. The tile already has a memory: *Carved here, in your hand: "If you're reading this, it happened again. Don't trust the crown."*
- Wolves circle. You can't fight them yet (no weapon), but they don't block you. *(Optional: they bite if you linger here at night, which gives a first reason to care about time.)*
- The description mentions roots and scratched bark. `examine roots` finds the **Old Map**. This teaches the first law: look closer.

### Act I: Insight (the Hermit)

**2. The Hermit** (Hermit's Grove)
- The Hermit doesn't hand you anything. They recognise you, which is unsettling: *"You've come back. Again."*
- They give one riddle: *"What you lost still sings in the high places. Follow the song at first light."*

**3. The singing stones** (highlands near the Mystic Mountains)
- Highland tiles mention crystals ringing, louder as you approach one specific ordinary tile. It is not the landmark itself. This teaches the second law.
- `search` or `examine` the ringing crystal there to find the **Crystal Focus**.
- Clue: the Hermit's riddle, plus the ringing itself.

**4. The sealed caves** (Crystal Caves)
- A shimmering wall blocks the entrance.
- Raise or look through the Focus **while the sun is up** and the wall's pattern resolves, so the wall opens. At night: *"The Focus is dark and cold in your hand."* This teaches the time law.
- Clues: the Focus's own lore (*"held up to sunlight in places of power, it reveals hidden paths"*) and the Hermit's "first light".

**5. The Insight ward** (inside the caves)
- A mural shows the War of Seven Herds. At its centre is a crowned centaur with **your markings**. This is the first story reveal.
- Three crystals: amber, violet and white. `strike` them in the order the mural's banners show. A wrong order gives *"discord rings through the cave"*, and the sequence resets.
- Reward: the **Insight** ward breaks and you can now read runes.

### Act II: Valor (the Fallen Warrior)

**6. The Fallen Warrior** (Warrior's Camp)
- Before Insight, they turn away: *"I know what you are."*
- After Insight, you can `read` the runes on their battle standard: the names of the Honor Guard, one marked *"fell at the valley, guarding the way."* Then they'll talk: *"So you remember. Enter the ruins as we did: from where the sun never reaches."*

**7. The ruins** (Ancient Ruins)
- You can only enter from **the north** ("where the sun never reaches"). From any other side: *"collapsed walls and rubble."*
- Inside is the **Ancient Sword**. Its runes, now readable, say: *"Valor is the strength to stop."* This is the clue for beat 10.

**8. The horn** (Warriors' Rest)
- A cairn of stones. Its runes glow only while you carry the First War sword. Examine the glowing cairn to find the **Horn of the Fallen**.
- Clue: one of your past self's carvings near the ruins: *"The old steel wakes the old stones."*

**9. The valley mouth** (Enchanted Valley)
- Spectral winds drive you back.
- Blow the horn at the valley mouth **at dusk**, when the dead walk. The spirits answer and part.
- Clues: the horn's description, and the dusk law (learned from the winds being strongest then).

**10. The Valor ward** (Enchanted Valley)
- The Shadow Guardian, bound spirit of the fallen Honor Guard. With the sword, you win. It **kneels**.
- Now `spare` it or `kill` it. **Both** break the ward, so you can't get stuck. Sparing is the "right" answer (*"Valor is the strength to stop"*), and killing adds to your hidden **pride**.
- Reward: the **Valor** ward breaks.

### Act III: Shadow (the Scout)

**11. The Scout** (Crossroads of Trials)
- By day the crossroads is empty, apart from **footprints that end mid-stride**.
- At dusk the Scout is there. They give *half* the way through the twilight: *"Twice toward the cold star…"*
- The other half is in your old carvings on two twilight tiles: *"…then toward sunset, then the cold star once more."*

**12. The Twilight Glade**
- Enter, and you're lost: every wrong step puts you back where you came in.
- Walk the sequence: **north, north, west, north**. "Cold star" means north and "sunset" means west; that compass language is consistent across every clue.
- Reward: the **Cloak of Shadows**.

**13. The Shadow ward** (Forgotten Grove)
- The Phantom Assassin sees everything, except someone **cloaked, at night**.
- Slip past and take **Phantom's Edge**, a blade that cuts wards.
- You can choose to `kill` the Phantom Assassin while unseen (an assassination, which adds pride) or simply slip past.
- A still pool sits at the grove's heart. `look into pool` at night and your reflection is the **Shadow Centaur's face**. Looking is the test: seeing what you are.
- Reward: the **Shadow** ward breaks.

### Finale

**14. The Shadow Domain**
- With all three wards broken, the barrier falls and the Domain opens.
- The Shadow Centaur is your power and pride. You can beat it, but the real choice comes after. **Proposed endings:**

| Ending | How | Meaning |
|---|---|---|
| **Repeat** | Take the crown | You're whole and proud again. *"You wake on cold earth…"* The game begins again. |
| **Break** | Shatter the crown | The cycle ends. You stay diminished but free. |
| **Mend** | Spare the shadow and take it back without the crown (only if pride is low) | The hidden best ending. |

*Stretch idea:* in the **Repeat** ending, your own `carve` messages from this playthrough appear in the next one as "in your hand" memories. The loop becomes literal.

## Map (fixed)

`y=0` is the south edge. Twelve landmarks are used. The Warriors' Armory and the Crystal Outpost are cut for now; they could come back later as optional secrets.

```
9  .  .  .  .  .  D  .  .  .  .     D  Shadow Domain        (5,9)
8  .  .  .  .  .  .  .  .  .  .
7  .  .  C  .  .  F  .  .  V  .     C  Crystal Caves        (2,7)
6  .  h  .  .  .  .  R  .  .  .     F  Forgotten Grove      (5,7)
5  .  .  .  .  G  .  .  .  .  .     V  Enchanted Valley     (8,7)
4  .  M  .  .  .  .  .  .  A  .     h  hidden Focus tile    (1,6)
3  .  .  .  .  .  X  .  .  .  .     R  Warriors' Rest       (6,6)
2  .  .  .  .  .  .  .  .  .  .     G  Twilight Glade       (4,5)
1  .  .  H  .  .  .  .  .  W  .     M  Mystic Mountains     (1,4)
0  .  .  .  .  .  S  .  .  .  .     A  Ancient Ruins        (8,4)  enter from (8,5)
   0  1  2  3  4  5  6  7  8  9     X  Crossroads           (5,3)
                                    H  Hermit's Grove       (2,1)
                                    W  Warrior's Camp       (8,1)
                                    S  Awakening Woods      (5,0)
```

The **ordinary tiles** keep their generated names and descriptions from a **fixed seed**, so they're the same for every player. They can be replaced with handwritten ones later.

## Engine changes this needs

| Mechanic | What it is |
|---|---|
| **Clock** | Each turn advances time through dawn, day, dusk and night (about 6 turns each). `wait` skips to the next phase. Descriptions reflect the time. |
| **Features** | Nouns in a tile that you can examine or use, e.g. roots, cairn, mural, pool. They can hide things or react. |
| **Interactions** | The core rule: *verb + (item) + place/feature + (time) + (needs)* → *effects*. Effects can reveal an item, open a landmark, set a flag, grant an ability, add to pride, write a memory or show a message. |
| **Abilities** | Insight (read runes), Valor and Shadow, regained from the wards. They change what you can see and do. |
| **Signals** | Hot/cold cues computed from distance to a hidden target (the singing crystals, the glowing runes). |
| **Approach gates** | A landmark that can only be entered from a given direction (the ruins). |
| **Lost woods** | A landmark that requires a move sequence once you're inside (the Glade). |
| **Echoes** | Pre-written "in your hand" memories, placed on tiles when the world is built. |
| **Pride** | A hidden counter that affects the ending. |
| **Endings** | Final choices at the throne. |

`content.py` drops the three-path tables. Paths are replaced by features, interactions, echoes, wards and endings. Everything stays data, and the engine stays generic.

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
2. **Act II and Act III**: approach gates, lost woods, pride. *Act II done.*
3. **Finale and endings.**
4. **LLM narrator.**
5. ~~**Delete the old `src/` tree**, the three-path content and the old tests.~~ Done.

## Settled questions

- **Story twist:** accepted.
- **Endings:** all valid; *The Last Centaur* is the hardest, true ending.
- **Wolves:** bite at night.
- **Spare/kill:** only some encounters (Valor ward, Phantom Assassin, finale).
