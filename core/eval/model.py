"""Model Eval"""
import faiss
from langchain import OpenAI
from langchain.chains import VectorDBQAWithSourcesChain
import pickle


class Model:
    def __init__(self, index_path, vector_path):
        index = faiss.read_index(index_path)

        with open(vector_path, "rb") as f:
            self.store = pickle.load(f)

        self.store.index = index
        self.chain = VectorDBQAWithSourcesChain.from_llm(llm=OpenAI(temperature=0), vectorstore=self.store)

    def read_index(self):
        """
        Debug information about the index the model is using.
        """
        print(type(self.store))
        print(type(self.chain))

    def ask_question(self, question: str, session_id: str, user_id: str):
        """
        :param question: Query to pass into the LLM
        :param session_id: Session this question belongs to
        :param user_id: User originating the question.
        :return: Text response from the model
        """
        model_response = self.chain({"question": question})
        # TODO: Add question, answer pair to a session Db
        return model_response

    def __format_answer(self, answer, response_header):
        """
        :param answer: Answer received from the model
        :param response_header: Text to append to the answer for easier understanding
        :return:
        """
        return response_header + "\n" + answer

    def get_important_emails(self, max_len: int):
        """
        :param max_len: Number of emails items to return
        :return: List of high interest emails for the customer
        """
        query = "Give me {} important items from my emails?"
        response_header = "Here's {} important items for you to read! \n"
        answer = self.__format_answer(
            # TODO: Append user specific data to the index before asking a question
            self.ask_question(query.format(max_len), session_id="", user_id=""),
            response_header.format(max_len)
        )
        return answer


model = Model("docs.index", "faiss_store.pkl")
answer = model.get_important_emails(3)
print(answer)
