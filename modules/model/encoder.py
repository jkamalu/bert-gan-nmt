__author__ = 'John Kamalu'

'''
A wrapper class for BERT/vanilla self-attention models for inclusion
in NMT and sequence-to-sequence pipelines
'''

import argparse
import torch.nn as nn

from transformers import (RobertaConfig, RobertaModel, RobertaTokenizer,
                          CamembertConfig, CamembertModel, CamembertTokenizer)


MODEL_CLASSES = {
    'english': (RobertaConfig, RobertaModel, "roberta-base"),
    'french': (CamembertConfig, CamembertModel, "camembert-base")
}


class Encoder(nn.Module):

    def __init__(self, impl):
        super().__init__()

        self.is_initialized = False
        self.impl = impl

    @classmethod
    def init_from_config(cls, impl, encoder_kwargs, embedding=None, language=None):
        module = cls(impl)
        
        if impl == "bert":
            _, model_class, weights = MODEL_CLASSES[language]
            module.model = model_class.from_pretrained(weights)
            module.embeddings = module.model.get_input_embeddings()
        else:
            raise NotImplementedError

        module.is_initialized = True

        return module

    def forward(self, src, lengths=None):
        assert self.is_initialized

        if self.impl == "bert":
            # huggingface models assume (B, L) and return [sequence_output, pooled_output, ...]
            output = self.model(src)[0]

        return output
