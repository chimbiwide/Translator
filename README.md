# Translator TUI

A TUI app to translate large volumes of text (e.g. A novel) using LM Studio

---

### Architecture

`translator.py`: define all the methods for interacting with LM Studio
`TUI.py`: the Textual app itself, using the methods from `translator.py`

### Translation Pipeline

- the user would select a file from the folder tree
- select their desired model for translation (e.g. [Hunyuan-MT](https://huggingface.co/tencent/Hunyuan-MT-7B))
- select their target language
- press the translate button
- the file would be cleaned (remove all blank lines)
- then the parsed file would be parsed into a list (chunks would be created for every 2000 characters)
- each element would be fed to the model
- when the translation is done, a file would be created (`translated_file.txt`)

### To-do List

- [ ] custom output file name
- [ ] multiple files at once (async)