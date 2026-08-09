import os

from dotenv import load_dotenv

load_dotenv()

# Azul (Banco Popular Dominicano) Payment Page settings.
# https://dev.azul.com.do — "Documento E-Commerce AZUL Página de Pagos"
AZUL_ENVIRONMENT = os.getenv("AZUL_ENVIRONMENT", "sandbox")

AZUL_MERCHANT_ID = os.getenv("AZUL_MERCHANT_ID", "")
AZUL_MERCHANT_NAME = os.getenv("AZUL_MERCHANT_NAME", "Economato UASD")
AZUL_MERCHANT_TYPE = os.getenv("AZUL_MERCHANT_TYPE", "ECommerce")
AZUL_AUTH_KEY = os.getenv("AZUL_AUTH_KEY", "")
AZUL_CURRENCY_CODE = os.getenv("AZUL_CURRENCY_CODE", "$")

# URLs per Azul's Payment Page guide.
AZUL_PAYMENT_PAGE_URL = (
    "https://pagos.azul.com.do/PaymentPage/Default.aspx"
    if AZUL_ENVIRONMENT == "production"
    else "https://pruebas.azul.com.do/PaymentPage/"
)
