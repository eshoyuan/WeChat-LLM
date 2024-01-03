# Constants
from llama_index.indices.postprocessor import MetadataReplacementPostProcessor, SentenceTransformerRerank
from llama_index.prompts import ChatPromptTemplate
from llama_index.llms import OpenAI, ChatMessage, MessageRole
from llama_index import Document, ServiceContext, VectorStoreIndex
from llama_index.node_parser import SentenceWindowNodeParser
import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"
MODEL = "gpt-4-1106-preview"
TEMPERATURE = 0.1
EMBED_MODEL = "local:BAAI/bge-small-zh-v1.5"
WINDOW_SIZE = 10
FILE_PATH = "./data/chat.txt"
RERANK_MODEL = "BAAI/bge-reranker-base"
TOP_N = 5
SIMILARITY_TOP_K = 10


class Chatbot:
    def __init__(self):
        self.node_parser = self.initialize_node_parser()
        self.llm = OpenAI(model=MODEL, temperature=TEMPERATURE)
        self.service_context = ServiceContext.from_defaults(
            llm=self.llm,
            embed_model=EMBED_MODEL,
            node_parser=self.node_parser,
        )
        self.engine = self.initialize_engine()

    @staticmethod
    def initialize_node_parser():
        def split(text):
            return text.split('\n')

        return SentenceWindowNodeParser.from_defaults(
            window_size=WINDOW_SIZE,
            window_metadata_key="window",
            original_text_metadata_key="original_text",
            sentence_splitter=split,
        )

    def initialize_engine(self):
        text = self.read_text(FILE_PATH)
        sentence_index = VectorStoreIndex.from_documents(
            [Document(text=text)], service_context=self.service_context
        )

        postproc = MetadataReplacementPostProcessor(
            target_metadata_key="window")
        rerank = SentenceTransformerRerank(top_n=TOP_N, model=RERANK_MODEL)

        wechat_bot_msgs = [
            ChatMessage(
                role=MessageRole.SYSTEM,
                content=(
                    "现在你将扮演我的克隆聊天机器人和朋友对话，请使用我的微信历史聊天记录作为参考，模仿这种特定的聊天风格和语气，以及句子回答的长度。注意使用类似的词汇、语句结构和表达方式、emoji的实用习惯。由于这个是微信聊天，请你说话不要太长太啰嗦。目标是使对话感觉自然、连贯，让他以为是在和我本人对话。"
                ),
            ),
            ChatMessage(
                role=MessageRole.USER,
                content=(
                    "我的相关微信历史聊天记录如下\n"
                    "---------------------\n"
                    "{context_str}\n"
                    "---------------------\n"
                    "请你模仿以上的聊天风格，完成以下对话，你的回答只包含回复\n"
                    "{query_str}\n"
                    "我的回复："
                )
            ),
        ]
        wechat_bot_template = ChatPromptTemplate(wechat_bot_msgs)

        engine = sentence_index.as_query_engine(
            similarity_top_k=SIMILARITY_TOP_K, node_postprocessors=[
                postproc, rerank]
        )
        engine.update_prompts(
            {"response_synthesizer:text_qa_template": wechat_bot_template})

        return engine

    @staticmethod
    def read_text(file_path):
        with open(file_path) as f:
            return f.read()

    def chat(self, input_text):
        query = f"{input_text}"
        response = self.engine.query(query)
        return response.response


def main():
    bot = Chatbot()
    print("Chatbot initialized. Start chatting!")
    history = "朋友："
    while True:
        user_input = input("You: ")
        if user_input.lower() in ['exit', 'quit']:
            break
        response = bot.chat(history + user_input)
        history += user_input + "\n" + "我：" + response + "\n" + "朋友："
        print("Bot:", response)


if __name__ == "__main__":
    main()
