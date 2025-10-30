from pathlib import Path
from typing import Iterable

from textual import on, work
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, DirectoryTree, Select, Button, ProgressBar, Label
from textual.containers import HorizontalGroup, CenterMiddle, Center, VerticalScroll

from translator import downloaded_models, start_server, stop_server, target_language, translate_pipeline

class FolderTree(DirectoryTree):
    def filter_paths(self, paths: Iterable[Path]) -> Iterable[Path]:
        return [path for path in paths if path.name.endswith(".txt")]

class Config(HorizontalGroup):
    def compose(self) -> ComposeResult:
        yield Select.from_values(downloaded_models(), prompt="Select Desired Model", id="model_select")
        yield Select.from_values(target_language(), prompt="Select target language", id="language_select")

class Bottom_Panel(VerticalScroll):
    def compose(self) -> ComposeResult:
        yield ProgressBar(show_eta=False,show_bar=False, show_percentage=False,id="translate_progress")
        yield Button("Translate", id="translate", variant="success")

class TUI(App):
    CSS_PATH = "TUI.tcss"

    selected_model = ""
    selected_language = ""
    file_path = ""
    file_name = ""

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        yield FolderTree("./", id="target_file")
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
            self.set_translate_state(True)
            self.do_translation()

    @work(exclusive=True, thread=True)
    def do_translation(self) -> None:
        progress_bar = self.query_one("#translate_progress", ProgressBar)
        progress_bar.show_bar = True
        progress_bar.show_percentage = True
        progress_bar.progress = 0

        translate_pipeline(
            self.file_path,
            self.selected_model,
            self.selected_language,
            0.7, 20, 0.6, 1.05,
            progress_callback=lambda current, total: self.call_from_thread(self.update_progress, current, total)
        )
        self.call_from_thread(self.on_translation_complete)

    def set_translate_state(self, translating: bool) -> None:
        folder_tree = self.query_one("#target_file", DirectoryTree)
        select_lang = self.query_one("#language_select", Select)
        select_model = self.query_one("#model_select", Select)
        translate_button = self.query_one("#translate", Button)

        if translating:
            folder_tree.disabled = True
            select_lang.disabled = True
            select_model.disabled = True

            translate_button.label = "Translating..."
            translate_button.disabled = True
        else:
            folder_tree.disabled = False
            select_lang.disabled = False
            select_model.disabled = False

            translate_button.label = "Translate"
            translate_button.disabled = False

    def update_progress(self, current: int, total: int) -> None:
        progress_bar = self.query_one("#translate_progress", ProgressBar)
        progress_bar.update(total=total, progress=current)

    def on_translation_complete(self) -> None:
        self.set_translate_state(False)

        progress_bar = self.query_one("#translate_progress", ProgressBar)
        progress_bar.progress = 0
        progress_bar.show_bar = False
        progress_bar.show_percentage = False

        self.sub_title = "Translation Complete!"
        self.set_timer(5, self.clear_subtitles)

    def clear_subtitles(self) -> None:
        self.sub_title = ""
if __name__ == "__main__":
    start_server()
    app = TUI()
    app.run()
    stop_server()