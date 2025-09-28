# api/test_views.py
from datetime import date
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase
from api.models import Author, Book

User = get_user_model()


class BookApiViewsTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        # Users
        cls.user = User.objects.create_user(username="user", password="pass12345")
        cls.staff = User.objects.create_user(username="staff", password="pass12345", is_staff=True)

        # Data
        cls.rowling = Author.objects.create(name="J. K. Rowling")
        cls.tolkien = Author.objects.create(name="J. R. R. Tolkien")

        cls.hp1 = Book.objects.create(title="Philosopher's Stone", publication_year=1997, author=cls.rowling)
        cls.hp2 = Book.objects.create(title="Chamber of Secrets", publication_year=1998, author=cls.rowling)
        cls.hobbit = Book.objects.create(title="The Hobbit", publication_year=1937, author=cls.tolkien)

    # URL helpers
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

    # -------- READ (public) --------
    def test_list_books_public(self):
        response = self.client.get(self.url_list())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)
        self.assertIn("title", response.data[0])
        self.assertIn("author", response.data[0])

    def test_detail_book_public(self):
        response = self.client.get(self.url_detail(self.hp1.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.hp1.id)
        self.assertEqual(response.data["title"], "Philosopher's Stone")

    # -------- CREATE (auth required; staff-only per hooks) --------
    def test_create_book_unauthenticated_denied(self):
        payload = {"title": "New Book", "publication_year": 2000, "author": self.rowling.id}
        response = self.client.post(self.url_create(), payload, format="json")
        self.assertIn(response.status_code, (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN))

    def test_create_book_authenticated_nonstaff_forbidden(self):
        self.client.login(username="user", password="pass12345")
        payload = {"title": "New Book", "publication_year": 2000, "author": self.rowling.id}
        response = self.client.post(self.url_create(), payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_book_staff_ok(self):
        self.client.login(username="staff", password="pass12345")
        payload = {"title": "Prisoner of Azkaban", "publication_year": 1999, "author": self.rowling.id}
        response = self.client.post(self.url_create(), payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["title"], "Prisoner of Azkaban")
        self.assertTrue(Book.objects.filter(title="Prisoner of Azkaban").exists())

    # -------- VALIDATION (future year) --------
    def test_create_rejects_future_year(self):
        self.client.login(username="staff", password="pass12345")
        payload = {
            "title": "Future Book",
            "publication_year": date.today().year + 5,
            "author": self.rowling.id,
        }
        response = self.client.post(self.url_create(), payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("publication_year", response.data)

    # -------- UPDATE --------
    def test_update_book_nonstaff_forbidden(self):
        self.client.login(username="user", password="pass12345")
        response = self.client.patch(self.url_update(self.hp1.id), {"title": "New Title"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_book_staff_ok(self):
        self.client.login(username="staff", password="pass12345")
        response = self.client.patch(self.url_update(self.hp1.id), {"title": "Sorcerer's Stone"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.hp1.refresh_from_db()
        self.assertEqual(self.hp1.title, "Sorcerer's Stone")

    # -------- DELETE --------
    def test_delete_book_nonstaff_forbidden(self):
        self.client.login(username="user", password="pass12345")
        response = self.client.delete(self.url_delete(self.hp2.id))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Book.objects.filter(id=self.hp2.id).exists())

    def test_delete_book_staff_ok(self):
        self.client.login(username="staff", password="pass12345")
        response = self.client.delete(self.url_delete(self.hp2.id))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Book.objects.filter(id=self.hp2.id).exists())

    # -------- FILTERING --------
    def test_filter_by_author(self):
        response = self.client.get(self.url_list(), {"author": self.rowling.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        titles = {b["title"] for b in response.data}
        self.assertSetEqual(titles, {"Philosopher's Stone", "Chamber of Secrets"})

    def test_filter_by_year(self):
        response = self.client.get(self.url_list(), {"publication_year": 1998})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["title"], "Chamber of Secrets")

    # -------- SEARCH --------
    def test_search_title_and_author(self):
        response = self.client.get(self.url_list(), {"search": "hobbit"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["title"], "The Hobbit")

        response = self.client.get(self.url_list(), {"search": "rowling"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 2)

    # -------- ORDERING --------
    def test_ordering_by_year(self):
        response = self.client.get(self.url_list(), {"ordering": "publication_year"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        years = [b["publication_year"] for b in response.data]
        self.assertEqual(years, sorted(years))

        response = self.client.get(self.url_list(), {"ordering": "-publication_year"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        years_desc = [b["publication_year"] for b in response.data]
        self.assertEqual(years_desc, sorted(years_desc, reverse=True))
