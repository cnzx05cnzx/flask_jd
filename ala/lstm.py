import pandas as pd
import random
import pkuseg
import torch
from torch import nn
from torchtext.legacy.data import BucketIterator, Field, TabularDataset
import torch.optim as optim
import torch.nn.functional as F


class LSTM(nn.Module):
    def __init__(self, emb_len, emb_dim, out_dim):
        super(LSTM, self).__init__()
        self.embedding = nn.Embedding(emb_len, emb_dim)
        self.lstm = nn.LSTM(emb_dim, out_dim, batch_first=True, dropout=0.5, bidirectional=True, num_layers=2)
        self.linear = nn.Sequential(
            nn.Linear(2 * out_dim, 64),
            nn.Dropout(0.3),
            nn.ReLU(),
            nn.Linear(64, 2)
        )

    def forward(self, x):
        # 初始输入格式为(length, batch_size)
        out = self.embedding(x)
        # (length, batch_size, emb) -> (batch_size, length , emb )

        out = torch.transpose(out, 0, 1)

        out, (h, c) = self.lstm(out)
        out = torch.cat((h[-2, :, :], h[-1, :, :]), dim=1)
        out = self.linear(out)

        return out


def tokenizer(text):
    return seg.cut(text)


if __name__ == "__main__":

    SEED = 721
    batch_size = 32
    learning_rate = 1e-3
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    torch.manual_seed(SEED)

    seg = pkuseg.pkuseg()

    TEXT = Field(sequential=True, tokenize=tokenizer, fix_length=125)
    LABEL = Field(sequential=False, use_vocab=False)

    FIELD = [('label', LABEL), ('content', TEXT)]

    df = TabularDataset(
        path='./data/phone.csv', format='csv',
        fields=FIELD, skip_header=True)

    TEXT.build_vocab(df, min_freq=3, vectors='glove.6B.50d')

    train, valid = df.split(split_ratio=0.7, random_state=random.seed(SEED))

    train_iter, valid_iter = BucketIterator.splits(
        (train, valid),
        batch_sizes=(batch_size, batch_size),
        device=device,
        sort_key=lambda x: len(x.content),
        sort_within_batch=False,
        repeat=False
    )
    model = LSTM(len(TEXT.vocab), 64, 128).to(device)
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)
    criterion = F.cross_entropy
    scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=20, gamma=0.5)

    # -----------------------------------模型训练--------------------------------------
    epochs = 100
    stop = 20
    cnt = 0
    best_valid_acc = float('-inf')
    model_save_path = './model/torchtext.pkl'
    for epoch in range(epochs):
        loss_one_epoch = 0.0
        correct_num = 0.0
        total_num = 0.0

        for i, batch in enumerate(train_iter):
            model.train()
            label, content = batch.label, batch.content
            # 进行forward()、backward()、更新权重
            optimizer.zero_grad()
            pred = model(content)
            loss = criterion(pred, label)
            loss.backward()
            optimizer.step()

            # 统计预测信息
            total_num += label.size(0)
            # 预测有多少个标签是预测中的，并加总
            correct_num += (torch.argmax(pred, dim=1) == label).sum().float().item()
            loss_one_epoch += loss.item()

        loss_avg = loss_one_epoch / len(train_iter)

        print("Train: Epoch[{:0>3}/{:0>3}]  Loss: {:.4f} Acc:{:.2%}".
              format(epoch + 1, epochs, loss_avg, correct_num / total_num))

        # ---------------------------------------验证------------------------------
        loss_one_epoch = 0.0
        total_num = 0.0
        correct_num = 0.0

        model.eval()
        for i, batch in enumerate(valid_iter):
            label, content = batch.label, batch.content
            pred = model(content)
            pred.detach()
            # 计算loss

            # 统计预测信息
            total_num += label.size(0)
            # 预测有多少个标签是预测中的，并加总
            correct_num += (torch.argmax(pred, dim=1) == label).sum().float().item()

        # 学习率调整
        scheduler.step()

        print('valid Acc:{:.2%}'.format(correct_num / total_num))

        # 每个epoch计算一下验证集准确率如果模型效果变好，保存模型
        if (correct_num / total_num) > best_valid_acc:
            print("超过最好模型,保存")
            best_valid_acc = (correct_num / total_num)
            torch.save(model.state_dict(), model_save_path)
            cnt = 0
        else:
            cnt = cnt + 1
            if cnt > stop:
                # 早停机制
                print("模型基本无变化，停止训练")
                print("训练集最高准确率为%.2f" % best_valid_acc)
                break
