from transformers import GPT2Tokenizer, GPT2LMHeadModel, Trainer, TrainingArguments
import glob

def preprocess_data():
    combined_data = ""
    for file in glob.glob("travel_data_*.md"):
        with open(file, "r") as f:
            combined_data += f.read()
    return combined_data

def train_model():
    tokenizer = GPT2Tokenizer.from_pretrained('gpt2')
    model = GPT2LMHeadModel.from_pretrained('gpt2')

    # Prepare dataset
    data = preprocess_data()
    # Tokenize and format data (simplified for this example)
    inputs = tokenizer(data, return_tensors='pt', max_length=512, truncation=True)

    # Fine-tune
    training_args = TrainingArguments(
        output_dir='./results',
        num_train_epochs=1,
        per_device_train_batch_size=2,
        save_steps=10_000,
        save_total_limit=2,
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=inputs,
    )

    trainer.train()

# Schedule weekly training
schedule.every().week.at("02:00").do(train_model)

while True:
    schedule.run_pending()
    time.sleep(1)