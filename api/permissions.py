from rest_framework import permissions

from boards.models import BoardMember, Board


class OwnerOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return True
        return False

    def has_object_permission(self, request, view, obj):
        if obj.owner == request.user:
            return True
        return False


class IsBoardOwnerOrMember(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return True
        return False

    def has_object_permission(self, request, view, obj):
        if obj.project.owner == request.user:
            return True
        if BoardMember.objects.filter(member=request.user, board=obj).exists() and request.method in ('GET',):
            return True
        return False


class IsBoardMember(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return True
        return False

    def has_object_permission(self, request, view, obj):
        if BoardMember.objects.filter(member=request.user, board=obj).exists():
            return True
        return False
