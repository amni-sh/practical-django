from django.contrib.auth import get_user_model
from django.test import TestCase, RequestFactory
from django.urls import resolve

from snippets.models import Snippet, Comment
from snippets.views import top, snippet_edit
UserModel = get_user_model()


class TopPageRenderSnippetsTest(TestCase):
    def setUp(self):
        self.user = UserModel.objects.create(
            username="test_user",
            email="test@example.com",
            password="top_secret_pass0001",
        )
        self.snippet = Snippet.objects.create(
            title="title1",
            code="print('hello')",
            description="description1",
            created_by=self.user,
        )
    
    def test_should_returns_snippet_title(self):
        request = RequestFactory().get("/")
        request.user = self.user
        response = top(request)
        self.assertContains(response, self.snippet.title)

    def test_should_returns_username(self):
        request = RequestFactory().get("/")
        request.user = self.user
        response = top(request)
        self.assertContains(response, self.user.username)


# Create your tests here.
class TopPageTest(TestCase):
    def test_top_returns_200(self):
        response = self.client.get("/")
        self.assertContains(response, "Djangoスニペット", status_code=200)

    def test_top_returns_expected_content(self):
        response = self.client.get("/")
        self.assertTemplateUsed(response, "snippets/top.html")


class CreateSnippetTest(TestCase):
    def setUp(self):
        self.user = UserModel.objects.create(
            username="test_user",
            email="test@example.com",
            password="secret",
        )
        self.client.force_login(self.user)

    def test_render_creation_form(self):
        response = self.client.get("/snippets/new/")
        self.assertContains(response, "スニペットの登録", status_code=200)

    def test_create_snippet(self):
        data = {"title": "タイトル", "code": "コード", "description": "解説"}
        self.client.post("/snippets/new/", data)
        snippet = Snippet.objects.get(title="タイトル")
        self.assertEqual("コード", snippet.code)
        self.assertEqual("解説", snippet.description)


class SnippetDetailTest(TestCase):
    def setUp(self):
        self.user = UserModel.objects.create(
            username="test_user",
            email="test@example.com",
            password="secret",
        )
        self.snippet = Snippet.objects.create(
            title="タイトル",
            code="コード",
            description="解説",
            created_by=self.user,
        )
        self.comment = Comment.objects.create(
            text="コメント本文",
            commented_to=self.snippet,
            commented_by=self.user,
        )

    def test_should_use_expected_template(self):
        response = self.client.get("/snippets/%s/" % self.snippet.id)
        self.assertTemplateUsed(response, "snippets/snippet_detail.html")

    def test_detail_page_returns_200_and_expected_heading(self):
        response = self.client.get("/snippets/%s/" % self.snippet.id)
        self.assertContains(response, self.snippet.title, status_code=200)
    
    def test_detail_page_returns_expected_comment(self):
        response = self.client.get("/snippets/%s/" % self.snippet.id)
        self.assertContains(response, self.comment.text) 


class EditSnippetTest(TestCase):
    def test_should_resolve_snippet_edit(self):
        found = resolve("/snippets/1/edit/")
        self.assertEqual(snippet_edit, found.func)


class CreateCommentTest(TestCase):
    def setUp(self):
        self.user = UserModel.objects.create(
            username="test_user",
            email="test@email.com",
            password="secret",
        )
        self.snippet = Snippet.objects.create(
            title="title",
            code="code",
            description="description",
            created_by=self.user
        )
        self.client.force_login(self.user)

    def test_create_comment(self):
        data = {"text": "comment"}
        self.client.post("/snippets/%s/comments/new/" % self.snippet.id, data)
        comment = Comment.objects.get(text="comment")
        self.assertEqual("title", comment.commented_to.title)
        self.assertEqual("test_user", comment.commented_by.username)
