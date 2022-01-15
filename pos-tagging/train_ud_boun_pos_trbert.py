import torch, flair
import sys
from tqdm import tqdm

from flair.datasets import UniversalDependenciesCorpus, XTREME
from flair.embeddings import TransformerWordEmbeddings
from flair.models import SequenceTagger
from flair.trainers import ModelTrainer
from flair.data import Corpus
from flair.datasets import ColumnCorpus

from torch.optim.lr_scheduler import OneCycleLR

tag_type = "upos"

data_f = sys.argv[1]

corpus = UniversalDependenciesCorpus(
    data_folder=data_f,
    train_file='tr_boun-ud-train.conllu',
    dev_file='tr_boun-ud-dev.conllu',
    test_file='tr_boun-ud-test.conllu'
)

tag_dictionary = corpus.make_tag_dictionary(tag_type)

hf_model = 'dbmdz/bert-base-turkish-cased'
embeddings = TransformerWordEmbeddings(
    model=hf_model,
    layers="-1",
    subtoken_pooling="first",
    fine_tune=True,
    use_context=False,
    respect_document_boundaries=False,
)

tagger: SequenceTagger = SequenceTagger(
            hidden_size=256,
            embeddings=embeddings,
            tag_dictionary=tag_dictionary,
            tag_type=tag_type,
            use_crf=False,
            use_rnn=False,
            reproject_embeddings=False,
        )

# init the model trainer
trainer = ModelTrainer(tagger, corpus, optimizer=torch.optim.AdamW)

output_folder = output_folder = f"flert-UD_Turkish-BOUN-{hf_model.replace('/', '.' ) }"


trainer.train(
    output_folder,
    learning_rate=5.0e-5,
    mini_batch_size=16,
    mini_batch_chunk_size=1,
    max_epochs=10,
    scheduler=OneCycleLR,
    embeddings_storage_mode='none',
    weight_decay=0.,
    train_with_dev=False,
    save_model_at_each_epoch=True
)


tagger = SequenceTagger.load( output_folder + '/' + 'final-model.pt' )

def sent_to_label( sent ):
    predictions = []
    for t in sent.tokens:
        predictions.append( t.get_labels()[1].value )
      
    return predictions


all_predictions = []
for t in tqdm( corpus.test ):
    tagger.predict( t )
    predictions = sent_to_label( t )
    all_predictions.append( predictions )
    

import json
data = {}
data['predictions'] = all_predictions

    
import json
with open('bert-pos-predictions.json', 'w') as f:
    json.dump(data, f)
    
    
