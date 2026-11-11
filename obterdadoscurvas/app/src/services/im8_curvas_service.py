import os
from urllib.parse import quote
import requests
from requests.adapters import HTTPAdapter, Retry
from src.errors.http_request_error import HttpRequestError
from src.configs.logger_config import logger


class Im8CurvasService:
    """Chama as APIs de Curvas do IM8 (guia de curvas, seção 6), no mesmo padrão do im8_service.py.

    A URL é montada pela configuração (URL_IM8_CURVAS); o campo `url` do evento nunca é chamado.
    """

    def __init__(self, correlation_id, client_id):
        self.base_url = os.getenv("URL_IM8_CURVAS").rstrip("/")
        self.x_itau_apikey = client_id
        self.x_itau_correlation_id = correlation_id
        self.x_apigw_api_id = os.getenv("X_APIGW_API_ID_CURVAS")
        self.certificate_path = os.getenv("CA_CERT_PATH")

    def obter_pontos(self, sts_token, curva):
        # TRANSFER usa pontotransferencias; BASE e COMPOSTA usam pontoscurvas (guia, 6.4)
        if curva.tipo_curva == "TRANSFER":
            url = f"{self.base_url}/curvas/v1/pontotransferencias"
            params = {"codigocurva": curva.codigo_curva, "dataexecucaocurva": curva.data_liberacao}
        else:
            url = f"{self.base_url}/curvas/v1/pontoscurvas/{quote(curva.nome_curva, safe='')}"
            params = {"data_execucao": curva.data_liberacao}
        return self._call_im8_api(sts_token, url, params)

    def _call_im8_api(self, sts_token, url, params):
        try:
            session = requests.Session()
            retries = Retry(total=6, backoff_factor=1, status_forcelist=[502, 503, 504],
                            allowed_methods={"GET"})
            session.mount("https://", HTTPAdapter(max_retries=retries))

            headers = {
                "x-itau-apikey": self.x_itau_apikey,
                "x-itau-correlationID": self.x_itau_correlation_id,
                "Authorization": "Bearer " + sts_token,
                "Accept-Encoding": "gzip",
            }
            if self.x_apigw_api_id:
                headers["x-apigw-api-id"] = self.x_apigw_api_id

            response = session.get(url=url, params=params, headers=headers,
                                   verify=self.certificate_path, timeout=15)

            if response.status_code == 200:
                return response.json()

            logger.error("Falha na chamada da api de curvas do IM8.", status_code_error=response.status_code,
                         error_message=response.reason, url_called=response.url)
            raise HttpRequestError(message=response.reason, status_code=response.status_code,
                                   url_called=response.url)
        except HttpRequestError:
            raise
        except Exception:
            logger.exception("Erro inesperado na chamada da api de curvas do IM8.", url=url)
            raise
