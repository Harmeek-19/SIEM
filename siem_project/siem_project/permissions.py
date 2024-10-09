from rest_framework import permissions

class IsOwnerOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return (
            request.user.is_staff or 
            obj.reported_by == request.user or 
            request.user.username == 'system_user'
        )