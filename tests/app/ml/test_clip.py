"""Tests for CLIP embedding helpers."""

import unittest

import numpy as np
from app.ml import clip

TEST_ASSETS_PATH = "./tests/assets/ml/clip"


class TestClip(unittest.TestCase):
    """Unit tests for CLIP image/text embedding functions."""

    def __init__(self, methodName="runTest"):
        self.model_ctx = clip.create_context()
        super().__init__(methodName)

    def test_embeds(self):
        """Test embedding images and text with CLIP."""

        cat_idx = 0
        elephant_idx = 1
        cat_path = f"{TEST_ASSETS_PATH}/cat.jpg"
        elephant_path = f"{TEST_ASSETS_PATH}/elephant.jpg"

        image_paths = [cat_path, elephant_path]
        embeddings = clip.embed_images(self.model_ctx, image_paths)
        self.assertEqual(len(embeddings), 2)
        self.assertEqual(embeddings[cat_idx].shape, (512,))
        self.assertEqual(embeddings[elephant_idx].shape, (512,))

        text_query = "a cute cat"
        cat_text_embedding = clip.embed_text(self.model_ctx, text_query)
        self.assertEqual(cat_text_embedding.shape, (512,))

        text_vec = cat_text_embedding
        mat = np.array(list(embeddings), dtype=np.float32)
        scores = mat @ text_vec.astype(np.float32)
        self.assertGreater(scores[cat_idx], scores[elephant_idx])

        text_query = "a large elephant"
        elephant_text_embedding = clip.embed_text(self.model_ctx, text_query)
        self.assertEqual(elephant_text_embedding.shape, (512,))

        text_vec = elephant_text_embedding
        mat = np.array(list(embeddings), dtype=np.float32)
        scores = mat @ text_vec.astype(np.float32)
        self.assertGreater(scores[elephant_idx], scores[cat_idx])
