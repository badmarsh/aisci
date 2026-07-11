"""Runtime compatibility shims for Python services started with this helper path.

Currently used by the Onyx model-server containers. Transformers 5 stores Qwen2
RoPE settings under ``rope_parameters`` while the remote code for
Alibaba-NLP/gte-Qwen2-1.5B-instruct still reads ``config.rope_theta``.
"""

try:
    from transformers.models.qwen2.configuration_qwen2 import Qwen2Config
except Exception:
    Qwen2Config = None


if Qwen2Config is not None and not hasattr(Qwen2Config, "rope_theta"):

    def _get_rope_theta(self):
        rope_parameters = getattr(self, "rope_parameters", None)
        if isinstance(rope_parameters, dict):
            return rope_parameters.get("rope_theta", 1000000.0)
        return getattr(rope_parameters, "rope_theta", 1000000.0)
    
    def _set_rope_theta(self, value):
        # Store in rope_parameters dict if it exists
        rope_parameters = getattr(self, "rope_parameters", None)
        if rope_parameters is None:
            object.__setattr__(self, "rope_parameters", {"rope_theta": value})
        elif isinstance(rope_parameters, dict):
            rope_parameters["rope_theta"] = value

    Qwen2Config.rope_theta = property(_get_rope_theta, _set_rope_theta)


if Qwen2Config is not None and not getattr(Qwen2Config, "_onyx_embedding_patch", False):
    _qwen2_config_init = Qwen2Config.__init__

    def _patched_qwen2_config_init(self, *args, **kwargs):
        _qwen2_config_init(self, *args, **kwargs)
        # The model server only uses Qwen2 here for embeddings; caching is not
        # useful and older remote model code is incompatible with Transformers 5.
        self.use_cache = False

    Qwen2Config.__init__ = _patched_qwen2_config_init
    Qwen2Config._onyx_embedding_patch = True


try:
    from transformers.cache_utils import DynamicCache
except Exception:
    DynamicCache = None


if DynamicCache is not None and not hasattr(DynamicCache, "from_legacy_cache"):

    @classmethod
    def _from_legacy_cache(cls, past_key_values=None, *args, **kwargs):
        if past_key_values is None or isinstance(past_key_values, cls):
            return past_key_values or cls()
        return cls(past_key_values)

    def _to_legacy_cache(self):
        return tuple((layer.keys, layer.values) for layer in self.layers)

    def _get_usable_length(self, new_seq_length=None, layer_idx=0):
        return self.get_seq_length(layer_idx)

    DynamicCache.from_legacy_cache = _from_legacy_cache
    DynamicCache.to_legacy_cache = _to_legacy_cache
    DynamicCache.get_usable_length = _get_usable_length
