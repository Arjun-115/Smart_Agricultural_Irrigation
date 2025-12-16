from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

# Small model, CPU-friendly
model_name = "google/flan-t5-large"  # ~1.5GB, can switch to 'flan-t5-small' for ~250MB

tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

def chat(prompt, max_length=150):
    inputs = tokenizer(prompt, return_tensors="pt")
    outputs = model.generate(**inputs, max_length=max_length)
    return tokenizer.decode(outputs[0], skip_special_tokens=True)

# Example usage
if __name__ == "__main__":
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            break
        response = chat(user_input)
        print(f"Bot: {response}")
