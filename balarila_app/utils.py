import os
import sys

# Adds the 'balarila_model' directory to the Python path
BALARILA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'balarila_model')
sys.path.insert(0, BALARILA_DIR)

# Import from balarila library
from balarila_model.gector.gec_model import GecBERTModel
from balarila_model.balarila_predict import get_model

_model_cache = None

def load_gec_model(
    model_type="roberta-large",
    model_stage=3,
    model_dir=None,
    max_len=50,
    min_len=3,
    iteration_count=5,
    min_error_probability=0.0,
    additional_confidence=0.0,
    additional_del_confidence=0.0,
    weights=None,
):
    global _model_cache
    if _model_cache is None:
        print(f"Loading Balarila GEC model: {model_type}, stage {model_stage}...")
        
        # Resolve model_dir if it's relative
        from django.conf import settings
        if model_dir and not os.path.isabs(model_dir):
            model_dir = os.path.join(settings.BASE_DIR, model_dir) # Ensure absolute path from BASE_DIR

        model_path, vocab_path, transformer_model, special_tokens_fix = \
            get_model(model_type, model_stage, model_dir)

        _model_cache = GecBERTModel(
            vocab_path=vocab_path,
            model_paths=[model_path],
            max_len=max_len,
            min_len=min_len,
            iterations=iteration_count,
            min_error_probability=min_error_probability,
            lowercase_tokens=False,
            model_name=transformer_model,
            special_tokens_fix=special_tokens_fix,
            log=False,
            confidence=additional_confidence,
            del_confidence=additional_del_confidence,
            is_ensemble=0,
            weigths=weights,
        )
        print("Balarila GEC model loaded successfully.")
    return _model_cache

def get_gec_model():
    global _model_cache
    if _model_cache is None:
        from django.conf import settings
        load_gec_model(
            model_type=getattr(settings, 'BALARILA_MODEL_TYPE', "roberta-large"),
            model_stage=getattr(settings, 'BALARILA_MODEL_STAGE', 3),
            model_dir=getattr(settings, 'BALARILA_MODEL_DIR', None),
            max_len=getattr(settings, 'BALARILA_MAX_LEN', 50),
            min_len=getattr(settings, 'BALARILA_MIN_LEN', 3),
            iteration_count=getattr(settings, 'BALARILA_ITERATION_COUNT', 5),
            min_error_probability=getattr(settings, 'BALARILA_MIN_ERROR_PROBABILITY', 0.0),
            additional_confidence=getattr(settings, 'BALARILA_ADDITIONAL_CONFIDENCE', 0.0),
            additional_del_confidence=getattr(settings, 'BALARILA_ADDITIONAL_DEL_CONFIDENCE', 0.0),
            weights=getattr(settings, 'BALARILA_WEIGHTS', None),
        )
    return _model_cache

def check_grammar(text):
    model = get_gec_model()
    pred, cnt, tags = model.refactored_handle_batch([text.split()])

    corrected_text = " ".join(pred[0])
    tags_applied = tags[0]
    corrections_count = cnt

    return {
        "original_text": text,
        "corrected_text": corrected_text,
        "tags": tags_applied,
        "corrections_count": corrections_count
    }

def correct_grammar(text):
    model = get_gec_model()
    pred, _, _ = model.refactored_handle_batch([text.split()])
    return " ".join(pred[0])