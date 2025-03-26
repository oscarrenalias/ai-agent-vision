from agents import Orchestrator
import logging

#
# Run the orchestrator agent
#
orchestrator = Orchestrator()
orchestrator.run(receipt_image_path="data/samples/receipt_sample_1.jpg")