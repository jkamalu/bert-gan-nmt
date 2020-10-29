from collections import defaultdict

from nltk.translate.bleu_score import sentence_bleu

import torch


def write_to_tensorboard(base, metrics, training, step, writer):
    """
    Write data to tensorboard.

    Example usage:
        writer = SummaryWriter("runs/regularize_hidden")
        write_to_tensorboard("CCE", {'l1-l2': 0.5, 'l2-l1': 0.4}, True, 42, writer)
    """

    tag = "{}/{}".format(base, "train" if training else "val")

    writer.add_scalars(tag, metrics, step)


def loss_fn(real_l1, real_l2, pred_l1, pred_l2, real_pred_ys={}, ignore_index_l1=1, ignore_index_l2=1):
    '''
    Adversarial Loss: standard loss with binary cross entropy on top of the discriminator outputs
    '''
    cce_loss_l2 = torch.nn.CrossEntropyLoss(ignore_index=ignore_index_l2)
    cce_loss_l1 = torch.nn.CrossEntropyLoss(ignore_index=ignore_index_l1)
    
    loss_l2 = cce_loss_l2(pred_l2.transpose(1,2), real_l2)
    loss_l1 = cce_loss_l1(pred_l1.transpose(1,2), real_l1)
    
    bce_loss = torch.nn.BCEWithLogitsLoss()
    reg_losses = defaultdict(lambda: torch.tensor(0.0))
    for regularization in real_pred_ys:
        real_y, pred_y = real_pred_ys[regularization]
        reg_losses[regularization] = bce_loss(pred_y, real_y)

    return loss_l2 + loss_l1 + torch.sum(torch.tensor(list(reg_losses.values()))), loss_l2, loss_l1, reg_losses


def exact_match(pred, real, ignore_index=1):
    '''
    Evaluate percent exact match between predictions and ground truth
    '''
    mask = real != ignore_index
    return torch.sum((pred == real) * mask).item() / torch.sum(mask).item()