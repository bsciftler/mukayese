git clone https://github.com/huggingface/transformers.git
cd transformers
git checkout 65659a29cf5a079842e61a63d57fa24474288998
cat summarize.py > transformers/examples/pytorch/summarization/run_summarization.py
pip install -r transformers/examples/pytorch/summarization/requirements.txt
