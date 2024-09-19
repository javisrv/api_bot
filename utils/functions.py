from langchain_openai  import ChatOpenAI

def get_model(model_type="4o-mini") -> ChatOpenAI:
    model = ChatOpenAI(model_name = model_type)
    return model