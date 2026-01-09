from pydantic import BaseModel, Field
from typing import Optional, Annotated
from langchain_core.messages import AnyMessage, HumanMessage
from langgraph.graph.message import add_messages
from models.output_model import BillingOutputModel
from models.utilities_bill_model import GeneralModel
from models.general_model2 import UnifiedBillModel

class State2(BaseModel):
    messages: Optional[Annotated[list[AnyMessage], add_messages]] = Field(
        None, description="The response from the LLM after processing the parsed text."
    )
    output_model: Optional[UnifiedBillModel] = Field(
        None, description="The structured output model parsed from the LLM response."
    )
    user_input: Optional[Annotated[list[HumanMessage], add_messages]] = Field(None, description="The input provided by the user to initiate the process.")
    pdf_document: Optional[bytes | str] = Field(None, description="The PDF document to be processed.")
    parsed_text: Optional[str] = Field(None, description="The extracted text from the PDF document.")
    structured_text_for_embeddings: Optional[str] = Field(None, description="The structured text prepared for embedding generation.")
    metadata: Optional[dict] = Field(None, description="Metadata associated with the structured text for embeddings.")
    type_of_bill: Optional[str] = Field(None, description="The type of the bill determined after analysis.")
