# Google Translate plugin
# author: Vladislav Janvarev

from oneringcore import OneRingCore
import os
import subprocess

modname = os.path.basename(__file__)[:-3] # calculating modname

# start function
def start(core:OneRingCore):
    manifest = { # plugin settings
        "name": "llama.cpp llm translator", # name
        "version": "1.0", # version

        "translate": {
            "llama_cpp": (init,translate) # 1 function - init, 2 - translate
        }
    }
    return manifest

def init(core:OneRingCore):
    pass

def translate(core:OneRingCore, text:str, from_lang:str = "", to_lang:str = "", add_params:str = ""):
    if(from_lang=="en"):
      from_lang="english"
    if(to_lang=="en"):
      to_lang="english"
    if(from_lang=="ru"):
      from_lang="russian"
    if(to_lang=="ru"):
      to_lang="russian"
    w=open("prompt.txt","w")
    w.write("You are text translator. Keep punctuation and quotes.### Instruction:\n\nTranslate from %s to %s.\n\n### Input:\n\n%s\n\n### Output:\n\n"%(from_lang,to_lang,text))
    w.close()
    process = subprocess.Popen("~/llama.cpp/build/default/bin/main -t 4 -m /d/llama-65b-q5_0.ggjt2 --temp 0 -e -r '\"\"' -r '##' -r '\\n\\n' -f prompt.txt > output.txt 2> output.err", shell=True, stdout=subprocess.PIPE)
    process.wait()
    w=open("output.txt","r")
    res=w.read()
    w.close()
    res = res.replace("<|prompter|>","").replace('""',"").replace("##","").strip();
    return res
