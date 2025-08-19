import os
from dataclasses import dataclass

import torch
from PIL import Image
from transformers import CLIPModel, CLIPProcessor

DEFAULT_MODEL_NAME = "openai/clip-vit-base-patch32"
DEFAULT_DEVICE = "cpu"


@dataclass
class ModelContext:
    model_name: str = DEFAULT_MODEL_NAME
    device: str = DEFAULT_DEVICE
    model: any = None
    processor: any = None

    def get_model(self) -> tuple:
        if not self.model or not self.processor:
            self.model = CLIPModel.from_pretrained(
                self.model_name,
                # device_map=None,          # don’t spread weights around
                # low_cpu_mem_usage=False,  # materialize weights immediately
            ).to(self.device)
            self.processor = CLIPProcessor.from_pretrained(self.model_name)
            self.model.eval()
        return self.model, self.processor


def create_context(
    model_name: str = DEFAULT_MODEL_NAME, device: str = DEFAULT_DEVICE
) -> ModelContext:
    return ModelContext(model_name=model_name, device=device)


@torch.no_grad()
def embed_images(model_ctx: ModelContext, image_paths: list):
    model, processor = model_ctx.get_model()
    images = [Image.open(p).convert("RGB") for p in image_paths]
    inputs = processor(images=images, return_tensors="pt", padding=True)
    inputs = {k: v.to(model_ctx.device) for k, v in inputs.items()}
    feats = model.get_image_features(**inputs)
    feats = feats / feats.norm(dim=-1, keepdim=True)
    return feats.cpu().numpy()


@torch.no_grad()
def embed_text(model_ctx: ModelContext, query: str):
    model, processor = model_ctx.get_model()
    inputs = processor(text=[query], return_tensors="pt", padding=True)
    inputs = {k: v.to(model_ctx.device) for k, v in inputs.items()}
    feats = model.get_text_features(**inputs)
    feats = feats / feats.norm(dim=-1, keepdim=True)
    return feats.squeeze(0).cpu().numpy()


_model_ctx = None


def get_model_context() -> ModelContext:
    global _model_ctx
    if _model_ctx is None:
        _model_ctx = create_context()
    return _model_ctx
