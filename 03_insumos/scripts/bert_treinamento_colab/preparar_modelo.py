
import pathlib, json, difflib
from huggingface_hub import HfApi, snapshot_download
root = pathlib.Path.cwd()
model = 'neuralmind/bert-base-portuguese-cased'
revision = HfApi().model_info(model).sha
snapshot = snapshot_download(model, revision=revision,
    allow_patterns=['config.json','tokenizer*','vocab.txt','special_tokens_map.json',
                    '*.safetensors','pytorch_model.bin'])
(root/'modelo_base.json').write_text(json.dumps({'repo_id':model,'revision':revision,'snapshot':snapshot},indent=2))
original = (root/'treinar_bert_original.py').read_text()
needle = 'MODEL_NAME  = "neuralmind/bert-base-portuguese-cased"'
assert original.count(needle) == 1
adaptado = original.replace(needle, 'MODEL_NAME  = ' + repr(snapshot))
(root/'treinar_bert.py').write_text(adaptado)
(root/'adaptacao.patch').write_text(''.join(difflib.unified_diff(
    original.splitlines(True),adaptado.splitlines(True),fromfile='original',tofile='execucao')))
