from dataclasses import dataclass


@dataclass
class ReceiptAnalyzerPrompt:
    template: str = """
       You are analyzing a Finnish grocery receipt. Your task is to extract structured information in JSON format. Please follow the rules carefully.

        Do not guess. If some information is missing just return "N/A" in the relevant field. If you determine that the image is not of a receipt, just set all the fields in the formatting instructions to "N/A".

        You must obey the output format under all circumstances. Please follow the formatting instructions exactly.
        Do not return any additional comments or explanation.

        1. List of Items
        For each line item (product), extract the following:
        - Name of the item in Finnish
        - Translated name in English
        - Unit of measure (e.g., kg, unit, pkg, box, etc.). Include it as a string. If the unit is not specified, set to null.
        - Number of units, kilos, or packages (include unit type: e.g., kg, unit, pkg, box, etc.). Only include the number, do not include the unit type.
        - Price per unit (e.g., €/kg or €/unit). Only include the number, do not include the currency or anything else.
        - Total price paid for this item before discount
        - If a discount is listed under the item (indicated by a line starting with PLUSSA-ETU), include the total discount for that item. Otherwise, set to null.
        - Include a boolean flag depending on whether a loyalty discount was applied to this item
        Lines that start with PLUSSA-TASAERÄ can be ignored.

        2. Receipt Summary
        Extract the following:
        - Total value of the items before loyalty discounts
        - Total amount saved via loyalty card discounts (PLUSSAT-EDUT YHTEENSÄ)
        - Total amount paid by the customer (including taxes)
       """
