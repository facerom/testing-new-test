import boto3
import json
from core.exceptions import ErrorController

class SecretManagerAWS:
    def __init__(self) -> None:
        self.secrets_client = boto3.client('secretsmanager')

    def get_secret(self, secret_name):
        if not secret_name:
            raise ErrorController(status_code=400, detail="El nombre del secreto no puede ser None.")
        try:
            get_secret_value_response = self.secrets_client.get_secret_value(SecretId=secret_name)
        except self.secrets_client.exceptions.ResourceNotFoundException:
            raise ErrorController(status_code=404, detail=f"El secreto '{secret_name}' no fue encontrado.")
        except self.secrets_client.exceptions.InvalidParameterException:
            raise ErrorController(status_code=400, detail=f"Nombre de secreto inválido: '{secret_name}'.")
        except self.secrets_client.exceptions.InvalidRequestException:
            raise ErrorController(status_code=400, detail="Solicitud inválida al obtener el secreto.")
        except self.secrets_client.exceptions.DecryptionFailure:
            raise ErrorController(status_code=500, detail="Error al descifrar el secreto.")
        except self.secrets_client.exceptions.InternalServiceError:
            raise ErrorController(status_code=500, detail="Error interno del servicio Secrets Manager.")
        except Exception as e:
            raise ErrorController(status_code=500, detail=f"Error al recuperar el secreto: {str(e)}")

        if 'SecretString' in get_secret_value_response:
            json_secret = json.loads(get_secret_value_response['SecretString'])
            return json_secret
        else:
            raise ErrorController(status_code=404, detail=f"El secreto '{secret_name}' no contiene un valor de cadena.")
