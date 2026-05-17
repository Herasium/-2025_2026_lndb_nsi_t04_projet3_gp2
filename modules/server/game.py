from modules.logger import Logger
import random
import json
import asyncio
import time

logger = Logger("Game")

class Game:

    def __init__(self):
        self.status = 0
        self.players = {}
        self.min_player_count = 3
        self.waiting_room = []
        self.playing_room = []
        self.death_room = []
        self.roles = ["villager", "werewolf","black_wolf","pyromane","moon_fighter","mark_garyson","crazy_dave"]
        self.pending_responses = {}
        self.phase_name = "waiting"         
        self.phase_start_time = None
        self.phase_duration = 0

    def set_game_flags(self):
        self.black_wolf_eaten = False
        self.moon_fighter_skiped = False
        self.pyromane_bombed = []
        self.crazy_dave_up = False
        self.witch_save_used = False
        self.witch_genocide_used = False
        self.death_eater_used = False

    async def send_all_players(self, opcode, data):
        logger.debug(f"Broadcasting '{opcode}' to playing room.")
        for id in list(self.playing_room):
            await self.send_player(id, opcode, data)

    async def send_all_players_waiting(self, opcode, data):
        logger.debug(f"Broadcasting '{opcode}' to waiting room.")
        for id in list(self.waiting_room):
            await self.send_player(id, opcode, data)

    async def send_all_players_dead(self, opcode, data):
        logger.debug(f"Broadcasting '{opcode}' to death room.")
        for id in list(self.death_room):
            await self.send_player(id, opcode, data)

    async def send_list_players(self, players, opcode, data):
        for id in players:
            await self.send_player(id, opcode, data)

    async def send_player(self, player_id, opcode, data):
        player = self.players.get(player_id)
        if not player:
            logger.warning(f"Cannot send '{opcode}', player {player_id} not found (likely disconnected).")
            return
            
        if not getattr(player, 'conn', None):
            logger.warning(f"Cannot send '{opcode}', player {player_id} has no active connection.")
            return

        try:
            await player.conn.send(json.dumps({"opcode": opcode, "data": data}))
        except Exception as e:
            logger.error(f"Failed to send data to player {player_id}: {e}")

    async def wait_for_players_responses(self, players_list, opcode, timeout):
        responses = {}
        logger.info(f"Waiting for responses on '{opcode}' from {len(players_list)} players (Timeout: {timeout}s).")
        
        async def wait_for_one(pid):
            loop = asyncio.get_running_loop()
            fut = loop.create_future()
            
            if pid not in self.pending_responses:
                self.pending_responses[pid] = {}
            self.pending_responses[pid][opcode] = fut
            
            try:
                return await asyncio.wait_for(fut, timeout=timeout)
            except asyncio.TimeoutError:
                logger.warning(f"Player {pid} timed out while waiting for '{opcode}'.")
                return None
            finally:
                if pid in self.pending_responses:
                    self.pending_responses[pid].pop(opcode, None)

        # Only wait for players that are still in the game
        active_players = [pid for pid in players_list if pid in self.players]
        tasks = {pid: asyncio.create_task(wait_for_one(pid)) for pid in active_players}
        
        if tasks:
            results = await asyncio.gather(*tasks.values())
            for pid, result in zip(tasks.keys(), results):
                responses[pid] = result
        
        logger.debug(f"Collected {len([r for r in responses.values() if r is not None])} valid responses for '{opcode}'.")
        return responses
    
    def transfer_to_player_room(self):
        logger.info(f"Transferring {len(self.waiting_room)} players to the playing room.")
        self.playing_room = self.waiting_room.copy()
        self.waiting_room = []

    def transfer_to_waiting_room(self):
        logger.info("Transferring all players back to the waiting room.")
        self.waiting_room = self.playing_room.copy() + self.waiting_room + self.death_room.copy()
        self.playing_room = []
        self.death_room = []

    def transfer_to_death_room(self, player):
        if player in self.playing_room:
            self.playing_room = [p for p in self.playing_room if p != player]
            if player not in self.death_room:
                self.death_room.append(player)
            logger.info(f"Player {player} moved to the death room.")
        else:
            logger.warning(f"Attempted to move player {player} to death room, but they are not in the playing room.")
    
    def transfer_to_living_room(self, player):
        if player in self.death_room:
            self.death_room = [p for p in self.death_room if p != player]
            if player not in self.playing_room:
                self.playing_room.append(player)
            logger.info(f"Player {player} moved to the playing room.")
        else:
            logger.warning(f"Attempted to move player {player} to playing room, but they are not in the death room.")
    

    async def new_player(self, player_id):
        # Assumes player_id has already been added to self.players and self.waiting_room by the caller.
        logger.info(f"New player {player_id} joined the waiting room.")
        players = []
        for id in list(self.waiting_room):
            if id in self.players:
                players.append({"id": id, "name": self.players[id].name})
            else:
                logger.warning(f"Player {id} is in waiting room but missing from players dictionary.")

        await self.send_all_players_waiting("waiting_room_list_update", {"players": players, "status": self.status})

    def get_roles(self):
        logger.debug("Assigning roles to players using balanced distribution.")
        
        player_ids = [pid for pid in self.playing_room if pid in self.players]
        num_players = len(player_ids)
        
        # Calculate number of werewolves (approx 1 for every 4 players, minimum 1)
        num_werewolves = max(1, num_players // 4)
        if num_players >= 6 and num_werewolves < 2:
            num_werewolves = 2
            
        # Get all special roles (everything except villager and generic werewolf)
        special_roles = [role for role in self.roles if role not in ("villager", "werewolf")]
        
        # Determine how many special roles can be included
        max_specials = num_players - num_werewolves
        if max_specials < 0:
            max_specials = 0
        # Randomly select a subset of special roles if we cannot include all
        selected_specials = random.sample(special_roles, min(len(special_roles), max_specials))
        
        # Build the role pool
        pool = (["werewolf"] * num_werewolves) + selected_specials + (["villager"] * (num_players - num_werewolves - len(selected_specials)))
        random.shuffle(pool)
        
        result = {}
        per_roles = {}

        for i, player_id in enumerate(player_ids):
            assigned_role = pool[i]
            result[player_id] = assigned_role

            if assigned_role not in per_roles:
                per_roles[assigned_role] = []
            per_roles[assigned_role].append(player_id)

        logger.info(f"Balanced roles assigned: { {role: len(p) for role, p in per_roles.items()} }")
        return result, per_roles

    def get_players_by_role(self, role, exclude_to_kill=True):
        players = []
        for id in self.players_per_roles.get(role, []):
            if id in self.players and id in self.playing_room:
                if getattr(self.players[id], 'role', None) == role:
                    if not exclude_to_kill or id not in self.to_kill:
                        players.append(id)
        return players

    def get_vote_result(self, responses):
        results = {}
        current = None
        current_count = 0

        for i in responses:
            if responses[i] is not None:
                vote_target = responses[i].get("vote")
                if vote_target is not None:
                    results[vote_target] = results.get(vote_target, 0) + 1

                    if results[vote_target] > current_count:
                        current = vote_target
                        current_count = results[vote_target]

        logger.debug(f"Vote results tallied: {results}. Winner: {current} with {current_count} votes.")
        return current, current_count

    async def run_black_wolf(self, id):
        black_wolfs = self.get_players_by_role("black_wolf")

        if len(black_wolfs) < 1:
            logger.warning("No black_wolf found during black_wolf phase. Skipping.")
            return    
        
        if self.black_wolf_eaten:
            return

        # Fixed: added missing data dict
        await self.send_list_players(black_wolfs, "night_black_wolfs_start", {})

        if id in self.players:
            info = {"id": id, "name": self.players[id].name}
            await self.send_list_players(black_wolfs, "night_black_wolf_vote", {"villager": info})

            responses = await self.wait_for_players_responses(
                black_wolfs, 
                "night_black_wolf_vote_response", 
                45
            )

            current, _ = self.get_vote_result(responses)
            await self.send_list_players(black_wolfs, "night_black_wolf_end", {})

            if current == id:
                # Remove the target from kill list (the black wolf "eats" him instead)
                try:
                    self.to_kill.remove(id)
                except ValueError:
                    pass  # id wasn't in the list (should not happen, but be safe)
                
                if id in self.players:
                    old_role = self.players[id].role
                    if old_role in self.players_per_roles:
                        try:
                            self.players_per_roles[old_role].remove(id)
                        except ValueError:
                            pass
                    self.players[id].role = "werewolf"
                    if "werewolf" not in self.players_per_roles:
                        self.players_per_roles["werewolf"] = []
                    self.players_per_roles["werewolf"].append(id)
                    await self.send_player(id, "role_change", {"new_role": "werewolf"})
                    self.black_wolf_eaten = True

    async def run_fortune_teller(self):
        fortune_tellers = self.get_players_by_role("fortune_teller")

        if len(fortune_tellers) < 1:
            logger.warning("No werewolves found during fortune telling phase. Skipping.")
            return

        await self.send_list_players(fortune_tellers, "night_fortune_teller_start", {})

        villagers = []

        for id in list(self.playing_room):
            if id in self.players:
                villagers.append({"id": id, "name": self.players[id].name})

        await asyncio.sleep(3)

        logger.debug("Asking fortune_tellers to vote.")
        await self.send_list_players(fortune_tellers, "night_fortune_teller_vote", {"villagers": villagers})

        responses = await self.wait_for_players_responses(
            fortune_tellers, 
            "night_fortune_teller_vote_response", 
            45
        )

        current, _ = self.get_vote_result(responses)

        role = getattr(self.players[current], 'role', "unknown")
        name = getattr(self.players[current], 'name', "???")

        await self.send_list_players(fortune_tellers,"night_fortune_teller_result", {"name":name,"role":role}) 
        await asyncio.sleep(5)
        await self.send_list_players(fortune_tellers,"night_fortune_teller_end",{})

    async def run_werewolf(self):
        logger.info("Starting Werewolf phase.")
        villagers = []
        werewolfs = self.get_players_by_role("werewolf") + self.get_players_by_role("black_wolf")

        if len(werewolfs) < 1:
            logger.warning("No werewolves found during werewolf phase. Skipping.")
            return

        await self.send_list_players(werewolfs, "night_werewolf_start", {})

        for id in list(self.playing_room):
            if id in self.players and getattr(self.players[id], 'role', None) != "werewolf":
                villagers.append({"id": id, "name": self.players[id].name})

        await asyncio.sleep(3)

        logger.debug("Asking werewolves to vote.")
        await self.send_list_players(werewolfs, "night_werewolf_vote", {"villagers": villagers})

        responses = await self.wait_for_players_responses(
            werewolfs, 
            "night_werewolf_vote_response", 
            45
        )

        current, _ = self.get_vote_result(responses)

        await self.send_list_players(werewolfs, "night_werewolf_end", {})

        if current is not None:
            logger.info(f"Werewolves voted to kill: {current}")
            self.to_kill.append(current)
            await self.run_black_wolf(current)
        else:
            logger.info("Werewolves did not agree on a target.")

    async def kill_players(self, players):
        killed = []
        # Remove duplicates
        unique_players = list(set(players))

        for id in unique_players:
            if id in self.players:
                if getattr(self.players[id], 'role', 'unknown') == "mark_garyson":
                    logger.info("MARK GARYSON ABILITY TRIGGERED")
                    await self.run_mark_garyson()

                logger.info(f"Killing player {id} ({self.players[id].name}).")
                killed.append({"id": id, "name": self.players[id].name, "role": getattr(self.players[id], 'role', 'unknown')})
                await self.send_player(id, "killed", {})
                self.transfer_to_death_room(id)
            else:
                logger.warning(f"Tried to kill player {id}, but they are no longer in the game.")

        if killed:
            await self.send_all_players("day_death", {"death": killed})

    async def run_mark_garyson(self):
        # When mark_garyson dies, he can take someone with him.
        # We need to include players that are in to_kill because the mark_garyson himself is about to die.
        mark_garyson = self.get_players_by_role("mark_garyson", exclude_to_kill=False)

        if len(mark_garyson) < 1:
            logger.error("No mark garyson found (or already dead).")
            return
        
        await self.send_all_players("mark_garyon_died", {})

        villagers = []
        for id in list(self.playing_room):
            if id in self.players and id not in self.to_kill:
                villagers.append({"id": id, "name": self.players[id].name})

        await self.send_list_players(mark_garyson, "mark_garyon_vote", {"villagers": villagers})

        responses = await self.wait_for_players_responses(
            mark_garyson, 
            "mark_garyon_response", 
            45
        )

        current, _ = self.get_vote_result(responses)
        if current is not None:
            # Fixed: must await the kill
            await self.kill_players([current])

    async def run_pyromane(self):
        pyromanes = self.get_players_by_role("pyromane")

        if len(pyromanes) < 1:
            logger.warning("No pyromane found during pyromane phase. Skipping.")
            return    

        # Fixed: added missing data dict
        await self.send_list_players(pyromanes, "night_pyromane_start", {})

        villagers = []
        for id in list(self.playing_room):
            if id in self.players:
                villagers.append({"id": id, "name": self.players[id].name})

        await asyncio.sleep(3)

        await self.send_list_players(pyromanes, "night_pyromane_vote", {"villagers": villagers})

        responses = await self.wait_for_players_responses(
            pyromanes, 
            "night_pyromane_response", 
            45
        )

        current, _ = self.get_vote_result(responses)

        if current == -1:
            await self.send_all_players("pyromane_explosion", {})
            self.to_kill.extend(self.pyromane_bombed)
            # Remove duplicates
            self.to_kill = list(set(self.to_kill))
            self.pyromane_bombed = []
            await asyncio.sleep(3)

        elif current is not None:
            self.pyromane_bombed.append(current)

        await self.send_list_players(pyromanes, "night_pyromane_end", {})

    async def moon_fighter(self):
        moon_fighters = self.get_players_by_role("moon_fighter")

        if len(moon_fighters) < 1 or self.moon_fighter_skiped:
            logger.warning("No moon_fighter found or already used. Skipping.")
            # Fixed: await the sleep
            await asyncio.sleep(1)
            return 0
        
        await self.send_list_players(moon_fighters, "night_moon_fighter_vote", {})

        responses = await self.wait_for_players_responses(
            moon_fighters, 
            "night_moon_fighter_response", 
            5
        )

        current, _ = self.get_vote_result(responses)
        if current == 1:
            self.moon_fighter_skiped = True
        return current

    async def run_night(self):
        self.phase_name = "night"
        self.phase_start_time = time.time()
        self.phase_duration = 55
        logger.info(f"--- Night {self.current_day} Starting ---")
        self.to_kill = []
        await self.send_all_players("switch_night", {"current_night": self.current_day})
        skip = await self.moon_fighter()
        if skip:
            return
        await self.run_fortune_teller()
        skip = await self.moon_fighter()
        if skip:
            return
        await self.run_werewolf()
        skip = await self.moon_fighter()
        if skip:
            return
        await self.run_pyromane()
        skip = await self.moon_fighter()
        if skip:
            return
        await self.run_death_eater()


    async def run_day(self):
        self.phase_name = "day"
        self.phase_start_time = time.time()
        self.phase_duration = 65 
        self.current_day += 1
        logger.info(f"--- Day {self.current_day} Starting ---")
        await self.send_all_players("switch_day", {"current_day": self.current_day})

        if self.to_kill:
            await self.kill_players(self.to_kill)    

        await asyncio.sleep(10)

        villagers = []
        for id in list(self.playing_room):
            if id in self.players:
                villagers.append({"id": id, "name": self.players[id].name})

        logger.debug("Initiating day vote.")
        await self.send_all_players("day_vote", {"villagers": villagers})

        responses = await self.wait_for_players_responses(
            list(self.playing_room), 
            "day_vote_response", 
            45
        )

        current, vote_count = self.get_vote_result(responses)
        logger.info(f"Day vote concluded. Target: {current} (Votes: {vote_count})")
        
        await asyncio.sleep(5)
        if current is not None:
            await self.kill_players([current])
            
        logger.debug(f"Alive room: {self.playing_room} | Dead room: {self.death_room}")
        await self.crazy_dave_vote()
        await asyncio.sleep(5)

    async def check_win(self):
        werewolfs = self.get_players_by_role("werewolf") + self.get_players_by_role("black_wolf")
        logger.debug(f"Win Check - Werewolves remaining: {len(werewolfs)}")
        
        if len(werewolfs) < 1:
            logger.success("Villagers Victory detected.")
            await self.send_all_players("game_end", {"winner": "villager"})
            self.finished = True
            return

        villagers = (self.get_players_by_role("villager") + 
                     self.get_players_by_role("mark_garyson") + 
                     self.get_players_by_role("moon_fighter") + 
                     self.get_players_by_role("pyromane"))
        logger.debug(f"Win Check - Villagers remaining: {len(villagers)}")
        
        if len(villagers) < 1:
            logger.success("Werewolf Victory detected.")
            await self.send_all_players("game_end", {"winner": "werewolf"})
            self.finished = True

    async def run_witch(self):
        logger.info("Starting Witch phase.")
        witches = self.get_players_by_role("witch")

        if len(witches) < 1:
            logger.warning("No witches found during witch phase. Skipping.")
            return

        await self.send_list_players(witches, "night_witch_start", {})

        await asyncio.sleep(3)

        victim = None
        name = None
        if len(self.to_kill) > 0:
            victim = random.choice(self.to_kill)
            name = getattr(self.players[victim],"name",None)


        logger.debug("Asking witches to vote.")
        await self.send_list_players(witches, "night_witches_vote", {"id": victim,"name":name,"save":self.witch_save_used,"genocide":self.witch_genocide_used})

        responses = await self.wait_for_players_responses(
            witches, 
            "night_witches_vote_response", 
            45
        )

        current, _ = self.get_vote_result(responses)

        if current == 1 and not self.witch_save_used:
            #Save
            self.to_kill.remove(victim)
            self.witch_save_used = True

        if current == 2 and not self.witch_genocide_used:
            await self.run_witch_genocide()

        await asyncio.sleep(3)
        await self.send_list_players(witches,"night_witch_end")

    async def run_death_eater(self):
        logger.info("Starting Death Eater phase.")
        death_eaters = self.get_players_by_role("death_eater")

        if len(death_eaters) < 1 or self.death_eater_used:
            logger.warning("No death_eaters found during death_eaters phase. Skipping.")
            return

        await self.send_list_players(death_eaters, "night_death_eater_start", {})

        villagers = []
        for id in list(self.death_room):
            if id in self.players:
                villagers.append({"id": id, "name": self.players[id].name})
  
        await self.send_list_players(death_eaters, "night_death_eater_vote", {"deads":villagers})

        responses = await self.wait_for_players_responses(
            death_eaters, 
            "night_death_eater_vote_response", 
            45
        )

        current, vote_count = self.get_vote_result(responses)  

        if current is not None:
            self.transfer_to_living_room(current)
            self.send_player(current,"alive",{})

        self.death_eater_used = True

    async def run_witch_genocide(self):
        logger.info("Starting Witch Genocide phase.")
        witches = self.get_players_by_role("witch")

        if len(witches) < 1:
            logger.warning("No witches found during witch genocide phase. Skipping.")
            return

        await self.send_list_players(witches, "night_witch_genocide_start", {})

        villagers = []
        for id in list(self.playing_room):
            if id in self.players:
                villagers.append({"id": id, "name": self.players[id].name})
  
        await self.send_list_players(witches, "night_witch_genocide_vote", {"villagers":villagers})

        responses = await self.wait_for_players_responses(
            witches, 
            "night_witch_genocide_vote_response", 
            45
        )

        current, vote_count = self.get_vote_result(responses)  

        if current is not None:
            self.to_kill.append(current)   

        self.witch_genocide_used = True

    async def crazy_dave_does(self):
        await self.send_all_players("crazy_dave_up", {})
        await asyncio.sleep(5)
        await self.send_all_players("switch_night", {"current_day": self.current_day})
        self.current_day += 1
        await asyncio.sleep(3)
        await self.send_all_players("switch_day", {"current_day": self.current_day})
        await asyncio.sleep(3)
        await self.send_all_players("switch_night", {"current_day": self.current_day})
        await asyncio.sleep(3)

        crazy_dave = self.get_players_by_role("crazy_dave", exclude_to_kill=False)

        if len(crazy_dave) < 1:
            logger.warning("No crazy_dave found during crazy_dave phase. Skipping.")
            await asyncio.sleep(5)
            return

        await self.send_list_players(crazy_dave, "crazy_dave_does_vote", {})

        responses = await self.wait_for_players_responses(
            crazy_dave, 
            "crazy_dave_does_response", 
            45
        )

        current, _ = self.get_vote_result(responses)
        if current is not None:
            await self.kill_players([current])

    async def crazy_dave_vote(self):
        crazy_dave = self.get_players_by_role("crazy_dave", exclude_to_kill=False)

        if len(crazy_dave) < 1 or self.crazy_dave_up:
            logger.warning("No crazy_dave found or already used. Skipping.")
            await asyncio.sleep(1)
            return

        await self.send_list_players(crazy_dave, "crazy_dave_vote", {})

        responses = await self.wait_for_players_responses(
            crazy_dave, 
            "crazy_dave_response", 
            15
        )

        current, _ = self.get_vote_result(responses)
        if current == 1:
            self.crazy_dave_up = True
            await self.crazy_dave_does()

    async def run_game(self):
        self.status = 0
        self.finished = False

        logger.info("Started Game Loop.")
        logger.debug(f"Waiting for minimum player count ({self.min_player_count}).")

        while len(self.players) < self.min_player_count:
            await asyncio.sleep(0.1)

        logger.debug("Player count met, starting game in 10 seconds.")
        await self.send_all_players_waiting("game_start_soon", {})
        self.status = 1

        await asyncio.sleep(10)

        self.transfer_to_player_room()
        logger.info(f"Starting day/night cycle. Current playing count: {len(self.playing_room)}")

        self.current_day = 0
        self.current_roles, self.players_per_roles = self.get_roles()
        self.set_game_flags()
        self.to_kill = []

        for i in list(self.playing_room):
            if i in self.players:
                self.players[i].role = self.current_roles[i]
                await self.send_player(i, "player_role", {"role": self.current_roles[i]})
            else:
                logger.warning(f"Player {i} dropped out before receiving their role.")

        await asyncio.sleep(15)

        while not self.finished:
            if not self.finished:
                await self.run_night()
                await self.check_win()

            if not self.finished:
                await self.run_day()
                await self.check_win()   

        logger.info("Game has finished. Resetting rooms.")
        await self.send_all_players("back_to_waiting", {})
        await self.send_all_players_dead("back_to_waiting", {})

        self.transfer_to_waiting_room()

        players = []
        for id in list(self.waiting_room):
            if id in self.players:
                players.append({"id": id, "name": self.players[id].name})

        await asyncio.sleep(1)

        await self.send_all_players_waiting("waiting_room_list_update", {"players": players, "status": self.status})
        self.phase_name = "waiting"
        self.phase_start_time = None
        self.phase_duration = 0
        logger.success("Game Loop Ended Cleanly.")