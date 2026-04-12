from transformers import pipeline

# Load the pre-trained model from Hugging Face
# This will automatically download the model the first time you run it.
classifier = pipeline("text-classification", model="mitulshah/global-financial-transaction-classifier")

# --- Test it with some Indian transaction descriptions ---
transactions = [
    "Flipkart - OnePlus Mobile",
    "Zomato Order - Biryani",
    "Ola Ride to Airport",
    "Big Bazaar Grocery Shopping"
]

print("--- Classification Results ---")
for transaction in transactions:
    result = classifier(transaction)
    # The model returns a list of dictionaries, e.g., [{'label': 'SHOPPING & RETAIL', 'score': 0.99}]
    predicted_label = result[0]['label']
    confidence = result[0]['score']
    print(f"Transaction: '{transaction}'")
    print(f"--> Category: {predicted_label} (Confidence: {confidence:.2f})")
    print("-" * 30)