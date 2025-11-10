from pathlib import Path
from typing import Iterable

from textual import on, work
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, DirectoryTree, Select, Button, ProgressBar, Input
from textual.containers import HorizontalGroup,VerticalScroll

from translator import downloaded_models, start_server, stop_server, target_language, translate_pipeline, process_file_pipeline, unload_model

class FolderTree(DirectoryTree):
    #folder tree to show the txt files in the directory
    def filter_paths(self, paths: Iterable[Path]) -> Iterable[Path]:
        return [path for path in paths if path.name.endswith(".txt")]
    def on_mount(self) -> None:
        self.watch_path()

class Config(HorizontalGroup):
    def compose(self) -> ComposeResult:
        #select model from the downloaded models
        yield Select.from_values(downloaded_models(), prompt="Select Desired Model", id="model_select")
        #seleect target language
        yield Select.from_values(target_language(), prompt="Select target language", id="language_select")

class Bottom_Panel(VerticalScroll):
    def compose(self) -> ComposeResult:
        #Input for file name:
        yield Input(placeholder="Enter Output file name(defaults to original filename + translated)", max_length=12, id="file_name")
        #progress bar to show steps for translations
        yield ProgressBar(show_eta=False,show_bar=True, show_percentage=True,id="translate_progress")
        #button for translating
        yield Button("Translate", id="translate", variant="success")

class TUI(App):
    CSS_PATH = "TUI.tcss"

    selected_model = ""
    selected_language = ""
    file_path = ""
    file_name = ""
    outputfile_name = ""

    def compose(self) -> ComposeResult:
        #folder at the very top, then the select, then the progressbar&button
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

    @on(Input.Changed)
    def outputfile(self, message: Input.Changed):
        self.outputfile_name = message.value + ".txt"

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
        if not self.outputfile_name:
            self.outputfile_name = self.file_name.replace(".txt", "_translated.txt")
        if button_id == "translate":
            self.set_timer(3, self.clear_subtitles)
            self.set_translate_state(True)
            self.do_translation()

    @work(exclusive=True, thread=True)
    def do_translation(self) -> None:
        #when the translation button is pressed, start a textual worker
        #the purpose is to make the progress bar update while the file is being translated
        segments = process_file_pipeline(self.file_path)
        segment_length = len(segments)

        self.call_from_thread(self.init_progress, segment_length)
        translate_pipeline(
            segments,
            self.selected_model,
            self.outputfile_name,
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
        progress_bar = self.query_one("#translate_progress", ProgressBar)
        input = self.query_one("#file_name", Input)

        if translating:
            folder_tree.disabled = True
            select_lang.disabled = True
            select_model.disabled = True
            progress_bar.visible = True
            input.disabled = True

            translate_button.label = "Translating..."
            translate_button.disabled = True

            progress_bar.progress = 0
        else:
            folder_tree.disabled = False
            select_lang.disabled = False
            select_model.disabled = False
            progress_bar.visible = False
            input.disabled = False

            translate_button.label = "Translate"
            translate_button.disabled = False

    def update_progress(self, current: int, total:int) -> None:
        progress_bar = self.query_one("#translate_progress", ProgressBar)
        progress_bar.update(progress=current)

    def init_progress(self, total: int) -> None:
        progress_bar = self.query_one("#translate_progress", ProgressBar)
        progress_bar.update(total=total, progress=0)

    def on_translation_complete(self) -> None:
        self.set_translate_state(False)

        progress_bar = self.query_one("#translate_progress", ProgressBar)
        progress_bar.progress = 0

        folder_tree = self.query_one("#target_file", FolderTree)
        folder_tree.reload()

        self.sub_title = "Translation Complete!"
        self.set_timer(5, self.clear_subtitles)

    def clear_subtitles(self) -> None:
        self.sub_title = ""

if __name__ == "__main__":
    start_server()
    app = TUI()
    app.run()
    unload_model()
    stop_server()