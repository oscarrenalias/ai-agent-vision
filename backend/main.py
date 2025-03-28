from dotenv import load_dotenv

from agents import Orchestrator

#
# Run the orchestrator agent
#
load_dotenv()

orchestrator = Orchestrator()
orchestrator.run(receipt_image_path="../data/samples/receipt_sample_1.jpg")
