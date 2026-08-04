from .base import BaseStateSerializer


class QuizStateSerializer(BaseStateSerializer):

    def serialize(self, answers):

        return {
            "answers": answers
        }


    def deserialize(self, state):

        return state.get(
            "answers",
            {}
        )