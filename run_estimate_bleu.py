from nltk.translate.bleu_score import sentence_bleu

# ----------
from oneringcore import OneRingCore

# ----------------- key settings params ----------------
BLEU_PAIRS = "fra->eng,eng->fra,rus->eng,eng->rus" # pairs of language in terms of FLORES dataset https://huggingface.co/datasets/gsarti/flores_101/viewer
BLEU_PAIRS_2LETTERS = "fr->en,en->fr,ru->en,en->ru" # pairs of language codes that will be passed to plugin (from_lang, to_lang params)

#BLEU_PAIRS = "fra->eng,eng->fra"
#BLEU_PAIRS_2LETTERS = "fr->en,en->fr" # needed to pass to plugins
#BLEU_PLUGINS = "no_translate,libre_translate,fb_nllb_translate,google_translate"

BLEU_PLUGINS = "no_translate,google_translate" # plugins to estimate
#BLEU_PLUGINS = "no_translate,google_translate" # plugins to estimate

BLEU_NUM_PHRASES = 100 # num of phrases to estimate. Between 1 and 100 for now.
BLEU_START_PHRASE = 150 # offset from FLORES dataset to get NUM phrases

core:OneRingCore = None

def load_dataset(lang, split, start, num):
    import requests
    req_url = f"https://datasets-server.huggingface.co/rows?dataset=gsarti%2Fflores_101&config={lang}&split={split}&offset={start}&limit={num}"
    #print(req_url)
    #return ""
    r = requests.get(req_url)
    j = r.json()
    #return j["rows"]

    # we have problems with NUM param when getting results from server, so try to fix it
    rows = j["rows"]
    if len(rows) > num:
        rows = rows[:num]

    return rows




def translate(text:str, from_lang:str = "", to_lang:str = "", translator_plugin:str = "", add_params:str = ""):
    if translator_plugin != "":
        core.init_translator_engine(translator_plugin)

        if translator_plugin not in core.inited_translator_engines:
            return {"error": "Translator plugin not inited"}

    if translator_plugin == "":
        translator_plugin = core.default_translator

    res = core.translators[translator_plugin][1](core,text,from_lang,to_lang,add_params)

    return res

if __name__ == "__main__":
    from tqdm import trange
    import tqdm
    #multiprocessing.freeze_support()
    core = OneRingCore()
    core.init_with_plugins()

    pairs_ar = BLEU_PAIRS.split(",")
    pairs_ar2 = BLEU_PAIRS_2LETTERS.split(",")
    bleu_plugins_ar = BLEU_PLUGINS.split(",")

    table_bleu = [([bleu_plugins_ar[i]] + (["-"] * len(pairs_ar))) for i in range(len(bleu_plugins_ar))]

    for j in range(len(pairs_ar)):
        pair = pairs_ar[j]
        pair2 = pairs_ar2[j]

        from_lang, to_lang = pair.split("->")
        from_lang_let2, to_lang_let2 = pair2.split("->") # we usually needs 2letter lang codes to transfer to plugins


        from_lines = load_dataset(from_lang, "devtest", BLEU_START_PHRASE, BLEU_NUM_PHRASES)
        to_lines = load_dataset(to_lang, "devtest", BLEU_START_PHRASE, BLEU_NUM_PHRASES)

        for k in range(len(bleu_plugins_ar)):
            plugin = bleu_plugins_ar[k]

            #print(f"--------------\n{plugin} plugin\n--------------\n")

            bleu_sum = 0.0
            bleu_cnt = 0
            print(f"---- Estimating {plugin} for pair {pair}....")
            tqdm_bar = trange(len(from_lines))
            for i in tqdm_bar: # tqdm range
                text_need_translate = from_lines[i]["row"]["sentence"]
                text_reference = to_lines[i]["row"]["sentence"]
                text_candidate = translate(text_need_translate,from_lang_let2,to_lang_let2, plugin)

                score = sentence_bleu([text_reference.strip().split()],text_candidate.strip().split(),weights=(0.5, 0.5))
                #print(f"Original: {text_need_translate}\nTranslation: {text_candidate}\nReference: {text_reference}\nScore: {score}\n\n")

                bleu_sum += score
                bleu_cnt += 1

                tqdm_bar.set_description(f"'{plugin}' on '{pair}' pair average BLEU score: {'{:8.2f}'.format(bleu_sum*100/bleu_cnt)}")

                # if plugin == "openai_chat":
                #     import time
                #     time.sleep(20)

            bleu_score = bleu_sum / len(from_lines)
            print(f"****** Average BLEU score for '{plugin}' on '{pair.upper()}' pair ({len(to_lines)} samples): {bleu_score}")

            table_bleu[k][j+1] = "{:8.2f}".format(bleu_score*100)

    from tabulate import tabulate
    res_print_table = tabulate(table_bleu,headers=[" "*60]+pairs_ar,tablefmt="github")

    print("*" * 60)
    print("BLEU scores")
    print("*" * 60)
    print(res_print_table)

