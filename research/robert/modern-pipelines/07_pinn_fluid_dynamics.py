import torch
import torch.nn as nn

class PINN(nn.Module):
    """
    Physics-Informed Neural Network for 1D Burgers' Equation 
    (a simplified Navier-Stokes analog).
    du/dt + u * du/dx - nu * d^2u/dx^2 = 0
    """
    def __init__(self):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(2, 20),
            nn.Tanh(),
            nn.Linear(20, 20),
            nn.Tanh(),
            nn.Linear(20, 1)
        )
        
    def forward(self, x, t):
        inputs = torch.cat([x, t], dim=1)
        return self.net(inputs)

def compute_physics_loss(model, x, t, nu=0.01 / torch.pi):
    # Enable gradients for inputs
    x.requires_grad_(True)
    t.requires_grad_(True)
    
    # Predict u(x,t)
    u = model(x, t)
    
    # Compute derivatives using autodiff
    u_t = torch.autograd.grad(u, t, grad_outputs=torch.ones_like(u), create_graph=True)[0]
    u_x = torch.autograd.grad(u, x, grad_outputs=torch.ones_like(u), create_graph=True)[0]
    u_xx = torch.autograd.grad(u_x, x, grad_outputs=torch.ones_like(u_x), create_graph=True)[0]
    
    # Burgers' equation residual
    f = u_t + u * u_x - nu * u_xx
    
    return torch.mean(f**2)

def main():
    print("Initializing PINN for Fluid Dynamics Scaffold...")
    model = PINN()
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
    
    # Collocation points inside the domain
    N_f = 1000
    x_f = torch.rand(N_f, 1) * 2 - 1 # x in [-1, 1]
    t_f = torch.rand(N_f, 1)         # t in [0, 1]
    
    # Boundary data (simplified)
    x_b = torch.tensor([[-1.0], [1.0]])
    t_b = torch.tensor([[0.5], [0.5]])
    u_b_target = torch.tensor([[0.0], [0.0]]) # Boundary conditions u(-1,t)=u(1,t)=0
    
    print("Training PINN...")
    for epoch in range(500):
        optimizer.zero_grad()
        
        # 1. Physics Loss (PDE residual)
        loss_f = compute_physics_loss(model, x_f, t_f)
        
        # 2. Data/Boundary Loss
        u_b = model(x_b, t_b)
        loss_b = torch.mean((u_b - u_b_target)**2)
        
        total_loss = loss_f + loss_b
        total_loss.backward()
        optimizer.step()
        
        if epoch % 100 == 0:
            print(f"Epoch {epoch:3d} | Total Loss: {total_loss.item():.5f} | PDE Loss: {loss_f.item():.5f}")

    print("\nTraining complete! PINN acts as a fully differentiable, fast surrogate for CFD.")

if __name__ == "__main__":
    main()
