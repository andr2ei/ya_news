import pytest
from django.conf import settings
from django.urls import reverse

HOME_URL = reverse('news:home')

@pytest.mark.django_db
def test_news_count(client, all_news):
    response = client.get(HOME_URL)
    object_list = response.context['object_list']
    news_count = len(object_list)
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_order(client, all_news):
    response = client.get(HOME_URL)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


@pytest.mark.django_db
def test_comments_order(detail_url, client, all_comments):
    response = client.get(detail_url)
    assert 'news' in response.context
    news = response.context['news']
    all_comments = news.comment_set.all()
    assert all_comments[0].created < all_comments[1].created


@pytest.mark.django_db
def test_anonymous_client_has_no_form(detail_url, client):
    response = client.get(detail_url)
    assert 'form' not in response.context


@pytest.mark.django_db
def test_authorized_client_has_form(detail_url, client, author):
    client.force_login(author)
    response = client.get(detail_url)
    assert 'form' in response.context
