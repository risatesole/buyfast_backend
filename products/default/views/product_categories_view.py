from django.core.exceptions import PermissionDenied
from django.db import IntegrityError
from django.db.models import ProtectedError
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from products.default.models import Category


def _require_employee(request):
    if not request.user.is_authenticated:
        raise PermissionDenied("Authentication required")
    if not request.user.is_active:
        raise PermissionDenied("Your account is inactive")
    if request.user.role != "employee":
        raise PermissionDenied("Only employees are allowed to perform this action")


@method_decorator(csrf_exempt, name='dispatch')
class CategoryView(APIView):
    """
    GET  /api/v1/products/categories/      - list all categories (public)
    GET  /api/v1/products/categories/<pk>/ - retrieve a single category (public)
    POST /api/v1/products/categories/      - create a category (employee only)
    PATCH  /api/v1/products/categories/<pk>/ - partially update a category (employee only)
    DELETE /api/v1/products/categories/<pk>/ - delete a category (employee only)
    """

    permission_classes = [AllowAny]

    def get(self, request, pk=None):
        if pk:
            try:
                category = Category.objects.get(pk=pk)
            except Category.DoesNotExist:
                return Response(
                    {'error': f'Category with ID {pk} not found'},
                    status=status.HTTP_404_NOT_FOUND,
                )
            return Response({"status": "ok", "data": category.as_dict()})

        categories = Category.objects.all().order_by("priority", "name")
        return Response({
            "status": "ok",
            "data": [category.as_dict() for category in categories],
        })

    def post(self, request, pk=None):
        try:
            _require_employee(request)

            payload = request.data.get("data", request.data)

            name = str(payload["name"]).strip()
            slug = str(payload["slug"]).strip()
            if not name:
                raise ValueError("name is required")
            if not slug:
                raise ValueError("slug is required")

            images = payload.get("images") or {}

            category = Category.objects.create(
                name=name,
                slug=slug,
                description=payload.get("description") or "",
                priority=payload.get("priority") or 0,
                image_banner=images.get("banner") or "",
                image_cart=images.get("cart") or "",
                image_default=images.get("default") or "",
            )

            return Response({
                "message": "Category created successfully",
                "data": category.as_dict(),
            }, status=status.HTTP_201_CREATED)

        except PermissionDenied as e:
            return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)
        except IntegrityError:
            return Response(
                {'error': f"A category with slug '{payload.get('slug')}' already exists"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except (KeyError, ValueError) as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {'error': f'Error creating category: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def patch(self, request, pk=None):
        if not pk:
            return Response(
                {'error': 'Category ID is required'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            _require_employee(request)

            try:
                category = Category.objects.get(pk=pk)
            except Category.DoesNotExist:
                return Response(
                    {'error': f'Category with ID {pk} not found'},
                    status=status.HTTP_404_NOT_FOUND,
                )

            payload = request.data.get("data", request.data)

            if "name" in payload:
                category.name = str(payload["name"]).strip()
            if "slug" in payload:
                category.slug = str(payload["slug"]).strip()
            if "description" in payload:
                category.description = payload["description"] or ""
            if "priority" in payload:
                category.priority = payload["priority"] or 0
            if "images" in payload:
                images = payload["images"] or {}
                if "banner" in images:
                    category.image_banner = images["banner"] or ""
                if "cart" in images:
                    category.image_cart = images["cart"] or ""
                if "default" in images:
                    category.image_default = images["default"] or ""

            category.save()

            return Response({
                "message": "Category updated successfully",
                "data": category.as_dict(),
            })

        except PermissionDenied as e:
            return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)
        except IntegrityError:
            return Response(
                {'error': 'A category with this slug already exists'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response(
                {'error': f'Error updating category: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def delete(self, request, pk=None):
        if not pk:
            return Response(
                {'error': 'Category ID is required'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            _require_employee(request)

            try:
                category = Category.objects.get(pk=pk)
            except Category.DoesNotExist:
                return Response(
                    {'error': f'Category with ID {pk} not found'},
                    status=status.HTTP_404_NOT_FOUND,
                )

            category.delete()

            return Response({
                'message': f'Category {pk} deleted successfully',
                'id': pk,
            })

        except PermissionDenied as e:
            return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)
        except ProtectedError:
            return Response(
                {'error': 'Cannot delete category: it still has products assigned to it.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response(
                {'error': f'Error deleting category: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
