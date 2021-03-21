from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404

from main.decorators import teacher_required
from main.forms import TestForm, ScheduleForm
from main.models import TestHistory, AnswerHistory, User, Test, Question, Subject


def save_user_test(user: User, form: TestForm):
    test_history = TestHistory.objects.create(user=user, test=form.test)

    answers = []

    for question in form.questions:
        answer = form.cleaned_data[str(question.id)]
        is_correct = question.answer == answer

        if is_correct:
            form.result_source += question.primary_score

        answer_history = AnswerHistory(test_history=test_history, question=question, user_answer=answer,
                                       is_correct=is_correct)
        answers.append(answer_history)

    test_history.primary_source = form.result_source
    test_history.save()
    AnswerHistory.objects.bulk_create(answers)

    user.coins += int(form.result_source // 1.5)
    user.save()


def get_test_questions_sources(test: Test):
    questions = Question.objects.filter(test=test)
    res = []
    for quest in questions:
        res.append(AnswerHistory.get_count_correct_answers_for_question(quest))

    return res


def get_pagination_vars(request, objects_list):
    paginator = Paginator(objects_list, 5)

    page_number = request.GET.get('page', 1)
    paginator_object = paginator.get_page(page_number)

    previous_url = next_url = '?page=%s' % paginator_object.number
    if paginator_object.has_previous():
        previous_url = '?page=%s' % paginator_object.previous_page_number()
    if paginator_object.has_next():
        next_url = '?page=%s' % paginator_object.next_page_number()

    context = {
        'paginator_object': paginator_object,
        'previous_url': previous_url,
        'page_number': page_number,
        'next_url': next_url
    }

    return context


def get_subject_of_page_and_all(subject_id):
    if subject_id == '0':
        subject_page = Subject.objects.first()
    else:
        subject_page = get_object_or_404(Subject, id=subject_id)

    return {'subject_page': subject_page, 'subjects': Subject.objects.all()}


@teacher_required
def save_schedule(files):
    form = ScheduleForm(files=files)
    if form.is_valid():
        form.save()
