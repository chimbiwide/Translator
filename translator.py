import lmstudio as lms

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

def llmInstance(text:str, target_lang: str, model:str, temp:float=1.0, top_k:int=40, top_p:float=0.9, rep_penalty: float=1.0) -> str:
    model = lms.llm(model)
    prompt = f"Translate the following segment into {target_lang}, without additional explanation.\n\n" + text
    translated_txt = model.respond(prompt, config={
        "temperature": temp,
        "topKSampling": top_k,
        "repeatPenalty": rep_penalty,
        "topPSampling": top_p
    })
    return translated_txt.content

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
    file = read_file("message.txt")
    text = parse_file(file)
    translated = translate(text, "zh", "huihui-ai.huihui-hunyuan-mt-7b-abliterated", 0.7, 20, 0.6, 1.05)
    write_file(translated)

if __name__ == "__main__":
    main()