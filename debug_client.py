import json
import asyncio
import websockets
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Button, Input, RichLog, Label
from textual.containers import VerticalScroll, Vertical, Container
from textual import work

class WerewolfClient(App):
    """An intelligent, narrative-driven client for the Werewolf Game."""

    CSS = """
    #main_layout {
        layout: horizontal;
        height: 1fr;
    }

    #left_panel {
        width: 35%;
        border-right: tall $primary;
        padding: 1;
        background: $surface;
    }

    #right_panel {
        width: 65%;
        padding: 1;
        background: $boost;
    }

    .section_container {
        border: round $accent;
        margin-bottom: 1;
        padding: 1;
        height: auto;
    }

    .section_label {
        text-style: bold;
        color: $secondary;
        margin-bottom: 1;
        content-align: center top;
    }

    Button {
        margin: 0 1 1 0;
        width: 100%;
    }

    .vote_btn {
        background: $error;
        color: white;
        text-style: bold;
    }

    #log_panel {
        border: double $primary;
        height: 1fr;
        background: #111111;
        color: #dddddd;
    }

    Input {
        margin-bottom: 1;
    }
    
    #action_container {
        height: 1fr;
        border: panel $success;
        padding: 1;
    }
    """

    def __init__(self):
        super().__init__()
        self.ws = None
        self.current_vote_opcode = None
        self.has_joined = False

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        
        with Container(id="main_layout"):
            # LEFT PANEL: Controls, Joining, and Dynamic Actions
            with Vertical(id="left_panel"):
                
                # Connection & Join Section
                with Vertical(classes="section_container"):
                    yield Label("🌐 CONNECTION & LOBBY", classes="section_label")
                    yield Input(value="ws://localhost:8765", id="ws_url", placeholder="Server URL...")
                    yield Button("Connect", id="connect_btn", variant="success")
                    
                    yield Input(placeholder="Enter your name...", id="player_name", disabled=True)
                    yield Button("Join Game", id="join_btn", variant="primary", disabled=True)

                # Dynamic Action Section (Populated only when expected by the server)
                with VerticalScroll(id="action_container"):
                    yield Label("🎮 GAME ACTIONS", classes="section_label")
                    yield Label("Waiting for game events...", id="action_status")

            # RIGHT PANEL: Narrative Log
            with Vertical(id="right_panel"):
                yield Label("📜 VILLAGE CHRONICLE", classes="section_label")
                yield RichLog(id="log_panel", markup=True, highlight=True, wrap=True)
        
        yield Footer()

    # --- UI EVENT HANDLERS ---

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        btn_id = event.button.id

        if btn_id == "connect_btn":
            if self.ws:
                await self.disconnect()
            else:
                url = self.query_one("#ws_url", Input).value
                self.connect_to_server(url)

        elif btn_id == "join_btn":
            name = self.query_one("#player_name", Input).value.strip()
            if name:
                await self.send_message("player_join", {"name": name})
                self.has_joined = True
                self.query_one("#player_name", Input).disabled = True
                event.button.disabled = True
                self.write_log(f"*[italic]You stepped into the village as '{name}'...[/italic]*")

        elif btn_id and btn_id.startswith("vote_target_"):
            # Extract the target ID from the button ID
            target_id = btn_id.replace("vote_target_", "")
            
            # Send the vote back using the context-aware opcode (Day or Night)
            if self.current_vote_opcode:
                await self.send_message(self.current_vote_opcode, {"vote": target_id})
                self.write_log("[bold cyan]You have cast your vote.[/bold cyan]")
                # Immediately clear actions so the user can't vote twice
                await self.clear_actions()
                self.query_one("#action_status", Label).update("Vote cast. Waiting for others...")

    # --- NETWORKING & WORKERS ---

    @work(exclusive=True)
    async def connect_to_server(self, url: str) -> None:
        conn_btn = self.query_one("#connect_btn", Button)
        join_btn = self.query_one("#join_btn", Button)
        name_input = self.query_one("#player_name", Input)

        self.write_log(f"[yellow]Journeying to {url}...[/yellow]")
        try:
            self.ws = await websockets.connect(url)
            self.write_log("[bold green]✅ Arrived at the village gates (Connected).[/bold green]")
            
            # Update UI for connection
            conn_btn.label = "Disconnect"
            conn_btn.variant = "error"
            if not self.has_joined:
                join_btn.disabled = False
                name_input.disabled = False

            # Listen loop
            while True:
                message = await self.ws.recv()
                await self.handle_server_message(json.loads(message))

        except Exception as e:
            self.write_log(f"[bold red]❌ The path is blocked (Error):[/bold red] {e}")
        finally:
            self.ws = None
            conn_btn.label = "Connect"
            conn_btn.variant = "success"
            join_btn.disabled = True
            name_input.disabled = True
            self.has_joined = False
            self.write_log("[yellow]You have left the village (Disconnected).[/yellow]")

    async def disconnect(self):
        if self.ws:
            await self.ws.close()
        
    async def send_message(self, opcode: str, data: dict):
        if self.ws:
            payload = json.dumps({"opcode": opcode, "data": data})
            await self.ws.send(payload)

    # --- GAME LOGIC & NARRATIVE INTERPRETER ---

    async def handle_server_message(self, msg: dict):
        opcode = msg.get("opcode")
        data = msg.get("data", {})
        
        # Lobby updates
        if opcode == "waiting_room_list_update":
            players = data.get("players", [])
            names = [p.get("name", "Unknown") for p in players]
            self.write_log(f"👥 [blue]The town square gathers:[/blue] {len(players)} souls present. ({', '.join(names)})")

        # Game Initializing
        elif opcode == "game_start_soon":
            self.write_log("\n[bold magenta]⏳ A chilling wind blows... The game begins in 10 seconds![/bold magenta]\n")
            await self.clear_actions()

        elif opcode == "player_role":
            role = data.get("role", "unknown")
            role_color = "bold red" if role == "werewolf" else "bold green"
            self.write_log(f"🎭 [bold]SECRET ROLE:[/bold] You are a [{role_color}]{role.upper()}[/{role_color}]!")

        # Night Phase
        elif opcode == "switch_night":
            self.write_log("\n[bold blue]🌙 The sun sets. The village goes to sleep. Close your eyes...[/bold blue]")
            await self.clear_actions()
            self.query_one("#action_status", Label).update("The village is asleep...")

        elif opcode == "night_werewolf_start":
            self.write_log("🐺 [bold red]WEREWOLVES WAKE UP.[/bold red] Time to hunt.")

        elif opcode == "night_werewolf_vote":
            self.write_log("🩸 [italic red]Who shall be your prey tonight?[/italic red]")
            await self.show_vote_buttons(data.get("villagers", []), "night_werewolf_vote_response")

        elif opcode == "night_werewolf_end":
            self.write_log("💤 [italic]The blood is washed away. Return to sleep.[/italic]")
            await self.clear_actions()

        # Day Phase
        elif opcode == "switch_day":
            day = data.get("current_day", 0)
            self.write_log(f"\n[bold yellow]☀️ Day {day} breaks! The village wakes up.[/bold yellow]")
            await self.clear_actions()

        elif opcode == "day_death":
            deaths = data.get("death", [])
            if not deaths:
                self.write_log("🕊️ [green]A peaceful morning. Nobody died last night![/green]")
            else:
                for d in deaths:
                    self.write_log(f"💀 [bold red]TRAGEDY![/bold red] [bold]{d['name']}[/bold] was found torn apart! They were a {d['role']}.")

        elif opcode == "day_vote":
            self.write_log("⚖️ [bold]The town gathers. Who is the Werewolf among you?[/bold]")
            await self.show_vote_buttons(data.get("villagers", []), "day_vote_response")

        # End states
        elif opcode == "killed":
            self.write_log("\n🪦 [bold red]YOU HAVE BEEN KILLED.[/bold red] You are now a ghost. You may watch, but you cannot speak.")
            await self.clear_actions()
            self.query_one("#action_status", Label).update("You are dead.")

        elif opcode == "game_end":
            winner = data.get("winner", "nobody")
            win_color = "bold red" if winner == "werewolf" else "bold green"
            self.write_log(f"\n🏆 [bold yellow]THE GAME IS OVER![/bold yellow] The [{win_color}]{winner.upper()}S[/{win_color}] have won!")
            await self.clear_actions()

        elif opcode == "back_to_waiting":
            self.write_log("\n🔙 Returning to the lobby...")

    # --- UI HELPER METHODS ---

    def write_log(self, text: str):
        """Safely write to the log panel."""
        log = self.query_one("#log_panel", RichLog)
        log.write(text)

    async def clear_actions(self):
        """Removes all dynamic vote buttons."""
        actions_container = self.query_one("#action_container")
        self.current_vote_opcode = None
        # Remove any existing buttons
        for btn in actions_container.query(Button):
            btn.remove()
        
    async def show_vote_buttons(self, targets: list, response_opcode: str):
        """Dynamically generates buttons only for valid voting targets."""
        await self.clear_actions()
        actions_container = self.query_one("#action_container")
        status_label = self.query_one("#action_status", Label)
        
        self.current_vote_opcode = response_opcode
        status_label.update("Select a target below:")

        for t in targets:
            # We don't render buttons for ourselves if we know our ID, 
            # but the server provides the list.
            btn_id = f"vote_target_{t['id']}"
            await actions_container.mount(Button(f"Vote: {t['name']}", id=btn_id, classes="vote_btn"))

if __name__ == "__main__":
    app = WerewolfClient()
    app.run()