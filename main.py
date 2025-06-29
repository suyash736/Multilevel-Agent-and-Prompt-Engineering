from agent import Orchestrator

if __name__ == "__main__":
    try:
        agent = Orchestrator()
        tasks = [
            "Calculate 123 × 45 + 678",
            "Who is the president of USA",
            "Weather in Kathmandu",
            "Convert 100 USD to EUR"
        ]
        for task in tasks:
            print(f"\nTask: {task}")
            response = agent.run(task)
            print(f"Response: {response}")
    except EnvironmentError as e:
        print(f"Setup error: {str(e)}")