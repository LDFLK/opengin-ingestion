from app.agents.orchestrator import Agent0

def main():
    agent0 = Agent0()
    pipeline_name = "test_run"
    input_file = "data/simple.pdf"
    
    print(f"Creating pipeline: {pipeline_name}")
    try:
        agent0.create_pipeline(pipeline_name, input_file, "simple.pdf")
        
        print("Running pipeline...")
        agent0.run_pipeline(pipeline_name, prompt="Extract all tables found in the document.")
        
        print("Pipeline execution completed successfully.")
        
    except Exception as e:
        print(f"Pipeline failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
