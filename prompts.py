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



    REWRITE_PROMPT = """
    You are a helpful assistant that reformulates user questions to be well-formed, clear, and specific — without changing their meaning.
    
    Instructions:
    - Keep the rewritten question as a **single question**.
    - Do not split, add or infer new information.
    - Just clarify ambiguous expressions and correct grammar.
    - Output only the rewritten question, no explanations.
    
    User question: {question}
    Rewritten question:
    """

    STYLIZE_PROMPT = """
    请将以下内容润色为一篇符合中国公文写作风格的通知类文稿，语言应庄重、规范，结构应包括背景说明、工作要求和结语，避免口语化表达。

    要求：
    - 使用“为了……”、“根据……”、“现就……事项通知如下”等句式
    - 语言准确、条理清晰，使用正式书面语
    - 可使用编号条目（如“一、二、三”）列出具体措施
    - 结尾处用“请予以贯彻执行”或“特此通知”等表达
    
    原始内容：
    {answer}
    
    请输出风格化后的公文内容，不要添加解释说明。
    """

