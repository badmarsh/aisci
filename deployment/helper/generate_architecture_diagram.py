import matplotlib.pyplot as plt
import matplotlib.patches as patches
import os

def create_architecture_diagram(output_dir):
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Hide axes
    ax.axis('off')
    
    # Define colors
    agent_color = '#e3f2fd'
    tool_color = '#f3e5f5'
    data_color = '#e8f5e9'
    border_color = '#1565c0'
    
    # Add nodes (x, y, width, height, text, color)
    nodes = {
        'deerflow': (0.35, 0.75, 0.3, 0.15, 'DeerFlow Orchestrator\n(Agent Coordination)', agent_color),
        'rag': (0.1, 0.45, 0.25, 0.15, 'Onyx RAG\n(Literature Retrieval)', tool_color),
        'sympy': (0.4, 0.45, 0.2, 0.15, 'SymPy\n(Symbolic Math)', tool_color),
        'minuit': (0.7, 0.45, 0.2, 0.15, 'iminuit\n(Numerical Fitting)', tool_color),
        'hepdata': (0.1, 0.15, 0.25, 0.1, 'HEPData\n(Experimental Spectra)', data_color),
        'output': (0.6, 0.15, 0.3, 0.1, 'Fitted Parameters & $\chi^2$\n(Validation Results)', data_color),
    }
    
    for key, (x, y, w, h, text, color) in nodes.items():
        rect = patches.Rectangle((x, y), w, h, linewidth=2, edgecolor=border_color, facecolor=color, alpha=0.9, zorder=2)
        ax.add_patch(rect)
        ax.text(x + w/2, y + h/2, text, ha='center', va='center', fontsize=12, fontweight='bold', zorder=3)
        
    # Add arrows
    arrows = [
        # DeerFlow to RAG
        (0.35, 0.825, 0.225, 0.6, 'Queries'),
        (0.225, 0.6, 0.35, 0.825, 'Context'),
        # DeerFlow to SymPy
        (0.5, 0.75, 0.5, 0.6, 'Formulas'),
        (0.5, 0.6, 0.5, 0.75, 'Derivations'),
        # DeerFlow to Minuit
        (0.65, 0.825, 0.8, 0.6, 'Models'),
        (0.8, 0.6, 0.65, 0.825, 'Fits'),
        # HEPData to RAG
        (0.225, 0.25, 0.225, 0.45, 'Data'),
        # Minuit to Output
        (0.8, 0.45, 0.8, 0.25, 'Results')
    ]
    
    for (x1, y1, x2, y2, label) in arrows:
        ax.annotate(label, xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle="->", color='#333333', lw=2),
                    ha='center', va='center', fontsize=10, bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="none", alpha=0.8), zorder=1)

    plt.title('AiSci Multi-Agent System Architecture', fontsize=16, fontweight='bold', pad=20)
    plt.tight_layout()
    
    # Save outputs
    os.makedirs(output_dir, exist_ok=True)
    plt.savefig(os.path.join(output_dir, 'architecture_diagram.pdf'), dpi=300, bbox_inches='tight')
    plt.savefig(os.path.join(output_dir, 'architecture_diagram.png'), dpi=300, bbox_inches='tight')
    plt.close()

if __name__ == '__main__':
    create_architecture_diagram('/home/ubuntu/aisci/thesis/figures')
