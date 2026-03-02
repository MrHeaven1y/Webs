import torch
import time
from dataclasses import dataclass, field
from torchvision import transforms as T
from torchvision import datasets
from torch.utils.data import DataLoader


@dataclass
class HYPERPARAMETERS:
    size: int = 64
    patch: int = 16
    dropout: float = 0.3
    n_layers: int = 12
    num_workers: int = 0
    batch_size: int = 128
    max_iterations: int = 80
    
    # Just assign it directly! Safe and completely bug-free.
    device: torch.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    
def load_class_mapping(filepath):
    pass

def benchmark_num_workers(batch_size, num_workers_list=[0, 2, 4, 8]):

    transform = T.Compose([
        T.Resize((64, 64)),
        T.ToTensor()
    ])

    dataset = datasets.FakeData(transform=transform)

    results = {}
    for nw in num_workers_list:
        loader = DataLoader(dataset,
                            batch_size=batch_size,
                            shuffle=True,
                            num_workers=nw,
                            pin_memory=True)
        
        start = time.time()
        for batch in loader:
            batch = batch[0].to("cuda", non_blocking=True)
        end = time.time()
        
        epoch_time = end - start
        results[nw] = epoch_time
        print(f"num_workers={nw} → epoch_time={epoch_time:.2f}s")

    sorted_results = dict(sorted(results.items(),key=lambda kv: kv[1]))

    return sorted_results

