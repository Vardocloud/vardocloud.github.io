"""Patch _PROVIDER_MODELS['nvidia'] + cached_provider_model_ids for glm-5.2."""
import sys
import importlib.abc
import importlib.machinery


class _NvidiaPatcherLoader(importlib.abc.Loader):
    """Loader that wraps the real models module and patches it."""

    def __init__(self, real_loader):
        self._real = real_loader

    def create_module(self, spec):
        return None  # Use default

    def exec_module(self, module):
        self._real.exec_module(module)

        # Patch _PROVIDER_MODELS — ensure glm-5.2 in curated list
        nv = getattr(module, "_PROVIDER_MODELS", {}).get("nvidia")
        if nv and "z-ai/glm-5.2" not in nv:
            nv.append("z-ai/glm-5.2")
            print("[usercustomize] +glm-5.2 to NVIDIA curated", flush=True)

        # Patch cached_provider_model_ids — pin glm-5.2 to TOP of picker list
        _orig_cached = getattr(module, "cached_provider_model_ids", None)
        if _orig_cached is not None:
            def _patched_cached(provider):
                result = list(_orig_cached(provider))
                if provider == "nvidia" and "z-ai/glm-5.2" in result:
                    result.remove("z-ai/glm-5.2")
                    result.insert(0, "z-ai/glm-5.2")
                return result
            module.cached_provider_model_ids = _patched_cached
            print("[usercustomize] glm-5.2 pinned to TOP of NVIDIA picker", flush=True)


class _NvidiaPatcherFinder(importlib.abc.MetaPathFinder):
    """Intercept hermes_cli.models to patch after load."""

    def find_spec(self, fullname, path, target=None):
        if fullname != "hermes_cli.models":
            return None
        # Find the real spec
        for finder in sys.meta_path:
            if finder is self:
                continue
            if hasattr(finder, 'find_spec'):
                spec = finder.find_spec(fullname, path, target)
                if spec is not None:
                    spec.loader = _NvidiaPatcherLoader(spec.loader)
                    return spec
        return None


# Register early (before other finders process anything)
sys.meta_path.insert(0, _NvidiaPatcherFinder())
