from rest_framework.decorators import api_view, authentication_classes, permission_classes
from api.utils import CsrfExemptSessionAuthentication
from ..services.category_service import CategoryService, CategoryAlreadyExistsError, CategoryNotFoundError
from rest_framework.response import Response
from accounts.accounts import AccountRole

@api_view(['GET', 'POST'])
@authentication_classes([CsrfExemptSessionAuthentication])
def product_categories(request):
    service = CategoryService()

    if request.method == 'GET':
        status = request.query_params.get("status")
        if status == "true":
            status = True
        elif status == "false":
            status = False
        else:
            status = None
        return Response({"status": "ok", "data": service.getCategories(status=status)})

    user = request.user
    if not user.is_authenticated:
        return Response({"status": "error", "message": "Authentication required"}, status=401)
    if user.role != AccountRole.EMPLOYEE.value:
        return Response({"status": "error", "message": "Only employees can create categories"}, status=403)

    try:
        category = service.setCategory(
            name=request.data.get("name"),
            slug=request.data.get("slug"),
            description=request.data.get("description", ""),
            image=request.data.get("image", ""),
            status=request.data.get("status", True),
        )
        return Response({"status": "created", "data": category}, status=201)
    except ValueError as e:
        return Response({"status": "error", "message": str(e)}, status=400)
    except CategoryAlreadyExistsError as e:
        return Response({"status": "error", "message": str(e)}, status=409)
    except Exception as e:
        return Response({"status": "error", "message": "An error occurred while creating the category"}, status=500)


@api_view(['GET', 'PATCH', 'DELETE'])
@authentication_classes([CsrfExemptSessionAuthentication])
def product_category_detail(request, category_id):
    service = CategoryService()
    
    # GET - Retrieve a single category
    if request.method == 'GET':
        try:
            category = service.getCategoryById(category_id)
            if not category:
                return Response(
                    {"status": "error", "message": "Category not found"}, 
                    status=404
                )
            return Response({"status": "ok", "data": category})
        except Exception as e:
            return Response(
                {"status": "error", "message": str(e)}, 
                status=500
            )
    
    # PATCH - Update a category
    if request.method == 'PATCH':
        user = request.user
        if not user.is_authenticated:
            return Response(
                {"status": "error", "message": "Authentication required"}, 
                status=401
            )
        if user.role != AccountRole.EMPLOYEE.value:
            return Response(
                {"status": "error", "message": "Only employees can update categories"}, 
                status=403
            )
        
        try:
            # Prepare update data
            update_data = {}
            if 'name' in request.data:
                update_data['name'] = request.data['name']
            if 'slug' in request.data:
                update_data['slug'] = request.data['slug']
            if 'description' in request.data:
                update_data['description'] = request.data['description']
            if 'image' in request.data:
                update_data['image'] = request.data['image']
            if 'status' in request.data:
                update_data['status'] = request.data['status']
            
            updated_category = service.updateCategory(category_id, **update_data)
            return Response({"status": "ok", "data": updated_category})
            
        except CategoryNotFoundError as e:
            return Response({"status": "error", "message": str(e)}, status=404)
        except ValueError as e:
            return Response({"status": "error", "message": str(e)}, status=400)
        except CategoryAlreadyExistsError as e:
            return Response({"status": "error", "message": str(e)}, status=409)
        except Exception as e:
            return Response(
                {"status": "error", "message": f"An error occurred while updating the category: {str(e)}"}, 
                status=500
            )
    
    # DELETE - Delete a category
    if request.method == 'DELETE':
        user = request.user
        if not user.is_authenticated:
            return Response(
                {"status": "error", "message": "Authentication required"}, 
                status=401
            )
        if user.role != AccountRole.EMPLOYEE.value:
            return Response(
                {"status": "error", "message": "Only employees can delete categories"}, 
                status=403
            )
        
        try:
            success = service.deleteCategory(category_id)
            if not success:
                return Response(
                    {"status": "error", "message": "Category not found"}, 
                    status=404
                )
            return Response({"status": "ok", "message": "Category deleted successfully"})
        except Exception as e:
            return Response(
                {"status": "error", "message": f"An error occurred while deleting the category: {str(e)}"}, 
                status=500
            )