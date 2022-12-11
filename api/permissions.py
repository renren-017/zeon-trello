from rest_framework import permissions

from boards.models import BoardMember, CardComment


class IsProjectOwnerOrReadOnly(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if obj.owner == request.user:
            return True
        return False


class IsBoardOwnerOrMember(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if obj.project.owner == request.user:
            return True
        if BoardMember.objects.filter(user=request.user, board=obj).exists() and request.method in ('GET',):
            return True
        return False


class IsBoardMember(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if BoardMember.objects.filter(user=request.user, board=obj).exists():
            return True
        return False


class IsCommentOwner(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if (CardComment.objects.filter(user=request.user, card=obj.card).exists() and
                BoardMember.objects.filter(user=request.user, board=obj.card.column.board).exists()):
            return True
        return False
