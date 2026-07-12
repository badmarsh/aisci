import time

def mock_serverless_function(task_name, duration):
    """
    Mocks a function executed remotely on a FaaS platform (like AWS Lambda, funcX, or Globus Compute).
    """
    print(f"  [Serverless Node] Executing {task_name}...")
    time.sleep(duration)
    return f"{task_name} completed successfully."

def orchestrate_workflow():
    """
    Demonstrates orchestrating multiple tasks seamlessly without a monolithic batch scheduler (Slurm).
    In reality:
    from funcx import FuncXClient
    fxc = FuncXClient()
    func_uuid = fxc.register_function(mock_serverless_function)
    res = fxc.run("Task A", 1, endpoint_id=my_endpoint, function_id=func_uuid)
    """
    print("Starting Serverless Orchestration (funcX/FaaS)...")
    
    tasks = [
        {"name": "Data Preprocessing", "time": 0.5},
        {"name": "Feature Extraction", "time": 0.8},
        {"name": "Model Inference", "time": 1.2}
    ]
    
    results = []
    # Mocking async submission
    print("Submitting tasks to distributed endpoints...")
    for t in tasks:
        # In FaaS, these would run completely parallel across heterogeneous hardware
        res = mock_serverless_function(t["name"], t["time"])
        results.append(res)
        
    print("\nAll tasks aggregated:")
    for r in results:
        print(" ->", r)
        
    print("\nThis replaces monolithic Slurm batch scripts with dynamic, portable task routing.")

def main():
    orchestrate_workflow()

if __name__ == "__main__":
    main()
