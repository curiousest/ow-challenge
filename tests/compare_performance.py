import time
from src.processing_pytorch import calculate_credits_batch_pytorch
from src.processing_pandas import calculate_credits_batch_pandas

if __name__ == "__main__":

    # Performance comparison script
    # Generate synthetic data
    num_messages = 10000
    messages = ["This is a synthetic message number " + str(i) for i in range(num_messages)]

    # Measure performance for PyTorch
    start_time = time.time()
    calculate_credits_batch_pytorch(messages)
    pytorch_duration = time.time() - start_time

    # Measure performance for Pandas
    start_time = time.time()
    calculate_credits_batch_pandas(messages)
    pandas_duration = time.time() - start_time

    print(f"PyTorch Duration: {pytorch_duration:.2f} seconds")
    print(f"Pandas Duration: {pandas_duration:.2f} seconds")