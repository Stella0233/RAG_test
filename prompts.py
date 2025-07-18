class Prompts:

    ANSWER_WITH_CONTEXT = """You are an assistant that answers questions based on the provided context.
    Question: {question}
    Context: {context}
    """



    ANSWER_WITHOUT_CONTEXT = """
    You are a knowledgable professor,limit your answer with in 200 words, please answer the question:
    """



    JUDGE_ANSWER = """
    Your task is to trace the accurate original sentence in the given context that serves as the basis for the provided answer.
    Question: {question}
    Answer: {answer}
    """



    TRACE = """
    Your task is to trace the accurate original sentence in the given context that serves as the basis for the provided answer.
    Answer: {answer}
    Context: {context}
    To trace the original sentence, you should:
    1. Analyze the key information in the answer.
    2. Search for sentences in the context that contain the same or highly relevant key information.
    3. Select the sentence that most accurately matches the answer as the original sentence, and return the sentence.
    """

