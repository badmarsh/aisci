import torch
import torch.nn as nn

class SimpleMLIP(nn.Module):
    """
    A minimal Machine Learning Interatomic Potential (MLIP) scaffold.
    Represents message passing for predicting potential energy.
    """
    def __init__(self, num_elements=10, hidden_dim=32):
        super().__init__()
        self.embedding = nn.Embedding(num_elements, hidden_dim)
        self.interaction = nn.Sequential(
            nn.Linear(hidden_dim + 1, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim)
        )
        self.energy_head = nn.Linear(hidden_dim, 1)

    def forward(self, atomic_numbers, coordinates):
        """
        atomic_numbers: (N,)
        coordinates: (N, 3)
        """
        N = atomic_numbers.shape[0]
        # Node features
        h = self.embedding(atomic_numbers) # (N, H)
        
        # Compute pairwise distances (N, N)
        dist_matrix = torch.cdist(coordinates, coordinates)
        
        # Simple message passing: aggregate features from neighbors weighted by distance
        # Real MLIPs use spherical harmonics, cutoffs, and body-ordered tensors (like MACE)
        total_energy = 0
        for i in range(N):
            # For each atom i, gather info from all j
            messages = []
            for j in range(N):
                if i != j:
                    dist = dist_matrix[i, j].unsqueeze(0)
                    msg_in = torch.cat([h[j], dist])
                    messages.append(self.interaction(msg_in))
            if messages:
                # Sum pool messages
                m = sum(messages)
                # Update node state and predict atomic energy
                e_i = self.energy_head(h[i] + m)
                total_energy += e_i
                
        return total_energy

def main():
    print("Initializing Machine Learning Interatomic Potential Scaffold...")
    # Synthetic molecule: Water (H2O)
    atomic_numbers = torch.tensor([8, 1, 1]) # O, H, H
    # Rough geometry
    coordinates = torch.tensor([
        [0.0, 0.0, 0.0],
        [0.96, 0.0, 0.0],
        [-0.24, 0.93, 0.0]
    ], requires_grad=True) # requires_grad to compute forces!
    
    model = SimpleMLIP()
    
    # Predict Energy
    energy = model(atomic_numbers, coordinates)
    
    # Compute Forces as negative gradient of Energy wrt coordinates
    forces = -torch.autograd.grad(energy, coordinates)[0]
    
    print(f"Predicted Total Energy: {energy.item():.4f}")
    print("Predicted Atomic Forces:")
    print(forces.detach().numpy())
    print("\nThis replaces DFT calculations with fast neural-network inference!")

if __name__ == "__main__":
    main()
