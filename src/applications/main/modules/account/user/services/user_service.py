from ..models.model_user import User, UserRoles
from ....customer.models.customer_model import Customer_model
class emailExistsError(Exception):
    pass
class UserService:
    ROLE_CUSTOMER = UserRoles.CUSTOMER.value
    ROLE_EMPLOYEE = UserRoles.EMPLOYEE.value

    def deactivateUser(self):
        raise NotImplementedError("This method is not implemented")
    
    def activateUser(self):
        raise NotImplementedError("This method is not implemented")
    
    def createCustomer(self,first_name,last_name,email,password):
        if User.objects.filter(email=email).exists():
            raise emailExistsError("This email is alrreddy in use")
        
        user = User.objects.create_user( # type: ignore
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password,
            role=self.ROLE_CUSTOMER,
            status="active"
        )
        customer = Customer_model.objects.create(
            user=user
        )

        return user, customer

    def setUserRoleCustomer(self,userid):
        raise NotImplementedError("This method is not implemented")
    
    def setUserRoleEmployee(self, userid):
        try:
            user = User.objects.get(id=userid)
        except User.DoesNotExist:
            raise ValueError("User not found")
        user.role = self.ROLE_EMPLOYEE
        user.save(update_fields=["role"])
        return user
    
    def getUserRole(self,userid):
        raise NotImplementedError("This method is not implemented")
    
    def isEmployee(self,user):
        if user.role == "employee":
            return True
        else:
            return False
    
    def isUserCustomer(self,userid):
        raise NotImplementedError("This method is not implemented")
    
