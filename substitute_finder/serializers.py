"""
All substitute_finder app models serializers.
"""
from django.contrib.auth.models import Permission
from rest_framework import serializers

from substitute_finder.models import Comment, CustomUser, Product, Category


class CategorySerializer(serializers.ModelSerializer):
    """
    Serializer for Category model.
    """

    class Meta:
        model = Category
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    """
    Serializer for Product model.
    """

    class Meta:
        model = Product
        fields = '__all__'


class CustomUserSerializer(serializers.ModelSerializer):
    """
    Serializer for CustomUser model.
    """

    class Meta:
        model = CustomUser
        fields = '__all__'


class CommentSerializer(serializers.ModelSerializer):
    """
    Serializer for Comment model.
    """
    permissions = serializers.SerializerMethodField()
    url = serializers.HyperlinkedIdentityField(
        view_name='substitute_finder:comment-detail',
        lookup_field='pk'
    )
    username = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['url', 'comment_text', 'created', 'updated', 'product', 'user', 'pk', 'permissions', 'username']

    def get_username(self, obj):
        return obj.user.username

    def get_permissions(self, obj):
        request = self.context.get('request')
        permissions = [code[0] for code in Permission.objects.filter(user=request.user).values_list('codename')]
        permission_codenames = [perm[0] for perm in obj._meta.permissions]
        if request and hasattr(request, 'user'):
            if request.user == obj.user or request.user.is_superuser:
                permissions = permissions + permission_codenames
        return list(set(permissions))
