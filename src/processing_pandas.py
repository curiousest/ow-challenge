import pandas as pd
import re


def calculate_credits_pandas(message_texts):
    df = pd.DataFrame({'message_text': message_texts})

    # Base Cost: 1 credit per message
    df['base_cost'] = 1.0

    # Character Count: Add 0.05 credits per character
    df['char_count'] = df['message_text'].apply(len)
    df['char_cost'] = df['char_count'] * 0.05

    # Word Length Multipliers
    df['words'] = df['message_text'].apply(lambda x: re.findall(r"\b\w+\b", x))
    df['word_cost'] = df['words'].apply(lambda words: sum(0.1 if 1 <= len(word) <= 3 else 0.2 if 4 <= len(word) <= 7 else 0.3 for word in words))

    # Third Vowels: Add 0.3 credits for each third vowel
    vowels = "aeiouAEIOU"
    df['third_vowel_count'] = df['message_text'].apply(lambda x: sum(1 for i, c in enumerate(x, 1) if c in vowels and i % 3 == 0))
    df['vowel_cost'] = df['third_vowel_count'] * 0.3

    # Length Penalty: If message length exceeds 100 characters, add 5 credits
    df['length_penalty'] = df['char_count'].apply(lambda x: 5.0 if x > 100 else 0.0)

    # Unique Word Bonus: Subtract 2 credits if all words are unique
    df['unique_word_bonus'] = df['words'].apply(lambda words: -2.0 if len(words) == len(set(words)) else 0.0)

    # Calculate total cost and ensure minimum cost of 1 credit
    df['total_cost'] = df[['base_cost', 'char_cost', 'word_cost', 'vowel_cost', 'length_penalty', 'unique_word_bonus']].sum(axis=1)
    df['total_cost'] = df['total_cost'].apply(lambda x: max(x, 1.0))

    # Palindrome: If message is a palindrome, double the total cost
    df['cleaned_text'] = df['message_text'].apply(lambda x: re.sub(r"[^a-zA-Z0-9]", "", x).lower())
    df['is_palindrome'] = df['cleaned_text'].apply(lambda x: x == x[::-1])
    df['total_cost'] = df.apply(lambda row: row['total_cost'] * 2 if row['is_palindrome'] else row['total_cost'], axis=1)

    return df['total_cost'].tolist()


def calculate_credits_batch_pandas(messages, batch_size=100):
    results = []
    for i in range(0, len(messages), batch_size):
        batch = messages[i:i + batch_size]
        results.extend(calculate_credits_pandas(batch))
    return results