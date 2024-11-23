import torch
import re
import concurrent.futures


def calculate_credits_pytorch(messages):
    # Base Cost: 1 credit per message
    base_cost = torch.ones(len(messages))

    # Character Count: Add 0.05 credits per character
    char_count = torch.tensor([len(message) for message in messages], dtype=torch.float32)
    char_cost = char_count * 0.05

    # Word Length Multipliers
    words_list = [re.findall(r"\b\w+\b", message) for message in messages]
    word_costs = []
    for words in words_list:
        word_cost = 0.0
        for word in words:
            if 1 <= len(word) <= 3:
                word_cost += 0.1
            elif 4 <= len(word) <= 7:
                word_cost += 0.2
            elif len(word) >= 8:
                word_cost += 0.3
        word_costs.append(word_cost)
    word_cost = torch.tensor(word_costs, dtype=torch.float32)

    # Third Vowels: Add 0.3 credits for each third vowel
    vowels = "aeiouAEIOU"
    third_vowel_counts = [
        sum(1 for i, c in enumerate(message, 1) if c in vowels and i % 3 == 0)
        for message in messages
    ]
    vowel_cost = torch.tensor(third_vowel_counts, dtype=torch.float32) * 0.3

    # Length Penalty: If message length exceeds 100 characters, add 5 credits
    length_penalty = torch.tensor([5.0 if len(message) > 100 else 0.0 for message in messages], dtype=torch.float32)

    # Unique Word Bonus: Subtract 2 credits if all words are unique
    unique_word_bonus = torch.tensor([
        -2.0 if len(words) == len(set(words)) else 0.0
        for words in words_list
    ], dtype=torch.float32)

    # Calculate total cost and ensure minimum cost of 1 credit
    total_cost = base_cost + char_cost + word_cost + vowel_cost + length_penalty + unique_word_bonus
    total_cost = torch.maximum(total_cost, torch.tensor(1.0))

    # Palindrome: If message is a palindrome, double the total cost
    cleaned_texts = [re.sub(r"[^a-zA-Z0-9]", "", message).lower() for message in messages]
    is_palindrome = torch.tensor([1.0 if text == text[::-1] else 0.0 for text in cleaned_texts], dtype=torch.float32)
    total_cost *= (1 + is_palindrome)

    return total_cost.tolist()



def calculate_credits_batch_pytorch(messages, batch_size=100):
    def process_message_batch(batch):
        return calculate_credits_pytorch(batch)

    results = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        batches = [messages[i:i + batch_size] for i in range(0, len(messages), batch_size)]
        for batch_result in executor.map(process_message_batch, batches):
            results.extend(batch_result)
    return results