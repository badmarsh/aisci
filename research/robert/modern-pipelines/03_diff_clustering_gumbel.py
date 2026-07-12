import torch
import torch.nn as nn
import torch.nn.functional as F

class DifferentiableClustering(nn.Module):
    """
    Replaces discrete rules (like Anti-kT) with a differentiable assignment 
    using the Gumbel-Softmax trick.
    """
    def __init__(self, feature_dim, num_clusters=3):
        super().__init__()
        self.num_clusters = num_clusters
        # Network predicting cluster assignment logits for each particle
        self.assignment_net = nn.Sequential(
            nn.Linear(feature_dim, 32),
            nn.ReLU(),
            nn.Linear(32, num_clusters)
        )
        
    def forward(self, particles, tau=1.0, hard=False):
        """
        particles: (batch_size, num_particles, feature_dim)
        Returns cluster assignments and cluster centers.
        """
        # (batch_size, num_particles, num_clusters)
        logits = self.assignment_net(particles)
        
        # Gumbel-Softmax allows gradients to flow through discrete-like assignments
        assignments = F.gumbel_softmax(logits, tau=tau, hard=hard, dim=-1)
        
        # Calculate cluster centers as weighted sum of particles
        # assignments: (B, N, K) -> (B, K, N)
        # particles: (B, N, D)
        weights = assignments.transpose(1, 2)
        # Normalize weights
        weights = weights / (weights.sum(dim=-1, keepdim=True) + 1e-8)
        
        centers = torch.bmm(weights, particles) # (B, K, D)
        return assignments, centers

def main():
    print("Initializing Differentiable Jet Clustering Scaffold...")
    batch_size, num_particles, feature_dim = 16, 50, 4 # (E, px, py, pz)
    
    # Synthetic particle kinematics
    particles = torch.randn(batch_size, num_particles, feature_dim)
    
    model = DifferentiableClustering(feature_dim, num_clusters=4)
    optimizer = torch.optim.Adam(model.parameters(), lr=0.01)
    
    for epoch in range(100):
        optimizer.zero_grad()
        # forward pass with annealing temperature
        tau = max(0.5, 2.0 * (0.95 ** epoch))
        assignments, centers = model(particles, tau=tau, hard=False)
        
        # Dummy loss: e.g. minimize intra-cluster variance (K-means like)
        # B x N x K x D
        expanded_particles = particles.unsqueeze(2).expand(-1, -1, 4, -1)
        expanded_centers = centers.unsqueeze(1).expand(-1, 50, -1, -1)
        
        dist_sq = ((expanded_particles - expanded_centers)**2).sum(dim=-1)
        # Weight by assignments
        loss = (assignments * dist_sq).sum(dim=(1, 2)).mean()
        
        loss.backward()
        optimizer.step()
        
        if epoch % 20 == 0:
            print(f"Epoch {epoch:3d} | Tau: {tau:.2f} | Clustering Loss: {loss.item():.4f}")

if __name__ == "__main__":
    main()
