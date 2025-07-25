class Prompts:

    ANSWER_WITH_CONTEXT = """
    You are an assistant that answers questions based on the provided context. Answer in details if necessary. Answer the question in Chinese.
    If necessary, you can refer to the history dialogue memory:
    Memory: {memory}
    
    Question: {question}
    Context: {context}
    """



    ANSWER_WITHOUT_CONTEXT = """
    You are a knowledgable professor,limit your answer with in 200 words, please answer the question in Chinese.
    If necessary, you can refer to the history dialogue memory:
    Memory: {memory}
    
    Question: {question}
    """



    JUDGE_ANSWER = """
    Your task is to trace the accurate original sentence in the given context that serves as the basis for the provided answer.
    Question: {question}
    Answer: {answer}
    """

    TRACE = """
    Your task is to identify and extract the original sentence(s) from the given context that most directly supports or corresponds to the provided answer.

    Instructions:
    1. Carefully analyze the answer, breaking it down sentence by sentence if needed.
    2. For each part of the answer, search for sentence(s) in the context that contain the same or closely related key information, facts, or reasoning.
    3. If no exact matches are found, look for sentences that are logically connected to the answer’s content and could reasonably serve as its basis.
    4. Return only the sentence(s) from the context that best align with the answer. Each sentence should be on a separate line.
    5. Do **not** include any explanation, commentary, or extra output—only the matched sentence(s) from the context.

    Answer:
    {answer}

    Context:
    {context}
    """

    REWRITE_PROMPT = """
    You are a helpful assistant that reformulates user questions to be well-formed, clear, and specific — without changing their meaning.
    Rewrite the question in Chinese.
    
    Instructions:
    - Keep the rewritten question as a **single question**.
    - Do not split, add or infer new information.
    - Just clarify ambiguous expressions and correct grammar.
    - Output only the rewritten question, no explanations.
    
    User question: {question}
    Rewritten question:
    """

    STYLIZE_PROMPT = """
    请将以下内容润色为一篇符合中国公文写作风格的文稿，语言应庄重、规范，结构，避免口语化表达。禁止改变内容原意。

    要求：
    - 语言准确、条理清晰，使用正式书面语
    - 可使用编号条目（如“一、二、三”）列出具体条目
    
    原始内容：
    {answer}
    
    请输出风格化后的公文内容，不要添加解释说明。
    """

