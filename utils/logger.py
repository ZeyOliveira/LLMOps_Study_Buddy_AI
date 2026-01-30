import logging
import os
from datetime import datetime
from typing import Optional

LOG_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

def get_logger(
    name: str,
    log_level: int = logging.INFO,
    # TRUQUE DE MESTRE: Mudamos o padrão para /tmp/logs
    # O diretório /tmp sempre aceita escrita, mesmo com usuários restritos
    log_dir: Optional[str] = "/tmp/logs", 
) -> logging.Logger:
    """
    Cria e retorna uma instância de logger configurada para MLOps.
    Redireciona arquivos para /tmp para evitar erros de permissão em containers.
    """

    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    logger.propagate = False 

    if logger.handlers:
        return logger 

    formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)

    # 1. Console handler: Essencial para ver logs via 'kubectl logs'
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # 2. File handler: Agora em diretório garantido
    if log_dir:
        try:
            os.makedirs(log_dir, exist_ok=True)
            log_file = os.path.join(
                log_dir, f"{datetime.now().strftime('%Y-%m-%d')}.log"
            )

            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(log_level)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except Exception as e:
            # Fallback: Se mesmo o /tmp falhar, o console handler já está ativo
            print(f"Aviso: Não foi possível criar arquivo de log em {log_dir}: {e}")

    return logger