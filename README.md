# WEB API for translation

Simple WEB API REST service for translation.

Features:
- **Plugin support**. If you misses some translation engine, you can add it yourself! 
- **Full offline translation (optionally).** You can setup your own offlie https://github.com/LibreTranslate/LibreTranslate service and target this service to use it as endpoint.
- **Ready to use**. By default use Google Translate service, and ready to use.
- Simple REST interface throw FastApi and openapi.json interface. After install go to `http://127.0.0.1:4990/docs` to see examples.
- **API keys**. (Disabled by default) You can restrict access to your service by set up a list of API keys, needed to access the service. 

Supported translators by plugins for now:
- Google Translate (online)
- Libre Translate (online or offline)
- FB NLLB neuronet (offline)
- KoboldAPI endpoint (offline mostly due to target localhost)
  - KoboldAPI is a REST interface for lots of LLM servers (like [koboldcpp](https://github.com/LostRuins/koboldcpp/releases), [text-generation-webui](https://github.com/oobabooga/text-generation-webui))
  - If you load some LLM model inside this LLM server, you can translate texts using them!
  - (Now plugin uses Alpaca template to set translation task. Change it if you want)
- No Translate (offline) - dummy translator to compare with

## One-click installer for Windows

Go here: https://github.com/janvarev/OneRingTranslator-installer and follow instructions.

## Install and run

To run: 
1. Install requirements ```pip install -r requirements.txt```
2. Run run_webapi.py.

Docs and test run: `http://127.0.0.1:4990/docs`

## Average BLEU results for translation quality

BLEU (bilingual evaluation understudy) is an automatic algorithm for evaluating the quality of text which has been machine-translated from one natural language to another.

Use this results just for reference.

Table with BLEU scores (higher is better, no_translate can be used as baseline):

|                                            |   fra->eng |   eng->fra |   rus->eng |   eng->rus |
|--------------------------------------------|------------|------------|------------|------------|
| no_translate                               |       3.98 |       3.9  |       0.57 |       0.56 |
| libre_translate                            |      47.66 |      49.62 |      32.43 |      30.99 |
| fb_nllb_translate nllb-200-distilled-600M  |      51.92 |      52.73 |      41.38 |      31.41 |
| fb_nllb_translate nllb-200-distilled-1.3B  |      56.81 |       55   |      46.03 |      33.98 |
| google_translate                           |      58.08 |      59.99 |      47.7  |      37.98 |

Average results with different LLMs:

|                                            |   rus->eng |   eng->rus |
|--------------------------------------------|------------|------------|
| no_translate                               |       0.57 |       0.56 |
| libre_translate                            |      32.43 |      30.99 |
| koboldapi_translate (alpaca7B-4bit)        |      32    |      14.19 |
| koboldapi_translate (alpaca30B-4bit)       |      -     |      24.0  |

'koboldapi_translate' on 'eng->rus' pair average BLEU score:     7.00: 80/100
on IlyaGusev-saiga_7b_lora_llamacpp-ggml-model-q4_1.bin, may be adjusting for input prompt needed

## Plugins

### google_translate

Used by default. 

Options: no

Translate with Google Translate.

### libre_translate

Libre Translate service

Options:
- `custom_url` If you want, setup your https://github.com/LibreTranslate/LibreTranslate server locally, and target custom_url to gain translation from your server)

### fb_nllb_translate

Translate by neuronet from https://github.com/facebookresearch/fairseq/tree/nllb

Options
- `model` define model to use 

Details:
- You need to install transfomers and torch to use this.
- This will use original BCP 47 Code to target language: https://github.com/facebookresearch/flores/blob/main/toxicity/README.md
Plugin try to recognize 2-language-codes to transform them to BCP 47 Code, but better will be pass them manually (by from_lang, to_lang params)  

### no_translate

Dummy plugins that just return original text. 

Options: no

Translate with Google Translate.

### koboldapi_translate

Translate by sending prompt to LLM throw KoboldAPI (REST) interface. 

Options:
- `custom_url` Kobold API endpoint

KoboldAPI is a REST interface for lots of LLM servers (like [koboldcpp](https://github.com/LostRuins/koboldcpp/releases), [text-generation-webui](https://github.com/oobabooga/text-generation-webui))

If you load some LLM model inside this LLM server, you can translate texts using them!

(Now plugin uses Alpaca template to set translation task. Change it if you want)


### More plugins

Please, post your additional plugins here:
https://github.com/janvarev/OneRingTranslator/issues/1

## Plugin support

Plugins supported throw [Jaa.py](https://github.com/janvarev/jaapy) - minimalistic one-file plugin engine.

Plugins are located in the plugins folder and must start with the "plugins_" prefix.

Plugin settings, if any, are located in the "options" folder (created after the first launch).

Examples can be found in `plugins` dir.

## Core options description (core.json)

Located in `options/core.json` after first run.

```python
{
    "default_translate_plugin": "google_translate", # default translation engine
    "default_from_lang": "es", # default from language
    "default_to_lang": "en", # default to language
    "api_keys_allowed": [], # set of API keys. If empty - no API key required.
    "debug_input_output": False, # allow debug print input and output in console
    "allow_multithread": True, # allow multithread run of translation engine
    "user_lang": "", # standart user language. Replaces "user" in to_lang or from_lang API params 
},
```

## API example usage

Translate from en to fr
```
http://127.0.0.1:4990/translate?text=Hi%21&from_lang=en&to_lang=fr
```

Translate from en to user language (user language defines in plugins/core.json)
```
http://127.0.0.1:4990/translate?text=Hi%21&from_lang=en&to_lang=user
```

Full Python usage example:
```python
custom_url = params['custom_url']
if custom_url == "":
    res = "Please, setup custom_url for OneRingTranslator (usually http://127.0.0.1:4990/)"
else:
    import requests
    response_orig = requests.get(f"{custom_url}translate", params={"text":string,"from_lang":from_lang,"to_lang":to_lang})
    if response_orig.status_code == 200:
        response = response_orig.json()
        #print("OneRingTranslator result:",response)

        if response.get("error") is not None:
            print(response)
            res = "ERROR: "+response.get("error")
        elif response.get("result") is not None:
            res = response.get("result")
        else:
            print(response)
            res = "Unknown result from OneRingTranslator"
    elif response_orig.status_code == 404:
        res = "404 error: can't find endpoint"
    elif response_orig.status_code == 500:
        res = "500 error: OneRingTranslator server error"
    else:
        res = f"{response_orig.status_code} error"
```

## Automatic BLEU estimation

There are builded package to run BLEU estimation of plugin translation on different languages.

There are pretty simple estimation based on FLORES dataset: https://huggingface.co/datasets/gsarti/flores_101/viewer

To estimate:
1. install requirements-bleu.txt
2. setup params in run_estimate_bleu.py (at beginning of file)
3. run run_estimate_bleu.py

RECOMMENDATIONS: 
1. debug separate plugins first!
2. To debug, use less BLEU_NUM_PHRASES.