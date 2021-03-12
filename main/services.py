from main.forms import TestForm
from main.models import TestHistory, AnswerHistory, User


def save_user_test(user: User, form: TestForm):
    test_history = TestHistory.objects.create(user=user, test=form.test)

    answers = []
    source = 0

    for question in form.questions:
        answer = form.cleaned_data[str(question.id)]
        is_correct = question.answer == answer

        if is_correct:
            source += question.primary_score

        answer_history = AnswerHistory(test_history=test_history, question=question, user_answer=answer,
                                       is_correct=is_correct)
        answers.append(answer_history)

    test_history.primary_source = source
    test_history.save()
    AnswerHistory.objects.bulk_create(answers)

    user.coins += source // 1.5
    user.save()
