from rest_framework import permissions


class IsAdministrador(permissions.BasePermission):
    """
    Permiso personalizado que solo permite acceso a administradores.
    """
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_admin()


class IsAdministradorOrReadOnly(permissions.BasePermission):
    """
    Permiso que permite lectura a todos los usuarios autenticados,
    pero solo escritura a administradores.
    """
    
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        return request.user and request.user.is_authenticated and request.user.is_admin()


class IsSameEmpresa(permissions.BasePermission):
    """
    Permiso que verifica que el usuario pertenezca a la misma empresa
    que el objeto que está intentando acceder.
    """
    
    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Si el objeto tiene empresa, verificar que sea la misma
        if hasattr(obj, 'empresa'):
            return obj.empresa == request.user.empresa
        
        return True
