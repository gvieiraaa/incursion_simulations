# incursion simulations for path of exile

Simulating incursion results based on several parameters 

This is a repository for the code used and resulting .csv files.

--- 

I was curious to find out the best tactics when doing Alva incursions, and since the atlas passives were implemented I don't think I've seen a simulation shown here.

I wanted to test more than the simulations I've seen years ago, that only simulate based on the locus. Also the atlas passives change a lot too.

So I wrote a program that simulates 1 million temples in each possible arrangement of those parameters:

- Using the Atlas point to have 4 incursions in a map or not
- If you should skip the next incursions right after a locus room
- If you should skip the next incursions right after a doryani room
- If you should skip the next incursions right after a nexus room
- If you should skip the last incursion of the map if it's not one of the good ones and it's a level 0 room
- If you should switch (kill the left side one) if the locus option was not seen yet, if the room is level 0.

Those are the results: https://docs.google.com/spreadsheets/d/18FT3oMk2Bwxd-g3JkKeRPosQBaLaRU11uwGAK9WymrE/edit?usp=sharing

That's the python script that was used, and the raw data it generated: https://github.com/gvieiraaa/incursion_simulations

# TLDR (I'll leave more information at the end if you want to know): 

Always pick those 4 atlas points: Contested development, Resource Reallocation, Artefacts of the vaal, Incursion Upgrade Chance (small)

---

### If your focus is pure profit from selling the temples: (based on current prices, make a copy and you can change them in the spreadsheet)

- Don't ever skip an incursion.
- Upgrade/switch to locus when you see one.
- If you find a nexus connected to a locus, upgrade/switch to it.
- If it's not a good room, upgrade if the room is level 1 or more, or switch if it's level 0

---

### If your focus is to have higher chances of getting a locus in the current temple: 

- Upgrade/switch to locus when you see one and then skip the next incursions in the map.
- If you find a nexus connected to a locus, upgrade/switch to it and then skip the next incursions in the map.
- If it's not a good room, upgrade if the room is level 1 or more, or switch if it's level 0

---

### If your focus is to have the best efficiency of locus / map:

- Do the same as the "focus on profit" part

---

I just want to note that I'm using "locus", "doryani" and "nexus" as the type of the rooms, not necessarily it being level 3

# End of the TLDR

--- 

Those assumptions were made:

- All rooms are connected
- You never fail a room
- Each room has a 50/50 chance of starting at level 1
- The two options are populated when the temple is created
- T3 rooms are not offered again, and also the second "boss" in that room is locked with it.
- You can never get the same room twice in the same map
- When you talk to alva at the start of the map, it DOES NOT lock all the next 2 (or 3) encounters, this was tested.
- The decision tree is heavily dependant on the variables mentioned before, but some are fixed:
- 1) If you see a locus, upgrade or switch to it.
- 2) if you find a nexus and there's a locus connected, switch to it or upgrade it

Columns in the spreadsheet (also explained while hovering each):

**incursions_per_map**: 3 or 4 incursions per map

**skip_after_locus**: if you should skip next incursions in a map if you find a locus

**skip_after_doryani**: same as above but for doryani

**skip_after_nexus**: same as above but for nexus

**skip_last_if_0**: If you should skip the last incursion of the map if it's not one of the good ones and it's a level 0 room

**switch_if_lvl0**: That's the last decision, it has no priority over the others. If the locus option was not seen yet, switch (kill the left side one) if the room is level 0.

The "Mechanics" options differ on how the next room is decided. 

The option "1" doesn't allow you to find the same room in the last incursion of a map and in the first of the next one. The option "2" does.

I've decided to do both because it's not clear which one is the one used in the game. The other theories I debunked myself by testing.

I can think of a few extra conditions but they would barely change anything, and it already takes hours to run this one (partially my fault, I could have optimized some stuff in the code and/or use multiprocessing, but I'm not really a programmer, so good enough I guess).

I'm pretty sure all the logic is correct, I've checked it multiple times, but please do point out if you find an error.
