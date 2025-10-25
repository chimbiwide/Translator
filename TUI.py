from pathlib import Path
from typing import Iterable

from textual import on
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, DirectoryTree, Select, Button, ProgressBar
from textual.containers import HorizontalGroup, CenterMiddle, Center, VerticalScroll

from translator import downloaded_models, start_server, stop_server,target_language, translate_pipeline

class FolderTree(DirectoryTree):
    def filter_paths(self, paths: Iterable[Path]) -> Iterable[Path]:
        return [path for path in paths if path.name.endswith(".txt")]

class Config(HorizontalGroup):
    def compose(self) -> ComposeResult:
        yield Select.from_values(downloaded_models(), prompt="Select Desired Model", id="model_select")
        yield Select.from_values(target_language(), prompt="Select target language", id="language_select")

class Bottom_Panel(VerticalScroll):
    def compose(self) -> ComposeResult:
        yield Button("Translate", id="translate", variant="success")
        yield ProgressBar(total=100, show_eta=False, id="translate_progress") #add total = length of parse_file()

class TUI(App):
    CSS_PATH = "TUI.tcss"

    selected_model = ""
    selected_language = ""
    file_path = ""
    file_name = ""

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        yield FolderTree("./")
        yield Config()
        yield Bottom_Panel()

    @on(Select.Changed)
    def select_changed(self,event:Select.Changed) -> None:
        if event.control.id == "model_select":
            self.selected_model = str(event.value)
        elif event.control.id == "language_select":
            self.selected_language = str(event.value)

    @on(FolderTree.FileSelected)
    def handle_file(self, message: DirectoryTree.FileSelected) -> None:
        selected_file_path = message.path
        selected_file_name = selected_file_path.name
        self.file_path = str(selected_file_path)
        self.file_name = selected_file_name

    @on(Button.Pressed)
    def start_translate(self, event: Button.Pressed) -> None:
        button_id = event.button.id
        if not self.file_path:
            self.sub_title = "Please select a file first"
            return
        if not self.selected_model:
            self.sub_title = "Please select a model first"
            return
        if not self.selected_language:
            self.sub_title = "Please select a target language first"
            return
        if button_id == "translate":
            self.add_class("started")
            translate_pipeline(self.file_path, self.selected_model, self.selected_language, 0.7, 20, 0.6, 1.05)

if __name__ == "__main__":
    start_server()
    app = TUI()
    app.run()
    stop_server()