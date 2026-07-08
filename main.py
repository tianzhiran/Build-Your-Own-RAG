#------------RAG 1--------------
# from openai import OpenAI

# client = OpenAI(
#     api_key="ecbbdbfb23fc48c81e8096dd23cc2003:YmMyNjRkMTBjNGQ1NDFlYjdjMTEwODk1",
#     base_url="https://maas-api.cn-huabei-1.xf-yun.com/v2"
# )


# # Step1 用户输入

# question = input("请输入你的问题：")

# # Step2 读取知识库

# with open("knowledge.txt", "r", encoding="utf-8") as f:
#     knowledge = f.read()

# # Step3 构造 Prompt

# prompt = f"""
# 你是一名武汉旅游专家。

# 请严格根据知识库回答问题。

# 知识库：

# {knowledge}

# 用户问题：

# {question}

# 如果知识库中没有相关内容，请回答：

# 知识库中暂无相关信息。
# """

# print(prompt)

# # Step4 调用模型

# response = client.chat.completions.create(
#     model="xop3qwen1b7",
#     messages=[
#         {
#             "role": "user",
#             "content": prompt
#         }
#     ]
# )

# print("\nAI回答：")
# print(response.choices[0].message.content)



# ------------RAG 2--------------

# # 读取知识库

# with open("knowledge.txt", "r", encoding="utf-8") as f:
#     knowledge = f.readlines()

# # 用户输入

# question = input("请输入你的问题：")

# # 存储检索结果

# retrieved_docs = []

# # 遍历知识库

# for doc in knowledge:

#     # 判断是否相关

#     if any(word in doc for word in question):

#         # 保存相关知识

#         retrieved_docs.append(doc)

# # 打印检索结果

# print("\n检索结果：")

# print(retrieved_docs)

# ------------RAG 3.5--------------


# 读取知识库
with open("knowledge.txt", "r", encoding="utf-8") as f:
    knowledge = f.readlines()

knowledge = [
    doc.strip()
    for doc in knowledge
    if doc.strip()
]

print(knowledge)

from sentence_transformers import SentenceTransformer

model = SentenceTransformer(
    'paraphrase-multilingual-MiniLM-L12-v2'
)

embeddings = model.encode(knowledge)
print(embeddings.shape)
print(embeddings[0])

import faiss
import numpy as np

dimension = embeddings.shape[1]
index = faiss.IndexFlatL2(dimension)
index.add(np.array(embeddings))

question = input("请输入问题：")
question_embedding = model.encode([question])

D, I = index.search(
    np.array(question_embedding),
    k = 2
)

print(I)

retrieved_docs = []

for idx in I[0]:

    retrieved_docs.append(
        knowledge[idx]
    )

print("\n检索结果：")

for doc in retrieved_docs:
    print(doc)

context = "\n".join(retrieved_docs)

prompt = f"""
你是一名武汉旅游助手。

请严格根据下面提供的知识回答问题。

知识：

{context}

用户问题：

{question}

如果知识库中没有答案，请回答：

"知识库中暂无相关信息。"
"""

print("\n========== Prompt ==========\n")
print(prompt)

from openai import OpenAI

client = OpenAI(
    api_key="ecbbdbfb23fc48c81e8096dd23cc2003:YmMyNjRkMTBjNGQ1NDFlYjdjMTEwODk1",
    base_url="https://maas-api.cn-huabei-1.xf-yun.com/v2"
)

response = client.chat.completions.create(
    model="xop3qwen1b7",
    messages=[
        {
            "role": "user",
            "content": prompt
        }
    ]
)
answer = response.choices[0].message.content

print("\n========== Final Answer ==========\n")

print(answer)