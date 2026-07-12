import torch
import torch.nn as nn
import torch.optim as optim

class VectorFieldNetwork(nn.Module):
    """A minimal neural network to estimate the vector field (velocity) for flow matching."""
    def __init__(self, dim=2):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(dim + 1, 64),
            nn.GELU(),
            nn.Linear(64, 64),
            nn.GELU(),
            nn.Linear(64, dim)
        )
        
    def forward(self, x, t):
        # x is (batch, dim), t is (batch, 1)
        t_expanded = t.expand(-1, 1)
        xt = torch.cat([x, t_expanded], dim=-1)
        return self.net(xt)

def main():
    print("Initializing Flow Matching FastSim Scaffold...")
    
    # 1. Generate target data (e.g. realistic physical distribution)
    batch_size = 256
    target_data = torch.randn(batch_size, 2) * 0.5 + 2.0  # Gaussian at (2,2)
    
    # 2. Source distribution (Standard Normal)
    source_data = torch.randn(batch_size, 2)
    
    model = VectorFieldNetwork(dim=2)
    optimizer = optim.Adam(model.parameters(), lr=1e-3)
    
    print("Starting training loop...")
    # Training Loop (Minimal Flow Matching loss)
    for epoch in range(500):
        optimizer.zero_grad()
        
        # Sample random time points t ~ U(0,1)
        t = torch.rand(batch_size, 1)
        
        # Linear interpolation path: x_t = (1-t)*x_0 + t*x_1
        # In FM, the target velocity v_t is (x_1 - x_0)
        x_t = (1 - t) * source_data + t * target_data
        target_velocity = target_data - source_data
        
        # Predict velocity
        pred_velocity = model(x_t, t)
        
        # Loss is MSE between predicted and target velocity
        loss = nn.functional.mse_loss(pred_velocity, target_velocity)
        loss.backward()
        optimizer.step()
        
        if epoch % 100 == 0:
            print(f"Epoch {epoch:3d} | Flow Matching Loss: {loss.item():.4f}")
            
    print("\nTraining complete! FastSim vector field is ready.")
    print("To simulate: Solve ODE dX/dt = v_theta(X, t) from t=0 to t=1 using torchdiffeq.")

if __name__ == "__main__":
    main()
