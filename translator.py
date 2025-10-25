import lmstudio as lms
import subprocess

def clean_file(path: str):
    with open(path, 'r', encoding='utf-8') as f:
        lines = [line for line in f if line.strip()]
    with open (path, "w", encoding='utf-8') as f:
        f.writelines(lines)

def read_file(path:str) -> str:
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()
    return text

def parse_file(text:str, max_chars:int=2000) -> list:
    if len(text) <= max_chars:
        return [text]
    lines = text.splitlines(keepends=True)
    chunks = []
    current_chunk = ""

    for line in lines:
        if len(current_chunk) + len(line) > max_chars and current_chunk:
            chunks.append(current_chunk)
            current_chunk = line
        else:
            current_chunk += line
    if current_chunk:
        chunks.append(current_chunk)

    return chunks

def downloaded_models():
            downloaded = lms.list_downloaded_models("llm")
            model_key = []
            for model in downloaded:
                model_key.append(model.model_key)
            return model_key

def start_server():
    result = subprocess.run(["lms","server","start"], capture_output=True, text=True)
    print(result.stderr)

def stop_server():
    result = subprocess.run(["lms","server","stop"], capture_output=True, text=True)
    print(result.stderr)

def llmInstance(text:str, target_lang: str, model:str, temp:float=1.0, top_k:int=40, top_p:float=0.9, rep_penalty: float=1.0) -> str:
    model = lms.llm(model,config={
        "contextLength": 10240,
        "gpu": {
            "ratio": 0.5,
        }
    })
    prompt = f"Translate the following segment into {target_lang}, without additional explanation.\n\n" + text
    translated_txt = model.respond(prompt, config={
        "temperature": temp,
        "topKSampling": top_k,
        "repeatPenalty": rep_penalty,
        "topPSampling": top_p
    })
    return translated_txt.content

def unload_model(model:str):
    model = lms.llm(model)
    model.unload()

def target_language():
    return ["English", "Chinese", "French", "Spanish", "Japanese", "Arabic", "German"]

def translate(file:list, target_lang: str, model:str, temp:float=1.0, top_k:int=40, top_p:float=0.9, rep_penalty: float=1.0) -> str:
    translated_text = ""
    for i, text in enumerate(file):
        print(f"Translating segment {i+1}")
        translated_text += llmInstance(text, target_lang, model, temp, top_k, top_p, rep_penalty)
        print(f"Translated segment {i+1}\n\n")
    return translated_text

def write_file(text:str, output_path:str="./translated_file.txt"):
    with open(output_path, 'w', encoding='utf-8') as f:
        f.writelines(text)

def main():
    clean_file("message.txt")
    file = read_file("message.txt")
    text = parse_file(file)
    translated = translate(text, "zh", "huihui-ai.huihui-hunyuan-mt-7b-abliterated", 0.7, 20, 0.6, 1.05)
    write_file(translated)

def translate_pipeline(path:str, model:str, target_lang:str,temp:float=1.0, top_k:int=40, top_p:float=0.9, rep_penalty: float=1.0) -> str:
    clean_file(path)
    file = read_file(path)
    text = parse_file(file)
    translated = translate(text, target_lang, model, 0.7, 20, 0.6, 1.05)
    write_file(translated)

if __name__ == "__main__":
    main()