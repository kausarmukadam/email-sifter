
class Model:
    def __init__(self, index_path):
        # Load index
        pass

    # TODO: Add capability to inspect model
    def read_index(self):
        pass

    def ask_question(self, question: str):
        return "Not implemented yet!"

    def __format_answer(self, answer, response_header):
        return reponse_header + "\n" + answer

    def get_reading_material(self, max_len: int):
        # TODO: Append user specific data to the index before asking a question
        query = "Give me {} important items from my emails?",
        response_header = "Here's {} important items for you to read! \n"
        answer = self.__format_answer(
            self.ask_question(query.format(max_len)),
            response_header.format(max_len)
        )
        # TODO: Pretty print answer
        print(answer)
        return answer

model = Model("")
answer = model.get_reading_material(3)
