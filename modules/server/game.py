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
        self.roles = ["villager", "werewolf"]
        self.nights_roles = ["werewolf"]
        self.pending_responses = {}
        self.phase_name = "waiting"         
        self.phase_start_time = None
        self.phase_duration = 0

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
    
    async def new_player(self, player_id):
        logger.info(f"New player {player_id} joined the waiting room.")
        players = []
        for id in list(self.waiting_room):
            if id in self.players:
                players.append({"id": id, "name": self.players[id].name})
            else:
                logger.warning(f"Player {id} is in waiting room but missing from players dictionary.")

        await self.send_all_players_waiting("waiting_room_list_update", {"players": players, "status": self.status})

    def get_roles(self):
        logger.debug("Assigning roles to players.")
        result = {}
        per_roles = {}

        for i in list(self.playing_room):
            if i in self.players:
                assigned_role = random.choice(self.roles)
                result[i] = assigned_role

                if assigned_role in per_roles:
                    per_roles[assigned_role].append(i)
                else:
                    per_roles[assigned_role] = [i]

        logger.info(f"Roles assigned: { {role: len(players) for role, players in per_roles.items()} }")
        return result, per_roles

    def get_players_by_role(self, role):
        players = []
        for id in self.players_per_roles.get(role, []):
            if id in self.players and id in self.playing_room and getattr(self.players[id], 'role', None) == role and id not in self.to_kill:
                players.append(id)
        return players

    def get_vote_result(self, responses):
        results = {}
        current = None
        current_count = 0

        for i in responses:
            if responses[i] is not None:
                vote_target = responses[i].get("vote")
                if vote_target:
                    results[vote_target] = results.get(vote_target, 0) + 1

                    if results[vote_target] > current_count:
                        current = vote_target
                        current_count = results[vote_target]

        logger.debug(f"Vote results tallied: {results}. Winner: {current} with {current_count} votes.")
        return current, current_count

    async def run_werewolf(self):
        logger.info("Starting Werewolf phase.")
        villagers = []
        werewolfs = self.get_players_by_role("werewolf")

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

        if current is not None:
            logger.info(f"Werewolves voted to kill: {current}")
            self.to_kill.append(current)        
        else:
            logger.info("Werewolves did not agree on a target.")
            
        await asyncio.sleep(3)
        await self.send_list_players(werewolfs, "night_werewolf_end", {})

    async def kill_players(self, players):
        killed = []

        for id in players:
            if id in self.players:
                logger.info(f"Killing player {id} ({self.players[id].name}).")
                killed.append({"id": id, "name": self.players[id].name, "role": getattr(self.players[id], 'role', 'unknown')})
                await self.send_player(id, "killed", {})
                self.transfer_to_death_room(id)
            else:
                logger.warning(f"Tried to kill player {id}, but they are no longer in the game.")

        if killed:
            await self.send_all_players("day_death", {"death": killed})

    async def run_night(self):
        self.phase_name = "night"
        self.phase_start_time = time.time()
        self.phase_duration = 55
        logger.info(f"--- Night {self.current_day} Starting ---")
        self.to_kill = []
        await self.send_all_players("switch_night", {"current_night": self.current_day})
        await asyncio.sleep(5)
        await self.run_werewolf()
        await asyncio.sleep(5)

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
        await asyncio.sleep(5)

    async def check_win(self):
        werewolfs = self.get_players_by_role("werewolf")
        logger.debug(f"Win Check - Werewolves remaining: {len(werewolfs)}")
        
        if len(werewolfs) < 1:
            logger.success("Villagers Victory detected.")
            await self.send_all_players("game_end", {"winner": "villager"})
            self.finished = True
            return

        villagers = self.get_players_by_role("villager")
        logger.debug(f"Win Check - Villagers remaining: {len(villagers)}")
        
        if len(villagers) < 1:
            logger.success("Werewolf Victory detected.")
            await self.send_all_players("game_end", {"winner": "werewolf"})
            self.finished = True
            return

    async def run_game(self):
        self.status = 0
        self.finished = False

        logger.info("Started Game Loop.")
        logger.debug(f"Waiting for minimum player count ({self.min_player_count}).")

        while not len(self.players.keys()) >= self.min_player_count:
            await asyncio.sleep(0.1)

        logger.debug("Player count met, starting game in 10 seconds.")
        await self.send_all_players("game_start_soon", {})
        self.status = 1

        await asyncio.sleep(10)

        self.transfer_to_player_room()
        logger.info(f"Starting day/night cycle. Current playing count: {len(self.playing_room)}")

        self.current_day = 0
        self.current_roles, self.players_per_roles = self.get_roles()
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
                await asyncio.sleep(3)
                
            if not self.finished:
                await self.run_day()
                await self.check_win()   
                await asyncio.sleep(3)
            
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