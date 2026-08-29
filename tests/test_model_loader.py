"""Tests for model loader utility."""


from src.ui.model_loader import ModelLoader


class TestModelLoader:
    """Tests for ModelLoader."""

    def test_init(self):
        loader = ModelLoader()
        assert loader is not None

    def test_load_model_returns_none_when_no_path(self):
        loader = ModelLoader()
        model = loader.load_model(None)
        assert model is None

    def test_load_vectorizer_returns_none_when_no_path(self):
        loader = ModelLoader()
        vec = loader.load_vectorizer(None)
        assert vec is None
