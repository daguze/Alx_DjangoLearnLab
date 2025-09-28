from datetime import date
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase
from api.models import Author, Book

User = get_user_model()


class BookApiTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        # Users for permission tests
        cls.user = User.objects.create_user(username="user", password="pass12345")
        cls.staff = User.objects.create_user(username="staff", password="pass12345", is_staff=True)

        # Authors
        cls.a_rowling = Author.objects.create(name="J. K. Rowling")
        cls.a_tolkien = Author.objects.create(name="J. R. R. Tolkien")

        # Books
        cls.b1 = Book.objects.create(title="Philosopher's Stone", publication_year=1997, author=cls.a_rowling)
        cls.b2 = Book.objects.create(title="Chamber of Secrets", publication_year=1998, author=cls.a_rowling)
        cls.b3 = Book.objects.create(title="The Hobbit", publication_year=1937, author=cls.a_tolkien)


    def url_list(self):
        return reverse("api:book-list")
    def url_detail(self, pk):
        return reverse("api:book-detail", kwargs={"pk": pk})

    def url_create(self):
        return reverse("api:book-create")

    def url_update(self, pk):
        return reverse("api:book-update", kwargs={"pk": pk})
    def url_delete(self, pk):
        return reverse("api:book-delete", kwargs={"pk": pk})


    def test_list_books_public(self):
        res = self.client.get(self.url_list())
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 3)

        self.assertIn("author", res.data[0])

    def test_detail_book_public(self):
        res = self.client.get(self.url_detail(self.b1.id))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["id"], self.b1.id)
        self.assertEqual(res.data["title"], "Philosopher's Stone")

    def test_create_book_unauthenticated_denied(self):
        payload = {"title": "New Book", "publication_year": 2001, "author": self.a_rowling.id}
        res = self.client.post(self.url_create(), payload, format="json")
        self.assertIn(res.status_code, (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN))

    def test_create_book_authenticated_nonstaff_denied(self):
        self.client.login(username="user", password="pass12345")
        payload = {"title": "New Book", "publication_year": 2001, "author": self.a_rowling.id}
        res = self.client.post(self.url_create(), payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_book_staff_ok(self):
        self.client.login(username="staff", password="pass12345")
        payload = {"title": "Prisoner of Azkaban", "publication_year": 1999, "author": self.a_rowling.id}
        res = self.client.post(self.url_create(), payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data["title"], "Prisoner of Azkaban")
        self.assertTrue(Book.objects.filter(title="Prisoner of Azkaban").exists())


    def test_create_book_rejects_future_year(self):
        self.client.login(username="staff", password="pass12345")
        next_year = date.today().year + 2
        payload = {"title": "Future Book", "publication_year": next_year, "author": self.a_rowling.id}
        res = self.client.post(self.url_create(), payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("publication_year", res.data)


    def test_update_book_nonstaff_denied(self):
        self.client.login(username="user", password="pass12345")
        res = self.client.patch(self.url_update(self.b1.id), {"title": "New Title"}, format="json")
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_book_staff_ok(self):
        self.client.login(username="staff", password="pass12345")
        res = self.client.patch(self.url_update(self.b1.id), {"title": "Sorcerer's Stone"}, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.b1.refresh_from_db()
        self.assertEqual(self.b1.title, "Sorcerer's Stone")


    def test_delete_book_nonstaff_denied(self):
        self.client.login(username="user", password="pass12345")
        res = self.client.delete(self.url_delete(self.b2.id))
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Book.objects.filter(id=self.b2.id).exists())

    def test_delete_book_staff_ok(self):
        self.client.login(username="staff", password="pass12345")
        res = self.client.delete(self.url_delete(self.b2.id))
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Book.objects.filter(id=self.b2.id).exists())


    def test_filter_by_exact_title(self):
        res = self.client.get(self.url_list(), {"title": "The Hobbit"})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]["title"], "The Hobbit")

    def test_filter_by_author_id(self):

        res = self.client.get(self.url_list(), {"author": self.a_rowling.id})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        titles = {b["title"] for b in res.data}
        self.assertSetEqual(titles, {"Philosopher's Stone", "Chamber of Secrets"})

    def test_filter_by_year(self):
        res = self.client.get(self.url_list(), {"publication_year": 1998})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]["title"], "Chamber of Secrets")

    def test_search_by_title_or_author(self):
        res1 = self.client.get(self.url_list(), {"search": "hobbit"})
        self.assertEqual(res1.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res1.data), 1)
        self.assertEqual(res1.data[0]["title"], "The Hobbit")

        res2 = self.client.get(self.url_list(), {"search": "rowling"})
        self.assertEqual(res2.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(res2.data), 2)


    def test_ordering_by_year_asc_desc(self):
        asc = self.client.get(self.url_list(), {"ordering": "publication_year"})
        desc = self.client.get(self.url_list(), {"ordering": "-publication_year"})
        self.assertEqual(asc.status_code, status.HTTP_200_OK)
        self.assertEqual(desc.status_code, status.HTTP_200_OK)

        asc_years = [b["publication_year"] for b in asc.data]
        desc_years = [b["publication_year"] for b in desc.data]
        self.assertEqual(asc_years, sorted(asc_years))
        self.assertEqual(desc_years, sorted(desc_years, reverse=True))