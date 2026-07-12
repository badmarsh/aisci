from database import get_stats

def print_dashboard():
    stats = get_stats()

    print("=" * 40)
    print("🚀 IGNITION MISSION: INTAKE DASHBOARD 🚀")
    print("=" * 40)
    print(f"📄 Total Papers Ingested:      {stats['papers']}")
    print(f"💡 Total Claims Extracted:     {stats['claims']}")
    print(f"⚔️  Total Contradictions Found: {stats['contradictions']}")
    print("=" * 40)

if __name__ == '__main__':
    print_dashboard()
