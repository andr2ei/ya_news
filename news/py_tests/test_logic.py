
from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects

from news.models import Comment


COMMENT_TEXT = 'Текст комментария'
NEW_COMMENT_TEXT = 'Обновлённый комментарий'


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, form_data, detail_url):
    client.post(detail_url, data=form_data)
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_user_can_create_comment(auth_client, form_data, detail_url, user, news):
    response = auth_client.post(detail_url, data=form_data)
    assertRedirects(response, f'{detail_url}#comments')

    comments_count = Comment.objects.count()
    assert comments_count == 1

    comment = Comment.objects.get()
    assert comment.text == COMMENT_TEXT
    assert comment.news == news
    assert comment.author == user


def test_author_can_delete_comment(author_client, comment_id, detail_url):
    delete_url = reverse('news:delete', args=(comment_id,))
    response = author_client.delete(delete_url)

    assertRedirects(response, f'{detail_url}#comments')

    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_user_cant_delete_comment_of_another_user(reader_client, comment_id):
    delete_url = reverse('news:delete', args=(comment_id,))
    response = reader_client.delete(delete_url)

    assert response.status_code == HTTPStatus.NOT_FOUND

    comments_count = Comment.objects.count()
    assert comments_count == 1


def test_author_can_edit_comment(author_client, form_data, detail_url, comment_id):
    edit_url = reverse('news:edit', args=(comment_id,))
    form_data['text'] = NEW_COMMENT_TEXT
    response = author_client.post(edit_url, data=form_data)

    assertRedirects(response, detail_url + '#comments')

    comment = Comment.objects.get()
    assert comment.text == NEW_COMMENT_TEXT

def test_user_cant_edit_comment_of_another_user(reader_client, comment_id, form_data):
    edit_url = reverse('news:edit', args=(comment_id,))
    response = reader_client.post(edit_url, data=form_data)

    assert response.status_code == HTTPStatus.NOT_FOUND

    comment = Comment.objects.get()
    assert comment.text == COMMENT_TEXT