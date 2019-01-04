"""
Web api.
"""
from rest_framework import generics
from rest_framework.viewsets import ModelViewSet

from substitute_finder.models import Comment, CustomUser, Category, Product
from substitute_finder.permissions import CommentCustomPermission
from substitute_finder.serializers import CommentSerializer, CustomUserSerializer, CategorySerializer, \
    ProductSerializer


class CategoryApiViewSet(ModelViewSet):
    """
    View that exposes Categories through rest api.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class ProductApiViewSet(ModelViewSet):
    """
    View that exposes Products through rest api.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class CustomUserApiViewSet(ModelViewSet):
    """
    View that exposes CustomUsers through rest api.
    """
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer


class CommentApiViewSet(ModelViewSet):
    """
    View that exposes Comments through rest api.
    """
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = (CommentCustomPermission,)

    def create(self, request, *args, **kwargs):
        request.data['user'] = request.user.id
        return super(CommentApiViewSet, self).create(request, *args, **kwargs)


class CommentsByProductApiView(generics.ListAPIView):
    """
    View that exposes Comments attached to specific product through rest api.
    """
    serializer_class = CommentSerializer

    def get_queryset(self):
        """
        This view return a list of comments attached to passed product in url.
        :return:
        """
        return Comment.objects.filter(product_id=self.kwargs['pk'])
