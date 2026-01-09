from langgraph.graph import StateGraph
from langgraph.types import Command
from typing import Literal
from state.state import State2 as AgentState
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os
from langchain_community.document_loaders import UnstructuredPDFLoader
from langchain_text_splitters import CharacterTextSplitter
from models.bill_type_model import BillTypeModel
from models.utilities_bill_model import GeneralModel
from langgraph.graph import START, END
from langchain_core.messages import ToolMessage
import chromadb
from system_prompt import SYSTEM_PROMPT
from langgraph.checkpoint.memory import InMemorySaver
from chromadb import K, Search
from models.general_model2 import UnifiedBillModel
from models.vendor_output import VendorOutput
load_dotenv()

class ReceiptAgent():
    def __init__(self):
        self.sml_Model = ChatGroq(model="meta-llama/llama-4-scout-17b-16e-instruct", temperature=0, api_key=os.getenv("GROQ_KEY"))
        self.llama_model = ChatGroq(model="llama-3.1-8b-instant", temperature=0, api_key=os.getenv("GROQ_KEY"))
        self.graph = self.create_graph()
        self.chroma_client = chromadb.CloudClient(
            api_key=os.getenv("CHROMA_DB_KEY"),
            tenant=os.getenv("CHROMA_DB_TENANT"),
            database='Recipets'
            )
        self.text_splitter = CharacterTextSplitter(
            separator="\n\n",
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            is_separator_regex=False,
        )

    def document_parser(self, state: AgentState) -> AgentState:
        document = state.pdf_document
        loader = UnstructuredPDFLoader(document)
        text_document = loader.load()
       
        return {
            "messages": [ToolMessage(tool_call_id="0", content="PDF document parsed successfully.")],
            "parsed_text": text_document[0].page_content
        }
    
    def document_type_checker(self, state: AgentState) -> AgentState:
        content = state.parsed_text[:2000]
        prompt = f"Check the type of the following bill based on its content {content}"
        response = self.llama_model.with_structured_output(BillTypeModel).invoke(prompt)
        return {
            "messages": [ToolMessage(tool_call_id="1", content="PDF document type checked successfully.")],
            "parsed_text": state.parsed_text,
            "type_of_bill": response.bill_type
        }

    def chunk_splitter(self, state: AgentState) -> AgentState:
        doc_type = state.type_of_bill
        content = state.parsed_text
        if doc_type.upper() == "GAS" or doc_type.upper() == "ELECTRICITY":
            text_document = state.parsed_text
            texts = self.text_splitter.create_documents([text_document])
            content = f"{texts[7]} \n {texts[8]}"
            
        return {
                "messages": [ToolMessage(tool_call_id="2", content="Document chunked successfully.")],
                "parsed_text": content
            }

    
    def llm_reasoner(self, state: AgentState) -> AgentState:

        llm = self.sml_Model.with_structured_output(UnifiedBillModel)
        prompt = f"{SYSTEM_PROMPT}\n\n{state.parsed_text}"
        response = llm.invoke(prompt)
        print("LLM Response: --------- ", response)
        return {
            "output_model": response,
            "messages": [ToolMessage(tool_call_id="3", content=str(response))]
        }
    
    def tranform_data_for_embeddings(self, state: AgentState) -> AgentState:
        
        structured_data = state.output_model
        print("Structured Data from LLM:", structured_data)
        structured_text_input = f""
        vendor_name = structured_data.vendor_name
        bill_type = structured_data.type_of_bill
        total_amount = structured_data.total_amount
        due_date = structured_data.due_date if structured_data.due_date is not None else "N/A"
        structured_text_input += f"\nVendor Name: {vendor_name}\nTotal Amount: {total_amount}\nDue Date: {due_date}\nBill Type: {bill_type}\nItems:\n"
        for item in structured_data.items:
            product_name = item.product_name
            quantity = item.quantity
            unit_price = item.unit_price
            total_price = item.total_price
            structured_text_input += f"Product Name: {product_name}, Quantity: {quantity}, Unit Price: {unit_price}, Total Price: {total_price}\n"
            if item.subitems is not None:
                for subitem in item.subitems:
                    subitem_name = subitem.name
                    subitem_quantity = subitem.quantity if subitem.quantity is not None else 0
                    subitem_unit_price = subitem.unit_price if subitem.unit_price is not None else 0
                    subitem_total_price = subitem.total_price
                    structured_text_input += f"Sub product Name: {subitem_name}, Quantity: {subitem_quantity}, Unit Price: {subitem_unit_price}, Total Price: {subitem_total_price}\n"
        metadata = {
            "vendor_name": vendor_name,
            "total_amount": total_amount,
            "due_date": due_date,
            "id": f"{vendor_name}_{structured_data.bill_date}_{total_amount}"
        }
        return {
            "messages": [ToolMessage(tool_call_id="4", content="Structured text prepared for embeddings.")],
            "structured_text_for_embeddings": structured_text_input,
            "metadata": metadata
        }

    def save_to_chromaDB(self, state: AgentState) -> AgentState:
        text = state.structured_text_for_embeddings
        metadata = state.metadata
        collection = self.chroma_client.get_or_create_collection(name="invoices")
        collection.add(documents=[text], metadatas=[metadata], ids=[metadata["id"]])
        return {
            "messages": [ToolMessage(tool_call_id="5", content="Document saved to ChromaDB successfully.")]
        }

    def intent_recognizer(self, state: AgentState) -> Command[Literal["Document Parser", "Query Handler"]]:
        pdf = state.pdf_document
        goto = None
        if pdf is None:
            goto = "Query Handler"
        else:
            goto =  "Document Parser"

        return Command(
            update=AgentState(messages=[ToolMessage(tool_call_id="intent_recognizer", content=f"Routing to {goto} based on user input.")]),
            goto=goto
        )
    
    def query_handler(self, state: AgentState) -> AgentState:
        user_messages = state.user_input
        llm = self.llama_model.with_structured_output(VendorOutput)
        llm_prompt = "Extract the vendor name from the following user query:\n" + user_messages[-1].content
        response = llm.invoke(llm_prompt)
        vendor_name = response.vendor_name.upper()

        collection = self.chroma_client.get_or_create_collection(name="invoices")
        search = Search().where(K.DOCUMENT.contains(vendor_name))
        results = collection.search(search)

        rows = results.rows()[0]
        print("Search Results: ", rows)
        print(rows[0]['document'])
        return{
            "messages": [ToolMessage(tool_call_id="query_handler", content=f"Found {len(rows)} documents matching the query.")],
            
        }
        


    def create_graph(self) -> StateGraph:
        state_graph = StateGraph(AgentState)
        state_graph.add_node("Intent Recognizer", self.intent_recognizer)
        state_graph.add_node("Query Handler", self.query_handler)
        state_graph.add_node("Document Parser", self.document_parser)
        state_graph.add_node("Document Type Checker", self.document_type_checker)
        state_graph.add_node("Chunk Splitter", self.chunk_splitter)
        state_graph.add_node("LLM Reasoner", self.llm_reasoner)
        state_graph.add_node("Transform Data for Embeddings", self.tranform_data_for_embeddings)
        state_graph.add_node("Save to ChromaDB", self.save_to_chromaDB)

        state_graph.add_edge(START, "Intent Recognizer")
        
        state_graph.add_edge("Document Parser", "Document Type Checker")
        state_graph.add_edge("Document Type Checker", "Chunk Splitter")
        state_graph.add_edge("Chunk Splitter", "LLM Reasoner")
        state_graph.add_edge("LLM Reasoner", "Transform Data for Embeddings")
        state_graph.add_edge("Transform Data for Embeddings", "Save to ChromaDB")
        state_graph.add_edge("Save to ChromaDB", END)

        return state_graph.compile(checkpointer=InMemorySaver())