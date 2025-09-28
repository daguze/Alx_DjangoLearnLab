import datetime

from rest_framework import serializers
from .models import Author, Book





class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = '__all__'

    """
        Serializes Book instances.
        Includes all fields: id, title, publication_year, author.
        Validation:
          - publication_year cannot be in the future.
        """

    def validate_publication_year(self, value:int):
        current = datetime.date.today()
        if value > current.year:
            raise serializers.ValidationError('The publication year can"t be in the future')
        return value




class AuthorSerializer(serializers.ModelSerializer):

    books = BookSerializer(many=True, read_only=True)

    class Meta:
        model = Author
        fields = 'id', 'name', 'books'