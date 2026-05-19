import json
import asyncio
import websockets
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Button, Input, RichLog, Label
from textual.containers import VerticalScroll, Vertical, Container
from textual import work

class WerewolfClient(App):
    CSS = """
    #main_layout { layout: horizontal; height: 1fr; }
    #left_panel { width: 35%; border-right: tall $primary; padding: 1; background: $surface; }
    #right_panel { width: 65%; padding: 1; background: $boost; }
    .section_container { border: round $accent; margin-bottom: 1; padding: 1; height: auto; }
    .section_label { text-style: bold; color: $secondary; margin-bottom: 1; content-align: center top; }
    Button { margin: 0 1 1 0; width: 100%; }
    .vote_btn { background: $error; color: white; text-style: bold; }
    .special_btn { background: $warning; color: black; text-style: bold; }
    #chronicle_log { border: double $primary; height: 1fr; background: #0a0a0a; color: #dddddd; }
    Input { margin-bottom: 1; }
    #action_container { height: 1fr; border: panel $success; padding: 1; }
    """

    def __init__(self):
        super().__init__()
        self.ws = None
        self.connected = False
        self.player_name = ""
        self.phase = "waiting"
        self.my_role = "unknown"
        self.pending_response_opcode = None
        self.vote_candidates = []
        self.alive = True
        self.lover = None

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Container(id="main_layout"):
            with Vertical(id="left_panel"):
                with Vertical(classes="section_container"):
                    yield Label("🌐 CONNECTION & LOBBY", classes="section_label")
                    yield Input(value="ws://localhost:8765", id="ws_url", placeholder="Server URL...")
                    yield Button("Connect", id="connect_btn", variant="success")
                    yield Input(placeholder="Enter your name...", id="player_name", disabled=True)
                    yield Button("Join Game", id="join_btn", variant="primary", disabled=True)

                with VerticalScroll(id="action_container"):
                    yield Label("🎮 GAME ACTIONS", classes="section_label")
                    yield Label("Waiting for the moon to rise...", id="action_status")
                    yield VerticalScroll(id="vote_buttons_container")
            with Vertical(id="right_panel"):
                yield Label("📜 VILLAGE CHRONICLE", classes="section_label")
                yield RichLog(id="chronicle_log", wrap=True, highlight=True)

    def on_mount(self) -> None:
        self.set_interval(1, self.update_ui)

    def update_ui(self) -> None:
        pass

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        btn_id = event.button.id
        if btn_id == "connect_btn":
            await self.action_connect()
        elif btn_id == "join_btn":
            await self.action_join()
        else:
            await self.handle_vote_button(btn_id)

    async def handle_vote_button(self, btn_id: str) -> None:
        if not self.pending_response_opcode or not self.ws:
            return
        target = None
        if btn_id == "vote_skip":
            target = None
        elif btn_id == "vote_explode":
            target = -1
        elif btn_id.startswith("vote_"):
            target = btn_id[5:]
        else:
            return

        response = {}
        opcode = self.pending_response_opcode
        if opcode in ("night_werewolf_vote_response", "night_greedy_wolf_response",
                      "night_black_wolf_vote_response", "night_pyromane_response",
                      "night_homelander_kill_response", "night_homelander_protect_response",
                      "mark_grayson_response", "crazy_dave_does_response",
                      "jules_cesar_vote_response", "day_vote_response",
                      "night_seer_response", "night_cupid_response",
                      "night_poisoner_response", "night_death_eater_response"):
            response["vote"] = target
        elif opcode == "night_moon_fighter_response":
            response["skip"] = True if target == "skip" else False
        elif opcode == "night_witch_response":
            response["heal"] = target if target != "none" else None
            response["kill"] = target if target != "none" else None
        elif opcode == "crazy_dave_response":
            response["activate"] = True if target == "activate" else False
        elif opcode == "jules_cesar_decide":
            response["use"] = True if target == "use" else False
        elif opcode == "night_cupid_response":
            response["targets"] = [target, target] if target else []
        await self.send_server_message(opcode, response)
        self.pending_response_opcode = None
        
        # Explicit clean-up on click action
        container = self.query_one("#vote_buttons_container")
        await container.remove_children()

    async def action_connect(self) -> None:
        url = self.query_one("#ws_url").value.strip()
        if not url:
            self.add_log("⚠️ Please enter a WebSocket server URL.")
            return
        try:
            self.ws = await websockets.connect(url)
            self.connected = True
            self.add_log("🌙 Connection to the village established...")
            self.query_one("#player_name").disabled = False
            self.query_one("#join_btn").disabled = False
            asyncio.create_task(self.message_listener())
        except Exception as e:
            self.add_log(f"❌ Connection failed: {e}")

    async def action_join(self) -> None:
        name = self.query_one("#player_name").value.strip()
        if not name:
            self.add_log("⚠️ Enter your name before joining.")
            return
        self.player_name = name
        await self.send_server_message("player_join", {"name": name})
        self.add_log(f"✨ {name} enters the village waiting room.")

    async def send_server_message(self, opcode: str, data: dict) -> None:
        if not self.ws:
            return
        try:
            message = json.dumps({"opcode": opcode, "data": data})
            await self.ws.send(message)
        except Exception as e:
            self.add_log(f"❌ Failed to send message: {e}")

    def add_log(self, message: str) -> None:
        try:
            self.query_one("#chronicle_log").write(message)
        except Exception:
            pass

    async def message_listener(self) -> None:
        while self.connected:
            try:
                msg = await self.ws.recv()
                data = json.loads(msg)
                await self.handle_message(data["opcode"], data.get("data", {}))
            except websockets.ConnectionClosed:
                self.add_log("💔 Connection to the village lost.")
                self.connected = False
                break
            except Exception as e:
                self.add_log(f"⚠️ Error: {e}")

    async def handle_message(self, opcode: str, data: dict) -> None:
        if opcode == "waiting_room_list_update":
            players = data.get("players", [])
            status = data.get("status", 0)
            names = [p["name"] for p in players]
            self.add_log(f"🏠 Waiting room ({len(names)}): {', '.join(names)}")
            self.query_one("#action_status").update("Waiting for players...")
        elif opcode == "game_start_soon":
            self.add_log("🔮 Game will start soon! The roles are being assigned...")
            self.query_one("#action_status").update("Game starting...")
        elif opcode == "player_role":
            self.my_role = data["role"]
            self.add_log(f"🎭 Your secret role: {self.my_role.upper()}")
            self.query_one("#action_status").update(f"You are {self.my_role}")
        elif opcode == "switch_night":
            night_num = data.get("current_night", 0)
            self.phase = "night"
            self.add_log(f"🌜 Night {night_num} falls upon the village... The creatures stir.")
            self.query_one("#action_status").update("Night phase")
        elif opcode == "switch_day":
            day = data.get("current_day", 0)
            self.phase = "day"
            self.add_log(f"☀️ Day {day} breaks. The survivors gather to accuse.")
            self.query_one("#action_status").update("Day phase")
        elif opcode == "night_seer_start":
            self.add_log("🔮 The Seer closes their eyes and reaches out to the spirits...")
        elif opcode == "night_seer_vote":
            await self.prepare_vote("night_seer_response", data.get("villagers", []), "Choose a villager to see their role")
        elif opcode == "night_seer_result":
            target = data.get("target")
            role = data.get("role")
            self.add_log(f"🔮 The spirits whisper: {target} is a {role}.")
        elif opcode == "night_seer_end":
            self.add_log("🔮 The Seer opens their eyes.")
        elif opcode == "night_cupid_start":
            self.add_log("💘 Cupid readies their bow...")
        elif opcode == "night_cupid_vote":
            await self.prepare_vote("night_cupid_response", data.get("villagers", []), "Select two villagers to bind (pick first target)")
        elif opcode == "night_cupid_end":
            self.add_log("💘 Cupid's arrows have flown.")
        elif opcode == "you_are_lovers":
            self.add_log("💕 You are now bound by love. If one lover dies, the other follows.")
        elif opcode == "night_poisoner_start":
            self.add_log("🧪 The Poisoner mixes a deadly brew...")
        elif opcode == "night_poisoner_vote":
            await self.prepare_vote("night_poisoner_response", data.get("villagers", []), "Choose a victim to poison (takes effect next day)")
        elif opcode == "night_poisoner_end":
            self.add_log("🧪 The Poisoner puts away the vials.")
        elif opcode == "poisoned_blocked":
            self.add_log("🤢 You feel too weak to vote today... the poison courses through your veins.")
        elif opcode == "night_necromancer_start":
            self.add_log("☠️ The Necromancer communes with the dead...")
        elif opcode == "night_necromancer_info":
            dead = data.get("dead_players", [])
            names = [f"{p['name']} ({p['role']})" for p in dead]
            self.add_log(f"☠️ The dead whisper: {', '.join(names) if names else 'No dead yet.'}")
        elif opcode == "night_necromancer_end":
            self.add_log("☠️ The Necromancer's ritual ends.")
        elif opcode == "homelander_psycho_mode":
            self.add_log("🔥 Homelander's mind snaps! They can now kill.")
        elif opcode == "night_homelander_start":
            self.add_log("🛡️ Homelander decides who to protect or eliminate...")
        elif opcode == "night_homelander_protect_vote":
            await self.prepare_vote("night_homelander_protect_response", data.get("villagers", []), "Choose a villager to protect")
        elif opcode == "night_homelander_kill_vote":
            await self.prepare_vote("night_homelander_kill_response", data.get("villagers", []), "Choose a villager to kill (psycho mode)")
        elif opcode == "night_homelander_end":
            self.add_log("🛡️ Homelander's action is set.")
        elif opcode == "night_werewolf_start":
            self.add_log("🐺 The werewolves gather under the moon...")
        elif opcode == "night_werewolf_vote":
            await self.prepare_vote("night_werewolf_vote_response", data.get("villagers", []), "Choose a victim to devour")
        elif opcode == "night_werewolf_end":
            self.add_log("🐺 The pack retreats.")
        elif opcode == "night_greedy_wolf_start":
            self.add_log("🍖 The Greedy Wolf hungers for an extra kill...")
        elif opcode == "night_greedy_wolf_vote":
            await self.prepare_vote("night_greedy_wolf_response", data.get("villagers", []), "Choose a second victim")
        elif opcode == "night_greedy_wolf_end":
            self.add_log("🍖 Greedy Wolf is satisfied.")
        elif opcode == "night_black_wolfs_start":
            self.add_log("🖤 The Black Wolf prepares to convert the victim...")
        elif opcode == "night_black_wolf_vote":
            info = data.get("villager", {})
            await self.prepare_vote("night_black_wolf_vote_response", [info], "Do you want to consume this villager's identity?")
        elif opcode == "night_black_wolf_end":
            self.add_log("🖤 The Black Wolf's jaws close.")
        elif opcode == "role_change":
            new_role = data.get("new_role")
            self.my_role = new_role
            self.add_log(f"🔄 Your role has changed! You are now {new_role}.")
        elif opcode == "night_witch_start":
            self.add_log("🧙 The Witch brews two potions...")
        elif opcode == "night_witch_vote":
            victims = data.get("victims", [])
            villagers = data.get("villagers", [])
            self.add_log("🧙 Choose to heal someone marked for death or poison a villager.")
            await self.prepare_vote("night_witch_response", villagers, f"Victims: {[v['name'] for v in victims]}. Tap a villager to heal/kill.")
        elif opcode == "night_witch_end":
            self.add_log("🧙 The Witch's cauldron settles.")
        elif opcode == "night_death_eater_start":
            self.add_log("💀 The Death Eater reaches for a fallen soul...")
        elif opcode == "night_death_eater_vote":
            await self.prepare_vote("night_death_eater_response", data.get("dead", []), "Choose a dead player to resurrect")
        elif opcode == "night_death_eater_end":
            self.add_log("💀 The Death Eater's hand fades.")
        elif opcode == "player_revived":
            name = data.get("name")
            self.add_log(f"✨ {name} has been resurrected!")
        elif opcode == "night_moon_fighter_vote":
            await self.prepare_vote("night_moon_fighter_response", [{"id": "skip", "name": "Skip the night"}, {"id": "continue", "name": "Continue night"}],
                              "Do you want to skip the entire night?")
        elif opcode == "night_moon_fighter_response":
            self.add_log("🌕 Moon Fighter makes a choice.")
        elif opcode == "night_pyromane_start":
            self.add_log("🔥 The Pyromane collects fuel...")
        elif opcode == "night_pyromane_vote":
            villagers = data.get("villagers", [])
            self.add_log("🔥 Choose a villager to douse, or press EXPLODE to ignite all doused.")
            await self.prepare_vote("night_pyromane_response", villagers, "Douse or EXPLODE")
        elif opcode == "pyromane_explosion":
            self.add_log("💥 KABOOM! The Pyromane's bombs explode!")
        elif opcode == "night_pyromane_end":
            self.add_log("🔥 The Pyromane rests.")
        elif opcode == "mark_grayson_died":
            self.add_log("⚡ Mark Grayson has been killed! Their final vengeance begins...")
        elif opcode == "mark_grayson_vote":
            await self.prepare_vote("mark_grayson_response", data.get("villagers", []), "Choose a victim for your dying wrath")
        elif opcode == "killed":
            self.alive = False
            self.add_log("💀 You have been killed. You wander the death room now.")
            self.query_one("#action_status").update("Dead")
        elif opcode == "day_death":
            deaths = data.get("death", [])
            for d in deaths:
                self.add_log(f"⚰️ {d['name']} ({d['role']}) has died.")
        elif opcode == "day_vote":
            villagers = data.get("villagers", [])
            await self.prepare_vote("day_vote_response", villagers, "Vote for a villager to be executed")
        elif opcode == "day_jules_cesar_prompt":
            await self.prepare_vote("jules_cesar_decide", [{"id": "use", "name": "Use power"}, {"id": "skip", "name": "Skip"}],
                              "Do you want to use your imperial authority?")
        elif opcode == "jules_cesar_took_vote":
            self.add_log(f"👑 Jules César takes the vote!")
        elif opcode == "jules_cesar_vote":
            await self.prepare_vote("jules_cesar_vote_response", data.get("villagers", []), "Choose the target of your imperial judgement")
        elif opcode == "jules_cesar_success":
            mayor = data.get("mayor")
            executed = data.get("executed")
            self.add_log(f"👑 César's verdict: {executed} is a werewolf and is executed!")
        elif opcode == "jules_cesar_failed":
            executed = data.get("executed")
            self.add_log(f"👑 César's error: {executed} was innocent. César is executed instead.")
        elif opcode == "crazy_dave_vote":
            await self.prepare_vote("crazy_dave_response", [{"id": "activate", "name": "Activate"}, {"id": "skip", "name": "Skip"}],
                              "Do you want to trigger your time-bending ability?")
        elif opcode == "crazy_dave_up":
            self.add_log("🌀 Crazy Dave warps time! Days and nights blur...")
        elif opcode == "crazy_dave_does":
            self.add_log("🌀 Crazy Dave's chaos unfolds...")
        elif opcode == "crazy_dave_does_vote":
            await self.prepare_vote("crazy_dave_does_response", data.get("villagers", []), "Choose a victim to erase from time")
        elif opcode == "game_end":
            winner = data.get("winner")
            self.add_log(f"🏆 The game is over! The {winner} win!")
            self.query_one("#action_status").update("Game ended")
            self.pending_response_opcode = None
            container = self.query_one("#vote_buttons_container")
            await container.remove_children()
        elif opcode == "back_to_waiting":
            self.add_log("🔁 Returning to the waiting room...")
            self.phase = "waiting"
            self.my_role = "unknown"
            self.alive = True
            self.lover = None
            self.query_one("#action_status").update("In waiting room")

    async def prepare_vote(self, response_opcode: str, candidates: list, instruction: str) -> None:
        self.pending_response_opcode = response_opcode
        self.vote_candidates = candidates
        container = self.query_one("#vote_buttons_container")
        
        # Awaiting clean-up prevents concurrent execution states from leaking memory
        await container.remove_children()
        
        self.add_log(f"🗳️ {instruction}")
        self.query_one("#action_status").update(instruction)

        widgets_to_mount = []

        if response_opcode in ("night_pyromane_response",):
            widgets_to_mount.append(Button("💥 EXPLODE", id="vote_explode", variant="error"))
            
        if response_opcode in ("night_moon_fighter_response",):
            for c in candidates:
                widgets_to_mount.append(Button(c["name"], id=f"vote_{c['id']}", variant="primary"))
            if widgets_to_mount:
                await container.mount(*widgets_to_mount)
            return
            
        if response_opcode in ("jules_cesar_decide", "crazy_dave_response"):
            for c in candidates:
                widgets_to_mount.append(Button(c["name"], id=f"vote_{c['id']}", variant="warning"))
            if widgets_to_mount:
                await container.mount(*widgets_to_mount)
            return

        for c in candidates:
            widgets_to_mount.append(Button(c["name"], id=f"vote_{c['id']}", variant="primary"))
            
        widgets_to_mount.append(Button("Skip", id="vote_skip", variant="default"))
        
        if widgets_to_mount:
            await container.mount(*widgets_to_mount)

if __name__ == "__main__":
    app = WerewolfClient()
    app.run()