from app.agents.orchestrator import Agent0


def main():
    agent0 = Agent0()
    pipeline_name = "test_run"
    input_file = "data/simple.pdf"

    print(f"Creating pipeline: {pipeline_name}")
    try:
        run_id, metadata = agent0.create_pipeline(pipeline_name, input_file, "simple.pdf")
        print(f"Created run: {run_id}")

        print("Running pipeline...")
        prompt = """
        Extract all tables from this document.

        The document is a PDF file containing tables.
        Look for the top of the page where it says the name of the minister.
        Based on that name you must make sure the aggregation logic make sure
        that the same name ministers would be saved to the same file.
        Also please note that a ,minister table can spread through multiple pages.
        """
        agent0.run_pipeline(pipeline_name, run_id, prompt=prompt)

        print("Pipeline execution completed successfully.")

    except Exception as e:
        print(f"Pipeline failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
