"""
Custom permissions for substitute_finder app
"""
from rest_framework.permissions import BasePermission, SAFE_METHODS


class CommentCustomPermission(BasePermission):
    """
    Custom permissions for actions on comment.
    """
    message = 'Vous n\'avez pas les droits pour mettre à jour ou supprimer ce commentaire'

    def has_object_permission(self, request, view, obj):
        """
        check if user is comment owner or has specific permissions to update or delete comment.
        """
        if request.method in SAFE_METHODS or request.user.is_superuser:
            return True
        if request.method == 'PATCH' and request.user.has_perm('substitute_finder.can_change_all_commments'):
            return True
        if request.method == 'DELETE' and request.user.has_perm('substitute_finder.can_delete_all_comments'):
            return True

        return request.user == obj.user
